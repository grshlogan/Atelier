# Resource Locks 与 Failure Recovery 子计划

> 执行顺序：第 1 个子计划。先补执行可靠性，再让 UI 读取更可信的状态。

## Objective（目标）

在现有 Phase 7 `SimpleScheduler` 的基础上，补齐首版 resource lock 与 failure recovery 最小链路，让任务 claim、运行、失败、恢复不只是状态字段，而是可以被 SQLite 记录、查询和测试的执行事实。

目标不是一次做完整生产调度器，而是建立可靠性骨架：

```text
runnable task
  -> acquire resource lock
  -> mark running
  -> record worker events
  -> release lock on terminal event
  -> classify failure
  -> expose recovery options
```

## Scope（范围）

- 为 `resource_locks` 表接入最小读写路径。
- 让 Scheduler claim task 时同步创建 resource lock。
- 在 completed / failed / cancelled terminal event 后释放或标记 resource lock。
- 为 failed task 记录最小 failure facts：`error_code`、`error_message`、recoverable、partial artifacts。
- 提供最小 recovery action 计算：retry、skip、resume/use partial artifacts、cancel/no action。
- 增加测试覆盖成功释放、失败保留诊断、stale lock 检测和可恢复动作。
- 更新 `APP_CODE_MAP.md`、`RECENT_CHANGES.md` 和主计划进度。

暂不实现：

- 多进程安全的生产级锁竞争。
- 真正 worker subprocess 管理。
- GPU 显存精确锁。
- 复杂 retry backoff。
- GUI failure recovery 面板。
- 跨启动崩溃恢复扫描的完整流程。

## Current Facts（当前事实）

- `resource_locks` 表已存在于 `atelier/storage/schema.sql`。
- `SimpleScheduler` 当前能 claim dependency-ready pending task，并将 task 标记为 `running`。
- `record_worker_events()` 当前能写入 `task_events`、`artifacts`、`task_artifacts`，并在 terminal event 后更新 task status。
- `FailedEvent` 已有 `error_code`、`message`、`recoverable`、`partial_artifacts` 字段。
- `task_status_from_terminal_event()` 当前把 `CANCELLED` 映射为 `cancelled`，其他 failed terminal event 映射为 `failed`。
- 当前验证基线是 `.venv/Scripts/python -m unittest discover -s tests`，最近记录为 31 tests passed。

## Constraints（约束）

- Scheduler 是唯一能绑定资源的组件；GUI 和 Worker 不得绕过 Scheduler 创建资源绑定。
- Storage 负责持久化 lock / task / event，不负责调度策略。
- `resource_locks` 不能成为装饰字段：claim 时必须有可查询 lock，terminal event 后必须有明确释放或 stale 语义。
- 不引入全局 `cuda:0` 默认策略。
- 不把失败恢复做成只有 modal error dialog 的 UI 行为；它必须先成为持久化状态。
- 不在本阶段引入真实 FFmpeg/model worker。
- 不用 sleep/retry 掩盖 race condition；先用单连接 SQLite 测试确认状态链正确。

## Execution Plan（执行计划）

### Phase A：Resource Lock 持久化骨架

目标：

- 为 `resource_locks` 增加最小 repository helpers。

完成信号：

- claim task 时创建 `resource_locks` row。
- row 包含 `task_id`、`device_id`、`lock_type`、`vram_mb`、`acquired_at`。
- 可查询 task 当前 active lock。

验证：

- 新增测试：`SimpleScheduler.claim_next_task()` 后，task status 是 `running`，且 active lock 存在。

状态：

- 已完成。新增 `tests/test_resource_locks.py`，验证 Scheduler claim 后创建 active `resource_locks` row。

### Phase B：Terminal Event 释放锁

目标：

- worker terminal event 进入 storage 后释放 lock。

完成信号：

- `CompletedEvent` 后 task status 为 `completed`，active lock 不再 active。
- `FailedEvent(error_code="CANCELLED")` 后 task status 为 `cancelled`，active lock 释放。
- 普通 `FailedEvent` 后 task status 为 `failed`，active lock 释放，同时保留 failure facts。

验证：

- 新增测试：completed / cancelled / failed 三类 terminal event 均释放 lock。

