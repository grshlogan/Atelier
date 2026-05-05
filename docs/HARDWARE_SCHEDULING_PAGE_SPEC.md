# Atelier Hardware Scheduling Page Spec

> 状态：规划中，尚未实现。本文档定义 Hardware Scheduling 复页的定位、信息架构、视图等级、面板布局、交互规则和数据来源。该复页是 `WorkflowGraph -> ExecutionPlan -> Scheduler -> Worker` 的可解释视图，不是普通硬件监控面板，也不是 workflow 编辑器。

## 1. 目标

Hardware Scheduling Page 需要回答四个问题：

```text
当前哪些任务在跑？
为什么这些任务在跑？
哪些任务在等？
它们为什么在等？
```

核心目标：

```text
解释 Scheduler 决策
呈现内置卡片流程与硬件映射
显示瓶颈、backlog、waiting reason
支持入门预设与专业自定义
保留 Debug 视图但不让 GUI 绕过 Scheduler
```

非目标：

```text
不替代 Workflow Canvas
不直接启动 FFmpeg / 模型 / Worker
不让用户手写 ResourceBinding / RuntimeBinding
不成为通用系统监控器
不在首版实现完整性能分析器
```

## 2. 参考资料与取舍

### Qt QMainWindow / QDockWidget

可借鉴：

- `QMainWindow` 支持 central widget、toolbar、status bar 和 dock widgets。
- `QDockWidget` 可停靠、浮动、关闭、重新布局。
- `QMainWindow.saveState()` / `restoreState()` 可保存 dock 布局。

Atelier 的取舍：

- Hardware Scheduling Page 是 central view / workflow 子页面。
- Inspector / Queue / Logs / Hardware detail 可以作为 dock panels。
- 页面布局可保存，但调度事实不存放在 widget 内部。

### 专业创作软件 Workspace

可借鉴：

- 工作区可按 Workflow / Execution / Review / Runtime / Debug 切换。
- 普通用户看简洁摘要，专业用户展开详细资源图。

Atelier 的取舍：

- 默认不暴露所有内部字段。
- 通过 Simple / Standard / Professional / Debug 分级展示复杂度。

### Scheduler / GRES / Resource View

可借鉴：

- 调度页面不仅展示利用率，还要展示资源被谁占用、谁在等待、为什么等待。
- GPU / API / Disk / CPU 可以被视为不同 lane。

Atelier 的取舍：

- 单机本地调度，使用 SQLite / Scheduler snapshot。
- 不实现 HPC cluster UI，但借鉴“资源 lane + allocation + waiting reason”。

## 3. 页面定位

```text
Hardware Scheduling Page
  = ExecutionPlan 的硬件执行视图
  = Queue Monitor 的专业版
  = Scheduler 决策的可解释界面
```

区别：

| 页面 | 关注点 |
|---|---|
| Workflow Canvas | 用户设计流程，卡片和连线 |
| Execution Canvas | 任务阶段、lane、执行蓝图 |
| Queue Monitor | 批量任务状态和进度 |
| Hardware Resources Panel | 当前硬件利用率 |
| Hardware Scheduling Page | task 为什么跑 / 等，如何映射到硬件和瓶颈 |

## 4. 页面总布局

推荐 1600 × 1000 概念布局：

```text
Top Bar:             x=0    y=0    w=1600 h=68
Left Sidebar:        x=0    y=68   w=210  h=932
Page Header:         x=210  y=68   w=1390 h=100
Workflow Overview:   x=210  y=168  w=1390 h=170
Stage Backlog:       x=210  y=350  w=235  h=360
Hardware Lanes:      x=455  y=350  w=820  h=360
Inspector:           x=1285 y=350  w=315  h=360
Waiting Table:       x=210  y=720  w=1390 h=260
```

说明：

- 这些坐标用于设计稿，不是硬编码 geometry。
- 产品实现应走 `QMainWindow + dockable panels + layout persistence`。
- 页面必须能降级为窄屏/低分辨率布局：Stage Backlog 可折叠，Inspector 可停靠/浮动。

## 5. 顶部 Header

内容：

