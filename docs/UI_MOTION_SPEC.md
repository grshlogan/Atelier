# Atelier UI Motion Spec

> 状态：规划中，尚未实现。本文档定义 Atelier 专属 `AtelierUI` 动效系统、motion token、动画驱动、覆盖层、自绘控件和开源参考边界。
> 事实源关系：根目录 `DESIGN.md` 仍是产品视觉与交互事实源；本文档服从 `DESIGN.md`，并补充 `docs/Atelier_Main_UI_Spec.md` 与 `docs/UI_WORKSPACE_SPEC.md` 中的动效实现边界。
> 工程边界：本文档不引入成熟 UI 库，不声明任何第三方项目已被 vendored、forked 或作为运行时依赖。
> 本地库边界：Atelier 必须保留本软件专属的 `AtelierUI` 本地库方向，用于自绘控件、动画效果和共享 GUI 视觉基础；该库只随 Atelier Runtime 或核心代码打包，不作为成熟通用库发布。

## 1. 目标

Atelier 的动效目标不是炫技，而是让 workflow、hardware execution、queue recovery 三个核心模型更容易理解。

```text
Make workflow state changes visible.
Make hardware execution transitions legible.
Make failure and recovery paths easier to locate.
```

动效应该回答：

- 哪个 workflow node 被加入、选中、拖动、连接或移除。
- 哪个 execution phase 被生成、排队、开始、阻塞、完成或失败。
- 哪个 queue row 正在变化，以及变化来自 worker event、cache hit、retry 还是 recovery action。
- 哪个 panel、overlay、inspector 或 page 与当前用户上下文相关。

动效不应该：

- 装饰性循环发光。
- 模糊任务真实进度。
- 用动画隐藏失败原因。
- 每个控件自己发明时长、曲线、状态和中断策略。
- 把 Atelier 迁移到 QML、Rive、Dear ImGui、raygui 或任何非 PySide6 Widgets 技术栈。

## 2. 当前事实

- `DESIGN.md` 已定义动效原则：短、可打断、解释状态变化，不影响按钮、日志、状态灯和进度可信度。
- `docs/Atelier_Main_UI_Spec.md` 已给出首版时长：card hover `120ms`、card select `140ms`、snap `180ms`、panel expand/collapse `180ms`、progress update `160ms`、error pulse `220ms`。
- `docs/UI_WORKSPACE_SPEC.md` 已定义 `QMainWindow + QDockWidget`、collapsible sidebar、workspace preset、floating panels 和 layout persistence。
- 当前 GUI 代码仍是最小 PySide6 workbench shell，没有实际动画系统；`AtelierUI Component Workbench` 已有 dev-only 入口用于 token / checklist 预览、story selection、controls metadata、手动截图和 JSON 审查备注留痕。
- `pyproject.toml` 中 PySide6 位于 optional `gui` extra；AtelierUI 不能变成非 GUI 安装路径的硬依赖。

## 3. AtelierUI 定位

`AtelierUI` 是项目专属 UI 基础层，不是成熟通用库。

它的使用边界：

- 只服务 Atelier GUI，不承诺对外 API、PyPI 发布、语义化版本或第三方复用。
- 只随 Atelier application runtime 或核心代码包一起打包。
- 用来承载软件自绘控件、动画效果、theme tokens、motion values、overlay layer、page transition、queue delegate 和其他共享 GUI 视觉基础。
- 不运行 worker、FFmpeg、模型推理、硬件调度、外部 shell 或 storage mutation。

它可以作为未来内部模块组织：

```text
atelier/gui/ui/
  theme_tokens.py
  widget_intake.py
  easing.py
  motion.py
  overlay.py
  painted_widgets.py
  page_transitions.py
  queue_delegate.py
```

当前已存在：

- `atelier/gui/ui/__init__.py`
- `atelier/gui/ui/theme_tokens.py`
- `atelier/gui/ui/widget_intake.py`

其余路径仍是规划方向，不表示当前已经存在。

