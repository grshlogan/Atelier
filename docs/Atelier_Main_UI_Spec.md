# Atelier 主界面 UI 绘制规格 v0.1

> 用途：作为 Atelier 主界面的绘制规格 / concept implementation spec，指导 Codex / Claude Code / 设计工具绘制和实现主工作台概念。  
> 事实源关系：根目录 `DESIGN.md` 仍是设计事实源；本文档服从 `DESIGN.md`，用于把主界面视觉、布局和组件落到可绘制规格。  
> 参考源关系：`docs/design-md-references/` 只作为建设性意见源，不作为 Atelier 事实源。  
> 品牌名：产品唯一名称是 `Atelier`。不要在 UI、文档或代码中使用其他名称作为产品名。  
> 目标：明确主界面布局、控件位置、尺寸、视觉层级、状态样式和交互意图。  
> 推荐画布：`1600 × 1000`，比例 `16:10`。所有坐标以左上角为原点。

---

## 0. 整体定位

这个界面不是“简单视频处理软件”，而是一个专业的 **AI 视频工作流工作站**。

用户一眼应该看到三件事：

```text
1. 中央：Workflow Canvas，说明正在设计什么视频处理流程
2. 嵌入/浮动：Card Detailed Settings / Inspector，说明当前选中节点的参数
3. 嵌入/浮动：Queue + Hardware，说明任务队列和硬件资源状态
```

整体气质：

```text
专业
克制
深色
低饱和
卡片化
清晰状态
工作站感
```

不要做成：

```text
传统后台表格软件
花哨游戏 UI
网页营销页
普通字幕工具
ComfyUI 满屏自由节点
```

---

## 1. 画布尺寸与全局坐标

推荐设计稿尺寸：

```text
width: 1600px
height: 1000px
ratio: 16:10
```

概念图区域划分：

```text
Top Bar:             x=0    y=0    w=1600 h=68
Left Sidebar:        x=0    y=68   w=210  h=560
Center Canvas:       x=210  y=68   w=1018 h=560
Right Inspector:     x=1238 y=68   w=362  h=560
Bottom Queue:        x=0    y=638  w=1030 h=362
Bottom Hardware:     x=1040 y=638  w=560  h=362
```

注意：

- 顶部栏横跨全屏。
- 这些坐标用于绘制 1600 × 1000 概念图，不代表唯一产品布局或不可移动的硬编码 geometry。
- 产品实现层面只有两条必须稳定的结构切割线：顶部栏切割线，以及左侧导航与 Workflow 工作区的切割线。
- 左侧导航与页栏概念独立，必须可收缩。
- `Queue Monitor`、`Hardware Resources`、`Card Detailed Settings / Inspector` 是可嵌入页 / dock panel / floating panel，默认可见但不应被写死为不可移动区域。
- 中央 `Workflow Canvas` 是主舞台；其他 panel 的布局服从 Workflow 可用性。

---

## 2. 全局颜色规范

### 2.1 背景色

```text
App Background:        #08111D
Panel Background:      #0D1826
Panel Background 2:    #111D2C
Card Background:       #172332
Card Background Hover: #1C2B3D
Canvas Background:     #0A1422
Top Bar:               #09131F
Sidebar:               #0A1420
Border:                #223247
Border Subtle:         #182638
```

### 2.2 主色与状态色

```text
Primary Blue:          #3B82F6
Primary Blue Light:    #60A5FA
Primary Glow:          rgba(59,130,246,0.35)

Success Green:         #39C86A
Success BG:            rgba(57,200,106,0.16)

Warning Yellow:        #F6C85F
Warning BG:            rgba(246,200,95,0.16)

Error Red:             #F87171
Error BG:              rgba(248,113,113,0.16)

Pending Gray:          #7A8797
Pending BG:            rgba(122,135,151,0.16)

Purple Accent:         #A78BFA
Cyan Accent:           #38BDF8
Pink Accent:           #F472B6
```

### 2.3 文字颜色

```text
Text Primary:          #F3F7FB
Text Secondary:        #B7C2D2
Text Muted:            #7F8EA3
Text Disabled:         #526174
Text On Primary:       #FFFFFF
```

