# Worker Protocol 与 Runner 骨架计划

> 执行顺序：在 `resource_locks + failure recovery` 和只读 PySide6 工作台壳完成后推进。目标是先把 Worker 事件边界稳定下来，再进入更完整的 worker lifecycle runner。

## Objective（目标）

建立 Atelier 的首版 Worker JSON Lines 协议代码边界，让未来真实 Worker 进程可以通过结构化事件向 Scheduler 汇报状态，同时保持 GUI、Scheduler、RuntimeManager、Worker 和 SQLite 的职责分离。

首版目标：

```text
WorkerEvent models
  -> JSON Lines encode/decode
  -> validated event stream
  -> future subprocess runner boundary
```

本计划不接入真实 FFmpeg、ASR、LLM、CUDA、模型推理或外部工具。

## Scope（范围）

- 实现 WorkerEvent JSON Lines 序列化与解析。
- 补齐当前协议文档中已经定义、但代码尚未建模的轻量事件类型，例如 `log` 和 `heartbeat`。
- 为 Scheduler 未来读取 Worker stdout 预留 event stream validation 边界。
- 保持 Worker 不直接写 SQLite；持久化仍由 storage/repository 层根据事件完成。
- 更新 `WORKER_PROTOCOL.md` 的实现状态、`APP_CODE_MAP.md`、`RECENT_CHANGES.md` 和主计划进展。

暂不实现：

- 生产级 worker lifecycle runner。
- stdin cancel/pause 控制通道。
- heartbeat timeout kill 逻辑。
- stderr log 文件落盘。
- typed FFmpeg/ffprobe/model adapters。
- ArtifactFinalizer 或用户导出路径落盘。

## Current Facts（当前事实）

- `docs/WORKER_PROTOCOL.md` 已定义 JSON Lines worker 协议，当前状态已更新为部分实现。
- 当前已有 `atelier/domain/worker_event.py`，包含 `StartedEvent`、`ProgressEvent`、`LogEvent`、`HeartbeatEvent`、`ArtifactEvent`、`CompletedEvent`、`FailedEvent` 和 `ArtifactRef`。
- 当前已有 `atelier/workers/protocol.py`，可对单个 WorkerEvent 做 JSON Lines 编解码，并可验证最小 stdout event stream lifecycle。
- 当前已有 `atelier/workers/runner.py`，可启动可控 subprocess 命令并捕获 stdout/stderr/return code。
- 当前已有 `atelier/workers/task_file.py`，可把 `ExecutionTask` 写成 `task.json` 并生成 `WorkerProcessSpec`。
- 当前已有 `atelier/workers/simulated.py`，可产生 deterministic simulated worker events。
- 当前已有 `record_worker_events()`，会根据结构化事件写入 SQLite，并在 terminal events 后释放 active resource locks。
- 当前测试基线是 stdlib `unittest`，最近完整验证为 55 tests passed。

## Constraints（约束）

- 生产代码变更必须先写测试并确认失败，再实现。
- Worker protocol 代码不得启动 worker 进程，不得调用外部工具，不得读写 SQLite。
- `WorkerEvent` 序列化必须保留协议字段，不从 stderr 或自由文本中推断主状态。
- Unknown event type、malformed JSON 和非对象 JSON 必须显式失败，不能静默吞掉。
- 事件模型必须继续兼容现有 storage 和 simulated worker 测试。
- 不能把 Scheduler claim、RuntimeManager path resolution 或 GUI 逻辑混进 protocol parser。

## Execution Plan（执行计划）

### Phase A：WorkerEvent JSON Lines 编解码

目标：

- 建立 `WorkerEvent` 到单行 JSON，以及单行 JSON 到具体事件模型的双向转换。

完成信号：

- 新增 protocol helper，能序列化已有事件模型为以换行结尾的 JSON Lines。
- 能根据 `type` 字段解析为 `StartedEvent`、`ProgressEvent`、`ArtifactEvent`、`CompletedEvent`、`FailedEvent`、`LogEvent` 或 `HeartbeatEvent`。
- malformed JSON、unknown event type、非对象 JSON 会抛出清晰协议错误。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_worker_protocol
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

状态：

- 已完成。新增 `atelier/workers/protocol.py` 和 `tests/test_worker_protocol.py`；先确认测试因缺少 `HeartbeatEvent` / `LogEvent` 失败，再补齐事件模型和 JSON Lines 编解码 helper。

### Phase B：Worker stdout event stream validation

目标：

- 在不启动 subprocess 的前提下，验证事件流顺序和最小生命周期约束。

完成信号：

- `started` 必须是首个事件。
- `seq` 必须从 0 开始且连续递增。
- `completed` / `failed` 必须作为 terminal event 结束流。
- terminal event 之后再出现事件应被标记为协议错误。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_worker_protocol
```

状态：

- 已完成。新增 `parse_worker_event_stream()`，验证 `started` 必须是首个事件、`seq` 必须从 0 连续递增、`completed` / `failed` 必须结束事件流，且 terminal event 后不得再出现事件。

### Phase C：Subprocess runner 边界骨架

目标：

- 定义未来 Scheduler 启动 Worker subprocess 的窄接口，但仍不接真实 adapter。

完成信号：

- runner 接收 typed command args、task file path、work dir 和环境映射。
- runner 只负责进程边界、stdout JSON Lines 读取和 stderr 捕获，不负责 Scheduler resource binding 或 RuntimeManager path resolution。
- 测试使用可控 Python stub worker，不调用真实 FFmpeg/model。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_worker_runner
```

