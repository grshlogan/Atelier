# Atelier Worker Protocol

> 状态：部分实现。已实现 `WorkerEvent` JSON Lines 编解码、最小 stdout event stream validation、最小 subprocess runner 边界、`log` / `heartbeat` 事件模型和协议错误边界；stdin 控制通道、heartbeat timeout、stderr 落盘、生产级 worker lifecycle 和真实 adapters 尚未实现。

## 1. 概述

Worker 是 Atelier 中实际执行重型任务的独立进程。Scheduler 根据 ExecutionPlan 启动 Worker，Worker 通过 JSON Lines 事件流向 Scheduler 汇报进度和结果。

```text
Scheduler
  ├── 启动 Worker 进程（subprocess）
  ├── 读取 Worker stdout（JSON Lines 事件）
  ├── 存储 stderr（人类可读日志）
  ├── 向 Worker stdin 发送控制指令
  ├── 监控心跳
  └── 根据事件更新 ExecutionTask 状态和 artifact 记录
```

### 核心原则

- **一个 Worker 进程对应一个 ExecutionTask**。不做多任务复用。
- **GUI 只信任结构化事件和数据库状态**，不从 stderr 日志中解析主进度。
- **Worker 不直接写数据库**。所有持久化由 Scheduler 根据事件完成。
- **Worker 不覆盖非自己任务的文件**。产物写入隔离的 task 目录。

## 2. 通信模型

```text
┌─────────────┐     stdin (控制指令)      ┌─────────────┐
│             │ ──────────────────────→   │             │
│  Scheduler  │                           │   Worker    │
│             │ ←────────────────────── 　│             │
│             │     stdout (JSON Lines)   │             │
│             │ ←────────────────────── 　│             │
└─────────────┘     stderr (调试日志)      └─────────────┘
```

| 通道 | 方向 | 格式 | 用途 |
|---|---|---|---|
| stdout | Worker → Scheduler | JSON Lines | 结构化事件（进度、artifact、完成、失败） |
| stderr | Worker → Scheduler | 自由文本 | 人类可读调试日志，存储但不解析 |
| stdin | Scheduler → Worker | JSON Lines | 控制指令（cancel、pause，预留） |

## 3. Worker 启动协议

### 3.1 启动命令

```bash
python -m atelier.workers.run --task-file <path_to_task.json>
```

`task.json` 是 ExecutionTask 的完整序列化（见 EXECUTION_PLAN_SPEC §6），包含 task_id、node_type、params、input_artifacts、output_artifact_slots 等全部信息。

### 3.2 启动序列

```text
Scheduler:
  1. 将 ExecutionTask 序列化为 task.json 写入工作目录
  2. 创建 task 工作目录：{work_dir}/{task_id}/
  3. 启动 subprocess
  4. 设置 Task 状态 → running
  5. 开始监听 stdout

Worker:
  1. 读取 task.json
  2. 加载对应 adapter（根据 node_type 查找）
  3. 验证输入文件/artifact 存在
  4. 发送 started 事件
  5. 开始执行
```

### 3.3 环境约定

- 工作目录：`{work_dir}/{task_id}/`
- 临时文件写入工作目录，使用 `.part` 后缀。
- Worker 进程不应修改工作目录之外的文件。
- Worker 进程不应读取或依赖 Atelier 数据库。
- Worker 进程不应假设系统 `PATH` 中存在 FFmpeg、CUDA 工具、llama.cpp、whisper.cpp 或模型文件。
- Scheduler 启动 Worker 前必须通过 RuntimeManager 解析 `runtime_binding`，并把组件路径、模型路径和必要环境变量写入 `task.json` 或 Worker 环境。
- Worker 只能使用 `runtime_binding` 中声明的外部工具和模型路径；缺失时返回 `RUNTIME_MISSING` 或 `DEPENDENCY`，不自行安装依赖。
- 面向用户的最终导出路径由 Scheduler / ArtifactFinalizer 负责确认和落盘。Worker 包括 `output.export` adapter 在内，只能先写入自己的 task 工作目录并产出可验证 artifact。

## 4. 事件类型 (WorkerEvent)

所有事件共享以下公共字段：

```python
class WorkerEvent(BaseModel):
    type:       str         # 事件类型名
    task_id:    str         # 所属 ExecutionTask
    timestamp:  str         # ISO 8601 UTC
    seq:        int         # 递增序列号（从 0 开始）
```

`seq` 用于事件排序和丢失检测。当前 protocol helper 会把非连续 `seq` 视为 `WorkerProtocolError`；未来 Scheduler 可以捕获该错误并记录 warning、失败原因或恢复事实。