状态：

- 已完成。`tests/test_resource_locks.py` 覆盖 completed、cancelled、failed 三类 terminal event 释放 active lock。

### Phase C：Failure Facts 与 Recovery Options

目标：

- 让失败恢复有可查询事实和最小建议动作。

完成信号：

- failed task 可查询 `error_code`、`error_message`、recoverable、partial artifact paths。
- recoverable failed task 返回 retry / resume 或 use partial artifacts 的最小建议。
- non-recoverable failed task 不返回 retry，返回 inspect/export usable artifacts 一类只读建议。

验证：

- 新增测试：recoverable 与 non-recoverable failure 产生不同 recovery options。

状态：

- 已完成。新增 `tests/test_failure_recovery.py`，验证 recoverable failure 会暴露 retry / use partial artifacts 选项，non-recoverable failure 不暴露 retry 且提供 inspect/export partial artifacts 只读选项。

### Phase D：Stale Lock 最小检测

目标：

- 为后续崩溃恢复建立基础。

完成信号：

- 能查询超过 `stale_after` 且未 released 的 lock。
- 能把 stale lock 标记为 released 或 stale-released。
- 不自动重跑任务，只提供明确状态。

验证：

- 新增测试：构造过期 lock，可被检测并释放。

状态：

- 已完成。`tests/test_resource_locks.py` 已覆盖：构造超过 `stale_after` 且未 released 的 lock，能被 `fetch_stale_resource_locks()` 检测，并能通过 `release_stale_resource_lock()` 释放；释放 stale lock 不自动改变 task status；未过期 lock 和已释放 lock 不会被 stale release 路径释放。

## Child Plans（子计划）

- 暂无。

如果后续发现 crash recovery / retry policy 变复杂，再拆 `docs/plan/plan_crash_recovery_retry_policy.md`。

## Verification（验证）

最小验证命令：

```powershell
.venv/Scripts/python -m unittest tests.test_resource_locks
.venv/Scripts/python -m unittest tests.test_failure_recovery
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

如果新增文件名不同，以实际测试文件为准，但必须覆盖：

- claim creates lock
- terminal event releases lock
- failed task records failure facts
- recovery options differ by recoverability
- stale lock detection

## Progress / Decisions（进展 / 决策）

- 2026-05-03：创建本子计划。决策：先补 resource lock / recovery 后端事实，再做只读 PySide6 工作台壳。
- 2026-05-03：完成 Phase A。新增 `ResourceLockRecord`、`fetch_active_resource_lock()`，并让 `mark_task_running()` 在 claim 路径中创建 active resource lock。
- 2026-05-03：Phase A 验证通过：`tests.test_resource_locks` passed，全量 unittest 为 24 tests passed。
- 2026-05-03：完成 Phase B。`record_worker_events()` 在 terminal event 路径更新 task status 后释放 active resource locks，completed / cancelled / failed 均已覆盖。
- 2026-05-03：Phase B 验证通过：`tests.test_resource_locks` 为 4 tests passed，全量 unittest 为 27 tests passed。
- 2026-05-03：完成 Phase C。新增 `FailureFacts`、`RecoveryOption`、`fetch_failure_facts()`、`suggest_recovery_options()`，并把 `FailedEvent.partial_artifacts` 以 `partial` 角色写入 `artifacts` / `task_artifacts`。
- 2026-05-03：Phase C 验证通过：`tests.test_failure_recovery` 为 2 tests passed，全量 unittest 为 29 tests passed。
- 2026-05-03：完成 Phase D。新增 `StaleResourceLockRecord`、`fetch_stale_resource_locks()` 和 `release_stale_resource_lock()`，只处理 stale lock 检测/释放，不自动重跑任务或改变 task status。
- 2026-05-03：Phase D 验证通过：`tests.test_resource_locks` 为 5 tests passed，全量 unittest 为 30 tests passed。
- 2026-05-03：Phase D 收尾补丁：补充 stale release 防护测试，确认未过期 lock 与已释放 lock 会被拒绝释放；`tests.test_resource_locks` 为 6 tests passed，全量 unittest 为 31 tests passed。

## Blockers（阻塞）

- 暂无。
