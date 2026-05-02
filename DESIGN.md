# Atelier DESIGN.md

本文档是 Atelier 的产品视觉与交互设计事实源。它回答“Atelier 应该如何呈现、如何感受、如何组织界面”。工程边界、架构纪律和开发流程以 `AGENTS.md` 为准。

Atelier 是一个本地优先的 AI 视频工作流工作站。它应该像一个安静、专业、可信的创作者工坊：用户在这里组织视频处理流程，软件把流程转译成硬件执行计划，队列稳定运行，失败可以恢复，产物可以追踪。

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

根目录 `DESIGN.md` 是 Atelier 的设计事实源。`docs/design-md-references/` 是参考库，只用于启发。

当前参考文件：

- `apple.DESIGN.md`：参考空间纪律、控件精致度、平台级克制。
- `linear.DESIGN.md`：参考工程工具的精确层级、状态密度、设置组织。
- `nvidia.DESIGN.md`：参考 GPU、性能指标、硬件状态表达。
- `ollama.DESIGN.md`：参考本地 AI、runtime、模型和命令输出语境。
- `runwayml.DESIGN.md`：参考视频媒体氛围、创作工具感和高质量媒体预览。

禁止：

- 不要把任一参考文件当作 Atelier 的事实源。
- 不要直接复制外部品牌色、字体、布局、官网 hero 或营销结构。
- 不要因为参考 `nvidia` 就把全局做成黑绿控制台。
- 不要因为参考 `runwayml` 就把工作台做成暗黑影院。
- 不要因为参考 `apple` 就把桌面工具做成大留白官网。

## 3. Visual Theme And Atmosphere

Atelier 的默认视觉基线是浅色工作台，辅以低饱和深色工具面板和少量清晰状态色。

整体感觉：

- 页面背景偏冷、干净、耐看。
- 工作区表面清晰，卡片轻描边，少厚阴影。
- 中央 canvas 有“正在编排流程”的空间感。
- 硬件和执行信息足够密集，但保持可读。
- 视频预览、缩略图、波形、字幕片段和产物状态是主要视觉内容，不用装饰图抢注意力。

界面丰富感来自信息组织、状态反馈、媒体内容和细节一致性，不来自大面积渐变、装饰光斑、巨型标题或营销式卡片堆叠。

## 4. Color Palette And Roles

长期颜色应语义化，不以外部品牌为来源。

| Role | Value | 用途 |
|---|---:|---|
| App background | `#F4F7FA` | 主应用背景 |
| Canvas background | `#EEF3F7` | Workflow / Execution canvas 底色 |
| Surface | `#FFFFFF` | 面板、卡片、输入表面 |
| Surface muted | `#F8FAFC` | 次级表面、表格行 |
| Surface dark | `#20252D` | 日志、硬件细节、深色检查器 |
| Surface dark raised | `#2A303A` | 深色面板抬升层 |
| Border | `#DCE3EA` | 默认描边 |
| Border strong | `#C8D2DC` | hover、选中或分割 |
| Text primary | `#111827` | 主文本 |
| Text secondary | `#5F6B7A` | 次级文本 |
| Text muted | `#8A96A6` | 元信息、占位 |
| Text on dark | `#F5F7FA` | 深色面板文本 |
| Accent cyan | `#25A7B8` | 主交互强调、当前节点、运行中 |
| Accent blue | `#4E7FD7` | 链接、计划生成、信息状态 |
| Agent violet | `#7868D8` | AI agent / 翻译 / 审校相关能力 |
| Success | `#2F8A63` | 完成、可用产物 |
| Warning | `#C9852B` | 等待、冲突、需确认 |
| Danger | `#D14B4B` | 失败、取消、破坏性动作 |

规则：

- 状态色必须有语义，不作装饰。
- 主色不要铺满大面积背景，优先用于边框、状态条、图标和当前项。
- 深色面板只用于日志、硬件详情、执行检查器等高技术密度区域。
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

Atelier 的主界面应是固定工作台结构，不是任意拖拽布局系统。

布局北极星是“专业工作站四区结构”，而不是某张图的颜色、图标或品牌风格。需要参考的是空间关系：

```text
Top command bar
  -> project actions, run workflow, schedule, global status

Left navigation rail
  -> workflow, hardware plan, queue, presets, projects, settings

Center work canvas
  -> Workflow Canvas / Execution Canvas as the primary stage

Right inspector
  -> selected node, task, artifact, or resource details

Bottom operational band
  -> Queue Monitor and Hardware Resources always visible enough to trust execution
```

推荐首版骨架：

```text
┌──────────────────────────────────────────────────────────────────────┐
│ Project actions / Run workflow / Schedule / Global status            │
├──────────────┬────────────────────────────────────┬─────────────────┤
│ Navigation   │ Workflow Canvas / Execution Canvas │ Inspector       │
│ Workflow     │ node graph, phase lanes, validity  │ Node params     │
│ Hardware     │ media flow, artifacts, conflicts   │ Resource need   │
│ Queue        │                                    │ Failure policy  │
│ Presets      │                                    │ Artifacts       │
│ Projects     ├──────────────────────┬─────────────┴─────────────────┤
│ Settings     │ Queue Monitor         │ Hardware Resources             │
│              │ progress, stages, ETA │ GPU / CPU / RAM / resource use │
└──────────────┴──────────────────────┴───────────────────────────────┘
```

布局规则：

- 中央区域优先服务 Workflow Canvas 和 Execution Canvas。
- 右侧 inspector 展示当前节点、参数、资源需求、失败策略和产物。
- 底部区域采用操作带结构，Queue Monitor 和 Hardware Resources 同时可见。
- 硬件状态要常驻可扫读，但不要抢走 workflow 的主导权。
- Queue Monitor 不应被藏到二级页；它是执行可信度的一部分。
- Hardware Resources 不应只是设置页信息；它应在执行时解释资源占用和冲突。
- 高频动作常驻，低频维护动作下沉到设置或管理面板。
- 不要把主界面改成自由拖拽仪表盘。
- 不要照搬参考图的颜色、图标、品牌名或视觉皮肤；只继承这种四区工作台布局。

## 7. Component Rules

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

- 日志区域使用深色表面和等宽字体。
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
- 使用媒体内容本身增强视觉，而不是添加装饰。
- 需要外部参考时只读相关文件，并转译为 Atelier 自己的语言。

## 12. Don't

- 不要做营销 hero。
- 不要做完全自由节点编辑器。
- 不要把所有参数摊成一个巨大全局表单。
- 不要把队列做成单个模糊进度条。
- 不要卡片嵌套卡片。
- 不要用大面积品牌色或装饰渐变。
- 不要把深色日志面板扩散成全局暗黑主题。
- 不要让 GUI 控件直接表达底层命令拼接。

## 13. Agent Usage Guide

当修改 UI、布局、主题、动效、组件、工作台页面、视觉基调或用户可见交互时：

1. 先读 `AGENTS.md`，确认工程边界。
2. 再读本文件，确认设计事实源。
3. 如需参考外部风格，只读取 `docs/design-md-references/` 中与任务相关的文件。
4. 把参考中的有用方法转译回 Atelier 的颜色、组件、布局和产品目标。
5. 修改后说明验证范围。若没有可运行 UI，就说明只完成文档级验证。
