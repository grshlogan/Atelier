# Video Input Vector Collapsed Card Plan

## Objective

为真实 WorkCanvas 路线搭建新的 `VideoInput` 节点卡片雏形：先实现内缩态，并把它放进控件画板的 WorkCanvas 预览区中审查。

本计划服务“矢量 / QGraphicsItem 路线”，不是继续扩展旧的 QWidget 版 `VideoInputCardCandidate`。

## Scope

- 新增内缩态的 `VideoInput` WorkCanvas 节点卡片 item。
- 使用 `QGraphicsObject` / `paint()` 绘制，作为未来真实 WorkCanvas 的迁移方向。
- 在控件画板 WorkCanvas 预览区里展示该 item。
- 保留旧 QWidget 候选卡片作为历史视觉参考，暂不删除。

暂不实现：

- 真实缩略图读取或生成。
- preview artifact / thumbnail cache 读模型。
- 展开态矢量 item。
- 拖拽、端口连线、hover、selected 动画。
- 产品 `atelier/gui/workflow_canvas.py` 调用。

## Current Facts

- 当前控件画板已有 `component-workbench-workcanvas-preview`，用于 dev-only WorkCanvas 预览。
- 当前旧 `VideoInputCardCandidate` 是 QWidget 组合候选，适合视觉打磨，不适合作为真实 WorkCanvas 大量节点的最终路线。
- `docs/WORKCANVAS_PREVIEW_ARTIFACT_SPEC.md` 已规定：缩略图来自 cached preview artifact，GUI 不在 paint 路径中生成。

## Constraints

- 新 item 不得读取媒体、生成缩略图、执行 workflow、调用 FFmpeg、调用 worker 或访问 SQLite。
- 新 item 的 `paint()` 只绘制已有 view model，不做 IO、不解码、不构建 `QPixmap`。
- 内缩态允许绘制轻量矢量 fallback 缩略图堆叠；未来接入真实缩略图时必须来自 preview artifact / thumbnail cache。
- 可见 UI 文案用中文；代码标识、objectName、data role 保持英文。
- 候选 item 未经用户审查前不得标记为共享入库或产品可调用。

## Execution Plan

### Phase A - Red test

目标：
- 新增失败测试，要求存在内缩态矢量 item，并能在控件画板 WorkCanvas 预览区中被找到。

完成信号：
- 测试先因缺少 `video_input_vector_card` 或缺少 preview item 失败。

验证：
```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_workcanvas_preview_hosts_thumbnail_free_vector_collapsed_video_input_card
```

### Phase B - Minimal vector item

目标：
- 新增 `VideoInputCollapsedNodeCardItem`，固定 300 px × 200 px。
- 绘制卡片背景、边框、Header、图标、标题、状态胶囊、视频数和三项摘要指标。
- 不读取真实媒体，不生成真实缩略图；缩略图视觉只能来自已有 view model、cached preview 或轻量矢量 fallback。

完成信号：
- item 暴露稳定 data/property，`boundingRect()` 返回固定尺寸。
- 能被 `QGraphicsScene` 渲染到 `QImage`。

