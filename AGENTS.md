# Atelier AGENTS.md

This file is the project-level operating guide for AI coding agents working inside the Atelier repository.

Atelier is a local-first AI video workflow workstation. It is not a simple subtitle GUI, not a single-purpose video enhancer, and not a ComfyUI clone.

Core product model:

```text
Workflow Canvas   -> defines what should happen to the media
Execution Canvas  -> defines how the workflow runs on local hardware
Queue Monitor     -> tracks execution, recovery, artifacts, logs, and outputs
```

Product standard:

```text
Make the workflow visible.
Make hardware execution controllable.
Make failures recoverable.
```

## 1. Language

- Use Simplified Chinese when talking to the user unless they request another language.
- Keep code identifiers, commands, paths, APIs, schema names, file names, model names, and logs in their original language.
- Lead with conclusions, then give actionable details.
- Do not invent files, commands, config fields, APIs, or completed features.
- If unsure, inspect local files first.

## 2. Source Of Truth

Read and maintain sources in this order:

1. `AGENTS.md`: engineering boundaries, agent workflow, and project rules.
2. Current code and executable validation results.
3. `README.md`: Chinese project overview, current stage, and document index.
4. `DESIGN.md`: visual, interaction, layout, density, and motion guidance.
5. Architecture docs such as `ARCHITECTURE.md`, `RELEASE_UPDATE_SPEC.md`, `RUNTIME_ENVIRONMENT_SPEC.md`, `PLUGIN_SYSTEM_SPEC.md`, `UI_WORKSPACE_SPEC.md`, `I18N_SPEC.md`, `HARDWARE_SCHEDULING_SPEC.md`, `FAILURE_RECOVERY_SPEC.md`, `SECURITY_PRIVACY_SPEC.md`, `WORKFLOW_NODE_SPEC.md`, `EXECUTION_PLAN_SPEC.md`, `WORKER_PROTOCOL.md`, and `DATABASE_SCHEMA.md`.

If documentation conflicts with code and verification, trust the code and update the docs.

## 3. DESIGN.md Relationship

Atelier follows the `DESIGN.md` separation used by `VoltAgent/awesome-design-md`:

```text
AGENTS.md  -> how agents should build and maintain the project
DESIGN.md  -> how the product should look and feel
```

Use root `DESIGN.md` as the design source of truth. Use `docs/design-md-references/` only as inspiration.

Current local references:

```text
docs/design-md-references/apple.DESIGN.md
docs/design-md-references/linear.DESIGN.md
docs/design-md-references/nvidia.DESIGN.md
docs/design-md-references/ollama.DESIGN.md
docs/design-md-references/runwayml.DESIGN.md
```

Rules:

- Do not treat any reference file as Atelier's design source of truth.
- Translate useful ideas back into Atelier's own visual language.
- Do not copy external brand colors, typography, hero layouts, or marketing structures directly.
- Read only the reference file relevant to the current design task.

## 4. Architecture Boundaries

Design the project around these models:

```text
Project
  -> Job
      -> WorkflowGraph
      -> ExecutionPlan
      -> Task DAG
      -> Artifact
      -> Worker Events
```

Preserve these responsibilities:

- `GUI`: submits user intent and renders state.
- `WorkflowGraph`: describes the processing flow.
- `ExecutionPlan`: describes execution phases, lanes, and hardware bindings.
- `Scheduler`: decides when tasks run and which resources they use.
- `HardwareDetector`: captures CPU, RAM, disk, GPU, driver, runtime capability, and process health snapshots.
- `RuntimeManager`: owns application runtime, external tool runtimes, backend manifests, model assets, and runtime health checks.
- `ReleaseManager`: owns release channels, update manifests, staging, verification, and rollback plans.
- `PluginManager`: discovers plugin manifests, validates permissions, registers contributions, and keeps plugin code out of GUI-critical paths.
- `WorkspaceManager`: owns dock layout, floating panels, workspace presets, and layout persistence.
- `I18nManager`: owns locale state, translation loading, and runtime language switching.
- `SecurityManager`: owns credential references, redaction, permission checks, and package integrity verification.
- `Worker`: performs actual work and reports structured progress.
- `SQLite`: stores jobs, tasks, artifacts, events, cache, and recovery state.

Do not collapse UI, workflow, scheduling, workers, and persistence into one page, one function, one button callback, or one script.

## 5. Non-Negotiable Boundaries

