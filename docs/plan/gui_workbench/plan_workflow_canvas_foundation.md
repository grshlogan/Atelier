# Workflow Canvas Foundation 计划

> 执行顺序：GUI 专注对话的下一个计划。本文只处理 GUI 层的 Workflow Canvas 基础，不处理 Scheduler、Worker、RuntimeManager、Storage、adapters、recovery execution、plugin/release/security。

## Objective

建立真正的卡片式 Workflow Canvas 基础，让 `MainWindow` 的 central view 不再只是 placeholder，并为后续 Workflow 编辑器、Execution Canvas 和 Inspector 接线打下 PySide6-native 边界。

首版目标链路：

```text
WorkflowGraph
  -> WorkflowCanvasViewModel
  -> PySide6-native WorkflowCanvas
  -> node card visual items + edge visual items
  -> selection signal / inspector view model placeholder
```

本计划的目标不是执行 workflow，也不是实现完整编辑器。GUI 只渲染 graph、提交 intent、读取 snapshot / view model，不直接运行 worker、FFmpeg、模型推理或硬件调度。

## Scope

- 新增最小 Workflow Canvas GUI 模块。
- central view 从纯 placeholder 变为 PySide6-native canvas/widget 边界。
- 渲染最小 `WorkflowGraph` 节点卡片和边关系。
- 保持 graph data 与 visual state 分离。
- 节点选择可以更新或预留 Inspector view model。
- 使用 TDD：先写 `tests/test_gui_workflow_canvas_foundation.py` 的失败测试，再实现最小代码。
- 更新 `APP_CODE_MAP.md`、`RECENT_CHANGES.md` 和相关 plan。

暂不实现：

- 完整 Workflow Canvas 编辑能力。
- 节点拖拽持久化、连线编辑、端口级验证。
- 真实 Inspector 表单生成。
- Execution Canvas。
- Queue Monitor delegate 重做。
- 文件选择、输出 intent、run button 演示增强。
- 后端 workflow 执行、Scheduler claim、worker、adapter 或 FFmpeg 调用。

## Current Facts

- `atelier/workflow/graph.py` 已有最小 `WorkflowGraph`、`WorkflowNode`、`WorkflowEdge`、`WorkflowPortRef`。
- `atelier/gui/main_window.py` 当前 central widget 已包含 placeholder title 和最小 run intent 控件。
- `docs/Atelier_Main_UI_Spec.md` 推荐 Workflow Canvas 使用 `QGraphicsView` / `QGraphicsScene` / node item / edge item。
- `docs/UI_WORKSPACE_SPEC.md` 要求 Workflow Canvas 是 central widget 的默认主舞台，Queue / Hardware / Inspector 作为 dock panels。
- `docs/UI_MOTION_SPEC.md` 已定义未来 motion token、canvas motion 和 visual-state 分离边界。
- `docs/plan/gui_workbench/plan_atelier_ui_local_library_governance.md` 已规定 `AtelierUI` 是本地专属库；新自绘控件必须先经用户审查，再作为库组件被软件调用。
- 当前验证基线为 `.venv\Scripts\python -m unittest discover -s tests`，最近本地复验为 122 tests passed。

## Constraints

- GUI 不直接运行 workflow。
- GUI 不直接调用 Scheduler、Worker、FFmpeg、模型或 adapter。
- WorkflowGraph 是数据事实源；canvas item 的选择、高亮、hover 等只是 visual state。
- `WorkflowCanvas` 不写 SQLite，不读取 RuntimeManager，不持久化 graph。
- 用户可见 UI 文案后续应进入 I18N；本计划只做最小可验证英文 placeholder。
- 保留现有 `MainWindow` run intent 边界，不回退当前未提交 GUI 改动。
- 当前 `WorkflowCanvas` 是 Workflow Canvas foundation 的候选基础实现，不等于已经完成 `AtelierUI` 共享自绘控件入库审查。
- 后续如果要把 node item、edge item、selection ring、drag ghost 或 canvas overlay 抽为 `AtelierUI` 共享控件，必须先补参考调研、最小验证和用户审查记录。

## Execution Plan

### Phase A: Canvas view model and widget boundary

目标：

- 新增 PySide-independent canvas view model 或轻量 snapshot。
- 新增 PySide6-native `WorkflowCanvas` widget，接受 view model / graph 渲染。

完成信号：

