# Atelier Artifact Lifecycle Spec

> 状态：规划中，尚未实现。本文档定义 artifact 从计划、生成、验证、缓存、复用、导出、清理到恢复的完整生命周期。已纳入 OCR Recognition 的 `ocr_text_track`、sampled frames 和 fusion metadata。

## 1. Artifact 类型

建议：

```text
video
audio
subtitle
image_seq
metadata
ocr_text_track
cache
diagnostic
```

与当前 `DATABASE_SCHEMA.md` 对齐的首版 artifact type 为 `video`、`audio`、`subtitle`、`ocr_text_track`、`image_seq`、`metadata`、`cache`。`diagnostic` 可先作为 `metadata` artifact 的 `metadata.kind` 表达，等实现需要后再决定是否进入数据库枚举。

若实现阶段暂不扩 DB enum，可用：

```text
artifact_type = metadata
metadata.kind = ocr_text_track
```

## 2. Artifact 状态

```text
planned
staging
valid
partial
suspect
final_output
cache_reused
deleted
orphaned
```

## 3. 生命周期

```text
output slot
  -> .part
  -> atomic rename
  -> artifact event
  -> Scheduler validates
  -> artifacts row
  -> task_artifacts link
  -> downstream input
  -> optional cache
  -> final output
  -> retention cleanup
```

## 4. Worker 写入规则

```text
Worker writes task_work_dir/file.part
  -> flush/close
  -> compute hash if feasible
  -> rename file.part -> file
  -> emit artifact event
```

Scheduler 验证 path traversal、exists、hash、metadata 后写 DB。

## 5. OCR Artifact

```text
ocr_track.json
artifact_type: ocr_text_track or metadata(kind=ocr_text_track)
metadata:
  backend
  model_id
  frames_sampled
  languages
  sampling_strategy
  confidence_stats
```

OCR frame cache：

```text
sampled_frames/
role: internal_cache or diagnostic
retention: short
```

规则：debug overlay 默认关闭；OCR partial track 可保留但标记 partial。

## 6. ASR Artifact

```text
raw_asr.srt
raw_asr.json sidecar
artifact_type: subtitle
metadata:
  source=asr
  language
  model_id
  backend
  segments
```

## 7. Translate Fusion Artifact

```text
translated.srt
translation_fusion.json
metadata:
  used_asr
  used_ocr
  translation_source: asr_only | ocr_only | asr_ocr_fusion
  conflict_count
  model_id/provider
```

OCR-only 输出必须标记 incomplete。

## 8. Image Sequence

用于 Video Enhance、Frame Interpolation、可选 OCR sampled frames。

规则：大中间帧默认不作为 final artifact；清理前检查下游和 cache 引用。

## 9. Cache

OCR cache key 额外包含：

```text
sampling_strategy
sample_interval_sec
crop_region
languages
min_confidence
backend/model
```

Video enhance cache key 额外包含：scale、tile_size、model_id、fp32、tta/uhd。

## 10. Final Output

```text
valid staged artifact
  -> user output path
  -> conflict check
  -> copy/move
  -> verify
  -> role=final_output
```

禁止 Worker 直接写最终目录或静默覆盖。

## 11. Startup Recovery

```text
scan task dirs
find .part
find artifact rows missing files
find files without rows
find running tasks with dead worker
mark interrupted / suspect / orphaned
```

## 12. 测试要求

```text
valid artifact write
hash mismatch suspect
OCR partial track
ASR + OCR fusion metadata
final output conflict
cache hit without worker
cleanup sampled frames
startup orphan recovery
path traversal rejection
```