```text
Title: Hardware Scheduling
Subtitle: ExecutionPlan-derived resource view for the active workflow
KPI chips:
  Batch 12
  Running 4
  Queued 18
  Blocked 31
  Bottleneck: Translate Agent

Controls:
  Scheduling Preset: Auto Balanced
  View Mode: Simple / Standard / Professional / Debug
```

KPI 定义：

| Chip | 来源 |
|---|---|
| Batch | 当前 batch media count |
| Running | running task count |
| Queued | queued / runnable but not running |
| Blocked | blocked by dependency/failure/runtime/hardware |
| Bottleneck | StageBacklog / SchedulingSnapshot 计算结果 |

## 6. Built-in Workflow Cards 概览

页面顶部必须展示当前内置卡片流程，作用是让用户知道调度视图来自哪条 workflow。

显示卡片：

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
Mux Audio
Output Export
```

推荐布局：

```text
Video Input -> Metadata Probe
              ├-> Audio Extract -> Audio Enhance -> ASR Subtitle -> Subtitle Normalize -> Translate Agent -> Subtitle Review
              ├-> OCR Recognition ------------------------------^
              └-> Video Enhance -> Frame Interpolation

Subtitle Review + Frame Interpolation + Audio Enhance
  -> Soft Subtitle Mux
  -> Burn Subtitle
  -> Mux Audio
  -> Output Export
```

展示规则：

- 当前瓶颈卡片用 warning accent，例如橙色描边。
- running 卡片可显示小绿点。
- blocked 卡片可显示红色小角标。
- 此区域只读；点击卡片会选中 stage，并刷新 Inspector。
- 不允许在此页面编辑连线；编辑必须回到 Workflow Canvas。

## 7. Stage Backlog Panel

标题：`Stage Backlog`

显示：

```text
Input / Probe        0
Audio Extract        1
Audio Enhance        1
ASR                  2
OCR                  1
Subtitle Normalize   1
Translate            8 warning
Review               3
Video Enhance        4
Frame Interpolation  5
Soft Mux             1
Burn Subtitle        1
Export               0
```

字段：

```python
class StageBacklogRow(BaseModel):
    stage_key: str
    label_key: str
    runnable_count: int
    queued_count: int
    running_count: int
    blocked_count: int
    paused_count: int
    backlog_limit: int | None
    is_bottleneck: bool = False
    severity: Literal["normal", "warning", "critical"] = "normal"
```

交互：

- 点击 row -> 选中 stage。
- hover 显示 breakdown：running / queued / paused / blocked。
- warning row 显示原因，例如 `Translate backlog 8/8`。
- row 不直接改变策略；策略修改在 Inspector 或 Preset 面板中完成。

## 8. Hardware Lanes Panel

标题：`Hardware Lanes`

默认 lane：

```text
GPU 0
GPU 1
CPU
API
Disk
```

可选 lane：

```text
RAM
Network
Runtime
Cache
```

每个 task block 显示：

```text
task display name
media id / video name
stage
progress %
ETA
state
resource binding
```

示例：

```text
GPU 0 | Enhance V02 78% ETA 2:15 | RIFE V02 68% ETA 2:40 | Translate V01 queued 8/8
GPU 1 | Enhance V03 61% ETA 3:05 | RIFE V03 54% ETA 2:55 | Idle
CPU   | ASR V04 72% ETA 1:35 | ASR V05 queued | Review V01 queued
API   | Translate V02 28% ETA 5:30 | Translate V03 16% ETA 6:10 | Translate V04+ queued
Disk  | Read V02 | Write frames V02 | Write subs V01 | Export V01
```

状态颜色：

| State | Color intent |
|---|---|
| running | green / success |
| queued | blue |
| waiting | yellow / orange |
| paused | gray |
| blocked | red |
| failed | red strong |
| completed | muted green |

交互：

- 点击 task block -> Inspector 显示 task details。
- 点击 lane label -> Inspector 显示 hardware/device details。
- Hover task block -> tooltip 显示 `ResourceRequest`、`ResourceBinding`、waiting reason。
- Debug mode 可显示 task_id、lock_id、worker_pid。
- 不允许在 lane 上直接拖 task 到 GPU；只能提交 preference override，交给 Scheduler 重新计算。

## 9. Scheduling Inspector

根据选中对象切换内容。

### 9.1 选中 Stage

以 `Translate Agent` 为例：

```text
Selected Stage: Translate Agent

