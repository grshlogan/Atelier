# Atelier Execution Plan Spec

> 状态：规划中，尚未实现。本文档定义 WorkflowGraph 如何转变为可调度的执行计划——阶段划分、泳道并行、硬件绑定、冲突检测和状态机。

## 1. 概述

ExecutionPlan 是 Atelier 的执行层核心。它回答"Workflow 里的每一步该怎么在本机硬件上跑起来"。

```text
WorkflowGraph（描述做什么）
  → ExecutionPlanner（规划怎么做）
    → ExecutionPlan（阶段 + 泳道 + 资源绑定）
      → Scheduler（决定何时运行）
        → Worker（实际执行）
```

ExecutionPlan 不直接运行任务。它是一份"执行蓝图"，由 Scheduler 消费。用户可以在 Execution Canvas 上查看和调整这份蓝图的硬件分配，但不能绕过 Scheduler 直接运行。

## 2. 核心概念

| 概念 | 含义 |
|---|---|
| Phase（阶段） | 串行执行的大步骤。Phase 0 完成后才开始 Phase 1 |
| Lane（泳道） | 同一 Phase 内可并行的执行轨道。不同 Lane 可同时运行 |
| ExecutionTask | Lane 内的原子执行单元，对应一个 WorkflowNode |
| ResourceRequest | Task 声明的资源需求 |
| ResourceBinding | Scheduler 分配的具体资源 |
| RuntimeRequest | Task 声明的软件运行环境需求 |
| RuntimeBinding | RuntimeManager 解析出的可执行环境、工具路径和模型路径 |
| HardwareSnapshot | 计划生成时刻的硬件快照 |
| Conflict | 资源冲突记录 |

### 执行模型

```text
Phase 0 ─────────────────────────────> Phase 1 ──────────> Phase 2
  ├── Lane A: [Task_input_video]         ├── Lane C: [Task_translate]   ├── Lane E: [Task_mux]
  └── Lane B: [Task_asr]                 └── Lane D: [Task_review]     └── Lane F: [Task_export]
       (依赖 Lane A 产物)                     (依赖 Lane C 产物)
```

- **Phase 间串行**：上一个 Phase 的所有 Lane 完成后，下一个 Phase 才开始。
- **Lane 间并行**：同一 Phase 内的不同 Lane 可并行执行（受资源约束）。
- **Lane 内串行**：同一 Lane 内的多个 Task 按依赖顺序串行执行。

## 3. ExecutionPlan Schema

```python
class PlanStatus(str, Enum):
    DRAFT     = "draft"       # 刚生成，未验证
    VALIDATED = "validated"   # 通过验证，可调度
    SCHEDULED = "scheduled"   # 已进入 Scheduler 队列
    RUNNING   = "running"     # 正在执行
    COMPLETED = "completed"   # 全部完成
    FAILED    = "failed"      # 存在失败且不可恢复
    CANCELLED = "cancelled"   # 用户取消

class ExecutionPlan(BaseModel):
    plan_id:            str                    # ULID
    job_id:             str                    # 所属 Job
    workflow_graph_id:  str                    # 来源 WorkflowGraph
    status:             PlanStatus = PlanStatus.DRAFT

    phases:             list[ExecutionPhase]
    conflicts:          list[Conflict] = []    # 冲突检测结果
    hardware_snapshot:  HardwareSnapshot       # 生成时硬件状态

    created_at:         str                    # ISO 8601 UTC
    updated_at:         str                    # ISO 8601 UTC
```

## 4. ExecutionPhase Schema

```python
class ExecutionPhase(BaseModel):
    phase_id:           str                    # ULID 或 "phase_0" 等
    phase_index:        int                    # 0-based 顺序号
    name:               str                    # 人类可读名，如 "媒体输入 + ASR"
    lanes:              list[ExecutionLane]
    depends_on_phases:  list[str] = []         # 前置 Phase ID 列表
```

