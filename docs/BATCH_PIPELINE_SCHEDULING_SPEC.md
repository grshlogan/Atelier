# Atelier Batch Pipeline Scheduling Spec

> 状态：规划中，尚未实现。本文档定义 Atelier 在批量视频进入同一 workflow 时，如何把每个视频展开为 task DAG，并通过有界流水线、backpressure、跨视频调度和可解释 waiting reason，让快阶段不空转、慢阶段不爆仓、硬件不被单个视频阻塞。

## 1. 目标

Atelier 的批量执行不应以“单个视频完整跑完”为调度单位，而应以 `ExecutionTask` 为调度单位。

核心目标：

```text
同一视频内部严格遵守 artifact dependency
跨视频任务可以流水线并行
快阶段可以提前生产，但受慢阶段 backlog 限制
慢阶段形成可观察瓶颈
Scheduler 解释每个 task 为什么运行或等待
Queue / Hardware Scheduling Page 展示可理解状态
```

非目标：

```text
不引入 Kubernetes / Slurm / Celery / Temporal
不实现分布式调度
不让 GUI 直接启动 Worker
不让插件或 Worker 直接管理 resource_locks
不在首版做全自动最优调度器
```

## 2. 参考资料与取舍

### Kubernetes Scheduler / Job Controller

可借鉴：

- Scheduler 负责把未绑定资源的工作单元放到合适节点上。
- Controller 不直接执行任务，而是持续让当前状态接近期望状态。
- Job 是一次性运行到完成的任务单元，可与 backoff、失败策略、清理策略结合。

Atelier 的取舍：

- 不引入 Kubernetes。
- 借鉴“desired state -> scheduler/controller reconcile”的思想。
- `Scheduler` 是本地 Job controller，SQLite 是状态事实源，Worker 是一次性执行进程。

### Slurm GRES / GPU Scheduling

可借鉴：

- GPU 是可声明、可分配、可跟踪的 generic resource。
- 分配后通过环境和资源约束让任务只能看到被分配的设备。
- GPU memory/utilization 可作为 accounting / diagnosis 数据。

Atelier 的取舍：

- 不实现 HPC 队列。
- 借鉴 GRES 的“资源请求 -> 调度绑定 -> 使用隔离 -> 资源释放”。
- 单机首版由 `ResourceBinding` / `resource_locks` 表达 GPU/CPU/API/Disk slots。

### Celery Rate Limit / Queue Discipline

可借鉴：

- 对某类任务设置启动频率限制。
- API 型任务可通过 queue / rate limit 控制并发和节奏。

Atelier 的取舍：

- 不引入 Celery。
- 借鉴“stage-level concurrency / rate limit”。
- 远程翻译、远程 LLM、下载类任务必须有 provider / stage concurrency limit。

### Temporal Heartbeat / Timeout

可借鉴：

- 长任务通过 heartbeat 表达存活。
- timeout / retry policy 是 activity 级别事实，而不是 UI 猜测。

Atelier 的取舍：

- 仍使用本地 Worker JSON Lines 协议。
- `heartbeat`、`progress`、`TIMEOUT`、`CANCELLED` 已属于 Worker/Scheduler 协议，不由 Batch Scheduler 重新发明。

## 3. 术语

| 术语 | 含义 |
|---|---|
| Batch | 一组一起提交的媒体项，例如 12 个视频 |
| Media Item | 单个视频 / 音频 / 字幕输入项 |
| Per-media DAG | 单个视频展开后的任务依赖图 |
| Cross-media Pipeline | 多个视频的同类 stage 形成共享流水线 |
| Stage | 逻辑阶段，如 ASR、Translate、Enhance、Mux |
| Backlog | 某 stage 中等待运行或正在运行的任务数量 |
| Backpressure | 下游慢阶段积压后，对上游快阶段施加暂停或降速 |
| Finish Priority | 对接近完成的视频的尾部任务提高优先级 |
| Waiting Reason | task 未运行的明确原因 |

## 4. 内置卡片范围

本文只覆盖当前内置卡片，不覆盖未来第三方插件。

首版内置流程卡片：

```text
Video Input
Audio Input
Subtitle Input
Metadata Probe
Audio Extract
Audio Enhance
ASR Subtitle
OCR Recognition
Subtitle Normalize
Translate Agent
Subtitle Review
Video Enhance
Frame Interpolation
Soft Subtitle Mux
Burn Subtitle
Output Export
```

推荐 node_type 命名可为：

```text
input.video
input.audio
input.subtitle
metadata.probe
media.audio_extract
audio.enhance
asr.whisper
ocr.recognition
subtitle.normalize
translate.llm
subtitle.review
enhance.realesrgan
enhance.rife
compose.mux_subtitle
compose.burn_subtitle
compose.mux_audio
output.export
```