- GUI must never run heavy video, ASR, LLM, or AI enhancement work directly.
- GUI must never block the Qt main event loop with long-running work.
- GUI button handlers must not construct final FFmpeg or model commands directly.
- Long tasks must run in worker processes or external tools.
- Workers should report progress through a structured event protocol, preferably JSON Lines.
- Workers must write large outputs to temporary paths first, then atomically finalize artifacts.
- Workers must never silently overwrite user files.
- Scheduler is the only component that assigns resources.
- GUI may express hardware preferences, but it must not bypass Scheduler.
- HardwareDetector only observes hardware and process state; it does not schedule tasks.
- RuntimeManager is the only component that resolves executable paths, backend paths, model paths, and runtime environment variables for Workers.
- GUI and Workers must not assume globally installed FFmpeg, CUDA tools, llama.cpp, whisper.cpp, model files, or developer-local paths.
- ReleaseManager is the only component that applies app/runtime/model/plugin update plans.
- PluginManager is the only component that loads plugin manifests and registers plugin contributions.
- Third-party plugin code must not run inside GUI event handlers or directly access Scheduler, SQLite, resource locks, secrets, or arbitrary shell execution.
- Workspace layout must be persisted through WorkspaceManager; do not hard-code one immutable four-panel layout.
- User-facing UI strings must go through I18nManager or Qt translation APIs; code symbols, paths, logs, node types, model names, and error codes stay in their original language.
- Do not hard-code GPU usage as `cuda:0` except in explicit test fixtures.
- Failures are recoverable product states, not only modal error dialogs.
- Do not expose arbitrary shell execution in UI, workflow nodes, hardware policy, or worker configuration.
- FFmpeg and external tools must be invoked through typed adapters or command builders.
- Do not commit secrets, API keys, bearer tokens, or model-provider credentials.
- Secrets must not be written to SQLite plaintext, logs, task events, project files, presets, or docs.
- SecurityManager must be used for credential references, redaction, package integrity checks, and permission checks.

## 6. Default Technology Direction

```text
Primary language: Python 3.11 / 3.12
GUI: PySide6
Workflow / Queue / Scheduler: Python
State database: SQLite
Worker protocol: JSON Lines over stdout/stderr or structured IPC
Video processing: FFmpeg / ffprobe through typed adapters
AI tasks: Python adapters + external model backends
Runtime: managed application runtime + managed tool/model/backend runtime manifest
Plugins: manifest-driven contributions with explicit permissions and Worker isolation
Workspace: QMainWindow/QDockWidget-style dockable panels with persisted layouts
I18N: runtime language switching through translation keys and localeChanged events
Hardware: psutil + optional NVML adapters feeding Scheduler resource bindings
Security: local-first defaults, OS credential storage, package signatures, log redaction
Future hotspots: Rust / C++ / CUDA as replaceable workers only
```

Do not migrate the project to Rust, C++, Electron, Tauri, Celery, Redis, or a web stack unless the user explicitly asks for an architectural migration.

Atelier should package or manage every redistributable runtime component it depends on, including its Python/PySide6/Qt application runtime, FFmpeg/ffprobe, model backends, and model assets. System-level GPU drivers may remain external prerequisites, but Atelier must detect them, validate compatibility, and expose repair guidance instead of silently failing.

## 7. UI Product Rules

The default UI should feel like a calm professional creator workstation.

- The first screen should be the actual workstation, not a landing page.
- Users should immediately see workflow entry, queue state, hardware state, progress, logs, and recovery affordances.
- High-frequency work stays visible. Low-frequency maintenance belongs in secondary panels, settings, or Expert sections.
- Use `Basic / Advanced / Expert` disclosure for complexity.
- Workflow Canvas uses a card-based light node system, not a fully free ComfyUI-style graph.
- Execution Canvas should be generated from WorkflowGraph, then allow hardware-plan adjustments.
- Queue Monitor must show multi-stage state, artifacts, logs, and recovery actions. Do not show only one vague progress bar.
- Cards are for real functional areas, not decorative section wrappers.
- Do not nest cards inside cards.
- Motion should explain state changes, not perform decoration.

## 8. Persistence, Artifacts, And Recovery

- Frequently changing runtime state belongs in SQLite, not one large JSON file.
- JSON, YAML, and TOML are appropriate for workflow presets, node definitions, hardware policies, static config, and shareable recipes.
- Every meaningful processing stage should produce or consume artifacts.
- Artifacts should record type, path, producing task, hash when available, and metadata.
- Cache keys should consider input hash, node type, params, model version, engine version, worker version, and hardware-sensitive settings when relevant.
- Cache hits should appear clearly in UI as `cached` or `skipped`.
- Failure screens should show failed stage, human-readable reason, technical reason, affected downstream tasks, usable artifacts, and recommended recovery actions.

## 9. Development Workflow

### Planning Discipline

For non-trivial work, create or update a plan document before implementation.

A task is non-trivial if any of these are true:

- It touches logic or control flow, not only wording or comments.
- It touches more than one file.
- It requires debugging, root-cause analysis, or research.
- It requires tests, build verification, or UI verification.
- It changes API, CLI, config, schema, protocol, or public behavior.
- It involves concurrency, scheduling, persistence, performance, security, or hardware tradeoffs.
- It needs multiple steps to complete safely.

