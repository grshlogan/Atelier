# Atelier Translate Agent Spec

> 建议路径：`docs/TRANSLATE_AGENT_SPEC.md`
> 状态：规划中，尚未实现。
> 面向对象：Codex / Claude Code / 后续实现者。
> 本文档定义 Atelier 的 `Translate Agent` 卡片如何设计、拆分、实现、测试和接入现有 `WorkflowGraph -> ExecutionPlan -> Scheduler -> Worker -> Artifact` 架构。

---

## 1. 结论

`Translate Agent` 不是普通聊天机器人，也不是简单的“把 SRT 丢给大模型翻译”。

它应该是一个 **结构化字幕翻译执行器**：

```text
ASR Subtitle
OCR Recognition
Glossary
Style Profile
Timeline Constraints
Provider Runtime
  -> Translate Agent
  -> translated subtitle
  -> fusion metadata
  -> warnings / conflicts
```

核心定位：

```text
Translate Agent
  = Recognition Source Fusion
  + Subtitle Translation
  + Timeline Preservation
  + Glossary / Style Control
  + Structured Output Validation
  + Artifact Generation
```

它必须作为 Worker Adapter 被 Scheduler 管理：

```text
ExecutionTask
  -> RuntimeBinding
  -> ResourceBinding
  -> TranslateAgentAdapter
  -> ProviderBackend
  -> WorkerEvent
  -> Artifact
```

---

## 2. 设计原则

### 2.1 必须做

```text
支持 ASR-only
支持 OCR-only draft
支持 ASR + OCR fusion
以结构化 JSON 作为 LLM 输出事实源
由 Atelier 自己重建 SRT/VTT/ASS
支持 glossary / terminology
支持上下文窗口
支持 chunk / retry / repair
支持 provider rate limit
支持 local LLM 和 remote API
失败可恢复，降级可解释
```

### 2.2 禁止做

```text
不要让 LLM 直接输出最终 SRT 作为唯一事实源
不要把 OCR 塞进 ASR adapter
不要让 Translate Agent 直接读 SQLite
不要让 Translate Agent 自己决定使用哪张 GPU
不要绕过 RuntimeManager 读取模型或 API key
不要把 API key / 字幕正文泄露到可分享 diagnostics
不要把 OCR-only 输出伪装成完整语音字幕翻译
不要让 GUI 按钮直接调用 provider API
```

---

## 3. 参考项目与可借鉴点

### 3.1 Subtitle Edit

Subtitle Edit 是成熟的开源字幕编辑器，支持大量字幕格式、Speech to Text、自动翻译、OCR、错误修复、拼写检查、烧录字幕和批量转换。

Atelier 可借鉴：

```text
字幕格式处理
OCR / ASR / 翻译并列存在
翻译后仍需错误检查和人工 review
时间轴与字幕内容必须一起管理
批量处理是核心能力
```

参考：

```text
https://subtitleedit.github.io/subtitleedit/overview.html
```

### 3.2 faster-whisper / Whisper 系列

faster-whisper 是基于 CTranslate2 的 Whisper 重实现，强调更快推理、更低内存占用和量化能力。

Atelier 可借鉴：

```text
ASR 输出不是普通文本，而是 timed segments
ASR artifact 应保存 SRT/VTT/JSON sidecar
Translate Agent 默认以 ASR timeline 为主轴
ASR backend 的模型、量化、设备绑定会影响 Scheduler
```

参考：

```text
https://github.com/SYSTRAN/faster-whisper
```

### 3.3 OpenAI Structured Outputs / JSON Schema

Structured Outputs 可以让模型输出符合指定 JSON Schema，减少漏字段、枚举乱写、格式漂移等问题。

Atelier 可借鉴：

```text
LLM 翻译结果必须走 schema
不要让模型自由输出 SRT
ResultValidator 必须验证 schema
失败 chunk 可 retry / repair
```

参考：

```text
https://platform.openai.com/docs/guides/structured-outputs
```

### 3.4 DeepL Glossary

