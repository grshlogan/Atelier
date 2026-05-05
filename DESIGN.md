# Atelier DESIGN.md

本文档是 Atelier 的产品视觉与交互设计事实源。它回答“Atelier 应该如何呈现、如何感受、如何组织界面”。工程边界、架构纪律和开发流程以 `AGENTS.md` 为准。

Atelier 是一个本地优先的 AI 视频工作流工作站。它应该像一个安静、专业、可信的深色创作者工坊：用户在这里组织视频处理流程，软件把流程转译成硬件执行计划，队列稳定运行，失败可以恢复，产物可以追踪。

## 1. Product Identity

Atelier 的设计关键词：

- 安静，但不是空。
- 专业，但不冰冷。
- 有媒体工作台的质感，但不做影院式首页。
- 有硬件控制的清晰度，但不变成黑绿硬件控制台。
- 有 AI 工具的灵活性，但不把复杂度直接摊给用户。

它不是：

- landing page。
- ComfyUI 式完全自由节点画布。
- 只有一个进度条的视频转换器。
- 单纯字幕工具。
- Apple、Linear、NVIDIA、Ollama 或 RunwayML 的仿站。

首屏应该是实际工作台，而不是介绍页。用户打开应用后应立即看到 workflow、队列、硬件状态、日志、产物和下一步动作。

## 2. Reference System

根目录 `DESIGN.md` 是 Atelier 的设计事实源。`docs/Atelier_Main_UI_Spec.md` 是主界面绘制规格 / concept implementation spec，用于把本文件的原则落到一张可绘制、可实现的主界面概念图上。`docs/design-md-references/` 是建设性意见源，只用于吸收方法、控件克制、空间纪律、状态密度、硬件表达或媒体工作台气质。

当前参考文件：

- `apple.DESIGN.md`：参考空间纪律、控件精致度、平台级克制。
- `linear.DESIGN.md`：参考工程工具的精确层级、状态密度、设置组织。
- `nvidia.DESIGN.md`：参考 GPU、性能指标、硬件状态表达。
- `ollama.DESIGN.md`：参考本地 AI、runtime、模型和命令输出语境。
- `runwayml.DESIGN.md`：参考视频媒体氛围、创作工具感和高质量媒体预览。

禁止：

- 不要把任一参考文件当作 Atelier 的事实源。
- 不要让 `docs/Atelier_Main_UI_Spec.md` 覆盖本文件的事实源地位；当两者冲突，以本文件为准，再反向修正绘制规格。
- 不要直接复制外部品牌色、字体、布局、官网 hero 或营销结构。
- 不要因为参考 `nvidia` 就把全局做成黑绿控制台。
- 不要因为参考 `runwayml` 就把工作台做成暗黑影院。
- 不要因为参考 `apple` 就把桌面工具做成大留白官网。

## 3. Visual Theme And Atmosphere

Atelier 的默认视觉基线是深色工作台。浅色主题可以作为未来 theme switching 保留，但主界面设计、默认截图、首版工作台和绘制规格都应优先使用深色。

整体感觉：

- 页面背景深、冷、干净、耐看。
- 工作区表面清晰，卡片轻描边，少厚阴影；可以有克制的选中 glow，但不能变成发光游戏 UI。
- 中央 canvas 有“正在编排流程”的空间感。
- 硬件和执行信息足够密集，但保持可读。
- 视频预览、缩略图、波形、字幕片段和产物状态是主要视觉内容，不用装饰图抢注意力。

界面丰富感来自信息组织、状态反馈、媒体内容、流程拓扑和细节一致性，不来自大面积渐变、装饰光斑、巨型标题或营销式卡片堆叠。

## 4. Color Palette And Roles

长期颜色应语义化，不以外部品牌为来源。下列深色 palette 是默认主界面基线；浅色 palette 将来作为可选主题另行定义。

