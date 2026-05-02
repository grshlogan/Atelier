# Atelier App Code Map

> This document maps the current code tree, file responsibilities, and boundaries. It is for AI agents and developers taking over the project. It does not replace `ARCHITECTURE.md`; it records what exists now.

Code file count: 47

Scope counted:

- `pyproject.toml`: 1 file
- `atelier/`: 34 files
- `tests/`: 12 files

## Current Code Tree

```text
pyproject.toml

atelier/
  __init__.py
  app/
    __init__.py
    bootstrap.py
    paths.py
    services.py
  core/
    __init__.py
    time.py
  domain/
    __init__.py
    execution_plan.py
    resources.py
    worker_event.py
  hardware/
    __init__.py
  i18n/
    __init__.py
  planning/
    __init__.py
    simple.py
  plugins/
    __init__.py
  release/
    __init__.py
  runtime/
    __init__.py
    health.py
    manager.py
    manifest.py
    store.py
  security/
    __init__.py
    package_integrity.py
  scheduler/
    __init__.py
    simple.py
  storage/
    __init__.py
    db.py
    repositories.py
    schema.sql
  workers/
    __init__.py
    simulated.py
  workflow/
    __init__.py
    graph.py

tests/
  test_app_paths.py
  test_app_services.py
  test_package_integrity.py
  test_phase6_minimal_loop.py
  test_planning_simple.py
  test_runtime_health.py
  test_runtime_manager.py
  test_runtime_store.py
  test_scheduler_simple.py
  test_simulated_worker.py
  test_storage_schema.py
  test_worker_events.py
```

## Root Project Files

### `pyproject.toml`

Responsibility:

- Declares the Python package name, Python version range, package discovery, and planned optional dependency groups.
- Current runtime dependency is `pydantic>=2.0`.
- Optional groups describe intended future stacks: `gui`, `scheduler`, `storage`, and `dev`.

Boundary:

- Does not install or manage Atelier runtime packs, model assets, FFmpeg, CUDA tools, or GUI runtime packages for end users.
- Do not treat optional dependencies as implemented product features.
- Development `.venv/` is local-only and should stay outside git; it is not the product App Runtime.

### `.gitignore`

Responsibility:

- Excludes Python bytecode/cache files, build outputs, local development virtual environments, and local Atelier development data.
- Current local-only environment paths:
  - `.venv/` and `venv/` for developer Python environments.
  - `.atelier/` for developer-local `AtelierData` simulation.

Boundary:

- `.gitignore` does not define product install paths.
- Do not put real product runtime packs into the repository just because they are ignored locally.

## Environment Directory Boundaries

Current intended split:

```text
atelier/runtime/              # runtime management source code
.venv/                        # developer Python environment, ignored
.atelier/AtelierData/         # developer-local managed runtime/data root, ignored
App Install Dir/app-runtime/  # packaged GUI runtime in release builds
AtelierData/runtimes/         # managed tool/backend/worker runtimes
```

Rules:

- `atelier/runtime/` never stores runtime binaries or virtual environments.
- `.venv/` is only for running tests and local development tools.
- `.atelier/AtelierData/` is the preferred local sandbox for testing runtime manifests, model stores, plugins, cache, and staging.
- Release packaging owns GUI runtime layout; RuntimeManager owns tool/model/backend runtime state.

## `atelier/`

### `atelier/__init__.py`

Responsibility:

- Marks `atelier` as the top-level Python package.

Boundary:

- Keep package initialization side-effect free.
- Do not place runtime setup, GUI startup, worker startup, or global logging configuration here.

## `atelier/app/`

### `atelier/app/__init__.py`

Responsibility:

- Marks the application orchestration package.

Boundary:

- No app boot side effects.

### `atelier/app/bootstrap.py`

Responsibility:

- Defines `AppBootstrapConfig`, the current minimal immutable application boot configuration.
- Records app name and optional database path for later bootstrapping.

Boundary:

- Does not create GUI objects, open SQLite connections, install runtimes, or start workers.
- Future bootstrap code should coordinate managers, not absorb GUI, scheduler, storage, or runtime logic.

