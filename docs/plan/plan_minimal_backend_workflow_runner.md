# Minimal Backend Workflow Runner 计划

> 执行顺序：第 12 个后续计划。建议在 `plan_output_export_finalizer.md` 完成并提交后执行。

## Objective

把当前“单节点 adapter 可 dispatch”的后端骨架推进为“最小多节点 workflow 可自动推进”的后端闭环：

```text
WorkflowGraph
  -> ExecutionPlan
  -> Scheduler claim
  -> RuntimeManager binding
  -> dispatch_claimed_task()
  -> WorkerEvent / SQLite
  -> next dependency-ready task
```

第一版重点不是生产级队列系统，而是验证：

```text
upstream artifact
  -> downstream input resolution
  -> claim / dispatch / persist loop
  -> stop on completed / failed / blocked
  -> read-only queue snapshot can explain the result
```

## Scope

- 新增最小 artifact handoff 查询能力，用于从已完成上游 task 找到输出 artifact。
- 新增下游 task 参数物化边界，让 `output.export` 这类下游节点不必在 workflow graph 中硬编码 staged artifact path。
- 新增最小后端 workflow runner service，串起 `SimpleScheduler.claim_next_task()`、`RuntimeManager.resolve()`、`dispatch_claimed_task()` 和 SQLite persistence。
- 首版 runner 只顺序推进单个 plan，不做并发。
- 首版 runner 停止条件必须结构化：
  - 所有 task completed。
  - 任一 task failed / cancelled。
  - 没有 runnable task 且仍有 pending task，标记为 blocked result。
- 保持 GUI 只读，不在本计划里新增 GUI 运行按钮。

暂不实现：

- 生产级 durable queue claiming。
- 多 worker 并发、优先级、重试执行、恢复 action execution。
- GUI workflow 编辑器或“运行”按钮。
- 真实 FFmpeg smoke test。
- ASR / OCR / Translate / subtitle mux/burn / video enhance adapters。
- 自动 output naming template、批量导出或覆盖/重命名 UI。

## Current Facts

- 当前已有 `SimpleScheduler.claim_next_task()`，可 claim 依赖已完成的 pending task，并写入 `ResourceBinding`。
- 当前已有 `dispatch_claimed_task()`，可执行一个已 claim task，写入 `task.json`，运行 adapter worker entrypoint，并把 Worker events 持久化到 SQLite。
- 当前已有 `RuntimeManager.resolve()`，可为 `metadata.probe`、`media.audio_extract` 和 `output.export` 提供 runtime binding。
- 当前已有 built-in adapter：`metadata.probe`、`media.audio_extract`、`output.export`。
- 当前 `output.export` 首版 adapter 仍需要 `input_path`；dispatch 准备边界已有 `materialize_downstream_task_inputs()` 可从唯一上游 role=`output` artifact 物化该参数。
- 当前 `planning.simple.build_linear_execution_plan()` 已把 `WorkflowEdge` 转成 `depends_on_tasks`，但没有端口级 artifact 参数映射。
- 当前完整验证基线是 `.venv/Scripts/python -m unittest discover -s tests`，最近结果为 119 tests passed。
- `rg` 在本地环境曾返回 Windows `Access is denied`，文本搜索暂用 PowerShell `Select-String`。

## Constraints

- GUI 不参与本计划，不启动 Scheduler 或 worker。
- Scheduler 仍是资源绑定事实源；runner 不能绕过 `SimpleScheduler` claim。
- RuntimeManager 仍是 executable path / env / model path 解析事实源；runner 不能从全局 PATH 自行找工具。
- Worker / adapter 仍通过 WorkerEvent 写 SQLite，adapter 不直接写数据库。
- Artifact handoff 只能读取 SQLite 中已持久化且与上游 task 关联的 artifact，不扫描工作目录猜测文件。
- 第一版 artifact handoff 不解决多输出端口歧义；遇到歧义应显式失败或留给后续 phase，不静默猜测。
- 不引入 Celery、Redis、web stack 或新的持久队列技术。

## Execution Plan

### Phase A: Artifact handoff 查询

目标：
- 新增最小 artifact handoff helper，用于查询某个 task 的已持久化 output artifact。

完成信号：
- 可按 task id 查询 role=`output` 的 artifact path / type / id。
- 可按 `artifact_type` 过滤。
- 查询结果来自 `artifacts` + `task_artifacts`，不是文件系统扫描。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_backend_workflow_handoff
```

状态：

- 已完成首个轻度切片。

### Phase B: Downstream task 参数物化

目标：
- 在 dispatch 前为下游 task 注入必要 artifact 参数，例如把上游 `audio` artifact path 注入 `output.export.input_path`。

完成信号：
- 单上游单输出场景可自动生成 `input_path`。
- 多上游或多同类输出不静默选择，返回结构化 blocked / ambiguous result。
- 原始 persisted task params 不被 GUI callback 临时覆盖；物化发生在后端 runner 的 dispatch 准备边界。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_backend_workflow_handoff
```

