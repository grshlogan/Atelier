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

- `run_worker_process()` 当前使用 `subprocess.run()`，适合最小 stub runner，并保留为兼容入口。
- `run_worker_lifecycle()` 当前使用 `subprocess.Popen()`，支持增量 stdout、startup/heartbeat timeout、最小 cancel control、terminate/kill escalation 和 stderr log path。
- Worker protocol 已定义 `heartbeat`、timeout、cancel 和 stderr 的长期规则。
- Scheduler/runner 接线计划已建立 stub dispatch 闭环，但 dispatch 仍未切换到 lifecycle runner。
- 当前 stderr 可作为字符串返回，也可写入调用方传入的 log path。
- 当前 stdin control channel 只覆盖 `cancel`，尚未覆盖 pause 或更复杂的 adapter 级取消。

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

- 已完成。

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

- 已完成。

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

- 已完成。

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

- 已完成。

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

- 已完成。

### Phase F：protocol error 生命周期收束

目标：

- lifecycle runner 遇到 malformed stdout 或事件顺序错误时，立即终止 worker，并保留 stderr / returncode / stderr log。

完成信号：

- protocol-violating stub worker 输出坏 JSON Lines 后不会继续占用进程。
- `WorkerProcessProtocolError` 保留 stderr 和非零 returncode。
- 调用方传入 `stderr_log_path` 时，protocol error 路径也会写入 stderr 文件。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_worker_lifecycle
```

状态：

- 已完成。

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
- 2026-05-04：开始执行 Phase A。决策：先定义 lifecycle runner 的配置、结果对象和兼容现有 `run_worker_process()` 行为的入口；本阶段不实现增量 stdout、timeout、cancel、kill escalation 或 stderr 文件落盘。
- 2026-05-04：完成 Phase A。先写 `tests/test_worker_lifecycle.py` 并确认缺少 `WorkerLifecycleConfig` 导致红灯；随后新增 `WorkerLifecycleConfig`、`WorkerLifecycleResult` 和 `run_worker_lifecycle()`，当前 lifecycle 入口复用最小 subprocess runner 并返回 lifecycle facts。增量 stdout、heartbeat timeout、cancel、terminate/kill escalation 和 stderr 文件落盘留给后续 Phase。
- 2026-05-04：开始执行 Phase B。决策：先覆盖 silent worker 超时路径；timeout 必须返回结构化 `FailedEvent(error_code="TIMEOUT")`，而不是把空 stdout 当普通 protocol error 抛给上层。
- 2026-05-04：完成 Phase B。`run_worker_lifecycle()` 改为 `Popen` 驱动，增量读取 stdout JSON Lines；startup/heartbeat deadline 超时时会 terminate，必要时 kill，并返回 `FailedEvent(error_code="TIMEOUT", recoverable=True)`。补充 heartbeat 保活测试，确认正常 heartbeat 不会被误判为 timeout。
- 2026-05-04：开始执行 Phase C。决策：最小 cancel 控制通道先使用调用方传入的 `threading.Event`；runner 观察到 cancel request 后向 worker stdin 写入 `{"type":"cancel"}`，并用 `cancel_grace_seconds` 控制升级终止。
- 2026-05-04：完成 Phase C。cancel-aware stub worker 会收到 stdin cancel 并上报 `FailedEvent(error_code="CANCELLED")`；忽略 cancel 的 worker 会在 `cancel_grace_seconds` 后被 terminate，必要时 kill，并返回结构化 `CANCELLED` 失败事件。
- 2026-05-04：开始执行 Phase D。决策：先支持调用方显式传入 stderr log path；runner 保留 stderr 字符串以兼容现有结果，同时把相同内容写入 managed log 文件。
- 2026-05-04：完成 Phase D。`run_worker_lifecycle(stderr_log_path=...)` 会创建父目录并写入 stderr 日志；测试确认 stdout JSON Lines 仍决定主事件事实源。
- 2026-05-04：完成 Phase E。`WORKER_PROTOCOL.md`、`APP_CODE_MAP.md`、`RECENT_CHANGES.md` 和主计划已对齐当前 lifecycle runner 能力与未实现边界。
- 2026-05-04：完整验证通过：`tests.test_worker_lifecycle tests.test_worker_runner` 9 tests passed，`unittest discover` 65 tests passed，`compileall` passed，`git diff --check` 仅有 Windows CRLF conversion warnings。
- 2026-05-04：开始执行 Phase F。决策：protocol error 仍作为异常向上暴露，但生命周期 runner 必须先终止 offending worker，并把 stderr 写入调用方指定 log path。
- 2026-05-04：完成 Phase F。malformed stdout 或事件顺序错误会触发 `WorkerProcessProtocolError`，runner 会先 terminate/kill worker、保留 stderr/returncode，并在传入 `stderr_log_path` 时写入 stderr log。
- 2026-05-04：Phase F 完整验证通过：`tests.test_worker_lifecycle tests.test_worker_runner` 10 tests passed，`unittest discover` 66 tests passed，`compileall` passed，`git diff --check` 仅有 Windows CRLF conversion warnings。

## Blockers（阻塞）

- 暂无。`plan_scheduler_worker_runner_integration.md` 已完成。