DeepL glossary 支持为词语和短语指定翻译映射，用于术语一致性。

Atelier 可借鉴：

```text
Glossary 是一等输入
术语表应独立 artifact 或 project resource
Translate Agent 应记录 glossary_applied
LLM provider 和传统翻译 provider 都应有术语策略
```

参考：

```text
https://developers.deepl.com/api-reference/multilingual-glossaries
```

### 3.5 OCR 系统

PaddleOCR / Tesseract 一类 OCR 工具可输出文本、置信度、位置、布局等信息。

Atelier 可借鉴：

```text
OCR 输出应是 ocr_text_track
OCR 不替代 ASR
OCR 给 Translate Agent 提供视觉上下文
OCR-only 输出必须标记 draft / incomplete
```

参考：

```text
https://www.paddleocr.ai/
https://tesseractocr.org/
```

---

## 4. 相关内置卡片

`Translate Agent` 直接或间接关联这些内置卡片：

```text
Video Input
Audio Input
Subtitle Input
Metadata Probe
Audio Extract
Audio Enhance
ASR Subtitle
OCR Recognition
Subtitle Normalize
Translate Agent
Subtitle Review
Video Enhance
Frame Interpolation
Soft Subtitle Mux
Burn Subtitle
Output Export
```

推荐 node_type：

```text
asr.whisper
ocr.recognition
media.audio_extract
subtitle.normalize
translate.llm
subtitle.review
input.video
input.audio
input.subtitle
compose.mux_subtitle
compose.burn_subtitle
compose.mux_audio
output.export
```

---

## 5. Recognition Modes

Translate Agent 必须支持三种识别模式。

### 5.1 ASR-only

适合：

```text
口播
访谈
教程
播客转视频
无硬字幕视频
```

流程：

```text
Audio Extract
  -> ASR Subtitle
  -> Subtitle Normalize
  -> Translate Agent
```

输出：

```text
translated.srt
translation_fusion.json:
  mode = ASR_ONLY
  used_asr = true
  used_ocr = false
```

### 5.2 OCR-only Draft

适合：

```text
无语音视频
屏幕录制
游戏 UI
硬字幕视频
PPT / 网课板书
歌词 MV
```

流程：

```text
OCR Recognition
  -> Translate Agent
```

输出必须标记：

```text
mode = OCR_ONLY_DRAFT
incomplete = true
```

UI 必须提示：

```text
该结果仅基于画面文字，不包含语音内容。
```

### 5.3 ASR + OCR Fusion

适合：

```text
语音 + 硬字幕
画面上有章节标题/术语/人名/地名
ASR 容易听错专有名词
视频中有 UI 文本或标注
```

流程：

```text
ASR Subtitle
OCR Recognition
  -> Translate Agent
```

默认规则：

```text
ASR 是主时间轴
OCR 是视觉上下文
OCR 可修正专有名词、屏幕文字、硬字幕
冲突写入 conflict / agent_notes
```

---

## 6. Degraded Dependency Policy

Translate Agent 不应硬性要求 ASR 和 OCR 同时成功。

推荐默认策略：

```text
prefer_fusion_but_degrade
```

规则表：

| ASR | OCR | 行为 |
|---|---|---|
| success | disabled | ASR-only |
| success | success | ASR + OCR fusion |
| success | failed | ASR-only with warning |
| failed | success | OCR-only draft if policy allows |
| failed | failed | blocked |
| pending | success | wait or OCR-only draft, by policy |
| success | pending | wait or ASR-only, by policy |

建议模型：

```python
class RecognitionFusionPolicy(str, Enum):
    REQUIRE_FUSION = "require_fusion"
    PREFER_FUSION_BUT_DEGRADE = "prefer_fusion_but_degrade"
    ASR_ONLY = "asr_only"
    OCR_ONLY_DRAFT = "ocr_only_draft"
```

---

## 7. Translate Agent 内部模块

Codex 实现时不要写成一个超大函数，应拆成这些模块。