---

## 3. 字体与字号

推荐字体：

```text
Windows: Segoe UI / Microsoft YaHei UI
macOS: SF Pro / PingFang SC
Fallback: Inter / Noto Sans CJK
```

字号层级：

```text
App Title:       22px / 600
Panel Title:     15px / 600
Card Title:      13px / 600
Body:            12px / 400
Meta:            11px / 400
Badge:           10px / 600
Tiny Label:      9px  / 500
```

行高：

```text
默认行高：1.35
密集元信息：1.25
```

---

## 3.5 图标资源

当前主界面图标库：

```text
atelier/assets/
```

使用规则：

- 顶部栏使用 `atelier/assets/toolbar/`。
- 左侧导航使用 `atelier/assets/navigation/`。
- Workflow 节点卡片使用 `atelier/assets/nodes/`。
- Queue Monitor 使用 `atelier/assets/queue/` 和 `atelier/assets/status/`。
- Hardware Resources 使用 `atelier/assets/hardware/`。
- Card Detailed Settings / Inspector 使用 `atelier/assets/inspector/`。
- Runtime、Security、Plugin、Workspace 等系统入口使用 `atelier/assets/system/`。
- 图标颜色通过 `currentColor` 继承，不在图标文件中写死主色。
- 本文档绘制主界面时应优先复用这些图标，不直接临摹外部参考品牌图标。

注意：`atelier/assets/` 是当前图标资源库，不代表已经实现 Qt `.qrc`、IconManager、图标缓存或主题重染色。

---

## 4. 顶部工具栏 Top Bar

顶部栏内容顺序固定为：

```text
软件图标
Atelier
New Project
Open
Save
Save As
Import
Export
Undo
Redo
Run Workflow
Schedule
Remind
Help
Light/Dark
Person
```

### 4.1 区域尺寸

```text
x=0 y=0 w=1600 h=68
background: #09131F
bottom border: 1px #182638
```

### 4.2 左侧 Logo 区

```text
Logo Icon: x=22 y=18 w=28 h=28
App Name:  x=58 y=19 w=150 h=28
Text: Atelier
Font: 22px / 600
Color: #F3F7FB
```

Logo 风格：

- 抽象节点 / 星形 / workflow 图标。
- 蓝色渐变，建议 `#60A5FA -> #2563EB`。
- 不要使用复杂插画。

### 4.3 文件操作按钮组

起始位置：

```text
x=220 y=16 h=36
```

按钮：

```text
New Project  w=120
Open         w=82
Save         w=82
Save As      w=100
Import       w=92
Export       w=92
```

按钮样式：

```text
background: #111D2C
border: 1px #1E2D40
radius: 6px
padding: 10px 14px
icon: 16px
gap: 8px
font: 12px
```

悬停：

```text
background: #182638
border: #2B3E57
```

### 4.4 中部撤销 / 重做

```text
Undo Icon: x=875 y=24 w=20 h=20
Redo Icon: x=920 y=24 w=20 h=20
Color: #B7C2D2
Hover: #F3F7FB
```

### 4.5 Run Workflow 主按钮

```text
x=990 y=14 w=175 h=40
background: #2563EB
radius: 7px
icon: play triangle 16px
text: Run Workflow
dropdown caret: right side
```

按钮应是整个顶栏最强视觉焦点。

### 4.6 Schedule 按钮

```text
x=1186 y=16 w=110 h=36
background: #111D2C
border: #1E2D40
radius: 6px
text: Schedule
icon: calendar
```

### 4.7 右侧状态图标组

```text
Remind:     x=1340 y=24
Help:       x=1388 y=24
Light/Dark: x=1436 y=24
Person:     x=1500 y=14 w=40 h=40
Status Dot: x=1552 y=31 w=8 h=8
```

Avatar：

```text
circle 40px
background: #2563EB
text: AD
font: 13px / 600
```

Status Dot：

```text
green #39C86A
```

---

## 5. 左侧导航 Sidebar

侧边栏规则：

