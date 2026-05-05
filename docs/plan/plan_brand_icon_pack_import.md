# Brand Icon Pack Import 计划

## Objective

把 `C:\Users\Administrator\Downloads\atelier_icon_pack` 中的软件品牌图标导入 Atelier 项目资产目录，并与现有 UI 功能图标库区分。

## Scope

- 读取外部 icon pack README 和 SVG 内容。
- 将品牌/软件图标导入 `atelier/assets/brand/`。
- 更新 `atelier/assets/README.md`、`icon_manifest.json`、`README.md`、`DESIGN.md`、`docs/Atelier_Main_UI_Spec.md`、`docs/APP_CODE_MAP.md` 和 `docs/RECENT_CHANGES.md`。
- 验证导入文件哈希与外部源文件一致。
- 根据用户补充的 PNG 参考渲染，重绘品牌 SVG，使其更接近 PNG 的轮廓、流程线和节点块。

## Current Facts

- `C:\Users\Administrator\Downloads\atelier_icon_pack` 包含 full app icon、standard/compact/mono logo、tray dark/light 和 preview。
- 现有 `atelier/assets/` 已包含 toolbar、navigation、nodes、queue、hardware、status、inspector 和 system 功能线性图标。
- 品牌图标与功能线性图标用途不同，不能混在 toolbar 或 system 目录。
- `atelier/assets/brand/01.png` 到 `04.png` 是用户补充的品牌视觉参考渲染；SVG 呈现应与这些 PNG 更一致。

## Constraints

- 本计划只导入品牌图标资产，不实现 Qt `.qrc`、IconManager、PNG/ICO/ICNS 导出或打包集成。
- 不覆盖现有 UI 功能图标。
- 产品品牌名仍唯一为 `Atelier`。
- SVG 必须保持纯矢量：不嵌入 PNG、base64 raster、外部字体或脚本。

## Execution Plan

1. 新建 `atelier/assets/brand/`，复制 icon pack 文件。
2. 更新 `icon_manifest.json`，加入 brand 分类条目。
3. 更新资产和设计文档，说明 brand icon 与 UI icon 的边界。
4. 运行哈希和文档级验证。
5. 以 `01.png` 到 `04.png` 为参考重绘品牌 SVG，并记录 PNG 是参考渲染而非运行时首选资产。

## Child Plans

- 暂无。

## Verification

```powershell
Get-FileHash C:\Users\Administrator\Downloads\atelier_icon_pack\*.svg
Get-FileHash .\atelier\assets\brand\*.svg
Get-ChildItem .\atelier\assets\brand -Filter *.svg | ForEach-Object { [xml](Get-Content -Raw -Encoding UTF8 $_.FullName) | Out-Null }
Select-String -Path .\atelier\assets\brand\*.svg -Pattern '<image|<script|font-face|base64'
Get-Content -Raw -Encoding UTF8 .\atelier\assets\icon_manifest.json | ConvertFrom-Json
git diff --check
```

## Progress / Decisions

- 2026-05-04：创建本计划。决策：把软件品牌图标放入 `atelier/assets/brand/`，而不是覆盖现有功能图标目录。
- 2026-05-04：已导入 6 个 SVG 品牌图标、`preview.html` 和 `README.md` 到 `atelier/assets/brand/`。
- 2026-05-04：已更新 `icon_manifest.json`，新增 6 个 `brand` category entries；manifest 校验为合法 JSON，共 86 entries。
- 2026-05-04：已更新资产、设计、UI spec、README、code map 和 recent changes，明确品牌图标与功能线性图标的用途边界。
- 2026-05-04：验证完成：品牌 SVG / README / preview 哈希与外部源文件一致；trailing whitespace scan 无匹配；`git diff --check` 仅有 Windows CRLF conversion warnings。
- 2026-05-04：用户补充 `01.png` 到 `04.png` 作为更高质量品牌视觉参考；决策：保留 PNG 为 reference renders，运行时仍优先使用 SVG。
- 2026-05-04：已重绘 6 个品牌 SVG，使 full / standard / compact / mono / tray variants 更接近 PNG 中的大圆角 A、流程线、节点块和发光质感。此步骤使 SVG 不再要求与外部导入源 SVG 哈希一致。
- 2026-05-04：已更新 `icon_manifest.json`，为 `01.png` 到 `04.png` 增加 `brand_reference` entries，避免把参考渲染误归入运行时 SVG 图标。
- 2026-05-04：已更新 `atelier/assets/brand/preview.html`，可同时预览 SVG 和 PNG reference renders。

## Blockers

- 暂无。
