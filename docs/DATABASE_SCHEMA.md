# Atelier Database Schema

> 状态：规划中，尚未实现。本文档定义 Atelier 的 SQLite 数据库完整表结构，作为 SQLAlchemy model 的直接依据。

## 1. 概述

SQLite 是 Atelier 的唯一项目与运行状态持久化层，负责存储 projects、jobs、workflow graphs、execution plans、tasks、artifacts、worker events、resource locks、cache entries、presets、runtime components、model assets 和 credential references。真实 secrets 不进入 SQLite，应交给 OS credential storage 或受控 credential backend。

### 设计原则

- **本地优先**：单文件 SQLite，无需外部数据库服务。
- **追加友好**：task_events 只追加不更新，方便回溯和审计。
- **JSON 与拆表并存**：整存整取的复杂结构用 JSON，需要关系查询的用拆表。
- **状态可恢复**：任务和 artifact 状态足以支撑崩溃后恢复。

## 2. 约定

| 项目 | 约定 |
|---|---|
| 主键格式 | ULID，存为 TEXT (26 字符) |
| 时间格式 | ISO 8601 UTC，存为 TEXT |
| 枚举格式 | TEXT + CHECK 约束 |
| 外键 | `PRAGMA foreign_keys = ON` |
| 表名 | 复数，snake_case |
| 列名 | snake_case |
| JSON 字段 | TEXT 类型，存储合法 JSON 字符串 |
| 布尔 | INTEGER (0/1)，SQLite 无原生 BOOL |
| NULL 策略 | 除主键和必需字段外允许 NULL |

## 3. 表定义

### 3.1 projects

项目元信息。一个 project 是用户的工作容器，包含多个 job。

```sql
CREATE TABLE projects (
    project_id   TEXT PRIMARY KEY,                -- ULID
    name         TEXT NOT NULL,
    description  TEXT NOT NULL DEFAULT '',
    root_dir     TEXT NOT NULL,                    -- 项目根目录路径
    created_at   TEXT NOT NULL,                    -- ISO 8601 UTC
    updated_at   TEXT NOT NULL
);

CREATE INDEX idx_projects_updated_at ON projects(updated_at);
```

---

### 3.2 jobs

一个 Job 代表一次"从 workflow 到产物"的完整执行。

```sql
CREATE TABLE jobs (
    job_id              TEXT PRIMARY KEY,          -- ULID
    project_id          TEXT NOT NULL REFERENCES projects(project_id),
    name                TEXT NOT NULL,
    workflow_graph_id   TEXT NOT NULL REFERENCES workflow_graphs(graph_id),
    execution_plan_id   TEXT REFERENCES execution_plans(plan_id),
    status              TEXT NOT NULL DEFAULT 'draft'
                        CHECK (status IN (
                            'draft', 'queued', 'running',
                            'completed', 'failed', 'cancelled'
                        )),
    priority            INTEGER NOT NULL DEFAULT 0,   -- 队列优先级，数值越大越优先
    input_media_paths   TEXT NOT NULL DEFAULT '[]',    -- JSON array of paths
    output_dir          TEXT,
    created_at          TEXT NOT NULL,
    updated_at          TEXT NOT NULL,
    started_at          TEXT,
    completed_at        TEXT,
    error_message       TEXT
);

CREATE INDEX idx_jobs_project_id ON jobs(project_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
```

---

### 3.3 workflow_graphs

存储 WorkflowGraph 快照。每次提交 Job 时冻结一份，保证执行记录可回溯。

```sql
CREATE TABLE workflow_graphs (
    graph_id     TEXT PRIMARY KEY,                -- ULID
    name         TEXT NOT NULL,
    description  TEXT NOT NULL DEFAULT '',
    graph_json   TEXT NOT NULL,                    -- 完整 WorkflowGraph JSON（含 nodes + edges）
    node_count   INTEGER NOT NULL DEFAULT 0,       -- 冗余统计字段
    edge_count   INTEGER NOT NULL DEFAULT 0,
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL
);
```