---

### 4.1 started

Worker 启动成功，准备执行。**必须是 Worker 发出的第一个事件**。

```python
class StartedEvent(WorkerEvent):
    type:            Literal["started"] = "started"
    worker_pid:      int
    worker_version:  str          # adapter 版本
    node_type:       str          # 确认实际使用的 node_type
```

```json
{"type":"started","task_id":"01JWF9TASK00000000000001","timestamp":"2026-05-03T10:00:01Z","seq":0,"worker_pid":12345,"worker_version":"1.0.0","node_type":"asr.whisper"}
```

---

### 4.2 progress

执行进度更新。

```python
class ProgressEvent(WorkerEvent):
    type:         Literal["progress"] = "progress"
    current:      int                # 已完成数量
    total:        int                # 总数量
    unit:         str                # "frames" | "tokens" | "bytes" | "steps" | "segments"
    percent:      float              # current/total * 100，冗余字段方便 GUI
    stage:        str = ""           # 当前子阶段名
    eta_seconds:  float | None = None
```

```json
{"type":"progress","task_id":"01JWF9TASK00000000000001","timestamp":"2026-05-03T10:00:15Z","seq":5,"current":250,"total":1000,"unit":"frames","percent":25.0,"stage":"inference","eta_seconds":45.0}
```

### 进度上报频率

- 建议每处理 1-5% 或每 2-5 秒上报一次，取先到者。
- 不应每帧/每 token 上报（会淹没事件流）。
- 长阶段（如模型加载）应在开始和结束时各发一次 progress。

---

### 4.3 log

结构化日志事件。与 stderr 的区别：log 事件是 Worker 主动发出的结构化信息，stderr 是任意调试输出。

```python
class LogEvent(WorkerEvent):
    type:    Literal["log"] = "log"
    level:   Literal["debug", "info", "warning", "error"]
    message: str
```

```json
{"type":"log","task_id":"01JWF9TASK00000000000001","timestamp":"2026-05-03T10:00:05Z","seq":2,"level":"info","message":"loaded whisper large-v3 model"}
```

---

### 4.4 artifact

产物就绪通知。在 Worker 将文件从 `.part` rename 为最终文件后发送。

```python
class ArtifactEvent(WorkerEvent):
    type:           Literal["artifact"] = "artifact"
    artifact_id:    str                  # ULID，Worker 生成
    artifact_type:  str                  # "subtitle" | "video" | "audio" | "image_seq" | "metadata" | "cache"
    path:           str                  # 最终文件路径（相对于 work_dir）
    hash:           str | None = None    # SHA-256 hex digest
    size_bytes:     int | None = None    # 文件大小
    metadata:       dict = {}            # 附加信息
```

```json
{"type":"artifact","task_id":"01JWF9TASK00000000000001","timestamp":"2026-05-03T10:01:30Z","seq":18,"artifact_id":"01JWF9ART000000000000001","artifact_type":"subtitle","path":"01JWF9TASK00000000000001/raw_asr.srt","hash":"a1b2c3d4...","size_bytes":15234,"metadata":{"format":"srt","segments":142,"language":"ja"}}
```

### metadata 建议字段

| artifact_type | 建议 metadata 字段 |
|---|---|
| `subtitle` | `format`, `segments`, `language` |
| `video` | `format`, `duration_sec`, `resolution`, `codec`, `fps` |
| `audio` | `format`, `duration_sec`, `sample_rate`, `channels` |
| `image_seq` | `format`, `frame_count`, `resolution` |
| `metadata` | 自由格式 |

---

### 4.5 completed

任务完成。**必须是 Worker 发出的最后一个正常事件**。

```python
class ArtifactRef(BaseModel):
    artifact_id:   str
    artifact_type: str
    path:          str

class CompletedEvent(WorkerEvent):
    type:              Literal["completed"] = "completed"
    artifacts:         list[ArtifactRef]      # 最终产物列表
    duration_seconds:  float                  # 总执行时长
```

```json
{"type":"completed","task_id":"01JWF9TASK00000000000001","timestamp":"2026-05-03T10:02:00Z","seq":20,"artifacts":[{"artifact_id":"01JWF9ART000000000000001","artifact_type":"subtitle","path":"01JWF9TASK00000000000001/raw_asr.srt"}],"duration_seconds":119.0}
```

---

### 4.6 failed

任务失败。

```python
class FailedEvent(WorkerEvent):
    type:               Literal["failed"] = "failed"
    error_code:         str                   # 见 §8 错误码枚举
    message:            str                   # 人类可读错误描述
    recoverable:        bool                  # 是否建议重试
    partial_artifacts:  list[ArtifactRef] = [] # 失败前已产出的可用产物
```

