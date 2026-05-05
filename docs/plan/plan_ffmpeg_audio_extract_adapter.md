# FFmpeg Audio Extract Adapter 计划

> 执行顺序：第 10 个后续计划。建议在 `plan_minimal_adapter_probe_workflow.md` 完成并提交后执行。

## Objective

让 Atelier 从只读 `metadata.probe` 继续推进到第一个真实媒体产物 adapter：

```text
input.video
  -> media.audio_extract
  -> audio artifact
```

目标不是完整字幕工作流，而是验证：

```text
RuntimeManager RuntimeBinding["ffmpeg"]
  -> FFmpegAudioExtractAdapter
  -> staged audio artifact
  -> WorkerEvent / Artifact
  -> SQLite
```

## Scope

- 新增 `media.audio_extract` / `FFmpegAudioExtractAdapter`。
- Adapter 必须从 `RuntimeBinding.component_paths["ffmpeg"]` 读取 FFmpeg path。
- 输入参数使用 `input_path`，输出写入 task work dir 内的 staged audio。
- 首版默认输出 `audio.wav`，后续再扩展 codec/container/sample-rate/channel 参数。
- 使用 fake FFmpeg executable 做集成测试，避免开发机必须安装真实 FFmpeg。
- 复用现有 `CommandSpec` / `run_command`、`AdapterContext`、`adapter_entry` 和 Scheduler dispatch seam。

暂不实现：

- 真实音轨检测和 no-audio policy。
- FFmpeg progress pipe。
- cancel long transcode。
- ASR、OCR、翻译、字幕 mux/burn。
- GUI 一键运行完整 workflow。
- 用户最终导出目录写入。

## Current Facts

- `metadata.probe` / `FFprobeMetadataAdapter` 已实现并提交。
- `atelier/adapters/` 已有 adapter contract、registry、typed command executor 和 built-in registry。
- `atelier/workers/adapter_entry.py` 已可按 `node_type` 调用 built-in adapter 并输出 Worker JSON Lines。
- `dispatch_claimed_task()` 已支持把 `RuntimeBinding` 写入 `task.json`。
- 当前完整验证基线是 `.venv/Scripts/python -m unittest discover -s tests`，最近结果为 98 tests passed。

## Constraints

- Adapter 不直接写 SQLite。
- Adapter 不从全局 PATH 查找 FFmpeg。
- Adapter 不写 task work dir 之外的路径。
- Adapter 不使用 `shell=True` 或 string-concatenated command。
- RuntimeManager 是 FFmpeg path 的唯一事实源。
- WorkerEvent / Artifact 仍由 worker entrypoint 和 dispatch seam 负责持久化。
- 当前阶段不把输出复制到用户目录；最终导出属于 `output.export` / ArtifactFinalizer 后续计划。

## Execution Plan

### Phase A: adapter 单元行为

目标：
- 新增 `FFmpegAudioExtractAdapter`，最小支持 `media.audio_extract`。

完成信号：
- 生成 FFmpeg 命令意图：

```text
ffmpeg -y -i input -vn audio.wav
```

- 输出 artifact：

```text
artifact_type: audio
path: audio.wav
```

- 缺 runtime component 映射为 `RUNTIME_MISSING`。
- 缺输入文件映射为 `INPUT_MISSING`。
- FFmpeg nonzero exit 映射为 `DEPENDENCY`。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_ffmpeg_audio_extract_adapter
```

状态：

- 已完成。

### Phase B: built-in registry 和 worker dispatch 集成

目标：
- 让 `adapter_entry` 可以通过 built-in registry 执行 `media.audio_extract`。

完成信号：
- fake FFmpeg worker path 产生 `started -> artifact -> completed`。
- staged `audio.wav` 存在于 task work dir。
- SQLite 中 task status 为 `completed`，artifact path 为 `audio.wav`。
- malformed / failing fake FFmpeg 产生结构化 `DEPENDENCY` failure。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_minimal_audio_extract_workflow
```

状态：

- 已完成。

### Phase C: 文档对齐

目标：
- 更新 adapter / FFmpeg / app code map / recent changes / main plan。

完成信号：
- `ADAPTER_SPEC.md` 和 `FFMPEG_ADAPTER_SPEC.md` 标记 `media.audio_extract` 已部分实现。
- `APP_CODE_MAP.md` 记录新增 adapter 和测试文件。
- `RECENT_CHANGES.md` 记录本次闭环。
- `plan_main_app_skeleton.md` child plan / progress 对齐。

验证：

```powershell
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

状态：

- 已完成。

## Child Plans

- 后续可拆 `plan_output_export_finalizer.md`。
- 后续可拆 `plan_whisper_asr_adapter_foundation.md`。
- 后续可拆 `plan_translate_agent_adapter_foundation.md`。

## Verification

计划验证命令：

```powershell
.venv/Scripts/python -m unittest tests.test_ffmpeg_audio_extract_adapter
.venv/Scripts/python -m unittest tests.test_minimal_audio_extract_workflow
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

最近验证事实：

- `.venv/Scripts/python -m unittest tests.test_ffmpeg_audio_extract_adapter tests.test_minimal_audio_extract_workflow`：7 tests passed。
- `.venv/Scripts/python -m unittest discover -s tests`：105 tests passed。
- `.venv/Scripts/python -m compileall -q atelier tests`：passed。
- `Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'`：no matches。
- `git diff --check`：passed，仅有 Windows CRLF conversion warnings。

## Progress / Decisions

- 2026-05-06：创建本计划。决策：第一个产物型 adapter 选择 `media.audio_extract`，因为它能复用 RuntimeManager、typed command、WorkerEvent、Artifact 和 Scheduler dispatch seam，同时比 ASR/OCR/翻译/视频增强风险更低。
- 2026-05-06：完成 Phase A。新增 `atelier/adapters/ffmpeg.py`，`FFmpegAudioExtractAdapter` 可从 `RuntimeBinding.component_paths["ffmpeg"]` 读取 FFmpeg path，运行 typed command，写入 `audio.wav` staged artifact，并映射 missing runtime/input、command failure 和 missing output。
- 2026-05-06：完成 Phase B。built-in registry 已注册 `media.audio_extract`；fake FFmpeg workflow 已验证 `WorkflowGraph -> ExecutionPlan -> Scheduler claim -> RuntimeManager RuntimeBinding -> task.json -> AdapterRegistry -> FFmpegAudioExtractAdapter -> WorkerEvent/Artifact -> SQLite`。
- 2026-05-06：完成 Phase C。`README.md`、`ADAPTER_SPEC.md`、`FFMPEG_ADAPTER_SPEC.md`、`APP_CODE_MAP.md`、`RECENT_CHANGES.md` 和主计划已对齐。

## Blockers

- 暂无。