状态：

- 已完成首版最小切片。

### Phase C: 最小 sequential workflow runner

目标：
- 新增后端 runner service，顺序推进一个 plan。

完成信号：
- fake `media.audio_extract -> output.export` workflow 可自动运行两步。
- runner 通过 `SimpleScheduler` claim，通过 `RuntimeManager` resolve runtime，通过 `dispatch_claimed_task()` 执行。
- 输出目录产生 final output artifact，SQLite 中记录上游 staged artifact 和下游 final output link。
- 失败时 runner 停止并返回 failed task facts。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_minimal_backend_workflow_runner
```

状态：

- 已完成首版最小切片。

### Phase D: Queue snapshot 对齐

目标：
- 让现有只读 GUI state reader 或新的 backend read model 能解释 runner 结果。

完成信号：
- 可读出 task 列表、状态、event count、artifact paths、final output path 和失败 facts。
- 不新增 GUI 按钮，不启动 Qt event loop 执行任务。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_gui_state_reader
```

状态：

- 已完成首版最小切片。

### Phase E: 文档对齐

目标：
- 更新 app code map、recent changes、main plan 和相关 spec 边界。

完成信号：
- `APP_CODE_MAP.md` 记录新增 handoff / runner service 和测试。
- `RECENT_CHANGES.md` 记录最小 backend workflow runner 边界。
- `plan_main_app_skeleton.md` child plan / progress 对齐。

验证：

```powershell
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

状态：

- 已完成首版文档对齐。

## Child Plans

- 后续可拆 `plan_gui_minimal_run_workflow_entry.md`，在本计划 runner 稳定后让 GUI 只提交 queue intent 和读取 snapshot。
- 后续可拆 `plan_ffmpeg_subtitle_mux_adapter.md`。
- 后续可拆 `plan_whisper_asr_adapter_foundation.md`。

## Verification

计划验证命令：

```powershell
.venv/Scripts/python -m unittest tests.test_backend_workflow_handoff
.venv/Scripts/python -m unittest tests.test_minimal_backend_workflow_runner
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

最近验证事实：

- `.venv\Scripts\python -m unittest tests.test_backend_workflow_handoff tests.test_minimal_backend_workflow_runner tests.test_gui_state_reader`：8 tests passed。
- `.venv\Scripts\python -m unittest discover -s tests`：119 tests passed。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed。
- `Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'`：no matches。
- `git diff --check`：passed，仅有 Windows CRLF conversion warnings。

## Progress / Decisions

- 2026-05-06：创建本计划。决策：下一阶段先做最小后端 workflow runner，不直接跳到 ASR/OCR/Translate 或 GUI 运行按钮。
- 2026-05-06：决策：轻度执行先落 Phase A artifact handoff 查询能力，因为它是多节点 workflow 自动推进的最小前置能力。
- 2026-05-06：完成 Phase A 首个轻度切片。新增 `TaskArtifactRecord` 和 `fetch_task_output_artifacts()`，测试覆盖 role=`output` artifact 查询和 `artifact_type` 过滤；尚未做 downstream params materialization。
- 2026-05-06：完成 Phase B 首版最小切片。新增 `scheduler/handoff.py`，`materialize_downstream_task_inputs()` 可为 `output.export` 注入唯一上游 output artifact 的 `input_path`，并在多候选时返回 `UPSTREAM_ARTIFACT_AMBIGUOUS`；尚未实现 full port-level mapping 或 runner loop。
- 2026-05-06：完成 Phase C 首版最小切片。新增 `scheduler/workflow_runner.py`，`run_sequential_workflow()` 可顺序 claim、物化、resolve runtime、dispatch，并跑通 fake `media.audio_extract -> output.export`；上游失败时 runner 停止且下游保持 pending。
- 2026-05-06：完成 Phase D 首版最小切片。`read_workbench_snapshot()` 现在可返回 `final_output_paths`、`failure_error_code`、`failure_message`；全量测试曾因 GUI smoke 手动构造 `WorkbenchTaskItem` 缺少新字段而失败，已通过默认值修复并复验通过。
- 2026-05-06：完成 Phase E 首版文档对齐。`APP_CODE_MAP.md`、`RECENT_CHANGES.md` 和 `plan_main_app_skeleton.md` 已记录 handoff、runner、GUI snapshot 读取边界与验证事实。

## Blockers

- 暂无。