采用 `AtelierUI` 的条件：

- 同一种动效规则会被两个以上控件复用。
- 动效需要统一处理 reduced motion、中断、时长、easing 或测试。
- 动效与 queue、workflow、execution、recovery 等产品状态绑定。
- 控件需要稳定自绘，避免通过频繁 `setStyleSheet()` 刷新视觉状态。

不采用 `AtelierUI` 的情况：

- 单个按钮 hover 或 focus 可以由普通 Qt style 完成。
- 一次性 prototype 不影响公共交互模型。
- 第三方组件会绕过 `WorkspaceManager`、`I18nManager`、`Scheduler` 或现有 state flow。

### 3.1 入库审查流程

新的自绘控件、delegate、overlay、page transition 或动画基础进入 `AtelierUI` 并被软件调用前，必须先经过用户审查。

准入流程：

1. 写清控件用途、调用场景、所属界面和非职责。
2. 调研相关开源项目、Qt 示例或现有项目代码，记录可借鉴的结构、状态模型、测试方式和许可证边界。
3. 先写最小失败测试或可复查的 GUI smoke / visual 验证说明。
4. 做 Atelier 自己的最小实现，保持 PySide6-native、view model 分离和 GUI-only visual state。
5. 提交给用户审查；审查通过后，才能作为 `AtelierUI` 共享组件被产品代码调用。

审查前允许：

- 在 feature 模块中做小范围候选实现。
- 用测试证明 visual state、selection、hover、animation value 不污染 domain state。
- 在文档中说明参考项目和取舍。

审查前禁止：

- 把候选控件作为通用 `AtelierUI` 组件大面积调用。
- 复制 GPL 或未授权代码。
- 为一个控件新增运行时依赖。
- 绕过 `DESIGN.md`、`I18nManager`、Workspace 边界或 GUI intent / snapshot / view model 边界。

## 4. 技术方向

AtelierUI 首选 PySide6 Widgets 与 Qt Animation Framework：

```text
QPropertyAnimation
QVariantAnimation
QParallelAnimationGroup
QSequentialAnimationGroup
QEasingCurve
QGraphicsObject / QGraphicsItem
QGraphicsOpacityEffect
QPainter
```

规则：

- 页面、panel、sidebar 和普通 widgets 使用 Qt property animation。
- Workflow Canvas 内的 node、edge、selection、drag ghost 优先使用 `QGraphicsObject` / `QGraphicsItem` 自绘状态。
- Queue 大规模列表优先使用 model/view delegate 或稳定 row widget，不为每一帧重建 widget tree。
- 进度条的业务事实来自 task / worker event / storage，不来自动画插值。
- 动画只插值视觉值，不修改 domain state。
- GUI 不直接执行 worker、FFmpeg、model inference 或 Scheduler 资源分配。

## 5. Motion Tokens

### 5.1 Duration Tokens

| Token | Value | 用途 |
|---|---:|---|
| `motion.instant` | `0-80ms` | reduced motion、状态立即落位、不可模糊的信息 |
| `motion.fast` | `120ms` | hover、press、small highlight |
| `motion.select` | `140ms` | node select、row select、focus ring |
| `motion.progress` | `160ms` | queue progress visual interpolation |
| `motion.panel` | `180ms` | sidebar、inspector、drawer、dock helper transition |
| `motion.snap` | `180ms` | card snap、slot snap、page content settle |
| `motion.page` | `220ms` | page transition、stacked view transition |
| `motion.alert` | `220ms` | failure pulse、conflict highlight，一次性 |
| `motion.max` | `320ms` | 只允许用于低频 workspace/panel transition |

默认限制：

- 高频交互不超过 `180ms`。
- 错误和冲突动画只播放一轮。
- loading shimmer 如必须使用，周期不低于 `1200ms`，且不表达真实进度。
- 真实进度动画不得超过实际 worker event 更新节奏，不能超前显示完成。

### 5.2 Easing Tokens

