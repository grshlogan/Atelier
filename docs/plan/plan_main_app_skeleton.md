# Atelier App Skeleton Plan

## Objective

Prepare the documentation contract for the first application skeleton, then scaffold a local-first Python/PySide6 desktop workstation around WorkflowGraph, ExecutionPlan, Scheduler, Worker, Storage, Hardware, and Runtime boundaries.

## Scope

- Patch current specs so they agree on artifacts, cache hits, cancellation, resource bindings, and runtime ownership.
- Treat Atelier's runtime environment as a first-class subsystem before code skeleton work begins.
- Treat release/update, plugin system, workspace layout, and i18n as first-class subsystem contracts before code skeleton work begins.
- Keep root clean: root docs stay limited to `README.md`, `AGENTS.md`, and `DESIGN.md`; planning lives under `docs/plan/`.

## Current Facts

- Project name is `Atelier`.
- First implementation direction is Python 3.12, PySide6, SQLite, Pydantic v2, JSON Lines workers, and typed external-tool adapters.
- Runtime-heavy work must not run in the GUI process.
- `rg` is unavailable in this environment because Windows returned `Access is denied`; use PowerShell `Select-String` for repository text search until this is resolved.

## Constraints

- GUI must not call FFmpeg, model inference, CUDA, llama.cpp, or any heavy backend directly.
- Scheduler is the only component that binds hardware resources.
- Runtime/tool/model paths must come from a managed runtime manifest, not from global `PATH` assumptions or developer-local paths.
- System GPU drivers may be detected and validated, but Atelier should manage all redistributable user-space runtime components it depends on.
- App/runtime/model/plugin updates must use manifest, hash/signature verification, staging, and rollback concepts.
- Plugin contributions must be manifest-driven and must not execute heavy work in the GUI process.
- Workspace layout must be persisted and restorable, not hard-coded as one immutable four-panel layout.
- UI text must use translation keys and support runtime locale switching.
- Hardware scheduling, failure recovery, and security/privacy boundaries must be documented before scaffold work.

## Execution Plan

### Phase 1: Documentation Patch

Goal: make the current docs internally consistent before scaffold work.

Completion signal:

- Specs mention runtime ownership.
- Cache-hit artifacts can be associated with the consuming task.
- Cancel semantics map clearly to `TaskStatus.CANCELLED`.
- Resource binding has one authoritative fact source.

Validation:

- Run `git diff --check`.
- Review changed docs with `Select-String` for the patched terms.

### Phase 2: Skeleton Design Confirmation

Goal: present a concise skeleton design before creating production code.

Completion signal:

- User confirms the module layout and runtime environment strategy.

Validation:

- No code scaffold is created before confirmation.

## Child Plans

- None yet.

## Verification

- Documentation phase: `git diff --check`.
- Code skeleton phase later: start with tests for pure domain/protocol/storage modules before production code.

## Progress / Decisions

- 2026-05-03: Created this plan before non-trivial documentation and skeleton work.
- 2026-05-03: Patched specs to add RuntimeManager ownership, RuntimeRequirement/RuntimeBinding, cache/runtime fingerprints, task_artifacts, and clearer cancellation/resource-binding rules.
- 2026-05-03: Added release/update, runtime environment, plugin system, UI workspace, and i18n specs after reviewing reference software patterns.
- 2026-05-03: Added hardware scheduling, failure recovery, and security/privacy specs after reviewing official/high-trust references.
- 2026-05-03: Ran cross-document alignment; added missing ReleaseManager/SecurityManager references, credential_refs schema, and INTERRUPTED worker error code.

## Blockers

- None.
