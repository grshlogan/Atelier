# Atelier UI Workspace Spec

> 状态：规划中，尚未实现。本文档定义 Atelier 的主工作区、dockable panels、布局保存、浮动窗口和 workspace preset 规则。

## 1. 目标

Atelier 的主界面不是写死的单页布局，而是一个可保存、可恢复、可折叠、可浮动的创作工作站。

核心原则：

```text
主呈现是四个功能区
布局不硬编码为唯一形态
高频区域默认可见
低频区域可以停靠、隐藏、浮动
用户布局必须可保存和恢复
```

## 2. 参考软件与取舍

### Adobe Premiere Pro

可借鉴：

- Workspace 由 panels 组成。
- Panel 可以 dock、group、float、resize。
- 用户可以保存不同 workspace。

Atelier 的取舍：

- 借鉴 panel/workspace 模型。
- 不复制 Premiere 的复杂菜单层级。

### Qt QMainWindow / QDockWidget

可借鉴：

- `QMainWindow` 天然支持 central widget、dock widgets、toolbars 和 menu bars。
- `saveState()` / `restoreState()` 可以保存 dock 布局。
- `QDockWidget` 支持 floating、tabified dock 和 allowed dock areas。

Atelier 的取舍：

- 首版使用 `QMainWindow + QDockWidget`。
- Workflow Canvas 作为默认 central widget。
- Queue/Inspector/Hardware/Logs/Runtime 作为 dock panels。

### DaVinci Resolve / Blender

可借鉴：

- 工作流模式切换影响面板组合。
- 专业工具允许用户根据任务阶段切换 workspace。

Atelier 的取舍：

- 提供 `Workflow`、`Execution`、`Review`、`Runtime`、`Debug` presets。
- 不在首版做过度复杂的自由 UI 编辑器。

## 3. 主工作区模型

默认四区块：

```text
Workflow Canvas      -> central area
Inspector            -> right dock
Queue Monitor        -> bottom dock
Hardware/Runtime     -> bottom/right dock tab group
```

扩展 panels：

```text
Execution Canvas
Log Viewer
Artifact Browser
Runtime Manager
Plugin Manager
Preset Browser
Debug Events
```

规则：

- 四区块是默认呈现，不是不可变布局。
- 任意 dock panel 可以隐藏、浮动或重新停靠。
- Workflow Canvas 和 Execution Canvas 可切换 central view，也可作为 tabbed central documents。
- 关键状态必须在 panel 被隐藏时仍能通过状态栏、通知或 Queue Monitor 看到。

## 4. Workspace Preset

内置 presets：

```text
Workflow
  -> Workflow Canvas + Inspector + Presets + Queue summary

Execution
  -> Execution Canvas + Hardware + Queue Monitor + Logs

Review
  -> Subtitle/Artifact Review + Inspector + Logs

Runtime
  -> Runtime Manager + Model Store + Hardware + Logs

Debug
  -> Queue Monitor + Worker Events + Logs + Storage Inspector
```

用户可以：

- 保存当前 layout 为 custom workspace。
- 重命名 custom workspace。
- 重置为内置 workspace。
- 导入/导出 workspace layout。

## 5. Layout Persistence

保存内容：

```text
workspace_id
app_version
layout_schema_version
main_window_geometry
qmainwindow_state
panel_visibility
panel_tab_groups
central_view
splitter_sizes
last_active_project
locale
theme
```

存储位置：

- 用户级布局：user settings。
- 项目级推荐布局：project metadata。
- 调试布局：可写入 `docs/plan/` 截图说明，但不进根目录。

规则：

- `QMainWindow.saveState()` 是 Qt dock 状态来源。
- 自定义 panel metadata 需要另存 JSON。
- 布局恢复失败时回退到默认 workspace。
- 新版本删除或重命名 panel 时，旧布局不能导致启动失败。

## 6. Panel Contract

```python
class PanelDescriptor(BaseModel):
    panel_id: str
    title_key: str
    default_area: Literal["left", "right", "top", "bottom"]
    default_visible: bool
    floatable: bool = True
    closable: bool = True
    requires_project: bool = False
```

规则：

- panel title 使用 i18n key。
- panel 不直接持有业务事实源。
- panel 订阅 state store 或 repository 查询结果。
- panel action 只提交 intent，不直接运行任务。

## 7. Floating Windows

允许：

- Inspector 浮动。
- Log Viewer 浮动。
- Queue Monitor 浮动。
- Runtime Manager 浮动。

限制：

- 浮动 panel 关闭不等于销毁业务状态。
- 浮动 panel 不应阻塞主窗口关闭。
- 关键任务状态不能只存在于浮动 panel。

## 8. UI State Flow

```text
User action
  -> Intent
  -> Controller / Application Service
  -> Domain / Scheduler / RuntimeManager / Storage
  -> State update
  -> Panel render
```

反模式：

- Button callback 直接调用 FFmpeg。
- Panel 直接写 SQLite。
- Panel 直接修改 Worker process。
- 多个 panel 分别维护同一事实源。

## 9. 首版实现建议

第一阶段：

- `MainWindow(QMainWindow)`
- `WorkflowCanvas` central placeholder
- `InspectorDock`
- `QueueMonitorDock`
- `HardwareRuntimeDock`
- `LogDock`
- `WorkspaceManager`
- layout save/restore

暂不实现：

- 第三方 panel plugin。
- 多显示器高级恢复。
- 复杂 workspace marketplace。

## 10. 参考资料

- Qt QMainWindow: https://doc.qt.io/qt-6/qmainwindow.html
- Qt QDockWidget: https://doc.qt.io/qt-6/qdockwidget.html
- Adobe Premiere Pro workspaces: https://helpx.adobe.com/premiere-pro/using/workspaces.html
- Qt for Python widgets examples: https://doc.qt.io/qtforpython-6/examples/index.html
