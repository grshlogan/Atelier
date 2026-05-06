# GUI Minimal Run Workflow Entry 计划

> 执行顺序：第 13 个后续计划。建议在 `plan_minimal_backend_workflow_runner.md` 收口并提交后执行。

## Objective

让 Atelier 从“后端 runner 可被测试调用”推进到“GUI 可以提交最小 workflow run 意图”的阶段，同时保持 GUI 职责清晰：

```text
GUI run intent
  -> App service boundary
  -> persisted WorkflowGraph / ExecutionPlan
  -> Scheduler claim
  -> RuntimeManager binding
  -> backend workflow runner
  -> SQLite events / artifacts / failure facts
  -> read-only WorkbenchSnapshot refresh
```

本计划的目标不是做完整工作流编辑器，也不是把 GUI 变成执行器；目标是建立最小可验证入口，让后续用户操作可以进入已经存在的后端 runner 链路。

## Scope

- 新增 GUI run entry 的应用层边界，使 GUI 不直接调用 adapter、FFmpeg 或 worker 命令构建逻辑。
- 首版只支持运行已经持久化的 plan，或由 app service 构造的受控 demo workflow intent。
- GUI 可触发 run intent，但不得在 button callback 中直接执行重任务或阻塞 Qt main event loop。
- 运行完成或失败后，GUI 仍通过 `read_workbench_snapshot()` 读取状态。
- Queue panel 应展示 final output paths 和 failure code/message，使 runner 结果对用户可见。
- 首版只做本地单进程/测试友好的最小链路；生产级后台任务、 durable queue、取消、重试和 recovery action execution 留给后续计划。

暂不实现：

- 完整 Workflow Canvas 编辑器。
- 用户文件选择、输出命名模板和批量导出 UI。
- 真实 FFmpeg smoke UI 流程。
- 后台 worker pool、多任务并发、durable run queue。
- GUI 中的 retry/cancel/recover 动作执行。
- ASR / OCR / Translate / subtitle mux/burn / enhance adapters。

## Current Facts

- 当前已有 `atelier/gui/main_window.py`，可构建只读 PySide6 `MainWindow`、dock workspace 和 runtime setup panel。
- 当前已有 `atelier/gui/workspace.py`，Queue panel 可渲染 task id、node type、status、resource device、event count 和 artifact paths。
- 当前已有 `atelier/gui/state_reader.py`，`WorkbenchSnapshot` 可读取 `final_output_paths`、`failure_error_code` 和 `failure_message`。
- 当前已有 `atelier/scheduler/workflow_runner.py`，`run_sequential_workflow()` 可顺序推进 fake `media.audio_extract -> output.export` 后端 workflow。
- 当前已有 `RuntimeManager.from_store()`，可从 managed runtime manifests 构造 runtime resolution 边界。
- 当前已有 `open_app_database(paths)`、`create_runtime_store(paths)` 和 `create_runtime_setup_service(paths)` app-level factories。
- 当前 GUI launch path 只读：`build_launch_context()` 打开 SQLite、读取 snapshot、创建 runtime setup service，然后构建 `MainWindow`。
- 当前验证基线是 `.venv/Scripts/python -m unittest discover -s tests`，最近结果为 121 tests passed。

## Constraints

- GUI button handler 不得构造最终 FFmpeg 命令，也不得直接调用 adapter。
- GUI 不得绕过 Scheduler 分配资源。
- GUI 不得绕过 RuntimeManager 解析 runtime/tool/model 路径。
- GUI 不得在 Qt main event loop 中同步执行长任务。
- 首版如果需要执行 runner，应通过 app service 或后台执行边界接入；测试可以用同步 fake path，但 GUI 代码必须保留可异步化边界。
- App service 可以 orchestrate，但不应把 workflow graph、scheduler、runtime、worker 和 storage 全部塞进 `MainWindow`。
- User-facing UI text 后续需要接入 I18n；首版若继续沿用现有 placeholder 文案，应记录为待办，不扩大本计划范围。

## Execution Plan

### Phase A: Run intent app service

目标：
- 新增应用层 `WorkflowRunAppService` 或等价边界，用于接收 `plan_id` 和运行上下文，并调用后端 runner。