```json
{"type":"failed","task_id":"01JWF9TASK00000000000001","timestamp":"2026-05-03T10:01:45Z","seq":15,"error_code":"OOM","message":"GPU memory exhausted during inference, peak usage 11.2GB on 8GB device","recoverable":true,"partial_artifacts":[]}
```

---

### 4.7 heartbeat

心跳事件。长时间无 progress 更新时（如模型加载阶段），Worker 应定期发送心跳证明进程存活。

```python
class HeartbeatEvent(WorkerEvent):
    type:            Literal["heartbeat"] = "heartbeat"
    uptime_seconds:  float              # Worker 启动以来的秒数
    memory_mb:       float              # 当前进程内存占用
    gpu_memory_mb:   float | None = None  # 当前 GPU 内存占用
```

```json
{"type":"heartbeat","task_id":"01JWF9TASK00000000000001","timestamp":"2026-05-03T10:00:35Z","seq":3,"uptime_seconds":34.0,"memory_mb":2048.5,"gpu_memory_mb":4096.0}
```

## 5. Artifact 交接协议

### 5.1 写入规则

1. Worker 将产物写入 `{work_dir}/{task_id}/{filename}.part`。
2. 写入完成后，计算 SHA-256 hash。
3. 原子 rename：`{filename}.part` → `{filename}`。
4. 发送 `artifact` 事件。

如果任务语义是导出到用户目录，Worker 仍只生成 staged artifact。Scheduler 验证 artifact 后，再由 ArtifactFinalizer 复制或移动到用户确认的输出目录，并避免静默覆盖已有文件。

### 5.2 Scheduler 验证

1. 收到 `artifact` 事件后，检查文件存在性。
2. 如果事件中提供了 hash，验证文件 hash 匹配。
3. 验证通过后将 artifact 记录写入数据库。
4. 如果验证失败，记录 warning 并标记 artifact 为 `suspect`。

### 5.3 隔离约束

- Worker 只能写入自己的 `{work_dir}/{task_id}/` 目录。
- Worker 不得覆盖非自己 task_id 目录的文件。
- Worker 不得删除非自己创建的文件。
- 违反隔离约束的行为应被 Scheduler 检测并记录 warning。

### 5.4 缓存产物

当 Scheduler 判定某 Task 命中缓存时：

1. 不启动 Worker 进程。
2. 直接将缓存中的 artifact 链接到当前 Task。
3. 设置 Task 状态 → `completed`（标记来源为 cache hit）。

## 6. 超时与心跳

### 6.1 心跳要求

- Worker 应至少每 **30 秒**发送一次 `heartbeat` 或 `progress` 事件。
- 进入长阻塞阶段（模型加载、大文件解码）前，Worker 应主动发一次 heartbeat。

### 6.2 超时判定

- Scheduler 默认 `heartbeat_timeout = 120` 秒。
- 超过 120 秒未收到任何事件 → Scheduler 判定 Worker 卡死。
- 超时处理：
  1. 发送 SIGTERM（Windows 上为 subprocess.terminate()）。
  2. 等待 15 秒。
  3. 如果进程仍存活，发送 SIGKILL（Windows 上为 subprocess.kill()）。
  4. 设置 Task 状态 → `failed`，error_code = `TIMEOUT`。

### 6.3 可配置超时

不同 node_type 可在 NodeRegistryEntry 中声明建议 heartbeat_timeout：

```python
class WorkerConfig(BaseModel):
    heartbeat_timeout_sec: int = 120
    startup_timeout_sec:   int = 60    # started 事件的最大等待时间
    cancel_grace_sec:      int = 10    # 收到 cancel 后的最大退出时间
```

## 7. 取消协议

### 7.1 正常取消

1. 用户在 GUI 点击取消，或 Scheduler 决定取消（如上游失败 + stop 策略）。
2. Scheduler 向 Worker stdin 写入：
   ```json
   {"type":"cancel"}
   ```
3. Worker 收到后：
   - 停止当前处理。
   - 清理临时文件（删除 `.part` 文件）。
   - 发送 `failed` 事件，error_code = `CANCELLED`。
   - 正常退出（exit code 0）。
4. Worker 应在 `cancel_grace_sec`（默认 10 秒）内退出。
5. 超时未退出则 Scheduler 强杀进程。

Scheduler 收到 `failed` 且 `error_code == CANCELLED` 时，必须将任务状态归一化为 `cancelled`，并将 Plan/Job 取消逻辑按 EXECUTION_PLAN_SPEC §12 处理。这类事件不进入普通失败重试路径。

