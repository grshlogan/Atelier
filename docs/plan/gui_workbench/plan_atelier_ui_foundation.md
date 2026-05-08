# AtelierUI Foundation 计划

> 本计划执行 GUI 专属库的第一块最小地基：目录边界、纯 Python theme tokens、以及自绘控件入库审查模板。不实现动画驱动，不迁移现有 `WorkflowCanvas`，不新增第三方依赖。

## Objective

建立 `AtelierUI` 的首个可测试本地库边界，让后续 Workflow Canvas、Execution Canvas、Queue Monitor、Inspector 和 motion 工作有统一的视觉 token 与自绘控件审查入口。

首版目标链路：

```text
DESIGN.md palette / typography / density facts
  -> atelier.gui.ui.theme_tokens
  -> feature widgets can consume stable pure-Python tokens later

AtelierUI governance rule
  -> atelier.gui.ui.widget_intake
  -> self-painted widget review checklist
```

## Scope

- 新增 `atelier/gui/ui/` 作为 Atelier 本地专属 UI 库目录。
- 新增 `theme_tokens.py`，只承载纯 Python token，不 import PySide6。
- 新增 `widget_intake.py`，记录自绘控件入库审查步骤。
- 新增 `atelier/gui/ui/README.md`，说明该目录不是成熟外部库。
- 使用 TDD：先写 `tests/test_gui_atelier_ui_foundation.py` 的失败测试，再实现最小代码。
- 更新 `APP_CODE_MAP.md`、`RECENT_CHANGES.md` 和相关 plan。

暂不实现：

- `AnimationDriver`。
- easing curve runtime wrapper。
- overlay layer。
- self-painted widget 抽取。
- `WorkflowCanvas` 迁移。
- Qt `.qrc`、IconManager、theme switching 或 runtime style application。

## Current Facts

- `DESIGN.md` 已定义默认深色 palette、typography 和桌面工作台密度规则。
- `docs/UI_MOTION_SPEC.md` 已规划 `atelier/gui/ui/` 的未来模块，包括 `theme_tokens.py`、`easing.py`、`motion.py`、`overlay.py`、`painted_widgets.py`、`page_transitions.py` 和 `queue_delegate.py`。
- `docs/plan/gui_workbench/plan_atelier_ui_local_library_governance.md` 已规定：`AtelierUI` 是本地专属库，新自绘控件入库并被软件调用前必须经过用户审查，有参考项目时先调研借鉴。
- 当前 `atelier/gui/workflow_canvas.py` 内部直接使用颜色和尺寸常量，但本计划不迁移它，避免扩大范围。

## Constraints

- `atelier.gui.ui` import 不得隐式 import PySide6 或创建 Qt application。
- theme token 只表达视觉事实，不读写 SQLite，不调用 Scheduler、RuntimeManager、Worker、FFmpeg 或外部工具。
- 自绘控件审查模板只记录准入步骤，不自动批准任何控件。
- 不把 `AtelierUI` 描述成对外稳定 API。
- 代码标识符保持英文；用户文档可使用中文。

## Execution Plan

### Phase A: Plan and red tests

目标：

- 创建本计划。
- 写 `tests/test_gui_atelier_ui_foundation.py`，先验证缺少 `atelier.gui.ui` 的红灯。

完成信号：

- 目标测试先失败，失败原因来自缺少新模块或新 API。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_foundation
```

状态：

- 已完成。

### Phase B: Minimal package boundary

目标：

- 新增 `atelier/gui/ui/__init__.py`。
- 新增 `atelier/gui/ui/README.md`，写明专属库边界和用户审查规则。

完成信号：

- `import atelier.gui.ui` 不 import PySide6。
- README 说明该库不作为成熟库发布。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_foundation
```

状态：

- 已完成。

### Phase C: Theme tokens

目标：

- 新增 `theme_tokens.py`，覆盖首版颜色、字体、typography、radius 和 Workflow Canvas 基础尺寸 token。

完成信号：

- 测试能读取 `DESIGN.md` 中的关键 palette roles。
- token 为 frozen dataclass 或等价不可变结构。
- 不依赖 PySide6。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_foundation
```

状态：

- 已完成。

### Phase D: Widget intake template

目标：

- 新增 `widget_intake.py`，用代码级 checklist 固化自绘控件入库审查步骤。

完成信号：

- checklist 包含 purpose、reference review、minimal test、Atelier-specific implementation、user review。
- checklist 不会把任何候选控件自动标为 approved。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_foundation
```

状态：

- 已完成。

### Phase E: Handoff docs and verification

目标：

- 更新 code map、recent changes 和相关主计划。
- 运行目标测试、最小 GUI smoke、全量 unittest、compileall、文档空白扫描和 `git diff --check`。

完成信号：

- 接手文档能说明 `AtelierUI` 已有的最小模块和仍未实现范围。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_foundation
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_foundation tests.test_gui_workflow_canvas_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'
git diff --check
```

状态：

- 已完成。

## Child Plans

- 后续可拆 `plan_gui_motion_foundation.md`，用于 `easing.py`、`motion.py` 和 reduced motion；计划文件应放在 `docs/plan/gui_workbench/`。
- 后续可拆 `plan_atelier_ui_self_painted_widget_intake.md`，用于某个具体自绘控件进入专属库前的审查；计划文件应放在 `docs/plan/gui_workbench/`。

## Verification

计划验证命令：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_foundation
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_foundation tests.test_gui_workflow_canvas_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'
git diff --check
```

当前验证事实：

- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_foundation`：red first，4 errors because `atelier.gui.ui` did not exist。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_foundation`：4 tests passed after minimal implementation。
- `.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_foundation tests.test_gui_workflow_canvas_foundation tests.test_gui_smoke`：14 tests passed。
- `.venv\Scripts\python -m unittest discover -s tests`：132 tests passed。
- `.venv\Scripts\python -m compileall -q atelier tests`：passed。
- `Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'`：no matches。
- `git diff --check`：passed with only Windows CRLF conversion warnings。

## Progress / Decisions

- 2026-05-07：创建本计划。决策：第一步只做 `atelier/gui/ui/` 最小地基、纯 Python tokens 和入库审查模板，不实现动画驱动，不迁移现有 `WorkflowCanvas`。
- 2026-05-07：TDD 红灯确认：`tests.test_gui_atelier_ui_foundation` 因缺少 `atelier.gui.ui` 失败。
- 2026-05-07：完成 Phase B-D。新增 `atelier/gui/ui/__init__.py`、`theme_tokens.py`、`widget_intake.py` 和 `README.md`；目标测试绿灯。
- 2026-05-07：完成 Phase E。code map、recent changes、README、UI motion spec 和主计划已对齐；全量验证为 132 tests passed。

## Blockers

- 暂无。