状态：

- 已完成。新增 `atelier/workers/runner.py` 和 `tests/test_worker_runner.py`；runner 接收 `WorkerProcessSpec`，追加 `--task-file`，使用 `work_dir` 作为 cwd，合并 env，捕获 stdout/stderr/return code，并用 `parse_worker_event_stream()` 验证 stdout。

### Phase D：协议文档状态对齐

目标：

- 把 `WORKER_PROTOCOL.md` 从纯规划状态更新为“部分实现”，明确已实现与未实现部分。

完成信号：

- 文档准确说明 JSON Lines encode/decode 已实现。
- 文档准确说明 subprocess runner、cancel、heartbeat timeout、stderr 落盘、真实 adapters 尚未实现。

验证：

```powershell
git diff --check
```

状态：

- 已完成状态对齐。`docs/WORKER_PROTOCOL.md` 已标记为“部分实现”，并明确最小 runner 已实现，stdin control、heartbeat timeout、stderr 落盘、生产级 lifecycle 和真实 adapters 尚未实现。

### Phase E：ExecutionTask task.json 与 Launch Spec

目标：

- 在 Scheduler 正式接 runner 前，先建立 `ExecutionTask -> task.json -> WorkerProcessSpec` 的窄边界。

完成信号：

- 能把一个 `ExecutionTask` 完整序列化到 task 工作目录下的 `task.json`。
- task 工作目录使用 `{work_root}/{task_id}`，由 helper 创建。
- 能根据 `ExecutionTask`、typed command args、work root 和可选 env 生成 `WorkerProcessSpec`。
- 如果 `ExecutionTask.runtime_binding.env` 存在，launch spec 会携带这些 env；调用方显式传入的 env 可以覆盖同名值。
- 不启动 subprocess，不 claim Scheduler，不写 SQLite，不解析 runtime/model path。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_worker_task_file
```

状态：

- 已完成。新增 `atelier/workers/task_file.py` 和 `tests/test_worker_task_file.py`；可写入完整 `ExecutionTask` JSON，并基于 task work dir、command args、runtime env 和 caller env 生成 `WorkerProcessSpec`。

## Child Plans（子计划）

- 暂无。

如果 subprocess runner 进入真实 worker lifecycle、timeout、cancel 或 adapter registry，需要拆出独立子计划。

## Verification（验证）

当前计划验证命令：

```powershell
.venv/Scripts/python -m unittest tests.test_worker_protocol
.venv/Scripts/python -m unittest tests.test_worker_runner
.venv/Scripts/python -m unittest tests.test_worker_task_file
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

当前最近验证事实：

- `.venv/Scripts/python -m unittest tests.test_worker_protocol`：9 tests passed。
- `.venv/Scripts/python -m unittest tests.test_worker_runner`：3 tests passed。
- `.venv/Scripts/python -m unittest tests.test_worker_task_file`：2 tests passed。
- `.venv/Scripts/python -m unittest discover -s tests`：55 tests passed。
- `.venv/Scripts/python -m compileall -q atelier tests`：passed。
- `git diff --check`：passed，仅有 Windows CRLF conversion warnings。

## Progress / Decisions（进展 / 决策）

- 2026-05-03：创建本计划。决策：先实现 Worker JSON Lines 事件协议边界，暂不启动真实 subprocess，不接外部工具。
- 2026-05-03：完成 Phase A。新增 WorkerEvent JSON Lines 编解码，补齐 `LogEvent` / `HeartbeatEvent` 事件模型；协议 helper 只处理单个事件，不启动 subprocess、不读写 SQLite。
- 2026-05-03：完成 Phase D 首轮状态对齐。`WORKER_PROTOCOL.md` 已标记为部分实现，并列出 runner/control/timeout/stderr/adapters 未实现。
- 2026-05-04：开始执行 Phase B。范围限定为 stdout JSON Lines event stream validation，不启动 subprocess、不读取 stderr、不写 SQLite。
- 2026-05-04：完成 Phase B。新增 `parse_worker_event_stream()` 和对应测试，事件流验证只处理已读取的 stdout JSON Lines，不负责 worker process lifecycle。
- 2026-05-04：完成 Phase C。新增最小 subprocess runner 边界；runner 不选择 runtime/model/hardware，不接 Scheduler，不实现 cancel/timeout/kill escalation。
- 2026-05-04：更新 Phase D 状态对齐。`WORKER_PROTOCOL.md` 当前明确最小 runner 已实现，但生产级 lifecycle、stdin control、heartbeat timeout、stderr 落盘和真实 adapters 仍未实现。
- 2026-05-04：开始执行 Phase E。范围限定为 `ExecutionTask` task file 写入和 `WorkerProcessSpec` 生成，不启动 runner、不接 Scheduler、不写 SQLite。
- 2026-05-04：完成 Phase E。新增 task file 写入与 launch spec 生成边界；显式 caller env 可覆盖 `runtime_binding.env` 中的同名 key。

## Blockers（阻塞）

- 暂无。
