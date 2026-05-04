# UI Design Source Alignment Plan

## Objective

对齐 `DESIGN.md`、`docs/Atelier_Main_UI_Spec.md`、`docs/UI_WORKSPACE_SPEC.md` 和接手文档中关于主 UI 的事实源层级、深色主题、主工作区布局、可停靠/浮动面板、侧边栏和品牌命名的规则。

## Scope

- 将 `DESIGN.md` 保持为设计事实源，并吸收用户确认的主 UI 决策。
- 将 `docs/Atelier_Main_UI_Spec.md` 明确定位为主界面绘制规格 / concept implementation spec。
- 将 `docs/design-md-references/` 明确为建设性意见源，不作为 Atelier 事实源。
- 统一品牌名为 `Atelier`。
- 对齐 `README.md`、`docs/UI_WORKSPACE_SPEC.md` 和 `docs/RECENT_CHANGES.md`。

## Current Facts

- `DESIGN.md` 当前仍写默认浅色工作台。
- `docs/Atelier_Main_UI_Spec.md` 当前包含深色主界面概念图规格，但标题和正文仍出现非 Atelier 品牌名。
- 用户已确认主视觉主题应以深色为主，浅色保留为未来主题切换。
- 用户已确认 `DESIGN.md` 仍是设计事实源，`Atelier_Main_UI_Spec.md` 是主界面绘制规格。
- 用户已确认主界面应以 Workflow 页和“卡片-连线-流程图”为最高优先级，并通过可嵌入/可浮动 panels 承载 Queue Monitor、Hardware Resources 和 Card Detailed Settings。
- `docs/UI_WORKSPACE_SPEC.md` 已有 `QMainWindow/QDockWidget`、panel float/save/restore 和 workspace preset 规划。
- `E:\AI\AiVideoSRTGui\app\gui\sidebar_navigation.py` 可作为可收缩侧边栏实现参考。
- `atelier/assets/` 已存在，并且是当前软件 toolbar、navigation、workflow nodes、queue、hardware、status、inspector 和 system 图标资源目录。

## Constraints

- 本计划只更新文档，不推进 Scheduler/Worker Phase。
- 不把真实 UI 实现写成已完成。
- 不让 `Atelier_Main_UI_Spec.md` 覆盖 `DESIGN.md` 的事实源地位。
- 不直接复制外部品牌色、字体或营销结构；`docs/design-md-references/` 只作为建设性意见源。
- `atelier/assets/` 只确认资源事实，不声明已实现 Qt `.qrc`、IconManager、图标缓存或运行时主题重染色。

## Execution Plan

1. 更新 `DESIGN.md`
   - 深色主主题成为默认视觉基线。
   - 浅色主题降级为未来可切换主题。
   - 明确设计源层级。
   - 重写主布局规则：顶部栏、可收缩侧边栏、Workflow 复页、嵌入/浮动 panels。
2. 更新 `docs/Atelier_Main_UI_Spec.md`
   - 去除非 Atelier 品牌名并统一为 `Atelier`。
   - 增加与 `DESIGN.md` 的关系说明。
   - 将固定坐标标记为概念图绘制坐标，不是唯一产品布局。
   - 对齐顶部栏、侧边栏、Workflow 复页和 dock/floating panel 规则。
3. 更新索引和接手文档
   - `README.md` 文档索引加入 `Atelier_Main_UI_Spec.md`。
   - `docs/UI_WORKSPACE_SPEC.md` 对齐当前布局与 panel 规则。
   - `docs/RECENT_CHANGES.md` 记录本次文档对齐。
4. 补充图标库事实
   - `atelier/assets/README.md` 去除旧品牌名，并说明该目录是当前软件图标库。
   - `DESIGN.md`、`Atelier_Main_UI_Spec.md`、`UI_WORKSPACE_SPEC.md`、`APP_CODE_MAP.md` 和 `README.md` 对齐图标来源与边界。

## Child Plans

- 暂无。

## Verification

```powershell
git diff --check
```

提交前完整验证：

```powershell
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
git diff --check
```

## Progress / Decisions

- 2026-05-04：创建本计划。决策：暂停后续 Phase，先处理 UI 文档冲突并对齐设计事实源。
- 2026-05-04：按用户裁决更新 `DESIGN.md`，将主视觉主题改为深色优先，浅色保留为未来主题切换；将 `Atelier_Main_UI_Spec.md` 定位为主界面绘制规格。
- 2026-05-04：更新 `Atelier_Main_UI_Spec.md`，统一品牌名为 `Atelier`，并明确固定坐标仅用于概念绘制，不是不可移动产品布局。
- 2026-05-04：更新 `README.md` 和 `UI_WORKSPACE_SPEC.md`，补充 Workflow 复页、可收缩 Sidebar、可嵌入/浮动 panels 和参考源层级。
- 2026-05-04：文档级验证通过：`git diff --check` 仅有 Windows CRLF conversion warnings。
- 2026-05-04：补充 `atelier/assets/` 当前软件图标库事实，并对齐设计事实源、主 UI 绘制规格、workspace spec、code map 和 README。
- 2026-05-04：提交前完整验证通过：59 个 unittest passed，`compileall` passed，`git diff --check` 仅有 Windows CRLF conversion warnings。

## Blockers

- 暂无。
