# 只读 PySide6 工作台壳子计划

> 执行顺序：第 2 个子计划。建议在 `plan_resource_locks_failure_recovery.md` 完成后执行，让 UI 读取更可信的 queue / lock / failure 状态。

## Objective（目标）

建立首版只读 PySide6 工作台壳，让 Atelier 的现有后端状态可以被看见，但不通过 GUI 执行重型任务。

首版 UI 目标：

```text
AppPaths / SQLite
  -> read workflow / plan / task / event / artifact / runtime status
  -> render read-only workstation shell
  -> no heavy work in GUI
```

界面只读，不做真实编辑器，不做 FFmpeg/model 执行，不做插件加载。

## Scope（范围）

- 引入最小 PySide6 app entry，但保持可选依赖边界。
- 建立 `gui/` package 和只读 `MainWindow`。
- 使用 dockable / panel-friendly 布局，为后续 Workflow Canvas、Execution Canvas、Queue Monitor、Hardware/Runtime 面板预留边界。
- 读取 SQLite 中已有 project/job/task/event/artifact 状态，展示只读表格或列表。
- 展示 runtime / data path 基础信息，帮助确认 `.atelier/AtelierData` 路径。
- 添加最小 smoke test，至少验证 GUI 模块可 import、窗口可构造但不启动 event loop。
- 更新 `APP_CODE_MAP.md`、`RECENT_CHANGES.md` 和主计划进度。

暂不实现：

- 真正 Workflow Canvas 绘制和编辑。
- 任务启动按钮。
- FFmpeg/model 执行。
- 完整主题系统。
- 完整 i18n catalog。
- 复杂 dock layout persistence。
- 截图级视觉验收，除非本阶段实际启动 GUI 并具备稳定检查路径。

## Current Facts（当前事实）

- 当前项目已有 `.venv/`，并已通过 `.venv/Scripts/python -m pip install -e ".[gui]"` 安装开发期 GUI extras。
- PySide6 仍然只在 `pyproject.toml` 的 optional dependency group 中，不是 core hard dependency。
- `pyproject.toml` 已有 optional dependency group：`gui = ["PySide6"]`。
- `AppPaths` 已能提供开发期 `.atelier/AtelierData`、database、cache、logs 等路径。
- `open_app_database(paths)` 已能打开并初始化 SQLite。
- 当前已有最小 workflow / planning / scheduler / storage / worker event 状态可供只读展示。
- 当前已有 `atelier/gui/entry.py`、`main_window.py`、`workspace.py` 和 `state_reader.py`。
- `DESIGN.md` 已定义 Atelier 的工作站基调，GUI 应参考该设计事实源，而不是另起 landing page。

## Constraints（约束）

- GUI 不得直接运行 FFmpeg、ASR、LLM、CUDA、model inference 或 worker heavy task。
- GUI 不得阻塞 Qt main event loop。
- GUI 只提交 intent 和渲染 state；本阶段甚至只渲染 state。
- UI 文案后续必须走 i18n；本阶段如临时 hard-code，必须集中并标记为后续替换点。
- 不把四区块写死为不可变布局；首版可以用 `QMainWindow` / `QDockWidget` 思路保留可停靠边界。
- 不把 runtime binaries、model assets 或 `.venv` 放入 GUI package。
- 不把 UI 做成营销 landing page；第一屏就是工作台壳。

## Execution Plan（执行计划）

### Phase A：GUI 依赖与入口边界

目标：

- 让 GUI 依赖保持 optional，并定义开发启动方式。

完成信号：

- 文档说明如何安装 GUI extras，例如 `.venv/Scripts/python -m pip install -e ".[gui]"`。
- 没有把 PySide6 变成 core hard dependency，除非用户明确改变技术策略。

验证：

- 未安装 PySide6 时，非 GUI 测试仍通过。
- 安装 PySide6 后，GUI smoke test 可运行。

状态：

- 已完成。新增 `atelier/gui/entry.py` 与 `tests/test_gui_optional_dependency.py`，确认 GUI 入口可选依赖边界清晰，缺失 PySide6 时会提示 `.venv/Scripts/python -m pip install -e ".[gui]"`。