```text
TranslateAgentAdapter
  ├─ RecognitionInputResolver
  ├─ TimelineBuilder
  ├─ OCRContextAligner
  ├─ ContextBuilder
  ├─ ChunkPlanner
  ├─ PromptBuilder
  ├─ ProviderClient
  ├─ ResultValidator
  ├─ RepairRunner
  └─ SubtitleRebuilder
```

### 7.1 RecognitionInputResolver

职责：

```text
读取 ASR subtitle artifact
读取 ASR sidecar json
读取 OCR text track
读取 glossary artifact
读取 style profile
判断 recognition mode
```

输出：

```python
class RecognitionBundle(BaseModel):
    mode: Literal["ASR_ONLY", "OCR_ONLY_DRAFT", "ASR_OCR_FUSION"]
    asr_segments: list[ASRSegment] = []
    ocr_items: list[OCRTextItem] = []
    source_language_hint: str | None = None
    target_language: str
    warnings: list[str] = []
```

### 7.2 TimelineBuilder

职责：

```text
确定主字幕时间轴
```

规则：

```text
ASR 存在：
  ASR segment timeline 是 primary timeline

ASR 不存在、OCR 存在：
  OCR time window 生成 draft timeline

ASR + OCR 都存在：
  ASR timeline 保持不变
  OCR items 按时间窗口附着到附近 ASR segments
```

数据模型：

```python
class TimelineSegment(BaseModel):
    segment_id: str
    start: float
    end: float
    source_text: str
    source: Literal["asr", "ocr_draft"]
    attached_ocr_item_ids: list[str] = []
```

### 7.3 OCRContextAligner

职责：

```text
把 OCR items 按时间窗口、bbox、置信度挂到 ASR segment 附近
```

策略：

```text
time overlap
nearest segment
same text similarity
subtitle-region priority
confidence threshold
```

不要做：

```text
不要让 OCR 改写 ASR 时间轴
不要把 UI 文本无脑插入字幕正文
```

### 7.4 ContextBuilder

职责：

```text
为每个 chunk 生成上下文
```

上下文内容：

```text
当前 segment range
前后 N 条 ASR 字幕
对应时间窗口 OCR 文本
视频 metadata
术语表
风格要求
上一 chunk summary
下一 chunk preview
```

### 7.5 ChunkPlanner

职责：

```text
把长字幕分块
```

分块原则：

```text
不超过 provider token limit
尽量不打断完整句子
保留 segment_id
保留时间轴
保留 overlap context
支持失败 chunk 单独 retry
```

建议模型：

```python
class TranslationChunk(BaseModel):
    chunk_id: str
    segment_start_index: int
    segment_end_index: int
    timeline_segments: list[TimelineSegment]
    ocr_context: list[OCRTextItem]
    previous_summary: str | None = None
    next_preview: str | None = None
```

### 7.6 PromptBuilder

职责：

```text
把结构化上下文转成 provider request
```

提示词原则：

```text
保持 segment_id 数量
不要改时间轴
不要输出 SRT
只输出 JSON
术语必须一致
OCR 只作为视觉上下文，不要无脑加入正文
冲突写入 conflicts
```

### 7.7 ProviderClient

职责：

```text
调用远程 LLM
调用本地 LLM
调用传统翻译 provider
处理 rate limit
处理 credential_ref
处理 structured output / JSON mode
```

Provider 类型：

```python
class TranslateProviderKind(str, Enum):
    OPENAI_COMPATIBLE = "openai_compatible"
    DEEPL = "deepl"
    GOOGLE = "google"
    AZURE = "azure"
    LOCAL_LLM = "local_llm"
```

### 7.8 ResultValidator

职责：

```text
验证 provider 输出
```

必须检查：

```text
JSON parse
schema valid
chunk_id match
segment_id match
segment count match
no missing translated_text
no extra hallucinated segment
no timing mutation
no OCR notes mixed into subtitle body
glossary applied if strict
line length constraint
provider refusal
```

### 7.9 RepairRunner

职责：

```text
修复单个失败 chunk
```

策略：