### `atelier/app/paths.py`

Responsibility:

- Defines `AppPaths`, the current single path source for development and user-data roots.
- Provides `AppPaths.for_development(workspace_root)` for `.atelier/AtelierData` under a local workspace.
- Provides `AppPaths.from_data_root(data_root)` for release/user-data roots supplied by installers, settings, or OS conventions later.
- Exposes standard paths for runtime manifests, model manifests, database, cache, staging, logs, plugins, models, and runtimes.
- Creates shared local data directories through `ensure_data_dirs()`.

Boundary:

- Does not create or manage `.venv/`.
- Does not decide release install directories.
- Does not open SQLite, instantiate `RuntimeStore`, or install runtimes.
- Does not put runtime binaries under `atelier/runtime/`.

### `atelier/app/services.py`

Responsibility:

- Provides app-level factory functions that wire `AppPaths` into lower-level services.
- `create_runtime_store(paths)` creates a `RuntimeStore` from `paths.data_root` after ensuring local data directories exist.
- `open_app_database(paths)` opens `paths.database_path` and initializes the SQLite schema.

Boundary:

- This is orchestration glue, not a service container framework.
- Does not start GUI, Scheduler, workers, or external tools.
- Does not make `runtime/` or `storage/` depend on `app/`.
- Callers still own database connection lifetime and must close returned SQLite connections.

## `atelier/core/`

### `atelier/core/__init__.py`

Responsibility:

- Marks shared core utilities.

Boundary:

- Keep this package small and dependency-light.

### `atelier/core/time.py`

Responsibility:

- Provides `utc_now_iso()` for second-precision UTC timestamps with a `Z` suffix.

Boundary:

- Do not add product clocks, scheduler timing policy, retry delay logic, or UI formatting here.
- User-facing time formatting belongs under future i18n/presentation layers.

## `atelier/domain/`

### `atelier/domain/__init__.py`

Responsibility:

- Marks pure domain model package.

Boundary:

- Domain package should stay independent from GUI, SQLite, worker process control, and external tools.

### `atelier/domain/resources.py`

Responsibility:

- Defines resource and runtime request/binding models:
  - `ResourceRequest`
  - `ResourceBinding`
  - `RuntimeRequest`
  - `RuntimeBinding`
  - `HardwareSnapshot`
- Captures the contract between execution planning, scheduler, runtime manager, and workers.

Boundary:

- Does not detect hardware.
- Does not schedule tasks.
- Does not resolve actual executable or model paths.
- Do not hard-code a default GPU such as `cuda:0`.

### `atelier/domain/execution_plan.py`

Responsibility:

- Defines `ExecutionTask`, `ArtifactSlot`, `FailurePolicy`, and `TaskStatus`.
- Represents task-level execution intent, resource/runtime requirements, bindings, dependencies, cache keys, retry state, and error state.

Boundary:

- Does not generate plans from workflow graphs.
- Does not run tasks or mutate persistent storage.
- Does not decide hardware assignment; `resource_binding` should come from Scheduler.
- Does not resolve runtime paths; `runtime_binding` should come from RuntimeManager.

### `atelier/domain/worker_event.py`

Responsibility:

- Defines structured worker event models:
  - `StartedEvent`
  - `ProgressEvent`
  - `ArtifactEvent`
  - `CompletedEvent`
  - `FailedEvent`
  - `ArtifactRef`
- Defines `task_status_from_terminal_event()` for terminal event normalization.

Boundary:

- Does not parse arbitrary logs.
- Does not write artifacts.
- Does not update SQLite directly.
- Keep event schema compatible with the JSON Lines worker protocol.

## `atelier/hardware/`

### `atelier/hardware/__init__.py`

Responsibility:

- Placeholder package for future hardware detection and process health adapters.

Boundary:

- Hardware detection belongs here later; scheduling decisions do not.
- Do not import NVML, psutil, or driver-specific libraries at package import time.

## `atelier/i18n/`

### `atelier/i18n/__init__.py`

Responsibility:

- Placeholder package for future runtime language switching and translation catalog management.