#### JSON vs 拆表决策

WorkflowGraph 的 nodes 和 edges 采用 JSON 整存（`graph_json`），不拆成 workflow_nodes 和 workflow_edges 表，理由：

- WorkflowGraph 是不可变快照，提交后不再修改单个节点。
- GUI 编辑时操作的是内存中的 Pydantic 对象，不需要数据库级的节点查询。
- 整存整取性能优于多表 JOIN。
- 如果未来需要跨 graph 搜索节点（如"找出所有用过 whisper 的 graph"），可加全文索引或异步构建搜索索引。

---

### 3.4 execution_plans

ExecutionPlan 的持久化。phases / lanes 结构用 JSON 存储。

```sql
CREATE TABLE execution_plans (
    plan_id             TEXT PRIMARY KEY,          -- ULID
    job_id              TEXT NOT NULL REFERENCES jobs(job_id),
    workflow_graph_id   TEXT NOT NULL REFERENCES workflow_graphs(graph_id),
    status              TEXT NOT NULL DEFAULT 'draft'
                        CHECK (status IN (
                            'draft', 'validated', 'scheduled',
                            'running', 'completed', 'failed', 'cancelled'
                        )),
    phases_json         TEXT NOT NULL DEFAULT '[]', -- JSON: list[ExecutionPhase]
    conflicts_json      TEXT NOT NULL DEFAULT '[]', -- JSON: list[Conflict]
    hardware_snapshot   TEXT NOT NULL,              -- JSON: HardwareSnapshot
    created_at          TEXT NOT NULL,
    updated_at          TEXT NOT NULL
);

CREATE INDEX idx_execution_plans_job_id ON execution_plans(job_id);
CREATE INDEX idx_execution_plans_status ON execution_plans(status);
```

---

### 3.5 execution_tasks

每个 ExecutionTask 独立一行。这是调度和状态追踪的核心表，需要拆表以支持高频状态更新和查询。

```sql
CREATE TABLE execution_tasks (
    task_id             TEXT PRIMARY KEY,          -- ULID
    plan_id             TEXT NOT NULL REFERENCES execution_plans(plan_id),
    phase_id            TEXT NOT NULL,             -- 所属 Phase ID
    lane_id             TEXT NOT NULL,             -- 所属 Lane ID
    source_node_id      TEXT NOT NULL,             -- 来源 WorkflowNode.node_id
    node_type           TEXT NOT NULL,             -- 节点类型名

    params_json         TEXT NOT NULL DEFAULT '{}', -- JSON: 实际运行参数
    status              TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN (
                            'pending', 'queued', 'running',
                            'completed', 'failed', 'retry_pending',
                            'skipped', 'cancelled'
                        )),

    resource_request    TEXT NOT NULL DEFAULT '{}', -- JSON: ResourceRequest
    resource_binding    TEXT,                       -- JSON: ResourceBinding（Scheduler 分配后填入）
    runtime_request     TEXT NOT NULL DEFAULT '{}', -- JSON: RuntimeRequest
    runtime_binding     TEXT,                       -- JSON: RuntimeBinding（RuntimeManager 解析后填入）

    failure_policy      TEXT NOT NULL DEFAULT '{}', -- JSON: FailurePolicy
    cache_key           TEXT,                       -- 缓存键
    cache_hit           INTEGER NOT NULL DEFAULT 0, -- 0/1 是否命中缓存
    retry_count         INTEGER NOT NULL DEFAULT 0,

    created_at          TEXT NOT NULL,
    updated_at          TEXT NOT NULL,
    started_at          TEXT,
    completed_at        TEXT,
    error_code          TEXT,                       -- 失败时的错误码
    error_message       TEXT,                       -- 失败时的错误描述
    duration_seconds    REAL                        -- 执行时长
);

CREATE INDEX idx_execution_tasks_plan_id ON execution_tasks(plan_id);
CREATE INDEX idx_execution_tasks_status ON execution_tasks(status);
CREATE INDEX idx_execution_tasks_node_type ON execution_tasks(node_type);
CREATE INDEX idx_execution_tasks_cache_key ON execution_tasks(cache_key);
```