| Role | Value | 用途 |
|---|---:|---|
| App background | `#08111D` | 主应用背景 |
| Top bar | `#09131F` | 顶部命令栏 |
| Sidebar | `#0A1420` | 左侧导航栏 |
| Canvas background | `#0A1422` | Workflow / Execution canvas 绘图区 |
| Panel background | `#0D1826` | 停靠面板、主工作区面板 |
| Panel background raised | `#111D2C` | 抬升面板、工具按钮、表单表面 |
| Card background | `#172332` | Workflow node、queue row、hardware card |
| Card hover | `#1C2B3D` | hover / active surface |
| Border | `#223247` | 默认描边 |
| Border subtle | `#182638` | 弱分割线、顶部切割线 |
| Border strong | `#2A3A50` | hover、选中或节点描边 |
| Text primary | `#F3F7FB` | 主文本 |
| Text secondary | `#B7C2D2` | 次级文本 |
| Text muted | `#7F8EA3` | 元信息、占位 |
| Text disabled | `#526174` | 禁用文本 |
| Primary blue | `#3B82F6` | 主交互强调、当前节点、运行中 |
| Primary blue light | `#60A5FA` | 高亮连线、focus、运行状态 |
| Agent violet | `#A78BFA` | AI agent / 翻译 / 审校相关能力 |
| Cyan accent | `#38BDF8` | 波形、音频、信息辅助强调 |
| Success | `#39C86A` | 完成、可用产物 |
| Warning | `#F6C85F` | 等待、冲突、需确认 |
| Danger | `#F87171` | 失败、取消、破坏性动作 |
| Pending | `#7A8797` | pending、disabled operational state |

规则：

- 状态色必须有语义，不作装饰。
- 主色不要铺满大面积背景，优先用于边框、状态条、图标、当前项和主运行按钮。
- 深色是默认主题，但仍要区分 app background、panel、card、canvas 和 hover surface，避免一团黑。
- 视频和产物缩略图可以带来真实色彩，应用 chrome 保持克制。

## 5. Typography

默认字体栈：

```text
"Segoe UI", "Microsoft YaHei UI", system-ui, sans-serif
```

等宽字体：

```text
"Cascadia Mono", "Consolas", "Courier New", monospace
```

建议层级：

| 用途 | 建议 |
|---|---|
| Window title | 14px / 700 |
| Page title | 20px / 750 |
| Panel title | 15px / 700 |
| Card title | 14px / 650 |
| Body | 13px / 400-600 |
| Caption | 12px / 500 |
| Metadata | 11px / 500 |
| Metric | 28-34px / 700 |
| Log / code | 12-13px / 400 |

规则：

- 这是桌面工作台，不使用 landing page 级巨型标题。
- 卡片、检查器、队列和状态面板使用紧凑字号。
- 日志、路径、命令、worker events 和 artifact ids 使用等宽字体。
- 中文和英文切换后不得裁切按钮、标签、队列状态或节点标题。

## 6. Layout Principles

Atelier 的主界面应是专业工作站，不是网页式单页，也不是完全自由拖拽仪表盘。默认结构应稳定，但面板应支持嵌入、停靠、隐藏、浮动和 workspace preset。

布局北极星是“Workflow 复页 + 可嵌入/可浮动 panels”。主界面只有两条必须稳定的结构切割线：顶部命令栏切割线，以及 Workflow 工作区与左侧导航栏的切割线。其他区域优先作为可停靠/可浮动 panel，而不是不可改变的硬编码分割。

```text
Top command bar
  -> app icon, Atelier, New Project, Open, Save, Save As, Import, Export,
     Undo, Redo, Run Workflow, Schedule, Remind, Help, Light/Dark, Person

Collapsible left navigation rail
  -> Workflow, Queue, Presets, Projects, Settings, and future Expert pages

Workflow page
  -> primary "card-line-flow graph" canvas
  -> hardware scheduling graph as a child page derived from the workflow graph

Embeddable / floating panels
  -> Queue Monitor, Hardware Resources, Card Detailed Settings,
     Inspector, Logs, Artifact Browser, Runtime panels

Workspace Manager
  -> persists panel docking, floating windows, visibility, tabs, and presets
```

推荐首版骨架：

```text
┌────────────────────────────────────────────────────────────────────────┐
│ Top command bar: app/actions/history/run/schedule/help/theme/person     │
├──────────────┬─────────────────────────────────────────────────────────┤
│ Collapsible  │ Workflow page                                           │
│ navigation   │   Card-line-flow canvas                                 │
│ rail         │   Hardware scheduling child page                         │
│              │   Embedded/floating panels as needed:                    │
│ Workflow     │     Queue Monitor                                        │
│ Queue        │     Hardware Resources                                   │
│ Presets      │     Card Detailed Settings / Inspector                   │
│ Projects     │     Logs / Artifacts / Runtime                           │
│ Settings     │                                                         │
└──────────────┴─────────────────────────────────────────────────────────┘
```