Boundary:

- User-facing strings should eventually flow through this subsystem or Qt translation APIs.
- Do not hard-code UI strings in GUI widgets once GUI work starts.

## `atelier/planning/`

### `atelier/planning/__init__.py`

Responsibility:

- Marks the execution planning package.

Boundary:

- No planning work at import time.

### `atelier/planning/simple.py`

Responsibility:

- Provides `build_linear_execution_plan()` for the current Phase 6 minimum loop.
- Converts a `WorkflowGraph` into an `ExecutionPlan` containing `ExecutionTask` objects.
- Preserves simple edge dependencies by mapping source node IDs to generated task IDs.

Boundary:

- Not a full scheduler.
- Does not allocate hardware resources.
- Does not inspect runtime availability.
- Does not optimize, parallelize, retry, or recover execution.

## `atelier/plugins/`

### `atelier/plugins/__init__.py`

Responsibility:

- Placeholder package for future plugin manifest loading, contribution registration, and permission validation.

Boundary:

- Plugin code must not run in GUI callbacks.
- Plugin loading must not bypass manifest validation, permissions, runtime isolation, or worker boundaries.

## `atelier/release/`

### `atelier/release/__init__.py`

Responsibility:

- Placeholder package for future release channels, update manifests, staging, verification, and rollback planning.

Boundary:

- Do not apply app, runtime, model, or plugin updates from GUI handlers.
- Release/update code must use verification and rollback concepts before mutating installed state.

## `atelier/runtime/`

### `atelier/runtime/__init__.py`

Responsibility:

- Marks the runtime management package.

Boundary:

- No runtime probing, downloading, or path mutation at import time.

### `atelier/runtime/manifest.py`

Responsibility:

- Defines runtime-related manifest models:
  - `RuntimeStatus`
  - `RuntimeManifest`
  - `ModelAssetManifest`
- Captures component IDs, versions, declared paths, capabilities, checksums, model locations, and status.

Boundary:

- Does not read or write manifest files.
- Does not validate file existence.
- Does not install runtimes or models.

### `atelier/runtime/store.py`

Responsibility:

- Defines `RuntimeStore`.
- Owns the local `AtelierData`-style directory layout for runtime/model manifest persistence.
- Reads and writes installed runtime and model asset manifests as JSON collections.
- Writes through a temporary file and replaces the final manifest path.

Boundary:

- Does not download packages.
- Does not resolve task runtime bindings.
- Does not health-check component paths.
- Does not write outside its configured `data_root`.

### `atelier/runtime/manager.py`

Responsibility:

- Defines `RuntimeManager`.
- Resolves `RuntimeRequest` into `RuntimeBinding` from managed runtime/model manifests.
- Supports `RuntimeManager.from_store(store)` to load manifests from `RuntimeStore`.

Boundary:

- Does not inspect global `PATH`.
- Does not install missing runtimes or models.
- Does not schedule hardware resources.
- Does not launch workers or external tools.

### `atelier/runtime/health.py`

Responsibility:

- Defines `RuntimeHealthReport` and `RuntimeHealthChecker`.
- Checks declared runtime component paths relative to `data_root`.
- Reports missing paths, checksum mismatch, and ready state.
- Checks model asset local paths and optional model hash.

Boundary:

- Does not start executables for dry-run checks yet.
- Does not check GPU driver/backend compatibility yet.
- Does not repair or install anything.
- Does not decide which runtime a task should use.

## `atelier/security/`

### `atelier/security/__init__.py`

Responsibility:

- Marks the security package.

Boundary:

- Keep package import side-effect free.

### `atelier/security/package_integrity.py`

Responsibility:

- Provides `sha256_file()` and `verify_sha256()` for file integrity checks.
- Reads files in chunks to avoid loading large packages fully into memory.

Boundary:

- Does not implement signatures, trust roots, transparency logs, or update policy yet.
- Do not put package verification logic inside runtime or release modules if it belongs to this shared security layer.

## `atelier/scheduler/`

### `atelier/scheduler/__init__.py`

Responsibility:

- Marks the queue and scheduling package.

Boundary:

- No scheduling work at import time.

### `atelier/scheduler/simple.py`

Responsibility:

- Provides `SimpleScheduler` for the current Phase 7 minimum queue/Scheduler path.
- Finds the next runnable task through storage repository helpers.
- Creates a `ResourceBinding` and marks the claimed task as `running`.
- Respects task dependency readiness as reported by storage.

Boundary:

- Not the final Scheduler.
- Does not execute worker processes.
- Does not manage resource locks, concurrency, retries, priorities, or recovery.
- CPU binding is intentionally simple; GPU support only picks the first declared GPU and is not a full policy.

## `atelier/storage/`

### `atelier/storage/__init__.py`

Responsibility:

- Marks the storage package.

Boundary:

- No database connection side effects at import time.

### `atelier/storage/db.py`

Responsibility:

- Provides `initialize_database(connection)` to apply `schema.sql` to a supplied SQLite connection.
- Provides `list_tables(connection)` for validation and tests.

Boundary:

- Does not own connection lifecycle.
- Does not implement repositories or migrations yet.
- Does not serialize domain models into rows yet.

### `atelier/storage/repositories.py`

Responsibility:

- Provides the current minimal SQLite persistence functions for Phase 6.
- `persist_planned_execution()` writes a project, workflow graph, job, execution plan, execution tasks, and task dependencies.
- `record_worker_events()` writes structured worker events to `task_events`, records `ArtifactEvent` rows to `artifacts` / `task_artifacts`, and updates terminal task status.
- Provides minimum queue helpers for Phase 7: `fetch_next_runnable_task()`, `mark_task_running()`, and `fetch_task_resource_binding()`.
- Provides small query helpers for tests: `fetch_task_event_types()`, `fetch_artifact_paths()`, and `fetch_task_status()`.

Boundary:

- This is not the final repository layer.
- Does not own SQLite connection lifecycle.
- Does not implement migrations.
- Does not implement durable queue claiming, retries, recovery actions, cache lookups, or scheduler locks.
- Does not parse logs; it records structured worker events only.

### `atelier/storage/schema.sql`

Responsibility:

- Defines the first SQLite schema skeleton:
  - projects
  - workflow_graphs
  - jobs
  - execution_plans
  - execution_tasks
  - task_dependencies
  - artifacts
  - task_artifacts
  - task_events
  - resource_locks
  - cache_entries
  - presets
  - runtime_components
  - model_assets
  - credential_refs

Boundary:

- Schema exists, but repository APIs and migration tooling are not implemented yet.
- Do not treat every target column as wired to code yet.

## `atelier/workers/`

### `atelier/workers/__init__.py`

Responsibility:

- Marks the worker package.

Boundary:

- No worker process startup at import time.

### `atelier/workers/simulated.py`

Responsibility:

- Provides `run_simulated_task()` for a deterministic simulated worker event sequence.
- Emits started, progress, artifact, and completed events for tests and early queue/storage integration.

Boundary:

- Does not perform video, ASR, LLM, or model work.
- Does not spawn subprocesses.
- Does not write artifacts to disk.
- Should be replaced by real worker runner/adapters only through the worker protocol boundary.

## `atelier/workflow/`

### `atelier/workflow/__init__.py`

Responsibility:

- Marks the workflow graph package.

Boundary:

- No registry loading or validation side effects at import time.

### `atelier/workflow/graph.py`

Responsibility:

- Defines the current minimal workflow graph models:
  - `WorkflowGraph`
  - `WorkflowNode`
  - `WorkflowEdge`
  - `WorkflowPortRef`
- Carries node params, resource requests, runtime requests, and simple edge references.

Boundary:

- Does not implement the full node registry.
- Does not validate media formats or node compatibility.
- Does not generate execution plans.
- Does not run workflow nodes.

## `tests/`

### `tests/test_app_paths.py`

Responsibility:

- Tests development `AppPaths` layout under `.atelier/AtelierData`.
- Tests shared runtime/model/plugin/cache/staging/log directory creation.
- Tests `AppPaths.from_data_root()` for release or user-data roots.

Boundary:

- Does not test installer-specific app runtime layout.
- Does not create `.venv/`.
- Does not instantiate real runtime stores, SQLite databases, or GUI objects.

### `tests/test_app_services.py`

Responsibility:

- Tests app-level wiring from `AppPaths` to `RuntimeStore`.
- Tests opening `AppPaths.database_path` and initializing SQLite schema through `open_app_database()`.

Boundary:

- Does not test GUI startup.
- Does not run worker tasks.
- Does not keep SQLite connections open after assertions.

### `tests/test_worker_events.py`

Responsibility:

- Tests terminal worker event normalization.
- Confirms `CANCELLED` maps to `cancelled` and `INTERRUPTED` remains failed but recoverable.

Boundary:

- Does not test storage persistence or worker process execution.

### `tests/test_runtime_manager.py`

Responsibility:

- Tests resolving runtime bindings from in-memory manifests.
- Tests missing runtime component failure.

Boundary:

- Does not check filesystem health or package integrity.

### `tests/test_runtime_store.py`

Responsibility:

- Tests runtime/model manifest persistence through `RuntimeStore`.
- Tests `RuntimeManager.from_store()` integration.

Boundary:

- Does not perform package download or runtime installation.

### `tests/test_scheduler_simple.py`

Responsibility:

- Tests the Phase 7 minimum queue/Scheduler path.
- Confirms only dependency-ready pending tasks can be claimed.
- Confirms claimed tasks are marked `running` and have persisted `ResourceBinding`.
- Confirms downstream tasks become claimable after upstream simulated worker events complete.

Boundary:

- Does not test real concurrency, resource locks, worker subprocesses, or GPU policy.

### `tests/test_runtime_health.py`

Responsibility:

- Tests runtime path checks, missing path reporting, checksum mismatch reporting, and model path health.

Boundary:

- Does not start real executables or inspect real GPU/backend compatibility.

### `tests/test_package_integrity.py`

Responsibility:

- Tests SHA-256 digest generation and mismatch rejection.

Boundary:

- Does not test signatures or release policy.

### `tests/test_phase6_minimal_loop.py`

Responsibility:

- Tests the current Phase 6 business loop:
  `WorkflowGraph -> ExecutionPlan -> simulated Worker -> SQLite events/artifacts`.
- Confirms worker event types, artifact paths, and completed task status are persisted.

Boundary:

- Does not test real GUI, Scheduler, FFmpeg, model backends, or worker subprocesses.

### `tests/test_planning_simple.py`

Responsibility:

- Tests `build_linear_execution_plan()` task generation and edge dependency preservation.
- Tests empty graph rejection.

Boundary:

- Does not test full scheduling or advanced graph validation.

### `tests/test_storage_schema.py`

Responsibility:

- Tests that SQLite schema initialization creates core tables.

Boundary:

- Does not test repositories, migrations, or domain-to-row mapping.

### `tests/test_simulated_worker.py`

Responsibility:

- Tests simulated worker event order, sequence numbers, and artifact path reporting.

Boundary:

- Does not execute real external tools or write output files.

## Not Yet Present

These packages are specified in docs but not fully implemented yet:

- `workflow/`: only minimal graph models exist; full node schema validation and registry are not implemented.
- `planning/`: only a simple linear planner exists; full ExecutionPlan generation, validation, conflict detection, and optimization are not implemented.
- `scheduler/`: only `SimpleScheduler` exists; durable queue claiming, resource locks, priorities, concurrency, and recovery are not implemented.
- `gui/`: PySide6 application window, dock workspace, canvas, panels.
- `workers/adapters/`: typed FFmpeg, ffprobe, ASR, translation, enhancement adapters.
- `storage/repositories/`: only minimal Phase 6 persistence and Phase 7 queue helpers exist; durable repository APIs are not complete.
- `runtime` advanced pieces: real runtime import, install, dry-run, backend compatibility, model store operations.
- `release` implementation: update manifests, staging, rollback.
- `plugins` implementation: manifest validation, contribution registry, isolation.
- `i18n` implementation: catalog loading and runtime locale switching.
