# Atelier Release And Update Spec

> 状态：规划中，尚未实现。本文档定义 Atelier 的打包、发布、更新、回滚和发布通道策略。

## 1. 目标

Atelier 的发布系统必须支持本地优先桌面软件、可管理 runtime、模型资产和插件生态。

核心目标：

```text
应用可稳定安装
runtime 可独立升级
模型可独立下载和校验
插件可独立启停
失败可回滚
更新可审计
```

## 2. 参考软件与取舍

### LM Studio

可借鉴：

- App 与 LLM runtime 分离。
- Runtime 可独立下载、更新、选择和删除。
- 模型资产与 runtime 更新链分离。
- 离线时仍能运行已下载模型。

Atelier 的取舍：

- 不采用单一 active runtime；Atelier 需要 per-task runtime binding。
- Runtime 更新不能打断正在执行的 Job。

### Qt Installer Framework

可借鉴：

- 支持离线安装器、在线安装器和组件化更新。
- 适合 Windows 桌面软件的组件安装与维护工具。

Atelier 的取舍：

- 可作为 Windows 首版安装器候选。
- 组件概念适合映射为 App、Runtime Pack、Model Pack 和 Plugin Pack。

### Tauri / Electron / Sparkle

可借鉴：

- 更新 manifest、签名校验、下载 staging、重启后切换版本。
- 失败回滚和 release channel 是成熟桌面软件的基本能力。

Atelier 的取舍：

- 不迁移到 Electron/Tauri。
- 借鉴更新安全模型，不借用前端技术栈。

## 3. 发布物类型

```text
App Package
  -> Atelier GUI / Core / Python / PySide6 / Qt plugins

Runtime Component Package
  -> FFmpeg / ffprobe / llama.cpp / whisper.cpp / ncnn-vulkan / Python worker env

Model Asset Package
  -> ASR / translate / enhance / interpolate model assets

Plugin Package
  -> node plugins / backend plugins / panel plugins / preset plugins

Documentation Package
  -> offline docs, license notices, release notes
```

规则：

- App Package 可以独立更新。
- Runtime Component Package 可以独立更新、禁用、回滚。
- Model Asset Package 可以独立下载、校验、删除。
- Plugin Package 可以独立安装、启停、升级。
- App 不应因为某个 optional runtime 缺失而无法启动。

## 4. Manifest 规范

所有发布物都必须有 manifest。

```toml
schema_version = "1"
package_id = "atelier.runtime.ffmpeg"
package_type = "runtime_component"
name = "FFmpeg Runtime"
version = "7.1.0"
channel = "stable"
platform = "windows-x86_64"
architecture = "x86_64"

[artifact]
url = "https://updates.example.invalid/atelier/runtime/ffmpeg/7.1.0/package.zip"
sha256 = "<sha256>"
size_bytes = 0
signature = "<signature>"

[compatibility]
min_app_version = "0.1.0"
max_app_version = ""
requires_restart = false

[capabilities]
tools = ["ffmpeg", "ffprobe"]
backends = []
hardware = ["cpu"]
```

必需字段：

- `schema_version`
- `package_id`
- `package_type`
- `version`
- `channel`
- `platform`
- `artifact.sha256`
- `artifact.signature`
- `compatibility.min_app_version`

## 5. 更新通道

```text
stable  -> 默认通道，只收稳定发布
beta    -> 提前接收 runtime/backend/model 更新
dev     -> 开发者和内部测试使用
local   -> 用户手动导入的本地包
```

规则：

- 用户可以分别设置 App、Runtime、Model 和 Plugin 的 channel。
- `stable` App 默认只使用 `stable` runtime，除非用户明确切换。
- `local` 包必须同样经过 manifest、hash 和兼容性检查。

## 6. OTA 更新流程

```text
Check
  -> download update index
  -> verify index signature
  -> compare installed manifests
  -> build update plan

Stage
  -> download packages into staging
  -> verify sha256
  -> verify signature
  -> unpack to staging

Apply
  -> wait for safe point
  -> stop affected workers if required and user approved
  -> switch manifest pointer
  -> run migrations if needed
  -> restart app if required

Verify
  -> health check
  -> mark active version
  -> keep previous version for rollback
```

安全点：

- App 更新通常需要重启。
- Runtime 更新不能影响正在运行的 Worker。
- Model 更新不能替换正在被任务读取的模型目录。
- Plugin 更新不能卸载正在被 Job 使用的 node/backend。

## 7. 回滚策略

```text
active/
previous/
staging/
downloads/
manifests/
```

规则：

- App 至少保留上一个可启动版本。
- Runtime 至少保留上一个可用版本。
- Model asset 可以按空间策略保留旧版本。
- Plugin 更新失败时回滚到旧插件 manifest。
- DB migration 必须有版本记录；破坏性 migration 需要明确备份点。

## 8. 版本兼容

兼容性维度：

```text
App schema version
Database schema version
Worker protocol version
Runtime manifest schema version
Plugin API version
Node registry schema version
Model asset schema version
```

不兼容处理：

- 阻止安装。
- 标记为需要 App 升级。
- 标记为需要 runtime 升级。
- 标记为 disabled，并给出修复入口。

## 9. 首版实现建议

首版不要做完整在线更新器，但要先写好结构：

```text
atelier/runtime/manifest.py
atelier/runtime/package.py
atelier/runtime/update_plan.py
atelier/runtime/health.py
atelier/release/channels.py
atelier/release/manifest_verifier.py
```

第一阶段能力：

- 从本地 manifest 读取 App/runtime/model/plugin 状态。
- 校验 hash。
- 显示 runtime health。
- 允许手动导入 local package。
- 不实现自动下载和自动更新。

## 10. 参考资料

- LM Studio runtimes: https://lmstudio.ai/docs/cli/runtime/runtime
- LM Studio 0.3.0 runtime separation: https://lmstudio.ai/blog/lmstudio-v0.3.0
- Qt Installer Framework: https://doc.qt.io/qtinstallerframework/
- Tauri updater: https://v2.tauri.app/plugin/updater/
- Electron autoUpdater: https://www.electronjs.org/docs/latest/api/auto-updater
- Sparkle updates: https://sparkle-project.org/documentation/