- 测试可由 `WorkflowGraph` 构造 canvas view model。
- canvas 不依赖 Scheduler / RuntimeManager / SQLite。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_workflow_canvas_foundation
```

状态：

- 已完成。

### Phase B: Render node cards and edge relations

目标：

- 在 canvas 中渲染节点卡片和边关系的最小视觉对象。

完成信号：

- 测试能找到两个 node card visual items。
- 测试能找到一条 edge visual item。
- card 显示 node type / node id 的稳定文本。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_workflow_canvas_foundation
```

状态：

- 已完成。

### Phase C: Selection and Inspector placeholder

目标：

- 节点选择更新 canvas visual state，并暴露 Inspector 可消费的最小 selection view model。

完成信号：

- 测试点击/调用 select 后能得到 selected node id。
- selection 不修改 `WorkflowGraph` 数据。
- `MainWindow` 能接收 selection signal 或预留 inspector label / view model。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_workflow_canvas_foundation tests.test_gui_smoke
```

状态：

- 已完成。

### Phase D: MainWindow central integration

目标：

- `MainWindow` central view 使用 `WorkflowCanvas`，不再只是纯 placeholder。

完成信号：

- `MainWindow` 默认可构造 canvas。
- 注入 `WorkflowGraph` 时 central canvas 能渲染最小 graph。
- 现有 run intent 控件仍只提交 intent，不执行 workflow。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_workflow_canvas_foundation tests.test_gui_smoke
```

状态：

- 已完成。

### Phase E: Documentation alignment

目标：

- 更新代码地图、最近变更和主计划。

完成信号：

- `APP_CODE_MAP.md` 记录新增 Workflow Canvas 模块、职责和边界。
- `RECENT_CHANGES.md` 记录实现范围、未实现范围和验证事实。
- `plan_main_app_skeleton.md` child plan / progress 对齐。
- 本计划标记完成进度。

验证：

```powershell
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

状态：

- 已完成。

## Child Plans

- 后续可拆 `plan_workflow_canvas_editing_intents.md`，用于 node add/remove/move/connect intent。
- 后续可拆 `plan_inspector_dynamic_params_foundation.md`，用于基于 `WORKFLOW_NODE_SPEC.md` 的 Basic / Advanced / Expert 参数面板。
- 后续可拆 `plan_execution_canvas_foundation.md`，用于从 `ExecutionPlan` 派生硬件执行视图。
- 后续可拆 `plan_atelier_ui_self_painted_widget_intake.md`，用于 Workflow node / edge 等自绘控件进入 `AtelierUI` 前的参考调研和用户审查。

## Verification

计划验证命令：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_workflow_canvas_foundation
.venv\Scripts\python -m unittest tests.test_gui_workflow_canvas_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

当前验证事实：

- `.venv\Scripts\python -m unittest tests.test_gui_workflow_canvas_foundation`：3 tests passed after the first green slice。
- `.venv\Scripts\python -m unittest tests.test_gui_workflow_canvas_foundation tests.test_gui_smoke`：10 tests passed after `MainWindow` integration。
- `.venv\Scripts\python -m unittest tests.test_gui_workflow_canvas_foundation tests.test_gui_smoke`：10 tests passed in final verification。
- `.venv\Scripts\python -m unittest discover -s tests`：128 tests passed。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed。
- `Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'`：no matches。
- `git diff --check`：passed with only Windows CRLF conversion warnings。

## Progress / Decisions

- 2026-05-07：创建本计划。决策：本对话只专注 GUI，第一阶段先建立 Workflow Canvas 基础，不做文件选择、运行按钮演示增强或后端统筹。
- 2026-05-07：TDD 红灯确认：`tests.test_gui_workflow_canvas_foundation` 首先因缺少 `atelier.gui.workflow_canvas` 失败。
- 2026-05-07：完成 Phase A/B。新增 `atelier/gui/workflow_canvas.py`，包含 canvas view model、`QGraphicsView` canvas、node card 和 edge path 渲染。
- 2026-05-07：完成 Phase C。`WorkflowCanvas.select_node()` 更新 GUI-only selection state，并发出 `selection_changed`，不修改 `WorkflowGraph`。
- 2026-05-07：完成 Phase D。`MainWindow` central view 接入 `WorkflowCanvas`，并保留现有 run intent 控件边界。
- 2026-05-07：完成 Phase E 首版文档对齐。`APP_CODE_MAP.md`、`RECENT_CHANGES.md`、`plan_main_app_skeleton.md` 和 `plan_main_interactive_gui_workbench.md` 已记录当前 canvas 边界。
- 2026-05-07：补充 `AtelierUI` 本地专属库治理边界。当前 `WorkflowCanvas` 仍保留在 feature 模块中作为 foundation，不迁入专属库；后续共享化前需要用户审查。

## Blockers

- 暂无。
