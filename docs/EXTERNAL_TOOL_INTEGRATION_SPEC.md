# Atelier External Tool Integration Spec

> 状态：规划中，尚未实现。本文档定义第三方工具、多后端工具和远程 provider 如何进入 Atelier。它补充 `ADAPTER_SPEC.md`、`PLUGIN_SYSTEM_SPEC.md`、`RUNTIME_ENVIRONMENT_SPEC.md` 和 `SECURITY_PRIVACY_SPEC.md`，不替代这些文档。

## 1. 结论

第三方工具接入不要在“插件系统”和“独立接口”之间二选一。Atelier 应采用两层模型：

```text
ExternalToolAdapter / WorkerAdapter
  -> 核心执行接口，独立于插件系统

PluginManager
  -> contribution / package / permission / registration / enable-disable / update layer
```

换句话说：

- 内置工具可以直接注册 adapter。
- 用户手动配置的本地工具可以通过 external tool profile 进入 RuntimeManager。
- 第三方插件可以声明 node、backend、runtime requirement 和 adapter entry。
- 真正执行时都必须进入 Scheduler -> Worker -> Adapter -> Artifact / WorkerEvent 边界。

PluginManager 不负责直接调用 LADA、DeepL、PaddleOCR、RealESRGAN、RIFE、Whisper 或 FFmpeg。PluginManager 只负责验证和注册这些能力的声明。

## 2. 为什么不是纯插件系统

如果把所有第三方工具都做成插件，会出现几个问题：

- 内置 adapter 也要伪装成插件，增加首版复杂度。
- 用户本地已有的 CLI 工具或 SDK 环境无法轻量接入。
- PluginManager 容易承担执行细节，破坏 Scheduler / RuntimeManager / Worker 分层。
- 翻译 API、OCR SDK、视频修复 CLI、模型 backend 的生命周期差异太大，不适合用一个插件执行模型覆盖。

因此插件系统应该是扩展入口，不是执行接口本身。

## 3. 为什么不是纯独立接口

只做独立 external tool interface 也不够，因为 Atelier 未来需要第三方生态：

- 插件需要 manifest、版本、兼容性、签名、权限和启停状态。
- 插件需要贡献 node schema、workflow preset、backend binding 和 runtime requirements。
- 插件缺失时，历史 Job 仍要显示 `missing_plugin` / `missing_backend` 状态。
- 用户需要可见地安装、禁用、更新或回滚第三方能力。

因此第三方生态必须走 PluginManager 管理，但执行仍落在 adapter/runtime/worker 边界。

## 4. 分层模型

```text
Workflow Node / NodeRegistry
  -> declares node_type, ports, params, runtime requirements

ExecutionPlanner
  -> converts WorkflowGraph into ExecutionTask DAG

Scheduler
  -> assigns ResourceBinding, device, concurrency, priority, and waiting reason

RuntimeManager
  -> resolves RuntimeBinding, model paths, executable paths, SDK env, provider profile

Worker
  -> loads WorkerAdapter or plugin-provided adapter in isolated process

ExternalToolAdapter
  -> invokes local CLI, local SDK, managed backend, or remote API through typed boundaries

Artifact Store / WorkerEvent Stream
  -> records outputs, metadata, logs, warnings, cache, and recovery state
```

## 5. 工具类型

Atelier 应把第三方工具按执行形态分类，而不是按插件来源分类。

```text
local_cli
  -> local executable resolved by RuntimeManager
  -> examples: FFmpeg, LADA-like repair tool, RealESRGAN ncnn, RIFE ncnn, Tesseract

local_sdk
  -> Python package, native library, or SDK inside a managed Worker env
  -> examples: PaddleOCR, faster-whisper, local LLM provider client

remote_api
  -> network provider through scoped credentials and provider policy
  -> examples: DeepL-like translation, OpenAI-compatible LLM, OCR cloud API

managed_runtime
  -> tool/backend/model packaged as Atelier runtime component
  -> examples: llama.cpp pack, whisper.cpp pack, ncnn-vulkan pack

plugin_backend
  -> adapter/backend contributed by a plugin manifest, executed only inside Worker
  -> examples: third-party video repair adapter, custom OCR backend, custom subtitle QA provider
```

## 6. Suggested Data Contracts

Planning sketch only:

```python
class ExternalToolKind(str, Enum):
    LOCAL_CLI = "local_cli"
    LOCAL_SDK = "local_sdk"
    REMOTE_API = "remote_api"
    MANAGED_RUNTIME = "managed_runtime"
    PLUGIN_BACKEND = "plugin_backend"

class ExternalToolBinding(BaseModel):
    tool_id: str
    kind: ExternalToolKind
    runtime_binding: RuntimeBinding | None = None
    credential_ref: str | None = None
    provider_profile_id: str | None = None
    permissions: list[str] = []
    rate_limit_key: str | None = None

class ExternalToolAdapter(WorkerAdapter):
    tool_id: str
    supported_tool_kinds: list[ExternalToolKind]

    def validate_tool(self, context: AdapterContext, binding: ExternalToolBinding) -> list[AdapterValidationError]: ...
```

Rules:

```text
ExternalToolBinding is resolved before Worker execution.
ExternalToolAdapter does not discover global tools on PATH.
ExternalToolAdapter does not install runtimes or models.
ExternalToolAdapter does not own provider secrets.
ExternalToolAdapter does not bypass ResourceBinding or rate limits.
```

## 7. Registration Modes

### Built-in Adapter

Used for first-party nodes and core tools:

```text
asr.whisper
ocr.recognition
translate.llm
enhance.realesrgan
enhance.rife
compose.mux_subtitle
```

These can be registered by Atelier itself without packaging them as third-party plugins.

### User External Tool Profile

Used when the user points Atelier at an existing local tool install:

```text
tool_id = "lada.local"
kind = "local_cli"
component = "lada"
executable_ref = "RuntimeManager-managed path"
allowed_node_types = ["enhance.video_restore"]
```

The UI may allow this in Settings / Runtime Setup, but the stored profile should still resolve through RuntimeManager and SecurityManager.

### Plugin-Provided Backend

Used when a plugin contributes a backend or adapter:

```toml
[[contributes.external_tools]]
tool_id = "thirdparty.lada"
kind = "local_cli"
display_name = "LADA Video Repair"
supported_node_types = ["enhance.video_restore"]
runtime_requirements = ["lada"]
adapter_entry = "atelier_lada.adapters:LadaRepairAdapter"

[[permissions]]
name = "runtime:request"

[[permissions]]
name = "filesystem:read-user-selected"

[[permissions]]
name = "filesystem:write-artifacts"
```

PluginManager validates this declaration. RuntimeManager resolves the runtime. Scheduler assigns resources. Worker imports the adapter at execution time.

### Remote Provider Profile

Used for translation, OCR, LLM review, or cloud enhancement providers:

```text
provider_profile_id = "deepl.default"
kind = "remote_api"
credential_ref = "credential:provider/deepl/default"
rate_limit_key = "deepl.default"
allowed_node_types = ["translate.llm"]
```

Secrets stay behind SecurityManager / OS credential storage. Logs and events carry only redacted provider metadata.

## 8. LADA-Like Tool Placement

A LADA-like video repair tool should be modeled as:

```text
Workflow node:
  enhance.video_restore or a more specific repair node type

Runtime:
  local_cli or managed_runtime component resolved by RuntimeManager

Adapter:
  ExternalToolAdapter / WorkerAdapter responsible for typed args, staged outputs, progress parsing, and error mapping

Plugin:
  optional packaging and registration path if the tool is third-party distributed
```

It should not be called by GUI, Project page, PluginManager, or arbitrary shell configuration.

## 9. Security Boundary

Rules:

- No `shell=True`.
- No arbitrary shell command fields in UI, workflow nodes, hardware policy, plugin manifest, or provider profile.
- Every command uses `CommandSpec`.
- Every path comes from `RuntimeBinding`, selected input artifacts, or task work directories.
- Remote providers use `credential_ref`, never plaintext keys in project files or SQLite.
- Plugin-provided adapters run only in Worker processes.
- External tool stdout/stderr must be parsed and redacted before becoming user-visible logs.
- Network providers require explicit provider profile and permission checks.

## 10. UI Placement

External tools should surface in UI through existing product concepts:

```text
Workflow Canvas
  -> user chooses a card/node and backend preference

Execution Canvas / Hardware Scheduling page
  -> user sees resource binding, device, waiting reason, fallback, estimated pressure

Queue Monitor
  -> user sees stage progress, logs, artifacts, failed step, and recovery actions

Settings / Runtime Setup
  -> user installs/imports runtime components, configures provider profiles, validates local tools

Plugin Manager
  -> user installs/enables/disables plugin-contributed nodes/backends/presets
```

Do not create one-off UI pages per external tool unless the tool needs a dedicated settings panel.

## 11. First Implementation Order

Recommended order:

1. Define `ExternalToolKind` and `ExternalToolBinding` models near runtime/adapter contracts.
2. Add an `AdapterRegistry` that maps `node_type + backend_id` to a `WorkerAdapter`.
3. Add RuntimeManager support for external tool profiles and health checks.
4. Keep built-in adapters first; do not open arbitrary third-party Python plugin execution in the first version.
5. Extend Plugin Manifest with `contributes.external_tools` after manifest validation and permission checks exist.
6. Add Settings / Runtime Setup validation UI for local tools and remote provider profiles.
7. Add plugin-provided backend execution only after Worker isolation and log redaction are tested.

## 12. Related Specs

- `ADAPTER_SPEC.md`: adapter lifecycle, typed command builder, error mapping.
- `PLUGIN_SYSTEM_SPEC.md`: plugin manifest, contribution points, permission model, lifecycle.
- `RUNTIME_ENVIRONMENT_SPEC.md`: runtime components, model store, `RuntimeBinding`, health checks.
- `SECURITY_PRIVACY_SPEC.md`: secrets, external command execution, plugin security, network policy.
- `WORKFLOW_NODE_SPEC.md`: node schema, ports, runtime requirements.
- `EXECUTION_PLAN_SPEC.md`: task generation, resource binding, runtime binding.
- `WORKER_PROTOCOL.md`: JSON Lines event protocol, artifacts, cancellation, failure states.