如现有文档中 node_type 命名未完全一致，以 `NodeRegistryEntry` 为最终事实源；本文只规定调度语义。

## 5. 批量 DAG 展开模型

### 5.1 单个视频 DAG

```text
Video Input
  -> Metadata Probe
  -> Audio Extract
      -> Audio Enhance
      -> ASR Subtitle
          -> Subtitle Normalize
          -> Translate Agent
          -> Subtitle Review
  -> Video Enhance
      -> Frame Interpolation

Subtitle Review + Frame Interpolation + Audio Enhance
  -> Soft Subtitle Mux
  -> Burn Subtitle
  -> Output Export
```

说明：

- `Soft Subtitle Mux` 依赖本视频的翻译/审校字幕和可用视频 artifact。
- `Burn Subtitle` 依赖本视频的字幕和视频支路。
- `Output Export` 依赖本视频的 mux / burn 结果。
- 不同视频之间默认无 artifact dependency。

### 5.2 批量展开

批量提交后：

```text
BatchJob
  -> MediaItem[V01]
      -> Task[V01.input.video]
      -> Task[V01.metadata.probe]
      -> ...
  -> MediaItem[V02]
      -> Task[V02.input.video]
      -> Task[V02.metadata.probe]
      -> ...
```

Scheduler 看到的是一个由多个 per-media DAG 组成的大 DAG：

```text
global runnable set = all tasks whose depends_on_tasks are completed/skipped-compatible
```

规则：

- 同一视频内部按依赖执行。
- 跨视频同类 task 可并行或排队。
- 调度单位是 `ExecutionTask`，不是整条视频。

## 6. 调度原则

### R-01：以 `ExecutionTask` 为最小调度单位

禁止：

```text
Video_01 全流程完成后才允许 Video_02 进入 ASR
```

允许：

```text
Video_01 Translate 正在慢速运行时，Video_02 / Video_03 可以继续 ASR
```

### R-02：同一视频内部必须等待自身依赖

例如：

```text
V01 Soft Subtitle Mux
  必须等待 V01 Subtitle Review 完成
  必须等待 V01 Frame Interpolation 或 Video Enhance 分支完成
```

但这不影响：

```text
V02 ASR
V03 Audio Extract
V04 Translate
```

### R-03：快阶段可以提前生产，但受 backpressure 控制

ASR 快、Translate 慢时：

```text
V01 ASR -> V01.srt -> Translate backlog
V02 ASR -> V02.srt -> Translate backlog
V03 ASR -> V03.srt -> Translate backlog
```

当 `translate_backlog >= max_translate_backlog` 时，暂停新的 ASR 或 Subtitle Normalize。

### R-04：慢阶段是瓶颈事实，不是错误

Translate、Review、Video Enhance、Frame Interpolation 可能长期成为瓶颈。Scheduler 应记录瓶颈原因，而不是把所有等待显示为普通 queued。

### R-05：接近完成的视频获得 finish priority

如果某视频只剩 Mux / Export，且资源成本低，应优先完成它，避免队列里大量“99% 视频”长期悬挂。

### R-06：硬件资源绑定仍由 Scheduler 唯一决定

GUI / preset 只表达：

```text
preferred device
stage concurrency
backlog limit
fallback preference
```

最终仍必须写成合法的 `ResourceBinding` / `RuntimeBinding`。

### R-07：API / LLM provider 必须有并发和速率限制

远程 API 翻译不受 GPU 限制，但受：

```text
provider concurrency
rate limit
token budget
cost policy
network availability
credential availability
```

### R-08：GPU-heavy task 默认倾向 exclusive

首版建议：

```text
enhance.realesrgan -> exclusive GPU by default
enhance.rife -> exclusive GPU by default
local translate.llm -> exclusive or high-reserve GPU by default
asr.whisper -> shared if small model, exclusive if large model
```

### R-09：waiting reason 必须可解释

每个未运行 task 至少有一个标准 waiting reason。

## 7. StageBacklog 模型

```python
class StageKey(str, Enum):
    INPUT_PROBE = "input_probe"
    AUDIO_EXTRACT = "audio_extract"
    AUDIO_ENHANCE = "audio_enhance"
    ASR = "asr"
    OCR = "ocr"
    SUBTITLE_NORMALIZE = "subtitle_normalize"
    TRANSLATE = "translate"
    SUBTITLE_REVIEW = "subtitle_review"
    VIDEO_ENHANCE = "video_enhance"
    FRAME_INTERPOLATION = "frame_interpolation"
    SOFT_MUX = "soft_mux"
    BURN_SUBTITLE = "burn_subtitle"
    EXPORT = "export"

class StageBacklog(BaseModel):
    stage: StageKey
    runnable_count: int = 0
    queued_count: int = 0
    running_count: int = 0
    blocked_count: int = 0
    paused_count: int = 0
    backlog_limit: int | None = None
    bottleneck_score: float = 0.0
```