---

### 3.6 task_dependencies

Task 之间的依赖关系。一个 Task 可依赖多个前置 Task。

```sql
CREATE TABLE task_dependencies (
    task_id             TEXT NOT NULL REFERENCES execution_tasks(task_id),
    depends_on_task_id  TEXT NOT NULL REFERENCES execution_tasks(task_id),
    PRIMARY KEY (task_id, depends_on_task_id)
);

CREATE INDEX idx_task_deps_depends_on ON task_dependencies(depends_on_task_id);
```

---

### 3.7 artifacts

产物记录。`artifacts.task_id` 表示原始生产任务。cache hit、复用输入、导出 finalization 等"本任务使用了哪个 artifact"的关系由 `task_artifacts` 表表达，避免把同一个 artifact 复制成多条互相矛盾的记录。

```sql
CREATE TABLE artifacts (
    artifact_id     TEXT PRIMARY KEY,              -- ULID
    task_id         TEXT NOT NULL REFERENCES execution_tasks(task_id),
    artifact_type   TEXT NOT NULL
                    CHECK (artifact_type IN (
                        'video', 'audio', 'subtitle',
                        'ocr_text_track', 'image_seq',
                        'metadata', 'cache'
                    )),
    path            TEXT NOT NULL,                 -- 文件路径
    hash            TEXT,                          -- SHA-256 hex digest
    size_bytes      INTEGER,                       -- 文件大小
    metadata_json   TEXT NOT NULL DEFAULT '{}',    -- JSON: 附加元信息
    status          TEXT NOT NULL DEFAULT 'valid'
                    CHECK (status IN (
                        'valid', 'suspect', 'deleted', 'partial'
                    )),
    created_at      TEXT NOT NULL
);

CREATE INDEX idx_artifacts_task_id ON artifacts(task_id);
CREATE INDEX idx_artifacts_type ON artifacts(artifact_type);
CREATE INDEX idx_artifacts_hash ON artifacts(hash);
```

常见 artifact type：

| artifact_type | 用途 |
|---|---|
| `subtitle` | ASR、翻译或审校后的 SRT/VTT/ASS 字幕文件 |
| `ocr_text_track` | OCR Recognition 产生的结构化画面文字轨道，用作 Translate Agent 的视觉上下文 |
| `metadata` | sidecar / fusion / warnings / probe 结果等结构化 JSON，例如 `translation_fusion.json` |

### Artifact Status 说明

| 状态 | 含义 |
|---|---|
| `valid` | 文件完整且 hash 验证通过 |
| `suspect` | hash 不匹配或文件可能不完整 |
| `deleted` | 文件已被清理（保留记录用于审计） |
| `partial` | 任务失败前产出的部分产物 |

---

### 3.8 task_artifacts

Task 与 artifact 的关联表。它记录某个 Task 消费、产出、缓存命中或保留了哪些 artifact。

```sql
CREATE TABLE task_artifacts (
    link_id       TEXT PRIMARY KEY,                -- ULID
    task_id       TEXT NOT NULL REFERENCES execution_tasks(task_id),
    artifact_id   TEXT NOT NULL REFERENCES artifacts(artifact_id),
    role          TEXT NOT NULL
                  CHECK (role IN (
                      'input', 'output', 'partial', 'cache_hit', 'final_output'
                  )),
    port_id       TEXT NOT NULL DEFAULT '',        -- 对应 input/output port，未知时为空字符串
    created_at    TEXT NOT NULL,
    UNIQUE (task_id, artifact_id, role, port_id)
);

CREATE INDEX idx_task_artifacts_task_id ON task_artifacts(task_id);
CREATE INDEX idx_task_artifacts_artifact_id ON task_artifacts(artifact_id);
CREATE INDEX idx_task_artifacts_role ON task_artifacts(role);
```

