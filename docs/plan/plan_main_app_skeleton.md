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
- 当前阶段只实现只读 PySide6 工作台壳，不实现真实编辑型 GUI、真实 Scheduler、真实 FFmpeg/model adapters、打包发布链或插件加载链。

## Current Facts（当前事实）

- 项目名是 `Atelier`。
- 当前本地 Python 是 `Python 3.11.9`。
- `pyproject.toml` 要求 `requires-python = ">=3.11"`，当前硬依赖只有 `pydantic>=2.0`。
- `.venv/` 已创建，本地包已通过 `.venv/Scripts/python -m pip install -e .` editable install。
- 开发 `.venv/` 已通过 `.venv/Scripts/python -m pip install -e ".[gui]"` 安装 PySide6 6.11.0；PySide6 仍只属于 optional `gui` extra，不是 core hard dependency。
- `.venv/`、`venv/`、`.atelier/` 已加入 `.gitignore`。
- 当前已有 `atelier/` 包、`tests/` 测试目录、`pyproject.toml`、`docs/APP_CODE_MAP.md` 和 `docs/RECENT_CHANGES.md`。
- 当前已有 `AppPaths`，开发期默认数据目录为 `.atelier/AtelierData/`。
- 当前已有 app-level factory：`create_runtime_store(paths)` 和 `open_app_database(paths)`。
- 当前已有 `RuntimeStore`、`RuntimeManager`、`RuntimeHealthChecker`、package SHA-256 helper、SQLite schema 初始化和 simulated Worker。
- 当前已有只读 `atelier/gui/` 工作台壳：optional dependency entry、`MainWindow`、dock workspace panel specs、SQLite read-only `WorkbenchSnapshot`。
- 当前验证基线是 `.venv/Scripts/python -m unittest discover -s tests`，最近一次结果为 36 tests passed。
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

执行顺序：

1. 先执行 `plan_resource_locks_failure_recovery.md`，让后端执行状态更可信。
2. 再执行 `plan_readonly_pyside6_workbench.md`，让 GUI 读取更完整的只读状态。

如后续某一阶段继续变复杂，例如 Worker protocol、Plugin system 或 ReleaseManager 需要独立拆分，再新增 `docs/plan/plan_<topic>.md`。

## Verification（验证）

当前验证命令：

```powershell
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

当前最近验证事实：

- `.venv/Scripts/python -m unittest discover -s tests`：36 tests passed。
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

## Blockers（阻塞）

- 暂无。
