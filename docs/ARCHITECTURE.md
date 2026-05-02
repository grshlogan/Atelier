# Atelier 架构草案

本文档是 Atelier 的首版技术栈与软件骨架规划。当前仍处于规划阶段，不代表已经实现。

## 1. 推荐路线

首版采用：

```text
Python 3.12
PySide6 + Qt Widgets
QGraphicsView / QGraphicsScene 自研轻节点 canvas
SQLite + SQLAlchemy 2.0
Pydantic v2 schema
NetworkX DAG utilities
subprocess worker runner + JSON Lines events
FFmpeg / ffprobe typed adapters
PyAV for thumbnails / previews only
psutil + nvidia-ml-py hardware adapters
pytest + ruff + mypy
```

核心判断：

- UI 应先选 `PySide6 + Qt Widgets`，不要首版就走 Qt Quick/QML。
- Canvas 应自研轻节点，而不是直接套完整自由节点编辑器。
- Scheduler 应自研 SQLite-backed local scheduler，不引入 Celery/Redis。
- FFmpeg 应通过 typed command builder 调用，不暴露任意 shell。
- 所有 worker progress 走结构化 JSON Lines，不从普通日志中解析主进度。

## 2. 为什么不是其他路线

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

## 3. 计划中的模块边界

未来代码骨架建议：

```text
atelier/
  app/
    main.py
    bootstrap.py

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

  gui/
    main_window.py
    theme.py
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
- `workers/` 只运行外部任务并上报事件。
- `storage/` 是 SQLite 的唯一入口。
- `gui/` 只提交 intent 和渲染 state。

## 4. 首版最小闭环

第一阶段不接真实模型，先做可信骨架：

```text
Create project
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

## 5. 关键 schema

优先定义这些 Pydantic models：

```text
WorkflowNode
WorkflowEdge
WorkflowGraph
NodeParamSchema
ResourceRequest
ResourceCapacity
ExecutionPlan
ExecutionPhase
ExecutionLane
Task
Artifact
WorkerEvent
FailurePolicy
RecoveryAction
```

这些 schema 是 GUI、SQLite、scheduler、worker protocol 之间的公共语言。

## 6. 数据库首版表

SQLite 首版建议：

```text
projects
jobs
workflow_nodes
workflow_edges
execution_plans
execution_tasks
task_dependencies
artifacts
task_events
resource_locks
cache_entries
presets
```

早期 migration 可以简单，但 schema 变化后应引入 `Alembic`。

## 7. Worker Protocol

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

## 8. 可借鉴项目与库

- `NodeGraphQt`：参考 Python + Qt node graph 交互。
- `qtpynodeeditor`：参考 port/connection 和 node editor model。
- `QtNodes`：参考 Model-View、headless graph、datatype-aware connections、JSON serialization、undo/redo。
- `PyQtGraph`：可参考高性能图表和硬件监控曲线，不作为 workflow canvas。

## 9. Agent Skills

当前可用并适合本项目的工作流：

- `brainstorming`：用于重大产品/架构决策前的方案收敛。
- `planning-with-files`：用于多阶段调研和实现计划。
- `get-api-docs` / Context7：用于第三方库/API 文档确认。
- `test-driven-development`：未来实现 domain / scheduler / storage / worker protocol 前使用。
- `audit` / `polish` / `dogfood`：未来 UI 可运行后用于质量检查。

未发现高可信、安装量大的 PySide6 专用 skill。`skills.sh` 搜索到的 Python GUI / desktop app 相关 skill 多偏自动化或 Rust/Tauri，不适合作为 Atelier 的主要指导。

## 10. 调研来源

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

## 11. 下一步

建议下一步先补：

```text
WORKFLOW_NODE_SPEC.md
EXECUTION_PLAN_SPEC.md
WORKER_PROTOCOL.md
DATABASE_SCHEMA.md
```

等这些文档确认后，再开始 scaffold 代码骨架。
