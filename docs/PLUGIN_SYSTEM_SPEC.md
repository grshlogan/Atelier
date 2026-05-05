# Atelier Plugin System Spec

> 状态：规划中，尚未实现。本文档定义 Atelier 的插件类型、manifest、权限、runtime 约束、加载边界和首版开放范围。

## 1. 目标

Atelier 的插件系统必须扩展 workflow、runtime、UI 和 presets，同时不破坏安全边界。

```text
插件可以扩展能力
插件不能绕过 Scheduler
插件不能直接控制硬件
插件不能让 GUI 执行重任务
插件必须可禁用、可回滚、可诊断
```

### 1.1 与第三方工具接入的关系

插件系统不是第三方工具的执行接口。它负责安装、声明、权限、注册、启停、更新和缺失状态；工具执行接口由 `ExternalToolAdapter` / `WorkerAdapter`、RuntimeManager、Scheduler 和 Worker 共同承担。

因此 LADA-like 修复工具、翻译 provider、OCR backend、ASR backend、视频增强 backend 可以由插件贡献，但不能由 PluginManager 直接运行。详细边界见 `EXTERNAL_TOOL_INTEGRATION_SPEC.md`。

## 2. 参考软件与取舍

### VS Code Extensions

可借鉴：

- `package.json` manifest 声明 extension metadata、activation、contributions。
- 插件通过 contribution points 扩展 UI 和能力，而不是任意改主程序。
- API version 和 engine version 约束清楚。

Atelier 的取舍：

- 使用 manifest-driven contribution。
- 不直接开放无限制 Python import。

### Blender Extensions / Add-ons

可借鉴：

- 扩展自包含。
- manifest 描述类型、版本、权限和维护者信息。
- 可从本地 zip 或 repository 安装。

Atelier 的取舍：

- 插件包必须自包含。
- 插件声明的 runtime requirements 必须进入 RuntimeManager。

### napari npe2

可借鉴：

- manifest 声明 commands、readers、writers、widgets 等 contribution。
- 插件发现和功能声明可以与实际加载分离。

Atelier 的取舍：

- 首版只读取 manifest 并注册 node/preset/backend 声明。
- 真正执行时再加载对应 Worker adapter。

## 3. 插件类型

```text
node_plugin
  -> 新增 Workflow Node / NodeRegistryEntry / 参数 schema

backend_plugin
  -> 新增 runtime backend / Worker adapter / command builder

preset_plugin
  -> 新增 workflow preset / node preset / hardware policy preset

panel_plugin
  -> 新增 dockable UI panel，首版暂不开放第三方

theme_plugin
  -> 新增主题或图标资源，首版暂不开放第三方
```

首版开放：

- 内置 `node_plugin`
- 内置 `backend_plugin`
- 内置 `preset_plugin`

第三方开放顺序：

1. preset_plugin
2. node_plugin with built-in adapters only
3. backend_plugin in worker process
4. panel_plugin after API stabilization

## 4. Plugin Manifest

```toml
schema_version = "1"
plugin_id = "atelier.plugin.whisper"
name = "Whisper Nodes"
version = "0.1.0"
publisher = "Atelier"
description = "ASR workflow nodes and worker adapter bindings."
api_version = "0.1"
enabled_by_default = true

[compatibility]
min_app_version = "0.1.0"
max_app_version = ""
worker_protocol = "1"
node_schema = "1"

[[contributes.nodes]]
node_type = "asr.whisper"
entry = "nodes/asr.whisper.json"

[[contributes.backends]]
backend_id = "faster-whisper"
runtime_requirements = ["faster-whisper"]
adapter_entry = "atelier_whisper.adapters:FasterWhisperAdapter"

[[permissions]]
name = "runtime:read"

[[permissions]]
name = "worker:spawn"
```

必需字段：

- `schema_version`
- `plugin_id`
- `version`
- `api_version`
- `compatibility.min_app_version`
- `contributes`

## 5. Contribution Points

### nodes

新增 WorkflowNode 类型。

必须声明：

- `node_type`
- input/output ports
- params
- failure policy
- cache policy
- runtime requirements

### backends

新增 Worker backend 或 adapter。

必须声明：

- backend id
- supported node types
- runtime requirements
- worker adapter entry
- command builder constraints

### external_tools

新增第三方工具声明。它描述工具形态和允许绑定的 node/backend，而不是直接声明可执行 shell 命令。

必须声明：

- tool id
- tool kind: `local_cli`、`local_sdk`、`remote_api`、`managed_runtime` 或 `plugin_backend`
- supported node types
- runtime requirements 或 provider profile requirements
- adapter entry
- required permissions

### presets

新增 preset。

必须声明：

- preset id
- graph_json
- required node types
- required plugin ids

### panels

新增 UI panel。

首版不开放第三方。未来必须：

- 只能通过稳定 UI API 读取 state。
- 不能直接写数据库。
- 不能直接启动 Worker。
- 可以注册 dock panel 和 actions。

## 6. 权限模型

权限示例：

```text
runtime:read
runtime:request
worker:spawn
storage:read
storage:write-own
network:download-model
network:remote-api
filesystem:read-user-selected
filesystem:write-artifacts
ui:panel
```

规则：

- 默认无权限。
- 插件必须声明权限。
- 高风险权限需要用户确认。
- 插件不能获得任意 shell 权限。
- 插件不能读取 secrets，除非通过受控 credential API。

## 7. 加载生命周期

```text
Discover
  -> scan plugin directories
  -> read manifest only
  -> validate schema

Register
  -> register nodes / presets / backend declarations
  -> do not import heavy code

Resolve
  -> RuntimeManager resolves requirements
  -> Scheduler confirms availability

Execute
  -> Worker process imports adapter
  -> reports structured events

Disable
  -> mark plugin disabled
  -> keep old job records readable
```

## 8. 隔离边界

强制规则：

- GUI 插件不能执行重型任务。
- backend plugin 代码只在 Worker process 中运行。
- 插件不直接访问 SQLite。
- 插件不直接管理 resource_locks。
- 插件不直接修改 RuntimeManifest。
- 插件不能覆盖已有 node_type，除非显式声明 replacement 并通过用户确认。

## 9. 兼容性和迁移

需要版本化：

```text
Plugin API
Node schema
Worker protocol
Runtime manifest schema
Database schema
```

旧 Job 可读性：

- 即使插件被卸载，历史 Job 仍应显示 node_type、参数快照、事件和 artifacts。
- 如果插件缺失，WorkflowGraph 显示为 `missing_plugin` 状态，而不是崩溃。

## 10. 首版实现建议

第一阶段：

- 定义 manifest schema。
- 支持内置插件目录。
- 注册内置 node/preset/backend。
- 不开放第三方 Python 插件安装。
- 为未来第三方插件保留 disabled/missing 状态。

建议目录：

```text
atelier/plugins/
  manager.py
  manifest.py
  registry.py
  permissions.py
  builtin/
```

用户数据目录：

```text
AtelierData/plugins/installed/
AtelierData/plugins/disabled/
AtelierData/plugins/staging/
```

## 11. 参考资料

- VS Code Extension Manifest: https://code.visualstudio.com/api/references/extension-manifest
- VS Code Contribution Points: https://code.visualstudio.com/api/references/contribution-points
- Blender Extensions: https://docs.blender.org/manual/en/latest/advanced/extensions/
- napari npe2 manifest: https://npe2.readthedocs.io/en/latest/manifest.html
- OBS plugin documentation: https://docs.obsproject.com/plugins