## 5. ExecutionLane Schema

```python
class ExecutionLane(BaseModel):
    lane_id:            str                    # ULID
    name:               str                    # 人类可读名，如 "ASR 轨道"
    tasks:              list[ExecutionTask]     # Lane 内按序执行
    lane_resource_hint: ResourceRequest | None = None    # UI 分组/偏好，不是最终资源事实源
```

`ExecutionTask.resource_binding` 是最终硬件绑定事实源。`ExecutionLane.lane_resource_hint` 只表达 UI 分组、用户偏好或批量调整意图；Scheduler 重新调度后必须把最终结果写回每个 Task。

## 6. ExecutionTask Schema

```python
class TaskStatus(str, Enum):
    PENDING       = "pending"
    QUEUED        = "queued"
    RUNNING       = "running"
    COMPLETED     = "completed"
    FAILED        = "failed"
    RETRY_PENDING = "retry_pending"
    SKIPPED       = "skipped"
    CANCELLED     = "cancelled"

class ArtifactSlot(BaseModel):
    slot_id:        str                        # 预期产物的插槽标识
    artifact_type:  str                        # "video", "audio", "subtitle" 等
    expected_path:  str | None = None          # 预期输出路径（Worker 完成后回填实际路径）

class ExecutionTask(BaseModel):
    task_id:              str                  # ULID
    source_node_id:       str                  # 回溯到 WorkflowNode.node_id
    node_type:            str                  # 节点类型名

    params:               dict[str, Any]       # 实际运行参数（已展开默认值）

    input_artifacts:      list[str]            # 依赖的 artifact_id（运行时解析）
    output_artifact_slots: list[ArtifactSlot]  # 预期产出

    resource_request:     ResourceRequest      # 声明的资源需求
    resource_binding:     ResourceBinding | None = None  # Scheduler 分配后填入
    runtime_request:      RuntimeRequest       # 声明的软件运行环境需求
    runtime_binding:      RuntimeBinding | None = None   # RuntimeManager 解析后填入

    status:               TaskStatus = TaskStatus.PENDING
    failure_policy:       FailurePolicy        # 从 WorkflowNode 继承
    depends_on_tasks:     list[str] = []       # 前置 Task ID
    cache_key:            str | None = None    # 缓存键
    retry_count:          int = 0              # 当前已重试次数

    started_at:           str | None = None
    completed_at:         str | None = None
    error_message:        str | None = None
```

### 字段说明

- `params`：合并 NodeRegistryEntry 的默认参数和用户在 WorkflowNode.param_values 中的覆盖值，生成最终执行参数。
- `input_artifacts`：初始为空列表。上游 Task 完成后，Scheduler 根据 edge 关系填入上游 artifact_id。
- `cache_key`：由 `node_type + 版本 + cache_key_fields 对应的 param 值 + 输入 artifact hash + runtime/model/backend 版本` 计算得出。如果 cache_entries 中存在匹配的 key，Scheduler 可跳过执行直接复用产物。

## 7. ResourceRequest / ResourceBinding

```python
class ResourceRequest(BaseModel):
    device_type:    DeviceType = DeviceType.ANY   # "gpu" | "cpu" | "any"
    vram_mb:        int | None = None             # 需要的 VRAM
    exclusive:      bool = False                  # 是否独占设备
    cpu_cores:      int | None = None             # 需要的 CPU 核心数

class ResourceBinding(BaseModel):
    device_id:        str                         # 实际设备 ID（如 "cuda:0", "cpu"）
    allocated_vram_mb: int | None = None          # 分配的 VRAM
    shared_with:      list[str] = []              # 同设备上并行的其他 task_id
    binding_reason:   str = ""                    # 分配原因（调试用）
```