规则：

- Worker 产出的 artifact：写入 `artifacts`，并写入 role=`output` 的 `task_artifacts`。
- cache hit：不复制 artifact 文件；写入 role=`cache_hit` 的 `task_artifacts`，并设置 `execution_tasks.cache_hit = 1`。
- 下游输入：Scheduler 根据依赖关系写入 role=`input` 的 `task_artifacts`。
- 用户最终导出：ArtifactFinalizer 写入 role=`final_output` 的 `task_artifacts`，并保留原始 staged artifact 记录。

---

### 3.9 task_events

Worker 事件持久化。**只追加，不更新**。完整保留事件流用于调试和审计。

```sql
CREATE TABLE task_events (
    event_id    TEXT PRIMARY KEY,                  -- ULID
    task_id     TEXT NOT NULL REFERENCES execution_tasks(task_id),
    event_type  TEXT NOT NULL
                CHECK (event_type IN (
                    'started', 'progress', 'log',
                    'artifact', 'completed', 'failed', 'heartbeat'
                )),
    payload     TEXT NOT NULL DEFAULT '{}',        -- JSON: 事件全部字段
    seq         INTEGER NOT NULL,                  -- Worker 发送的序列号
    timestamp   TEXT NOT NULL,                     -- 事件时间戳
    UNIQUE (task_id, seq)
);

CREATE INDEX idx_task_events_task_id ON task_events(task_id);
CREATE INDEX idx_task_events_task_type ON task_events(task_id, event_type);
CREATE INDEX idx_task_events_timestamp ON task_events(timestamp);
```

### 存储策略

- task_events 是高频写入表。建议对已完成 Job 的 events 定期归档或清理。
- progress 和 heartbeat 事件数量可能很大。可配置策略：只保留最新 N 条 progress，或只保留 10% 采样。
- started / completed / failed / artifact 事件始终保留。

---

### 3.10 resource_locks

运行时资源占用状态。Scheduler 在分配资源时写入，任务完成或释放时更新。

```sql
CREATE TABLE resource_locks (
    lock_id       TEXT PRIMARY KEY,                -- ULID
    task_id       TEXT NOT NULL REFERENCES execution_tasks(task_id),
    device_id     TEXT NOT NULL,                   -- "cuda:0", "cpu" 等
    lock_type     TEXT NOT NULL
                  CHECK (lock_type IN ('exclusive', 'shared')),
    vram_mb       INTEGER,                         -- 占用的 VRAM
    owner_pid     INTEGER,                         -- 持有锁的 Worker 进程 PID
    acquired_at   TEXT NOT NULL,
    heartbeat_at  TEXT,                            -- 锁持有者最近心跳
    stale_after   TEXT,                            -- 超过该时间未释放可视为 stale
    released_at   TEXT                             -- NULL 表示仍持有
);

CREATE INDEX idx_resource_locks_device_id ON resource_locks(device_id);
CREATE INDEX idx_resource_locks_active ON resource_locks(device_id, released_at);
```

### 活跃锁查询

```sql
SELECT * FROM resource_locks
WHERE device_id = :device_id AND released_at IS NULL;
```

---

### 3.11 cache_entries

缓存索引。记录哪些 artifact 可以被后续相同参数的任务复用。