- Sidebar 与 Workflow 页栏独立。
- Sidebar 必须支持收缩与展开。
- 折叠态优先保留图标、tooltip 和当前页指示；展开态显示文字。
- 可参考 `E:\AI\AiVideoSRTGui\app\gui\sidebar_navigation.py` 的实现策略：`48px` 折叠宽度、可中断展开/收起动画、宽度驱动的文字淡入/滑入、tooltip 同步和 i18n 文案更新。
- Sidebar 不直接承载 Queue / Hardware / Inspector 内容，这些内容是独立页或可嵌入/浮动 panel。

### 5.1 区域尺寸

```text
x=0 y=68 w=210 h=560
background: #0A1420
right border: 1px #182638
```

### 5.2 导航项

起始：

```text
x=8 y=86
item w=190 h=52
gap=12
radius=8
```

导航项列表：

```text
Workflow       active
Hardware Plan
Queue
Presets
Projects
Settings
```

每项结构：

```text
icon: x+18 y+16 w=20 h=20
label: x+58 y+16
font: 14px / 500
```

Active 样式：

```text
background: linear-gradient(90deg, #1E3A8A, #1D4ED8)
left active bar: x=0 w=4 h=52 color #3B82F6
text: #F3F7FB
icon: #93C5FD
```

Inactive：

```text
background: transparent
text: #B7C2D2
icon: #9CA8B8
hover background: #111D2C
```

### 5.3 Current Project 卡片

```text
x=12 y=535 w=186 h=76
background: #111D2C
border: 1px #1E2D40
radius: 8
```

内容：

```text
Title: Current Project
  x=24 y=548
  font 10px muted

Project Name: Travel Doc Upgrade
  x=24 y=570
  font 13px / 600

Path: /Projects/Travel_Doc
  x=24 y=590
  font 11px muted

Caret: x=172 y=570
```

---

## 6. 中央 Workflow Canvas

Workflow 是页的概念，而且是复页：

```text
Workflow Page
  -> Workflow Canvas: 用户定义的“卡片-连线-流程图”
  -> Hardware Scheduling Graph: 基于 Workflow Canvas 派生的硬件调度子页面
```

规则：

- “卡片-连线-流程图”优先级最高，是主界面的工作台核心。
- Workflow Canvas 可以被保存为 workflow preset / template。
- Hardware Scheduling Graph 基于 WorkflowGraph / ExecutionPlan 生成，不允许绕过 Scheduler。
- Queue、Presets、Projects、Settings 等侧边栏入口是独立页；Queue Monitor 也可以作为嵌入 panel 出现在 Workflow 页中。

### 6.1 区域尺寸

```text
x=210 y=68 w=1018 h=560
background: #0D1826
border: 1px #1E2D40
radius: 8
```

内边距：

```text
left/right: 24px
top: 18px
bottom: 18px
```

### 6.2 标题与工具区

标题：

```text
x=234 y=86
text: Workflow Canvas
font: 15px / 600
color: #F3F7FB
```

左侧 Canvas 控件：

```text
Zoom Group: x=234 y=118 w=126 h=34
  [-] [100%] [+]
  radius: 6
  background: #111D2C
```

其他控件：

```text
Fit View: x=370 y=118 w=34 h=34
Lock:     x=414 y=118 w=34 h=34
```

右侧控件：

```text
Add Node:   x=970 y=82 w=110 h=36
View Toggle Group: x=1090 y=82 w=110 h=36
```

### 6.3 Canvas 绘图区

```text
x=226 y=156 w=985 h=450
background: #0A1422
radius: 6
```

背景：

- 点阵网格。
- 点半径 `1px`。
- 点颜色 `rgba(148,163,184,0.18)`。
- 间距 `16px`。
- 不要使用粗网格线。

---

## 7. Workflow 节点卡片规范

### 7.1 通用节点尺寸

普通节点：

```text
w=140 h=92
radius=8
background: #172332
border: 1px #2A3A50
shadow: 0 8 22 rgba(0,0,0,0.28)
```

选中节点：

```text
border: 2px #3B82F6
outer glow: 0 0 0 3 rgba(59,130,246,0.15)
```

状态角标：

```text
x=card_right-46 y=card_bottom-24
h=18
radius=9
font=9px/600
```

连接点：

