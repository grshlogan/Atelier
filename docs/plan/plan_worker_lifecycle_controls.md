# Worker Lifecycle Controls 计划

> 执行顺序：第 2 个后续计划。建议在 `plan_scheduler_worker_runner_integration.md` 完成后执行，因为 timeout、cancel、kill escalation 和 stderr 文件落盘需要依托可运行的 dispatch 闭环验证。

## Objective（目标）

把当前最小 runner 从“一次性 subprocess.run 边界”推进到可控的 worker lifecycle runner：能观察启动、处理 timeout、取消任务、终止/强杀进程，并把 stderr 作为可追踪日志落盘。

目标链路：

```text
WorkerProcessSpec
  -> lifecycle runner starts process
  -> reads stdout JSON Lines incrementally
  -> captures stderr to log file
  -> timeout / cancel / terminate / kill
  -> terminal WorkerEvent or structured failure event
```

## Scope（范围）

- 将 runner 能力扩展为可控制生命周期的边界。
- 支持 startup timeout 和 heartbeat/event timeout。
- 支持 cancel request 的最小控制通道。
- 支持 terminate -> kill escalation。
- 支持 stderr 写入 managed log path，并在结果中返回 log path。
- 使用 stub worker 测试 long-running、silent、cancel-aware 和 stuck worker。
- 更新 `WORKER_PROTOCOL.md`、`APP_CODE_MAP.md`、`RECENT_CHANGES.md` 和主计划。

暂不实现：

- GUI 取消按钮。
- 真实 FFmpeg/model adapter 的取消逻辑。
- OS job object / process tree 完整治理。
- 跨平台高级 signal 策略。
- retry/recovery action 执行。
- log viewer UI。

## Current Facts（当前事实）

- `run_worker_process()` 当前使用 `subprocess.run()`，适合最小 stub runner，但不能做增量 stdout、timeout 或 cancel。
- Worker protocol 已定义 `heartbeat`、timeout、cancel 和 stderr 的长期规则。
- Scheduler/runner 接线计划会先建立 stub dispatch 闭环。
- 当前 stderr 只作为字符串返回，没有落盘。
- 当前没有 stdin control channel。

## Constraints（约束）

- GUI 不参与本计划。
- 本计划仍只使用 stub worker，不接真实 adapters。
- Worker stdout 仍必须是 JSON Lines，主状态不能从 stderr 推断。
- cancel/timeout 结果必须转成结构化失败事件或明确 dispatch result，不能只靠异常。
- stderr 日志不得包含 secrets；后续接 SecurityManager redaction 前，测试数据必须保持无敏感内容。
- 不能把 retry/recovery orchestration 混入 lifecycle runner。

## Execution Plan（执行计划）

### Phase A：Lifecycle runner 接口

目标：

- 定义可控制生命周期的 runner spec/result，不破坏现有最小 runner 调用方。

完成信号：

- 有 `WorkerLifecycleConfig` 或等价配置，包含 startup timeout、heartbeat timeout、terminate grace。
- result 能表达 events、stderr log path、returncode、timed_out、cancelled、killed 等事实。
- 当前 `run_worker_process()` 可保留为简单入口或转接到新 runner。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_worker_lifecycle
```

状态：

- 待执行。

### Phase B：stdout 增量读取与 heartbeat timeout

目标：

- runner 能增量读取 stdout JSON Lines，并在长时间无事件时判定 timeout。

完成信号：

- 正常 heartbeat/progress 可保持进程存活。
- silent worker 超过 timeout 后被终止。
- timeout 会产生结构化失败事实，建议 error_code 使用 `TIMEOUT`。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_worker_lifecycle
```

状态：

- 待执行。

### Phase C：Cancel 与 terminate/kill escalation

目标：

- 支持最小 cancel 控制通道和强制终止升级路径。

完成信号：

- cancel-aware stub worker 收到 cancel 后发出 `FailedEvent(error_code="CANCELLED")` 并退出。
- stuck worker 不退出时，runner 先 terminate，再 kill。
- result 清晰记录 cancelled/killed/returncode。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_worker_lifecycle
```

状态：

- 待执行。

### Phase D：stderr 文件落盘

目标：

- stderr 进入 managed log 文件，为 Queue Monitor 和失败恢复面板提供可追踪日志来源。

完成信号：

- stderr 被写入调用方指定 log path 或 task log dir。
- result 返回 stderr log path。
- 测试确认 stderr 内容存在，stdout 仍只通过 JSON Lines 决定主状态。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_worker_lifecycle
```

状态：

- 待执行。

### Phase E：文档状态对齐

目标：

- 更新协议和接手文档，明确当前 lifecycle runner 能力和仍未实现的真实 adapter/GUI/恢复动作。

完成信号：

- `WORKER_PROTOCOL.md`、`APP_CODE_MAP.md`、`RECENT_CHANGES.md`、主计划更新。

验证：

```powershell
git diff --check
```

状态：

- 待执行。

## Child Plans（子计划）

- 暂无。

真实 FFmpeg/ffprobe adapter、ArtifactFinalizer 或 GUI cancellation 进入实现前，应再拆独立计划。

## Verification（验证）

计划验证命令：

```powershell
.venv/Scripts/python -m unittest tests.test_worker_lifecycle
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

## Progress / Decisions（进展 / 决策）

- 2026-05-04：创建本计划。决策：在 Scheduler runner integration 之后处理 worker lifecycle controls，避免在尚未接线前过早堆复杂进程控制。

## Blockers（阻塞）

- 等待 `plan_scheduler_worker_runner_integration.md` 完成后执行。
