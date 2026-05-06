# Atelier 应用骨架主计划

> 本计划是首版应用骨架的主计划文档。它按照 `AGENTS.md` 的 Planning Discipline 维护：轻量、可更新、只记录已验证事实和真实约束。

## Objective（目标）

在不提前接入真实 GUI、真实模型和真实外部工具的前提下，搭建 Atelier 的首版可信代码骨架。

目标边界：

- 先确定文档契约、工程边界、runtime 目录模型和本地开发环境。
- 让 `WorkflowGraph -> ExecutionPlan -> Worker Events -> SQLite` 的最小闭环逐步可运行。
- 保持 GUI、WorkflowGraph、ExecutionPlan、Scheduler、RuntimeManager、Worker、Storage、Security 等职责分离。

## Scope（范围）

- 对齐首版 specs，确保 artifacts、cache hit、cancel、resource binding、runtime ownership、release/update、plugin、workspace、i18n、hardware scheduling、failure recovery、security/privacy 等基础契约不互相冲突。
- 建立 Python 包骨架、测试基线、SQLite schema 初始化、runtime manifest 管理、runtime health check、package hash 校验、开发 `.venv` 和 `AppPaths` 路径事实源。
- 保持根目录清爽：根目录文档只保留 `README.md`、`AGENTS.md`、`DESIGN.md`；计划与阶段文档放在 `docs/plan/`。
- 当前阶段已实现只读 PySide6 工作台壳，并开始实现 Worker JSON Lines 协议边界、事件流验证、`ExecutionTask -> task.json -> WorkerProcessSpec` 边界、最小 subprocess runner 边界、窄的 claimed-task dispatch seam、lifecycle runner 接口形状、增量 stdout 读取、startup/heartbeat timeout、最小 cancel control、protocol-error worker 终止、stderr 文件落盘，以及 claimed-task dispatch 对 lifecycle timeout/cancel/protocol-error 的 SQLite 持久化；真实 adapter 目前只覆盖 `metadata.probe`、`media.audio_extract` 和 `output.export` 的最小 fake/staged 后端闭环，仍不实现真实编辑型 GUI、生产级 Scheduler、完整生产级 worker lifecycle 行为、完整 FFmpeg/model adapters、打包发布链或插件加载链。

## Current Facts（当前事实）

