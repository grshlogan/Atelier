# Atelier App Code Map

> This document maps the current code tree, file responsibilities, and boundaries. It is for AI agents and developers taking over the project. It does not replace `ARCHITECTURE.md`; it records what exists now.

Code file count: 96

Scope counted:

- `pyproject.toml`: 1 file
- `atelier/`: 58 files
- `tests/`: 37 files

Non-code asset files are listed for ownership and handoff, but are not included in the code file count.

## Current Code Tree

```text
pyproject.toml

atelier/
  adapters/
    __init__.py
    base.py
    builtins.py
    command.py
    finalize.py
    ffmpeg.py
    ffprobe.py
    registry.py
  assets/
    README.md
    icon_manifest.json
    preview.html
    atelier_icons_sprite.svg
    brand/
    hardware/
    inspector/
    navigation/
    nodes/
    queue/
    status/
    system/
    toolbar/
  __init__.py
  app/
    __init__.py
    bootstrap.py
    paths.py
    runtime_setup.py
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
  gui/
    __init__.py
    app.py
    entry.py
    layout_store.py
    main_window.py
    runtime_setup_panel.py
    runtime_setup_state.py
    state_reader.py
    workspace.py
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
    registration.py
    setup.py
    store.py
  security/
    __init__.py
    package_integrity.py
  scheduler/
    __init__.py
    dispatch.py
    simple.py
  storage/
    __init__.py
    db.py
    repositories.py
    schema.sql
  workers/
    __init__.py
    adapter_entry.py
    protocol.py
    runner.py
    simulated.py
    task_file.py
  workflow/
    __init__.py
    graph.py

tests/
  test_adapter_registry.py
  test_app_runtime_setup_service.py
  test_app_paths.py
  test_app_services.py
  test_artifact_finalizer_adapter.py
  test_backend_workflow_handoff.py
  test_command_executor.py
  test_failure_recovery.py
  test_ffmpeg_audio_extract_adapter.py
  test_ffprobe_metadata_adapter.py
  test_gui_app_entry.py
  test_gui_optional_dependency.py
  test_gui_layout_store.py
  test_gui_runtime_setup.py
  test_gui_runtime_setup_state.py
  test_gui_smoke.py
  test_gui_state_reader.py
  test_minimal_audio_extract_workflow.py
  test_minimal_probe_workflow.py
  test_output_export_workflow.py
  test_package_integrity.py
  test_phase6_minimal_loop.py
  test_planning_simple.py
  test_runtime_health.py
  test_runtime_manager.py
  test_runtime_registration.py
  test_runtime_setup_snapshot.py
  test_runtime_store.py
  test_resource_locks.py
  test_scheduler_worker_runner_integration.py
  test_scheduler_simple.py
  test_simulated_worker.py
  test_storage_schema.py
  test_worker_events.py
  test_worker_lifecycle.py
  test_worker_protocol.py
  test_worker_runner.py
  test_worker_task_file.py
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

### `atelier/adapters/`

Responsibility:

- Provides the first Worker adapter boundary for real tool execution.
- Keeps adapter contract, registry, typed command execution, ffprobe metadata probing, FFmpeg audio extraction, and final output copying outside GUI, Scheduler, and SQLite layers.

Boundary:

- Adapter code does not schedule tasks, claim resources, or write SQLite directly.
- Adapters consume `ExecutionTask`, `RuntimeBinding`, `ResourceBinding`, and a task work directory, then return artifact refs / metadata or raise structured adapter errors.
- External tools are invoked only through typed command specs, not shell strings.

### `atelier/adapters/__init__.py`

Responsibility:

- Marks the adapter package.

Boundary:

- No registry loading or command execution at import time.

### `atelier/adapters/base.py`

Responsibility:

- Defines the current minimal adapter contract:
  - `AdapterContext`
  - `AdapterResult`
  - `AdapterValidationError`
  - `AdapterExecutionError`
  - `WorkerAdapter`
- Provides default `prepare()` behavior for task work directories.

Boundary:

- Does not import PySide6, Scheduler, SQLite, subprocess runner, or concrete tool adapters.
- Does not own cancellation transport beyond the future `WorkerAdapter.cancel()` hook.

### `atelier/adapters/registry.py`

Responsibility:

- Defines `AdapterRegistry` and `AdapterRegistryError`.
- Registers adapter instances by `node_type`.
- Provides explicit duplicate and missing-adapter diagnostics.

Boundary:

- Does not auto-discover plugins or load third-party code.
- Does not validate node schemas or runtime requirements.

### `atelier/adapters/command.py`

Responsibility:

- Defines `CommandSpec`, `CommandResult`, `CommandExecutionError`, and `run_command()`.
- Runs typed commands as `[executable, *args]` with caller-provided `cwd`, env overlay, UTF-8 text capture, optional timeout, and redacted command metadata.

Boundary:

- Does not support arbitrary shell strings or `shell=True`.
- Does not select executable paths; RuntimeManager / RuntimeBinding must supply them.
- Does not redact stdout/stderr automatically beyond exposing a redacted command shape.

### `atelier/adapters/finalize.py`

Responsibility:

- Defines `ArtifactFinalizerAdapter` for `output.export`.
- Copies an existing staged artifact from task `input_path` to task `output_dir`.
- Uses an optional safe `filename`, defaulting to the source filename.
- Rejects output conflicts instead of overwriting user files.
- Verifies final output size and SHA-256 after copy.
- Returns a final output artifact ref with `metadata.role = final_output`.

Boundary:

- Does not run FFmpeg or any external executable.
- Does not write SQLite directly.
- Does not delete or move the staged source artifact.
- Does not implement GUI file dialogs, batch export, naming templates, mux/burn, or format conversion.

### `atelier/adapters/ffprobe.py`

Responsibility:

- Defines `FFprobeMetadataAdapter` for `metadata.probe`.
- Reads the `ffprobe` executable path from `RuntimeBinding.component_paths`.
- Validates the input media path from task params.
- Runs `ffprobe -v error -print_format json -show_format -show_streams <input>`.
- Writes `probe.json` under the task work directory and returns a `metadata` artifact ref plus summarized metadata.
- Maps missing runtime, missing input, command failure, and invalid JSON into structured `AdapterExecutionError` values.

Boundary:

- Does not call global `PATH`.
- Does not write SQLite or final user output directories.
- Does not implement audio extraction, mux/burn, export, ASR, OCR, translation, or enhancement.

### `atelier/adapters/ffmpeg.py`

Responsibility:

- Defines `FFmpegAudioExtractAdapter` for `media.audio_extract`.
- Reads the `ffmpeg` executable path from `RuntimeBinding.component_paths`.
- Validates the input media path from task params.
- Runs `ffmpeg -y -i <input> -vn audio.wav` through typed `CommandSpec`.
- Verifies `audio.wav` exists under the task work directory and returns an `audio` artifact ref.
- Maps missing runtime, missing input, command failure, and missing output into structured `AdapterExecutionError` values.

Boundary:

- Does not call global `PATH`.
- Does not write SQLite or final user output directories.
- Does not implement no-audio policy, progress parsing, ASR, OCR, translation, mux/burn, or final export.

### `atelier/adapters/builtins.py`

Responsibility:

- Provides `create_builtin_adapter_registry()`.
- Registers the current built-in `metadata.probe` / `FFprobeMetadataAdapter`, `media.audio_extract` / `FFmpegAudioExtractAdapter`, and `output.export` / `ArtifactFinalizerAdapter`.

Boundary:

- Does not load plugin adapters.
- Does not perform runtime health checks or command execution during registry construction.

### `atelier/assets/`

Responsibility:

- Stores the current Atelier icon resources.
- Provides brand/app icon assets under `brand/` for app icon, installer/about page, header logo, monochrome mark, and tray variants.
- Keeps `brand/01.png` through `brand/04.png` as visual reference renders for the brand SVGs.
- Provides original 24 × 24 SVG line icons for toolbar, navigation, workflow nodes, queue, hardware, status, inspector, and system module surfaces.
- Provides `icon_manifest.json` as the current icon inventory.
- Provides `atelier_icons_sprite.svg` and `preview.html` as preview / future build-pipeline reference assets.

Boundary:

- This is a resource directory, not Python runtime logic.
- Does not implement Qt `.qrc` registration, IconManager, runtime recoloring, icon cache, or theme switching.
- Does not generate Windows `.ico`, macOS `.icns`, or a complete PNG export set from brand SVGs.
- Do not load icons through ad hoc hard-coded paths in many widgets once GUI implementation starts; add a single asset path / icon loading boundary first.
- Does not contain third-party brand logos or external reference design assets.

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
- Exposes `workspace_layouts_path` for GUI layout persistence under the managed cache root.
- Creates shared local data directories through `ensure_data_dirs()`.

Boundary:

- Does not create or manage `.venv/`.
- Does not decide release install directories.
- Does not open SQLite, instantiate `RuntimeStore`, or install runtimes.
- Does not put runtime binaries under `atelier/runtime/`.

### `atelier/app/runtime_setup.py`

Responsibility:

- Defines `RuntimeSetupAppService`.
- Wraps `RuntimeRegistrationService`, `RuntimeHealthChecker`, and `RuntimeSetupSnapshot` refresh for app/UI callers.
- Provides controlled registration methods for local `ffprobe`, local `ffmpeg`, development Worker Python, and a local demo model directory.
- Returns refreshed runtime setup snapshots after successful registration.

Boundary:

- Does not open file dialogs or render GUI widgets.
- Does not run FFmpeg, Python workers, model inference, Scheduler, or external tools.
- Does not download, install, repair, or overwrite runtimes/models.
- Keeps runtime/profile defaults centralized for the first GUI Runtime Setup surface.

### `atelier/app/services.py`

Responsibility:

- Provides app-level factory functions that wire `AppPaths` into lower-level services.
- `create_runtime_store(paths)` creates a `RuntimeStore` from `paths.data_root` after ensuring local data directories exist.
- `create_runtime_setup_service(paths)` creates a `RuntimeSetupAppService` over the managed data root.
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
  - `LogEvent`
  - `HeartbeatEvent`
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

## `atelier/gui/`

### `atelier/gui/__init__.py`

Responsibility:

- Marks the optional GUI package.

Boundary:

- Importing `atelier.gui` must not import PySide6 or start a Qt application.
- Keep package initialization side-effect free.

### `atelier/gui/app.py`

Responsibility:

- Provides the formal development launch entry for the read-only workbench.
- Supports `.venv/Scripts/python -m atelier.gui.app`.
- Parses `--workspace-root`, `--data-root`, and `--no-restore-layout`.
- Opens the app database, reads a `WorkbenchSnapshot`, creates a `RuntimeSetupAppService`, reads a `RuntimeSetupSnapshot`, creates `MainWindow`, optionally restores workspace layout, and starts the Qt event loop from `main()`.

Boundary:

- Does not trigger Scheduler claim, worker execution, FFmpeg/model adapters, runtime install, plugin loading, or recovery actions.
- Test helpers build the launch context without entering the Qt event loop.
- Keeps launch orchestration separate from `MainWindow` rendering, `state_reader` queries, and runtime setup registration behavior.

### `atelier/gui/entry.py`

Responsibility:

- Defines the Phase A optional GUI dependency boundary.
- Provides `check_gui_dependency()` to report whether `PySide6` is installed.
- Provides `ensure_gui_dependency()` to fail with the documented `.[gui]` install command when PySide6 is missing.

Boundary:

- Does not import PySide6 at module import time.
- Does not create `QApplication`, windows, docks, panels, or event loops.
- Does not read SQLite, run Scheduler, start workers, or install runtimes.

### `atelier/gui/layout_store.py`

Responsibility:

- Defines `WorkspaceLayoutStore` and `WorkspaceLayoutRecord`.
- Saves and loads named workspace layout geometry/state bytes as JSON under `AppPaths.workspace_layouts_path`.
- Encodes Qt byte arrays with base64 so the layout file stays text-based.

Boundary:

- Does not import PySide6.
- Does not decide dock policy, panel visibility, or workspace presets.
- Does not write outside the managed `AtelierData` cache root.

### `atelier/gui/main_window.py`

Responsibility:

- Defines the first read-only PySide6 `MainWindow`.
- Accepts `AppPaths`, optional `WorkbenchSnapshot`, optional `RuntimeSetupSnapshot`, and an optional runtime setup service.
- Creates a `QMainWindow` with dock widgets for workflow, execution, queue, resources/runtime, and Runtime Setup panels.
- Renders the queue snapshot as read-only text when provided.
- Renders Runtime Setup through `runtime_setup_panel.py` when a snapshot is provided.
- Saves and restores workspace geometry/state through `WorkspaceLayoutStore`.

Boundary:

- Does not start `QApplication` or the Qt event loop.
- Does not open SQLite directly.
- Does not call Scheduler, worker runners, FFmpeg, model backends, or runtime installers.
- Does not choose executable/model paths itself; Runtime Setup actions go through the supplied app service.
- Does not implement complex workspace presets, panel visibility policy, or user-facing layout management UI yet.

### `atelier/gui/runtime_setup_panel.py`

Responsibility:

- Defines the first actionable PySide6 Runtime Setup panel.
- Renders runtime/model summary, component/model details, registration buttons, refresh, and diagnostic errors.
- Uses `RuntimeSetupServiceProtocol` so widget actions call an app service instead of constructing commands or writing manifests directly.
- Opens file/directory pickers only for local path selection; registration behavior remains outside the widget.

Boundary:

- Does not run external tools, Scheduler, workers, FFmpeg, Python backends, or model inference.
- Does not parse shell commands or mutate runtime manifests directly.
- Does not implement download/install/repair flows or full Settings integration.

### `atelier/gui/runtime_setup_state.py`

Responsibility:

- Defines PySide-independent view models for Runtime Setup:
  - `RuntimeSetupSummaryView`
  - `RuntimeSetupItemView`
  - `RuntimeSetupActionView`
  - `RuntimeSetupViewState`
- Converts `RuntimeSetupSnapshot` into GUI-renderable labels, detail lines, and registration action enabled states.

Boundary:

- Does not import PySide6.
- Does not read/write manifests, register runtimes, or run health checks.
- Does not own visual styling or file dialogs.

### `atelier/gui/state_reader.py`

Responsibility:

- Defines GUI-facing read-only view models:
  - `WorkbenchTaskItem`
  - `WorkbenchSnapshot`
- Provides `read_workbench_snapshot(connection)` to read task status, resource device, event count, and artifact paths from SQLite.

Boundary:

- Does not import PySide6.
- Does not write to SQLite.
- Does not call Scheduler or recovery actions.
- Does not attempt to render widgets.

### `atelier/gui/workspace.py`

Responsibility:

- Defines `WorkspacePanelSpec` and `DEFAULT_WORKSPACE_PANELS`.
- Creates read-only placeholder panel widgets for the workstation shell.
- Formats queue snapshot rows for the current minimal Queue panel.

Boundary:

- Does not read SQLite directly.
- Does not run tasks or mutate state.
- Does not implement theme, i18n catalog, real canvases, or dock layout persistence yet.

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
  - `RuntimeKind`
  - `RuntimeProfileKind`
  - `RuntimeManifest`
  - `ModelAssetManifest`
- Captures component IDs, versions, runtime kind, profile kind, display name, platform, declared component/executable paths, library dirs, scoped env, capabilities, backend tags, integrity/checksums, model locations, model family/task/backend metadata, and status.

Boundary:

- Does not read or write manifest files.
- Does not validate file existence.
- Does not install runtimes or models.

### `atelier/runtime/registration.py`

Responsibility:

- Defines `RuntimeRegistrationError` and `RuntimeRegistrationService`.
- Registers local executable runtime profiles into `RuntimeStore` without copying binaries or mutating system environment.
- Registers development Worker Python profiles as `kind="worker_env"` / `profile_kind="dev"`.
- Registers local model asset profiles into `RuntimeStore`.
- Rejects empty paths, missing paths, relative path traversal, duplicate runtime ids, and duplicate model ids.
- Stores paths relative to `RuntimeStore.data_root` when possible; user-selected absolute paths outside `AtelierData` remain local profile paths in the user's manifest only.

Boundary:

- Does not download, unpack, install, run, or health-check runtime binaries.
- Does not parse arbitrary shell commands.
- Does not write secrets.
- Does not resolve `RuntimeRequest` or launch Workers.

### `atelier/runtime/setup.py`

Responsibility:

- Defines GUI-readable runtime setup snapshot models:
  - `RuntimeComponentSnapshot`
  - `ModelAssetSnapshot`
  - `RuntimeSetupSnapshot`
- Provides `build_runtime_setup_snapshot(store, checker)`.
- Loads runtime/model manifests from `RuntimeStore`.
- Uses `RuntimeHealthChecker` to attach status, issues, repair hints, and checked paths.

Boundary:

- Does not register, download, repair, or install runtimes.
- Does not launch Workers or run heavy tools.
- Does not mutate manifests.
- Does not render GUI widgets.

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
- Defines `RuntimeResolutionError` with `subject_id` and `reason` for missing, disabled, status-mismatched, and capability-mismatched runtime/model resolution failures.
- Merges manifest-scoped env into `RuntimeBinding.env` without reading global `PATH`.

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
- Provides GUI-readable `repair_hints` for missing, broken, disabled, and dry-run failure states.
- Supports caller-provided safe dry-run probe args using list-based subprocess execution without `shell=True`.
- Checks model asset local paths and optional model hash.

Boundary:

- Does not choose dry-run commands itself.
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

### `atelier/scheduler/dispatch.py`

Responsibility:

- Defines `WorkerDispatchResult`.
- Provides `dispatch_claimed_task()` for the first narrow Scheduler-to-runner integration seam.
- Accepts an already claimed `ClaimedTask`, writes `task.json` through `build_worker_process_spec()`, runs the supplied stub worker command through `run_worker_process()` or `run_worker_lifecycle()`, persists returned Worker events through `record_worker_events()`, and returns task id, parsed events, stderr, return code, final SQLite task status, and optional lifecycle facts.
- Supports optional `runtime_binding`, `lifecycle_config`, `cancel_event`, and `stderr_log_path` parameters for callers that need RuntimeManager binding or lifecycle timeout/cancel/log behavior.
- Copies the Scheduler-provided `ResourceBinding` onto the task payload before writing `task.json`.
- Copies the caller-provided `RuntimeBinding` onto the task payload before writing `task.json`.
- Converts `WorkerProcessProtocolError` into a persisted `FailedEvent(error_code="INTERNAL")` so malformed worker stdout does not leave a task running or a resource lock active.
- Persists lifecycle timeout as `TIMEOUT`, lifecycle cancel as `CANCELLED` / `cancelled`, and lifecycle protocol errors as `INTERNAL`, while preserving stderr log path facts and releasing active resource locks.

Boundary:

- Does not claim tasks; callers must use Scheduler first.
- Does not choose runtime/model paths, command args, or hardware resources.
- Does not implement multi-worker concurrency, priority scheduling, retry execution, protocol-error retry/recovery actions, or automatic timeout/cancel policy selection.
- Does not let `workers.runner` write SQLite; persistence remains in storage repositories.

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
- `record_worker_events()` writes structured worker events to `task_events`, records `ArtifactEvent` rows to `artifacts` / `task_artifacts`, updates terminal task status, and releases active task resource locks on terminal events.
- Records `ArtifactEvent.metadata.role == "final_output"` as `task_artifacts.role = "final_output"`; other artifact events remain role `output`.
- Provides `TaskArtifactRecord` and `fetch_task_output_artifacts()` as the first artifact handoff query for downstream workflow runner work.
- Provides minimum queue helpers for Phase 7: `fetch_next_runnable_task()`, `mark_task_running()`, and `fetch_task_resource_binding()`.
- Provides minimum resource lock helpers for the resource-lock plan: `ResourceLockRecord`, `StaleResourceLockRecord`, `fetch_active_resource_lock()`, `fetch_stale_resource_locks()`, and `release_stale_resource_lock()`.
- Provides minimum failure recovery helpers for the resource-lock plan: `FailureFacts`, `RecoveryOption`, `fetch_failure_facts()`, and `suggest_recovery_options()`.
- Records `FailedEvent.partial_artifacts` as partial artifacts and links them through `task_artifacts`.
- Persists terminal failure `error_code` and `error_message` onto `execution_tasks`.
- Provides small query helpers for tests: `fetch_task_event_types()`, `fetch_artifact_paths()`, `fetch_task_artifact_links()`, and `fetch_task_status()`.

Boundary:

- This is not the final repository layer.
- Does not own SQLite connection lifecycle.
- Does not implement migrations.
- Does not implement durable queue claiming, retry execution, crash recovery scans, cache lookups, or production scheduler locks.
- Does not materialize downstream task params or choose between ambiguous multi-output artifacts.
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

### `atelier/workers/adapter_entry.py`

Responsibility:

- Provides the first adapter worker entrypoint.
- Supports `.venv/Scripts/python -m atelier.workers.adapter_entry --task-file <task.json>`.
- Loads an `ExecutionTask` from `task.json`, resolves the adapter by `node_type` from the built-in adapter registry, builds `AdapterContext`, runs the adapter, and emits Worker JSON Lines.
- Emits `started -> artifact -> completed` on success and `started -> failed` for structured adapter failures.

Boundary:

- Does not read or write SQLite.
- Does not claim Scheduler tasks or assign hardware.
- Does not resolve runtime paths itself; it requires `runtime_binding` to already be present in the task payload.
- Does not load plugin adapters or run GUI code.

### `atelier/workers/protocol.py`

Responsibility:

- Defines the current Worker JSON Lines encode/decode boundary.
- Provides `format_worker_event_json_line()` for serializing typed worker events as single-line JSON.
- Provides `parse_worker_event_json_line()` for validating one Worker stdout JSON line into a concrete event model.
- Provides `parse_worker_event_stream()` for validating a minimal stdout lifecycle:
  - `started` must be first.
  - `seq` must be contiguous from 0.
  - `completed` / `failed` must be terminal.
  - no events may appear after a terminal event.
- Raises `WorkerProtocolError` for malformed JSON, non-object JSON, missing/invalid `type`, unknown event types, or invalid event payloads.

Boundary:

- Does not spawn subprocesses.
- Does not read stderr, write logs, or manage stdin control messages.
- Does not read or write SQLite.
- Does not call Scheduler, RuntimeManager, GUI, FFmpeg, model backends, or adapters.
- Does not supervise process lifetime, heartbeat timeout, stdin control, or stderr capture.

### `atelier/workers/runner.py`

Responsibility:

- Defines the current minimum subprocess runner boundary:
  - `WorkerProcessSpec`
  - `WorkerProcessResult`
  - `WorkerLifecycleConfig`
  - `WorkerLifecycleResult`
  - `WorkerProcessProtocolError`
  - `run_worker_process()`
  - `run_worker_lifecycle()`
- Starts a typed command with `--task-file <path>` and `cwd=work_dir`.
- Merges supplied environment variables into the child process environment.
- Captures stdout and validates it through `parse_worker_event_stream()`.
- Captures stderr as text and returns the process exit code.
- Raises `WorkerProcessProtocolError`, a `WorkerProtocolError` subclass that preserves stderr and return code, when stdout violates the Worker JSON Lines protocol.
- Provides the lifecycle runner interface shape: configurable startup/heartbeat/terminate/cancel timeouts and a result object that can express stderr log path, timed out, cancelled, and killed facts.
- `run_worker_lifecycle()` now starts the worker with `subprocess.Popen()`, reads stdout JSON Lines incrementally, treats startup/heartbeat silence as `FailedEvent(error_code="TIMEOUT")`, sends `{"type":"cancel"}` over stdin when the caller-provided cancel event is set, terminates or kills the worker when timeout/cancel handling requires it, and can write stderr to a caller-provided log path.
- On malformed stdout or event-order protocol errors, `run_worker_lifecycle()` terminates or kills the worker before raising `WorkerProcessProtocolError`, preserving stderr/returncode and writing the optional stderr log path.

Boundary:

- Does not choose runtime paths, model paths, command args, or hardware resources.
- Does not call Scheduler, RuntimeManager, GUI, SQLite, FFmpeg, model backends, or adapters.
- Does not implement pause, GUI/Scheduler cancellation wiring, adapter-specific cancellation, retry, or recovery.
- Does not treat nonzero exit code as a protocol error when the Worker emitted a valid terminal event stream.

### `atelier/workers/task_file.py`

Responsibility:

- Defines the current `ExecutionTask -> task.json -> WorkerProcessSpec` bridge.
- Provides `write_worker_task_file()` to serialize a full `ExecutionTask` into a task work directory.
- Writes through a temporary file and atomically replaces the final `task.json`.
- Provides `build_worker_process_spec()` to create a task-specific work directory, write `task.json`, and return a `WorkerProcessSpec`.
- Merges `ExecutionTask.runtime_binding.env` into the worker env; explicit env supplied by the caller overrides duplicate keys.

Boundary:

- Does not start subprocesses.
- Does not claim Scheduler tasks or mutate task status.
- Does not read or write SQLite.
- Does not resolve runtime/model paths; it only serializes bindings already present on the `ExecutionTask`.
- Does not choose command args, hardware resources, retries, recovery, timeout, or cancel policy.

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

### `tests/test_adapter_registry.py`

Responsibility:

- Tests Phase A of `plan_minimal_adapter_probe_workflow.md`.
- Confirms `AdapterRegistry` can register and resolve adapters by `node_type`.
- Confirms duplicate node types and missing node types produce explicit diagnostics.

Boundary:

- Does not run external tools, workers, Scheduler, RuntimeManager, or SQLite.

### `tests/test_app_runtime_setup_service.py`

Responsibility:

- Tests `create_runtime_setup_service(paths)` and `RuntimeSetupAppService`.
- Confirms registering a local `ffmpeg` path writes a runtime profile and returns a refreshed ready snapshot.
- Confirms missing executable paths surface `RuntimeRegistrationError` diagnostics.

Boundary:

- Does not construct Qt widgets.
- Does not run FFmpeg or any external executable.
- Does not test download/install/repair flows.

### `tests/test_command_executor.py`

Responsibility:

- Tests Phase B of `plan_minimal_adapter_probe_workflow.md`.
- Confirms `CommandSpec` uses executable + args list + cwd + env.
- Confirms `run_command()` captures stdout/stderr/return code facts and exposes redacted command metadata.
- Confirms nonzero command exits raise `CommandExecutionError` with stderr and redacted command facts.

Boundary:

- Does not test ffprobe-specific arguments or AdapterRegistry.
- Does not use `shell=True`.

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
- Does not cover Runtime Setup action behavior; that lives in `tests/test_app_runtime_setup_service.py`.

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

### `tests/test_worker_protocol.py`

Responsibility:

- Tests Phase A and Phase B of `plan_worker_protocol_runner.md`.
- Confirms Worker events serialize to newline-terminated JSON Lines.
- Confirms JSON Lines parse back into concrete event models, including `completed`, `log`, `heartbeat`, and `started`.
- Confirms malformed JSON, non-object JSON, and unknown event types raise `WorkerProtocolError`.
- Confirms valid Worker event streams start with `started`, use contiguous `seq`, and end with `completed` / `failed`.
- Confirms invalid event streams fail when they miss `started`, skip `seq`, omit terminal event, or append events after terminal state.

Boundary:

- Does not test subprocess runner behavior.
- Does not execute real external tools or write worker artifacts.

### `tests/test_worker_runner.py`

Responsibility:

- Tests Phase C of `plan_worker_protocol_runner.md`.
- Uses temporary Python stub workers to verify `run_worker_process()` passes `--task-file`, `cwd`, and environment variables.
- Confirms stdout JSON Lines are parsed into worker events.
- Confirms stderr text and nonzero exit codes are captured.
- Confirms malformed stdout raises `WorkerProtocolError`.

Boundary:

- Does not run real FFmpeg/model adapters.
- Does not test Scheduler integration, RuntimeManager path resolution, stdin cancel, heartbeat timeout, kill escalation, or stderr file persistence.

### `tests/test_worker_lifecycle.py`

Responsibility:

- Tests Phase A of `plan_worker_lifecycle_controls.md`.
- Verifies `run_worker_lifecycle()` exposes a lifecycle result shape while preserving existing stub worker execution behavior.
- Confirms the Phase A result can report events, stderr text, return code, stderr log path, timed out, cancelled, and killed facts.
- Tests Phase B silent worker timeout and heartbeat keep-alive behavior.
- Tests Phase C cancel-aware worker handling and termination of a worker that ignores cancel.
- Tests Phase D stderr log file persistence while preserving stdout JSON Lines as the event source.
- Tests Phase F protocol-error process termination and stderr log persistence.

Boundary:

- Does not test pause, GUI/Scheduler cancellation wiring, adapter-specific cancellation, Scheduler dispatch, or SQLite persistence.

### `tests/test_worker_task_file.py`

Responsibility:

- Tests Phase E of `plan_worker_protocol_runner.md`.
- Confirms `write_worker_task_file()` writes `task.json` with `ExecutionTask` fields, resource binding, and runtime binding.
- Confirms `build_worker_process_spec()` creates a task work directory, writes `task.json`, preserves command args, and merges runtime env with caller env overrides.

Boundary:

- Does not start subprocesses.
- Does not test Scheduler integration, RuntimeManager path resolution, real adapters, timeout, cancel, or SQLite persistence.

### `tests/test_runtime_manager.py`

Responsibility:

- Tests resolving runtime bindings from in-memory manifests.
- Tests missing runtime component failure.
- Tests scoped runtime env merging.
- Tests diagnostic `RuntimeResolutionError` for disabled runtimes, capability mismatch, and missing model assets.

Boundary:

- Does not check filesystem health or package integrity.

### `tests/test_runtime_registration.py`

Responsibility:

- Tests Phase B of `plan_runtime_management_foundation.md`.
- Verifies local `ffprobe` / `ffmpeg` executable profile registration.
- Verifies `python.worker-dev` development Worker Python profile registration.
- Verifies local demo model directory profile registration.
- Verifies empty path, missing path, path traversal, duplicate runtime id, and duplicate model id rejection.

Boundary:

- Does not health-check executables or run dry-run commands.
- Does not copy binaries or model files.
- Does not test GUI runtime setup actions.

### `tests/test_runtime_setup_snapshot.py`

Responsibility:

- Tests Phase E of `plan_runtime_management_foundation.md`.
- Verifies `build_runtime_setup_snapshot()` creates GUI-readable runtime/model health snapshots from `RuntimeStore` and `RuntimeHealthChecker`.
- Verifies snapshot counts, ready/problem status, issues, repair hints, runtime capabilities, and model task types.

Boundary:

- Does not render PySide6 widgets.
- Does not register, install, repair, or execute runtimes.

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

### `tests/test_backend_workflow_handoff.py`

Responsibility:

- Tests Phase A of `plan_minimal_backend_workflow_runner.md`.
- Confirms `fetch_task_output_artifacts()` returns persisted role=`output` artifact links for an upstream task.
- Confirms artifact type filtering works without scanning the filesystem.

Boundary:

- Does not materialize downstream params, run Scheduler dispatch loops, start worker subprocesses, or touch GUI.

### `tests/test_scheduler_worker_runner_integration.py`

Responsibility:

- Tests Phase A, Phase B, and Phase C of `plan_scheduler_worker_runner_integration.md`.
- Tests Phase A of `plan_scheduler_lifecycle_dispatch_integration.md`.
- Confirms `dispatch_claimed_task()` accepts an already claimed task, writes a `task.json` with the Scheduler-provided resource binding, runs a temporary stub worker command, records returned events, preserves stderr/return code in the dispatch result, and reports the final SQLite task status.
- Confirms `dispatch_claimed_task()` can use lifecycle runner options and return stderr log path plus lifecycle flags on a completed stub worker path.
- Confirms lifecycle dispatch timeout records `TIMEOUT`, marks the task failed, preserves stderr log path, and releases the active resource lock.
- Confirms lifecycle dispatch cancellation records `CANCELLED`, normalizes the task status to `cancelled`, and releases the active resource lock for both cancel-aware and stuck workers.
- Confirms lifecycle dispatch protocol errors preserve stderr log details, record an internal failed event, and release the active resource lock.
- Confirms a completed stub worker path records `started -> artifact -> completed` events, writes artifact rows, links `task_artifacts`, marks the task completed, and releases the active resource lock.
- Confirms a valid failed worker stream records failure facts, marks the task failed, preserves stderr/return code, and releases the active resource lock.
- Confirms malformed stdout is converted to an internal failed event instead of escaping as an unpersisted protocol exception.

Boundary:

- Does not test retry/recovery action execution, GUI cancellation wiring, automatic claim loops, real adapters, or GUI execution.

### `tests/test_resource_locks.py`

Responsibility:

- Tests Phase A, Phase B, and Phase D of `plan_resource_locks_failure_recovery.md`.
- Confirms `SimpleScheduler.claim_next_task()` creates an active `resource_locks` row.
- Confirms the active lock records task id, device id, lock type, VRAM field, acquisition timestamp, and unreleased state.
- Confirms completed, cancelled, and failed terminal worker events release active resource locks.
- Confirms stale resource locks can be detected by `stale_after` and released without automatically changing task status.
- Confirms stale release rejects locks that are not stale yet or were already released.

Boundary:

- Does not test failure recovery options.
- Does not test crash recovery scans or automatic task recovery.

### `tests/test_failure_recovery.py`

Responsibility:

- Tests Phase C of `plan_resource_locks_failure_recovery.md`.
- Confirms recoverable failed tasks expose `error_code`, `error_message`, recoverable state, and partial artifact paths.
- Confirms recoverable failed tasks receive retry and use-partial-artifacts recovery options.
- Confirms non-recoverable failed tasks do not receive retry and instead expose read-only inspect/export options.

Boundary:

- Does not execute recovery actions.
- Does not test stale lock detection.
- Does not test GUI failure panels.

### `tests/test_artifact_finalizer_adapter.py`

Responsibility:

- Tests Phase A of `plan_output_export_finalizer.md`.
- Confirms `ArtifactFinalizerAdapter` copies a staged artifact to the requested output directory, verifies size/hash, and returns a final output artifact.
- Confirms default filename behavior, output conflict handling, unsafe filename rejection, and missing input mapping.

Boundary:

- Does not run worker subprocesses.
- Does not write SQLite.
- Does not test GUI export dialogs or FFmpeg format conversion.

### `tests/test_ffmpeg_audio_extract_adapter.py`

Responsibility:

- Tests Phase A of `plan_ffmpeg_audio_extract_adapter.md`.
- Confirms `FFmpegAudioExtractAdapter` reads `ffmpeg` from `RuntimeBinding`, builds the expected FFmpeg argument list, writes a staged `audio.wav`, and returns an audio artifact.
- Confirms missing runtime path, missing input path, FFmpeg command failure, and command success without output map to structured adapter failures.

Boundary:

- Uses an injected command runner for adapter behavior tests.
- Does not require a real FFmpeg installation.
- Does not write SQLite or run Scheduler.

### `tests/test_ffprobe_metadata_adapter.py`

Responsibility:

- Tests Phase C of `plan_minimal_adapter_probe_workflow.md`.
- Confirms `FFprobeMetadataAdapter` reads `ffprobe` from `RuntimeBinding`, builds the expected ffprobe argument list, parses JSON, writes `probe.json`, and returns a metadata artifact.
- Confirms missing runtime path, missing input path, and invalid ffprobe JSON map to structured adapter failures.

Boundary:

- Uses an injected command runner for adapter behavior tests.
- Does not require a real FFmpeg installation.
- Does not write SQLite or run Scheduler.

### `tests/test_gui_app_entry.py`

Responsibility:

- Tests Phase F of `plan_readonly_pyside6_workbench.md`.
- Confirms launch argument parsing for `--workspace-root` and `--no-restore-layout`.
- Confirms launch context construction creates a `MainWindow`, reads an empty snapshot, and does not enter the Qt event loop.
- Confirms launch context reads runtime setup manifests into the Runtime Setup dock.

Boundary:

- Does not perform long-running GUI execution.
- Does not run Scheduler, workers, FFmpeg/model adapters, or recovery actions.
- Skips when PySide6 is not installed.

### `tests/test_gui_optional_dependency.py`

Responsibility:

- Tests Phase A of `plan_readonly_pyside6_workbench.md`.
- Confirms GUI entry helpers can be imported when PySide6 is not installed.
- Confirms missing PySide6 errors point to the documented `.[gui]` install command.

Boundary:

- Does not install PySide6.
- Does not construct a `QApplication` or `MainWindow`.
- Does not test GUI layout or SQLite state rendering.

### `tests/test_gui_layout_store.py`

Responsibility:

- Tests Phase E of `plan_readonly_pyside6_workbench.md`.
- Confirms `WorkspaceLayoutStore` round-trips geometry/state bytes.
- Confirms missing layout names return `None`.
- Confirms layout persistence uses `AppPaths.workspace_layouts_path`.

Boundary:

- Does not import PySide6.
- Does not test real dock movement.
- Does not test complex workspace presets.

### `tests/test_gui_runtime_setup.py`

Responsibility:

- Tests Phase B and Phase C of `plan_initial_actionable_gui_runtime_setup.md`.
- Constructs `MainWindow` in offscreen Qt and confirms the Runtime Setup dock renders runtime snapshots.
- Confirms Runtime Setup panel actions call the app service, refresh displayed snapshot state, and show registration errors.

Boundary:

- Does not run FFmpeg, workers, Scheduler, or model inference.
- Does not test native file dialog interaction directly; tests call the same panel action methods with explicit paths.
- Skips when PySide6 is not installed.

### `tests/test_gui_runtime_setup_state.py`

Responsibility:

- Tests Phase A of `plan_initial_actionable_gui_runtime_setup.md`.
- Confirms PySide-independent Runtime Setup view state exposes summary counts, component/model display rows, status labels, detail lines, and action enabled state.

Boundary:

- Does not import PySide6.
- Does not read or write runtime manifests.
- Does not run health checks or registration actions.

### `tests/test_gui_smoke.py`

Responsibility:

- Tests Phase B and the visible part of Phase C for `plan_readonly_pyside6_workbench.md`.
- Constructs `QApplication` in offscreen mode and creates `MainWindow` without entering the event loop.
- Confirms the five current dock areas exist and remain movable/floatable.
- Confirms Queue panel can render task id, status, resource device, and artifact path from a `WorkbenchSnapshot`.
- Skips GUI smoke tests when PySide6 is not installed, preserving the optional dependency boundary.
- Confirms `MainWindow` can save and restore workspace layout through `WorkspaceLayoutStore`.

Boundary:

- Does not start a long-running Qt event loop.
- Does not perform screenshot-level visual verification.
- Does not execute Scheduler or worker tasks.

### `tests/test_gui_state_reader.py`

Responsibility:

- Tests Phase C of `plan_readonly_pyside6_workbench.md`.
- Builds a temporary SQLite state through existing workflow/planning/scheduler/worker test helpers.
- Confirms `read_workbench_snapshot()` returns task id, node type, status, resource device, event count, and artifact paths for GUI consumption.

Boundary:

- Does not construct Qt widgets.
- Does not write GUI state.
- Does not execute real external tools.

### `tests/test_minimal_audio_extract_workflow.py`

Responsibility:

- Tests Phase B of `plan_ffmpeg_audio_extract_adapter.md`.
- Confirms the adapter worker entrypoint can run `media.audio_extract` from a task file, invoke a fake FFmpeg executable, emit `started -> artifact -> completed`, and let `dispatch_claimed_task()` persist task events, audio artifact rows, and completed task status.
- Confirms failing fake FFmpeg output emits `started -> failed` and persists structured `DEPENDENCY` failure facts.

Boundary:

- Uses a fake `ffmpeg.cmd` executable, not a system FFmpeg installation.
- Does not implement GUI trigger, no-audio policy, final export, production retry/recovery execution, or multi-worker concurrency.

### `tests/test_minimal_probe_workflow.py`

Responsibility:

- Tests Phase D and Phase E of `plan_minimal_adapter_probe_workflow.md`.
- Confirms the adapter worker entrypoint can run `metadata.probe` from a task file, invoke a fake ffprobe executable, emit `started -> artifact -> completed`, and let `dispatch_claimed_task()` persist task events, metadata artifact rows, and completed task status.
- Confirms malformed fake ffprobe output emits `started -> failed` and persists structured `DEPENDENCY` failure facts.
- Confirms the RuntimeManager-produced `RuntimeBinding` is present in worker `task.json`.

Boundary:

- Uses a fake `ffprobe.cmd` executable, not a system FFmpeg installation.
- Does not implement GUI trigger, final export, production retry/recovery execution, or multi-worker concurrency.

### `tests/test_output_export_workflow.py`

Responsibility:

- Tests Phase B of `plan_output_export_finalizer.md`.
- Confirms the adapter worker entrypoint can run `output.export` from a task file, copy an existing staged artifact, emit `started -> artifact -> completed`, and let `dispatch_claimed_task()` persist final output artifact rows.
- Confirms `task_artifacts` stores role `final_output` when Worker artifact metadata declares `role=final_output`.
- Confirms output conflicts emit `started -> failed` and persist structured `OUTPUT_CONFLICT` failure facts.

Boundary:

- Uses an existing temporary staged file, not a real upstream media adapter.
- Does not implement GUI trigger, batch export, overwrite UI, move semantics, mux/burn, or format conversion.

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
- `scheduler/`: `SimpleScheduler`, a narrow claimed-task dispatch helper, and the first storage-backed artifact handoff query exist; lifecycle timeout/cancel/protocol-error results can be persisted for already claimed stub tasks, but durable queue claiming, full dispatch loops, downstream param materialization, priorities, concurrency, retry execution, protocol-error retry/recovery actions, and crash recovery are not implemented.
- `gui/`: optional dependency entry helpers, formal development launch entry, a `MainWindow`, basic dock workspace specs, minimal layout persistence, read-only SQLite view models, and a minimal actionable Runtime Setup dock exist; real canvases, workflow editing, theme system, i18n catalog, workspace preset UI, packaged app entry, and visual verification are not implemented yet.
- `atelier/domain/translation.py`: translation / OCR fusion / structured subtitle output models described by `docs/TRANSLATE_AGENT_SPEC.md`.
- `atelier/translation/`: input resolver, timeline builder, OCR context aligner, chunk planner, prompt builder, provider clients, result validator, repair runner, and subtitle rebuilder described by `docs/TRANSLATE_AGENT_SPEC.md`.
- `adapters`: minimal adapter contract, built-in registry, typed command executor, `metadata.probe` / `FFprobeMetadataAdapter`, `media.audio_extract` / `FFmpegAudioExtractAdapter`, and `output.export` / `ArtifactFinalizerAdapter` exist; subtitle mux/burn, ASR, OCR recognition, Translate Agent, subtitle review, composition, enhancement, plugin adapter discovery, and production adapter cancellation are not implemented.
- `workers/task_file`: `ExecutionTask -> task.json -> WorkerProcessSpec` bridge exists; the first claimed-task dispatch seam uses it from Scheduler, including lifecycle timeout/cancel/protocol-error result persistence for stub workers, while production worker lifecycle orchestration is not implemented.
- `workers/adapter_entry`: first built-in adapter worker entrypoint exists for task-file based `metadata.probe`, `media.audio_extract`, and `output.export`; plugin adapters, GUI trigger, and broader production adapter orchestration are not implemented.
- `workers/runner`: minimum subprocess boundary plus lifecycle interface, incremental stdout reading, startup/heartbeat timeout handling, timeout/cancel/protocol-error terminate-kill behavior, minimal stdin cancel control, and optional stderr log file persistence exist; pause, GUI/Scheduler cancellation wiring, adapter-specific cancellation, and full production worker lifecycle behavior are not implemented.
- `storage/repositories/`: minimal Phase 6 persistence, Phase 7 queue helpers, resource lock persistence/release/stale detection, failure fact/recovery option queries, and a first `fetch_task_output_artifacts()` handoff query exist; durable repository APIs are not complete.
- `runtime` advanced pieces: real runtime import, install, automatic dry-run selection, backend compatibility, model store operations, and repair flows.
- `release` implementation: update manifests, staging, rollback.
- `plugins` implementation: manifest validation, contribution registry, isolation.
- `i18n` implementation: catalog loading and runtime locale switching.