```sql
CREATE TABLE cache_entries (
    cache_key           TEXT PRIMARY KEY,          -- node_type + versions + params_hash + input_hash
    node_type           TEXT NOT NULL,
    node_version        TEXT NOT NULL,
    artifact_id         TEXT NOT NULL REFERENCES artifacts(artifact_id),
    params_hash         TEXT NOT NULL,             -- 参数部分的 hash
    input_hash          TEXT NOT NULL,             -- 输入 artifact 的 hash
    runtime_fingerprint TEXT NOT NULL DEFAULT '',  -- backend / engine / worker / hardware-sensitive settings
    model_fingerprint   TEXT NOT NULL DEFAULT '',  -- model id + model version/hash
    created_at          TEXT NOT NULL,
    last_hit_at         TEXT,                      -- 上次命中时间
    hit_count           INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_cache_entries_node_type ON cache_entries(node_type);
CREATE INDEX idx_cache_entries_node_version ON cache_entries(node_type, node_version);
CREATE INDEX idx_cache_entries_last_hit ON cache_entries(last_hit_at);
```

### Cache Key 计算

```text
cache_key = sha256(
    node_type
    + node_version
    + sorted(cache_key_fields 对应的 param_values)
    + sorted(input_artifact_hashes)
    + runtime_fingerprint
    + model_fingerprint
)
```

---

### 3.12 presets

Workflow 预设模板。用户可保存和复用常用 workflow。

```sql
CREATE TABLE presets (
    preset_id    TEXT PRIMARY KEY,                 -- ULID
    name         TEXT NOT NULL,
    category     TEXT NOT NULL DEFAULT 'general',  -- 分类标签
    description  TEXT NOT NULL DEFAULT '',
    graph_json   TEXT NOT NULL,                    -- WorkflowGraph JSON（与 workflow_graphs.graph_json 格式一致）
    is_builtin   INTEGER NOT NULL DEFAULT 0,       -- 0/1 是否为内置预设
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL
);

CREATE INDEX idx_presets_category ON presets(category);
CREATE INDEX idx_presets_name ON presets(name);
```

---

### 3.13 runtime_components

RuntimeManager 管理的软件组件记录，包括 FFmpeg、ffprobe、llama.cpp、whisper.cpp、ncnn-vulkan backend、Python worker environment 等。

```sql
CREATE TABLE runtime_components (
    component_id   TEXT PRIMARY KEY,              -- ULID
    name           TEXT NOT NULL,                 -- "ffmpeg", "llama.cpp" 等逻辑名
    version        TEXT NOT NULL,
    kind           TEXT NOT NULL
                   CHECK (kind IN (
                       'app', 'python_env', 'tool', 'library', 'backend'
                   )),
    install_path   TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'missing'
                   CHECK (status IN (
                       'missing', 'installing', 'ready', 'broken', 'disabled'
                   )),
    hash           TEXT,
    metadata_json  TEXT NOT NULL DEFAULT '{}',
    installed_at   TEXT,
    last_checked_at TEXT
);

CREATE UNIQUE INDEX idx_runtime_components_name_version ON runtime_components(name, version);
CREATE INDEX idx_runtime_components_status ON runtime_components(status);
```

### 3.14 model_assets

Atelier 管理的本地模型资产。节点参数中的 `MODEL_ID` 应引用此表或其上层 model store。

```sql
CREATE TABLE model_assets (
    model_id       TEXT PRIMARY KEY,              -- stable model id
    display_name   TEXT NOT NULL,
    backend        TEXT NOT NULL,                 -- "faster-whisper", "llama.cpp", "realesrgan" 等
    version        TEXT NOT NULL DEFAULT '',
    local_path     TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'missing'
                   CHECK (status IN (
                       'missing', 'downloading', 'ready', 'broken', 'disabled'
                   )),
    hash           TEXT,
    size_bytes     INTEGER,
    metadata_json  TEXT NOT NULL DEFAULT '{}',
    created_at     TEXT NOT NULL,
    updated_at     TEXT NOT NULL
);

CREATE INDEX idx_model_assets_backend ON model_assets(backend);
CREATE INDEX idx_model_assets_status ON model_assets(status);
```

### 3.15 credential_refs

凭据引用记录。真实 secret 必须存放在 OS credential storage 或受控 credential backend 中，SQLite 只保存引用和元信息。