布局规则：

- Workflow Canvas 是主界面的最高优先级区域；它承载用户定义的“卡片-连线-流程图”，并可保存为 workflow preset / template。
- Execution / Hardware Scheduling Graph 是 Workflow Canvas 的子页面或派生页，不能绕过 WorkflowGraph 与 Scheduler。
- Queue Monitor、Hardware Resources、Card Detailed Settings / Inspector 都是可嵌入页或 panel；默认应足够可见，但允许用户浮动、停靠、隐藏或重排。
- 硬件状态要常驻可扫读，但不要抢走 workflow 的主导权。
- Queue Monitor 不应被藏到不可发现的二级入口；它可以作为独立页，也可以作为嵌入 panel。
- Hardware Resources 不应只是设置页信息；它应在执行时解释资源占用和冲突。
- 左侧导航栏与页栏概念独立，必须可收缩；折叠态优先保留图标和 tooltip，展开态显示文字。可参考 `E:\AI\AiVideoSRTGui\app\gui\sidebar_navigation.py` 的 48px 折叠宽度、可中断动画、宽度驱动文字淡入/滑入和 tooltip 同步策略。
- 高频动作常驻，低频维护动作下沉到设置或管理面板。
- 不要照搬参考图的颜色、图标、品牌名或视觉皮肤；只继承这种四区工作台布局。

## 7. Component Rules

### Icons

- 当前主界面图标库是 `atelier/assets/`。
- 当前软件品牌图标位于 `atelier/assets/brand/`，用于 app icon、窗口图标、安装器、About 页面、顶部品牌标记和托盘图标。
- 图标以 24 × 24 的线性 SVG 为基线，使用 `stroke="currentColor"` 和 `fill="none"`，颜色由主题 palette、控件状态或样式系统控制。
- `brand/atelier_icon_full.svg` 可使用渐变和 app tile 质感；小尺寸 UI 应使用 `atelier_logo_compact.svg`、`atelier_logo_mono.svg` 或 tray variants，避免把 full icon 机械缩小到 16-32px。
- `brand/01.png` 到 `brand/04.png` 是品牌 SVG 的视觉参考渲染；SVG 应尽量保持与这些 PNG 的轮廓、流程线数量、节点块和发光质感一致，但不能通过嵌入 raster image 伪装成 SVG。
- 顶部栏、左侧导航、Workflow 节点、Queue Monitor、Hardware Resources、Inspector、状态提示和系统模块图标应优先从 `atelier/assets/toolbar/`、`navigation/`、`nodes/`、`queue/`、`hardware/`、`inspector/`、`status/`、`system/` 取用。
- `atelier/assets/icon_manifest.json` 是当前图标清单；`atelier/assets/atelier_icons_sprite.svg` 和 `preview.html` 可用于预览或后续构建流程参考。
- 不直接复制外部品牌 logo、第三方产品图标或参考文档里的视觉皮肤；需要新增图标时，应保持 Atelier 当前线性、克制、深色工作站兼容的语言。
- 图标库是资源事实，不等于已经实现 Qt resource 注册、IconManager、运行时重染色或图标缓存。

### Workflow Cards

- 卡片代表真实 workflow node，不只是视觉块。
- 卡片应显示 node name、category、关键参数、输入输出端口、状态和缓存信息。
- 合法连接清晰可见，非法连接阻止或标红说明。
- 当前选中卡片使用 `Accent cyan` 边框或细状态条。
- AI agent 类节点可使用少量 `Agent violet`，但不要扩散成全局主题。

### Execution Cards

- Execution card 表示已调度 task。
- 必须显示 phase、lane、resource binding、exclusive/shared、状态和冲突。
- GPU 冲突、显存不足、设备缺失等状态要有明确修复动作。
- 不要让用户在 Execution Canvas 中直接绕过 Scheduler。

### Queue Rows