Runtime: Remote API / Local LLM
Concurrency: 2
Backlog Limit: 8
Priority: High
Preferred Device: GPU 0
CPU Fallback: Off
Notes: Current bottleneck. New ASR tasks pause when backlog reaches limit.

Suggested Actions:
  Increase API concurrency
  Use smaller model
  Move to GPU 0
  Pause new ASR
```

### 9.2 选中 Hardware Lane

```text
GPU 1
Display Name: NVIDIA RTX xxxx
VRAM: 18.7 / 24 GB
Reserved VRAM: 2048 MB
Active Tasks: 1
Queued Compatible Tasks: 4
Mode: exclusive preferred
```

### 9.3 选中 Task

```text
Task: V04.asr.whisper
State: paused
Reason: translate backlog 8/8
Depends on: V04.audio_extract completed
Preferred Device: GPU 1
Can CPU fallback: yes
Runtime: whisper.cpp / faster-whisper
```

### 9.4 选中 Waiting Reason

```text
Reason: paused_by_backpressure
Policy: max_translate_backlog = 8
Current: 8
Suggested: wait, increase translate concurrency, or pause ASR
```

## 10. Waiting Reasons & Task State Table

列：

```text
Task | Video | Stage | State | Reason | Device | ETA | Actions
```

首版列可简化为：

```text
Task | Video | Stage | State | Reason
```

示例：

| Task | Video | Stage | State | Reason |
|---|---|---|---|---|
| `translate.llm` | V03 | Translate Agent | queued | API concurrency full |
| `asr.whisper` | V04 | ASR Subtitle | paused | translate backlog 8/8 |
| `enhance.rife` | V02 | Frame Interpolation | waiting | depends on Video Enhance |
| `compose.mux_subtitle` | V01 | Soft Subtitle Mux | blocked | waiting for Subtitle Review |
| `output.export` | V05 | Output Export | blocked | waiting for Soft Subtitle Mux |

交互：

- 点击行 -> 选中 task。
- 右键菜单：View events、Open logs、Show dependencies、Show artifacts。
- 普通模式不显示 destructive actions。
- Debug 模式可显示 Release stale lock，但必须二次确认。

## 11. View Mode 分级

### Simple

用户只看到：

```text
当前瓶颈
正在运行
等待原因摘要
推荐动作
```

隐藏：

```text
ResourceBinding
RuntimeBinding
resource_locks
worker_pid
task_events
```

### Standard

显示：

```text
Stage Backlog
Hardware Lanes 简化版
Waiting Reasons
Preset
少量策略调节
```

### Professional

显示：

```text
完整 lane
stage concurrency
backlog limit
device preference
fallback
finish priority
OOM / timeout recovery hints
```

### Debug

显示：

```text
task_id
worker_pid
ResourceRequest
ResourceBinding
RuntimeRequest
RuntimeBinding
resource_locks
heartbeat
stderr path
task_events
cache key
scheduling decisions
```

限制：

- Debug 可以观察和导出诊断。
- Debug 不允许绕过 Scheduler 直接启动 Worker。
- Release stale lock 等危险操作必须有确认和 audit note。

## 12. 自定义范围

### 12.1 视图自定义

允许：

```text
显示 / 隐藏 lane
按视频分组
按 stage 分组
按硬件分组
显示 / 隐藏 Disk / API / RAM lane
显示 ETA / VRAM / waiting reason
保存 workspace layout
```

### 12.2 策略自定义

按等级开放：

| 等级 | 可调内容 |
|---|---|
| Simple | 只能选 preset |
| Standard | concurrency、backlog、finish priority |
| Professional | stage weight、device preference、fallback、reserve VRAM |
| Debug | 查看内部事实，危险操作需确认 |

禁止：

```text
手写 Worker command
手写 shell
手动指定 CUDA_VISIBLE_DEVICES 并绕过 Scheduler
直接写 SQLite
直接释放 live lock
```

## 13. SchedulingPageSnapshot

页面应从一个快照模型读取，不直接散查多个 repository。

```python
class SchedulingPageSnapshot(BaseModel):
    captured_at: str
    batch_id: str
    plan_id: str
    preset_id: str
    view_mode: str

    kpis: SchedulingKpis
    workflow_cards: list[WorkflowCardView]
    stage_backlog: list[StageBacklogRow]
    hardware_lanes: list[HardwareLaneView]
    waiting_tasks: list[WaitingTaskView]
    selected: SchedulingSelection | None
    suggested_actions: list[SchedulingActionView]
