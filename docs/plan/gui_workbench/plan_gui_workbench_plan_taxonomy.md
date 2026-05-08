# GUI Workbench Plan Taxonomy

## Objective

整理 GUI 专线、AtelierUI 控件画板、UI 打磨和候选节点卡片相关计划，避免 `docs/plan/` 根目录继续堆积大量短周期 UI 试验计划。

## Scope

- 建立 `docs/plan/gui_workbench/` 作为 GUI / AtelierUI / 控件画板 / UI 打磨计划目录。
- 保留仍需维护的 GUI 主计划、Workflow Canvas 基础计划、AtelierUI 治理计划、控件画板主计划、节点卡片候选计划。
- 将已完成的控件画板阶段计划归档到 `docs/plan/gui_workbench/archive/component_workbench_phases/`。
- 更新当前文档索引和活跃计划之间的相对链接。

## Current Facts

- GUI 专线和后端统筹已经在对话层拆分。
- `AtelierUI` 是 Atelier 本地专属 UI 库，不作为成熟库发布。
- 控件画板用于候选自绘控件入库前的参数调试、状态展示、截图和用户审查。
- UI 打磨会长期产生许多短周期计划，继续放在 `docs/plan/` 根目录会降低可读性。

## Constraints

- 不移动后端、Scheduler、Worker、RuntimeManager、Storage、adapter、release 或 security 计划。
- 不把 UI 打磨中的临时截图或 `.atelier/` 审查产物纳入 GitHub。
- 归档计划保留历史信息，但不再作为当前执行入口。
- 当前 GUI 代码不因本次文档整理改变。

## Execution Plan

### Phase A - 建立目录边界

- 创建 `docs/plan/gui_workbench/`。
- 创建 `docs/plan/gui_workbench/archive/component_workbench_phases/`。
- 添加该 taxonomy 计划和目录索引。

验证：`docs/plan/gui_workbench/` 下能清楚区分 active plans 与 archive。

### Phase B - 移动活跃 GUI / UI 打磨计划

- 移动 GUI 专线主计划、Workflow Canvas 基础计划、AtelierUI 治理与地基计划、控件画板主计划、Workflow Canvas 节点卡片候选计划。
- 保留通用后端和全局主计划在 `docs/plan/` 根目录。

验证：README 和主计划中的当前入口不再指向旧路径。

### Phase C - 归档完成阶段计划

- 将控件画板 foundation / controls / screenshot / review page 阶段计划归档。
- 将一次性 UI motion spec 写作计划归档。

验证：根 `docs/plan/` 不再暴露已完成的控件画板 phase 文件。

### Phase D - 链接和空白检查

- 更新 README、`docs/UI_MOTION_SPEC.md`、相关活跃 plan 的链接。
- 运行文档空白扫描和 `git diff --check`。

## Child Plans

- 当前无子计划。本文件用于整理 plan 分类，不引入 GUI 代码实现阶段。

## Verification

- `Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\docs\plan\gui_workbench\*.md, .\docs\plan\gui_workbench\archive\component_workbench_phases\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'`
- `git diff --check`

## Progress / Decisions

- 2026-05-08：决定把 GUI / AtelierUI / 控件画板 / UI 打磨计划隔离到 `docs/plan/gui_workbench/`。
- 2026-05-08：决定把已完成控件画板 phase 计划放入 `docs/plan/gui_workbench/archive/component_workbench_phases/`。
- 2026-05-08：完成活跃 GUI 计划移动、已完成 phase 计划归档，并更新 README、`docs/UI_MOTION_SPEC.md`、`docs/plan/plan_main_app_skeleton.md` 和活跃计划链接。

## Blockers

- 无。