### Phase B：只读 MainWindow 壳

目标：

- 创建 `atelier/gui/` package 和最小 `MainWindow`。

完成信号：

- `MainWindow` 可接收 app state reader 或 `AppPaths`。
- 窗口包含面向四区块的只读区域：workflow / execution / queue / resources-runtime。
- 不启动 worker，不触发 scheduler claim。

验证：

- smoke test 构造窗口对象，不进入长时间 event loop。

状态：

- 已完成。新增 `atelier/gui/main_window.py`、`atelier/gui/workspace.py` 和 `tests/test_gui_smoke.py`，可在 offscreen `QApplication` 下构造 `MainWindow`，并验证 workflow / execution / queue / resources-runtime 四个只读 dock。

### Phase C：SQLite 只读状态读取

目标：

- 从 SQLite 读取现有 project/job/task/event/artifact 状态。

完成信号：

- 有只读 query helper 或 view model。
- Queue panel 至少能显示 task id、node type、status、resource binding、event count。
- Artifact panel 或 task detail 至少能显示 artifact path。

验证：

- 使用测试数据库构造状态，view model 返回可展示数据。

状态：

- 已完成。新增 `atelier/gui/state_reader.py` 和 `tests/test_gui_state_reader.py`，从 SQLite 读取 task id、node type、status、resource binding、event count 和 artifact path；`MainWindow` Queue panel 可渲染 `WorkbenchSnapshot`。

### Phase D：工作台布局边界

目标：

- 为后续真实工作台铺好布局边界。

完成信号：

- UI 结构区分主窗口、workspace、panels。
- 不把所有东西塞进一个巨大 `main_window.py`。
- 布局代码不混入 storage 写逻辑或 scheduler logic。

验证：

- import / construction tests。
- 如能启动本地 GUI，再做一次手动运行记录。

状态：

- 已完成首版边界。当前 UI 结构已分离为 `main_window.py`、`workspace.py` 和 `state_reader.py`；布局代码不读取/写入 SQLite，窗口类不调用 Scheduler 或 worker。

## Child Plans（子计划）

- 暂无。

如 UI 范围扩大到真实 canvas、主题系统或 i18n catalog，再拆独立子计划。

## Verification（验证）

基础验证：

```powershell
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

GUI extras 验证（执行本计划时再启用）：

```powershell
.venv/Scripts/python -m pip install -e ".[gui]"
.venv/Scripts/python -m unittest tests.test_gui_smoke
```

如果 PySide6 未安装，不得声称 GUI smoke test 已通过。

当前最近验证事实：

- `.venv/Scripts/python -m pip install -e ".[gui]"`：passed，当前开发 `.venv` 已安装 PySide6 6.11.0。
- `.venv/Scripts/python -m unittest tests.test_gui_optional_dependency`：2 tests passed。
- `.venv/Scripts/python -m unittest tests.test_gui_smoke`：2 tests passed。
- `.venv/Scripts/python -m unittest tests.test_gui_state_reader`：1 test passed。
- `.venv/Scripts/python -m unittest discover -s tests`：36 tests passed。
- `.venv/Scripts/python -m compileall -q atelier tests`：passed。
- `git diff --check`：passed，仅有 Windows CRLF conversion warnings。

## Progress / Decisions（进展 / 决策）

- 2026-05-03：创建本子计划。决策：首版 GUI 只读展示状态，不承担任务执行、调度和 runtime 安装。
- 2026-05-03：完成 Phase A。安装开发期 GUI extras，但保持 PySide6 只属于 optional dependency；新增 optional dependency entry helper。
- 2026-05-03：完成 Phase B。新增只读 `MainWindow` 和四个 dockable workstation panels，不启动 worker，不触发 Scheduler claim。
- 2026-05-03：完成 Phase C。新增 SQLite read-only `WorkbenchSnapshot` view model，Queue panel 能显示 task id、node type、status、resource device、event count 和 artifact path。
- 2026-05-03：完成 Phase D 首版布局边界。窗口、workspace panel spec、state reader 已拆分，未把 UI、SQL、scheduler 和 worker 混进一个文件。

## Blockers（阻塞）

- 暂无。
