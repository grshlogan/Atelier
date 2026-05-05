# Initial Actionable GUI Runtime Setup 计划

> 执行顺序：第 8 个后续计划。建议在 `plan_runtime_management_foundation.md` 完成后执行，让当前只读 PySide6 工作台具备最小可操作 runtime setup 能力。

## Objective（目标）

把当前只读 GUI 推进到“初始可操作”的状态：用户能看到 runtime / model 健康状态，并能通过受控入口登记本地工具路径、触发轻量 health check。

目标链路：

```text
RuntimeSetupSnapshot
  -> Runtime Setup dock / page
  -> choose local executable or model directory
  -> Runtime registration service
  -> RuntimeHealthChecker
  -> refreshed GUI state
```

## Scope（范围）

- 新增 Runtime Setup UI surface，复用现有 `MainWindow` / workspace / state reader 边界。
- 显示 runtime components、model assets、status、issues、repair hints。
- 支持最小 action：
  - register local `ffprobe` / `ffmpeg` executable。
  - register local Worker Python executable for development profile。
  - register local demo model directory。
  - run health check / refresh。
- 所有 action 进入 app service / RuntimeManager 边界，不在 widget callback 中直接拼 command。
- 更新 GUI tests、APP_CODE_MAP 和 RECENT_CHANGES。

暂不实现：

- 运行真实 workflow。
- 在 GUI 中启动 Scheduler / Worker。
- 下载 runtime 或模型。
- 插件安装 UI。
- 完整 Settings 系统。
- 复杂主题、图标管理或视觉 polish。

## Current Facts（当前事实）

- `atelier/gui/main_window.py` 已有只读工作台壳和 dockable panels。
- `atelier/gui/state_reader.py` 已能读取 SQLite queue snapshot。
- `atelier/runtime/` 已有最小 store / manager / health checker、registration service 和 `RuntimeSetupSnapshot`。
- `atelier/app/runtime_setup.py` 已提供 `RuntimeSetupAppService`，作为 GUI action 到 runtime registration / snapshot refresh 的 app-level 边界。
- `docs/Atelier_Main_UI_Spec.md` 将 Settings / Queue / Projects / Presets 等视为可独立页面，右侧/底部 panels 可嵌入或浮动。
- GUI 不得阻塞 Qt main event loop，不得直接运行重型任务。

## Constraints（约束）

- Runtime Setup action 只能登记 manifest 或执行轻量 health check。
- GUI 不直接运行 FFmpeg、模型、外部工具、Scheduler 或 Worker。
- 用户选择路径必须进入 Runtime registration service 校验。
- UI strings 后续应进入 I18N；本计划可保持最小英文/中文混合开发文本，但不得扩大硬编码范围。
- 本计划不追求完整视觉实现，只要初始可操作。

## Execution Plan（执行计划）

### Phase A：Runtime setup view model

目标：

- 新增 GUI 可消费的 runtime setup view model。

完成信号：

- view model 能表达 components、models、status、issues、actions enabled state。
- 无 PySide6 环境下也可测试 view model。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_gui_runtime_setup_state
```

状态：

- 已完成。

### Phase B：Runtime Setup dock / page

目标：

- 在当前 MainWindow 中加入 Runtime Setup 入口或 dock。

完成信号：

- offscreen Qt smoke test 可构造窗口并找到 Runtime Setup surface。
- surface 可显示 snapshot。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_gui_smoke tests.test_gui_runtime_setup
```

状态：

- 已完成。

### Phase C：受控 registration actions

目标：

- 把选择本地 executable/model path 的 action 接到 app service。

完成信号：

- widget callback 不拼 command。
- action 调用 service 后刷新 snapshot。
- 缺失路径或非法路径显示可诊断错误。

验证：

```powershell
.venv/Scripts/python -m unittest tests.test_gui_runtime_setup
```

状态：

- 已完成。

### Phase D：文档状态对齐

目标：

- 更新 GUI 和 runtime 接手文档。

完成信号：

- `APP_CODE_MAP.md`、`Atelier_Main_UI_Spec.md`、`RECENT_CHANGES.md` 和主计划更新。

验证：

```powershell
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

状态：

- 已完成。

## Child Plans（子计划）

- [plan_minimal_adapter_probe_workflow.md](./plan_minimal_adapter_probe_workflow.md)：Runtime setup 可用后，接入最简 adapter / metadata probe workflow。

## Verification（验证）

计划验证命令：

```powershell
.venv/Scripts/python -m unittest tests.test_gui_runtime_setup_state tests.test_gui_runtime_setup
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

最近验证事实：

- `.venv/Scripts/python -m unittest discover -s tests`：87 tests passed。
- `.venv/Scripts/python -m compileall -q atelier tests`：passed。
- `Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'`：no matches。
- `git diff --check`：passed，仅有 Windows CRLF conversion warnings。

## Progress / Decisions（进展 / 决策）

- 2026-05-05：创建本计划。决策：GUI 先做 runtime setup 的轻量操作面，不启动 Scheduler / Worker，也不运行真实外部工具。
- 2026-05-05：完成 Phase A。新增 `atelier/gui/runtime_setup_state.py`，把 `RuntimeSetupSnapshot` 转为 PySide-independent view state，覆盖 summary、components、models、status、detail lines 和 action enabled state。
- 2026-05-05：完成 Phase B。新增 `atelier/gui/runtime_setup_panel.py`，`MainWindow` 现在包含 `Runtime Setup` dock；开发启动入口会读取 runtime manifests 并显示 runtime setup snapshot。
- 2026-05-05：完成 Phase C。新增 `atelier/app/runtime_setup.py` 和 `create_runtime_setup_service(paths)`，Runtime Setup panel 的 register / refresh action 只调用 app service；非法路径显示为诊断错误。
- 2026-05-05：完成 Phase D。`APP_CODE_MAP.md`、`Atelier_Main_UI_Spec.md`、`RECENT_CHANGES.md` 和主计划已对齐；最终验证见本计划 Verification / 最近变更记录。

## Blockers（阻塞）

- 暂无。
