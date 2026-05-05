# Third-Party External Tool Integration Plan

## Objective

Clarify how Atelier should integrate third-party tools such as translation providers, OCR engines, ASR engines, video repair tools, and enhancement tools.

Primary decision:

```text
External tool execution is an independent adapter/runtime contract.
The plugin system is the contribution, packaging, permission, registration, enable/disable, and update layer.
```

This avoids making every local tool look like a plugin while still allowing third-party plugins to contribute tools safely.

## Scope

- Define the relationship between `ExternalToolAdapter`, `WorkerAdapter`, `PluginManager`, `RuntimeManager`, `Scheduler`, and `SecurityManager`.
- Add a dedicated planning spec under `docs/`.
- Align related documentation so LADA-like repair tools, translation providers, OCR tools, ASR tools, and enhancement tools have one architecture path.

Out of scope:

- Implementing real adapters.
- Implementing plugin loading.
- Implementing external tool discovery UI.
- Adding a specific LADA adapter or provider client.

## Current Facts

- `docs/ADAPTER_SPEC.md` already defines `WorkerAdapter`, `AdapterContext`, `AdapterResult`, typed command builders, and the rule that adapters do not schedule, install runtimes, write SQLite, or concatenate shell commands.
- `docs/PLUGIN_SYSTEM_SPEC.md` already defines plugin manifests, contribution points, permissions, and the rule that backend plugin code runs in Worker processes only.
- `docs/RUNTIME_ENVIRONMENT_SPEC.md` already makes RuntimeManager responsible for tool paths, model paths, backend compatibility, and runtime health.
- `docs/SECURITY_PRIVACY_SPEC.md` already requires no `shell=True`, typed command builders, minimal Worker environments, credential references, and plugin permission checks.
- Main planned cards include input, preprocessing, ASR, OCR, translation, subtitle review/normalize, video enhancement, composition, and export nodes.

## Constraints

- GUI must not call third-party tools directly.
- PluginManager must not execute third-party tools directly.
- Scheduler remains the only resource assignment authority.
- RuntimeManager remains the only path/model/backend/runtime resolver.
- Workers execute tools through adapter boundaries and report structured events.
- External tool invocation must not expose arbitrary shell execution.
- Secrets and provider credentials must be referenced through `credential_ref`, not plaintext docs, project files, SQLite rows, or logs.

## Execution Plan

### Phase A - Define The Boundary

Goal:

- Add `EXTERNAL_TOOL_INTEGRATION_SPEC.md`.
- Record the two-layer model:
  - core external tool interface independent of plugins.
  - plugin system as the extension distribution and registration layer.

Completion signal:

- The new spec explains local CLI tools, local SDK/Python tools, remote API providers, managed runtime packs, and plugin-provided backends.

Validation:

- Read the spec and confirm it answers whether LADA-like tools belong to plugins or a separate interface.

### Phase B - Align Existing Specs

Goal:

- Link `README.md`, `ADAPTER_SPEC.md`, `PLUGIN_SYSTEM_SPEC.md`, `RUNTIME_ENVIRONMENT_SPEC.md`, and `SECURITY_PRIVACY_SPEC.md` to the new boundary.

Completion signal:

- Existing specs no longer imply PluginManager is the execution interface.
- Existing specs no longer imply every external tool must be packaged as a plugin.

Validation:

- Run a trailing whitespace scan and `git diff --check`.

## Child Plans

- None for this documentation-only change.

## Verification

Run:

```powershell
Select-String -Path .\docs\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## Progress / Decisions

- 2026-05-05: Decided on the hybrid model: independent external tool adapter contract plus plugin system contribution layer.
- 2026-05-05: Added `docs/EXTERNAL_TOOL_INTEGRATION_SPEC.md` and aligned README, Adapter, Plugin, Runtime, Security, and Recent Changes docs.

## Blockers

- None.