`bottleneck_score` 首版可简单计算：

```text
bottleneck_score =
  queued_count * 1.0
  + running_count * avg_remaining_minutes
  + blocked_downstream_count * 0.5
```

不要在首版追求精确数学模型；先让 UI 能解释“明显瓶颈”。

## 8. BackpressurePolicy

```python
class BackpressurePolicy(BaseModel):
    max_ocr_backlog: int = 6
    max_translate_backlog: int = 8
    max_review_backlog: int = 6
    max_video_enhance_backlog: int = 4
    max_frame_interpolation_backlog: int = 4
    max_asr_ahead: int = 6
    max_pending_intermediate_bytes: int | None = None
    pause_fast_upstream_when_bottleneck_full: bool = True
    allow_probe_ahead: bool = True
    allow_audio_extract_ahead: bool = True
```

规则：

- `max_asr_ahead` 表示 ASR 可以比 Translate 完成进度提前多少个媒体项。
- `max_ocr_backlog` 限制 OCR 抽帧/识别支路积压，避免视觉文字识别把磁盘、CPU/GPU 或中间帧缓存压爆。
- `max_pending_intermediate_bytes` 用于防止大量中间视频帧、临时音频、字幕堆满磁盘。
- `pause_fast_upstream_when_bottleneck_full=True` 时，ASR / OCR / Normalize 可能被置为 `paused_by_backpressure`。

## 9. ConcurrencyPolicy

```python
class ConcurrencyPolicy(BaseModel):
    max_cpu_tasks: int = 4
    max_disk_heavy_tasks: int = 2
    max_gpu_tasks_per_device: int = 1
    max_shared_gpu_tasks_per_device: int = 2
    max_remote_translate_tasks: int = 2
    max_local_llm_tasks: int = 1
    max_mux_tasks: int = 2
    max_export_tasks: int = 1
```

说明：

- CPU task 不等于无限并发，FFmpeg / disk IO 过多会拖慢系统。
- API task 不占 GPU，但必须受 provider / credential / cost 策略控制。
- `max_export_tasks` 默认较低，避免大量最终写盘导致 UI 卡顿或磁盘拥塞。

## 10. WaitingReason

```python
class WaitingReasonCode(str, Enum):
    WAITING_DEPENDENCY = "waiting_dependency"
    WAITING_HARDWARE = "waiting_hardware"
    WAITING_RUNTIME = "waiting_runtime"
    WAITING_API_SLOT = "waiting_api_slot"
    PAUSED_BY_BACKPRESSURE = "paused_by_backpressure"
    WAITING_DISK_BANDWIDTH = "waiting_disk_bandwidth"
    BLOCKED_BY_FAILED_UPSTREAM = "blocked_by_failed_upstream"
    WAITING_USER_CONFIRMATION = "waiting_user_confirmation"
    WAITING_CREDENTIAL = "waiting_credential"
    WAITING_CACHE_VALIDATION = "waiting_cache_validation"
    WAITING_RETRY_POLICY = "waiting_retry_policy"
```

UI 展示示例：

| Task | State | Reason |
|---|---|---|
| `V03.translate.llm` | queued | API concurrency full |
| `V04.asr.whisper` | paused | translate backlog 8/8 |
| `V02.enhance.rife` | waiting | depends on Video Enhance |
| `V01.compose.mux_subtitle` | blocked | waiting for Subtitle Review |
| `V05.output.export` | blocked | waiting for Soft Subtitle Mux |

## 11. SchedulingDecision

每次调度循环应可选择性记录决策摘要，供 Debug / Scheduling Page 使用。

```python
class SchedulingDecision(BaseModel):
    decision_id: str
    task_id: str
    media_id: str
    stage: StageKey
    decision: Literal["run", "queue", "pause", "block", "skip"]
    reason_code: WaitingReasonCode | None = None
    resource_binding: ResourceBinding | None = None
    runtime_binding_id: str | None = None
    policy_snapshot_id: str
    created_at: str
    human_reason: str
```

首版可以不建新表，先通过 repository 查询实时状态生成 `SchedulingDecisionView`；行为稳定后再考虑持久化。

## 12. 调度循环建议

```text
Scheduler tick
  -> load pending / queued / retry_pending tasks
  -> mark dependency-ready tasks as candidate
  -> resolve runtime availability
  -> capture hardware snapshot
  -> compute stage backlog
  -> apply backpressure
  -> apply concurrency limits
  -> score candidates
  -> bind resources
  -> write resource_locks
  -> dispatch selected tasks
  -> expose decisions to Queue / Hardware Scheduling Page
```

候选评分建议：

```text
score =
  user_priority
  + finish_priority
  + bottleneck_priority
  + fairness_bonus
  - resource_cost_penalty
  - backlog_pressure_penalty
```

