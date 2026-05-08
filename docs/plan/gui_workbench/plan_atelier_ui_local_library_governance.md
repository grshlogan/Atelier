# AtelierUI 本地专属库治理计划

> 本计划只处理 GUI 专属 UI 基础库的治理边界，不实现新控件，不迁移现有 canvas 代码，不引入第三方 UI runtime 依赖。

## Objective

建立 Atelier 本地专属 UI 库的准入规则，使后续自绘控件、动效、overlay、theme tokens 和共享视觉基础有统一归宿，同时避免把它扩张成对外发布的成熟通用库。

核心结论：

```text
AtelierUI is a project-specific local UI library.
It is packaged with Atelier runtime or core application code.
Every new self-painted widget needs user review before library adoption and product use.
Reference first, then implement.
```

## Scope

- 记录 `AtelierUI` 作为本软件专属库的定位。
- 约束未来路径，例如 `atelier/gui/ui/`，但本计划不立即创建代码目录。
- 规定自绘控件进入专属库并被软件调用前必须经过用户审查。
- 规定有开源参考项目或参考代码时，先阅读和提炼，再做 Atelier 自己的实现。
- 对齐 `AGENTS.md`、`docs/UI_MOTION_SPEC.md`、GUI 主计划、Workflow Canvas foundation 计划、code map 和 recent changes。

暂不实现：

- 新的 self-painted widgets。
- `AnimationDriver`、theme tokens、overlay layer 或 queue delegate 代码。
- 第三方代码 vendoring。
- 对外发布的 PyPI / pip library。
- 迁移当前 `atelier/gui/workflow_canvas.py` 到 `atelier/gui/ui/`。

## Current Facts

- `docs/UI_MOTION_SPEC.md` 已规划 `AtelierUI`，并列出 theme tokens、easing curves、animation driver、motion values、overlay layer、self-painted widgets、queue delegate animation 和 page transition manager。
- `atelier/gui/workflow_canvas.py` 已作为首个 PySide6-native Workflow Canvas foundation 存在，但当前仍属于 GUI feature 模块，不是已审查入库的通用 self-painted widget 基础库。
- `DESIGN.md` 是视觉与交互事实源，要求 Workflow Canvas 使用卡片式轻节点系统，动效解释状态变化而不是装饰。
- 当前开源参考项目只作为学习来源；`docs/UI_MOTION_SPEC.md` 已明确不把这些项目作为当前依赖或 vendored code。
- 用户已规定：本地必须有本软件专属库，放置软件自绘控件、动画效果和其他共享 GUI 基础；该库暂不做完整库发布，只作为软件专属代码打包在 Runtime 或核心代码里。

## Constraints

- 新自绘控件在进入 `AtelierUI` 并被软件调用前，必须经过用户审查。
- 自绘控件如有参考代码或参考项目，必须优先调研和借鉴结构、边界、测试方式或交互模式，不鼓励无依据手搓。
- 参考项目代码不得绕过许可证、third-party notice、security review 或 packaging plan。
- 明显不稳定、bug 过多、许可证或维护状态不可确认的项目不进入 AtelierUI 参考体系；可以记录为 rejected candidate，避免后续重复评估。
- `AtelierUI` 不能绕过 `WorkspaceManager`、`I18nManager`、Scheduler / RuntimeManager 边界或 GUI intent / snapshot / view model 边界。
- `AtelierUI` 只做 GUI visual / interaction 基础，不执行业务 workflow、worker、FFmpeg、模型推理、硬件调度或任意 shell。
- 当前先沉淀文档规则，不扩大到代码重构。

## Execution Plan

### Phase A: Governance docs

目标：

- 把专属库、审查和参考优先规则写入项目规则与 GUI motion spec。

完成信号：

- `AGENTS.md` 明确本地专属 UI 库是 GUI 开发硬边界。
- `docs/UI_MOTION_SPEC.md` 明确 `AtelierUI` 的本地库定位、打包边界和入库审查流程。

验证：

```powershell
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'
git diff --check
```

状态：

- 已完成。

### Phase B: Plan and handoff alignment

目标：

- 将规则同步到 GUI 主计划、Workflow Canvas foundation 计划、APP_CODE_MAP 和 RECENT_CHANGES。

完成信号：

- GUI 主计划把 `AtelierUI` 治理作为 motion/workspace 后续工作的前置约束。
- Workflow Canvas foundation 计划标注当前 canvas 是候选基础，不等于已审查入库的 self-painted widget 库。
- code map 和 recent changes 能让后续接手者看到这条规则。

验证：

```powershell
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'
git diff --check
```

状态：

- 已完成。

## Child Plans

- 后续可拆 `docs/plan/gui_workbench/plan_gui_motion_foundation.md`，用于真正实现 motion tokens / animation driver。
- 后续可拆 `docs/plan/gui_workbench/plan_atelier_ui_self_painted_widget_intake.md`，用于某个具体自绘控件的参考调研、TDD、用户审查和入库流程。

## Verification

文档级验证命令：

```powershell
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'
git diff --check
```

当前验证事实：

- `Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'`：no matches。
- `git diff --check`：passed with only Windows CRLF conversion warnings。

## Progress / Decisions

- 2026-05-07：创建本计划。决策：`AtelierUI` 是 Atelier 本地专属 UI 库，不作为成熟通用库发布；新自绘控件先用户审查，再入库并被软件调用；参考项目优先阅读和借鉴，不无依据手搓。
- 2026-05-07：决策：本次只更新文档和治理边界，不创建 `atelier/gui/ui/` 代码目录，不迁移 `workflow_canvas.py`。
- 2026-05-07：后续 `plan_atelier_ui_foundation.md` 已创建 `atelier/gui/ui/` 最小地基；该目录目前只有纯 Python tokens 和 intake checklist，仍没有已审查的共享自绘控件。
- 2026-05-07：决策：`Moekotori/ECHO` 不纳入 Atelier 参考体系。原因：用户评估该软件 bug 过多，不适合作为 GUI、AtelierUI、插件、发布或 smoke checklist 的参考依据。

## Blockers

- 暂无。