```text
retry same prompt
repair with validator error
split chunk smaller
fallback provider
mark chunk failed
```

### 7.10 SubtitleRebuilder

职责：

```text
根据 validated structured result 重建字幕文件
```

输出：

```text
translated.srt
translated.vtt
translated.ass optional
translation_fusion.json
translation_warnings.json
```

---

## 8. 输入 Artifact Contract

### 8.1 ASR artifact

```text
artifact_type: subtitle
path: raw_asr.srt
sidecar: raw_asr.json
metadata:
  source = asr
  language
  segments
  model_id
  backend
```

ASR sidecar 建议：

```python
class ASRSegment(BaseModel):
    segment_id: str
    start: float
    end: float
    text: str
    confidence: float | None = None
    speaker: str | None = None
```

### 8.2 OCR artifact

```text
artifact_type: ocr_text_track
path: ocr_track.json
metadata:
  source = ocr
  backend
  model_id
  frames_sampled
  confidence_stats
```

OCR item：

```python
class OCRTextItem(BaseModel):
    item_id: str
    start_time: float
    end_time: float | None = None
    text: str
    confidence: float | None = None
    bbox: list[float] | None = None
    frame_index: int | None = None
    region: str | None = None
```

### 8.3 Glossary artifact

```python
class GlossaryEntry(BaseModel):
    source: str
    target: str
    note: str | None = None
    case_sensitive: bool = False
```

### 8.4 Style profile

```python
class TranslationStyleProfile(BaseModel):
    tone: Literal["natural", "formal", "casual", "technical"] = "natural"
    preserve_line_breaks: bool = True
    max_chars_per_line: int | None = 42
    subtitle_readability: Literal["compact", "balanced", "literal"] = "balanced"
    honorific_policy: str | None = None
```

---

## 9. 输出 Artifact Contract

Translate Agent 至少输出：

```text
translated.srt
translation_fusion.json
translation_warnings.json
```

### 9.1 translated.srt

规则：

```text
时间轴来自 TimelineBuilder
字幕文本来自 validated structured result
不要让 provider 直接决定最终 SRT 格式
```

### 9.2 translation_fusion.json

```python
class TranslationFusionMetadata(BaseModel):
    mode: Literal["ASR_ONLY", "OCR_ONLY_DRAFT", "ASR_OCR_FUSION"]
    used_asr: bool
    used_ocr: bool
    primary_timeline: Literal["asr", "ocr_draft"]
    provider_kind: str
    model_id: str | None
    chunks: int
    glossary_entries_used: int
    conflict_count: int
    warnings: list[str] = []
```

### 9.3 translation_warnings.json

```python
class TranslationWarning(BaseModel):
    warning_id: str
    severity: Literal["info", "warning", "critical"]
    segment_id: str | None
    code: str
    message: str
    related_ocr_item_ids: list[str] = []
```

---

## 10. Structured Output Schema

Provider 输出不要是 SRT。必须是结构化结果。

```python
class TranslationConflict(BaseModel):
    conflict_id: str
    segment_id: str | None = None
    asr_text: str | None = None
    ocr_text: str | None = None
    resolution: str
    note: str

class TranslatedSegment(BaseModel):
    segment_id: str
    translated_text: str
    confidence: float | None = None
    used_ocr_item_ids: list[str] = []
    notes: list[str] = []

class TranslationChunkResult(BaseModel):
    chunk_id: str
    mode: Literal["ASR_ONLY", "OCR_ONLY_DRAFT", "ASR_OCR_FUSION"]
    target_language: str
    segments: list[TranslatedSegment]
    glossary_applied: list[str] = []
    conflicts: list[TranslationConflict] = []
    chunk_summary: str = ""
```

Validator rules：

```text
segments count must match expected segment count
segment_id set must match expected segment IDs
translated_text must be non-empty unless source is intentionally silent
no timing fields allowed from provider
notes must not be merged into translated_text
```

---

## 11. Translate Agent 参数

基础参数：

