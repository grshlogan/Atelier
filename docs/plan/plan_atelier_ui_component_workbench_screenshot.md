# AtelierUI Component Workbench Screenshot 计划

> 本计划推进控件画板第三阶段：手动截图和审查备注留痕。仍然不实现真实自绘控件、不批准入库、不接入产品 `MainWindow`，不运行 workflow / Scheduler / Worker / FFmpeg / model backend。

## Objective

让 `AtelierUI Component Workbench` 能保存当前画板状态的可复查截图和最小审查备注，为后续自绘控件入库审查提供轻量证据。

第三阶段目标链路：

```text
selected story + controls metadata + reviewer note
  -> review snapshot record
  -> PNG screenshot
  -> JSON metadata
```

## Scope

- 新增 PySide-independent review snapshot metadata：
  - selected story id。
  - selected story label。
  - controls id 列表。
  - reviewer note。
  - screenshot filename。
- 画板右侧新增审查备注输入框。
- 启用截图按钮。
- 点击按钮保存当前窗口 PNG 和 JSON 记录。
- 默认输出到仓库内开发目录 `.atelier/component-workbench/reviews/`。
- 文件名只使用 story id 和时间戳，不包含用户媒体路径。

暂不实现：

- 自动视觉回归。
- 图片 diff。
- 审查备注数据库。
- 用户审查批准状态切换。
- 自绘控件入库。
- 产品内截图或日志导出。

## Current Facts

- `docs/plan/plan_atelier_ui_component_workbench_foundation.md` 已完成第一阶段。
- `docs/plan/plan_atelier_ui_component_workbench_controls.md` 已完成第二阶段。
- 当前画板可打开、可切换 story，并展示 states / controls metadata。
- 当前截图按钮已启用，可保存当前窗口 PNG 和 JSON 记录。
- 当前已有审查备注输入框和 review snapshot 记录。

## Constraints

- 控件画板必须 dev-only，不进入默认产品 `MainWindow`。
- 控件画板不得运行 Worker、FFmpeg、模型推理、硬件调度、任意 shell 或 SQLite mutation。
- `component_workbench_state.py` 不得 import PySide6。
- Review snapshot 不得包含用户媒体路径、secrets、worker logs、SQLite rows 或系统环境变量。
- 保存 review snapshot 不代表控件已通过用户审查或可共享入库。

## Execution Plan

### Phase A: Red tests for review snapshot metadata and UI

目标：

- 扩展 `tests/test_gui_atelier_ui_component_workbench.py`。
- 先确认测试因缺少 review snapshot metadata、note editor 或 enabled screenshot action 失败。

完成信号：

- 目标测试红灯，失败原因来自尚未实现的 review snapshot 或 screenshot UI。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 已完成。

### Phase B: PySide-independent review snapshot

目标：

- 新增 review snapshot dataclass 和 builder。

完成信号：

- 可根据 `ComponentWorkbenchState`、story id、note 和 screenshot filename 构造可 JSON 化记录。
- 记录不包含绝对用户路径。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 已完成。

### Phase C: Screenshot and note UI

目标：

- 新增审查备注输入框。
- 启用截图按钮。
- 为测试暴露稳定 objectName。

完成信号：

- tests 可定位 `component-workbench-review-note`。
- tests 可定位 enabled `component-workbench-save-review`.

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 已完成。

### Phase D: Save review artifacts

目标：

- 点击按钮保存 PNG 和 JSON。

完成信号：

- 可注入 review output directory。
- tests 可调用保存方法并确认 PNG / JSON 存在。
- JSON 记录 story id、note、controls 和 screenshot filename。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 已完成。

### Phase E: Docs and verification

目标：

- 更新 code map、recent changes、README 和相关 plan。
- 运行目标测试、GUI 组合测试、全量 unittest、compileall、文档空白扫描和 `git diff --check`。

完成信号：

- 接手文档准确记录第三阶段能力和边界。

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

- 后续可拆 `plan_atelier_ui_workflow_node_item_intake.md`，用于真实 `WorkflowNodeItem` 候选自绘控件审查。
- 后续可拆 `plan_atelier_ui_component_workbench_visual_regression.md`，用于图片 diff 或自动视觉回归。

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

- Red first：`.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench` 先因缺少 `build_review_snapshot_record()`、可注入 review output dir、审查备注输入框和启用的截图按钮而失败。
- Green after implementation：`.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench` 已通过，8 tests passed。
- GUI 组合验证：`.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke`：18 tests passed。
- 全量验证：`.venv\Scripts\python -m unittest discover -s tests`：140 tests passed。
- `compileall`：`.venv\Scripts\python -m compileall -q atelier tests`：passed。
- 文档空白扫描：no matches。
- `git diff --check`：passed with only Windows CRLF conversion warnings。

## Progress / Decisions

- 2026-05-07：创建本计划。决策：第三阶段只做手动截图和 JSON 审查备注留痕，不做视觉 diff、数据库、批准状态或产品内导出。
- 2026-05-07：完成 Phase A-D。新增 review snapshot metadata builder、审查备注输入框、保存截图和备注按钮；可注入输出目录并保存 PNG / JSON。
- 2026-05-07：完成 Phase E 验证。目标测试、GUI 组合测试、全量 unittest、compileall、文档空白扫描和 `git diff --check` 均通过。

## Blockers

- 暂无。
