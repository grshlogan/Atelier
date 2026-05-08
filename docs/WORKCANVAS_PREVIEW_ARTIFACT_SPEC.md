# WorkCanvas Preview Artifact Spec

## Objective

定义 Atelier WorkCanvas 中节点预览、缩略图和 GUI 绘制的边界，避免未来节点卡片因为在 GUI 线程中读媒体、解码、缩放或生成缩略图而卡顿。

本文件只约束 GUI / WorkCanvas / preview artifact 的产品边界，不改变 Scheduler、Worker、RuntimeManager、Storage 或 adapter 职责。

## Reference Lessons

Atelier 可以借鉴 ComfyUI 的三个结构性优点：

- Workflow 是可序列化的节点图，而不是一组散落按钮。
- 节点通过输入、输出和类型契约组织，预览节点与最终保存节点可以分离。
- 执行与界面分离，前端显示图和预览，后端负责实际节点执行、状态消息和产物。

参考来源：

- [ComfyUI workflow core concept](https://docs.comfy.org/development/core-concepts/workflow)
- [ComfyUI nodes core concept](https://docs.comfy.org/development/core-concepts/nodes)
- [ComfyUI custom nodes](https://docs.comfy.org/development/core-concepts/custom-nodes)
- [ComfyUI server messages](https://docs.comfy.org/development/comfyui-server/comms_messages)

Atelier 不照搬 ComfyUI 的自由大图复杂度。Atelier 的默认 Workflow Canvas 仍是卡片式轻节点系统，Execution Canvas 和 Queue Monitor 负责硬件执行、队列、恢复和产物状态。

## Core Decision

WorkCanvas 只渲染 GUI view model 和 preview artifact 引用。GUI 不生成 preview artifact。

```text
media path / upstream artifact
  -> Worker / adapter / preview generator
  -> preview artifact / thumbnail cache
  -> GUI snapshot / view model
  -> WorkCanvas draws cached pixmap or vector fallback
```

禁止路线：

```text
WorkCanvas paint()
  -> read media
  -> decode video frame
  -> scale image
  -> mask rounded thumbnail
  -> draw
```

## Preview Artifact

`preview artifact` 是给 GUI 快速显示用的中间产物，不等同于最终输出。

首版建议字段：

- `artifact_id`
- `source_artifact_id` 或 `source_path_ref`
- `preview_kind`，例如 `thumbnail`, `contact_sheet`, `waveform`, `subtitle_preview`
- `pixel_size`
- `cache_key`
- `file_path_ref`
- `content_hash`
- `generated_by_task_id`
- `created_at`

GUI 只能读取 snapshot / view model 中暴露的 preview 引用。GUI 不直接读取任意用户路径，也不直接从视频抽帧。

## Thumbnail Policy

视频输入节点缩略图是最容易卡的部分，因此必须按以下规则处理：

- 缩略图由后台边界生成，不能在 WorkCanvas 绘制路径中生成。
- WorkCanvas 只接收适配当前显示尺寸的缓存图，例如 72x46、124x70、240x140。
- 圆角裁剪、叠层、播放三角、暗角等复杂效果应预合成或缓存为最终 `QPixmap`。
- 画布缩放时使用现有尺寸缓存，必要时延迟请求更合适尺寸，不随每帧缩放重采样。
- 缩小时使用 LOD 简化：只显示图标、标题、状态和数量；放大后再显示缩略图和详情。

## Vector Node Item Direction

控件画板中的 QWidget 版节点卡片只用于审美、布局和参数打磨。真实 WorkCanvas 路线应转译为更轻的节点 item：

- `QGraphicsItem` / `QGraphicsObject` 承载节点。
- `paint()` 绘制背景、边框、文字、胶囊、端口、按钮和 cached thumbnail。
- `boundingRect()` 返回稳定尺寸。
- `shape()` 只覆盖真实命中区域。
- 只对受影响节点和连线调用 `update()`。
- 缩放时通过 LOD 切换信息密度。

## Workbench Preview Area

`AtelierUI` 控件画板中的 WorkCanvas 预览区是 dev-only 承载区：

- 用于观察候选节点卡片在画布背景中的比例、边距、发光、端口和可读性。
- 用于记录候选卡片未来转译为矢量 item 的约束。
- 用于暴露 preview / thumbnail cache 策略，不代表产品 WorkCanvas 已实现。
- 不运行 workflow，不生成缩略图，不执行 FFmpeg，不访问 SQLite。

首阶段 object boundary：

```text
component-workbench-workcanvas-preview
  -> component-workbench-workcanvas-stage
      -> component-workbench-video-input-card
```

## Non-Goals

- 不把 ComfyUI 自由节点图作为 Atelier 默认交互。
- 不引入 Vulkan、Qt Quick、QML 或 Web Canvas。
- 不把 QWidget 候选卡片直接作为真实 WorkCanvas 大量节点的最终方案。
- 不在 GUI 线程中抽帧、解码、转码或读取任意用户媒体。
- 不让 GUI 绕过 Scheduler、RuntimeManager、Worker 或 Storage。

## First Implementation Signal

第一阶段完成后：

- 控件画板有 WorkCanvas 预览区。
- `VideoInputCardCandidate` 在该区域中显示。
- 预览区明确声明 `thumbnail_policy = cached-preview-artifact-only`。
- 文档和测试都记录 GUI 不生成缩略图、不执行 workflow 的边界。

当前新增矢量路线候选：

- `VideoInputCollapsedNodeCardItem`：内缩态，固定 300 px × 200 px，使用 `QGraphicsObject` / `paint()`。
- 该 item 只绘制矢量背景、文字、状态胶囊、摘要指标和轻量矢量 thumbnail fallback；真实缩略图仍必须来自 preview artifact / thumbnail cache。
- 内缩态展开 affordance 绑定缩略图堆叠：鼠标接近缩略图热区时淡入四角展开线条，离开扩展热区后淡回缩略图，不占用底部摘要指标区域。
- 画板中的 `component-workbench-video-input-vector-preview` 仅用于审查该 item 的 WorkCanvas 适配方向。
