# Atelier Adapter Spec

> 状态：部分实现。当前已落地最小 `WorkerAdapter` / `AdapterRegistry`、typed `CommandSpec` / safe executor、`metadata.probe` / `FFprobeMetadataAdapter`、`media.audio_extract` / `FFmpegAudioExtractAdapter` 和 adapter worker entrypoint。其他 Adapter 仍处于规划中。具体工具细节见 `FFMPEG_ADAPTER_SPEC.md`、`ASR_ADAPTER_SPEC.md`、`OCR_ADAPTER_SPEC.md`、`VIDEO_ENHANCE_ADAPTER_SPEC.md`。

## 1. Adapter 定位

```text
ExecutionTask + RuntimeBinding + ResourceBinding + task work dir
  -> Adapter
  -> WorkerEvent stream
  -> staged artifacts
```

Adapter 不拥有调度权、数据库写入权、runtime 安装权。

### 1.1 与第三方工具接入的关系

`ExternalToolAdapter` 是 `WorkerAdapter` 的专门化方向，用于接入本地 CLI、本地 SDK、托管 runtime、远程 provider 或插件贡献 backend。它属于核心执行接口，不依赖 PluginManager。

PluginManager 可以贡献 adapter/backend 声明，但执行仍然必须走：

```text
Scheduler -> RuntimeManager -> Worker -> Adapter -> WorkerEvent / Artifact
```

详细规划见 `EXTERNAL_TOOL_INTEGRATION_SPEC.md`。

## 2. 通用原则

```text
一个 Worker 进程对应一个 ExecutionTask
Adapter 不直接写 SQLite
Adapter 不直接读 GUI 状态
Adapter 不直接管理 resource_locks
Adapter 不从全局 PATH 找工具
Adapter 不下载 runtime/model
Adapter 不直接读取或保存 provider secrets
Adapter 不绕过 PluginManager 使用插件贡献代码
Adapter 不覆盖 task work dir 之外的文件
Adapter 不拼接 shell command
```

## 3. 通用接口

```python
class AdapterContext(BaseModel):
    task: ExecutionTask
    runtime_binding: RuntimeBinding
    resource_binding: ResourceBinding | None
    work_dir: Path
    cancel_token: CancelToken
    emitter: EventEmitter
    redactor: Redactor

class AdapterResult(BaseModel):
    artifacts: list[ArtifactRef]
    duration_seconds: float
    metadata: dict[str, Any] = {}

class WorkerAdapter(ABC):
    node_type: str
    adapter_version: str

    def validate(self, context: AdapterContext) -> list[AdapterValidationError]: ...
    def prepare(self, context: AdapterContext) -> None: ...
    def run(self, context: AdapterContext) -> AdapterResult: ...
    def cancel(self, context: AdapterContext) -> None: ...
```

## 4. Typed Command Builder

```python
class CommandSpec(BaseModel):
    executable: Path
    args: list[str]
    cwd: Path
    env: dict[str, str] = {}
    redacted_args: list[str] = []
```

规则：

```text
no shell=True
no string-concatenated command
every argument is a list item
paths come from RuntimeBinding
user params validated before conversion
secret values redacted before logging
```

## 5. 通用错误映射

| 场景 | error_code |
|---|---|
| 显存不足 | OOM |
| 模型缺失 | MODEL_MISSING |
| 输入文件缺失 | INPUT_MISSING |
| 输入损坏 | INPUT_CORRUPT |
| Runtime 缺失 | RUNTIME_MISSING |
| 外部依赖失败 | DEPENDENCY |
| 权限不足 | PERMISSION |
| 磁盘满 | DISK_FULL |
| 用户取消 | CANCELLED |
| 心跳超时 | TIMEOUT |
| 未分类异常 | INTERNAL |

## 6. 内置 Adapter 清单

```text
metadata.probe           -> FFmpegProbeAdapter
input.video              -> InputMediaAdapter
input.audio              -> InputMediaAdapter
input.subtitle           -> InputSubtitleAdapter
media.audio_extract      -> FFmpegAudioExtractAdapter
compose.mux_subtitle     -> FFmpegSoftSubtitleMuxAdapter
compose.burn_subtitle    -> FFmpegBurnSubtitleAdapter
compose.mux_audio        -> FFmpegMuxAudioAdapter
output.export            -> ArtifactFinalizer / FFmpegExportAdapter

asr.whisper              -> WhisperASRAdapter
ocr.recognition          -> OCRRecognitionAdapter
translate.llm            -> TranslateAgentAdapter
subtitle.review          -> LLMSubtitleReviewAdapter
subtitle.normalize       -> SubtitleNormalizeAdapter

enhance.realesrgan       -> RealESRGANAdapter
enhance.rife             -> RIFEAdapter
audio.enhance            -> AudioEnhanceAdapter
```

## 7. Translate Agent 融合输入

```python
class TranslationContext(BaseModel):
    asr_subtitle_artifact_id: str | None
    ocr_text_track_artifact_id: str | None
    source_language_hint: str | None
    target_language: str
    glossary_artifact_id: str | None = None
    style_profile: str | None = None
```

规则：

```text
ASR + OCR -> fusion translation
ASR only -> ASR-only translation
OCR only -> OCR-only draft, mark incomplete
Neither -> Translate blocked
```

## 8. Adapter 测试基线

```text
validate params
missing input
missing runtime
cancel
artifact output
stderr/log redaction
error mapping
path traversal rejection
```
