# Split Docs v2 Import And Alignment 计划

## Objective

读取 `C:\Users\Administrator\Downloads\atelier_split_docs_v2`，将其中对 Atelier 规划有用的补充文档移动到 `docs/`，并把首版主要卡片与 OCR Recognition 补齐到现有事实源。

## Scope

- 读取 split docs v2 的 `README.md`、`DOC_ALIGNMENT_NOTES.md` 和各规格文档结构。
- 将 split docs v2 中的规格文档移动到 `docs/`。
- 精确忽略用户暂时不想追踪的新 SVG 文件，不影响已有品牌 SVG 资产。
- 更新 `README.md` 文档索引。
- 更新 `docs/WORKFLOW_NODE_SPEC.md`，统一主要内置卡片 / node_type 清单，并补齐 OCR Recognition。
- 更新 ExecutionPlan、Runtime、Scheduling、UI State、Artifact、Adapter、APP_CODE_MAP 和 RECENT_CHANGES 的对齐记录。

## Current Facts

- split docs v2 包含 Product Flow、MVP Acceptance、Adapter、FFmpeg、ASR、OCR、Video Enhance、Artifact Lifecycle、UI State、Onboarding Runtime Setup 和 Documentation Alignment Notes。
- 包内 README 说明 `OCR_ADAPTER_SPEC.md` 是有意新增，OCR 应作为独立卡片/adapter，而不是 ASR 的一部分。
- 当前用户指定的主要卡片包括 input、media preprocessing、subtitle、video enhance、compose 和 output 类 node_type。
- 当前还需补入 OCR：`ocr.recognition`。
- 当前工作树已有未跟踪 `atelier/assets/brand/001.svg` 和 `atelier/assets/brand/01.svg`；用户要求新加 SVG 暂时不要追踪。

## Constraints

- 本计划只导入和对齐文档，不实现真实 adapters、OCR、FFmpeg、ASR、视频增强、GUI 状态机或 onboarding runtime 安装逻辑。
- 不忽略整个 `atelier/assets/brand/*.svg`，因为品牌 SVG 资产本身需要继续纳入项目；只精确忽略用户新增且暂不追踪的 SVG。
- OCR Recognition 必须保持独立 node / adapter / plugin 边界。
- GUI 不直接执行 adapter；所有重任务仍经 Scheduler / Worker / RuntimeManager。

## Execution Plan

1. 创建本计划并记录当前事实。
2. 将 split docs v2 的规格文档移动到 `docs/`，保留包内 README 只作为导入说明来源。
3. 更新 `.gitignore`，精确忽略 `atelier/assets/brand/001.svg` 和 `atelier/assets/brand/01.svg`。
4. 更新文档索引与主要 node_type 清单，补齐 `ocr.recognition`。
5. 更新相关规格的交叉引用与接手记录。
6. 运行哈希/文档级校验。

## Child Plans

- 暂无。后续真实 adapter / OCR / UI state 实现应另建实现计划。

## Verification

```powershell
Get-FileHash <source-before-move>
Get-FileHash .\docs\<imported-docs>
Select-String -Path .\docs\*.md, .\README.md, .\.gitignore -Pattern '[ \t]+$'
git diff --check
git status --short --branch
```

## Progress / Decisions

- 2026-05-05：创建本计划。决策：导入 v2 规格文档；包内 README 作为导入说明来源，不作为 `docs/README.md` 引入，避免与项目文档索引职责混淆。
- 2026-05-05：决策：精确忽略 `atelier/assets/brand/001.svg` 与 `atelier/assets/brand/01.svg`，不忽略其他品牌 SVG。
- 2026-05-05：已将 11 个 split docs v2 规格/对齐文档移动到 `docs/`；移动前后 SHA-256 一致。源目录保留包内 `README.md` 作为外部说明来源。
- 2026-05-05：已更新 `.gitignore`，`git check-ignore` 确认 `001.svg` 与 `01.svg` 被忽略，`atelier_icon_full.svg` 未被忽略。
- 2026-05-05：已把主要 node_type 目录固化到 `docs/WORKFLOW_NODE_SPEC.md`，并同步到 Product Flow、Batch Scheduling、Hardware Scheduling、Adapter、FFmpeg、Worker Protocol、Runtime、ExecutionPlan、Scheduling Presets、Artifact Lifecycle 和 Translate Agent 相关文档。
- 2026-05-05：验证完成：trailing whitespace scan 无匹配；`git diff --check` 通过，仅有 Windows CRLF conversion warnings；临时 SVG draft ignore 规则按预期生效。

## Blockers

- 暂无。