```text
circle 10px
fill: #0A1422
stroke: #B7C2D2
selected stroke: #3B82F6
```

连接线：

```text
stroke: #9CA8B8
width: 2px
style: smooth cubic bezier
active stroke: #60A5FA
```

### 7.2 节点内部布局

```text
Icon: x+14 y+16 w=22 h=22
Title: x+42 y+14
Subtitle: x+14 y+48
Status Badge: x+90 y+62
```

标题：

```text
font 13px / 600
color #F3F7FB
```

副标题：

```text
font 11px
color #B7C2D2
```

### 7.3 具体节点位置

以下坐标以全局画布为基准，接近之前生成图。

#### Video Input

```text
x=226 y=278 w=132 h=92
title: Video Input
subtitle: Source
status: OK
icon: purple film
```

输出连接点：

```text
right: x=358 y=324
```

#### Audio Extract

```text
x=420 y=190 w=140 h=92
title: Audio Extract
subtitle: Extract Audio
status: OK
icon: cyan waveform
```

输入点：

```text
left: x=420 y=236
```

输出点：

```text
right: x=560 y=236
```

#### ASR Subtitle

```text
x=595 y=190 w=140 h=92
title: ASR Subtitle
subtitle: Whisper Large V3
status: OK
icon: blue CC
```

#### Translate Agent selected

```text
x=770 y=190 w=160 h=92
title: Translate Agent
subtitle: DeepL Pro
status: RUNNING
icon: globe
selected: true
```

节点右上角更多菜单：

```text
three dots x=910 y=202
```

#### Video Enhance

```text
x=420 y=372 w=140 h=92
title: Video Enhance
subtitle: Topaz Video AI
status: OK
icon: purple sparkles
```

#### Frame Interpolation

```text
x=595 y=372 w=165 h=92
title: Frame Interpolation
subtitle: RIFE v4.6
status: OK
icon: grid frames
```

#### Soft Subtitle Mux

```text
x=975 y=286 w=140 h=92
title: Soft Subtitle Mux
subtitle: Burn-In (Soft)
status: WAITING
icon: pink CC
```

#### Output

```text
x=1130 y=286 w=104 h=92
title: Output
subtitle: MP4 (H.265)
status: PENDING
icon: output/export
```

### 7.4 连线拓扑

逻辑：

```text
Video Input
  ├─ Audio Extract -> ASR Subtitle -> Translate Agent
  └─ Video Enhance -> Frame Interpolation
Translate Agent + Frame Interpolation -> Soft Subtitle Mux -> Output
```

连线样式：

- 从 `Video Input` 向右分叉。
- 分叉线应有圆角，不要直角折线。
- 两条分支在 `Soft Subtitle Mux` 左侧合流。
- 合流处用小圆点标识。
- 连线颜色为灰白，选中 Translate Agent 相关连线可略微高亮。

### 7.5 Mini Map

```text
x=234 y=490 w=185 h=116
background: #0D1826
border: #2A3A50
radius: 6
```

内部：

```text
overview area: x=242 y=500 w=140 h=78
controls column: x=390 y=500 w=24 h=78
```

Mini Map 显示缩略节点块，不需要文字。

控件：

```text
pan / fit / zoom icon
size 24x24
gap 6
```

---

## 8. Card Detailed Settings / Inspector 面板

此面板用于展示当前选中 workflow card、execution task、artifact 或 hardware resource 的详细设置。概念图中它位于右侧，但产品实现中它应是可嵌入、可停靠、可浮动的 panel。

### 8.1 区域尺寸

```text
x=1238 y=68 w=362 h=560
background: #0D1826
border: 1px #1E2D40
radius: 8
```

### 8.2 Header

```text
x=1260 y=88
icon: globe 28px
title: Translate Agent
subtitle: DeepL Pro
```

Title：

```text
font 15px / 600
color #F3F7FB
```

Subtitle：

```text
font 11px
color #B7C2D2
```

右上按钮：

```text
Duplicate: x=1470 y=84 w=32 h=32
Delete:    x=1508 y=84 w=32 h=32
Close:     x=1546 y=84 w=32 h=32
```

按钮样式：

