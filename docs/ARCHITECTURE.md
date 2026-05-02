# Atelier 架构草案

本文档是 Atelier 的首版技术栈与软件骨架规划。当前已有最小 Python 骨架起步，但本文档仍描述目标边界，不代表所有模块都已实现。

## 1. 推荐路线

首版采用：

```text
Python 3.12
PySide6 + Qt Widgets
QGraphicsView / QGraphicsScene 自研轻节点 canvas
QMainWindow / QDockWidget dockable workspace
SQLite + SQLAlchemy 2.0
Pydantic v2 schema
NetworkX DAG utilities
subprocess worker runner + JSON Lines events
FFmpeg / ffprobe typed adapters
PyAV for thumbnails / previews only
psutil + nvidia-ml-py hardware adapters
manifest-driven RuntimeManager / PluginManager
runtime language switching through I18nManager
local-first security with OS credential storage and redacted diagnostics
component updates through ReleaseManager
pytest + ruff + mypy
```

核心判断：

- UI 应先选 `PySide6 + Qt Widgets`，不要首版就走 Qt Quick/QML。
- Canvas 应自研轻节点，而不是直接套完整自由节点编辑器。
- Scheduler 应自研 SQLite-backed local scheduler，不引入 Celery/Redis。
- FFmpeg 应通过 typed command builder 调用，不暴露任意 shell。
- 所有 worker progress 走结构化 JSON Lines，不从普通日志中解析主进度。
- Atelier 必须拥有自己的 runtime 管理层，不假设用户已经全局安装 GUI、FFmpeg、CUDA user-space 组件、llama.cpp、whisper.cpp 或模型文件。
- 发布、runtime、模型、插件应分成独立 manifest 和更新链。
- UI 使用 dockable workspace，不把四区块写死成唯一布局。
- UI 文案从第一天走 i18n key，支持运行时语言切换。
- 硬件状态由 HardwareDetector 观测，Scheduler 做唯一资源绑定。
- 失败恢复要围绕 error_code、partial artifacts、downstream impact 和 recovery actions。
- secrets、插件权限、更新签名和日志脱敏从首版骨架开始建边界。

## 2. Runtime 环境所有权

Atelier 的交付目标不是"源码项目 + 用户自己配环境"，而是一个自带运行环境的本地工作站：

```text
Application Runtime  -> Python / PySide6 / Qt plugins / app dependencies
Tool Runtime         -> FFmpeg / ffprobe / llama.cpp / whisper.cpp / ncnn-vulkan 等
Model Store          -> Whisper、LLM、增强、插帧等模型资产
Hardware Probe       -> GPU driver、CUDA/Vulkan/CPU capabilities 检测
Runtime Manifest     -> 组件版本、路径、hash、能力、状态
```

边界：

- 能随软件分发或下载管理的组件，由 Atelier 管理安装、版本、校验、修复和启停。
- 系统 GPU driver 属于操作系统/硬件层，通常不能由应用直接打包替换；Atelier 负责检测版本、能力和缺失状态，并给出明确修复入口。
- Worker 不读全局 `PATH`，不依赖开发机路径，不自行下载模型；所有工具路径、模型路径和环境变量来自 RuntimeManager 解析出的 RuntimeBinding。
- GUI 只展示 Runtime 状态、安装进度、修复动作和 backend 选择，不直接执行安装脚本或外部工具。
- Cache key 必须把 runtime/backend/model 版本纳入计算，避免不同 backend 复用不兼容产物。

## 3. 为什么不是其他路线

### 路线 A：Qt Widgets + 自研轻节点（推荐）

优点：

- 最贴合当前 `AGENTS.md` 和 `DESIGN.md`。
- GUI、WorkflowGraph、ExecutionPlan、Scheduler、Worker 边界容易守住。
- `QGraphicsView / QGraphicsScene` 天然适合节点卡片、连线、缩放、选择和大型 2D scene。
- 桌面应用稳定，Python 生态足够覆盖 SQLite、FFmpeg、硬件监控和测试。

代价：

- 节点 canvas 需要自己实现交互细节。
- 视觉 polish 要靠自定义绘制和 QSS discipline。

### 路线 B：Qt Quick/QML + Python backend

优点：

- 动效、状态切换和现代 UI 表达更强。
- 长期可以做更丝滑的 canvas 和 inspector。

代价：