| Token | Qt Direction | 用途 |
|---|---|---|
| `ease.standard` | `QEasingCurve.InOutCubic` | 普通 panel/page 状态变化 |
| `ease.enter` | `QEasingCurve.OutCubic` | 新 item、overlay、tooltip、inspector 内容进入 |
| `ease.exit` | `QEasingCurve.InCubic` | item 移除、overlay 消失 |
| `ease.hover` | `QEasingCurve.OutQuad` | hover、focus、small visual response |
| `ease.snap` | `QEasingCurve.OutCubic` | card snap、slot settle、page settle |
| `ease.progress` | `QEasingCurve.Linear` | progress bar fill interpolation |
| `ease.alert` | `QEasingCurve.OutCubic` | failure pulse、conflict flash |

不要使用过强弹性曲线作为默认值。`OutBack`、bounce、elastic 只能用于调试 demo 或明确的低风险 delight，不进入任务进度、失败、硬件冲突或日志相关 UI。

## 6. Animation Driver

`AnimationDriver` 是内部协调者，负责创建、命名、取消和复用动画。它不是业务 controller。

职责：

- 通过 token 创建 Qt animation。
- 同一 widget / item / property 同一时间只允许一个主动画。
- 重复触发时从当前视觉值继续，不从旧 logical start value 重播。
- 支持 `reduced_motion`：把非必要动画缩短到 `0-80ms` 或直接落位。
- 动画结束后清理 `QGraphicsOpacityEffect`、临时 overlay 和 driver registry。
- 暴露测试友好的 deterministic mode。

非职责：

- 不读取 SQLite 作为事实源。
- 不解析 worker stdout。
- 不决定 Scheduler resource binding。
- 不持久化 workspace layout。
- 不直接创建业务 action。

建议接口形态：

```python
class AnimationDriver:
    def animate_property(self, target, property_name: bytes, end_value, token: str) -> None:
        ...

    def stop(self, target, property_name: bytes) -> None:
        ...

    def settle_now(self, target) -> None:
        ...
```

这只是规划接口，实际实现时应按 PySide6 类型、测试需要和现有 GUI 模块拆分。

## 7. Motion Values

AtelierUI 应尽量把视觉状态表达为少量 motion values，而不是到处拼 style string。

推荐 motion values：

| Value | Type | 用途 |
|---|---|---|
| `opacity` | `float 0..1` | overlay、tooltip、page content、temporary label |
| `offset_x` / `offset_y` | `float` | page slide、drag ghost、sidebar label slide |
| `scale` | `float` | card drag lift，默认只允许 `1.0..1.02` |
| `highlight` | `float 0..1` | selection ring、conflict border、cache hit marker |
| `progress_visual` | `float 0..1` | queue progress bar visual interpolation |
| `pulse` | `float 0..1` | failure/conflict one-shot pulse |
| `reveal` | `float 0..1` | inspector section expand/collapse |

稳定性规则：

- motion value 不能成为业务事实源。
- motion value 不影响 task status、artifact path、resource binding、locale、theme 或 queue order。
- hover、selection、enabled、visibility 每类状态应只有一个事实源。
- 不要让多个函数同时争夺同一个 widget 的 geometry、opacity 或 style。

## 8. Overlay Layer

Overlay layer 用于表达临时视觉反馈，不用于承载主内容。

允许：

- drag ghost。
- connection preview。
- invalid connection hint。
- conflict highlight。
- page transition mask。
- modal scrim。
- focus guide。
- short toast/snackbar 类状态提示。

禁止：

- 在 overlay 中放长期业务状态。
- 用 overlay 代替 Queue Monitor、Logs、Inspector 或 Artifact Browser。
- 用 overlay 执行任意 shell、worker 或 external tool。
- 在 overlay 动画中每帧重新布局主窗口。

实现方向：

