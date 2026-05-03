# Scheduler Worker Runner 接线计划

> 执行顺序：第 1 个后续计划。建议在 `plan_worker_protocol_runner.md` Phase E 完成后执行，让已经存在的 Scheduler claim、task file、runner 和 SQLite event persistence 形成首个可验证闭环。

## Objective（目标）

建立首版 `Scheduler -> task.json -> Worker runner -> WorkerEvent -> SQLite` 接线路径。该路径只使用可控 stub worker，不接真实 FFmpeg/model adapter，不做生产级并发和生命周期控制。

目标链路：

```text
SimpleScheduler.claim_next_task()
  -> build_worker_process_spec()
  -> run_worker_process()
  -> record_worker_events()
  -> SQLite task_events / artifacts / task status / resource lock release
```

## Scope（范围）

- 新增一个窄的 orchestration helper，用于把已 claim 的 `ExecutionTask` 交给 runner。
- 使用已存在的 `build_worker_process_spec()` 写入 `task.json`。
- 使用已存在的 `run_worker_process()` 运行可控 stub worker。
- 使用已存在的 `record_worker_events()` 写入 SQLite。
- 测试 completed、failed 和 protocol-error 三类结果。
- 更新 `APP_CODE_MAP.md`、`RECENT_CHANGES.md` 和主计划。

暂不实现：

- 真实 FFmpeg/ffprobe/model adapters。
- RuntimeManager 自动选择 command args。
- 多 worker 并发调度。
- priority scheduling。
- heartbeat timeout、cancel、kill escalation。
- stderr 文件落盘和 GUI log 面板。
- retry/recovery action 执行。

## Current Facts（当前事实）

- `SimpleScheduler` 已能 claim dependency-ready pending task，并写入 `running` 状态、`ResourceBinding` 和 active resource lock。
- `write_worker_task_file()` / `build_worker_process_spec()` 已能写入 `task.json` 并生成 `WorkerProcessSpec`。
- `run_worker_process()` 已能启动可控 subprocess，捕获 stdout/stderr/return code，并验证 stdout JSON Lines。
- `record_worker_events()` 已能持久化 worker events、artifacts、terminal status，并释放 active resource locks。
- 当前测试基线是 stdlib `unittest`，最近完整验证为 55 tests passed。

## Constraints（约束）

- GUI 不参与本计划。
- Scheduler 仍是 resource binding 的唯一来源。
- RuntimeManager 仍是 runtime/model path 解析的唯一来源；本计划不伪造真实 runtime resolution。
- Runner 不应写 SQLite；SQLite 写入仍通过 storage repository。
- 本计划只能使用 stub worker。
- 对 protocol error 的处理必须记录为失败事实，不能静默吞掉。
- 不把 subprocess lifecycle 的 timeout/cancel/kill 逻辑塞进本计划。

## Execution Plan（执行计划）

### Phase A：接线接口形状

目标：

- 定义一个最小 dispatch helper，输入为 SQLite connection、claimed task、work root、command args 和 optional env。

完成信号：

- helper 不自行 claim task。
- helper 不自行选择 runtime/model/hardware。
- helper 返回结构化 dispatch result，包含 task id、events、stderr、returncode 和最终 task status。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_scheduler_worker_runner_integration
```

状态：

- 待执行。

### Phase B：completed stub worker 路径

目标：

- 用 stub worker 产出 valid `started -> artifact -> completed` event stream，并通过 storage 写入 SQLite。

完成信号：

- `task_events` 包含 stub worker 事件。
- `artifacts` / `task_artifacts` 记录 artifact。
- task status 变为 `completed`。
- active resource lock 被释放。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_scheduler_worker_runner_integration
```

状态：

- 待执行。

### Phase C：failed 和 protocol error 路径

目标：

- 确认失败路径不会留下“永远 running”的 task 或 unreleased lock。

完成信号：

- valid `failed` terminal event 会持久化 error facts，task status 变为 `failed`，active lock 被释放。
- protocol error 会转换为结构化 `FailedEvent(error_code="INTERNAL" 或 "INTERRUPTED")` 再持久化，而不是只抛异常给上层。
- stderr 被保留在 dispatch result，后续可接 stderr 文件落盘。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_scheduler_worker_runner_integration
```

状态：

- 待执行。

### Phase D：文档状态对齐

目标：

- 更新接手文档，明确当前已经有 stub worker dispatch 闭环，但生产级 worker lifecycle 仍未实现。

完成信号：

- `APP_CODE_MAP.md`、`RECENT_CHANGES.md`、主计划更新。
- 不把真实 adapters、timeout、cancel 或 GUI execution 误写成已完成。

验证：

```powershell
git diff --check
```

状态：

- 待执行。

## Child Plans（子计划）

- [plan_worker_lifecycle_controls.md](./plan_worker_lifecycle_controls.md)：第 2 个后续计划。处理 timeout、cancel、kill escalation 和 stderr 文件落盘。

## Verification（验证）

计划验证命令：

```powershell
.venv/Scripts/python -m unittest tests.test_scheduler_worker_runner_integration
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

## Progress / Decisions（进展 / 决策）

- 2026-05-04：创建本计划。决策：先用 stub worker 打通 Scheduler 到 runner 到 SQLite 的首个闭环，再进入生产级 lifecycle controls。

## Blockers（阻塞）

- 暂无。