- Python/QML 边界复杂。
- 首版工程风险更高。
- 对当前“先搭可信骨架”的阶段不划算。

### 路线 C：直接采用 NodeGraphQt / qtpynodeeditor

优点：

- 节点编辑交互起步快。
- 有现成 port、connection、undo/redo、serialization 参考。

代价：

- 容易把产品带向完全自由 node editor。
- 与 Atelier “卡片式轻节点 + 合法 slot + workflow/execution 分离”的产品边界不完全一致。
- 后续可能反而要拆掉大量默认行为。

结论：第三方 node editor 只作参考，不作为首版核心依赖。

## 4. 计划中的模块边界

未来代码骨架建议：

```text
atelier/
  app/
    main.py
    bootstrap.py
    paths.py

  core/
    ids.py
    time.py
    errors.py

  domain/
    project.py
    job.py
    workflow_graph.py
    execution_plan.py
    task.py
    artifact.py
    worker_event.py
    resources.py
    presets.py

  workflow/
    node_registry.py
    node_schema.py
    validation.py
    graph_builder.py

  planning/
    execution_planner.py
    phase_builder.py
    conflict_detector.py

  scheduler/
    scheduler.py
    queue.py
    resource_locks.py
    recovery.py

  runtime/
    manager.py
    manifest.py
    store.py
    environment.py
    resolver.py
    components.py
    model_store.py
    health.py

  release/
    manager.py
    channels.py
    manifests.py
    update_plan.py
    verifier.py

  plugins/
    manager.py
    manifest.py
    registry.py
    permissions.py

  i18n/
    manager.py
    catalog.py
    formatting.py

  storage/
    db.py
    models.py
    repositories/
    migrations/

  workers/
    protocol.py
    runner.py
    adapters/
      ffmpeg.py
      ffprobe.py
      asr.py
      translate.py
      video_enhance.py

  hardware/
    detector.py
    resources.py
    psutil_adapter.py
    nvidia_adapter.py
    scheduling_policy.py

  security/
    manager.py
    credentials.py
    redaction.py
    permissions.py
    package_integrity.py

  gui/
    main_window.py
    theme.py
    workspace.py
    widgets/
    canvas/
      workflow_canvas.py
      execution_canvas.py
      card_items.py
      edge_items.py
    panels/
      inspector.py
      queue_monitor.py
      hardware_resources.py
      log_viewer.py

  tests/
```

规则：

- `domain/` 不依赖 GUI。
- `workflow/` 只处理 workflow graph 和 node schema。
- `planning/` 把 workflow 转成 execution plan。
- `scheduler/` 决定任务何时运行、占用什么资源。
- `runtime/` 管理软件运行环境、外部工具、backend、模型资产和 RuntimeBinding。
- `release/` 管理发布通道、更新 manifest、校验、staging 和回滚计划。
- `plugins/` 管理插件 manifest、权限、contribution 注册和禁用状态。
- `i18n/` 管理语言包、运行时语言切换和本地化格式化。
- `hardware/` 观测硬件和进程状态，并提供可调度资源快照。
- `security/` 管理 credential references、redaction、权限和包完整性校验。
- `workers/` 只运行外部任务并上报事件。
- `storage/` 是 SQLite 的唯一入口。
- `gui/` 只提交 intent 和渲染 state；workspace 布局由 WorkspaceManager 管理。

## 5. 首版最小闭环

第一阶段不接真实模型，先做可信骨架：

```text
Create project
  -> verify application runtime and simulated tool runtime
  -> load i18n catalog and default workspace layout
  -> load built-in plugin manifests
  -> build sample WorkflowGraph
  -> validate graph
  -> generate ExecutionPlan
  -> enqueue Job
  -> run simulated Worker
  -> emit JSON Lines events
  -> persist tasks / events / artifacts
  -> update Queue Monitor and Hardware Resources
  -> simulate failure and recovery action
```

这个闭环能验证 Atelier 最重要的产品事实：

```text
流程可见
硬件可解释
失败可恢复
产物可追踪
```

## 6. 关键 schema

优先定义这些 Pydantic models：

```text
WorkflowNode
WorkflowEdge
WorkflowGraph
NodeParamSchema
ResourceRequest
ResourceBinding
HardwareSnapshot
RuntimeRequirement
RuntimeRequest
RuntimeBinding
RuntimeManifest
ModelAssetManifest
PluginManifest
ReleaseManifest
WorkspaceLayout
LocaleCatalog
FailureRecord
RecoveryAction
CredentialRef
ExecutionPlan
ExecutionPhase
ExecutionLane
ExecutionTask
Artifact
WorkerEvent
FailurePolicy
```