```python
class RuntimeRequest(BaseModel):
    components:    list[str] = []                 # "ffmpeg", "llama.cpp", "faster-whisper" 等
    capabilities:  list[str] = []                 # "cuda", "vulkan", "cpu", "avx2" 等
    model_ids:     list[str] = []                 # Atelier model store 中的模型 ID

class RuntimeBinding(BaseModel):
    runtime_id:       str                         # RuntimeManager 生成的环境 ID
    component_paths:  dict[str, str] = {}         # 组件名 -> 可执行文件或库目录
    model_paths:      dict[str, str] = {}         # model_id -> 本地模型目录或文件
    env:              dict[str, str] = {}         # 仅传给 Worker 的环境变量
    binding_reason:   str = ""                    # 解析原因（调试用）
```

`RuntimeBinding` 只描述软件运行环境，不分配硬件资源。硬件由 `ResourceBinding` 表达，二者都由 Scheduler 启动 Worker 前统一确认。

### Scheduler 分配规则

1. Scheduler 遍历 Phase 内所有 Lane 的 Task，收集 ResourceRequest。
2. 按优先级（exclusive > shared > any）排列。
3. 根据 HardwareSnapshot 的可用资源逐个分配。
4. exclusive Task 独占设备；shared Task 可与其他 shared Task 共享设备（VRAM 总和不超限）。
5. 无法满足的 Task 标记 Conflict 并等待前置 Task 释放资源后重新分配。

## 8. HardwareSnapshot Schema

```python
class GPUInfo(BaseModel):
    device_id:    str                             # "cuda:0", "cuda:1" 等
    name:         str                             # "NVIDIA RTX 4090"
    vram_total_mb: int
    vram_free_mb: int
    driver_version: str

class HardwareSnapshot(BaseModel):
    gpus:           list[GPUInfo]
    cpu_cores:      int
    ram_total_mb:   int
    ram_free_mb:    int
    captured_at:    str                           # ISO 8601 UTC
```

HardwareSnapshot 在 ExecutionPlan 生成时捕获一次，用于冲突检测和计划验证。运行时 Scheduler 使用实时硬件状态做最终调度决策。

## 9. 计划生成规则

ExecutionPlanner 从 WorkflowGraph 生成 ExecutionPlan 的步骤：

### 9.1 拓扑排序

1. 对 WorkflowGraph 执行拓扑排序，得到节点的分层（topological levels）。
2. 同一层的节点之间无依赖关系。

### 9.2 Phase 划分

3. 将拓扑层合并为 Phase。合并策略：
   - 相邻层且所有节点的 `resource_hint.exclusive_gpu` 都为 `False` 时，可考虑合并到同一 Phase。
   - 存在 `exclusive_gpu = True` 的层通常独立成 Phase 或与同设备无冲突的层合并。
   - 默认策略：每个拓扑层 = 一个 Phase。高级策略未来可优化。

### 9.3 Lane 分配

4. 每个 Phase 内，将无依赖关系的节点分配到不同 Lane，允许并行。
5. 有依赖关系的节点放入同一 Lane 按序执行。

### 9.4 Task 生成

6. 每个 WorkflowNode 生成一个 ExecutionTask。
7. 填充 `params`（合并默认值和用户值）。
8. 填充 `resource_request`（从 WorkflowNode.resource_hint 转换）。
9. 填充 `depends_on_tasks`（从 WorkflowEdge 推导）。
10. 计算 `cache_key`。

### 9.5 验证与冲突检测

11. 运行冲突检测（见 §10）。
12. 无 error 级 Conflict 时状态设为 `validated`。
13. 存在 error 级 Conflict 时状态保持 `draft`，用户需在 Execution Canvas 调整。

## 10. 冲突检测

