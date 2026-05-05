# Atelier Documentation Alignment Notes

> 状态：规划中。本文档回答：新增 `OCR Recognition` 卡片后，是否需要让其他文档对齐？答案是：**需要**。否则 Workflow、ExecutionPlan、Scheduler、Adapter、Artifact、UI 会出现语义断层。

## 1. 新增卡片

```text
UI card: OCR Recognition
node_type: ocr.recognition
output: ocr_text_track or metadata(kind=ocr_text_track)
```

## 2. 必须更新的既有文档

### WORKFLOW_NODE_SPEC.md

新增 `ocr.recognition`：input video，output ocr_text_track，params 包括 backend、languages、sampling_strategy、max_frames、crop_region、min_confidence。

更新 `translate.llm`：输入至少包含 ASR 或 OCR 一路；ASR+OCR 时 fusion；OCR-only 时 draft/incomplete。

### EXECUTION_PLAN_SPEC.md

新增 OCR task；Translate Agent 依赖 ASR/OCR 变成可降级依赖。需要表达：ASR failed + OCR valid、OCR failed + ASR valid、两者都 failed。

### WORKER_PROTOCOL.md

新增 `OCRRecognitionAdapter` 和 `ocr_text_track` artifact 示例。

### DATABASE_SCHEMA.md

当前规划选择：在 `DATABASE_SCHEMA.md` 中增加 `ocr_text_track` artifact type；如果实现阶段暂不扩展数据库 enum，可临时使用 metadata artifact + `metadata.kind=ocr_text_track` 作为兼容降级。

### RUNTIME_ENVIRONMENT_SPEC.md

新增 PaddleOCR/Tesseract runtime component、OCR model assets、language packs。

### BATCH_PIPELINE_SCHEDULING_SPEC.md

新增 OCR stage。OCR 与 ASR 可并行，但受 Translate backlog、frame sampling、disk policy 限制。

### HARDWARE_SCHEDULING_PAGE_SPEC.md

新增 OCR backlog row、OCR lane block、OCR waiting reasons。

### SCHEDULING_PRESETS_SPEC.md

更新 Subtitle First、Low VRAM Safe、Local LLM Translation、Remote API Translation，加入 OCR 权重、OCR model profile、max_frames。

### ARTIFACT_LIFECYCLE_SPEC.md

新增 ocr_track.json、sampled_frames、debug_overlay、fusion metadata。

### UI_STATE_SPEC.md

新增 OCR UI states：ocr_sampling_frames、ocr_recognizing、ocr_failed_asr_can_continue、ocr_only_draft。

### ONBOARDING_RUNTIME_SETUP_SPEC.md

新增 OCR setup、language packs、skip OCR、ASR-only continue。

## 3. 图与 UI 需要更新

```text
Workflow concept image: add OCR Recognition parallel to ASR branch
Hardware Scheduling page: add OCR stage row and OCR task blocks
Translate Agent inspector: show ASR + OCR fusion inputs
```

## 4. 命名统一

使用：

```text
OCR Recognition
ocr.recognition
ocr_text_track
ASR + OCR Fusion Translation
```

避免混用：ORC、screen scan、visual subtitle reader。

## 5. 设计风险

```text
OCR 如果塞进 ASR，会污染音频/视觉边界
Translate 如果硬依赖 ASR+OCR 两者，会降低容错
OCR 如果默认全帧扫描，会造成磁盘/显存/耗时灾难
```

推荐：OCR 独立卡片，Translate Agent 支持 optional/fusion 输入，OCR 抽帧默认有界。