- 项目名是 `Atelier`。
- 当前本地 Python 是 `Python 3.11.9`。
- `pyproject.toml` 要求 `requires-python = ">=3.11"`，当前硬依赖只有 `pydantic>=2.0`。
- `.venv/` 已创建，本地包已通过 `.venv/Scripts/python -m pip install -e .` editable install。
- 开发 `.venv/` 已通过 `.venv/Scripts/python -m pip install -e ".[gui]"` 安装 PySide6 6.11.0；PySide6 仍只属于 optional `gui` extra，不是 core hard dependency。
- `.venv/`、`venv/`、`.atelier/` 已加入 `.gitignore`。
- 当前已有 `atelier/` 包、`tests/` 测试目录、`pyproject.toml`、`docs/APP_CODE_MAP.md` 和 `docs/RECENT_CHANGES.md`。
- 当前已有 `AppPaths`，开发期默认数据目录为 `.atelier/AtelierData/`。
- 当前已有 app-level factories：`create_runtime_store(paths)`、`create_runtime_setup_service(paths)` 和 `open_app_database(paths)`。
- 当前已有 `RuntimeStore`、`RuntimeManager`、`RuntimeHealthChecker`、`RuntimeRegistrationService`、`RuntimeSetupSnapshot` service、package SHA-256 helper、SQLite schema 初始化和 simulated Worker；`RuntimeManifest` / `ModelAssetManifest` 已完成 Phase A 字段加固，可表达 runtime kind、profile kind、display name、platform、executable paths、library dirs、scoped env、backend tags、integrity metadata、model family、task types、compatible backends、size bytes 和 metadata。
- 当前已有 `atelier/gui/` 工作台壳：optional dependency entry、formal development launch entry、`MainWindow`、dock workspace panel specs、workspace layout store、SQLite read-only `WorkbenchSnapshot`，以及最小可操作 `Runtime Setup` dock。
- 当前已有 `atelier/workers/protocol.py`，支持单个 WorkerEvent 的 JSON Lines 编解码、最小 stdout event stream validation，并补齐 `LogEvent` / `HeartbeatEvent` 事件模型。
- 当前已有 `atelier/workers/runner.py`，支持可控 subprocess 命令、`--task-file`、`cwd`、env、stdout event stream validation、stderr capture、return code capture、保留 stderr/returncode 的 protocol-error exception、lifecycle runner 接口形状、增量 stdout 读取、startup/heartbeat timeout、最小 cancel control、protocol-error worker 终止和 stderr 文件落盘。
- 当前已有 `atelier/workers/task_file.py`，支持 `ExecutionTask` 写入 `task.json`，并生成 `WorkerProcessSpec`。
- 当前已有 `atelier/adapters/` 最小 adapter contract、built-in registry、typed command executor、`metadata.probe` / `FFprobeMetadataAdapter`、`media.audio_extract` / `FFmpegAudioExtractAdapter` 和 `output.export` / `ArtifactFinalizerAdapter`。
- 当前已有 `atelier/workers/adapter_entry.py`，可从 task.json 调用 built-in adapter 并输出 Worker JSON Lines。
- 当前已有 `atelier/scheduler/dispatch.py`，支持把已 claim 的 `ClaimedTask` 接到 `task.json`、stub worker runner / lifecycle runner 和 SQLite event/artifact/failure persistence，并返回结构化 dispatch result；已验证 completed、timeout、cancel、failed 和 protocol-error stub paths。当前已有 `atelier/scheduler/workflow_runner.py`，可顺序推进 fake `media.audio_extract -> output.export` 后端 workflow。当前 `WorkbenchSnapshot` 可读出 final output paths 和 failure code/message。
- 当前已有 `atelier/assets/`，作为 Atelier 主界面 toolbar、navigation、workflow nodes、queue、hardware、status、inspector 和 system 的 SVG 线性图标资源库。
- 当前验证基线是 `.venv/Scripts/python -m unittest discover -s tests`，最近一次结果为 119 tests passed。
- `rg` 在此环境曾返回 Windows `Access is denied`，文本搜索暂用 PowerShell `Select-String`。

## Constraints（约束）

- GUI 不得直接调用 FFmpeg、模型推理、CUDA、llama.cpp 或其他重型 backend。
- GUI 不得阻塞 Qt main event loop。
- Scheduler 是唯一能进行硬件资源绑定的组件。
- RuntimeManager 是唯一解析 executable path、backend path、model path 和 worker runtime env 的组件。
- `atelier/runtime/` 是 runtime 管理源码目录，不存放 runtime 二进制、模型或虚拟环境。
- 开发 `.venv/` 只服务本仓库开发，不是产品 App Runtime，也不提交。
- 发布后的 GUI runtime 属于 App Install Dir；工具/runtime/model/backend 数据属于 AtelierData。
- `runtime/` 和 `storage/` 不反向依赖 `app/`；由 app orchestration layer 负责接线。
- Worker 应通过结构化事件协议上报进度，当前首版使用 pydantic models 和 simulated Worker。
- SQLite 是 runtime state、events、artifacts、cache、recovery state 的首选持久层。
- `atelier/assets/` 是资源目录，不代表已经实现 Qt `.qrc`、IconManager、图标缓存或运行时主题重染色。
- 不假设全局安装 FFmpeg、CUDA tools、llama.cpp、whisper.cpp、模型文件或开发机路径。
- 不硬编码 `cuda:0` 作为默认策略。
- 不提交 secrets、API keys、bearer tokens、模型 provider credentials 或本地 runtime 数据。

## Execution Plan（执行计划）

### Phase 1：文档契约对齐