验证：
```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

### Phase C - Workbench integration

目标：
- 在 WorkCanvas 预览区增加矢量 item 预览视图。

完成信号：
- 选择 `VideoInputCard 候选` 时，画板中可见新的内缩态矢量卡片。
- 预览视图声明 `thumbnail_strategy = cached-preview-or-vector-fallback` 和 `item_route = qgraphicsitem-paint`。

### Phase D - Docs and validation

目标：
- 更新 code map、recent changes 和相关 plan。
- 运行目标测试、组合测试、compileall、文档空白扫描和 `git diff --check`。

### Phase E - Basic WorkCanvas preview zoom

目标：
- 给控件画板中的矢量 WorkCanvas 预览增加最基础缩放和平移能力。

完成信号：
- 有 `+`、`-`、`100%` 控件和当前缩放值显示。
- 缩放改变 `QGraphicsView` transform，不改变 `VideoInputCollapsedNodeCardItem.boundingRect()`。
- 首版缩放范围为 50% 到 200%。
- 鼠标左键拖动可平移预览画布。

### Phase F - Workbench cleanup and fullscreen

目标：
- 让画板更专注 WorkCanvas 卡片打磨。

完成信号：
- `WorkflowNodeItem 候选` 和 `主题 Tokens` 不再出现在 catalog 或 WorkCanvas 上方。
- 右侧入库审查清单不再显示。
- WorkCanvas 预览区提供全屏入口。
- 旧 QWidget 参考卡片和新矢量卡片不再默认堆叠，通过卡片入口切换显示。

### Phase G - Non-fullscreen controls and grid LOD

目标：
- 修复非全屏模式下 WorkCanvas 控件不容易看见的问题。
- 优化缩小画布时的网格绘制，避免 scene-space 网格在 zoom-out 时绘制量反向变大。

完成信号：
- WorkCanvas 预览不依赖外层 `QScrollArea` 查找控件；非全屏窗口中卡片入口、缩放、全屏控件保持可见。
- 网格背景改为 viewport / screen-space 绘制，并根据屏幕像素间距做 LOD：缩小时减少小格线和点阵。
- `QGraphicsScene` 生命周期稳定，非全屏和全屏 `QGraphicsView.scene()` 不会被 Python GC 清掉。

### Phase H - Cached grid tile

目标：
- 避免小网格在每次 paint 时按整个 viewport 逐条线 / 逐点绘制。

完成信号：
- WorkCanvas 网格背景使用 cached tile / brush 平铺策略。
- 同一 zoom LOD 重复绘制复用同一张网格 tile。
- 小网格只在 tile 内绘制一次，不在每帧按全可视区生成大批 primitives。

### Phase I - Paint performance instrumentation

目标：
- 为 WorkCanvas 背景和 `VideoInputCollapsedNodeCardItem.paint()` 增加可开关的性能观测入口。

完成信号：
- `_WorkCanvasView` 支持 `debug_perf` 开关和 `debug_perf_snapshot()`。
- 背景统计包含 `drawBackground` 耗时、tile cache 命中 / 未命中、tile key、当前 zoom、背景 AA 状态。
- `_WorkCanvasView` 可切换 viewport update mode：`minimal` / `bounding` / `full`。
- 背景网格绘制显式关闭 AA，节点绘制保留 AA。
- `VideoInputCollapsedNodeCardItem.paint()` 支持独立 `debug_perf` 和耗时快照。

### Phase J - Visible performance HUD and launch geometry

目标：
- 把 Phase I 的性能快照做成 dev-only 可见 HUD。
- 控件画板每次打开默认 1980 px × 1080 px，并按当前屏幕重新居中。

完成信号：
- WorkCanvas 预览区有可见 HUD，展示 zoom、背景耗时、tile cache、tile key、update mode、背景 / 节点 AA 和节点 paint 耗时。
- HUD 读取现有 `debug_perf_snapshot()`，不引入新的 worker、FFmpeg、缩略图生成或后端逻辑。
- `ComponentWorkbenchWindow` 不保存关闭位置；每次显示时重新按屏幕 available geometry 居中。

### Phase K - Fullscreen overlay visibility and HUD stability

目标：
- 修复全屏模式看不到普通模式 WorkCanvas 控件的问题。
- 修复全屏 HUD 随实时性能文字变化而发生视觉抖动的问题。

完成信号：
- 全屏模式显示 zoom 控件和性能 HUD。
- 全屏 HUD live refresh 不改变 HUD size。

### Phase L - Border-independent content layout

目标：
- 将 `VideoInputCollapsedNodeCardItem` 的边框绘制坐标和内容定位坐标分离。

完成信号：
- 调整 `CARD_BORDER_WIDTH` 只影响边框绘制，不改变图标、标题、状态胶囊、主指标和分割线坐标。

## Child Plans

### Phase M - Selected/resting style, summary icons, and expand affordance

目标：
- 将当前矢量卡片明确为选中态：粗蓝边、轻微辉光；补充非选中态：细暗边、无辉光。
- 优化卡片背景为克制的深色渐变，参考 `dark-tech-sharp.DESIGN.md` 的边框式层级，不照搬纯黑网页风格。
- 将底部 `总时长`、`总大小`、`待处理` 恢复为“图标 + 标题”一行、数值下一行。
- 在矢量卡片内绘制一个带垂直渐变、轻阴影和箭头图例的展开/收缩 affordance。

完成信号：
- `VideoInputCollapsedNodeCardItem` 暴露 appearance / summary layout / expand affordance 快照，测试可验证选中态和非选中态视觉 token。
- `paint()` 仍然只绘制已有 view model，不做 IO、不生成缩略图、不执行 workflow。

### Phase N - Collapsed thumbnail stack proximity reveal

目标：
- 内缩态恢复缩略图堆叠，避免右侧视觉过空，但不在 GUI 中读取或生成真实缩略图。
- 将展开 affordance 从底部摘要区迁移到缩略图堆叠上，保持 `总时长 / 总大小 / 待处理` 的统一信息节奏。
- 鼠标进入缩略图堆叠外扩 40 px 热区时，以短动画让缩略图降透明、四角展开线条淡入；鼠标离开 64 px 外扩区后淡回缩略图，避免边界抖动。

完成信号：
- `VideoInputCollapsedNodeCardItem` 暴露 thumbnail stack / proximity reveal 快照，测试可验证 thumbnail count、热区阈值、hysteresis 和 opacity 状态。
- `summary_metric_layout_snapshot()` 显示底部指标不再为右下角展开 affordance 让位。
- WorkCanvas 预览继续声明不生成缩略图、不执行 workflow、不访问后端。

### Phase O - Line-only thumbnail expand affordance

目标：
- 删除缩略图区展开 affordance 的按钮外框、按钮背景和伴随阴影。
- 只绘制四角展开线条，使用圆角线帽，降低缩略图上的突兀感。
- 保持 Phase N 的 40 px enter / 64 px exit proximity reveal 和缩略图降透明逻辑。

完成信号：
- `expand_affordance_snapshot()` 暴露 `visual_treatment = line-only`、`line_style = four-corner-expand`、`background_treatment = none` 和 `shadow = none`。
- `paint()` 中展开 affordance 只绘制线条，不绘制圆角按钮面、不绘制阴影。
- 现有 WorkCanvas preview、hover proximity、底部摘要布局测试继续通过。

- 后续可拆 `plan_video_input_vector_expanded_card.md`，推进展开态矢量 item。
- 后续可拆 `plan_workcanvas_thumbnail_cache_boundary.md`，接入真实 cached preview artifact。

## Verification

- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`
- `.venv\Scripts\python -m unittest discover -s tests`
- `.venv\Scripts\python -m compileall -q atelier tests`
- `Select-String -Path .\README.md, .\AGENTS.md, .\DESIGN.md, .\docs\*.md, .\docs\plan\*.md, .\docs\plan\gui_workbench\*.md -Pattern '[ \t]+$'`
- `git diff --check`

