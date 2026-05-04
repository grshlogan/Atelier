# Scheduler Lifecycle Dispatch Integration 计划

> 执行顺序：第 6 个后续计划。建议在 `plan_worker_lifecycle_controls.md` 完成后执行，把 lifecycle runner 的 timeout、cancel、stderr log 和 protocol-error 收束能力接回 Scheduler dispatch seam。

## Objective（目标）

让当前 `Scheduler -> task.json -> Worker runner -> SQLite` 的窄接线 helper 使用 lifecycle runner 能力，而不是只使用一次性 `subprocess.run()` 最小 runner。

目标链路：

```text
SimpleScheduler.claim_next_task()
  -> dispatch_claimed_task()
  -> build_worker_process_spec()
  -> run_worker_lifecycle()
  -> record_worker_events()
  -> SQLite task_events / artifacts / task status / resource lock release
  -> WorkerDispatchResult lifecycle facts
```

## Scope（范围）

- 扩展 `dispatch_claimed_task()`，允许传入 lifecycle config、cancel event 和 stderr log path。
- 让 dispatch result 暴露 stderr log path、timed_out、cancelled、killed 等 lifecycle facts。
- 验证 completed、timeout、cancel 和 protocol-error 路径都能持久化正确 task 状态并释放 resource lock。
- 更新 `WORKER_PROTOCOL.md`、`APP_CODE_MAP.md`、`RECENT_CHANGES.md` 和主计划。

暂不实现：

- 自动 claim loop。
- 多 worker 并发。
- GUI 取消按钮。
- retry/recovery action 执行。
- 真实 FFmpeg/model adapters。
- RuntimeManager 自动选择 command args。
- OS job object / process tree 完整治理。

## Current Facts（当前事实）

- `dispatch_claimed_task()` 当前已经能接收已 claim task、写 `task.json`、运行 stub worker、持久化 worker events，并释放 terminal event 对应的 active resource lock。
- `run_worker_lifecycle()` 当前支持增量 stdout、startup/heartbeat timeout、最小 cancel control、terminate/kill escalation、protocol-error worker 收束和 stderr log path。
- `dispatch_claimed_task()` 当前仍调用 `run_worker_process()`，因此不能使用 lifecycle timeout、cancel 或 stderr log path。
- 当前完整验证基线为 66 tests passed。

## Constraints（约束）

- GUI 不参与本计划。
- Scheduler 仍是 resource binding 的唯一来源。
- Dispatch helper 不自行 claim task，不选择 runtime/model/hardware。
- Runner 不直接写 SQLite；SQLite 写入仍通过 storage repository。
- 本计划仍只使用 stub worker。
- timeout/cancel/protocol-error 必须转成可持久化的结构化 worker event 或 dispatch result facts，不能让 task 永远停留在 `running`。

## Execution Plan（执行计划）

### Phase A：completed lifecycle dispatch 形状

目标：

- 让 `dispatch_claimed_task()` 能使用 lifecycle runner，并在 completed stub worker 路径返回 stderr log path 和 lifecycle flags。

完成信号：

- completed stub worker 仍写入 `started -> completed`。
- result 暴露 `stderr_log_path`、`timed_out=False`、`cancelled=False`、`killed=False`。
- stderr log 文件存在，且主事件事实仍来自 stdout JSON Lines。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_scheduler_worker_runner_integration
```

状态：

- 已完成。

### Phase B：timeout lifecycle dispatch 路径

目标：

- silent worker 超过 lifecycle timeout 后，dispatch 持久化 `FailedEvent(error_code="TIMEOUT")` 并释放 resource lock。

完成信号：

- task status 变为 `failed`。
- failure facts 为 `TIMEOUT`。
- result `timed_out=True`。
- active resource lock 被释放。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_scheduler_worker_runner_integration
```

状态：

- 待执行。

### Phase C：cancel lifecycle dispatch 路径

目标：

- cancel-aware worker 或忽略 cancel 的 worker 都不会留下 running task 或 active lock。

完成信号：

- cancel-aware worker 上报 `CANCELLED` 后 task status 归一为 `cancelled`。
- stuck worker 被 terminate/kill 后也记录 `CANCELLED` failure event。
- result `cancelled=True`，active resource lock 被释放。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_scheduler_worker_runner_integration
```

状态：

- 待执行。

### Phase D：protocol-error lifecycle dispatch 路径

目标：

- malformed stdout worker 被 lifecycle runner 收束后，dispatch 仍记录为结构化 internal failure，并保留 stderr log。

完成信号：

- task status 变为 `failed`。
- failure facts 为 `INTERNAL`。
- result stderr / stderr log path 可用于后续 Queue Monitor。
- active resource lock 被释放。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_scheduler_worker_runner_integration
```

状态：

- 待执行。

### Phase E：文档状态对齐

目标：

- 更新接手文档，明确 dispatch 已接入 lifecycle runner，但真实 adapters、自动 claim loop、GUI cancel 和 retry/recovery action 仍未实现。

完成信号：

- `WORKER_PROTOCOL.md`、`APP_CODE_MAP.md`、`RECENT_CHANGES.md` 和主计划更新。

验证：

```powershell
git diff --check
```

状态：

- 待执行。

## Child Plans（子计划）

- 暂无。

真实 adapters、GUI cancellation、retry/recovery orchestration 或 process tree governance 进入实现前，应再拆独立计划。

## Verification（验证）

计划验证命令：

```powershell
.venv/Scripts/python -m unittest tests.test_scheduler_worker_runner_integration
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

## Progress / Decisions（进展 / 决策）

- 2026-05-04：创建本计划。决策：先把 lifecycle runner 接回现有 claimed-task dispatch seam，再考虑自动 dispatch loop、GUI cancel 或真实 adapters。
- 2026-05-04：开始执行 Phase A。先扩展 `tests/test_scheduler_worker_runner_integration.py`，确认 `dispatch_claimed_task()` 尚不接受 `lifecycle_config`。
- 2026-05-04：完成 Phase A。`dispatch_claimed_task()` 保持旧调用兼容；当传入 `lifecycle_config`、`cancel_event` 或 `stderr_log_path` 时改用 `run_worker_lifecycle()`，并在 `WorkerDispatchResult` 暴露 `stderr_log_path`、`timed_out`、`cancelled` 和 `killed`。
- 2026-05-04：Phase A 完整验证通过：`tests.test_scheduler_worker_runner_integration tests.test_worker_lifecycle tests.test_worker_runner` 15 tests passed，`unittest discover` 67 tests passed，`compileall` passed，`git diff --check` 仅有 Windows CRLF conversion warnings。

## Blockers（阻塞）

- 暂无。`plan_worker_lifecycle_controls.md` 已完成到 Phase F。