目标：

- 让现有 specs 在 runtime ownership、artifact/cache、cancel semantics、resource binding 等关键概念上保持一致。

完成信号：

- specs 明确 RuntimeManager ownership。
- cache-hit artifacts 可关联到 consuming task。
- cancel semantics 能映射到 `TaskStatus.CANCELLED`。
- resource binding 有单一事实源。

验证：

- `git diff --check`
- 使用 `Select-String` 复查关键术语。

状态：

- 已完成。

### Phase 2：骨架设计确认

目标：

- 在创建生产代码前确认模块布局、runtime environment strategy 和首版边界。

完成信号：

- 用户确认 module layout、runtime strategy 和先搭骨架的方向。

验证：

- 代码骨架创建前已完成设计确认。

状态：

- 已完成。

### Phase 3：首版代码骨架

目标：

- 创建不接真实 GUI、真实模型、真实外部工具的首版可执行 Python skeleton。

完成信号：

- `atelier/` package 存在，并包含 `app`、`core`、`domain`、`runtime`、`storage`、`workers` 等基础边界。
- `pyproject.toml` 描述项目包和未来依赖方向。
- stdlib `unittest` 覆盖 worker events、runtime binding、runtime manifest storage、runtime health checks、package hash checks、SQLite 初始化和 simulated Worker。
- 没有 GUI callback、model inference、FFmpeg call 或 global runtime path assumption。

验证：

- `python -m unittest discover -s tests`
- `python -m compileall -q atelier tests`
- `git diff --check`

状态：

- 已完成。

### Phase 4：开发环境与 AppPaths

目标：

- 建立可复现的本地开发环境，并建立 development data、runtime manifests、cache、logs、SQLite 的单一路径事实源。

完成信号：

- `.venv/` 可在本地运行当前测试套件。
- `.venv/`、`venv/`、`.atelier/` 被 git 忽略。
- `AppPaths` 定义开发期 `.atelier/AtelierData/` 布局。
- tests 覆盖路径布局和目录创建行为。

验证：

- `.venv/Scripts/python -m pip install -e .`
- `.venv/Scripts/python -m unittest discover -s tests`
- `.venv/Scripts/python -m compileall -q atelier tests`
- `git diff --check`

状态：

- 已完成。

### Phase 5：AppPaths 集成

目标：

- 通过 app orchestration layer 把 `AppPaths` 接到 `RuntimeStore` 和 SQLite database opening。

完成信号：

- `create_runtime_store(paths)` 使用 `AppPaths.data_root` 创建 `RuntimeStore`。
- `open_app_database(paths)` 使用 `AppPaths.database_path`，创建父目录并初始化 SQLite schema。
- `runtime/` 和 `storage/` 不 import `app/`。

验证：

- `.venv/Scripts/python -m unittest tests.test_app_services`
- `.venv/Scripts/python -m unittest discover -s tests`
- `.venv/Scripts/python -m compileall -q atelier tests`
- `git diff --check`

状态：

- 已完成。

### Phase 6：最小业务闭环

目标：

- 实现最小 `WorkflowGraph -> ExecutionPlan -> simulated Worker -> SQLite events/artifacts` 路径。

完成信号：

- 新增最小 `workflow/` domain 或 schema，能表达一个 sample workflow。
- 新增最小 `planning/` 转换器，把 sample workflow 转为 `ExecutionTask`。
- simulated Worker events 能被持久化到 SQLite `task_events`。
- artifact event 能产生或记录到 `artifacts` / `task_artifacts` 的最小写入路径。
- 所有新行为有测试，并先看到失败再实现。

验证：

- `.venv/Scripts/python -m unittest discover -s tests`
- `.venv/Scripts/python -m compileall -q atelier tests`
- `git diff --check`

状态：

- 已完成首版最小闭环。

说明：

- 当前 Phase 6 只覆盖 sample workflow、simple planner、simulated Worker、SQLite events/artifacts。
- queue、Scheduler、真实 worker subprocess、failure recovery action 尚未进入本阶段。

