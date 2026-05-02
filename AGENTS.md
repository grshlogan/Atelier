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
5. Future architecture docs such as `ARCHITECTURE.md`, `WORKFLOW_NODE_SPEC.md`, `EXECUTION_PLAN_SPEC.md`, and `WORKER_PROTOCOL.md`.

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
- Do not hard-code GPU usage as `cuda:0` except in explicit test fixtures.
- Failures are recoverable product states, not only modal error dialogs.
- Do not expose arbitrary shell execution in UI, workflow nodes, hardware policy, or worker configuration.
- FFmpeg and external tools must be invoked through typed adapters or command builders.
- Do not commit secrets, API keys, bearer tokens, or model-provider credentials.

## 6. Default Technology Direction

```text
Primary language: Python 3.11 / 3.12
GUI: PySide6
Workflow / Queue / Scheduler: Python
State database: SQLite
Worker protocol: JSON Lines over stdout/stderr or structured IPC
Video processing: FFmpeg / ffprobe through typed adapters
AI tasks: Python adapters + external model backends
Future hotspots: Rust / C++ / CUDA as replaceable workers only
```

Do not migrate the project to Rust, C++, Electron, Tauri, Celery, Redis, or a web stack unless the user explicitly asks for an architectural migration.

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

Before editing:

1. Read relevant files.
2. Identify the layer: `UI`, `WorkflowGraph`, `ExecutionPlan`, `Scheduler`, `Worker`, `Storage`, `Adapter`, `Preset`, or `Docs`.
3. Check whether the change affects schemas, protocols, or public contracts.
4. Make targeted edits only.

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
- Feature-specific progress bars disconnected from the task model.
- Failures shown only through modal error dialogs.
- Every feature inventing its own parameter UI.
- Every worker inventing its own progress format.
- Adding video or AI functionality without a node protocol.
- Adding hardware controls without Scheduler involvement.