完成信号：
- GUI 以外的测试可通过 app service 运行一个已持久化的 fake `media.audio_extract -> output.export` plan。
- app service 通过 `SimpleScheduler`、`RuntimeManager.from_store()` 和 `run_sequential_workflow()` 接线。
- app service 返回结构化 result，不直接暴露 worker stdout。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_gui_workflow_run_entry
```

状态：

- 已完成首版最小切片。

### Phase B: Queue panel result visibility

目标：
- 让现有 Queue panel 展示 final output paths 和 failure facts。

完成信号：
- final output artifact 在 Queue panel 中可见。
- failed task 显示 `failure_error_code` 和 `failure_message`。
- 仍通过 `WorkbenchSnapshot` 读取，不从 GUI 查询其他事实源。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_gui_smoke
```

状态：

- 已完成首版最小切片。

### Phase C: Minimal GUI run control boundary

目标：
- 在 GUI 中加入最小 run intent 控制，但保持执行边界可测试、可异步化。

完成信号：
- `MainWindow` 可接收 run service protocol / callback。
- 控件触发的是 app service intent，不直接调用 `dispatch_claimed_task()`、adapter 或 FFmpeg。
- 首版测试验证控件存在、可触发 fake service，并刷新 snapshot 或记录可刷新状态。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_gui_workflow_run_entry tests.test_gui_smoke
```

状态：

- 未开始。

### Phase D: Non-blocking execution boundary

目标：
- 为真实 GUI 执行建立不会阻塞 Qt main event loop 的边界。

完成信号：
- 设计并实现最小后台运行包装，例如 worker thread / queued callback / service protocol fake。
- 测试证明 GUI 层不直接同步调用重 runner。
- 失败结果仍落 SQLite，GUI 通过 snapshot 刷新读取。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_gui_workflow_run_entry
```

状态：

- 未开始。

### Phase E: 文档对齐

目标：
- 更新 `APP_CODE_MAP.md`、`RECENT_CHANGES.md`、主计划和相关 GUI/workflow 边界文档。

完成信号：
- code map 记录 app service、GUI run entry、测试和边界。
- recent changes 记录实现范围和未实现范围。
- main plan child plan / progress 对齐。

验证：

```powershell
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

状态：

- 未开始。

## Child Plans

- 后续可拆 `plan_gui_workflow_file_picker_and_output_intent.md`，用于真实文件选择和输出目录 intent。
- 后续可拆 `plan_gui_run_background_executor.md`，用于更完整的 Qt-safe background execution。
- 后续可拆 `plan_gui_recovery_actions.md`，用于 retry / use partial artifacts / inspect failure 动作。

## Verification

计划验证命令：

```powershell
.venv/Scripts/python -m unittest tests.test_gui_workflow_run_entry
.venv/Scripts/python -m unittest tests.test_gui_smoke
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

当前验证事实：

- `.venv\Scripts\python -m unittest tests.test_gui_workflow_run_entry`：1 test passed。
- `.venv\Scripts\python -m unittest tests.test_gui_workflow_run_entry tests.test_minimal_backend_workflow_runner tests.test_gui_state_reader`：6 tests passed。
- `.venv\Scripts\python -m unittest tests.test_gui_smoke`：4 tests passed。
- `.venv\Scripts\python -m unittest tests.test_gui_workflow_run_entry tests.test_gui_smoke tests.test_minimal_backend_workflow_runner tests.test_gui_state_reader`：10 tests passed。
- `.venv\Scripts\python -m unittest discover -s tests`：121 tests passed。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed。

## Progress / Decisions

- 2026-05-06：创建本计划。决策：下一阶段先建立 GUI run intent 到 app service 的最小边界，不把 runner、Scheduler、RuntimeManager 或 adapter 逻辑塞进 `MainWindow`。
- 2026-05-06：完成 Phase A 首版最小切片。新增 `WorkflowRunAppService`，可从 GUI-facing app service 边界接收 persisted `plan_id`，通过 `RuntimeStore -> RuntimeManager.from_store()`、`SimpleScheduler` 和 `run_sequential_workflow()` 跑通 fake `media.audio_extract -> output.export`；尚未做 GUI 控件、后台执行或 Queue panel 展示扩展。
- 2026-05-06：完成 Phase B 首版最小切片。Queue panel 继续只读 `WorkbenchSnapshot`，现在会展示 `final_output_paths` 和 `failure_error_code` / `failure_message`；尚未做 GUI run 控件或后台执行边界。

## Blockers

- 暂无。
