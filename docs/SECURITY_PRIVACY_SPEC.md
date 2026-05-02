# Atelier Security And Privacy Spec

> 状态：规划中，尚未实现。本文档定义 Atelier 的本地优先安全边界、secrets、插件权限、更新校验、日志脱敏和隐私策略。

## 1. 目标

Atelier 是本地优先 AI 视频工作站。默认不上传用户媒体、项目、日志或模型使用信息。

核心目标：

```text
默认本地处理
用户文件不被静默上传
secrets 不进 SQLite / 日志 / 项目文件
插件权限可见
更新和 runtime 包可校验
外部命令不可注入
```

## 2. 参考资料与取舍

### OWASP

可借鉴：

- Secrets 不应硬编码或写入普通配置。
- 日志中不应记录敏感信息。
- 输入必须验证，命令执行必须避免注入。
- 依赖、插件和更新链需要完整性校验。

Atelier 的取舍：

- 采用 OWASP 的安全原则，但以本地桌面软件落地。
- 所有外部工具走 typed command builder。

### Windows Credential Locker / Credential Manager

可借鉴：

- Windows 提供系统级凭据存储。

Atelier 的取舍：

- Windows 首版 secrets 优先存系统凭据存储。
- Python 可通过 `keyring` 访问系统后端，具体实现需验证。

### VS Code / Browser Extension Permission Model

可借鉴：

- 插件权限必须声明。
- 高风险能力需要用户可见。

Atelier 的取舍：

- Plugin manifest 声明 permissions。
- 默认不授予网络、文件系统、secrets、shell 权限。

### Signed Updaters

可借鉴：

- App/runtime/plugin 更新需要 signature 和 hash 校验。
- 更新下载到 staging，验证后再切换。

Atelier 的取舍：

- Release/update 链必须校验 manifest、package hash 和 signature。

## 3. Trust Boundaries

```text
Trusted Core
  -> Atelier app code
  -> Scheduler
  -> RuntimeManager
  -> ReleaseManager
  -> PluginManager
  -> SecurityManager
  -> Storage

Semi-trusted
  -> signed runtime packs
  -> signed model packs
  -> signed plugin packs

Untrusted / user-provided
  -> media files
  -> subtitle files
  -> imported presets
  -> local plugin packages
  -> user text prompts
  -> remote API responses
```

Rules:

- User media is untrusted input.
- Plugin packages are untrusted until manifest, compatibility, permissions, hash and signature are checked.
- Runtime packages are untrusted until verified.
- Remote API output is untrusted content and must not become executable commands.

## 4. Secrets Policy

Secrets include:

- API keys.
- bearer tokens.
- OAuth refresh tokens.
- provider credentials.
- private update keys.
- plugin repository credentials.

Rules:

- Secrets must not be stored in SQLite plaintext.
- Secrets must not be written to `README.md`, `AGENTS.md`, `DESIGN.md`, docs, project files, presets, logs or task_events.
- Secrets should be stored through OS credential storage.
- SQLite stores only credential references, e.g. `credential_ref`.
- Workers receive secrets only when required and scoped to that task.
- Secrets passed to Worker must not be echoed in events or stderr.

首版建议：

```text
atelier/security/credentials.py
  -> uses keyring on Windows if available
  -> stores credential_ref in SQLite
  -> never returns secrets to GUI widgets unless explicitly needed for edit flow
```

## 5. File System Access

Rules:

- GUI may read files explicitly selected by the user.
- Workers may read input artifact paths passed by Scheduler.
- Workers may write only their task work directory.
- ArtifactFinalizer is responsible for copying/moving final outputs to user-selected output paths.
- No silent overwrite of user files.
- Path traversal must be rejected when unpacking packages, plugins or model assets.

Dangerous paths:

- system directories.
- application install directory.
- credential stores.
- other users' directories.
- project files not selected by user.

## 6. External Tool Execution

Rules:

- No `shell=True`.
- No string-concatenated shell commands.
- Use typed command builders.
- Every argument is a list element.
- User input is validated by type and constraints before becoming an argument.
- External tool paths come from `RuntimeBinding.component_paths`.
- Worker environment is scoped and minimal.

Command execution record should include:

- logical tool name.
- version.
- sanitized argv.
- working directory.
- exit code.
- stderr path.

Do not log:

- API keys.
- full remote authorization headers.
- secrets embedded in URLs.
- user prompt contents when marked private.

## 7. Plugin Security

Rules:

- PluginManager validates manifest before registration.
- PluginManager checks API version and permissions.
- Third-party plugin code must not run in GUI event handlers.
- Backend plugin code runs in Worker process only.
- Plugins cannot access SQLite directly.
- Plugins cannot manage resource_locks directly.
- Plugins cannot read secrets without a scoped credential API.
- Plugins cannot register arbitrary shell commands.
- Panel plugins are disabled until UI plugin API is stable.

Permission examples:

```text
network:remote-api
network:download-model
filesystem:read-user-selected
filesystem:write-artifacts
credential:read-provider
runtime:request
worker:spawn
ui:panel
```

## 8. Update / Runtime / Model Integrity

All packages need:

- manifest.
- sha256.
- signature.
- package type.
- version.
- platform.
- compatibility constraints.

Rules:

- Download to staging.
- Verify before unpacking.
- Reject path traversal in archives.
- Keep previous known-good version for rollback.
- Do not apply app/runtime/plugin updates while affected Workers are running.
- Do not replace model files while they are in use.

## 9. Network Policy

Default:

- No telemetry.
- No crash report upload.
- No media upload.
- No model usage analytics.

Network allowed only for:

- user-triggered model/runtime/plugin download.
- user-configured remote model provider.
- update check if user enables or accepts it.

Network UI must show:

- destination/provider.
- what data is sent.
- whether media/subtitles/prompts are included.
- where credentials are stored.

## 10. Logging And Redaction

Logs are local by default.

Log categories:

```text
app.log
worker stderr
task_events
runtime health logs
update logs
plugin logs
```

Redaction rules:

- redact tokens and API keys.
- redact authorization headers.
- redact signed URLs.
- redact credential_ref secrets.
- optionally redact full user paths in shareable diagnostics.

Shareable diagnostics must be generated explicitly by user action.

## 11. Privacy Modes

Suggested modes:

```text
Local Only
  -> no remote model APIs, no update checks, no downloads unless manually imported

Balanced
  -> update checks and downloads allowed after confirmation

Connected
  -> remote LLM providers allowed when configured
```

Mode changes must not retroactively upload existing data.

## 12. Security Review Triggers

Require explicit review before:

- adding new plugin permission.
- adding remote API provider.
- changing credential storage.
- changing updater signature verification.
- allowing plugin UI code.
- adding archive extraction code.
- adding command builder for external tools.
- adding telemetry or diagnostics export.

## 13. 首版实现建议

第一阶段：

- credential abstraction with no plaintext secrets in SQLite.
- command builder helpers.
- redaction helper.
- package hash verification helper.
- plugin permission manifest fields.
- Local Only default network mode.

暂不实现：

- automatic crash uploads.
- third-party panel plugins.
- remote plugin marketplace.
- telemetry.

## 14. 参考资料

- OWASP Secrets Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- OWASP Logging Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- OWASP OS Command Injection Defense: https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html
- Microsoft Credential Locker: https://learn.microsoft.com/en-us/windows/apps/develop/security/credential-locker
- Python keyring documentation: https://keyring.readthedocs.io/en/latest/
- VS Code extension manifest and permissions model reference: https://code.visualstudio.com/api/references/extension-manifest