- 普通 QWidget 页面使用透明 child overlay widget。
- Workflow Canvas 使用 `QGraphicsScene` 内的 overlay item 或独立 foreground layer。
- Overlay 应可被 `AnimationDriver` 统一取消和清理。
- Overlay 文案需要走 `I18nManager` 或 Qt translation API；error code、task id、路径和模型名保留原文。

## 9. Self-Painted Widgets

Atelier 应优先自绘这些高频控件：

```text
WorkflowNodeItem
WorkflowEdgeItem
StatusBadge
ResourceUsageBar
QueueProgressBar
QueueRowDelegate
HardwareResourceCard
CompactToggle
MotionOverlay
```

这些名称是候选方向，不表示已经进入 `AtelierUI`。每个新自绘控件都必须按第 3.1 节完成参考调研、最小验证和用户审查后，才能作为专属库组件被软件调用。

自绘规则：

- 使用 `QPainter` 绘制背景、边框、进度、badge 和状态层。
- 避免每帧 `setStyleSheet()`。
- 避免复杂阴影跟随拖拽。
- 文字布局必须稳定，状态变化不能导致 row height 或 card size 跳动。
- 状态色来自 `DESIGN.md` palette role，不在控件内部散落 magic color。
- icons 优先来自 `atelier/assets/`，继承 `currentColor` 的设计意图。

### 9.1 Component Workbench

候选自绘控件不应直接放进真实产品 GUI 中调参。AtelierUI 需要 dev-only 控件画板，用于在入库前调试参数、状态、尺寸、theme token、motion token 和截图记录。

当前第一阶段入口：

```powershell
.venv\Scripts\python -m atelier.gui.ui.component_workbench
```

控件画板边界：

- 只作为开发 / 审查工具，不进入默认工作台。
- 可以展示候选控件、参数 controls、状态 presets、token swatches 和 review checklist。
- 不运行 worker、FFmpeg、模型推理、硬件调度、任意 shell 或 SQLite mutation。
- 候选控件在画板可见，不代表已经进入 `AtelierUI` 共享调用。
- 当前已实现 token swatches、typography samples、intake checklist、story selection、controls metadata、手动 screenshot / review snapshot 和 `WorkflowNodeItem` 候选 placeholder；尚未实现真实参数 controls 驱动绘制、motion token playback、视觉 diff 或已审查共享控件。

参考模型：

- Storybook / Widgetbook 的 component catalog、story、controls、use case 组织方式。
- Qt Designer custom widget preview 的插件边界。
- Qt Design Studio 的 state / transition / timeline 思路。

规划见 `docs/plan/plan_atelier_ui_component_workbench.md`；第一阶段实现计划见 `docs/plan/plan_atelier_ui_component_workbench_foundation.md`；第二阶段 controls 计划见 `docs/plan/plan_atelier_ui_component_workbench_controls.md`；第三阶段 screenshot / review notes 计划见 `docs/plan/plan_atelier_ui_component_workbench_screenshot.md`。

## 10. Queue Delegate Animation

Queue Monitor 是 Atelier 的高频状态区域，动效必须服务可信度。

允许动画：

- `pending -> queued -> running` 的左侧状态条过渡。
- progress visual fill 从旧值插值到新值。
- 当前 stage 文本更新时短暂 highlight。
- cache hit / skipped 显示短暂状态标记。
- failed retryable 显示一次性 conflict pulse，并固定 recovery action。
- row reordering 使用短位移动画，但不能改变真实排序事实。

禁止动画：

- 进度条循环前进后回退。
- worker event 未到达时提前显示成功。
- 失败 row 只闪红但不展示原因和 recovery action。
- 为大量 queue rows 各自创建长期 timer。

事实源：

```text
Task status / Worker events / Artifacts / Storage snapshot
  -> Queue view model
  -> Queue delegate visual values
  -> AnimationDriver interpolates visual-only values
```

## 11. Page Transition Manager

Page transition manager 负责 central view、stacked pages 和 sidebar page selection 的过渡。

适用对象：

