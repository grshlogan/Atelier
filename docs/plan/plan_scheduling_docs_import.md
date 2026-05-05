# Scheduling Docs Import 计划

## Objective

把 `C:\Users\Administrator\Downloads\atelier_scheduling_docs` 中新增的三份 scheduling 规划文档提取到项目 `docs/`，并更新项目文档索引和接手记录。

## Scope

- 读取外部 `README.md` 和三份 scheduling 文档。
- 将三份文档复制到 `docs/`：
  - `BATCH_PIPELINE_SCHEDULING_SPEC.md`
  - `HARDWARE_SCHEDULING_PAGE_SPEC.md`
  - `SCHEDULING_PRESETS_SPEC.md`
- 更新 `README.md` 文档索引。
- 更新 `docs/RECENT_CHANGES.md`。

## Current Facts

- 外部 README 明确说明三份文档 intended to be copied into `./docs/`。
- 三份文档均声明状态为规划中，尚未实现。
- 文档核心方向与当前 Atelier 模型一致：`WorkflowGraph -> ExecutionPlan -> Scheduler -> Worker -> SQLite`。
- 当前 `docs/` 尚无同名文件。

## Constraints

- 本计划只导入文档，不实现调度策略、页面 UI、preset 模型或 Scheduler 行为。
- 不把新增 scheduling 文档写成已完成产品功能。
- 保持 `Scheduler` 是资源绑定事实源，`RuntimeManager` 是 runtime/model path 解析事实源。

## Execution Plan

1. 复制三份 scheduling spec 到 `docs/`。
2. 更新 `README.md`，把三份文档加入文档索引。
3. 更新 `docs/RECENT_CHANGES.md`，记录导入来源、边界和验证。
4. 运行文档级验证。

## Child Plans

- 暂无。

## Verification

```powershell
Get-FileHash C:\Users\Administrator\Downloads\atelier_scheduling_docs\*.md
Get-FileHash .\docs\BATCH_PIPELINE_SCHEDULING_SPEC.md
Get-FileHash .\docs\HARDWARE_SCHEDULING_PAGE_SPEC.md
Get-FileHash .\docs\SCHEDULING_PRESETS_SPEC.md
git diff --check
```

## Progress / Decisions

- 2026-05-04：创建本计划。已读取外部 README 和三份正文，决策：按 README 意图原样引入三份 spec，再补 README 索引与 RECENT_CHANGES。
- 2026-05-04：已复制三份 spec 到 `docs/`，并更新 `README.md` 文档索引与 `docs/RECENT_CHANGES.md`。
- 2026-05-04：验证完成：三份导入文档 SHA256 与外部源文件一致；导入文档和本计划无 trailing whitespace；`git diff --check` 对 tracked modifications 通过，仅有 Windows CRLF conversion warnings。

## Blockers

- 暂无。