- 队列项应显示缩略图、媒体名、workflow preset、整体进度、当前阶段、资源、ETA、输出路径和主要动作。
- 多阶段任务要显示阶段和分支进度，不只显示一个百分比。
- 失败行应保留可用 artifacts 和 recovery actions。

### Inspector

- Inspector 是上下文面板，不是全局设置页。
- 当前选中 workflow node、execution task 或 artifact 决定 inspector 内容。
- 参数分为 `Basic / Advanced / Expert`。
- Dangerous 或 experimental 项必须明确标记。

### Logs And Console

- 日志区域使用更深的表面和等宽字体，与默认深色 chrome 仍要有层级差。
- 默认显示高信号摘要，详细日志可展开。
- Worker progress 以结构化事件为事实源，不从随机文本日志解析主进度。

### Media And Artifacts

- 视频缩略图、音频波形、字幕片段和输出文件是核心视觉内容。
- Artifact card 应展示类型、路径、来源 task、hash 或 metadata、是否可复用。
- 产物预览要帮助用户判断结果，不要只展示文件名。

## 8. Motion Principles

动效用于解释状态变化：

- card drag。
- slot snap。
- node added / removed。
- execution plan generated。
- task started / completed / failed。
- conflict highlight。
- inspector expand / collapse。
- queue progress update。

规则：

- 动画要短，可打断。
- 不要让动效影响按钮、日志、状态灯和进度可信度。
- 失败和冲突动效应帮助定位问题，不要制造紧张感。

## 9. Responsive And Window Behavior

Atelier 首先是桌面应用。

- 1280px 宽度以下优先收窄导航和 inspector。
- 1024px 以下可把 inspector 变成可折叠侧栏。
- Queue Monitor 可以在小窗口中变成底部 tabs。
- Canvas 必须保持最小可用尺寸，不因侧栏挤压到不可读。
- 所有固定格式元素需要稳定尺寸，hover、状态文本和进度变化不得导致布局跳动。

## 10. Accessibility And Readability

- 文本与背景必须有足够对比度。
- 状态不能只靠颜色表达，应配合文字、图标或形状。
- 错误、等待、运行、完成、缓存、跳过状态必须容易区分。
- 控件命中区域适合桌面鼠标操作。
- 中英文混排时路径、模型名、GPU 名称和 task id 不应被错误换行。

## 11. Do

- 保持工作台真实可用，不做展示页。
- 把 workflow、execution、queue、artifacts、hardware 和 recovery 作为界面核心。
- 让硬件计划可解释，让失败可恢复。
- 默认使用深色工作台主题，保留浅色主题作为未来可切换主题。
- 以 Workflow 复页和“卡片-连线-流程图”为主舞台，让 Queue / Hardware / Inspector 作为可嵌入或可浮动 panel 协同工作。
- 使用媒体内容本身增强视觉，而不是添加装饰。
- 需要外部参考时只读相关文件，并转译为 Atelier 自己的语言；`docs/design-md-references/` 只提供建设性意见。

## 12. Don't

- 不要做营销 hero。
- 不要做完全自由节点编辑器。
- 不要把 Workflow 主舞台降级成普通二级页。
- 不要把 Queue Monitor、Hardware Resources 或 Card Detailed Settings 写死为不可移动的唯一布局。
- 不要把所有参数摊成一个巨大全局表单。
- 不要把队列做成单个模糊进度条。
- 不要卡片嵌套卡片。
- 不要用大面积品牌色或装饰渐变。
- 不要把深色主题做成黑绿控制台、暗黑影院或花哨游戏 UI。
- 不要让 GUI 控件直接表达底层命令拼接。

## 13. Agent Usage Guide

当修改 UI、布局、主题、动效、组件、工作台页面、视觉基调或用户可见交互时：

1. 先读 `AGENTS.md`，确认工程边界。
2. 再读本文件，确认设计事实源。
3. 需要绘制或实现主界面时，再读 `docs/Atelier_Main_UI_Spec.md`，把它作为主界面 concept implementation spec。
4. 如需参考外部风格，只读取 `docs/design-md-references/` 中与任务相关的文件。
5. 把参考中的有用方法转译回 Atelier 的颜色、组件、布局和产品目标。
6. 修改后说明验证范围。若没有可运行 UI，就说明只完成文档级验证。
