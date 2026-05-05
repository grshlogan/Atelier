# Minimal Adapter Probe Workflow 计划

> 执行顺序：第 9 个后续计划。建议在 `plan_runtime_management_foundation.md` 完成后执行；如果要从 GUI 触发，则先完成 `plan_initial_actionable_gui_runtime_setup.md` 的相关入口。

## Objective（目标）

跑通第一条最简真实 adapter workflow，让 Atelier 从规划和 stub worker 迈向受控真实工具执行。

推荐第一条链路：

```text
input.video
  -> metadata.probe
  -> output.export / artifact finalization
```

第一版重点不是视频处理效果，而是证明：

```text
WorkflowGraph
  -> ExecutionPlan
  -> Scheduler claim
  -> RuntimeManager RuntimeBinding
  -> Worker task.json
  -> AdapterRegistry
  -> FFprobeMetadataAdapter
  -> WorkerEvent / Artifact
  -> SQLite
```

## Scope（范围）

- 新增最小 `WorkerAdapter` / `AdapterRegistry` 实现边界，贴合 `docs/ADAPTER_SPEC.md`。
- 新增 typed `CommandSpec` / safe subprocess command executor，禁止 `shell=True` 和 string-concatenated command。
- 新增 `FFprobeMetadataAdapter` 或 `metadata.probe` adapter，使用 RuntimeBinding 中的 `ffprobe` path。
- adapter 将 ffprobe JSON 或 fake probe JSON 写入 task work dir，并上报 metadata artifact。
- 新增 adapter worker entrypoint 或 adapter dispatch helper，让 Worker process 能按 node_type 调用 adapter。
- 用 fake ffprobe executable 做集成测试，避免 CI/开发机必须安装真实 FFmpeg。
- 可选增加真实 ffprobe smoke test，但必须在未安装时自动 skip。

暂不实现：

- 视频转码、音频提取、字幕 mux/burn。
- ASR、OCR、Translate Agent、RealESRGAN、RIFE、LADA-like 修复。
- 自动下载 FFmpeg。
- GUI 一键运行完整 workflow。
- 多 worker 并发和 production retry/recovery action execution。

## Current Facts（当前事实）

- Scheduler claim、task file、runner、lifecycle dispatch、SQLite event/artifact/failure persistence 已有 stub worker 闭环。
- RuntimeManager 已有最小 `RuntimeRequest -> RuntimeBinding` 解析，并将在 Runtime 管理计划中补本地 runtime profile / health / GUI snapshot。
- `docs/ADAPTER_SPEC.md` 已定义 `WorkerAdapter`、`AdapterContext`、`AdapterResult` 和 typed command builder 原则。
- `docs/FFMPEG_ADAPTER_SPEC.md` 已规划 ffprobe / FFmpeg adapters。
- `docs/WORKFLOW_NODE_SPEC.md` 已列出 `metadata.probe` 与主要 node catalog。

## Constraints（约束）

- GUI 不参与本计划，除非后续明确进入 GUI trigger plan。
- RuntimeManager 是 ffprobe path 的唯一事实源。
- Adapter 不从全局 PATH 查找 ffprobe。
- Adapter 不写 SQLite；只发 WorkerEvent / artifact refs。
- Adapter 输出必须先写 task work dir，再由 artifact flow 记录。
- fake ffprobe 测试必须覆盖 command args 和 JSON parse，不依赖真实系统 FFmpeg。

## Execution Plan（执行计划）

### Phase A：adapter contract 与 registry

目标：

- 落地最小 adapter contract 和 registry。

完成信号：

- 可按 `node_type` 查到 adapter。
- 未注册 node_type 有明确错误。
- contract 不依赖 GUI / Scheduler / SQLite。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_adapter_registry
```

状态：

- 待执行。

### Phase B：typed command executor

目标：

- 新增安全命令执行边界。

完成信号：

- `CommandSpec` 使用 executable + args list + cwd + env。
- executor 不使用 `shell=True`。
- stderr/stdout/redaction 有测试。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_command_executor
```

状态：

- 待执行。

### Phase C：metadata.probe adapter

目标：

- 实现 `metadata.probe` 的首个 adapter。

完成信号：

- adapter 从 RuntimeBinding 读取 `ffprobe` path。
- adapter 对用户输入路径做 artifact/input 校验。
- adapter 解析 JSON 并写 metadata artifact。
- adapter 把 dependency / invalid JSON / missing input 映射为结构化失败。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_ffprobe_metadata_adapter
```

状态：

- 待执行。

### Phase D：adapter worker dispatch 集成

目标：

- 让 Worker process 能加载 task.json 并调用 adapter。

完成信号：

- fake ffprobe worker path 产生 `started -> artifact -> completed`。
- malformed fake ffprobe 输出产生结构化 failure。
- Scheduler dispatch seam 能持久化 adapter 事件和 artifact。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_minimal_probe_workflow
```

状态：

- 待执行。

### Phase E：最简 workflow 闭环

目标：

- 跑通 `input.video -> metadata.probe` 的后端闭环。

完成信号：

- WorkflowGraph 可生成 ExecutionPlan。
- RuntimeManager 解析 fake/registered ffprobe RuntimeBinding。
- Scheduler claim 后 dispatch adapter worker。
- SQLite 中能看到 task_events、metadata artifact、task status。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_minimal_probe_workflow
```

状态：

- 待执行。

### Phase F：文档状态对齐

目标：

- 更新 adapter / workflow / runtime / worker 接手文档。

完成信号：

- `ADAPTER_SPEC.md`、`FFMPEG_ADAPTER_SPEC.md`、`APP_CODE_MAP.md`、`RECENT_CHANGES.md` 和主计划更新。
- 明确只实现 metadata probe，不实现转码、ASR、OCR、翻译或增强。

验证：

```powershell
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

状态：

- 待执行。

## Child Plans（子计划）

- 后续可拆 `plan_ffmpeg_audio_extract_adapter.md`。
- 后续可拆 `plan_translate_agent_adapter_foundation.md`。
- 后续可拆 `plan_ocr_recognition_adapter_foundation.md`。

## Verification（验证）

计划验证命令：

```powershell
.venv/Scripts/python -m unittest tests.test_adapter_registry tests.test_command_executor tests.test_ffprobe_metadata_adapter tests.test_minimal_probe_workflow
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

## Progress / Decisions（进展 / 决策）

- 2026-05-05：创建本计划。决策：首个真实 adapter 选择 `metadata.probe` / ffprobe，因为它能验证 runtime path、typed command、artifact 和 dispatch 闭环，同时比 ASR/OCR/翻译/视频增强风险低。

## Blockers（阻塞）

- 依赖 `plan_runtime_management_foundation.md` 完成可用 runtime profile / RuntimeBinding。