```python
class TranslateAgentParams(BaseModel):
    target_language: str
    provider_kind: TranslateProviderKind
    model_id: str | None = None
    fusion_policy: RecognitionFusionPolicy = "prefer_fusion_but_degrade"
    glossary_artifact_id: str | None = None
    style_profile_id: str | None = None
    context_window_segments: int = 5
    max_chunk_tokens: int = 6000
    overlap_segments: int = 2
    preserve_line_breaks: bool = True
    max_chars_per_line: int | None = 42
    conflict_strategy: Literal["agent_resolve_with_notes", "prefer_asr", "prefer_ocr_for_screen_text"] = "agent_resolve_with_notes"
```

高级参数：

```python
class TranslateAgentAdvancedParams(BaseModel):
    max_concurrent_chunks: int = 2
    retry_count: int = 2
    repair_on_schema_error: bool = True
    strict_structured_output: bool = True
    private_prompt_mode: bool = True
    redact_diagnostics: bool = True
    provider_rate_limit_per_minute: int | None = None
```

---

## 12. Provider 抽象

### 12.1 OpenAI-compatible LLM

适合：

```text
ASR + OCR fusion
术语一致性
风格控制
冲突解释
```

要求：

```text
优先使用 structured outputs / JSON schema
如果 provider 不支持 strict schema，必须本地 validate + repair
```

### 12.2 DeepL / traditional MT

适合：

```text
ASR-only 快速翻译
术语表强约束
成本可控
```

限制：

```text
不擅长 ASR/OCR 融合推理
不应直接承担 conflict resolution
```

### 12.3 Local LLM

适合：

```text
隐私优先
离线翻译
ASR/OCR fusion
```

调度注意：

```text
占 GPU/CPU
受 max_local_llm_tasks 限制
可能与 ASR/OCR/Video Enhance 抢资源
```

---

## 13. Scheduler / ExecutionPlan 接入

### 13.1 Dependency

Translate Agent 可以有三种依赖模式：

```text
ASR_ONLY:
  depends_on = [asr.whisper]

OCR_ONLY_DRAFT:
  depends_on = [ocr.recognition]

ASR_OCR_FUSION:
  depends_on = [asr.whisper, ocr.recognition]
```

对于默认 `prefer_fusion_but_degrade`：

```text
ASR completed + OCR failed:
  runnable as ASR_ONLY with warning

ASR failed + OCR completed:
  runnable as OCR_ONLY_DRAFT if policy allows

ASR pending + OCR completed:
  wait or draft depending user/preset policy

OCR pending + ASR completed:
  wait or ASR-only depending user/preset policy
```

### 13.2 ResourceRequest

Remote API：

```text
resource_type = api_slot
provider = selected provider
concurrency = max_remote_translate_tasks
```

Local LLM：

```text
resource_type = gpu/cpu
exclusive_preferred = true
vram estimate from model
```

### 13.3 Backpressure

Translate Agent 是慢阶段，必须被 `BATCH_PIPELINE_SCHEDULING_SPEC.md` 里的 backlog 控制：

```text
max_translate_backlog
max_remote_translate_tasks
max_local_llm_tasks
provider_rate_limit
```

---

## 14. Worker Event 行为

Translate Agent Worker 必须发：

```text
started
log
heartbeat
progress
artifact
completed
failed
```

Progress stage 建议：

```text
stage=resolve_inputs
stage=build_timeline
stage=plan_chunks
stage=translate_chunk
stage=validate_chunk
stage=repair_chunk
stage=rebuild_subtitle
stage=write_artifacts
```

Progress unit：

```text
chunks
segments
tokens optional
```

---

## 15. 错误映射

| 场景 | error_code |
|---|---|
| ASR/OCR 都缺失 | INPUT_MISSING |
| ASR artifact 损坏 | INPUT_CORRUPT |
| OCR track 损坏 | INPUT_CORRUPT |
| provider credential missing | PERMISSION / RUNTIME_MISSING |
| local model missing | MODEL_MISSING |
| provider timeout | TIMEOUT |
| schema validation repeatedly failed | INTERNAL |
| context too large | INTERNAL or POLICY_LIMIT future |
| API rate limit | DEPENDENCY or PROVIDER_RATE_LIMIT future |
| local LLM OOM | OOM |
| user cancelled | CANCELLED |