### 7.2 取消时的 partial artifacts

- 如果取消前已有完整产物，Worker 应在 failed 事件的 `partial_artifacts` 中列出。
- Scheduler 根据 partial_artifacts 决定哪些产物可保留。

## 8. 错误码枚举

```python
class ErrorCode(str, Enum):
    OOM            = "OOM"             # GPU 或系统内存不足
    MODEL_MISSING  = "MODEL_MISSING"   # 模型文件不存在或无法加载
    INPUT_CORRUPT  = "INPUT_CORRUPT"   # 输入文件损坏或格式不支持
    INPUT_MISSING  = "INPUT_MISSING"   # 输入 artifact 文件不存在
    TIMEOUT        = "TIMEOUT"         # 执行超时（由 Scheduler 设定）
    RUNTIME_MISSING = "RUNTIME_MISSING" # RuntimeManager 未解析出所需组件、模型或 backend
    INTERNAL       = "INTERNAL"        # Worker 内部错误
    INTERRUPTED    = "INTERRUPTED"     # App 崩溃、Worker 进程丢失或系统重启导致任务中断
    CANCELLED      = "CANCELLED"       # 用户或 Scheduler 取消
    DEPENDENCY     = "DEPENDENCY"      # 外部依赖不可用（FFmpeg 未安装等）
    PERMISSION     = "PERMISSION"      # 文件权限不足
    DISK_FULL      = "DISK_FULL"       # 磁盘空间不足
```

### 建议 Recovery Action

| 错误码 | recoverable | 建议动作 |
|---|---|---|
| `OOM` | true | 降低 batch size / 切换到更小模型 / 分配到更大显存设备 |
| `MODEL_MISSING` | false | 提示用户下载模型 |
| `INPUT_CORRUPT` | false | 检查输入文件完整性 |
| `INPUT_MISSING` | false | 重新运行上游 Task |
| `TIMEOUT` | true | 增加超时时间 / 检查任务规模 |
| `RUNTIME_MISSING` | false | 打开 Runtime 面板安装、修复或切换 backend |
| `INTERNAL` | true | 重试；多次失败后报告 bug |
| `INTERRUPTED` | true | 启动恢复流程，检查 partial artifacts 后决定重试或恢复 |
| `CANCELLED` | false | 用户主动取消，不需恢复 |
| `DEPENDENCY` | false | 安装缺失依赖 |
| `PERMISSION` | false | 检查文件/目录权限 |
| `DISK_FULL` | false | 清理磁盘空间 |

## 9. Worker Adapter 约定

### 9.1 Adapter 职责

每种 node_type 对应一个 Worker Adapter，负责：

1. 接收 ExecutionTask.params。
2. 验证参数合法性。
3. 将参数和 `runtime_binding` 转换为具体的外部工具命令或 API 调用。
4. 执行任务并发送事件流。
5. 管理临时文件和最终产物。

### 9.2 Adapter 接口

```python
class WorkerAdapter(ABC):
    @abstractmethod
    def validate(self, task: ExecutionTask) -> list[str]:
        """验证参数。返回错误列表，空列表表示通过。"""

    @abstractmethod
    def run(self, task: ExecutionTask, emitter: EventEmitter) -> None:
        """执行任务。通过 emitter 发送事件。异常会被 runner 捕获并转为 failed 事件。"""
```

### 9.3 安全约束

- Adapter **必须**通过 typed command builder 调用外部工具（如 FFmpegCommand builder）。
- **禁止**拼接裸 shell 命令字符串。
- **禁止**使用 `shell=True` 调用 subprocess。
- **禁止**将用户参数直接拼入命令行（防止命令注入）。
- Adapter 不应访问 Atelier 数据库。
- Adapter 不应从全局 `PATH`、开发机固定路径或用户随手配置的路径寻找外部工具；外部工具路径必须来自 `runtime_binding.component_paths`。
- Adapter 不应直接修改 RuntimeManifest、下载模型或安装 backend；这些动作属于 RuntimeManager。

### 9.4 首版计划 Adapter

| node_type | Adapter | 外部工具 |
|---|---|---|
| `input.video` | InputVideoAdapter | FFprobe |
| `asr.whisper` | WhisperAdapter | faster-whisper / whisper.cpp |
| `translate.llm` | LLMTranslateAdapter | LLM API（本地或远程） |
| `subtitle.review` | SubtitleReviewAdapter | LLM API |
| `enhance.realesrgan` | RealESRGANAdapter | realesrgan-ncnn-vulkan |
| `enhance.rife` | RIFEAdapter | rife-ncnn-vulkan |
| `audio.enhance` | AudioEnhanceAdapter | 待定 |
| `compose.mux_subtitle` | MuxSubtitleAdapter | FFmpeg |
| `compose.burn_subtitle` | BurnSubtitleAdapter | FFmpeg |
| `compose.mux_audio` | MuxAudioAdapter | FFmpeg |
| `output.export` | ExportAdapter | FFmpeg |

