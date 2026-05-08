# Interactive GUI Workbench 主计划

## Objective

把 Atelier GUI 从“只读工作台壳 + 最小 run intent”推进为真正可交互的创作者工作站。

本主计划服务 GUI 专线对话，重点放在：

```text
Workflow Canvas
  -> Execution Canvas
  -> Queue Monitor
  -> Inspector / Runtime / Recovery panels
  -> Workspace persistence
```

GUI 的目标不是演示一个低完成度按钮流程，而是逐步建立 Atelier 的核心产品模型：

```text
Make the workflow visible.
Make hardware execution controllable.
Make failures recoverable.
```

## Scope

- 建立长期 GUI 交互主线，使 GUI 任务可以独立消耗上下文、token 和验证周期。
- 保持 GUI 与后端全局统筹分工清楚：
  - GUI 专线：界面结构、Workflow Canvas、Execution Canvas、Queue Monitor、Inspector、workspace、交互状态、视觉与动效。
  - 全局/后端专线：Scheduler、Worker、RuntimeManager、Storage、adapters、recovery execution、plugin/release/security 等后端能力。
- 优先推进 `workflow_canvas_foundation`，不优先做低完成度 file picker 演示。
- 保持 GUI 不直接执行 worker、FFmpeg、模型推理或硬件调度。
- 建立本地专属 `AtelierUI` 库治理边界，用于未来自绘控件、动效、overlay、theme tokens 和共享 GUI 视觉基础；该库只服务 Atelier，不作为成熟通用库发布。

暂不把本主计划当作单个巨大实现任务。每个阶段需要拆独立子计划，并按 TDD / GUI smoke / 必要视觉验证推进。

## Current Facts

- 当前已有最小 PySide6 `MainWindow`、dock workspace、Runtime Setup panel、Queue placeholder 和 workspace layout persistence。
- 当前已有 `WorkbenchSnapshot`，可读取 task status、events、artifact paths、final output paths 和 failure code/message。
- 当前已有 `WorkflowRunAppService`，可从 app service 边界运行 persisted fake `media.audio_extract -> output.export` plan。
- 当前已有 `WorkflowRunIntentExecutor`，GUI run intent 不会阻塞 Qt 点击路径。
- 当前 central view 仍是 placeholder，不是真正 Workflow Canvas。
- 当前 Queue panel 仍是 text placeholder，不是模型视图、表格 delegate 或 recovery UI。
- 当前 GUI user-facing strings 还未接入 I18nManager / Qt translation keys。
- 当前 GUI motion 已有 `docs/UI_MOTION_SPEC.md` 作为规划规范；`AtelierUI` 已有最小纯 Python theme tokens 和 widget intake checklist，但尚未实现 motion layer。
- 当前已有 `docs/plan/gui_workbench/plan_atelier_ui_local_library_governance.md`，记录 `AtelierUI` 本地专属库、用户审查和参考优先规则。
- 当前已有 `docs/plan/gui_workbench/plan_atelier_ui_foundation.md`，记录 `atelier/gui/ui/` 最小地基。
- 当前已有 dev-only 控件画板入口：`.venv\Scripts\python -m atelier.gui.ui.component_workbench`。当前可见工作区已聚焦 `VideoInputCard 候选` 和 WorkCanvas 预览，旧 token / typography / checklist 预览只保留为历史阶段记录。

## Constraints

- GUI 不得直接运行 heavy video、ASR、LLM、AI enhancement、FFmpeg 或 model backend。
- GUI 不得绕过 Scheduler、RuntimeManager、Storage 或 Worker protocol。
- GUI button handler 只能提交 intent、刷新 view model 或调用 app service 边界。
- Workflow Canvas 是 Atelier 核心，不做 ComfyUI-style 自由大图；按 `DESIGN.md` 使用卡片式轻节点系统。
- Execution Canvas 从 WorkflowGraph 派生，并允许硬件计划调整；GUI 不自行分配硬件资源。
- Queue Monitor 必须展示多阶段状态、artifact、logs、failure facts 和 recovery affordances，不只显示一个进度条。
- 交互实现必须保留 Qt main event loop 响应性；长任务需要后台边界。
- UI 文字后续需要接入 I18n；当前 placeholder 文字只允许作为过渡状态。
- 不引入 web stack、Electron、Tauri、QML 或成熟第三方 UI framework，除非用户明确要求架构迁移。
- 新自绘控件进入 `AtelierUI` 并被软件调用前，必须经过用户审查。
- 自绘控件、delegate、overlay 或动画如有开源参考项目或参考代码，必须先调研借鉴结构、状态模型、测试方式和许可证边界，再做 Atelier 自己的实现。
- `AtelierUI` 只作为 Atelier 本地专属库随 Runtime 或核心代码打包，不作为成熟库发布。

## Execution Plan

### Phase 1: `workflow_canvas_foundation`

目标：
- 建立真正的卡片式 Workflow Canvas 基础。

完成信号：
- central view 不再只是 placeholder。
- 有 PySide6-native canvas/widget 边界，能渲染最小 `WorkflowGraph` 节点卡片和边关系。
- 节点选择能更新 Inspector 或预留 Inspector view model。
- Graph data 与 visual state 分离；GUI 不直接执行 workflow。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_gui_workflow_canvas_foundation
.venv/Scripts/python -m unittest tests.test_gui_smoke
```

状态：

- 已完成首版 foundation。

### Phase 2: Execution Canvas read model

目标：
- 从 `ExecutionPlan` 读取执行阶段、lane、hardware binding 和 task DAG 的可视化模型。

完成信号：
- Execution panel 不再只是 placeholder。
- 可展示 phases / lanes / tasks / resource binding。
- 与 Scheduler 事实源对齐，GUI 不自行做资源分配。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_gui_execution_canvas_state
```