Plan files belong under:

```text
docs/plan/
```

Naming rules:

- Main objective plans must start with `plan_main_`, for example `docs/plan/plan_main_app_skeleton.md`.
- Sub-task plans should use descriptive names, for example `docs/plan/plan_worker_protocol.md`.
- Do not use vague names such as `implementation_plan.md`, `task_plan.md`, `progress.md`, or `findings.md` in the repository root.
- Root directory must stay limited to `README.md`, `AGENTS.md`, `DESIGN.md`, and project files that genuinely belong at root.

Plan documents should use a lightweight stable structure that improves continuity and updateability without creating process overhead.

A main plan document should normally contain these sections:

1. `Objective`
2. `Scope`
3. `Current Facts`
4. `Constraints`
5. `Execution Plan`
6. `Child Plans`
7. `Verification`
8. `Progress / Decisions`
9. `Blockers`

Guidelines:

- Keep the structure lightweight; do not turn plan files into heavyweight PRD-style process documents.
- `Current Facts` should contain verified facts only.
- `Constraints` should record real architectural, file-boundary, validation, or scope limits.
- When the work is multi-stage, `Execution Plan` should be organized by phases. Each phase should define its work goal and a short validation guide so the developer can confirm that the phase works as expected before proceeding to the next one. Provide test code when it is necessary to make the validation clear, reproducible, or easy to execute.
- Phase entries in `Execution Plan` should stay lightweight: define the phase goal, the expected completion signal, and a short validation guide without turning the plan into a heavy test-spec document.
- `Child Plans` should link only real sub-plans that materially reduce complexity.
- `Progress / Decisions` should be the primary section updated during execution.
- Update only the sections affected by new facts or progress.

### Debug Discipline

- During debugging, do not stack speculative patches, fallback branches, delays, retries, or local bypasses before confirming the root cause.
- Review the full chain first and identify the true error point; if the chain itself is defective, then consider a patch or structural fix.
- A single control should have one fact source for the same class of state such as geometry, visibility, enabled state, style, or core data binding; do not let multiple functions fight over that state unless the conversation explicitly requires it.
- For non-obvious bugs, chain-level bugs, or bugs that may affect multiple areas, report before fixing.
- In user-facing explanations, use the language currently being used by the user for communication; however, when referring to code symbols, file paths, class names, function names, or commands, retain their original language. Use this report format:
  `Root cause - Scope - Severity and priority - Fix plan - Fix scope - Risk of new bugs`

### Edit Discipline

Before editing:

1. Read relevant files.
2. Identify the layer: `UI`, `WorkflowGraph`, `ExecutionPlan`, `Scheduler`, `Worker`, `Storage`, `Adapter`, `Preset`, or `Docs`.
3. Check whether the change affects schemas, protocols, or public contracts.
4. For non-trivial tasks, read or create the relevant `docs/plan/` plan.
5. Make targeted edits only.

Evidence rules:

- Before suggesting a feature, flag, API, config option, or command exists, verify it with local files or official documentation.
- Anchor important claims to concrete files, docs, or command output.
- Do not assume CLI flags, config fields, or APIs exist without checking first.
- Never overwrite existing files with full-file rewrites when a targeted section edit is enough.

After editing:

1. Run the smallest useful validation.
2. If schemas change, update tests and docs.
3. If UI behavior changes, update interaction notes or screenshots when available.
4. If worker protocol changes, update protocol docs and compatibility notes.

Suggested validation once the project exists:

```powershell
python -m pytest
python -m ruff check .
python -m mypy .
```

If these tools are not configured yet, do not claim they passed. State exactly what was run.

## 10. Anti-Patterns

Avoid:

- One giant `main_window.py` containing UI, workflow, scheduling, and execution.
- Button callbacks that run FFmpeg or model inference directly.
- One JSON file storing all job runtime state.
- Hard-coded `cuda:0` across the project.
- Assuming global FFmpeg, CUDA tools, llama.cpp, whisper.cpp, model files, or developer-local runtime paths.
- Loading plugin code before validating its manifest, compatibility, and permissions.
- Putting plugin execution, model inference, downloads, or update application inside GUI callbacks.
- Hard-coding the four main UI regions as an immutable layout instead of a managed workspace.
- Writing user-facing UI text directly in widgets without translation keys.
- Retrying the same OOM/runtime/permission failure without a changed condition or recorded reason.
- Logging secrets, authorization headers, signed URLs, private prompts, or full sensitive paths in shareable diagnostics.
- Feature-specific progress bars disconnected from the task model.
- Failures shown only through modal error dialogs.
- Every feature inventing its own parameter UI.
- Every worker inventing its own progress format.
- Adding video or AI functionality without a node protocol.
- Adding hardware controls without Scheduler involvement.