```python
class ConflictSeverity(str, Enum):
    ERROR   = "error"       # 阻止执行
    WARNING = "warning"     # 可执行但有风险

class ConflictCode(str, Enum):
    VRAM_OVERFLOW       = "vram_overflow"
    EXCLUSIVE_CONFLICT  = "exclusive_conflict"
    DEVICE_MISSING      = "device_missing"
    UPSTREAM_FAILURE    = "upstream_failure"
    INSUFFICIENT_RAM    = "insufficient_ram"
    CIRCULAR_DEPENDENCY = "circular_dependency"

class Conflict(BaseModel):
    conflict_id:    str                        # ULID
    code:           ConflictCode
    severity:       ConflictSeverity
    phase_id:       str | None = None
    lane_id:        str | None = None
    task_ids:       list[str]                  # 涉及的 Task
    device_id:      str | None = None          # 涉及的设备
    message:        str                        # 人类可读描述
    suggested_fix:  str = ""                   # 建议修复动作
```

| 冲突码 | 含义 | 严重度 | 建议修复 |
|---|---|---|---|
| `vram_overflow` | 同 Phase 并行 Task 的 VRAM 需求总和超过设备可用 VRAM | error | 移动 Task 到不同 Phase 或分配到不同 GPU |
| `exclusive_conflict` | 同 Phase 同设备存在多个 exclusive Task | error | 将 exclusive Task 分到不同 Phase |
| `device_missing` | Task 请求的设备类型在系统中不存在（如无 GPU） | error | 修改 resource_request 或安装硬件 |
| `upstream_failure` | 上游 Task 已 failed 且 failure_policy 不允许 skip | warning | 处理上游失败 |
| `insufficient_ram` | 系统 RAM 不足以支撑并行 Task | warning | 减少并行度 |
| `circular_dependency` | Task 依赖图存在环 | error | 修复 WorkflowGraph |

## 11. 计划调整

用户在 Execution Canvas 上可执行以下调整：

| 操作 | 效果 |
|---|---|
| 修改 Lane 的 device 偏好 | 更新 `lane_resource_hint`，清空受影响 Task 的 `resource_binding`，由 Scheduler 重新计算 |
| 将 Task 移到其他 Lane | 更新 Lane 归属，需保持依赖合法 |
| 将 Task 移到其他 Phase | 更新 Phase 归属，需保持依赖合法 |
| 标记 Task 为 skip | 设置 status = `skipped` |
| 调整 failure_policy | 覆盖从 WorkflowNode 继承的策略 |

### 调整约束

- 任何调整后必须重新运行冲突检测。
- 不可将 Task 移到其依赖 Task 之前的 Phase。
- 不可绕过 Scheduler 直接启动 Task。
- 调整操作记录到 plan.updated_at。
- `ExecutionLane.lane_resource_hint` 不是执行事实源；运行时只信任 `ExecutionTask.resource_binding`。
- `runtime_binding` 不由用户手写，必须由 RuntimeManager 根据 RuntimeRequest 和 RuntimeManifest 解析。

### 11.1 OCR / Translate Agent 降级依赖

`translate.llm` 是首个需要 optional / degraded dependency 表达的内置卡片。默认推荐：

```text
ASR completed + OCR completed -> ASR + OCR fusion
ASR completed + OCR failed    -> ASR-only with warning
ASR failed + OCR completed    -> OCR-only draft if policy allows
ASR failed + OCR failed       -> blocked
```

ExecutionPlanner / Scheduler 不应把 `translate.llm` 固定成必须同时依赖 `asr.whisper` 和 `ocr.recognition` 成功。具体策略由 `TRANSLATE_AGENT_SPEC.md`、`BATCH_PIPELINE_SCHEDULING_SPEC.md` 和后续 NodeRegistry dependency policy 细化。

## 12. TaskStatus 状态机

```text
                   ┌──────────────────────────────────────────────────┐
                   │                                                  │
                   v                                                  │
  pending ──→ queued ──→ running ──→ completed                       │
                            │                                         │
                            ├──→ failed ──→ retry_pending ──→ queued ─┘
                            │       │
                            │       └──→ (max_retries exhausted → stay failed)
                            │
                            └──→ cancelled

  pending ──→ skipped  (上游失败 + on_failure == skip)
```