状态：

- 未开始。

### Phase 3: Queue Monitor model/view foundation

目标：
- 把 Queue panel 从 text placeholder 推进为可扫描、可扩展的 queue monitor。

完成信号：
- 使用明确 view model 或 Qt model/view 边界展示 task rows。
- 展示 stage、status、progress/event count、artifact/final output、failure facts。
- 为 recovery actions 预留位置，但不执行 recovery。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_gui_queue_monitor
```

状态：

- 未开始。

### Phase 4: Inspector and node parameter surface

目标：
- 建立节点 Inspector 和参数展示/编辑边界。

完成信号：
- 选中 Workflow node 后 Inspector 可显示 node type、params、resource preference、runtime requirements。
- 首版可以只读或受控编辑，不能每个 feature 自己发明参数 UI。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_gui_inspector
```

状态：

- 未开始。

### Phase 5: Workspace interaction and motion foundation

目标：
- 接入 `docs/UI_MOTION_SPEC.md` 中最小 motion tokens / driver，并完善 workspace interaction。

完成信号：
- motion tokens 有单一来源。
- 至少两个控件复用同一 motion/transition 边界。
- reduced motion 有最小测试。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_gui_motion
```

状态：

- 未开始。

### Phase 6: GUI integration docs and visual verification

目标：
- 每个 GUI 子计划完成后，更新 code map / recent changes / design notes，并在必要时进行截图或手动视觉验证记录。

完成信号：
- GUI 文件职责、边界、测试和未实现范围清楚。
- 对视觉/布局/交互改动有可复查记录。

验证：

```powershell
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

状态：

- 未开始。

## Child Plans

- 已创建并执行 `docs/plan/gui_workbench/plan_workflow_canvas_foundation.md`。
- 后续可拆 `docs/plan/plan_execution_canvas_read_model.md`。
- 后续可拆 `docs/plan/plan_queue_monitor_model_view.md`。
- 后续可拆 `docs/plan/plan_gui_inspector_node_params.md`。
- 已创建 `docs/plan/gui_workbench/plan_atelier_ui_local_library_governance.md`。
- 已创建并执行 `docs/plan/gui_workbench/plan_atelier_ui_foundation.md` 的首版最小地基。
- 后续 GUI / AtelierUI / 画板 / UI 打磨计划默认放在 `docs/plan/gui_workbench/`。
- 后续可拆 `docs/plan/gui_workbench/plan_gui_motion_foundation.md`。

明确不优先执行：

- `gui_file_import_output_intent` 暂缓。原因：低完成度演示软件意义不大，且容易让 GUI 变成“文件选择 + 跑按钮”的窄产品，而不是 Atelier 的 workflow workstation。

## Verification

本主计划级验证命令：

```powershell
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

当前验证事实：

- `.venv\Scripts\python -m unittest tests.test_gui_workflow_run_intent tests.test_gui_smoke tests.test_gui_app_entry tests.test_gui_workflow_run_entry`：11 tests passed。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed。
- `.venv\Scripts\python -m unittest discover -s tests`：124 tests passed。
- `Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'`：no matches。
- `git diff --check`：passed，仅有 Windows CRLF conversion warnings。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_foundation tests.test_gui_workflow_canvas_foundation tests.test_gui_smoke`：14 tests passed after `AtelierUI` foundation。
- `.venv\Scripts\python -m unittest discover -s tests`：132 tests passed after `AtelierUI` foundation。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：14 tests passed after `AtelierUI Component Workbench` foundation。
- `.venv\Scripts\python -m unittest discover -s tests`：136 tests passed after `AtelierUI Component Workbench` foundation。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：15 tests passed after `AtelierUI Component Workbench` controls phase。
- `.venv\Scripts\python -m unittest discover -s tests`：137 tests passed after `AtelierUI Component Workbench` controls phase。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：8 tests passed after `AtelierUI Component Workbench` review snapshot phase。

## Progress / Decisions

- 2026-05-07：创建本主计划。决策：GUI 专线对话专注交互式工作台，另一个全局/后端对话负责项目统筹和后端推进。
- 2026-05-07：决策：下一步选择 `workflow_canvas_foundation`，暂不优先做 `gui_file_import_output_intent` 演示路线。
- 2026-05-07：完成 `workflow_canvas_foundation` 首版。`MainWindow` central view 已接入 PySide6-native `WorkflowCanvas`，可渲染最小 `WorkflowGraph` 节点和边，并保持 selection 作为 GUI-only visual state。
- 2026-05-07：新增 `AtelierUI` 本地专属库治理规则。决策：所有新自绘控件先经用户审查再入库并被软件调用；有参考项目时先调研借鉴，不无依据手搓；本次只沉淀文档规则，不迁移现有 canvas 代码。
- 2026-05-07：执行 `plan_atelier_ui_foundation.md` 首版。新增 `atelier/gui/ui/`、纯 Python `theme_tokens.py` 和 `widget_intake.py`，作为后续动效和自绘控件的最小地基；全量验证为 132 tests passed。
- 2026-05-07：执行 `plan_atelier_ui_component_workbench_foundation.md` 第一阶段。新增 dev-only `AtelierUI Component Workbench`，候选自绘控件后续可先在产品 GUI 外做 token / state / checklist 预览和用户审查。
- 2026-05-07：执行 `plan_atelier_ui_component_workbench_controls.md` 第二阶段。画板现在支持 catalog 切换、story states 和 controls metadata 展示，仍不做真实自绘控件或产品调用。
- 2026-05-07：执行 `plan_atelier_ui_component_workbench_screenshot.md` 第三阶段。画板现在可保存当前窗口 PNG 和 JSON 审查备注记录，仍不代表候选控件已通过用户审查。

## Blockers

- 暂无。
