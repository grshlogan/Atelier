# Translate Agent Spec Alignment 计划

## Objective

将新增的 `docs/TRANSLATE_AGENT_SPEC.md` 纳入 Atelier 文档事实体系，并把它暴露出的 `Translate Agent`、`OCR Recognition`、`ocr_text_track` 和字幕翻译 artifact 契约补齐到现有规格文档中。

## Scope

- 更新 `README.md` 文档索引与项目范围。
- 更新 `docs/WORKFLOW_NODE_SPEC.md`，明确 `translate.llm` 与 `ocr.recognition` 的节点/端口边界。
- 更新 `docs/WORKER_PROTOCOL.md`，补充 OCR text track artifact、TranslateAgentAdapter 和 OCR adapter 规划。
- 更新 `docs/DATABASE_SCHEMA.md`，让规划级 artifact type 覆盖 `ocr_text_track` 和翻译 metadata。
- 更新 `docs/Atelier_Main_UI_Spec.md`，让主 UI 中的 Translate Agent 卡片/Inspector 与新 spec 的 ASR/OCR fusion 定位一致。
- 更新 `docs/APP_CODE_MAP.md` 和 `docs/RECENT_CHANGES.md`，记录当前代码边界和接手事实。

## Current Facts

- `docs/TRANSLATE_AGENT_SPEC.md` 已存在，状态为规划中，尚未实现。
- 当前代码没有 `atelier/domain/translation.py`、`atelier/translation/` 或 `atelier/workers/adapters/translate_agent.py`。
- 当前 `atelier/domain/worker_event.py` 的 `artifact_type` 是字符串，代码层没有枚举约束。
- 当前 `atelier/storage/schema.sql` 的实际 artifacts 表没有 artifact type CHECK 约束；规划文档 `docs/DATABASE_SCHEMA.md` 有更严格的 artifact type 列表。
- `docs/WORKFLOW_NODE_SPEC.md` 已有 `translate.llm` 示例，但还没有 `ocr_text_track` data type。

## Constraints

- 本计划只做文档/规格对齐，不实现真实 OCR、真实 provider API、translation domain models、worker adapter、Scheduler optional dependency 或 GUI 运行时逻辑。
- OCR Recognition 应保持独立节点/adapter/plugin 边界；Translate Agent 消费 OCR 输出，但不拥有 OCR 识别职责。
- `Translate Agent` 必须继续服从 `WorkflowGraph -> ExecutionPlan -> Scheduler -> Worker -> Artifact` 架构。
- 不把 OCR-only 结果伪装成完整语音字幕翻译；必须保留 draft / incomplete 表达。

## Execution Plan

1. 建立本对齐计划，记录范围和非实现边界。
2. 将 `docs/TRANSLATE_AGENT_SPEC.md` 加入 `README.md` 文档索引，并在项目范围里标明未来 OCR 字幕/画面文字识别可以由插件或自研 adapter 提供。
3. 更新 workflow / worker / database / UI 规格，补齐 `ocr_text_track`、Translate Agent 输入、artifact metadata 和 UI Inspector 表达。
4. 更新 `APP_CODE_MAP` 与 `RECENT_CHANGES`，说明当前只是规划与文档对齐。
5. 运行文档级校验。

## Child Plans

- 暂无。后续首次代码实现应另建翻译 Agent Phase A-C 的实现计划。

## Verification

```powershell
Select-String -Path .\docs\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

## Progress / Decisions

- 2026-05-05：创建本计划。决策：`TRANSLATE_AGENT_SPEC.md` 是 Translate Agent 卡片、SRT/OCR 翻译、fusion metadata 和 provider 抽象的专项规格；OCR 识别本身保持 `ocr.recognition` 节点/adapter/plugin 边界。
- 2026-05-05：已更新 README、Workflow Node、Worker Protocol、Database Schema、主 UI spec、APP_CODE_MAP 和 RECENT_CHANGES；当前仅为文档/规格对齐，不实现代码。
- 2026-05-05：验证完成：docs/README trailing whitespace scan 无匹配；`git diff --check` 通过，仅有 Windows CRLF conversion warnings。

## Blockers

- 暂无。