```sql
CREATE TABLE credential_refs (
    credential_ref_id TEXT PRIMARY KEY,            -- ULID
    provider          TEXT NOT NULL,               -- "openai", "deepl", "custom_llm" 等
    account_label     TEXT NOT NULL DEFAULT '',    -- GUI 显示标签，不含 secret
    purpose           TEXT NOT NULL DEFAULT '',    -- "translation", "asr", "model_download" 等
    backend           TEXT NOT NULL DEFAULT 'os',  -- "os", "keyring", "none"
    status            TEXT NOT NULL DEFAULT 'active'
                      CHECK (status IN (
                          'active', 'missing', 'revoked', 'disabled'
                      )),
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL,
    last_checked_at   TEXT
);

CREATE INDEX idx_credential_refs_provider ON credential_refs(provider);
CREATE INDEX idx_credential_refs_status ON credential_refs(status);
```

规则：

- 不在 SQLite 中存储 API key、bearer token、refresh token 或 provider password。
- `credential_ref_id` 可被任务参数或 provider config 引用。
- 删除 credential reference 不应删除历史 Job 记录，但会让需要该凭据的新任务进入 `credential_missing` 状态。

---

## 4. 索引策略总结

| 表 | 索引 | 理由 |
|---|---|---|
| `jobs` | `project_id`, `status`, `created_at` | 按项目筛选、按状态过滤、按时间排序 |
| `execution_tasks` | `plan_id`, `status`, `node_type`, `cache_key` | 按计划查任务、按状态过滤、缓存命中查询 |
| `task_dependencies` | `depends_on_task_id` | 反向查找下游任务 |
| `artifacts` | `task_id`, `artifact_type`, `hash` | 按任务查产物、按类型过滤、缓存匹配 |
| `task_artifacts` | `task_id`, `artifact_id`, `role` | 查任务输入/输出、cache hit 复用和最终导出 |
| `task_events` | `task_id`, `(task_id, event_type)`, `timestamp` | 按任务查事件、按类型过滤、按时间排序 |
| `resource_locks` | `device_id`, `(device_id, released_at)` | 查设备当前锁定状态 |
| `cache_entries` | `node_type`, `last_hit_at` | 按类型查缓存、LRU 清理 |
| `presets` | `category`, `name` | 分类浏览、名称搜索 |
| `runtime_components` | `(name, version)`, `status` | 查组件可用性和修复状态 |
| `model_assets` | `backend`, `status` | 查模型资产和 backend 可用性 |
| `credential_refs` | `provider`, `status` | 查 provider 凭据引用和缺失状态 |

## 5. 状态机映射

### Job Status

```text
draft → queued → running → completed
                    │
                    ├──→ failed
                    └──→ cancelled
```

与 `execution_plans.status` 联动：当 plan 完成时 job 完成，当 plan 失败时 job 失败。

### Task Status

与 EXECUTION_PLAN_SPEC §12 的状态机完全一致：

```text
pending → queued → running → completed
                      │
                      ├──→ failed → retry_pending → queued
                      │       │
                      │       └──→ (max retries → stay failed)
                      └──→ cancelled

pending → skipped
```

`execution_tasks.status` 列的 CHECK 约束覆盖所有合法状态值。

## 6. JSON 字段策略

| 字段 | 表 | 理由 |
|---|---|---|
| `graph_json` | workflow_graphs | 不可变快照，整存整取，不需要库内节点级查询 |
| `graph_json` | presets | 同上，模板存储 |
| `phases_json` | execution_plans | Phase/Lane 结构嵌套深，整取后在内存中操作 |
| `conflicts_json` | execution_plans | 验证结果，展示用 |
| `hardware_snapshot` | execution_plans | 快照数据，不需查询 |
| `params_json` | execution_tasks | 参数结构因 node_type 而异，无法统一列 |
| `resource_request` | execution_tasks | 嵌套结构，整取后在内存中操作 |
| `resource_binding` | execution_tasks | 同上 |
| `runtime_request` | execution_tasks | Runtime 需求因 node_type 而异 |
| `runtime_binding` | execution_tasks | RuntimeManager 解析结果，整取后传给 Worker |
| `failure_policy` | execution_tasks | 同上 |
| `metadata_json` | artifacts | 元信息因 artifact_type 而异 |
| `payload` | task_events | 事件载荷因 event_type 而异 |
| `metadata_json` | runtime_components | 组件能力、来源、校验信息因组件而异 |
| `metadata_json` | model_assets | 模型格式、量化、许可、上下文长度等因模型而异 |
| `input_media_paths` | jobs | 简单列表 |