- `Workflow` / `Queue` / `Presets` / `Projects` / `Settings` page 切换。
- `Workflow Canvas` / `Hardware Scheduling Graph` 子页切换。
- Runtime / Debug / Review workspace preset 中 central view 切换。

规则：

- 首版只做 slide + fade，不做复杂 3D、blur 或 perspective。
- page transition 时长默认 `motion.page = 220ms`。
- 重复切换必须可中断。
- 新旧页面都不能在动画期间执行长任务。
- 页面切换不改变 dock layout persistence；dock layout 仍归 `WorkspaceManager`。
- 如果页面包含 running queue 或 logs，信息必须继续可见或在状态栏/Queue Monitor 有替代入口。

## 12. Collapsible Sidebar Motion

Sidebar 已在 `DESIGN.md` 与 `docs/UI_WORKSPACE_SPEC.md` 中明确必须可收缩。

推荐 motion：

```text
expanded_width: design-dependent
collapsed_width: 48px
duration: motion.panel
easing: ease.standard
label opacity: width-driven reveal
label offset_x: 4-8px
tooltip: collapsed state only, no delayed stale tooltip
```

规则：

- 宽度动画可中断。
- 当前 page indicator 不能丢失。
- 折叠态保留 icon、tooltip 和 active marker。
- 展开/收起不应挤压 Workflow Canvas 到不可读；低宽度下优先折叠 Inspector。

## 13. Workflow Canvas Motion

Workflow Canvas 是主舞台，动效应表达 node graph 的结构变化。

推荐动画：

- Node added：`opacity 0 -> 1`，`offset_y 6 -> 0`，`motion.snap`。
- Node removed：`opacity 1 -> 0`，短 exit，随后从 graph scene 删除。
- Drag lift：`scale 1.0 -> 1.02`，shadow/outline 提升，但不改变实际 graph geometry。
- Slot snap：位置插值到目标 slot，edge path 同步重绘。
- Selection：border/highlight `0 -> 1`，`motion.select`。
- Invalid connection：red path preview + tooltip，一次性 `motion.alert`。
- Execution plan generated：由 WorkflowGraph 到 ExecutionPlan 的派生关系高亮，不允许用户绕过 Scheduler。

规则：

- WorkflowGraph 是业务事实源；visual item position 需要通过明确 commit 写回 preset / graph，不靠动画过程隐式落库。
- 连线使用 `QPainterPath.cubicTo` 表达平滑连接。
- 选中 node 发 signal 更新 Inspector；动画不直接写 Inspector 数据。
- 大 graph 下优先保证拖拽、缩放和选择性能。

## 14. Hardware And Runtime Motion

硬件状态动效要帮助用户理解资源占用，而不是制造性能仪表盘噪声。

允许：

- CPU/RAM/GPU/VRAM usage bar 平滑到新值。
- waiting resource 原因短暂 highlight。
- resource conflict 使用一次性 border pulse。
- runtime component health 从 unknown / missing / ready 变化时短暂状态过渡。

禁止：

- GPU usage 大面积循环发光。
- 用动画暗示硬件修复已完成。
- 把 runtime setup action 做成不可中断的 GUI blocking flow。

硬件资源分配事实源仍是 Scheduler；HardwareDetector 只观察，GUI 只渲染。

## 15. Failure And Recovery Motion

失败是可恢复产品状态，不是单纯 error popup。

失败动效应显示：

- failed stage。
- human-readable reason。
- technical reason。
- affected downstream tasks。
- usable artifacts。
- recovery actions。

动效规则：

- failure pulse 只播放一轮。
- failed row 保持稳定可读，不自动消失。
- retry / skip / export partial artifact 等 action 必须固定在可发现位置。
- 恢复动作触发后，queue row 应进入明确状态：`retrying`、`skipped`、`exporting_partial` 或后续定义状态。

## 16. Reduced Motion And Accessibility

AtelierUI 必须提供 reduced motion 策略。

规则：