### Phase 7：最小 Queue / Scheduler

目标：

- 在不实现真实并发和外部 worker subprocess 的前提下，建立最小 queue claim 和 Scheduler 资源绑定路径。

完成信号：

- Scheduler 能从 SQLite 找到依赖已满足的 pending task。
- Scheduler 为 runnable task 生成 `ResourceBinding`。
- 被 claim 的 task 状态更新为 `running`，并持久化 resource binding。
- 有依赖的下游 task 在上游完成前不会被 claim。
- 上游 task 完成并记录 worker events 后，下游 task 可被 claim。

验证：

- `.venv/Scripts/python -m unittest tests.test_scheduler_simple`
- `.venv/Scripts/python -m unittest discover -s tests`
- `.venv/Scripts/python -m compileall -q atelier tests`
- `git diff --check`

状态：

- 已完成首版最小 queue / Scheduler claim。

说明：

- 当前 Phase 7 只覆盖 dependency-ready pending task claim、CPU resource binding 和 task running 状态持久化。
- durable queue claiming、resource locks、priority scheduling、concurrency、retries 和 recovery 尚未进入本阶段。

## Child Plans（子计划）

- [plan_resource_locks_failure_recovery.md](./plan_resource_locks_failure_recovery.md)：第 1 个后续子计划。补 resource locks、terminal event lock release、failure facts、recovery options 和 stale lock 检测。
- [plan_readonly_pyside6_workbench.md](./plan_readonly_pyside6_workbench.md)：第 2 个后续子计划。建立只读 PySide6 工作台壳，读取 SQLite / runtime / queue 状态并展示，不执行重型任务。
- [plan_worker_protocol_runner.md](./plan_worker_protocol_runner.md)：第 3 个后续子计划。补 Worker JSON Lines 协议编解码、event stream validation 和未来 subprocess runner 边界。
- [plan_scheduler_worker_runner_integration.md](./plan_scheduler_worker_runner_integration.md)：第 4 个后续子计划。把 Scheduler claim、task file、runner 和 SQLite event persistence 接成 stub worker 闭环。
- [plan_worker_lifecycle_controls.md](./plan_worker_lifecycle_controls.md)：第 5 个后续子计划。补 timeout、cancel、terminate/kill escalation 和 stderr 文件落盘。
- [plan_scheduler_lifecycle_dispatch_integration.md](./plan_scheduler_lifecycle_dispatch_integration.md)：第 6 个后续子计划。把 lifecycle runner 的 timeout、cancel、stderr log 和 protocol-error 收束能力接回 Scheduler dispatch seam。
- [plan_runtime_management_foundation.md](./plan_runtime_management_foundation.md)：第 7 个后续子计划。在真实 workflow 前补 runtime manifest、local runtime/model registration、health check、RuntimeBinding resolution 和 GUI snapshot。
- [plan_initial_actionable_gui_runtime_setup.md](./plan_initial_actionable_gui_runtime_setup.md)：第 8 个后续子计划。在 Runtime 管理骨架完成后，让 GUI 具备最小 runtime setup 操作面。
- [plan_minimal_adapter_probe_workflow.md](./plan_minimal_adapter_probe_workflow.md)：第 9 个后续子计划。在 Runtime 管理骨架完成后，接入最简 metadata.probe / ffprobe adapter workflow。
- [plan_ffmpeg_audio_extract_adapter.md](./plan_ffmpeg_audio_extract_adapter.md)：第 10 个后续子计划。在 metadata probe 跑通后，接入第一个产物型 `media.audio_extract` / FFmpeg audio adapter workflow。
- [plan_output_export_finalizer.md](./plan_output_export_finalizer.md)：第 11 个后续子计划。在 staged artifact workflow 跑通后，接入最小 `output.export` / final output link。
- [plan_minimal_backend_workflow_runner.md](./plan_minimal_backend_workflow_runner.md)：第 12 个后续子计划。把单节点 adapter dispatch 推进为最小多节点后端 workflow runner。