```

```python
class HardwareLaneView(BaseModel):
    lane_id: str
    lane_type: Literal["gpu", "cpu", "api", "disk", "ram", "network"]
    display_name: str
    utilization_label: str
    blocks: list[SchedulingBlockView]
```

```python
class SchedulingBlockView(BaseModel):
    task_id: str
    media_id: str
    label: str
    stage_key: str
    state: str
    start_offset_sec: float | None
    estimated_duration_sec: float | None
    progress_percent: float | None
    eta_seconds: float | None
    warning: bool = False
```

首版可以用静态估算 duration；后续通过历史运行数据修正。

## 14. 空状态 / 错误状态

### 无项目

```text
No project opened
Open or create a project to view hardware scheduling.
```

### 无 ExecutionPlan

```text
No execution plan yet
Run workflow validation to generate an ExecutionPlan.
```

### Runtime 缺失

```text
Runtime missing
Some tasks cannot be scheduled because required runtime components are missing.
Action: Open Runtime Manager
```

### Hardware unknown

```text
Hardware unavailable
GPU detector failed; scheduling will use CPU-safe mode.
```

### 任务失败

```text
Task failed
Show error_code, human message, affected downstream tasks, usable artifacts, recovery actions.
```

## 15. UI 与数据刷新

刷新来源：

```text
SQLite task status changes
Worker events appended
resource_locks updated
HardwareSnapshot polling
Runtime health changes
Preset/policy changes
```

建议：

- UI 通过 snapshot 刷新，避免 panel 各自查询不同事实源。
- Hardware utilization 可 1s 刷新。
- task_events / queue 状态可事件驱动或 500ms-1s 合并刷新。
- 不要每帧刷新 timeline；避免 Qt 主线程压力。

## 16. 首版实现建议

### Phase A：Read-only Snapshot

- 新增 `SchedulingPageSnapshot` builder。
- 从现有 tasks/events/locks 生成 kpi、stage backlog、waiting table。
- 不画 timeline，只显示表格和 backlog。

### Phase B：Static Hardware Lanes

- 按当前 running / queued task 显示 lane。
- ETA 可为空或粗略。
- 不做拖拽。

### Phase C：Preset Selector

- 接入 `SCHEDULING_PRESETS_SPEC.md`。
- 允许切换 preset，但先只影响后续调度，不改变 running task。

### Phase D：Professional Inspector

- 显示 selected stage/task/device。
- 开放少量策略 override。

### Phase E：Debug Mode

- 显示 resource_locks、worker_pid、stderr path、task_events。
- 支持导出诊断报告。

## 17. 与其他文档的关系

```text
BATCH_PIPELINE_SCHEDULING_SPEC
  -> 提供 stage backlog、waiting reason、backpressure 语义

SCHEDULING_PRESETS_SPEC
  -> 定义 preset 和策略参数

EXECUTION_PLAN_SPEC
  -> 提供 task DAG 和 status machine

HARDWARE_SCHEDULING_SPEC
  -> 提供硬件检测、资源绑定、resource locks

WORKER_PROTOCOL
  -> 提供 progress / heartbeat / failed / completed 事件

UI_WORKSPACE_SPEC
  -> 提供 dockable workspace 和 layout persistence 边界
```

## 18. Blockers

- 内置卡片目录尚未完全冻结。
- `SchedulingPageSnapshot` 需要后端支持。
- WaitingReason 需要 Scheduler 统一生成。
- ETA / duration 估算首版会不准，必须标记为 estimate。

## 19. 参考资料

- Qt Application Main Window: https://doc.qt.io/qt-6/mainwindow.html
- Qt QMainWindow: https://doc.qt.io/qt-6/qmainwindow.html
- Qt QDockWidget: https://doc.qt.io/qt-6/qdockwidget.html
- NVIDIA NVML API: https://docs.nvidia.com/deploy/nvml-api/