- reduced motion 下保留状态变化，但移除 slide、scale、pulse、shimmer。
- progress 可以直接跳到最新值，或使用 `motion.instant`。
- focus ring、selected border、status badge 不能被移除。
- 状态不能只靠颜色或动效表达；必须配合文字、icon 或形状。
- 中英混排、路径、task id、model name 和 GPU name 不应因动画裁切。

## 17. Open-Source Reference Boundary

这些项目是学习来源，不是当前依赖。

### 17.1 第一梯队

| Project | Link | 需要学习 | 使用边界 |
|---|---|---|---|
| `QWidget-FancyUI` | https://github.com/COLORREF/QWidget-FancyUI | Qt Widgets 主题、窗口 chrome、自绘控件、动画组织 | GPL-3.0；只读学习，不复制代码，不 vendoring |
| `PyQt-Fluent-Widgets` | https://github.com/zhiyiYo/PyQt-Fluent-Widgets | PyQt/PySide 组件分层、theme manager、animation helpers、navigation、stack/page patterns | GPL-3.0 / commercial；只读学习，不复制代码，不作为默认依赖 |
| `qt-material-widgets` | https://github.com/laserpants/qt-material-widgets | overlay、ripple、state transition、drawer、snackbar、progress 的 Widgets 架构 | BSD-3-Clause；可学习结构，未来若引用代码必须保留许可证与第三方声明 |
| `SlidingStackedWidget` | https://github.com/timschneeb/SlidingStackedWidget | stacked page slide transition、中断、方向、demo 验证方式 | MIT；可学习算法边界，Atelier 优先自行实现 PySide6 版本 |

第一梯队的作用是决定 AtelierUI 的 Widgets motion 结构。

### 17.2 第二梯队

| Project | Link | 需要学习 | 使用边界 |
|---|---|---|---|
| `QML-UI-Animations` | https://github.com/Furkanzmc/QML-UI-Animations | QML states/transitions、timing、easing demo 组织 | Public domain；仅学习概念，不迁移到 QML |
| `DarkShrill/QML-Animations` | https://github.com/DarkShrill/QML-Animations | QML animation demo、状态变化表达 | 未确认许可证；只读学习，不复制代码 |
| `RiveQtQuickPlugin` | https://github.com/basysKom/RiveQtQuickPlugin | Rive asset 与 QtQuick 集成、未来高质量 vector animation 可能性 | QtQuick 方向，非 MVP；使用前必须重新核对许可证、Rive runtime 和打包边界 |

第二梯队的作用是提醒我们：Atelier 的 motion language 可以学习声明式状态机和高质量动画资产，但当前技术方向仍是 PySide6 Widgets。

### 17.3 第三梯队

| Project | Link | 需要学习 | 使用边界 |
|---|---|---|---|
| `ImAnim` | https://github.com/soufianekhiat/ImAnim | immediate-mode motion value、easing taxonomy、timeline/debug 文档 | MIT；学习概念，不引入 Dear ImGui |
| `ImAnimate` | https://github.com/RaidcoreGG/ImAnimate | ID-keyed animation、sequence、one-shot animation API | MIT；学习 API 形态，不引入 Dear ImGui |
| `raygui animation_curve` | https://github.com/raysan5/raygui | animation curve editor、curve preview、debug UI 思路 | zlib；仅作为未来 Expert motion debug/curve editor 参考 |

第三梯队的作用是帮助定义 `motion values`、curve vocabulary 和未来 debug tools，不影响主 GUI 技术栈。

## 18. External Code Policy

默认政策：

- 可以阅读开源项目代码和文档。
- 可以记录学习结论和设计模式。
- 有参考代码或参考项目时，先阅读、比较和提炼，再实现 Atelier 自己的版本。
- 只把结构清晰、维护状态可信、bug 风险可控、许可证明确的项目纳入 Atelier 参考体系。
- 明显不稳定、bug 过多、许可证或维护状态不可确认的项目只能作为 rejected candidate 记录，不进入可借鉴清单。
- 不复制 GPL 或未授权代码。
- 不把第三方项目代码粘贴到 Atelier。
- 不新增运行时依赖，除非有单独 plan、license review、security review 和 packaging plan。
- 如果未来确实引用 permissive licensed code，需要新增 third-party notice、许可证文本、源码来源、版本、hash 和修改说明。

