# Atelier UI State Spec

> 状态：规划中，尚未实现。本文档定义 Atelier UI 状态机，并加入 OCR Recognition 后的新状态。它负责“什么时候显示什么状态”，绘制细节仍由 GUI 绘制规格负责。

## 1. 状态层级

```text
AppState
ProjectState
WorkflowState
ExecutionPlanState
JobState
TaskState
RuntimeState
ArtifactState
PageState
```

## 2. AppState

```text
booting
ready_no_project
ready_project_open
startup_recovery
degraded_runtime
fatal_error
closing
```

## 3. WorkflowState

```text
empty
editing
validating
valid
invalid
locked_by_running_job
```

OCR 后验证规则：

```text
ocr.recognition output 是否连接到 translate.llm 或被显式禁用
translate.llm 至少有 ASR 或 OCR 一路输入
OCR-only 输出是否标记 draft/incomplete
```

## 4. ExecutionPlanState

```text
not_generated
generating
draft
validated
scheduled
running
completed
failed
cancelled
```

`draft` 应显示：runtime missing、OCR model missing、Translate lacks recognition input、hardware conflict。

## 5. TaskState

```text
pending
queued
running
completed
failed
retry_pending
skipped
cancelled
paused_by_backpressure
blocked
```

Waiting reason：

```text
waiting_dependency
waiting_hardware
waiting_runtime
waiting_api_slot
waiting_disk_bandwidth
waiting_credential
paused_by_backpressure
blocked_by_failed_upstream
```

OCR-specific：

```text
ocr_disabled
ocr_sampling_frames
ocr_recognizing
ocr_partial
ocr_failed_asr_can_continue
ocr_only_draft
```

## 6. RuntimeState

```text
unknown
missing
installing
ready
broken
disabled
incompatible
update_available
```

OCR missing 时显示：Install OCR Runtime、Import OCR Model、Disable OCR、Continue ASR-only。

## 7. ArtifactState

```text
planned
staging
valid
partial
suspect
final_output
deleted
orphaned
```

OCR artifact 显示：frames sampled、confidence、languages、used by Translate Agent。

## 8. Button Enablement

### Run Workflow

需要 project open、workflow valid、input media present、plan valid/generatable、blocking runtime issues resolved or degradable。

### Continue ASR-only

需要 OCR failed/missing、ASR valid、Translate Agent 可 ASR-only、用户确认质量 warning。

### Continue OCR-only Draft

需要 ASR failed/missing、OCR valid、workflow policy allows draft、用户确认 incomplete output。

## 9. Failure Panels

OCR OOM：降低 sampled frames、crop subtitle region、use mobile OCR model、switch CPU、continue ASR-only。

ASR failed + OCR valid：retry ASR、continue OCR-only draft、skip video。

ASR/OCR conflict：review conflicts、prefer ASR、prefer OCR for screen text、ask Agent to resolve。

## 10. 测试要求

```text
workflow with ASR only
workflow with OCR only
workflow with ASR + OCR
OCR runtime missing
OCR failed ASR continue
ASR failed OCR draft
Translate blocked no recognition input
Hardware Scheduling waiting reasons
startup recovery partial OCR
```