首版不用暴露复杂公式，可实现为清晰的排序规则：

1. 可让某个视频完成的 Mux / Export。
2. 瓶颈阶段中可运行的 task。
3. GPU-heavy task，如果设备空闲且不会造成 OOM 风险。
4. 快速前置 task，但受 backpressure 限制。
5. FIFO。

## 13. 示例：ASR 快、Translate 慢

场景：

```text
ASR: 1 min / video
Translate: 8 min / video
Review: 3 min / video
Mux: 1 min / video
Batch: 10 videos
max_translate_backlog = 6
```

调度行为：

```text
T+00 V01 ASR starts
T+01 V01 Translate starts; V02 ASR starts
T+02 V02 Translate queued; V03 ASR starts
T+03 V03 Translate queued; V04 ASR starts
...
当 Translate backlog = 6:
  新 ASR 暂停
  Queue shows: paused_by_backpressure
  Hardware page shows: Bottleneck = Translate Agent
Translate 完成一个:
  backlog 降低
  允许补充一个新的 ASR
```

封装行为：

```text
V01 Mux waits for:
  V01 Subtitle Review completed
  V01 video branch completed
V01 不等待 V02/V03 的翻译
V02/V03 不等待 V01 完整导出后才进入 ASR
```

## 14. OOM / TIMEOUT / CANCELLED 交互

### OOM

```text
Worker reports OOM
  -> task failed(OOM)
  -> release resource lock
  -> reduce same-condition retry score
  -> suggest lower batch/tile/smaller model/switch device
  -> do not silently retry same GPU with same params
```

### TIMEOUT

```text
heartbeat timeout
  -> terminate/kill
  -> task failed(TIMEOUT)
  -> release lock
  -> optionally retry with larger timeout if policy allows
```

### CANCELLED

```text
cancel selected media item:
  -> cancel runnable/running tasks for that media item
  -> preserve completed artifacts
  -> mark downstream as cancelled unless policy says export_partial
```

## 15. 与 Queue Monitor 的关系

Queue Monitor 显示用户级状态：

```text
V01 68% Translate Agent ETA 03:12
V02 Queued Video Enhance
```

Hardware Scheduling Page 显示调度解释：

```text
V04 ASR paused because translate backlog 8/8
V02 RIFE waiting because enhance.realesrgan not completed
GPU 1 idle because no compatible runtime available
```

## 16. 首版实现建议

### Phase A：只实现 per-media DAG 展开

- 每个 input media 展开为同一套内置 task DAG。
- 写入 `task_dependencies`。
- 不做复杂优化。

### Phase B：实现 StageBacklog 和 WaitingReason

- 从 SQLite / repository 生成 stage backlog。
- 为 pending / queued / blocked task 生成 waiting reason。
- Queue Monitor 可先显示 reason。

### Phase C：实现基础 Backpressure

- 只对 Translate / Review 加 backlog limit。
- ASR / Normalize 在 backlog 满时暂停。
- 不改真实 worker，先只改变 claim candidate。

### Phase D：实现 finish priority

- Mux / Export 在依赖满足时获得较高优先级。
- 防止大量视频都卡在最后一步。

### Phase E：接入 Hardware Scheduling Page

- 提供 `SchedulingPageSnapshot`。
- Page 只读展示，不直接运行任务。

## 17. 与其他文档的关系

```text
WORKFLOW_NODE_SPEC
  -> 定义内置卡片、端口、参数、runtime requirements

EXECUTION_PLAN_SPEC
  -> 定义 task、depends_on_tasks、phase、lane、状态机

HARDWARE_SCHEDULING_SPEC
  -> 定义硬件检测、ResourceRequest、ResourceBinding、resource_locks

WORKER_PROTOCOL
  -> 提供 progress / heartbeat / completed / failed 事件

HARDWARE_SCHEDULING_PAGE_SPEC
  -> 展示本文的 backlog、waiting reason、hardware lanes

SCHEDULING_PRESETS_SPEC
  -> 把本文策略包装成用户可选择的 preset
```

## 18. Blockers

- 内置 node_type / Builtin Card Catalog 尚未最终冻结。
- 真实 adapter 尚未实现。
- 资源估算仍会粗糙；首版必须保守。
- 远程 API provider 的 rate limit / credential 状态需要后续单独接入。

## 19. 参考资料

- Kubernetes Scheduler: https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/
- Kubernetes Jobs: https://kubernetes.io/docs/concepts/workloads/controllers/job/
- Kubernetes Controllers: https://kubernetes.io/docs/concepts/architecture/controller/
- Slurm GRES Scheduling: https://slurm.schedmd.com/gres.html
- Celery Task Rate Limit: https://docs.celeryq.dev/en/stable/userguide/tasks.html
- Temporal Activity Heartbeats: https://docs.temporal.io/