当前验证事实：

- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_workcanvas_preview_hosts_thumbnail_free_vector_collapsed_video_input_card`：red first，失败原因为缺少 `atelier.gui.ui.workflow_canvas.node_cards.video_input_vector_card`。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_workcanvas_preview_hosts_thumbnail_free_vector_collapsed_video_input_card`：passed after implementation。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_workcanvas_vector_preview_supports_basic_zoom_controls`：red first，失败原因为缺少 `component-workbench-workcanvas-zoom-label`；追加平移断言后，失败原因为缺少 `pan_interaction`。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_workcanvas_vector_preview_supports_basic_zoom_controls`：passed after implementation。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：16 tests passed。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：26 tests passed。
- `.venv\Scripts\python -m unittest discover -s tests`：148 tests passed。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed。
- 文档空白扫描：no matches。
- `git diff --check`：passed with only Windows CRLF conversion warnings。
- Phase F red first：新增 catalog 清理、入口切换和全屏断言后，测试先失败在 catalog 仍暴露旧入口、右侧审查 UI 仍存在、卡片入口 / fullscreen 控件缺失。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：16 tests passed after Phase F implementation。
- 文档空白扫描 after Phase F：no matches。
- `git diff --check` after Phase F：passed with only Windows CRLF conversion warnings。
- Phase G red first：新增非全屏控件可见性、viewport LOD 和 scene 生命周期断言后，测试先失败在 `view.scene()` 为 `None`、网格未暴露 viewport LOD 属性。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：18 tests passed after Phase G implementation。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：28 tests passed after Phase G implementation。
- `.venv\Scripts\python -m unittest discover -s tests`：150 tests passed after Phase G implementation。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed after Phase G implementation。
- 文档空白扫描 after Phase G：no matches。
- `git diff --check` after Phase G：passed with only Windows CRLF conversion warnings。
- Phase H red first：新增 cached tile / brush 断言后，测试先失败在 `grid_paint_strategy` 未设置。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：19 tests passed after Phase H implementation。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：29 tests passed after Phase H implementation。
- `.venv\Scripts\python -m unittest discover -s tests`：151 tests passed after Phase H implementation。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed after Phase H implementation。
- 文档空白扫描 after Phase H：no matches。
- `git diff --check` after Phase H：passed with only Windows CRLF conversion warnings。
- Phase I red first：新增 WorkCanvas debug perf / viewport update mode / node paint perf 断言后，测试先失败在 `_WorkCanvasView.set_debug_perf()` 和 `VideoInputCollapsedNodeCardItem.set_debug_perf()` 缺失。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：21 tests passed after Phase I implementation。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：31 tests passed after Phase I implementation。
- `.venv\Scripts\python -m unittest discover -s tests`：153 tests passed after Phase I implementation。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed after Phase I implementation。
- 文档空白扫描 after Phase I：no matches。
- `git diff --check` after Phase I：passed with only Windows CRLF conversion warnings。
- Phase J red first：新增 WorkCanvas 性能 HUD 和启动几何断言后，测试先失败在缺少 `COMPONENT_WORKBENCH_DEFAULT_WIDTH` 与 `component-workbench-workcanvas-perf-hud`。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：23 tests passed after Phase J implementation。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：33 tests passed after Phase J implementation。
- `.venv\Scripts\python -m unittest discover -s tests`：155 tests passed after Phase J implementation。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed after Phase J implementation。
- 文档空白扫描 after Phase J：no matches。
- `git diff --check` after Phase J：passed with only Windows CRLF conversion warnings。
- Phase K red first：全屏 overlay 断言先失败在缺少 `component-workbench-workcanvas-fullscreen-toolbar`；HUD 稳定性断言先失败在 live refresh 后 HUD size 从 750×30 变成 771×30。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：24 tests passed after Phase K implementation。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：34 tests passed after Phase K implementation。
- `.venv\Scripts\python -m unittest discover -s tests`：156 tests passed after Phase K implementation。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed after Phase K implementation。
- 文档空白扫描 after Phase K：no matches。
- `git diff --check` after Phase K：passed with only Windows CRLF conversion warnings。
- Phase L red first：新增边框宽度不影响内容布局断言后，测试先失败在 `VideoInputCollapsedNodeCardItem.content_layout_snapshot()` 缺失。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：27 tests passed after Phase L implementation。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：37 tests passed after Phase L implementation。
- `.venv\Scripts\python -m unittest discover -s tests`：159 tests passed after Phase L implementation。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed after Phase L implementation。
- Phase M red first：新增选中/非选中外观、底部图标标题行、展开 affordance 快照断言后，测试先失败在缺少 `selected` view-model 字段、`summary_metric_layout_snapshot()` 和 `expand_affordance_snapshot()`。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_video_input_collapsed_appearance_separates_selected_and_resting_state tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_video_input_collapsed_summary_metrics_use_icon_title_rows tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_video_input_collapsed_expand_affordance_is_line_only_corners`：3 tests passed after Phase M implementation。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：32 tests passed after Phase M implementation。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：42 tests passed after Phase M implementation。
- `.venv\Scripts\python -m unittest discover -s tests`：164 tests passed after Phase M implementation。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed after Phase M implementation。
- 文档空白扫描 after Phase M：no matches。
- `git diff --check` after Phase M：passed with only Windows CRLF conversion warnings。
- Phase N red first：新增缩略图堆叠、40/64 px proximity reveal 和缩略图区展开 affordance 断言后，测试先失败在 `thumbnail_strategy = none`、缺少 `thumbnail_stack_snapshot()`，以及展开按钮仍位于 `(240, 150)` 底部区域。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_workcanvas_preview_hosts_thumbnail_stack_vector_collapsed_video_input_card tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_video_input_collapsed_thumbnail_stack_reveals_expand_on_pointer_proximity tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_video_input_collapsed_expand_affordance_is_line_only_corners`：3 tests passed after Phase N implementation。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：34 tests passed after Phase N implementation。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：44 tests passed after Phase N implementation。
- `.venv\Scripts\python -m unittest discover -s tests`：166 tests passed after Phase N implementation。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed after Phase N implementation。
- 文档空白扫描 after Phase N：no matches。
- `git diff --check` after Phase N：passed with only Windows CRLF conversion warnings。
- Phase O red first：将展开 affordance 测试改为 line-only 后，测试先失败在 `expand_affordance_snapshot()` 缺少 `visual_treatment`。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_video_input_collapsed_expand_affordance_is_line_only_corners tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_video_input_collapsed_thumbnail_stack_reveals_expand_on_pointer_proximity`：2 tests passed after Phase O implementation。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench`：34 tests passed after Phase O implementation。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：44 tests passed after Phase O implementation。
- `.venv\Scripts\python -m unittest discover -s tests`：166 tests passed after Phase O implementation。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed after Phase O implementation。
- 文档空白扫描 after Phase O：no matches。
- `git diff --check` after Phase O：passed with only Windows CRLF conversion warnings。