```text
background: #111D2C
border: #1E2D40
radius: 6
icon color: #B7C2D2
```

### 8.3 Tabs

```text
x=1238 y=132 w=362 h=42
```

Tabs：

```text
Basic     x=1268 w=70 active
Advanced  x=1370 w=90
Expert    x=1494 w=70
```

Active：

```text
text #F3F7FB
underline y=173 h=2 color #3B82F6
```

Inactive：

```text
text #B7C2D2
```

### 8.4 表单控件区

控件布局：

```text
label x=1260
control x=1398
row height=46
control w=182 h=34
```

起始 y：

```text
y=195
```

表单行：

```text
Source Language        Auto Detect
Target Language        English (US)
Service                DeepL Pro
Formality              Prefer More Natural
Glossary / Terms       travel_terms.txt + folder icon
Preserve Line Breaks   toggle on
Max Characters per Line 42 + slider
Context Window         5 + slider
Use Translation Memory toggle on
```

控件样式：

```text
input background: #172332
border: #223247
radius: 6
text: #F3F7FB
height: 34
```

Toggle：

```text
w=34 h=18
track on: #2563EB
thumb: #FFFFFF
```

Slider：

```text
track: #24364C
active: #60A5FA
thumb: #DCEBFF
```

---

## 9. Queue Monitor Panel

`Queue Monitor` 是可独立嵌入页 / dock panel / floating panel。概念图中它位于左下角，用于保证执行状态始终可扫读；产品实现中它也可以作为 `Queue` 独立页打开。

### 9.1 区域尺寸

```text
x=0 y=638 w=1030 h=362
background: #0D1826
border: 1px #1E2D40
radius: 8
```

### 9.2 Header

```text
title: x=20 y=656
text: Queue Monitor (4)
font: 15px / 600
```

右侧工具：

```text
Pause All:       x=620 y=656
Clear Completed: x=720 y=656
Sort Dropdown:   x=850 y=650 w=130 h=34
Menu Dots:       x=1000 y=656
```

### 9.3 队列项尺寸

```text
item x=14
item w=1000
item h=64
gap=10
radius=8
background: #111D2C
border: #1E2D40
```

队列项 y：

```text
row1 y=690
row2 y=764
row3 y=838
row4 y=912
```

### 9.4 队列项内部布局

缩略图：

```text
x=26 y=row+10 w=92 h=44
radius=5
```

文件名：

```text
x=132 y=row+12
font 13px / 600
```

元信息：

```text
x=132 y=row+36
font 10px muted
```

状态 Badge：

```text
x=335 y=row+22 w=72 h=24
```

进度条：

```text
x=430 y=row+30 w=165 h=6
radius=3
```

百分比：

```text
x=610 y=row+23
```

当前阶段：

```text
label x=635 y=row+14
value x=635 y=row+34
```

硬件：

```text
label x=790 y=row+14
value x=790 y=row+34
```

ETA：

```text
label x=875 y=row+14
value x=875 y=row+34
```

操作按钮：

```text
pause/play x=950 y=row+18 w=32 h=32
more x=995 y=row+22
```

### 9.5 队列示例内容

#### Row 1

```text
thumbnail: mountain lake
filename: 01_Alpine_Lake.mp4
meta: 1080p | 23.976fps | 00:12:45
status: RUNNING
progress: 68%
current stage: Translate Agent
hardware: GPU 0
eta: 00:03:12
```

#### Row 2

```text
thumbnail: city night
filename: 02_City_Night.mp4
meta: 4K | 29.97fps | 00:08:31
status: QUEUED
progress: 0%
current stage: Video Enhance
hardware: GPU 1
eta: 00:09:47
```

#### Row 3

```text
thumbnail: coastline drone
filename: 03_Coastline_Drone.mp4
meta: 4K | 29.97fps | 00:15:09
status: QUEUED
progress: 0%
current stage: Audio Extract
hardware: GPU 0
eta: 00:14:02
```

#### Row 4

```text
thumbnail: forest trail
filename: 04_Forest_Trail.mp4
meta: 1080p | 30fps | 00:11:23
status: PENDING
progress: 0%
current stage: Waiting for resources
hardware: —
eta: —
```