Rejected reference candidates：

- `Moekotori/ECHO`：不纳入 Atelier GUI / AtelierUI / plugin / release / smoke checklist 参考体系。原因：用户评估该软件 bug 过多，不适合作为本项目参考依据。

当前结论：

```text
AtelierUI should be designed as project-specific code.
AtelierUI should not be a mature reusable library.
AtelierUI should not vendor the reference projects.
AtelierUI self-painted widgets need user review before shared adoption.
```

## 19. Implementation Phases

### Phase 1: Motion Tokens And Driver

目标：

- 定义 duration / easing tokens。
- 添加 `AnimationDriver` 或等价内部 helper。
- 支持 reduced motion。

完成信号：

- 两个以上 widget 使用同一 token source。
- 单元测试能验证 token 值和 reduced motion 行为。

### Phase 2: Sidebar And Page Transition

目标：

- 实现 collapsible sidebar motion。
- 实现 page transition manager。

完成信号：

- 重复点击可中断。
- `Workflow` / `Queue` / `Settings` 等页面切换不会破坏 dock layout。

### Phase 3: Queue Delegate Animation

目标：

- Queue row 状态条、progress visual、stage highlight 和 failure pulse 使用统一 motion values。

完成信号：

- worker event 更新后 UI 平滑但不超前。
- failed row 保留 recovery actions 和原因。

### Phase 4: Workflow Canvas Motion

目标：

- Workflow node add/remove/select/drag/snap/connection preview 使用 canvas-native motion。

完成信号：

- Graph state 与 visual motion 分离。
- 大于首版 demo graph 的节点数量下仍可拖拽和选择。

### Phase 5: Overlay And Expert Motion Tools

目标：

- 增加 overlay layer。
- 评估是否需要 Expert-only motion debug panel 或 curve preview。

完成信号：

- Overlay 不承载长期业务状态。
- Debug 工具不进入默认工作台。

## 20. Validation

文档级验证：

```powershell
Get-Content -Encoding UTF8 docs\UI_MOTION_SPEC.md
```

实现级验证建议：

```powershell
python -m unittest discover -s tests
python -m pytest
python -m ruff check .
python -m mypy .
```

如果这些工具或 GUI extra 尚未配置，不要声称通过。UI motion 实现后，还应补充：

- reduced motion 单元测试。
- animation interruption 测试。
- queue progress 不超前业务事实源的测试。
- 手动 GUI 验证或截图记录。

## 21. Reference Links

- Qt Animation Framework overview: https://doc.qt.io/qt-6/animation-overview.html
- Qt for Python examples: https://doc.qt.io/qtforpython-6/examples/index.html
- `QWidget-FancyUI`: https://github.com/COLORREF/QWidget-FancyUI
- `PyQt-Fluent-Widgets`: https://github.com/zhiyiYo/PyQt-Fluent-Widgets
- `qt-material-widgets`: https://github.com/laserpants/qt-material-widgets
- `SlidingStackedWidget`: https://github.com/timschneeb/SlidingStackedWidget
- `QML-UI-Animations`: https://github.com/Furkanzmc/QML-UI-Animations
- `DarkShrill/QML-Animations`: https://github.com/DarkShrill/QML-Animations
- `RiveQtQuickPlugin`: https://github.com/basysKom/RiveQtQuickPlugin
- `ImAnim`: https://github.com/soufianekhiat/ImAnim
- `ImAnimate`: https://github.com/RaidcoreGG/ImAnimate
- `raygui`: https://github.com/raysan5/raygui

## 22. One-Line Rule

```text
Atelier motion should make state easier to trust, not make the interface harder to believe.
```
