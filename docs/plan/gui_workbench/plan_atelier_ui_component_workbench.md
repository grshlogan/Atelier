# AtelierUI Component Workbench 计划

> 本计划只规划 AtelierUI 控件画板 / component workbench，不实现真实控件，不接入 Worker / FFmpeg / Scheduler，不把候选控件放入真实产品 GUI 中调参。

## Objective

建立 AtelierUI 自绘控件进入真实软件前的独立调试与审查环境。

核心原则：

```text
Tune self-painted widgets outside the product GUI.
Review candidates before shared adoption.
Keep the workbench dev-only.
```

控件画板的目标不是成为正式功能页，而是帮助开发和审查：

- 调整自绘控件参数。
- 查看不同状态、尺寸、密度、主题 token 和 motion token。
- 对比候选实现和参考项目的取舍。
- 生成可复查的截图或 smoke 记录。
- 在用户审查通过前阻止候选控件进入 `AtelierUI` 共享调用。

## Scope

- 规划一个 dev-only `AtelierUI Component Workbench`。
- 首选作为仓库内独立 PySide6 开发入口，而不是产品主窗口的一部分。
- 支持候选控件按 catalog / story / scenario 组织。
- 支持参数面板、状态切换、尺寸 preset、theme token 查看和截图记录。
- 记录可借鉴的外部工具模型，但不引入 web stack 或迁移到 QML。

暂不实现：

- 自绘控件迁移。
- 自动视觉回归服务。
- Qt Designer plugin。
- Figma / web / Electron 画板。

## Current Facts

- 当前已有第三阶段 `AtelierUI` 控件画板入口：`.venv\Scripts\python -m atelier.gui.ui.component_workbench`。
- 当前可打开的 GUI 入口是 `.venv\Scripts\python -m atelier.gui.app`，它是产品工作台壳，不应用于调试候选自绘控件。
- 当前 `atelier/assets/preview.html` 是图标预览，不是 Qt 控件画板。
- 当前 `atelier/assets/Main.py` 是贝塞尔曲线辅助工具，不是产品控件画板，也不是已审查 `AtelierUI` 组件。
- `atelier/gui/ui/` 当前有纯 Python theme tokens、widget intake checklist metadata、PySide-independent component workbench state 和 dev-only PySide6 component workbench。
- 当前可见画板已收敛为 `VideoInputCard 候选` + WorkCanvas 预览打磨工作区：旧 `WorkflowNodeItem 候选`、主题 token 预览、右侧入库审查清单从当前工作区隐藏 / 归档。
- 当前 WorkCanvas 预览区支持卡片入口切换、基础 zoom / pan、全屏预览、全屏 overlay 控件和 dev-only 性能 HUD。
- 当前控件画板窗口默认 1980 px × 1080 px，每次显示时按当前屏幕重新居中，不以关闭位置为准。
- 当前已有 `docs/plan/gui_workbench/archive/component_workbench_phases/plan_atelier_ui_component_workbench_review_page.md`，把 PNG / JSON 审查产物生成静态 HTML review page，并明确 GitHub 收录边界。

## Constraints

- 控件画板必须 dev-only，不进入默认产品工作台。
- 控件画板不得运行 Worker、FFmpeg、模型推理、硬件调度、任意 shell 或 SQLite mutation。
- 控件画板可以读取 `AtelierUI` tokens 和构造候选控件，但不能自动批准入库。
- 候选控件在画板中可调参，不代表能被真实 GUI 调用；真实调用仍需要用户审查。
- 不迁移到 Electron / React / web stack / QML，除非用户明确要求架构迁移。
- 截图和 smoke 记录不能替代 TDD；新控件仍需先写失败测试或可复查的 GUI smoke。
- 控件画板源码、测试、文档和开发脚本应进入 GitHub；`.atelier/component-workbench/reviews/` 下生成的 PNG / JSON / HTML 审查产物不进入 GitHub。

## Reference Models

这些项目和工具是工作流模型参考，不是当前依赖：

