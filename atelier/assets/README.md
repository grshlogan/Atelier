# Atelier Icon Pack

这是为 `Atelier` 准备的 SVG 图标资源目录，包含软件品牌图标和主界面功能线性图标。

当前分层：

- `brand/`：软件品牌图标 / app icon / logo / tray icon。
- 其他分类目录：主界面 toolbar、navigation、nodes、queue、hardware、status、inspector、system 等功能图标。

## 设计风格

- 24 × 24 viewBox
- `stroke="currentColor"`
- `fill="none"`
- `stroke-width="1.8"`
- 圆角线帽和圆角连接
- 适合 PySide6 / QtSvg / QIcon / QSvgRenderer
- 适合 Atelier 深色优先的专业工作站 UI

图标颜色应由 Qt palette / style 或 SVG `currentColor` 继承，不在单个图标文件里写死主题色。

注意：`brand/` 中的 full / standard / compact 图标允许使用渐变和品牌发光效果；`brand/atelier_logo_mono.svg` 与 tray variants 用于单色、托盘、高对比或主题化场景。`brand/01.png` 到 `brand/04.png` 是当前品牌 SVG 的视觉参考渲染，运行时 UI 默认仍优先使用 SVG。

## 目录

```text
icon_manifest.json       图标清单
atelier_icons_sprite.svg 预览/整合用 sprite
preview.html             图标预览页
brand/       软件品牌图标、logo、tray icon
navigation/   左侧导航
toolbar/      顶栏与画布工具
nodes/        Workflow Canvas 节点卡片
queue/        Queue Monitor
hardware/     GPU/CPU/RAM/资源锁
status/       状态图标
inspector/    右侧参数面板
system/       数据库、runtime、plugin、security 等系统模块
```

## 使用建议

### Qt / PySide6

可以直接作为 `QIcon` 使用：

```python
from PySide6.QtGui import QIcon

button.setIcon(QIcon("atelier/assets/toolbar/run_workflow.svg"))
```

实际产品代码应通过统一的 asset path / resource loader 获取图标路径；不要在多个 widget 中散落硬编码路径。

品牌图标示例：

```python
window.setWindowIcon(QIcon("atelier/assets/brand/atelier_icon_full.svg"))
```

小尺寸 UI 或托盘图标不要直接缩放 `atelier_icon_full.svg`，优先使用 `atelier_logo_compact.svg`、`atelier_tray_dark.svg` 或 `atelier_tray_light.svg`。

### 颜色建议

```text
默认图标:      #B7C2D2
Active 图标:   #93C5FD
Success:       #39C86A
Warning:       #F6C85F
Error:         #F87171
Node Accent:   #60A5FA / #A78BFA / #38BDF8
```

## 注意

- 这些图标是原创通用线性图标，不包含第三方品牌 logo。
- 不含字体文件。
- 当前目录是 UI 图标资源库，不代表已经实现 Qt `.qrc` 注册、运行时主题重染色、图标缓存或 IconManager。
- `brand/` 是品牌资源事实；其中 `01.png` 到 `04.png` 是参考渲染，不代表已经生成 Windows `.ico`、macOS `.icns` 或完整多尺寸 PNG export set。
- 后续 UI 实现应优先复用本目录图标，再根据真实控件状态继续打磨细节。
