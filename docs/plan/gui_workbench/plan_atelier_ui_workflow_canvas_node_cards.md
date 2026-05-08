# AtelierUI Workflow Canvas Node Cards 计划

> 本计划只推进 `AtelierUI` 画板里的 Workflow Canvas 节点卡片候选目录和第一张 `VideoInputCard` 候选卡片。候选卡片用于用户审查，不代表已批准共享入库或可被真实产品 GUI 调用。

## Objective

在 `AtelierUI Component Workbench` 中建立 Workflow Canvas 节点卡片候选区，让所有 Workflow Canvas 节点卡片按同一父目录和同一审查流程沉淀。

目标目录：

```text
atelier/gui/ui/workflow_canvas/
  node_cards/
    video_input_card.py
```

首个候选：

```text
VideoInputCard 候选
  -> 只展示视频输入节点卡片的静态视觉稿
  -> 只表达 GUI intent 边界
  -> 不读取真实媒体
  -> 不运行 FFmpeg / Worker / Scheduler
```

## Scope

- 新增 Workflow Canvas 节点卡片候选目录。
- 新增 `VideoInputCard` 候选 story。
- 在控件画板 catalog 中展示 `VideoInputCard 候选`。
- 在控件画板中央 preview 中渲染视频输入卡片候选。
- 保持保存 PNG / JSON / HTML review snapshot 的能力。

暂不实现：

- 文件选择。
- 真实视频读取、缩略图抽取或 metadata probe。
- WorkflowGraph 节点创建。
- 产品 Workflow Canvas 调用。
- shared `AtelierUI` 组件入库批准。
- 参数面板真实驱动绘制。

## Current Facts

- 当前 `AtelierUI Component Workbench` 已存在 dev-only PySide6 启动入口。
- 当前画板已支持聚焦的 `VideoInputCard 候选` catalog、story states / controls metadata、WorkCanvas 预览、卡片入口切换、基础 zoom / pan、全屏预览，以及隐藏的 PNG / JSON / HTML review snapshot 能力。
- 当前 `atelier/gui/workflow_canvas.py` 是产品 GUI 的 Workflow Canvas foundation，不是已审查的共享 `AtelierUI` 节点卡片库。
- 当前 `atelier/gui/ui/` 是 Atelier 专属 UI 基础库路径，但还没有 Workflow Canvas 节点卡片子目录。

## Constraints

- 新节点卡片必须先进入画板审查，不能直接接入产品 `MainWindow` 或真实 Workflow Canvas。
- 候选卡片不得运行 Worker、FFmpeg、模型推理、硬件调度、任意 shell 或 SQLite mutation。
- 候选卡片不得读取用户真实媒体路径。
- 可见 UI 文案使用中文；代码标识、objectName、story id、port id 保持英文。
- 候选卡片未获用户审查前不得标记为 `shared_adoption_approved=True`。

## Execution Plan

### Phase A: Node card candidate directory and story contract

目标：

- 建立 Workflow Canvas 节点卡片候选目录。
- 在 workbench state 中登记 `VideoInputCard 候选` story。

完成信号：

- catalog 可列出 `VideoInputCard 候选`。
- story surface 显示为 `Workflow Canvas / Node Cards`。
- story controls 包含 `selected`、`hovered`、`media_status`、`thumbnail`。
- story 保持未批准共享入库。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 已完成。

### Phase B: Dev-only card preview

目标：

- 在控件画板中渲染第一版 `VideoInputCard` 展开态候选卡片。

完成信号：