---

## 10. Hardware Resources Panel

`Hardware Resources` 是可独立嵌入页 / dock panel / floating panel。概念图中它位于右下角，用于解释 GPU / CPU / RAM 资源占用；产品实现中它也可以作为 `Hardware Plan` 或 `Runtime` 相关页面的一部分。

### 10.1 区域尺寸

```text
x=1040 y=638 w=560 h=362
background: #0D1826
border: 1px #1E2D40
radius: 8
```

### 10.2 Header

```text
title x=1060 y=656
text: Hardware Resources
font: 15px / 600
```

右侧：

```text
View Details x=1480 y=656
menu dots x=1572 y=656
```

### 10.3 资源项尺寸

```text
item x=1052
item w=530
item h=58
gap=12
radius=8
background: #111D2C
border: #1E2D40
```

y 坐标：

```text
GPU 0:      y=690
GPU 1:      y=760
CPU:        y=830
System RAM: y=900
```

### 10.4 资源项内部布局

Icon box：

```text
x=1068 y=item+12 w=34 h=34
radius=7
background:
  GPU: rgba(57,200,106,0.18)
  CPU/RAM: rgba(59,130,246,0.18)
```

名称：

```text
x=1120 y=item+10
font 13px / 600
```

副标题：

```text
x=1120 y=item+31
font 11px muted
```

使用率区域：

```text
label x=1275 y=item+10
value x=1275 y=item+30
bar x=1275 y=item+42 w=145 h=5
```

Active Tasks：

```text
label x=1470 y=item+10
value x=1470 y=item+32
```

### 10.5 内容示例

```text
GPU 0
NVIDIA RTX 4090
VRAM 17.2 / 24 GB
72%
Active Tasks: 2

GPU 1
NVIDIA RTX 4080
VRAM 12.6 / 16 GB
79%
Active Tasks: 1

CPU
AMD Ryzen 9 7950X
Usage 38%
Active Tasks: 4

System RAM
64 GB DDR5
Usage 21.8 / 64 GB
34%
Active Tasks: —
```

---

## 11. 状态 Badge 规范

### 11.1 尺寸

```text
height: 18px for node cards
height: 24px for queue rows
padding: 8px horizontal
radius: half height
font: 9-10px / 600
letter spacing: 0.2px
```

### 11.2 状态颜色

```text
OK:
  bg rgba(57,200,106,0.18)
  text #39C86A

RUNNING:
  bg rgba(59,130,246,0.18)
  text #60A5FA

WAITING:
  bg rgba(96,165,250,0.14)
  text #93C5FD

PENDING:
  bg rgba(122,135,151,0.16)
  text #9CA8B8

QUEUED:
  bg rgba(59,130,246,0.16)
  text #60A5FA

FAILED:
  bg rgba(248,113,113,0.16)
  text #F87171
```

---

## 12. 交互状态

### 12.1 Workflow Node

默认：

```text
border #2A3A50
background #172332
```

Hover：

```text
border #3D526E
background #1C2B3D
cursor: open hand
```

Dragging：

```text
opacity 0.92
scale 1.02
shadow stronger
z-index top of canvas
```

Selected：

```text
border 2px #3B82F6
show connector handles
right inspector updates
```

Invalid connection：

```text
temporary red line #F87171
show small tooltip near cursor
```

### 12.2 Queue Row

Hover：

```text
background #162337
show more actions
```

Running：

```text
left subtle blue accent line
progress bar animated shimmer very subtle
```

Failed：

```text
border #F87171
show recovery icon/action
```

### 12.3 Hardware Resource

Hover：

```text
background #162337
show “View Tasks” affordance
```

High usage:

```text
bar green under 80%
bar yellow 80%-92%
bar red above 92%
```

---

## 13. 动效规范

所有动画都应短、克制、表达状态。

```text
Card hover: 120ms ease-out
Card select: 140ms ease-out
Card drag lift: 120ms ease-out
Snap to slot: 180ms cubic ease-out
Panel expand/collapse: 180ms
Progress update: 160ms linear/ease
Error pulse: 220ms, one cycle only
```

禁止：