---

## 16. GUI / Inspector 设计要求

Translate Agent 卡片显示：

```text
Translate Agent
Mode: ASR + OCR Fusion
Provider: OpenAI-compatible / DeepL / Local LLM
Backlog: 8 queued
```

Inspector 显示：

```text
Recognition Inputs
  ASR Subtitle:
    enabled/completed/failed/missing
    segments
    language
  OCR Recognition:
    enabled/completed/failed/missing
    items
    confidence
    frames sampled

Fusion Policy
  Primary timeline: ASR
  Conflict strategy
  Degrade behavior

Provider
  kind
  model
  concurrency
  rate limit

Output
  format
  max chars per line
  glossary
  style profile
```

失败动作：

```text
Continue ASR-only
Continue OCR-only draft
Retry OCR
Retry ASR
Retry failed translation chunks
Use smaller model
Switch provider
Open logs
```

---

## 17. Implementation Plan for Codex

### Phase A：Models Only

新增或扩展：

```text
atelier/domain/translation.py
```

包含：

```text
ASRSegment
OCRTextItem
RecognitionBundle
TimelineSegment
TranslationChunk
TranslationChunkResult
TranslationFusionMetadata
TranslationWarning
TranslateAgentParams
```

验收：

```text
pydantic validation tests pass
schema examples serialize/deserialize
```

### Phase B：Input Resolver + Timeline Builder

新增：

```text
atelier/translation/input_resolver.py
atelier/translation/timeline_builder.py
atelier/translation/ocr_context_aligner.py
```

验收：

```text
ASR-only input builds ASR timeline
OCR-only input builds draft timeline
ASR+OCR attaches OCR items to ASR segments
failed/missing input produces correct mode warning
```

### Phase C：Chunk Planner + Prompt Builder

新增：

```text
atelier/translation/chunk_planner.py
atelier/translation/prompt_builder.py
```

验收：

```text
chunk preserves segment ids
chunk respects max token estimate
overlap segments included
prompt includes OCR context but not raw huge frame dumps
```

### Phase D：Provider Interface

新增：

```text
atelier/translation/providers/base.py
atelier/translation/providers/openai_compatible.py
atelier/translation/providers/deepl.py
atelier/translation/providers/local_llm.py
```

首版可以先实现 fake provider / test provider。

验收：

```text
provider returns TranslationChunkResult
rate limit simulated
credential missing mapped
```

### Phase E：Result Validator + Repair

新增：

```text
atelier/translation/result_validator.py
atelier/translation/repair_runner.py
```

验收：

```text
missing segment rejected
extra segment rejected
invalid JSON rejected
notes not mixed into subtitles
repair prompt generated
```

### Phase F：Subtitle Rebuilder

新增：

```text
atelier/translation/subtitle_rebuilder.py
```

验收：

```text
SRT generated from timeline + translated segments
timecodes preserved
max chars per line applied if configured
fusion metadata written
warnings written
```

### Phase G：TranslateAgentAdapter

新增：

```text
atelier/workers/adapters/translate_agent.py
```

职责：

```text
read task.json
resolve input artifacts
build timeline/chunks
call provider
validate/repair
write artifacts
emit WorkerEvents
```

验收：

```text
simulated ASR-only task completed
simulated OCR-only draft completed with warning
simulated ASR+OCR fusion completed
provider failure -> failed event
cancel -> CANCELLED
```

### Phase H：Scheduler / UI Integration

接入：

```text
ExecutionPlan dependency policy
BATCH_PIPELINE_SCHEDULING waiting reason
Hardware Scheduling Page stage backlog
Queue Monitor status
Inspector controls
```

---

## 18. Testing Matrix

### Unit Tests