- [Storybook Controls](https://storybook.js.org/docs/essentials/controls)：可借鉴 args / controls / stories 模型，让一个组件在多个参数状态下被调试。
- [Storybook Component Tests](https://storybook.js.org/docs/8/writing-tests/component-testing)：可借鉴 interaction playback、pause / resume / step 的调试体验。
- [Qt Widgets Designer custom widgets](https://doc.qt.io/qt-6/designer-using-custom-widgets.html)：可借鉴 custom widget preview / plugin 边界，但 Atelier 首版不做 Designer plugin。
- [Qt Design Studio states](https://doc.qt.io/qtdesignstudio/quick-states.html)：可借鉴 state / transition / timeline 思路；当前技术方向仍是 PySide6 Widgets，不迁移 QML。
- [Widgetbook](https://docs.widgetbook.io/~1087/getting-started/components)：可借鉴 component catalog tree / use case 组织方式。

拒绝参考：

- `Moekotori/ECHO`：不纳入 Atelier 参考体系。

## Proposed Workbench Shape

建议未来入口：

```powershell
.venv\Scripts\python -m atelier.gui.ui.component_workbench
```

当前收敛后的窗口结构：

```text
Left catalog
  -> VideoInputCard 候选

Center preview stage
  -> selected story summary / states
  -> WorkCanvas preview
  -> card entry controls
  -> zoom / pan controls
  -> paint performance HUD
  -> fullscreen preview

Archived or hidden from current surface
  -> theme token preview
  -> generic WorkflowNodeItem placeholder
  -> right-side intake review checklist
  -> visible screenshot / review note panel
```

首版历史阶段已经完成并归档：

- Theme token swatches。
- Typography / radius / spacing preview。
- `WorkflowNodeItem` 候选 story placeholder。
- Widget intake checklist 可视化。

## Execution Plan

### Phase A: Workbench plan and reference boundary

目标：

- 写清控件画板必要性、参考模型和边界。

完成信号：

- 本计划存在并被 README / UI motion spec 索引。

验证：

```powershell
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'
git diff --check
```

状态：

- 已完成。

### Phase B: Dev-only launch entry

目标：

- 后续新增 `.venv\Scripts\python -m atelier.gui.ui.component_workbench`。

完成信号：

- 启动控件画板不会打开产品 `MainWindow`。
- 不读取 SQLite，不执行 workflow。
- 可显示 theme token swatches 和基础 typography samples。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 已完成第一阶段。

### Phase C: Candidate story registry

目标：

- 建立 PySide-independent story metadata，用于描述候选控件、状态和参数。

完成信号：

- story registry 可列出 component id、surface、states、parameters、review status。
- 未审查控件不能标记为 shared adopted。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 已完成第二阶段。

### Phase D: Screenshot / review notes

目标：

- 增加手动截图和审查备注路径。

完成信号：

- 能保存 dev-only screenshot。
- 截图记录不包含 secrets、用户路径或 worker logs。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 已完成第三阶段。

### Phase E: Static HTML review page

目标：

- 生成可由 Codex 浏览器打开和批注的静态 HTML review page。

完成信号：

- review snapshot 可生成 HTML 页面。
- 页面展示 screenshot、story、states、controls 和 reviewer note。
- 页面仍是 dev-only 审查报告，不是产品 UI 或 Web app。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 已完成第四阶段。

## Child Plans

- [plan_atelier_ui_component_workbench_foundation.md](./archive/component_workbench_phases/plan_atelier_ui_component_workbench_foundation.md)：已建立第一阶段 dev-only workbench、catalog/state、token preview、typography preview 和 intake checklist preview。
- [plan_atelier_ui_component_workbench_controls.md](./archive/component_workbench_phases/plan_atelier_ui_component_workbench_controls.md)：已建立第二阶段 catalog selection、story states / controls metadata 和 controls panel。
- [plan_atelier_ui_component_workbench_screenshot.md](./archive/component_workbench_phases/plan_atelier_ui_component_workbench_screenshot.md)：已建立第三阶段手动截图和 JSON 审查备注留痕。
- [plan_atelier_ui_component_workbench_review_page.md](./archive/component_workbench_phases/plan_atelier_ui_component_workbench_review_page.md)：规划静态 HTML review page 和 GitHub 收录边界。
- [plan_component_workbench_workcanvas_preview_area.md](./plan_component_workbench_workcanvas_preview_area.md)：建立 dev-only WorkCanvas 预览承载区，用于观察候选节点卡片在画布环境中的比例、边界和 preview artifact 策略。
- [plan_video_input_vector_collapsed_card.md](./plan_video_input_vector_collapsed_card.md)：搭建新的 `VideoInput` 内缩态矢量卡片。
- `WorkflowNodeItem` 通用候选已从当前画板工作区暂缓 / 归档，后续确实需要时再拆专门入库审查计划。

## Verification

当前验证命令：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'
git diff --check
```

当前验证事实：

- `Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'`：no matches。
- `git diff --check`：passed with only Windows CRLF conversion warnings。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：4 tests passed。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：14 tests passed。
- `.venv\Scripts\python -m unittest discover -s tests`：136 tests passed。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed。
- 文档空白扫描：no matches。
- `git diff --check`：passed with only Windows CRLF conversion warnings。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：5 tests passed after controls phase。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：15 tests passed after controls phase。
- `.venv\Scripts\python -m unittest discover -s tests`：137 tests passed after controls phase。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：8 tests passed after review snapshot phase。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：18 tests passed after review snapshot phase。
- `.venv\Scripts\python -m unittest discover -s tests`：140 tests passed after review snapshot phase。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：9 tests passed after static HTML review page phase。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：19 tests passed after static HTML review page phase。
- `.venv\Scripts\python -m unittest discover -s tests`：141 tests passed after static HTML review page phase。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed after static HTML review page phase。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：16 tests passed after focused WorkCanvas tuning surface phase。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：26 tests passed after focused WorkCanvas tuning surface phase。
- `.venv\Scripts\python -m unittest discover -s tests`：148 tests passed after focused WorkCanvas tuning surface phase。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed after focused WorkCanvas tuning surface phase。
- 文档空白扫描：no matches after focused WorkCanvas tuning surface phase。
- `git diff --check`：passed with only Windows CRLF conversion warnings after focused WorkCanvas tuning surface phase。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：18 tests passed after WorkCanvas controls / grid LOD fix。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：28 tests passed after WorkCanvas controls / grid LOD fix。
- `.venv\Scripts\python -m unittest discover -s tests`：150 tests passed after WorkCanvas controls / grid LOD fix。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed after WorkCanvas controls / grid LOD fix。
- 文档空白扫描：no matches after WorkCanvas controls / grid LOD fix。
- `git diff --check`：passed with only Windows CRLF conversion warnings after WorkCanvas controls / grid LOD fix。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：19 tests passed after cached grid tile fix。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：29 tests passed after cached grid tile fix。
- `.venv\Scripts\python -m unittest discover -s tests`：151 tests passed after cached grid tile fix。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed after cached grid tile fix。
- 文档空白扫描：no matches after cached grid tile fix。
- `git diff --check`：passed with only Windows CRLF conversion warnings after cached grid tile fix。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：21 tests passed after paint performance instrumentation。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：31 tests passed after paint performance instrumentation。
- `.venv\Scripts\python -m unittest discover -s tests`：153 tests passed after paint performance instrumentation。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed after paint performance instrumentation。
- 文档空白扫描：no matches after paint performance instrumentation。
- `git diff --check`：passed with only Windows CRLF conversion warnings after paint performance instrumentation。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：23 tests passed after visible performance HUD / centered launch phase。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：33 tests passed after visible performance HUD / centered launch phase。
- `.venv\Scripts\python -m unittest discover -s tests`：155 tests passed after visible performance HUD / centered launch phase。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed after visible performance HUD / centered launch phase。
- 文档空白扫描：no matches after visible performance HUD / centered launch phase。
- `git diff --check`：passed with only Windows CRLF conversion warnings after visible performance HUD / centered launch phase。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：24 tests passed after fullscreen overlay / HUD stability fix。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：34 tests passed after fullscreen overlay / HUD stability fix。
- `.venv\Scripts\python -m unittest discover -s tests`：156 tests passed after fullscreen overlay / HUD stability fix。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed after fullscreen overlay / HUD stability fix。
- 文档空白扫描：no matches after fullscreen overlay / HUD stability fix。
- `git diff --check`：passed with only Windows CRLF conversion warnings after fullscreen overlay / HUD stability fix。

## Progress / Decisions

- 2026-05-07：创建本计划。决策：AtelierUI 需要独立控件画板；候选自绘控件不应放在真实产品 GUI 中调参。
- 2026-05-07：决策：首版借鉴 Storybook / Widgetbook 的 catalog + controls + stories 模型，借鉴 Qt Designer / Qt Design Studio 的 custom widget / state 思路，但保持 PySide6 Widgets 技术方向。
- 2026-05-07：执行 `plan_atelier_ui_component_workbench_foundation.md` 第一阶段。新增 dev-only `atelier.gui.ui.component_workbench` 入口，可展示 token swatches、typography samples、intake checklist 和 `WorkflowNodeItem` 候选 placeholder；真实参数 controls、screenshot 和自绘控件入库仍未实现。
- 2026-05-07：执行 `plan_atelier_ui_component_workbench_controls.md` 第二阶段。左侧 catalog 可切换 story，中央 preview 和右侧 controls panel 可展示当前 story 的 states / controls 元数据；仍未实现真实控件绘制、参数驱动或截图保存。
- 2026-05-07：执行 `plan_atelier_ui_component_workbench_screenshot.md` 第三阶段。画板可保存当前窗口 PNG 和 JSON 审查备注记录；仍不代表候选控件已通过用户审查或可共享入库。
- 2026-05-07：新增 `plan_atelier_ui_component_workbench_review_page.md`。决策：画板源码、测试、开发脚本和文档进入 GitHub；生成的 PNG / JSON / HTML 审查产物留在 `.atelier/`，不进入 GitHub。
- 2026-05-07：执行 `plan_atelier_ui_component_workbench_review_page.md` Phase B-D。保存 review snapshot 时同步生成静态 HTML 审查页，并在画板内显示最近一次 HTML 文件名，方便 Codex 浏览器打开批注。
- 2026-05-07：完成 `plan_atelier_ui_component_workbench_review_page.md` Phase E。当前画板 review snapshot 输出 PNG / JSON / HTML 三件套，JSON 和 HTML 都只记录相邻文件名，不记录本机绝对路径。
- 2026-05-08：执行 `plan_component_workbench_workcanvas_preview_area.md` 第一阶段。画板新增 dev-only WorkCanvas 预览承载区，当前承载 `VideoInputCardCandidate`，并明确缩略图只来自 cached preview artifact，不由 GUI 生成。
- 2026-05-08：执行 `plan_video_input_vector_collapsed_card.md` 第一阶段。新增 `VideoInputCollapsedNodeCardItem`，以 `QGraphicsObject` / `paint()` 绘制内缩态，并在 WorkCanvas 预览区展示。
- 2026-05-08：执行 `plan_video_input_vector_collapsed_card.md` Phase F。当前画板聚焦 `VideoInputCard 候选` 和 WorkCanvas 预览；主题 token、`WorkflowNodeItem 候选`、右侧入库审查清单从可见工作区隐藏 / 归档；新增卡片入口切换和全屏预览。
- 2026-05-08：执行 `plan_video_input_vector_collapsed_card.md` Phase G。WorkCanvas 预览从外层滚动区收敛为真实 canvas viewport；非全屏控件保持可见；网格使用 viewport-space LOD 绘制，降低 zoom-out 卡顿风险。
- 2026-05-08：执行 `plan_video_input_vector_collapsed_card.md` Phase H。WorkCanvas 小网格改为 cached tile / brush 平铺，避免每帧全可视区逐条绘制小网格。
- 2026-05-08：执行 `plan_video_input_vector_collapsed_card.md` Phase I。新增 WorkCanvas 背景和 `VideoInputCollapsedNodeCardItem.paint()` 的 dev-only 性能快照，支持 viewport update mode 切换，背景网格 AA 关闭而节点绘制 AA 保留。
- 2026-05-09：执行 `plan_video_input_vector_collapsed_card.md` Phase J。WorkCanvas 预览增加可见性能 HUD；控件画板窗口默认 1980×1080，并在每次显示时重新居中。
- 2026-05-09：执行 `plan_video_input_vector_collapsed_card.md` Phase K。全屏 WorkCanvas 增加 overlay controls / HUD，并稳定 HUD live-refresh 尺寸。

## Blockers

- 暂无。