## Progress / Decisions

- 2026-05-08：创建本计划。决策：先做内缩态，使用 `QGraphicsObject` / `paint()` 路线，旧 QWidget 卡片只保留为视觉参考。
- 2026-05-08：完成 Phase A-C。新增 `VideoInputCollapsedNodeCardItem` 和 `component-workbench-video-input-vector-preview`，当前只绘制矢量信息，不读取或生成真实缩略图。
- 2026-05-08：完成 Phase E 首版。矢量预览支持 `+`、`-`、`100%` 缩放控件和鼠标拖动画布平移；缩放作用于 `QGraphicsView` transform，不改变 item 固定尺寸。
- 2026-05-08：完成 Phase D。文档、code map、recent changes 和验证事实已对齐。
- 2026-05-08：完成 Phase F 实现。当前画板聚焦 `VideoInputCard 候选` 和 WorkCanvas 预览；`WorkflowNodeItem 候选`、主题 token 预览、右侧入库审查清单从可见工作区移除；旧 QWidget 展开参考和新矢量内缩卡片通过入口切换显示，并新增全屏预览。
- 2026-05-08：完成 Phase G 实现。非全屏 WorkCanvas 预览不再依赖外层滚动区查找控件；`QGraphicsScene` 生命周期稳定；网格改为 viewport / screen-space 绘制，并在 zoom-out 时跳过 minor grid 和点阵。
- 2026-05-08：完成 Phase H 实现。小网格改为 cached tile / brush 平铺，重复 zoom LOD 复用同一张 tile，不再每帧按全可视区生成小格线和点阵 primitives。
- 2026-05-08：完成 Phase I 实现。`_WorkCanvasView` 增加 `debug_perf`、背景耗时 / tile cache / zoom / update mode 快照，viewport update mode 可在 `minimal`、`bounding`、`full` 间切换；`VideoInputCollapsedNodeCardItem.paint()` 增加独立耗时统计，背景 AA 关闭、节点 AA 保留。
- 2026-05-09：完成 Phase J 实现。WorkCanvas 预览显示 dev-only 性能 HUD，读取背景与节点 paint 快照；控件画板窗口默认 1980×1080，并在每次显示时按当前屏幕重新居中。
- 2026-05-09：完成 Phase K 实现。全屏模式补充 zoom / HUD overlay，并固定 HUD live-refresh 尺寸，避免鼠标移动触发 repaint 时性能文本改变导致 HUD 抖动。
- 2026-05-09：完成 Phase L 实现。`VideoInputCollapsedNodeCardItem` 边框几何和内容几何分离，边框宽度变化不再移动内容坐标。
- 2026-05-09：完成 Phase M 实现。当前矢量卡片明确为选中态：粗蓝边和轻微辉光；新增非选中态细暗边 token；背景改为克制深色渐变；底部三指标改为图标+标题行、数值下一行；新增绘制型渐变展开 affordance。
- 2026-05-09：完成 Phase N 首版实现。矢量内缩卡片恢复 3 张缩略图 fallback 堆叠；展开 affordance 从底部摘要区迁移到缩略图区，鼠标进入 40 px 热区时缩略图降透明并淡入展开 affordance，离开 64 px 扩展区后淡回缩略图；底部摘要指标不再为展开 affordance 让位。
- 2026-05-09：完成 Phase O 实现。缩略图区展开 affordance 删除按钮外框、背景和阴影，改为只绘制四角展开线条；proximity reveal 逻辑保持不变。

## Blockers

- 暂无。
