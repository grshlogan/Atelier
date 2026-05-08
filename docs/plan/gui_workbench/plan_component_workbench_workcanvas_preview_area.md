# Component Workbench WorkCanvas Preview Area Plan

## Objective

把控件画板推进到更接近真实 WorkCanvas 的预览环境：候选节点卡片不只孤立展示，而是在 dev-only WorkCanvas 预览承载区里观察画布背景、节点定位、preview artifact 策略和未来矢量化迁移边界。

## Scope

- 沉淀 WorkCanvas preview / thumbnail cache / ComfyUI 借鉴结论到正式文档。
- 在 `AtelierUI` 控件画板中新增 dev-only WorkCanvas 预览区。
- 首阶段只承载现有 `VideoInputCardCandidate`，不改变产品 `MainWindow` 和真实 `WorkflowCanvas`。
- 使用 TDD：先写失败测试，再实现最小 UI。

## Current Facts

- `VideoInputCardCandidate` 当前仍是 QWidget 组合候选，适合画板打磨，不适合作为最终 WorkCanvas 大量节点的直接实现。
- 真实 WorkCanvas 当前位于 `atelier/gui/workflow_canvas.py`，使用 `QGraphicsView/QGraphicsScene` 作为基础。
- 缩略图和预览内容未来应来自 preview artifact / thumbnail cache，GUI 不应在 paint 路径中解码或生成。
- `docs/plan/gui_workbench/` 已作为 GUI / AtelierUI / 控件画板 / UI 打磨计划目录。

## Constraints

- 控件画板仍是 dev-only 工具，不进入默认工作台。
- GUI 不直接运行 worker、FFmpeg、模型推理、硬件调度、任意 shell 或 SQLite mutation。
- WorkCanvas 预览区不代表候选控件已通过用户审查或进入共享 `AtelierUI` 调用。
- 第一阶段不引入 Vulkan、Qt Quick、QML 或新的渲染栈。
- 第一阶段不把 QWidget 候选卡片嵌入真实 `QGraphicsScene` 产品路线；只是用于画板观察。

## Execution Plan

### Phase A - Preview artifact strategy document

目标：
- 新增 WorkCanvas preview artifact 策略文档，记录 ComfyUI 可借鉴点和 Atelier 的取舍。

完成信号：
- 文档明确 preview artifact、thumbnail cache、GUI-only drawing、ComfyUI 借鉴与不照搬边界。

验证：
- 文档链接进入 README / recent changes。

### Phase B - Red test for workbench preview area

目标：
- 先在 `tests/test_gui_atelier_ui_component_workbench.py` 中新增失败测试。

完成信号：
- 测试能证明当前画板缺少 WorkCanvas 预览承载区。

验证：
```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_workbench_exposes_workcanvas_preview_area_for_node_card
```

### Phase C - Minimal dev-only WorkCanvas preview area

目标：
- 在 `component_workbench.py` 中新增 WorkCanvas 预览区，并把 `VideoInputCardCandidate` 放入该区域。

完成信号：
- 预览区有稳定 objectName、边界属性和中文标题。
- 预览区声明 thumbnail policy 为 cached preview artifact only。
- 选中 `VideoInputCard 候选` 后，卡片在 WorkCanvas 预览区内可见。

验证：
```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

### Phase D - Handoff docs and checks

目标：
- 更新 README、APP_CODE_MAP、RECENT_CHANGES 和相关 plan。
- 运行最小目标测试、compileall、文档空白扫描和 `git diff --check`。

## Child Plans

- 后续可拆 `plan_workcanvas_vector_node_item_migration.md`，用于把 QWidget 候选节点卡片转译成 `QGraphicsItem` / 自绘 paint 版本。
- 后续可拆 `plan_workcanvas_thumbnail_cache_boundary.md`，用于真实 preview artifact / thumbnail cache 读模型。

## Verification

- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`
- `.venv\Scripts\python -m compileall -q atelier tests`
- `Select-String -Path .\README.md, .\AGENTS.md, .\DESIGN.md, .\docs\*.md, .\docs\plan\*.md, .\docs\plan\gui_workbench\*.md -Pattern '[ \t]+$'`
- `git diff --check`

当前验证事实：

- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_workbench_exposes_workcanvas_preview_area_for_node_card`：red first，失败原因为缺少 `component-workbench-workcanvas-preview`。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_workbench_exposes_workcanvas_preview_area_for_node_card`：passed after implementation。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：13 tests passed。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：23 tests passed。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed。
- 文档空白扫描：no matches。
- `git diff --check`：passed with only Windows CRLF conversion warnings。

## Progress / Decisions

- 2026-05-08：创建本计划。决策：第一阶段只做 dev-only WorkCanvas 预览承载区，不把 QWidget 候选卡片作为真实产品 canvas 路线。
- 2026-05-08：完成 Phase A-C。新增 `docs/WORKCANVAS_PREVIEW_ARTIFACT_SPEC.md`，并在控件画板中加入 `component-workbench-workcanvas-preview`，用于承载当前 `VideoInputCardCandidate`。
- 2026-05-08：完成 Phase D。接手文档、计划索引、README 和验证事实已更新。

## Blockers

- 暂无。
