# DESIGN.md Dark Reference Plan

## Objective

为 Atelier 的深色工作台补充一个来自 DESIGN.md 官网/库的外部参考文档，放入 `docs/design-md-references/`，仅作为设计方法参考，不作为 Atelier 的事实源。

## Scope

- 选择一个更贴近 Atelier 深色、AI 工具、复杂工作台方向的 DESIGN.md 参考。
- 下载原始 Markdown 到 `docs/design-md-references/`。
- 更新 `DESIGN.md` 的参考清单，说明它的参考边界。

## Current Facts

- Atelier 默认视觉方向是深色创作者工作站。
- 现有参考包括 Apple、Linear、NVIDIA、Ollama、RunwayML。
- `getdesign.md` 的 Cursor 页面指向 `Dark Tech Sharp` 风格。
- `Dark Tech Sharp` 的 use case 包含 developer tools、SaaS dashboards、productivity apps、AI products。

## Constraints

- 外部参考不能覆盖根目录 `DESIGN.md`。
- 不复制外部品牌颜色、字体、官网结构或营销布局。
- 只把可转译的方法沉淀为参考，例如深色层级、边框式 elevation、排版纪律和密集工具界面克制。

## Execution Plan

1. 下载 `Dark Tech Sharp` Markdown 到 `docs/design-md-references/dark-tech-sharp.DESIGN.md`。
2. 更新 `DESIGN.md` 的参考文件列表。
3. 运行文档空白扫描与 `git diff --check`。

## Verification

- 已确认 `docs/design-md-references/dark-tech-sharp.DESIGN.md` 存在，内容来自官网 Markdown 源 `https://designmd.info/dark-tech-sharp.md`。
- 已更新 `DESIGN.md` 的参考清单，仅新增参考说明和禁止照搬约束，不改变 Atelier 自身设计事实。
- 文档空白扫描通过：无尾随空白。
- `git diff --check` 通过，仅有既有 Windows CRLF conversion warnings。

## Progress / Decisions

- 选择 `Dark Tech Sharp`，因为它比单纯媒体/营销风格更接近 Atelier 的深色 AI 工作台和复杂工具界面。
- 文件命名为 `dark-tech-sharp.DESIGN.md`，不命名为 `cursor.DESIGN.md`，避免把通用风格文档误表达成 Cursor 官方品牌系统。

## Blockers

- 无。