这些 schema 是 GUI、SQLite、scheduler、worker protocol 之间的公共语言。

## 7. 数据库首版表

SQLite 首版建议：

```text
projects
jobs
workflow_graphs
execution_plans
execution_tasks
task_dependencies
artifacts
task_artifacts
task_events
resource_locks
cache_entries
presets
runtime_components
model_assets
credential_refs
```

早期 migration 可以简单，但 schema 变化后应引入 `Alembic`。

## 8. Worker Protocol

Worker 输出 JSON Lines，例如：

```json
{"type":"started","task_id":"task_001","message":"started"}
{"type":"progress","task_id":"task_001","current":12,"total":100,"unit":"frames"}
{"type":"log","task_id":"task_001","level":"info","message":"loaded backend"}
{"type":"artifact","task_id":"task_001","artifact_type":"subtitle","path":"cache/raw_asr.srt.part"}
{"type":"completed","task_id":"task_001","artifact_path":"cache/raw_asr.srt"}
{"type":"failed","task_id":"task_001","error_code":"OOM","message":"GPU memory exhausted"}
```

GUI 只能信任结构化事件和数据库状态，不把普通日志当主进度来源。

## 9. 可借鉴项目与库

- `NodeGraphQt`：参考 Python + Qt node graph 交互。
- `qtpynodeeditor`：参考 port/connection 和 node editor model。
- `QtNodes`：参考 Model-View、headless graph、datatype-aware connections、JSON serialization、undo/redo。
- `PyQtGraph`：可参考高性能图表和硬件监控曲线，不作为 workflow canvas。

## 10. Agent Skills

当前可用并适合本项目的工作流：

- `brainstorming`：用于重大产品/架构决策前的方案收敛。
- `planning-with-files`：用于多阶段调研和实现计划。
- `get-api-docs` / Context7：用于第三方库/API 文档确认。
- `test-driven-development`：未来实现 domain / scheduler / storage / worker protocol 前使用。
- `audit` / `polish` / `dogfood`：未来 UI 可运行后用于质量检查。

未发现高可信、安装量大的 PySide6 专用 skill。`skills.sh` 搜索到的 Python GUI / desktop app 相关 skill 多偏自动化或 Rust/Tauri，不适合作为 Atelier 的主要指导。

## 11. 调研来源

- Qt for Python / PySide6: https://doc.qt.io/qtforpython-6/
- Qt Graphics View Framework: https://doc.qt.io/qt-6/graphicsview.html
- SQLAlchemy 2.0: https://docs.sqlalchemy.org/en/20/
- Pydantic: https://pydantic.dev/docs/validation/latest/get-started/
- NetworkX DAG algorithms: https://networkx.org/documentation/stable/reference/algorithms/dag.html
- FFprobe documentation: https://ffmpeg.org/ffprobe.html
- PyAV documentation: https://pyav.org/docs/stable/
- psutil documentation: https://psutil.readthedocs.io/latest/
- nvidia-ml-py: https://pypi.org/project/nvidia-ml-py/
- Python subprocess: https://docs.python.org/3/library/subprocess.html
- pytest: https://docs.pytest.org/en/stable/
- Ruff: https://docs.astral.sh/ruff/
- APScheduler: https://apscheduler.readthedocs.io/en/master/
- NodeGraphQt: https://github.com/jchanvfx/NodeGraphQt
- qtpynodeeditor: https://klauer.github.io/qtpynodeeditor/
- QtNodes: https://github.com/paceholder/nodeeditor
- PyQtGraph: https://github.com/pyqtgraph/pyqtgraph

## 12. 下一步

首版 skeleton 已开始落地，下一步继续补最小闭环：

```text
1. 已创建 Python package / pyproject / test baseline
2. 已实现 domain schema、worker event schema、SQLite schema 初始化
3. 已加入 RuntimeManager manifest binding、RuntimeStore、RuntimeHealthChecker 和 sha256 校验基础
4. 接 sample WorkflowGraph -> ExecutionPlan -> queue -> SQLite events/artifacts 的最小闭环
5. 最后接 PySide6 主窗口和只读状态面板
```