执行顺序：

1. 先执行 `plan_resource_locks_failure_recovery.md`，让后端执行状态更可信。
2. 再执行 `plan_readonly_pyside6_workbench.md`，让 GUI 读取更完整的只读状态。
3. 再执行 `plan_worker_protocol_runner.md`，让未来真实 Worker subprocess 接入前先有可验证协议边界。
4. 再执行 `plan_scheduler_worker_runner_integration.md`，先用 stub worker 形成 Scheduler 到 runner 到 SQLite 的闭环。
5. 再执行 `plan_worker_lifecycle_controls.md`，处理 timeout、cancel、kill escalation 和 stderr 文件落盘。
6. 再执行 `plan_scheduler_lifecycle_dispatch_integration.md`，把 lifecycle runner 结果接回 claimed-task dispatch seam。
7. 再执行 `plan_runtime_management_foundation.md`，先把 runtime/model/tool profile、health check 和 RuntimeBinding 管理立稳。
8. 再执行 `plan_initial_actionable_gui_runtime_setup.md`，让 GUI 具备最小 runtime setup 操作面。
9. 再执行 `plan_minimal_adapter_probe_workflow.md`，用 metadata probe 跑通首个最简真实 adapter workflow。
10. 再执行 `plan_ffmpeg_audio_extract_adapter.md`，用 audio extract 跑通首个 staged audio artifact workflow。
11. 再执行 `plan_output_export_finalizer.md`，把 staged artifact 安全复制为 final output artifact。
12. 再执行 `plan_minimal_backend_workflow_runner.md`，让上游 artifact 能进入下游任务，并形成最小 claim / dispatch / persist loop。

如后续某一阶段继续变复杂，例如 Worker protocol、Plugin system 或 ReleaseManager 需要独立拆分，再新增 `docs/plan/plan_<topic>.md`。

## Verification（验证）

当前验证命令：