表中的外部工具名是逻辑组件名。真实可执行文件、动态库、模型目录和环境变量由 RuntimeManager 管理并通过 `runtime_binding` 传入 Worker。

## 10. 完整生命周期示例

以 `asr.whisper` 任务为例，Worker stdout 的完整 JSON Lines 输出：

```jsonl
{"type":"started","task_id":"01JWF9TASK00000000000001","timestamp":"2026-05-03T10:00:01Z","seq":0,"worker_pid":12345,"worker_version":"1.0.0","node_type":"asr.whisper"}
{"type":"log","task_id":"01JWF9TASK00000000000001","timestamp":"2026-05-03T10:00:02Z","seq":1,"level":"info","message":"loading whisper large-v3 model"}
{"type":"heartbeat","task_id":"01JWF9TASK00000000000001","timestamp":"2026-05-03T10:00:32Z","seq":2,"uptime_seconds":31.0,"memory_mb":1024.0,"gpu_memory_mb":3800.0}
{"type":"log","task_id":"01JWF9TASK00000000000001","timestamp":"2026-05-03T10:00:45Z","seq":3,"level":"info","message":"model loaded, starting transcription"}
{"type":"progress","task_id":"01JWF9TASK00000000000001","timestamp":"2026-05-03T10:00:50Z","seq":4,"current":100,"total":1000,"unit":"segments","percent":10.0,"stage":"transcription","eta_seconds":90.0}
{"type":"progress","task_id":"01JWF9TASK00000000000001","timestamp":"2026-05-03T10:01:00Z","seq":5,"current":250,"total":1000,"unit":"segments","percent":25.0,"stage":"transcription","eta_seconds":67.5}
{"type":"progress","task_id":"01JWF9TASK00000000000001","timestamp":"2026-05-03T10:01:10Z","seq":6,"current":500,"total":1000,"unit":"segments","percent":50.0,"stage":"transcription","eta_seconds":45.0}
{"type":"progress","task_id":"01JWF9TASK00000000000001","timestamp":"2026-05-03T10:01:20Z","seq":7,"current":750,"total":1000,"unit":"segments","percent":75.0,"stage":"transcription","eta_seconds":22.5}
{"type":"progress","task_id":"01JWF9TASK00000000000001","timestamp":"2026-05-03T10:01:30Z","seq":8,"current":1000,"total":1000,"unit":"segments","percent":100.0,"stage":"transcription","eta_seconds":0}
{"type":"log","task_id":"01JWF9TASK00000000000001","timestamp":"2026-05-03T10:01:31Z","seq":9,"level":"info","message":"transcription complete, writing SRT"}
{"type":"artifact","task_id":"01JWF9TASK00000000000001","timestamp":"2026-05-03T10:01:32Z","seq":10,"artifact_id":"01JWF9ART000000000000001","artifact_type":"subtitle","path":"01JWF9TASK00000000000001/raw_asr.srt","hash":"a1b2c3d4e5f6...","size_bytes":15234,"metadata":{"format":"srt","segments":142,"language":"ja"}}
{"type":"completed","task_id":"01JWF9TASK00000000000001","timestamp":"2026-05-03T10:01:33Z","seq":11,"artifacts":[{"artifact_id":"01JWF9ART000000000000001","artifact_type":"subtitle","path":"01JWF9TASK00000000000001/raw_asr.srt"}],"duration_seconds":92.0}
```

## 11. 与其他文档的关系

```text
WORKFLOW_NODE_SPEC
  → (本文档) WORKER_PROTOCOL：
      node_type 决定使用哪个 adapter。
      NodeParam / param_values 最终成为 ExecutionTask.params 传给 Worker。

EXECUTION_PLAN_SPEC
  → (本文档) WORKER_PROTOCOL：
      ExecutionTask 序列化为 task.json 是 Worker 的输入。
      TaskStatus 状态机由 Worker 事件驱动更新。
      ResourceBinding 决定 Worker 运行在哪个设备上。

WORKER_PROTOCOL (本文档)
  → DATABASE_SCHEMA：
      task_events 表追加存储所有 WorkerEvent。
      artifacts 表存储 artifact 记录。
      stderr 日志存储到文件系统（不入数据库）。
```