- 选择 `VideoInputCard 候选` 后，中央 preview 显示视频输入卡片。
- 卡片固定 400 px × 600 px，圆角 16 px，边框 3 px，并带向外发散的高亮效果。
- 顶部介绍区高度 50 px。
- 顶部信息框不显示边框，内部为图标在左、文字在右，整体相对介绍区左侧垂直居中；图标尺寸由标题字体高度乘以 `ICON_TO_TITLE_FONT_HEIGHT_RATIO` 得出。
- 图标倍率由 `atelier/gui/ui/workflow_canvas/node_cards/video_input_card.py` 顶部常量 `ICON_TO_TITLE_FONT_HEIGHT_RATIO` 控制。
- 顶部信息框只显示 `视频输入`，不显示 `输入视频源` 副标题。
- 状态胶囊固定 80 px × 30 px，圆角 15 px，文本居中，默认绿色 `正常`；后续可扩展红色路径失效、灰色无输入。
- 视频流区按垂直顺序排列，水平居中，间隔 5 px。
- 视频卡片固定 380 px × 75 px，圆角 12 px，不显示 AI 图中误生成的“视频”标签。
- 输入路径框与顶部信息框左边对齐。
- 输入路径行固定 380 px × 40 px，左右距卡片边缘 10 px。
- 浏览按钮固定 100 px × 40 px，与输入路径框间隔 5 px，右边与状态胶囊右侧圆切点对齐。
- 输入框宽度按 `400 - 100 - 10 - 10 - 5 = 275 px` 固定。
- 产品 `MainWindow` 不调用该卡片。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 已完成。

### Phase C: Docs and verification

目标：

- 更新 `APP_CODE_MAP.md`、`RECENT_CHANGES.md`、README 或相关 plan。
- 运行目标测试、GUI 组合测试、全量 unittest、compileall、文档空白扫描和 `git diff --check`。

完成信号：

- 接手文档准确记录节点卡片候选目录和未批准共享边界。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'
git diff --check
```

状态：

- 已完成。

## Child Plans

- 后续可拆 `plan_atelier_ui_workflow_node_item_intake.md`，用于正式 `WorkflowNodeItem` 节点卡片抽象。
- 后续可拆 `plan_atelier_ui_workflow_canvas_node_card_visual_states.md`，用于 hover / selected / warning / failed 等状态审查。

## Verification

当前验证事实：

- Red first：`.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench` 先因 `video-input-card` story 和 preview 缺失而失败。
- Green after implementation：`.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench` 已通过，10 tests passed。
- Expanded-state red first：`.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench` 先因卡片高度仍为 300 px 而失败。
- Expanded-state green：`.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench` 已通过，10 tests passed。
- Geometry-adjustment red first：`.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench` 先因外边框仍为 4 px 而失败。
- GUI group：`.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke` 已通过，20 tests passed。
- Full unittest：`.venv\Scripts\python -m unittest discover -s tests` 已通过，142 tests passed。
- `compileall`：`.venv\Scripts\python -m compileall -q atelier tests` 已通过。

## Progress / Decisions

- 2026-05-07：创建本计划。决策：Workflow Canvas 相关节点卡片统一沉淀在 `atelier/gui/ui/workflow_canvas/node_cards/`，候选卡片先进入画板审查，不进入产品 GUI 调用。
- 2026-05-07：完成 Phase A-B。新增 `VideoInputCard 候选` story 和 dev-only 静态卡片预览；仍不读取真实媒体、不创建 WorkflowGraph 节点、不进入产品 GUI。
- 2026-05-07：按审查反馈调整 `VideoInputCardCandidate`。卡片固定为 400 px × 300 px，圆角 16 px，边框 4 px，内部 3 × 3 九宫格不显示分割线，所有内容按各自格子中心对齐。
- 2026-05-07：按展开态审查反馈重绘 `VideoInputCardCandidate`。卡片改为 400 px × 600 px，使用 Header / Stream 语义分区、状态胶囊、视频卡片和输入路径行，不再使用整体九宫格作为最终排布。
- 2026-05-07：按审查反馈微调展开态几何。外边框改为 3 px，Header 改为 40 px，状态胶囊改为 80 px × 30 px / 15 px 圆角，去掉 `输入视频源` 副标题，输入行改为 40 px 高，浏览按钮改为 100 px，输入框固定为 275 px。
- 2026-05-07：按审查反馈再次微调 Header。Header 改回 50 px；`视频输入` 标题取消粗体并与状态文字同 weight；左上角图标尺寸由 `ICON_TO_TITLE_FONT_HEIGHT_RATIO` 控制。
- 2026-05-07：完成 Phase C。README、APP_CODE_MAP、RECENT_CHANGES 和 AtelierUI README 已记录节点卡片候选目录与未批准共享边界。

## Blockers

- 暂无。
