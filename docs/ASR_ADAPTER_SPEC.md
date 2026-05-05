# Atelier ASR Adapter Spec

> 状态：规划中，尚未实现。本文档定义 ASR Subtitle 卡片。OCR 是独立卡片，见 `OCR_ADAPTER_SPEC.md`。

## 1. 目标

ASR Adapter 将音频 artifact 转换为带时间轴的字幕 artifact。

```text
node_type: asr.whisper
UI card: ASR Subtitle
```

## 2. Backend

首版候选：

```text
faster-whisper
whisper.cpp
remote transcription API later
```

## 3. 输入

```python
class ASRInput(BaseModel):
    audio_artifact_id: str
    source_language_hint: str | None = None
    expected_subtitle_format: Literal['srt','vtt','json'] = 'srt'
```

## 4. 参数

```python
class ASRParams(BaseModel):
    model_id: str
    backend: Literal['faster-whisper','whisper.cpp']
    language: str | None = None
    beam_size: int = 5
    vad_filter: bool = True
    output_format: Literal['srt','vtt','json'] = 'srt'
    word_timestamps: bool = False
    compute_type: str | None = None
```

## 5. Runtime / Resource

```text
components: faster-whisper or whisper.cpp
model_ids: whisper model
capabilities: asr + cuda/vulkan/cpu
```

Resource：小模型可 shared，大模型可 exclusive；device 由 Scheduler 的 ResourceBinding 决定。

## 6. 输出 Artifact

```text
artifact_type: subtitle
path: raw_asr.srt / raw_asr.vtt / raw_asr.json
metadata:
  source: asr
  language
  model_id
  backend
  duration_sec
  segments
  confidence_stats
```

建议保存 JSON sidecar，供 Translate Agent 使用。

## 7. 与 OCR 的关系

ASR 只处理音频，不读取视频帧。Translate Agent 读取：

```text
asr_subtitle + ocr_text_track
```

默认以 ASR 时间轴作为字幕主线，OCR 用于纠错/补充画面文字。

## 8. 错误映射

```text
INPUT_MISSING
INPUT_CORRUPT
MODEL_MISSING
RUNTIME_MISSING
OOM
CANCELLED
TIMEOUT
INTERNAL
```

## 9. 测试要求

```text
missing audio
corrupt audio
model missing
language auto detect
srt/json sidecar output
cancel during inference
OOM mapping
resource_binding respected
ASR + OCR translation context build
```

## 10. 参考资料

- faster-whisper: https://github.com/SYSTRAN/faster-whisper
- OpenAI Speech to text: https://platform.openai.com/docs/guides/speech-to-text
- Whisper: https://github.com/openai/whisper
