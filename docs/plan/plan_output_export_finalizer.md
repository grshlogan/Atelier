# Output Export ArtifactFinalizer 计划

> 执行顺序：第 11 个后续计划。建议在 `plan_ffmpeg_audio_extract_adapter.md` 完成并提交后执行。

## Objective

补齐第一个最终输出边界，让 Atelier 能把已经生成的 staged artifact 安全落到用户选择的输出目录：

```text
valid staged artifact
  -> output.export / ArtifactFinalizer
  -> final output artifact link
```

第一版重点不是完整导出系统，而是验证：

```text
staged artifact path
  -> conflict check
  -> copy to output_dir
  -> hash / size verification
  -> WorkerEvent / final_output artifact
  -> SQLite task_artifacts role=final_output
```

## Scope

- 新增 `output.export` / `ArtifactFinalizerAdapter`。
- 输入参数使用：
  - `input_path`：已有 staged artifact 文件路径。
  - `output_dir`：用户选择的目标输出目录。
  - `filename`：可选输出文件名；未指定时使用 `input_path.name`。
  - `artifact_type`：可选 artifact type，默认 `video`。
- 输出文件必须写入 `output_dir` 内。
- 输出文件已存在时失败，不静默覆盖。
- 拒绝带路径分隔符、绝对路径或 `..` 的 `filename`。
- 复制后验证目标文件存在、大小一致、SHA-256 一致。
- 通过 WorkerEvent / Artifact 将 final output 写入 SQLite，并在 `task_artifacts` 中使用 `role=final_output`。

暂不实现：

- GUI 导出对话框。
- 多 artifact 批量导出。
- move 语义和清理 staged artifact。
- 输出命名模板。
- 容器格式转换、字幕 mux/burn、FFmpeg 导出预设。
- 用户目录冲突 UI 交互。
- 权限修复建议或磁盘空间预估。

## Current Facts

- `metadata.probe` / `FFprobeMetadataAdapter` 已实现并提交。
- `media.audio_extract` / `FFmpegAudioExtractAdapter` 已实现并提交。
- `adapter_entry` 已可从 `task.json` 调用 built-in adapter 并输出 Worker JSON Lines。
- `RuntimeManager.resolve(RuntimeRequest())` 可返回 `runtime:none` binding，因此 `output.export` 首版不需要真实 runtime component。
- `record_worker_events()` 当前会把 `ArtifactEvent.metadata.role == "final_output"` 记录为 role=`final_output`；其他 `ArtifactEvent` 保持 role=`output`。
- 当前完整验证基线是 `.venv/Scripts/python -m unittest discover -s tests`，最近结果为 112 tests passed。

## Constraints

- Worker 不直接覆盖用户文件。
- Finalizer 不写 `output_dir` 之外的路径。
- Finalizer 不依赖全局 PATH、FFmpeg 或模型 backend。
- Finalizer 不直接写 SQLite；SQLite 写入仍由 WorkerEvent 持久化边界完成。
- GUI 不参与本计划。
- 不把 staged artifact 删除或移动走，第一版只复制。
- 冲突、路径越界、缺输入、复制校验失败都必须是结构化失败。

## Execution Plan

### Phase A: ArtifactFinalizer adapter 单元行为

目标：
- 新增 `ArtifactFinalizerAdapter`，最小支持 `output.export`。

完成信号：
- 可把 existing staged file 复制到 `output_dir / filename`。
- 未给 `filename` 时使用源文件名。
- 返回 artifact：

```text
artifact_type: task.params.artifact_type or video
path: final output absolute path
metadata.role: final_output
metadata.source_path
metadata.size_bytes
metadata.sha256
```

- 源文件缺失映射为 `INPUT_MISSING`。
- 输出冲突映射为 `OUTPUT_CONFLICT`。
- 不安全 filename 映射为 `PERMISSION`。
- copy 后 hash/size 不一致映射为 `INTERNAL`。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_artifact_finalizer_adapter
```

状态：

- 已完成。

### Phase B: worker dispatch 和 SQLite final_output link

目标：
- 让 `adapter_entry` 可以执行 `output.export`，并让 SQLite 记录 final output link。

完成信号：
- fake staged file workflow 产生 `started -> artifact -> completed`。
- 目标输出文件存在且内容一致。
- SQLite 中 artifact path 为最终输出路径。
- `task_artifacts` 中 role 为 `final_output`。
- 冲突时产生结构化 `OUTPUT_CONFLICT` failure。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_output_export_workflow
```

状态：

- 已完成。

### Phase C: 文档对齐

目标：
- 更新 adapter / artifact lifecycle / app code map / recent changes / main plan。

完成信号：
- `ADAPTER_SPEC.md` 标记 `output.export` 首版已部分实现。
- `ARTIFACT_LIFECYCLE_SPEC.md` 标记 final output 首版已部分实现。
- `APP_CODE_MAP.md` 记录新增 finalizer adapter 和测试。
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

- 后续可拆 `plan_gui_minimal_run_workflow_entry.md`。
- 后续可拆 `plan_ffmpeg_subtitle_mux_adapter.md`。
- 后续可拆 `plan_whisper_asr_adapter_foundation.md`。

## Verification

计划验证命令：

```powershell
.venv/Scripts/python -m unittest tests.test_artifact_finalizer_adapter
.venv/Scripts/python -m unittest tests.test_output_export_workflow
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

最近验证事实：

- `.venv\Scripts\python -m unittest tests.test_artifact_finalizer_adapter`：5 tests passed。
- `.venv\Scripts\python -m unittest tests.test_output_export_workflow`：2 tests passed。
- `.venv/Scripts/python -m unittest discover -s tests`：112 tests passed。
- `.venv/Scripts/python -m compileall -q atelier tests`：passed。
- `Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'`：no matches。
- `git diff --check`：passed，仅有 Windows CRLF conversion warnings。

## Progress / Decisions

- 2026-05-06：创建本计划。决策：第一个 `output.export` 只做安全复制和 final output link，不做格式转换、mux/burn、GUI 导出或批量导出。
- 2026-05-06：完成 Phase A。新增 `atelier/adapters/finalize.py`，`ArtifactFinalizerAdapter` 可复制 existing staged artifact 到 `output_dir`，拒绝输出冲突和不安全 filename，并验证 size / SHA-256。
- 2026-05-06：完成 Phase B。built-in registry 已注册 `output.export`；`record_worker_events()` 可将 `ArtifactEvent.metadata.role == "final_output"` 记录为 `task_artifacts.role = "final_output"`；worker dispatch 已验证 completed 和 `OUTPUT_CONFLICT` failed paths。
- 2026-05-06：完成 Phase C。`README.md`、`ADAPTER_SPEC.md`、`ARTIFACT_LIFECYCLE_SPEC.md`、`FFMPEG_ADAPTER_SPEC.md`、`WORKER_PROTOCOL.md`、`APP_CODE_MAP.md`、`RECENT_CHANGES.md` 和主计划已对齐。
- 2026-05-06：接手复验时补齐 `WORKER_PROTOCOL.md` 对齐：`output.export` 明确为 `ArtifactFinalizerAdapter` / internal file copy / `runtime:none`，并记录为普通 Worker 写工作目录规则的受控 finalization 例外。

## Blockers

- 暂无。
