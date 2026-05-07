# AtelierUI Component Workbench Controls 计划

> 本计划推进控件画板第二阶段：catalog 可切换、story 元数据更完整、基础 controls 面板可见。仍然不实现真实自绘控件、不接入产品 `MainWindow`、不运行 workflow / Scheduler / Worker / FFmpeg / model backend。

## Objective

把 `AtelierUI Component Workbench` 从静态 token/checklist 预览推进到可选择 story、查看候选控件状态和基础参数的开发审查工具。

第二阶段目标链路：

```text
ComponentWorkbenchState stories / controls
  -> catalog selection
  -> selected story preview
  -> controls panel
  -> review checklist remains visible
```

## Scope

- 扩展 PySide-independent story metadata：
  - story id。
  - label。
  - surface。
  - summary。
  - states。
  - controls。
  - review status。
- 支持左侧 catalog 切换当前 story。
- 中央 preview 标题和说明随选中 story 更新。
- 右侧 controls 面板展示候选参数定义。
- Controls 首版只展示元数据，不实时修改真实绘制结果。
- UI 可见文案继续使用中文；代码标识、objectName、token role、类名、命令参数和产品模型名保持原文。
- 根目录提供开发入口脚本 `open_atelier_ui_workbench.ps1`，用于快速打开控件画板。

暂不实现：

- 真实自绘 `WorkflowNodeItem`。
- 参数 slider 真正驱动绘制。
- motion playback。
- screenshot 保存。
- review notes 持久化。
- 自动视觉回归。

## Current Facts

- `docs/plan/plan_atelier_ui_component_workbench_foundation.md` 已完成第一阶段。
- 当前画板可打开，并展示 token swatches、typography samples、candidate placeholder 和 intake checklist。
- 当前 catalog 已可切换 story，并更新 preview / controls 元数据。
- 当前 story metadata 已描述基础 states 和 controls。
- 当前 screenshot 按钮是禁用占位。
- 当前根目录已有快速打开控件画板的 PowerShell 开发入口 `open_atelier_ui_workbench.ps1`。

## Constraints

- 控件画板必须 dev-only，不进入默认产品 `MainWindow`。
- 控件画板不得运行 Worker、FFmpeg、模型推理、硬件调度、任意 shell 或 SQLite mutation。
- `component_workbench_state.py` 不得 import PySide6。
- 候选 story 和 controls 只是审查元数据，不代表控件已审查通过。
- 不引入 web stack、Electron、React、QML 或 Qt Designer plugin。

## Execution Plan

### Phase A: Red tests for story controls and selection

目标：

- 扩展 `tests/test_gui_atelier_ui_component_workbench.py`。
- 先确认测试因缺少 story states / controls 或 catalog selection 行为失败。

完成信号：

- 目标测试红灯，失败原因来自尚未实现的 story metadata 或 selection update。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 已完成。

### Phase B: PySide-independent story metadata

目标：

- 扩展 `ComponentStoryView` 和新增 control view model。

完成信号：

- `workflow-node` story 暴露基础 states 和 controls。
- state module 仍不 import PySide6。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 已完成。

### Phase C: Catalog selection updates preview

目标：

- 让左侧 catalog selection 驱动当前 story。

完成信号：

- 选择 `WorkflowNodeItem 候选` 后，中央 preview 标题、说明和审查状态更新。
- `tokens` story 仍可查看 token/typography preview。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 已完成。

### Phase D: Controls panel

目标：

- 新增右侧 controls panel，展示当前 story 的基础参数和可选状态。

完成信号：

- tests 可定位 `component-workbench-controls-panel`。
- `workflow-node` story 可展示 `selected`、`hovered`、`density` 等元数据。
- controls 不运行真实绘制或产品逻辑。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 已完成。

### Phase E: Docs and verification

目标：

- 更新 code map、recent changes、README 或相关 plan。
- 运行目标测试、GUI 组合测试、全量 unittest、compileall、文档空白扫描和 `git diff --check`。

完成信号：

- 接手文档准确记录第二阶段能力和边界。

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

### Phase F: Root PowerShell launcher

目标：

- 在仓库根目录新增 `open_atelier_ui_workbench.ps1`，快速打开控件画板。

完成信号：

- 脚本从自身路径定位仓库根目录。
- 优先使用 `.venv\Scripts\python.exe`。
- 调用 `-m atelier.gui.ui.component_workbench`。
- 支持透传额外参数。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 已完成。

## Child Plans

- 后续可拆 `plan_atelier_ui_component_workbench_screenshot.md`，用于 screenshot / review notes。
- 后续可拆 `plan_atelier_ui_workflow_node_item_intake.md`，用于真实 `WorkflowNodeItem` 候选自绘控件审查。

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

- Red first：`.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench` 先因 `ComponentStoryView` 缺少 `controls`、窗口缺少 selected story preview / controls panel 而失败。
- Root launcher red first：`.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench` 先因 `open_atelier_ui_workbench.ps1` 不存在而失败。
- Green after implementation：`.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench` 已通过，5 tests passed。
- GUI 组合验证：`.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：15 tests passed。
- 全量验证：`.venv\Scripts\python -m unittest discover -s tests`：137 tests passed。
- `compileall`：`.venv\Scripts\python -m compileall -q atelier tests`：passed。
- 文档空白扫描：no matches。
- `git diff --check`：passed with only Windows CRLF conversion warnings。
- Root launcher：`powershell -NoProfile -ExecutionPolicy Bypass -File .\open_atelier_ui_workbench.ps1 --no-exec`：passed。

## Progress / Decisions

- 2026-05-07：创建本计划。决策：第二阶段只做 story selection、states / controls metadata 和 controls panel，不做真实自绘控件或截图持久化。
- 2026-05-07：完成 Phase A-D。`ComponentStoryView` 新增 states / controls；左侧 catalog 可切换当前 story；中央 preview 和右侧 controls panel 会随选择更新。
- 2026-05-07：完成 Phase E 验证。目标测试、GUI 组合测试、全量 unittest、compileall、文档空白扫描和 `git diff --check` 均通过。
- 2026-05-07：开始 Phase F。按用户要求在软件根目录补一个快速打开控件画板的 PowerShell 开发入口。
- 2026-05-07：完成 Phase F。新增 `open_atelier_ui_workbench.ps1`，从仓库根目录快速启动 `atelier.gui.ui.component_workbench`，并透传额外参数。

## Blockers

- 暂无。