```text
ASR sidecar parse
OCR track parse
Recognition mode resolution
TimelineBuilder ASR-only
TimelineBuilder OCR-only
TimelineBuilder ASR+OCR
OCRContextAligner overlap
ChunkPlanner boundaries
PromptBuilder includes glossary
ResultValidator schema valid
ResultValidator missing segment
SubtitleRebuilder SRT output
```

### Integration Tests

```text
TranslateAgentAdapter fake provider ASR-only
TranslateAgentAdapter fake provider OCR-only draft
TranslateAgentAdapter fake provider ASR+OCR fusion
Provider timeout
Provider invalid JSON then repair
Cancel during chunk translation
Artifact write and validation
```

### E2E Demo Tests

```text
V01 ASR + OCR fusion -> translated.srt
V02 OCR failed -> ASR-only degrade
V03 ASR failed -> OCR-only draft
V04 both failed -> blocked
Batch backlog -> paused_by_backpressure
```

---

## 19. Anti-patterns

Codex 必须避免：

```text
把整个 SRT 一次性发给 LLM
让 LLM 直接生成最终 SRT
把 OCR 文本无脑插入字幕正文
忽略 segment_id
忽略时间轴
provider 失败后吞错并 completed
API key 出现在 logs/events/stderr
Adapter 直接写最终导出目录
Adapter 直接查 SQLite
GUI 直接调用 provider
```

---

## 20. File Placement Recommendation

建议新增：

```text
docs/TRANSLATE_AGENT_SPEC.md

atelier/domain/translation.py
atelier/translation/input_resolver.py
atelier/translation/timeline_builder.py
atelier/translation/ocr_context_aligner.py
atelier/translation/chunk_planner.py
atelier/translation/prompt_builder.py
atelier/translation/result_validator.py
atelier/translation/repair_runner.py
atelier/translation/subtitle_rebuilder.py
atelier/translation/providers/base.py
atelier/workers/adapters/translate_agent.py
tests/test_translation_*.py
```

---

## 21. 与其他文档对齐

必须同步检查：

```text
PRODUCT_FLOW_SPEC.md
MVP_ACCEPTANCE_SPEC.md
ADAPTER_SPEC.md
ASR_ADAPTER_SPEC.md
OCR_ADAPTER_SPEC.md
ARTIFACT_LIFECYCLE_SPEC.md
BATCH_PIPELINE_SCHEDULING_SPEC.md
HARDWARE_SCHEDULING_PAGE_SPEC.md
SCHEDULING_PRESETS_SPEC.md
UI_STATE_SPEC.md
ONBOARDING_RUNTIME_SETUP_SPEC.md
WORKER_PROTOCOL.md
EXECUTION_PLAN_SPEC.md
DATABASE_SCHEMA.md
```

尤其要确认：

```text
translate.llm 是否支持 optional/degraded dependency
ocr_text_track 是否有 artifact 表达
translation_fusion.json 是否有 artifact metadata
Scheduler 是否能显示 ASR-only / OCR-only / ASR+OCR fusion waiting reason
```

---

## 22. Codex 首次实现提示词建议

```text
Read docs/TRANSLATE_AGENT_SPEC.md and related docs first.

Implement only Phase A-C first:
1. Create translation domain models.
2. Implement RecognitionInputResolver, TimelineBuilder, OCRContextAligner.
3. Implement ChunkPlanner and PromptBuilder.
4. Add unit tests using fake ASR/OCR artifacts.

Do not implement real provider API calls yet.
Do not edit Scheduler or GUI yet.
Do not use shell commands.
Do not write final SRT directly from LLM output.
Keep all output schema-driven and testable.
```

---

## 23. 参考资料

```text
Subtitle Edit Overview:
https://subtitleedit.github.io/subtitleedit/overview.html

faster-whisper:
https://github.com/SYSTRAN/faster-whisper

OpenAI Structured Outputs:
https://platform.openai.com/docs/guides/structured-outputs

DeepL Glossaries:
https://developers.deepl.com/api-reference/multilingual-glossaries

PaddleOCR:
https://www.paddleocr.ai/

Tesseract OCR:
https://tesseractocr.org/
```