```text
长时间循环发光
大面积模糊动画
频繁 layout 重算
每帧 setStyleSheet
复杂阴影跟随拖拽
```

---

## 14. 视觉层级

从强到弱：

```text
1. Run Workflow 主按钮
2. 选中的 Translate Agent 节点
3. 中央 Workflow Canvas
4. Queue Monitor 当前 running 任务
5. Hardware Resources 使用率
6. Sidebar 导航
7. Inspector 次级参数
```

界面视觉焦点应落在：

```text
中央工作流 + 当前选中节点 + 当前运行队列
```

不要让顶部工具栏抢走过多注意力。

---

## 15. PySide6 实现建议

### 15.1 主布局

推荐结构：

```text
QMainWindow
  TopBar custom QWidget
  CollapsibleSidebar
  WorkflowCanvas as central widget
  Dock panels
    Card Detailed Settings / Inspector
    Queue Monitor
    Hardware Resources
    Logs
    Artifact Browser
```

关键规则：

```text
Workflow Canvas 是 central widget 的默认主舞台
Queue / Hardware / Inspector 是 QDockWidget / panel
panel 可嵌入、可浮动、可隐藏、可 tabified
WorkspaceManager 保存和恢复布局
```

首版可以先提供少量固定 preset，但不要把 Queue Monitor、Hardware Resources 或 Card Detailed Settings 写死为不可移动区域。`QMainWindow.saveState()` / `restoreState()` 与 `WorkspaceManager` 是布局持久化方向。

### 15.2 Workflow Canvas

推荐：

```text
QGraphicsView
QGraphicsScene
WorkflowNodeItem : QGraphicsObject / QGraphicsItem
WorkflowEdgeItem : QGraphicsPathItem
MiniMapView : QGraphicsView
```

关键实现点：

```text
节点 item 自绘背景、边框、状态 badge
连线使用 QPainterPath cubicTo
拖拽只移动 item，不触发主布局
连接点随节点位置刷新
选中节点发 signal 更新 Inspector
```

### 15.3 Queue Monitor

推荐：

```text
QListView + custom delegate
或者
QScrollArea + custom QueueRowWidget
```

MVP 阶段可用 `QScrollArea + QWidget rows`，后期任务多再切 `QListView`。

### 15.4 Hardware Resources

推荐：

```text
QWidget + QVBoxLayout
HardwareResourceCard custom QWidget
```

使用自绘进度条，不要用默认 `QProgressBar`，默认样式太普通。

---

## 16. 响应式策略

主尺寸低于 `1400px`：

```text
Card Detailed Settings / Inspector 可折叠
Hardware Resources 可合并为资源抽屉
Queue Monitor 保持可见
```

主尺寸高于 `1800px`：

```text
中央画布扩展
Inspector 保持 360-400px
Queue Monitor 可显示更多行
Hardware 可显示更多设备
```

最小建议窗口：

```text
1366 × 768
```

在该尺寸下：

```text
Sidebar 缩窄为 icon-only
Inspector 默认折叠
Queue Monitor 高度压缩
```

---

## 17. 设计复刻检查清单

绘制完成后检查：

```text
[ ] 一眼能看出是专业工作站
[ ] 左侧导航、中央画布、右侧参数、底部队列、硬件资源都清楚
[ ] 中央节点流程表达了视频输入分支、字幕分支、视频增强分支、合流输出
[ ] Translate Agent 处于选中状态，Card Detailed Settings / Inspector 对应它
[ ] Queue Monitor 显示至少 4 个任务
[ ] Hardware Resources 显示至少 GPU 0 / GPU 1 / CPU / RAM
[ ] 状态标签清楚：OK / RUNNING / WAITING / PENDING / QUEUED
[ ] 深色主题克制，不花哨
[ ] 没有大面积空白
[ ] 没有过多营销式视觉元素
[ ] 所有文字短而可信
[ ] 视觉焦点在 Workflow Canvas 和运行任务上
```

---

## 18. 一句话设计目标

```text
Atelier 的主界面应该像一个冷静、专业、可信赖的 AI 视频生产控制台：
用户设计流程，软件规划执行，队列稳定运行，硬件状态可解释，失败可以恢复。
```
