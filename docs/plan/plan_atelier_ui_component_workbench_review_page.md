# AtelierUI Component Workbench Review Page 计划

> 本计划只规划控件画板的静态 HTML review page，不实现代码。目标是让 PySide6 原生控件画板保存的 PNG / JSON 审查记录，可以生成可在 Codex 浏览器中打开和批注的页面。

## Objective

把 `AtelierUI Component Workbench` 的审查产物从“PNG + JSON 文件”推进到“可浏览器打开的静态 review page”。

核心目标：

```text
PySide6 Workbench
  -> PNG screenshot + JSON review snapshot
  -> static HTML review page
  -> Codex browser annotation
  -> developer applies feedback back to PySide6 widgets / tokens / controls
```

这条路线不把控件改成 Web 技术，也不迁移到 React / Electron / QML。浏览器只作为审查和批注辅助，真实控件仍然以 PySide6 / Qt 为准。

## Scope

- 生成单个静态 HTML review page。
- 页面读取或嵌入当前 review snapshot 的关键信息：
  - screenshot。
  - story id / label / surface。
  - states。
  - controls。
  - reviewer note。
  - screenshot filename。
  - metadata filename。
- 页面用中文展示可见文案。
- 页面不需要前端构建系统，不引入 React、Vue、Electron、Tauri 或 Web server。
- 支持从控件画板保存 review snapshot 后生成对应 HTML。
- 支持根目录开发脚本或画板 UI 提示最近一次 review page 路径。

暂不实现：

- 浏览器内编辑参数后反写 PySide6。
- 自动视觉 diff。
- 多 review session 数据库。
- 在线上传或远程分享。
- GitHub Pages。
- CI 自动发布审查页面。

## Current Facts

- 当前控件画板是 dev-only PySide6 工具。
- 当前画板可保存 PNG screenshot 和 JSON metadata。
- 当前默认输出目录是 `.atelier/component-workbench/reviews/`。
- `.gitignore` 已忽略 `.atelier/`，因此本地生成的截图、JSON 和未来 HTML review page 默认不会进入 Git。
- 当前根目录已有 `open_atelier_ui_workbench.ps1` 作为开发快捷入口。
- 当前 Codex 浏览器更适合打开 HTML 页面做视觉定位、截图和批注；它不能直接操作 PySide6 widget tree。

## Constraints

- GUI 仍然不直接运行 Worker、FFmpeg、模型推理、硬件调度或 SQLite mutation。
- HTML review page 是静态审查报告，不是产品页面。
- Review page 不得包含 secrets、用户媒体路径、worker logs、SQLite rows、绝对开发机路径或系统环境变量。
- Review page 不能代表控件已通过用户审查；它只是审查证据。
- 生成的 review artifacts 不进入 GitHub。
- 页面模板源码可以进入 GitHub，但生成页面不进入。

## GitHub Decision

结论：

```text
画板源码应该进 GitHub。
画板生成的审查产物不应该进 GitHub。
```

应该进入 GitHub 的内容：

- `atelier/gui/ui/component_workbench.py`。
- `atelier/gui/ui/component_workbench_state.py`。
- 未来 review page 生成器源码。
- 未来静态 HTML 模板源码。
- `tests/test_gui_atelier_ui_component_workbench.py`。
- `open_atelier_ui_workbench.ps1`。
- `docs/plan/` 下的控件画板计划文档。
- `README.md` / `APP_CODE_MAP.md` / `RECENT_CHANGES.md` 中的入口和边界说明。

理由：

- 这是 Atelier GUI 专属开发工具链的一部分，不是个人临时脚本。
- 它承载自绘控件入库前的审查流程和测试边界。
- 后续所有开发者和 AI agent 都需要同一套画板入口、story metadata、review snapshot 行为和验证命令。
- 源码进入 GitHub 能让审查流程可复现，也方便 CI / code review 覆盖。

不应该进入 GitHub 的内容：

- `.atelier/component-workbench/reviews/*.png`。
- `.atelier/component-workbench/reviews/*.json`。
- `.atelier/component-workbench/reviews/*.html`。
- 用户手写审查备注原始产物。
- 任何真实媒体、真实项目路径、真实工作区截图、日志或本地绝对路径。

理由：

- 审查产物可能包含本地 UI 状态、个人备注、时间戳和上下文。
- 截图和 HTML review page 是可再生成产物，应该留在 `.atelier/` 本地开发数据里。
- `.atelier/` 已经被 `.gitignore` 忽略，符合当前项目边界。

例外：

- 如果未来需要测试 fixture，可新增小型合成样例，放在明确的 `tests/fixtures/` 或 `docs/fixtures/`，并确保不包含真实路径、真实媒体或隐私信息。

## Execution Plan

### Phase A: Plan and GitHub boundary

目标：

- 写清 review page 方案和 GitHub 收录判断。

完成信号：

- 本计划存在。
- README / main component workbench plan 能索引到本计划。
- GitHub 决策写清楚源码和生成产物的边界。

验证：

```powershell
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'
git diff --check
```

状态：

- 已完成。

### Phase B: Review page metadata contract

目标：

- 扩展 review snapshot metadata，使 HTML 页面无需读本地绝对路径即可渲染。

完成信号：

- review snapshot 提供相对 screenshot filename 和 display fields。
- 测试确认 metadata 不包含绝对路径。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 未开始。

### Phase C: Static HTML generation

目标：

- 新增静态 HTML review page 生成器。

完成信号：

- 保存 review snapshot 后可以生成 `.html` 文件。
- HTML 包含 screenshot、story、states、controls、note。
- HTML 不依赖 Web server 或前端构建工具。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 未开始。

### Phase D: Browser handoff

目标：

- 让开发者能快速打开最近一次 HTML review page。

完成信号：

- 画板 UI 或根目录脚本能展示 / 输出 review page 路径。
- Codex 浏览器可打开本地 HTML 文件进行批注。

验证：

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

状态：

- 未开始。

### Phase E: Docs and verification

目标：

- 更新 code map、recent changes、README 和相关 plan。
- 运行目标测试、GUI 组合测试、全量 unittest、compileall、文档空白扫描和 `git diff --check`。

完成信号：

- 接手文档准确记录 review page 能力和 GitHub 边界。

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

- 未开始。

## Child Plans

- 后续可拆 `plan_atelier_ui_component_workbench_visual_regression.md`，用于图片 diff 或自动视觉回归。
- 后续可拆 `plan_atelier_ui_workflow_node_item_intake.md`，用于真实 `WorkflowNodeItem` 候选自绘控件审查。

## Verification

计划验证命令：

```powershell
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'
git diff --check
```

当前验证事实：

- 文档空白扫描：no matches。
- `git diff --check`：passed with only Windows CRLF conversion warnings。

## Progress / Decisions

- 2026-05-07：创建本计划。决策：控件画板源码、测试、文档和开发脚本应该进 GitHub；`.atelier/component-workbench/reviews/` 下生成的 PNG / JSON / HTML 审查产物不进 GitHub。
- 2026-05-07：决策：Codex 浏览器用于 HTML review page 批注，不作为真实 PySide6 控件运行环境。
- 2026-05-07：完成 Phase A。README 和主控件画板计划已索引本计划，文档空白扫描和 `git diff --check` 通过。

## Blockers

- 暂无。