**判断标准**：

- 需要 WHERE / JOIN / GROUP BY → 拆为独立列或表。
- 只读 / 整存整取 / 结构因类型而异 → JSON。

## 7. ER 关系总览

```text
projects
  └──< jobs
         ├──→ workflow_graphs
         └──< execution_plans
                └──< execution_tasks
                       ├──< task_dependencies
                       ├──< artifacts
                       │      ├──< task_artifacts
                       │      └──< cache_entries
                       ├──< task_events
                       └──< resource_locks

presets (独立表，不与 jobs 关联)
runtime_components (RuntimeManager 管理表)
model_assets (RuntimeManager / model store 管理表)
credential_refs (SecurityManager / credential backend 引用表)
```

`<` 表示一对多关系，`→` 表示引用关系。

## 8. Migration 策略

### 首版

- 手写 `CREATE TABLE` 语句，在 `atelier/storage/schema.sql` 中维护。
- 应用启动时检查数据库是否存在，不存在则执行建表。
- 用 `PRAGMA user_version` 标记 schema 版本号。

### 后续版本

- schema 变化时引入 Alembic。
- 每次变更生成 migration 文件。
- 应用启动时自动运行 pending migrations。
- 不直接修改 schema.sql，通过 Alembic 管理所有变更。

### 建议初始化代码结构

```text
atelier/storage/
    db.py              # 数据库连接和初始化
    schema.sql         # 首版 CREATE TABLE 语句
    models.py          # SQLAlchemy model 定义
    repositories/      # 按领域划分的数据访问层
        job_repo.py
        task_repo.py
        artifact_repo.py
        event_repo.py
        cache_repo.py
        preset_repo.py
    migrations/        # 未来 Alembic 目录
```

## 9. 与其他文档的关系

```text
WORKFLOW_NODE_SPEC
  → workflow_graphs 表：graph_json 存储 WorkflowGraph 完整序列化。
  → presets 表：graph_json 同格式。

EXECUTION_PLAN_SPEC
  → execution_plans 表：phases_json / conflicts_json / hardware_snapshot。
  → execution_tasks 表：每个 ExecutionTask 一行，支持状态跟踪。
  → task_dependencies 表：Task 依赖关系。
  → resource_locks 表：运行时资源占用。

WORKER_PROTOCOL
  → task_events 表：所有 WorkerEvent 追加存储。
  → artifacts 表：Worker 产出的 artifact 记录。

TRANSLATE_AGENT_SPEC
  → artifacts 表：`ocr_text_track` 存储 OCR 文字轨道，`subtitle` 存储翻译字幕，`metadata` 存储 fusion / warnings sidecar。
  → credential_refs 表：远程翻译 provider / OpenAI-compatible provider / DeepL 等只保存 credential reference，不保存 secret。

RuntimeManager
  → runtime_components 表：软件 runtime 组件安装、校验和状态。
  → model_assets 表：本地模型资产、backend 和校验状态。
  → execution_tasks.runtime_binding：任务启动时使用的具体 runtime 解析结果。

SECURITY_PRIVACY_SPEC
  → credential_refs 表：只保存凭据引用和状态，不保存 secret 明文。
  → task_events 表：事件 payload 必须经过 redaction 后再存储。
```
