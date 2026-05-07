# AtelierUI Component Workbench Foundation 计划

> 本计划执行控件画板第一实现阶段：dev-only 启动入口、PySide-independent catalog/state、theme token preview 和 intake checklist preview。不实现真实自绘控件，不迁移 `WorkflowCanvas`。

## Objective

把 `AtelierUI Component Workbench` 从规划推进到最小可打开的 PySide6 开发工具，让候选自绘控件以后可以在真实产品 GUI 之外调参和审查。

首版目标链路：

```text
AtelierUI theme tokens / widget intake checklist
  -> ComponentWorkbenchState
  -> PySide6 ComponentWorkbenchWindow
  -> dev-only module entry
```

## Scope

- 新增 PySide-independent `component_workbench_state.py`。
- 新增 PySide6 `component_workbench.py`。
- 支持 `.venv\Scripts\python -m atelier.gui.ui.component_workbench --no-exec` 测试启动，不进入事件循环。
- 支持无参数启动真实控件画板。
- 首版展示：
  - catalog entries。
  - color token swatches。
  - typography samples。
  - widget intake checklist。
  - `WorkflowNodeItem` 候选 placeholder。
- 使用 TDD：先写 `tests/test_gui_atelier_ui_component_workbench.py` 的失败测试。

暂不实现：

- 参数 sliders / controls。
- 动画驱动和 motion token。
- screenshot 保存。
- 真实 `WorkflowNodeItem` 自绘控件。
- Qt Designer plugin。
- 自动视觉回归。

## Current Facts

- `docs/plan/plan_atelier_ui_component_workbench.md` 已规划控件画板形态。
- `atelier/gui/ui/theme_tokens.py` 已提供纯 Python `ATELIER_THEME_TOKENS`。
- `atelier/gui/ui/widget_intake.py` 已提供自绘控件入库 checklist。
- 当前已有 `atelier.gui.ui.component_workbench_state` 和 `atelier.gui.ui.component_workbench` 第一阶段入口。

## Constraints

- 控件画板是 dev-only，不进入默认产品 `MainWindow`。
- 控件画板不读取 SQLite，不运行 workflow，不调用 Scheduler、Worker、FFmpeg、model backend 或 shell。
- `component_workbench_state.py` 不得 import PySide6。
- 候选 story 只是 placeholder，不代表控件已审查通过。
- 本阶段不临时实现半套 i18n；控件画板可见 UI 文案统一使用中文，代码标识、objectName、token role、类名、命令参数和产品模型名保持原文。

## Execution Plan

### Phase A: Red tests

目标：

- 新增 `tests/test_gui_atelier_ui_component_workbench.py`。
- 先确认测试因缺少 `component_workbench_state` / `component_workbench` 失败。

完成信号：

- 目标测试红灯，失败原因来自缺少新模块或新 API。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 已完成。

### Phase B: PySide-independent workbench state

目标：

- 新增 story / catalog / token preview view models。

完成信号：

- 测试可读取 catalog id。
- token swatches 来自 `ATELIER_THEME_TOKENS`。
- intake checklist 包含 user review。
- state module 不 import PySide6。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 已完成。

### Phase C: Dev-only PySide6 window

目标：

- 新增 `ComponentWorkbenchWindow` 和 `build_component_workbench_window()`。

完成信号：

- offscreen Qt 可构造窗口。
- objectName 可定位。
- 不构造产品 `MainWindow`。
- 中央 preview / catalog / controls / checklist 可被测试定位。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 已完成。

### Phase D: Launch entry

目标：

- 新增 `parse_workbench_args()` 和 `main()`。

完成信号：

- `--no-exec` 构造窗口后返回 `0`，不进入事件循环。
- 无参数入口可显示窗口并进入 `QApplication.exec()`。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 已完成。

### Phase E: Docs and verification

目标：

- 更新 code map、recent changes、component workbench plan 和 README。
- 运行目标测试、GUI 组合测试、全量 unittest、compileall、文档空白扫描和 `git diff --check`。

完成信号：

- 接手文档准确记录画板入口和边界。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'
git diff --check
```

状态：

- 已完成。

## Child Plans

- 后续可拆 `plan_atelier_ui_component_workbench_controls.md`，用于参数 controls / size presets / background presets。
- 后续可拆 `plan_atelier_ui_component_workbench_screenshot.md`，用于 screenshot / review notes。

## Verification

计划验证命令：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'
git diff --check
```

当前验证事实：

- Red first：`.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench` 先因缺少 `atelier.gui.ui.component_workbench_state` / `atelier.gui.ui.component_workbench` 报 4 errors。
- Green after implementation：`.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench` 已通过，4 tests passed。
- GUI 组合验证：`.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：14 tests passed。
- 全量验证：`.venv\Scripts\python -m unittest discover -s tests`：136 tests passed。
- `compileall`：`.venv\Scripts\python -m compileall -q atelier tests`：passed。
- 文档空白扫描：no matches。
- `git diff --check`：passed with only Windows CRLF conversion warnings。

## Progress / Decisions

- 2026-05-07：创建本计划。决策：控件画板第一阶段只做 dev-only launch entry、token preview、catalog 和 checklist，不做真实自绘控件。
- 2026-05-07：完成 Phase A-D。新增 `component_workbench_state.py`、`component_workbench.py` 和 `tests/test_gui_atelier_ui_component_workbench.py`；画板可在产品 `MainWindow` 外启动，支持 `--no-exec` 测试入口。
- 2026-05-07：完成 Phase E 验证。目标测试、GUI 组合测试、全量 unittest、compileall、文档空白扫描和 `git diff --check` 均通过。
- 2026-05-07：决策：在正式 i18n 管理器接入前，dev-only 控件画板的用户可见文案先统一改为中文，不继续保留英文 labels。
- 2026-05-07：完成控件画板中文化小修。窗口标题、catalog label、候选审查状态、入库清单和截图按钮均改为中文；测试已锁定这些可见文案。

## Blockers

- 暂无。