```powershell
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

当前最近验证事实：

- `.venv/Scripts/python -m unittest discover -s tests`：119 tests passed。
- `.venv/Scripts/python -m compileall -q atelier tests`：passed。
- `git diff --check`：passed，仅有 Windows CRLF conversion warnings。

项目未来配置完成后，再启用：

```powershell
python -m pytest
python -m ruff check .
python -m mypy .
```

在这些工具未配置前，不声称它们已通过。

## Progress / Decisions（进展 / 决策）

- 2026-05-03：创建本计划，用于首版文档契约和应用骨架工作。
- 2026-05-03：补齐 RuntimeManager ownership、RuntimeRequirement / RuntimeBinding、cache/runtime fingerprints、task_artifacts 和 cancel/resource-binding 规则。
- 2026-05-03：新增 release/update、runtime environment、plugin system、UI workspace、i18n specs。
- 2026-05-03：新增 hardware scheduling、failure recovery、security/privacy specs。
- 2026-05-03：完成跨文档对齐，补充 ReleaseManager、SecurityManager、credential_refs、INTERRUPTED worker error code。
- 2026-05-03：用户确认开始搭建 skeleton。当前本地可用 Python 3.11 和 pydantic v2；首版使用 stdlib `unittest` / `sqlite3` 加 pydantic models，未来依赖写入 `pyproject.toml` optional groups。
- 2026-05-03：搭建首版 executable skeleton：`pyproject.toml`、package boundaries、pydantic domain models、SQLite schema 初始化、RuntimeManager binding、simulated Worker events 和 unittest coverage。
- 2026-05-03：优先补 runtime foundation：`RuntimeStore`、`RuntimeHealthChecker`、package SHA-256 helpers，并按 TDD 先写测试。
- 2026-05-03：新增 `docs/APP_CODE_MAP.md` 和 `docs/RECENT_CHANGES.md`，作为代码结构地图和持久变更记忆。
- 2026-05-03：明确 `.venv/`、`.atelier/AtelierData/`、release App Runtime、managed AtelierData runtime directory 的边界。
- 2026-05-03：创建本地 `.venv/`，执行 editable install，并新增 `AppPaths` 作为 development/user data path 的首个单一事实源。
- 2026-05-03：新增 app-level factories：从 `AppPaths` 创建 `RuntimeStore`，并打开初始化后的 SQLite connection，同时保持 lower layers 不依赖 `app/`。
- 2026-05-03：按用户要求对照 `AGENTS.md` 重写本计划：保留主计划九段结构，正文改为中文，并补齐当前事实、验证事实和 Phase 6。
- 2026-05-03：完成 Phase 6 首版最小业务闭环：新增 minimal `workflow/`、simple `planning/`、SQLite repository helpers，并验证 `WorkflowGraph -> ExecutionPlan -> simulated Worker -> SQLite events/artifacts`。
- 2026-05-03：完成 Phase 7 首版 queue / Scheduler claim：新增 `SimpleScheduler`，验证只 claim 依赖满足的 pending task，并持久化 `ResourceBinding` 和 `running` 状态。
- 2026-05-03：按后续实施顺序拆出两个子计划：先 `resource_locks + failure recovery`，再只读 PySide6 工作台壳。
- 2026-05-03：`plan_resource_locks_failure_recovery.md` 已执行到 Phase C：resource lock claim/release、failure facts、partial artifacts 和 recovery option 查询已具备首版测试覆盖。
- 2026-05-03：`plan_resource_locks_failure_recovery.md` 已完成 Phase D：stale resource lock 可以被查询和释放，但不会自动改变 task status 或触发任务重跑。
- 2026-05-03：补充 Phase D stale release 防护测试：未过期 lock 和已释放 lock 不会被 stale release 路径释放。
- 2026-05-03：完成 `plan_readonly_pyside6_workbench.md` Phase A-D。安装开发期 GUI extras，新增只读 PySide6 `MainWindow`、dock workspace panel specs 和 SQLite read-only state reader；GUI 只渲染状态，不启动 worker 或 Scheduler。
- 2026-05-03：完成 `plan_readonly_pyside6_workbench.md` Phase E。新增最小 workspace layout persistence，`MainWindow` 可保存/恢复 Qt geometry/state，布局文件位于 managed `AtelierData/cache`。
- 2026-05-03：完成 `plan_readonly_pyside6_workbench.md` Phase F。新增正式开发启动入口 `.venv/Scripts/python -m atelier.gui.app`，保持只读启动链，不触发 Scheduler 或 worker。
- 2026-05-03：创建并执行 `plan_worker_protocol_runner.md` Phase A。新增 WorkerEvent JSON Lines 单事件编解码，补齐 `LogEvent` / `HeartbeatEvent`，并将 `WORKER_PROTOCOL.md` 标记为部分实现。
- 2026-05-04：完成 `plan_worker_protocol_runner.md` Phase B。新增最小 stdout event stream validation，验证 `started` 首事件、`seq` 连续、terminal event 结束和 terminal 后禁止追加事件。
- 2026-05-04：完成 `plan_worker_protocol_runner.md` Phase C。新增最小 subprocess runner 边界，可用 stub worker 验证 `--task-file`、`cwd`、env、stdout JSON Lines、stderr 和 return code。
- 2026-05-04：扩展并完成 `plan_worker_protocol_runner.md` Phase E。新增 `ExecutionTask -> task.json -> WorkerProcessSpec` 边界，为后续 Scheduler 接 runner 做前置准备。
- 2026-05-04：新增后续两个计划：先执行 `plan_scheduler_worker_runner_integration.md`，再执行 `plan_worker_lifecycle_controls.md`。
- 2026-05-04：完成 `plan_scheduler_worker_runner_integration.md` Phase A。新增窄的 `dispatch_claimed_task()` 接口形状，连接已 claim task、`task.json`、runner 和 SQLite event persistence；artifact 闭环、failed 路径和 protocol-error 转失败仍留给后续 Phase B/C。
- 2026-05-04：完成 `plan_scheduler_worker_runner_integration.md` Phase B。completed stub worker 路径已验证 `task_events`、`artifacts`、`task_artifacts`、completed status 和 active resource lock release；failed 路径和 protocol-error 转失败仍留给 Phase C。
- 2026-05-04：完成 `plan_scheduler_worker_runner_integration.md` Phase C。valid failed stream 和 malformed stdout protocol error 都会持久化失败事实并释放 active resource lock；timeout、cancel、kill escalation 和 stderr 文件落盘仍留给后续 lifecycle controls。
- 2026-05-04：开始并完成 `plan_worker_lifecycle_controls.md` Phase A。新增 lifecycle runner 配置、结果对象和兼容现有最小 runner 行为的入口；增量 stdout、timeout、cancel、kill escalation 和 stderr 文件落盘仍未实现。
- 2026-05-04：完成 `plan_worker_lifecycle_controls.md` Phase B。`run_worker_lifecycle()` 开始增量读取 stdout，并把 silent worker 的 startup/heartbeat timeout 转为结构化 `TIMEOUT` 失败事件；取消语义和 stderr 文件落盘仍未实现。
- 2026-05-04：完成 `plan_worker_lifecycle_controls.md` Phase C/D/E。runner 已支持最小 stdin cancel、cancel grace 后 terminate/kill、可选 stderr log path，并更新协议与接手文档；GUI/Scheduler 取消接线和真实 adapters 仍未实现。
- 2026-05-04：完成 `plan_worker_lifecycle_controls.md` Phase F。lifecycle runner 遇到 malformed stdout / protocol error 会先终止 worker，再抛出保留 stderr/returncode 的 `WorkerProcessProtocolError`，并支持 stderr log path。
- 2026-05-04：新增 `plan_scheduler_lifecycle_dispatch_integration.md`，作为 worker lifecycle controls 之后的下一个计划。
- 2026-05-04：完成 `plan_scheduler_lifecycle_dispatch_integration.md` Phase A。`dispatch_claimed_task()` 可选接入 lifecycle runner，并返回 stderr log path 与 lifecycle flags；timeout/cancel/protocol-error dispatch 持久化仍留给后续 phases。
- 2026-05-05：完成 `plan_scheduler_lifecycle_dispatch_integration.md` Phase B-D。timeout、cancel-aware worker、stuck cancel worker 和 lifecycle protocol-error 都已在 claimed-task dispatch seam 中验证能持久化 terminal failure facts、归一化 task status，并释放 active resource lock；GUI 取消、自动 claim loop、真实 adapters 和 retry/recovery action execution 仍未实现。
- 2026-05-05：完成 `plan_scheduler_lifecycle_dispatch_integration.md` Phase E。接手文档已对齐；完整验证为 71 tests passed，`compileall` passed，`git diff --check` passed with CRLF warnings only。
- 2026-05-05：新增后续三个计划：先执行 `plan_runtime_management_foundation.md`，再执行 `plan_initial_actionable_gui_runtime_setup.md`，再执行 `plan_minimal_adapter_probe_workflow.md`。决策：真实 workflow 前必须先补 Runtime 管理骨架，避免 adapter 从全局 PATH 或 GUI callback 直接找工具。
- 2026-05-05：完成 `plan_runtime_management_foundation.md` Phase A。runtime/model manifest 字段已加固并保持旧 manifest 兼容；完整验证为 72 tests passed，`compileall` passed，`git diff --check` passed with CRLF warnings only。
- 2026-05-05：完成 `plan_runtime_management_foundation.md` Phase B。新增 manifest-only local runtime/model profile registration，可登记 ffprobe/ffmpeg、python.worker-dev 和 demo model directory；完整验证为 75 tests passed，`compileall` passed，`git diff --check` passed with CRLF warnings only。
- 2026-05-05：完成 `plan_runtime_management_foundation.md` Phase C。runtime health report 已有 repair hints，health checker 支持 caller-provided safe dry-run probe args；完整验证为 76 tests passed，`compileall` passed，`git diff --check` passed with CRLF warnings only。
- 2026-05-05：完成 `plan_runtime_management_foundation.md` Phase D。RuntimeManager resolution 已有 `RuntimeResolutionError(subject_id, reason)` 诊断和 manifest-scoped env binding；完整验证为 79 tests passed，`compileall` passed，`git diff --check` passed with CRLF warnings only。
- 2026-05-05：完成 `plan_runtime_management_foundation.md` Phase E。新增 RuntimeSetupSnapshot service，为后续 GUI runtime setup 面板提供只读 runtime/model health snapshot。
- 2026-05-05：完成 `plan_runtime_management_foundation.md` Phase F。Runtime 管理骨架接手文档已对齐；完整验证为 80 tests passed，`compileall` passed，`git diff --check` passed with CRLF warnings only。
- 2026-05-05：完成 `plan_initial_actionable_gui_runtime_setup.md` Phase A-D。GUI 现在有最小 `Runtime Setup` dock，可显示 runtime/model snapshot，通过 app service 登记本地 `ffprobe`、`ffmpeg`、Worker Python 和 demo model directory，并显示注册诊断；完整验证为 87 tests passed，`compileall` passed，`git diff --check` passed with CRLF warnings only。
- 2026-05-05：完成 `plan_minimal_adapter_probe_workflow.md` Phase A-F。首个真实 adapter 链路已跑通：fake ffprobe `metadata.probe` workflow 通过 RuntimeManager binding、adapter worker entrypoint、Worker JSON Lines 和 SQLite event/artifact persistence 完成后端闭环。
- 2026-05-06：新增并执行 `plan_ffmpeg_audio_extract_adapter.md` Phase A/B。首个产物型 adapter 链路已跑通：fake FFmpeg `media.audio_extract` workflow 通过 RuntimeManager binding、adapter worker entrypoint、Worker JSON Lines 和 SQLite event/artifact persistence 生成 staged `audio.wav` artifact。
- 2026-05-06：新增并执行 `plan_output_export_finalizer.md` Phase A-C。最小 `output.export` 链路已跑通：existing staged artifact 可安全复制到用户输出目录，产生 final output artifact，并在 SQLite 中记录 `task_artifacts.role = final_output`；adapter、artifact lifecycle、worker protocol、code map 和 recent changes 文档已对齐。
- 2026-05-06：新增 `plan_minimal_backend_workflow_runner.md`，并轻度执行 Phase A。新增 `fetch_task_output_artifacts()`，可从 SQLite 查询上游 task 的 role=`output` artifact，为后续 downstream params materialization 和最小 backend runner 做前置。
- 2026-05-06：继续执行 `plan_minimal_backend_workflow_runner.md` Phase B。新增 `scheduler/handoff.py`，可为 `output.export` 从唯一上游 output artifact 物化 `input_path`，遇到多候选时返回 `UPSTREAM_ARTIFACT_AMBIGUOUS` blocked result。
- 2026-05-06：继续执行 `plan_minimal_backend_workflow_runner.md` Phase C。新增 `scheduler/workflow_runner.py`，可通过 `SimpleScheduler -> RuntimeManager -> dispatch_claimed_task()` 顺序跑通 fake `media.audio_extract -> output.export`，并在上游失败时停止。
- 2026-05-06：继续执行 `plan_minimal_backend_workflow_runner.md` Phase D。扩展 `WorkbenchSnapshot`，可读出 final output paths 和 failure code/message；新增字段带默认值以保持 GUI smoke 手动构造兼容。
- 2026-05-06：收口 `plan_minimal_backend_workflow_runner.md` Phase E。文档地图、recent changes 和主计划已对齐最小 backend runner、artifact handoff、GUI snapshot 读取事实与验证基线。

## Blockers（阻塞）

- 暂无。
