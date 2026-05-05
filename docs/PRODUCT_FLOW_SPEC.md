# Atelier Product Flow Spec

> 状态：规划中，尚未实现。本文档定义 Atelier 首版产品主流程：从创建项目、导入视频、选择内置 Workflow、生成 ExecutionPlan、执行批量任务、失败恢复到最终导出。验收标准放在 `MVP_ACCEPTANCE_SPEC.md`。

## 1. 产品定位

Atelier 是本地优先的 AI 视频工作流工作站，不是单按钮字幕工具。

```text
导入批量视频
  -> 选择/调整内置 Workflow
  -> 生成 ExecutionPlan
  -> Scheduler 做硬件调度
  -> Worker 执行内置卡片
  -> 失败可恢复
  -> artifact 可追踪
  -> 最终导出可控
```

## 2. 首版内置卡片

```text
Input / Probe:
  Video Input
  Audio Input
  Subtitle Input
  Metadata Probe

Audio / Speech:
  Audio Extract
  Audio Enhance
  ASR Subtitle

Visual Text:
  OCR Recognition

Subtitle / Agent:
  Subtitle Normalize
  Translate Agent
  Subtitle Review

Video:
  Video Enhance
  Frame Interpolation

Compose / Output:
  Soft Subtitle Mux
  Burn Subtitle
  Output Export
```

推荐 `node_type`：

```text
input.video
input.audio
input.subtitle
metadata.probe
media.audio_extract
audio.enhance
asr.whisper
ocr.recognition
subtitle.normalize
translate.llm
subtitle.review
enhance.realesrgan
enhance.rife
compose.mux_subtitle
compose.burn_subtitle
compose.mux_audio
output.export
```

## 3. 主 Workflow

### 3.1 基础字幕翻译

```text
Video Input
  -> Metadata Probe
  -> Audio Extract
  -> ASR Subtitle
  -> Subtitle Normalize
  -> Translate Agent
  -> Soft Subtitle Mux
  -> Output Export
```

### 3.2 ASR + OCR 综合翻译

OCR Recognition 用于识别画面中的硬字幕、UI 文本、歌词、标注、弹幕等视觉文字。它不替代 ASR，而是给 Translate Agent 提供第二路证据。

```text
Video Input
  -> Metadata Probe
  -> Audio Extract
      -> Audio Enhance
      -> ASR Subtitle
  -> OCR Recognition

ASR Subtitle + OCR Recognition
  -> Subtitle Normalize
  -> Translate Agent
  -> Subtitle Review
  -> Soft Subtitle Mux / Burn Subtitle
  -> Output Export
```

规则：

- ASR 输出 `asr_subtitle`，负责语音内容与主时间轴。
- OCR 输出 `ocr_text_track`，负责画面文本与硬字幕线索。
- Translate Agent 同时读取 ASR 和 OCR 时，执行 `asr_ocr_fusion`。
- OCR 缺失时可降级 ASR-only。
- ASR 缺失但 OCR 有效时，可生成 OCR-only draft，必须标记 incomplete。

### 3.3 全流程视频增强

```text
Video Input
  -> Video Enhance
  -> Frame Interpolation
  -> Soft Subtitle Mux / Burn Subtitle
  -> Output Export
```

视频支路与字幕支路默认并行，最终在 Compose/Output 阶段汇合。

## 4. 产品主路径

### Flow A：首次进入

```text
Open Atelier
  -> load settings
  -> open/create SQLite
  -> check runtime/model/hardware
  -> show Start screen or recent project
```

### Flow B：创建项目

```text
New Project
  -> choose name/root
  -> create project record
  -> create project data dirs
  -> open Workflow workspace
```

### Flow C：导入批量视频

```text
Import videos
  -> create input media records
  -> run Metadata Probe
  -> show duration/codec/resolution/audio stream summary
```

### Flow D：选择 Workflow Preset

推荐内置 preset：

```text
Subtitle Translation
ASR + OCR Translation
Video Enhance + Subtitle
Full Pipeline
```

### Flow E：生成 ExecutionPlan

```text
Validate Workflow
  -> node/edge/param validation
  -> runtime/model check
  -> per-video DAG expansion
  -> conflict detection
  -> ExecutionPlan summary
```

### Flow F：执行与调度

```text
Run Workflow
  -> Scheduler claims dependency-ready tasks
  -> RuntimeManager resolves RuntimeBinding
  -> Scheduler writes ResourceBinding/resource_locks
  -> Worker emits events
  -> Queue and Hardware Scheduling Page update
```

批量视频按 task DAG 流水线执行，不按整条视频逐个串行。

### Flow G：ASR + OCR + Translate Agent

```text
V01 ASR completed
V01 OCR completed
  -> V01 Translate runnable
  -> prompt/context includes:
       ASR timed segments
       OCR text track
       OCR bbox/time windows
       glossary/style rules
```

Translate 输出：

```text
translated subtitle artifact
fusion metadata:
  used_asr
  used_ocr
  translation_source
  conflict_count
  agent_notes
```

### Flow H：失败恢复与降级

```text
OCR failed + ASR valid -> allow ASR-only translation
ASR failed + OCR valid -> allow OCR-only draft
ASR/OCR both failed -> Translate blocked
```

### Flow I：最终导出

```text
Worker creates staged artifact
  -> Scheduler validates
  -> ArtifactFinalizer copies/moves to user path
  -> no silent overwrite
  -> final_output link recorded
```

## 5. 需要同步的文档

新增 OCR 后必须同步：`WORKFLOW_NODE_SPEC`、`EXECUTION_PLAN_SPEC`、`WORKER_PROTOCOL`、`DATABASE_SCHEMA`、`RUNTIME_ENVIRONMENT_SPEC`、`BATCH_PIPELINE_SCHEDULING_SPEC`、`HARDWARE_SCHEDULING_PAGE_SPEC`、`SCHEDULING_PRESETS_SPEC`、`ARTIFACT_LIFECYCLE_SPEC`、`UI_STATE_SPEC`。详见 `DOC_ALIGNMENT_NOTES.md`。