### 状态转换规则

| 从 | 到 | 触发条件 |
|---|---|---|
| `pending` | `queued` | Scheduler 将 Task 加入执行队列 |
| `pending` | `skipped` | 上游 Task failed 且当前 Task 的 failure_policy 为 skip |
| `queued` | `running` | Scheduler 启动 Worker 进程 |
| `running` | `completed` | Worker 发送 `completed` 事件 |
| `running` | `failed` | Worker 发送 `failed` 事件，或心跳超时 |
| `running` | `cancelled` | 用户取消或 Scheduler 取消 |
| `failed` | `retry_pending` | retry_count < max_retries |
| `retry_pending` | `queued` | Scheduler 重新排队 |

### Job 状态联动

- 当 Plan 中所有 Task 为 `completed` 或 `skipped` 时，Plan.status → `completed`。
- 当任一 Task 为 `failed` 且无法重试、无法 skip 时，Plan.status → `failed`。
- 用户取消时，所有未完成 Task 标记 `cancelled`，Plan.status → `cancelled`。
- 如果 Worker 发送 `failed` 且 `error_code == CANCELLED`，Scheduler 必须将该 Task 归一化为 `cancelled`，而不是普通 `failed`。

## 13. 完整示例

以 WORKFLOW_NODE_SPEC §14 的"字幕翻译流程"为输入，生成的 ExecutionPlan 结构示意：

```text
ExecutionPlan
  plan_id: "01JWF9PLAN000000000000001"
  job_id:  "01JWF9JOB0000000000000001"
  status:  validated

  Phase 0 "媒体输入"
    └── Lane A
          └── Task: input.video (pending)
                     resource: cpu
                     output_slots: [video, audio]

  Phase 1 "ASR 识别"
    └── Lane B
          └── Task: asr.whisper (pending)
                     resource: gpu:<selected_gpu>, exclusive, 4096MB
                     depends_on: [Task_input_video]
                     output_slots: [subtitle]

  Phase 2 "翻译"
    └── Lane C
          └── Task: translate.llm (pending)
                     resource: cpu
                     depends_on: [Task_asr]
                     output_slots: [subtitle]

  Phase 3 "封装 + 导出"
    └── Lane D
          ├── Task: compose.mux_subtitle (pending)
          │          resource: cpu
          │          depends_on: [Task_input_video, Task_translate]
          │          output_slots: [video]
          └── Task: output.export (pending)
                     resource: cpu
                     depends_on: [Task_mux]
                     output_slots: []
```

同一 Lane 内按依赖顺序串行执行，避免把 `output.export` 与它依赖的 `compose.mux_subtitle` 放入可并行的不同 Lane。

## 14. 与其他文档的关系

```text
WORKFLOW_NODE_SPEC
  → (本文档) EXECUTION_PLAN_SPEC：
      WorkflowGraph 是 ExecutionPlanner 的输入。
      WorkflowNode.resource_hint → ExecutionTask.resource_request。
      WorkflowNode.runtime_requirements → ExecutionTask.runtime_request。
      WorkflowNode.failure_policy → ExecutionTask.failure_policy。
      WorkflowEdge → ExecutionTask.depends_on_tasks。

EXECUTION_PLAN_SPEC (本文档)
  → WORKER_PROTOCOL：
      ExecutionTask 序列化为 task.json 交给 Worker 执行。
      TaskStatus 由 Worker 事件驱动更新。
  → DATABASE_SCHEMA：
      execution_plans 表持久化 ExecutionPlan。
      execution_tasks 表持久化每个 ExecutionTask。
      task_dependencies 表持久化 depends_on_tasks。
      resource_locks 表跟踪运行时资源占用。
      runtime_components / model_assets 表跟踪 RuntimeManager 管理的组件和模型资产。
```
