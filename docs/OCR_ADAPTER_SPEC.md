# Atelier OCR Adapter Spec

> 状态：规划中，尚未实现。本文档定义 OCR Recognition 卡片。OCR 识别画面文字、硬字幕、UI 文本、歌词、标注、弹幕等视觉文本，并与 ASR 一起供 Translate Agent 综合翻译。

## 1. 目标

```text
node_type: ocr.recognition
UI card: OCR Recognition
```

核心目标：

```text
从视频帧识别视觉文本
生成带时间窗口的 OCR text track
为 Translate Agent 提供 ASR 之外的视觉上下文
OCR 失败时 ASR-only 可继续
```

非目标：

```text
不替代 ASR
不默认全帧 OCR 长视频
不直接生成最终字幕时间轴
不直接把 OCR 文本烧进视频
```

## 2. Backend

首版候选：

```text
PaddleOCR
Tesseract
```

建议：PaddleOCR 作为多语言/CJK 视频文字主 backend，Tesseract 作为轻量本地 fallback。

## 3. 输入

```python
class OCRInput(BaseModel):
    video_artifact_id: str
    metadata_artifact_id: str | None = None
```

## 4. 参数

```python
class OCRParams(BaseModel):
    backend: Literal['paddleocr','tesseract']
    model_id: str | None = None
    languages: list[str] = []
    sampling_strategy: Literal['fixed_interval','scene_change','subtitle_region','keyframes'] = 'subtitle_region'
    sample_interval_sec: float = 1.0
    max_frames: int = 2000
    crop_region: Rect | None = None
    min_confidence: float = 0.5
    merge_nearby_boxes: bool = True
    deduplicate_repeated_text: bool = True
    output_debug_images: bool = False
```

## 5. 抽帧策略

OCR 不能默认每帧识别。

推荐优先级：

```text
subtitle_region -> scene_change -> fixed_interval -> keyframes
```

必须限制：

```text
max_frames
max_intermediate_bytes
max_ocr_runtime_minutes
```

## 6. Runtime / Resource

```text
components: paddleocr or tesseract, ffmpeg for frame extraction
model_ids: OCR detection/recognition model
capabilities: ocr + cpu/gpu
```

Resource：默认 CPU/any；重型 PaddleOCR 可 GPU；是否 exclusive 由 Scheduler 决定。

## 7. 输出 Artifact

推荐新增：

```text
artifact_type: ocr_text_track
```

若 DB enum 暂不扩展：

```text
artifact_type: metadata
metadata.kind = ocr_text_track
```

文件：

```text
ocr_track.json
```

Schema：

```python
class OCRTextTrack(BaseModel):
    source: Literal['ocr'] = 'ocr'
    video_artifact_id: str
    backend: str
    model_id: str | None
    language_hints: list[str]
    frames_sampled: int
    items: list[OCRTextItem]

class OCRTextItem(BaseModel):
    start_time: float
    end_time: float | None
    text: str
    confidence: float | None
    bbox: list[float] | None
    frame_index: int | None
    region: str | None = None
```

## 8. 与 ASR/Translate Agent 的关系

```text
ASR: 语音内容和主时间轴
OCR: 画面文字、硬字幕、UI/标注、歌词
Translate Agent: 融合两者，默认以 ASR 时间轴为主
```

融合规则：

```text
ASR + OCR -> fusion
ASR only -> ASR-only
OCR only -> OCR-only draft, mark incomplete
ASR/OCR conflict -> preserve agent_notes/conflict metadata
```

## 9. Progress

```text
stage=frame_extract
stage=text_detection
stage=text_recognition
stage=deduplicate
stage=write_track
unit=frames/ocr_regions
```

## 10. Artifact / Cache

```text
ocr_track.json      valid artifact
sampled_frames/     short-retention internal cache
debug_overlay/      optional diagnostic artifact
```

Cache key 包含：视频 hash、sampling params、crop region、languages、backend/model。

## 11. UI 状态

```text
OCR disabled
OCR sampling frames
OCR recognizing
OCR partial
OCR failed but ASR can continue
OCR-only draft
OCR used by Translate Agent
```

## 12. 测试要求

```text
fixed interval sampling
subtitle region crop
max_frames limit
OCR model missing
OCR runtime missing
OOM mapping
partial OCR track
ASR + OCR fusion context
ASR-only degradation
OCR-only draft warning
debug images off by default
```

## 13. 参考资料

- PaddleOCR Documentation: https://www.paddleocr.ai/
- PaddleOCR General OCR Pipeline: https://www.paddleocr.ai/main/en/version3.x/pipeline_usage/OCR.html
- Tesseract OCR: https://tesseractocr.org/
