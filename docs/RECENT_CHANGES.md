# Atelier Recent Changes

> This file records meaningful project changes for future AI agents and developers. It is intentionally more durable than chat history. Keep entries concise, factual, and anchored to files or behavior that exists.

## 20260503_084529 [执行只读 PySide6 工作台 Phase A-D]

- Started execution of `docs/plan/plan_readonly_pyside6_workbench.md` after completing the resource locks / failure recovery plan.
- Added `tests/test_gui_optional_dependency.py` before implementation and confirmed the first failure was `ModuleNotFoundError: No module named 'atelier.gui'`.
- Added `atelier/gui/__init__.py` and `atelier/gui/entry.py`.
- Added `check_gui_dependency()` and `ensure_gui_dependency()` so GUI entry code can be imported without PySide6 installed and missing GUI extras produce a clear install command.
- Kept PySide6 as an optional dependency under `pyproject.toml` `gui` extras; it is not a core hard dependency.
- Installed GUI extras in the local development `.venv` with `.venv/Scripts/python -m pip install -e ".[gui]"`; PySide6 6.11.0 is now available locally.
- Added `tests/test_gui_smoke.py` before implementation and confirmed the first failure was missing `atelier.gui.main_window`.
- Added `atelier/gui/main_window.py` and `atelier/gui/workspace.py` with a read-only `QMainWindow` shell and workflow / execution / queue / resources-runtime docks.
- Added `tests/test_gui_state_reader.py` before implementation and confirmed the first failure was missing `atelier.gui.state_reader`.
- Added `atelier/gui/state_reader.py` with `WorkbenchSnapshot`, `WorkbenchTaskItem`, and `read_workbench_snapshot()`.
- Updated `MainWindow` so Queue panel can render task id, node type, status, resource device, event count, and artifact path from a `WorkbenchSnapshot`.
- Updated `docs/APP_CODE_MAP.md`, `docs/plan/plan_main_app_skeleton.md`, `docs/plan/plan_readonly_pyside6_workbench.md`, and `README.md`.

Current GUI boundary:

- Implemented: optional GUI dependency detection, read-only `MainWindow`, four dockable workstation panels, read-only SQLite view model, and offscreen construction tests.
- Not implemented: real Workflow Canvas drawing/editing, task start actions, Scheduler/worker control from GUI, theme system, i18n catalog, dock layout persistence, screenshot-level visual verification, or real runtime/model panels.

Validation run:

```powershell
.venv/Scripts/python -m pip install -e ".[gui]"
.venv/Scripts/python -m unittest tests.test_gui_optional_dependency
.venv/Scripts/python -m unittest tests.test_gui_smoke
.venv/Scripts/python -m unittest tests.test_gui_state_reader
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m pip install -e ".[gui]"`: passed; PySide6 6.11.0 installed in local `.venv`.
- `.venv/Scripts/python -m unittest tests.test_gui_optional_dependency`: 2 tests passed.
- `.venv/Scripts/python -m unittest tests.test_gui_smoke`: 2 tests passed.
- `.venv/Scripts/python -m unittest tests.test_gui_state_reader`: 1 test passed.
- `.venv/Scripts/python -m unittest discover -s tests`: 36 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_080447 [执行 resource locks Phase D]

- Extended `tests/test_resource_locks.py` before implementation and confirmed the first failure was the missing `fetch_stale_resource_locks` repository helper.
- Added `StaleResourceLockRecord`, `fetch_stale_resource_locks()`, and `release_stale_resource_lock()` in `atelier/storage/repositories.py`.
- Stale detection now returns unreleased locks whose `stale_after` timestamp is older than or equal to the supplied `now`.
- Stale release marks the lock released by `lock_id` and leaves the task status unchanged, preserving crash recovery as a later explicit decision.
- Added guard coverage confirming stale release rejects locks that are not stale yet or were already released.
- Updated `docs/APP_CODE_MAP.md`, `docs/plan/plan_main_app_skeleton.md`, and `docs/plan/plan_resource_locks_failure_recovery.md`.

Current Phase D boundary:

- Implemented: stale resource lock detection, explicit stale lock release, and release guards for non-stale/already-released locks.
- Not implemented: crash recovery scan orchestration, retry execution, worker subprocess supervision, or GUI recovery panels.

Validation run:

```powershell
.venv/Scripts/python -m unittest tests.test_resource_locks
.venv/Scripts/python -m unittest tests.test_failure_recovery
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest tests.test_resource_locks`: 6 tests passed.
- `.venv/Scripts/python -m unittest tests.test_failure_recovery`: 2 tests passed.
- `.venv/Scripts/python -m unittest discover -s tests`: 31 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_075217 [执行 resource locks Phase C]

- Added `tests/test_failure_recovery.py` before implementation and confirmed the first failure was the missing `fetch_failure_facts` repository helper.
- Added `FailureFacts`, `RecoveryOption`, `fetch_failure_facts()`, and `suggest_recovery_options()` in `atelier/storage/repositories.py`.
- Updated `record_worker_events()` so `FailedEvent.partial_artifacts` are persisted as `partial` artifacts linked through `task_artifacts`.
- Updated terminal failure persistence so `execution_tasks.error_code` and `execution_tasks.error_message` are populated from `FailedEvent`.
- Updated `docs/APP_CODE_MAP.md`, `docs/plan/plan_main_app_skeleton.md`, and `docs/plan/plan_resource_locks_failure_recovery.md`.

Current Phase C boundary:

- Implemented: failed task facts, partial artifact path query, recoverable retry/use-partial suggestions, and non-recoverable inspect/export suggestions.
- Not implemented yet: stale lock detection, retry execution, GUI recovery panels, and real worker subprocess recovery.

Validation run:

```powershell
.venv/Scripts/python -m unittest tests.test_resource_locks
.venv/Scripts/python -m unittest tests.test_failure_recovery
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest tests.test_resource_locks`: 4 tests passed.
- `.venv/Scripts/python -m unittest tests.test_failure_recovery`: 2 tests passed.
- `.venv/Scripts/python -m unittest discover -s tests`: 29 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_073409 [执行 resource locks Phase A]

- Started execution of `docs/plan/plan_resource_locks_failure_recovery.md`.
- Added `tests/test_resource_locks.py` before implementation and confirmed the first failure was missing `fetch_active_resource_lock`.
- Added `ResourceLockRecord` and `fetch_active_resource_lock()` in `atelier/storage/repositories.py`.
- Updated `mark_task_running()` so Scheduler claim now creates an active `resource_locks` row in the same claim path.
- Updated `docs/APP_CODE_MAP.md` and `docs/plan/plan_resource_locks_failure_recovery.md`.

Current Phase A boundary:

- Implemented: Scheduler claim creates a queryable active resource lock.
- Not implemented yet: terminal event lock release, failure facts, recovery options, stale lock detection.

Validation run:

```powershell
.venv/Scripts/python -m unittest tests.test_resource_locks
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest tests.test_resource_locks`: passed.
- `.venv/Scripts/python -m unittest discover -s tests`: 24 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_074057 [执行 resource locks Phase B]

- Extended `tests/test_resource_locks.py` before implementation to cover terminal event lock release for:
  - `CompletedEvent`
  - `FailedEvent(error_code="CANCELLED")`
  - ordinary recoverable `FailedEvent`
- Confirmed the expected red state: task status was updated but active locks were not released.
- Updated `record_worker_events()` terminal event path in `atelier/storage/repositories.py` so active resource locks are released after task status is updated.
- Updated `docs/plan/plan_resource_locks_failure_recovery.md`.

Current Phase B boundary:

- Implemented: completed / cancelled / failed terminal events release active locks.
- Not implemented yet: failed task facts, recovery options, stale lock detection.

Validation run:

```powershell
.venv/Scripts/python -m unittest tests.test_resource_locks
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest tests.test_resource_locks`: 4 tests passed.
- `.venv/Scripts/python -m unittest discover -s tests`: 27 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_072200 [分发后续两个子计划]

- Added `docs/plan/plan_resource_locks_failure_recovery.md`.
  - Execution order: first.
  - Scope: resource locks, terminal event lock release, failure facts, recovery options, stale lock detection.
  - Boundary: no real worker subprocesses, no production multi-process locking, no GUI recovery panel.
- Added `docs/plan/plan_readonly_pyside6_workbench.md`.
  - Execution order: second.
  - Scope: read-only PySide6 workbench shell that renders existing SQLite / runtime / queue state.
  - Boundary: no heavy task execution in GUI, no real Workflow Canvas editing, no FFmpeg/model work.
- Updated `docs/plan/plan_main_app_skeleton.md` Child Plans to link both sub-plans and record the intended execution order.

Validation run:

```powershell
git diff --check
```

Result:

- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_065626 [完成 Phase 7 最小 queue / Scheduler claim]

- Added `atelier/scheduler/simple.py` with `SimpleScheduler` and `ClaimedTask`.
- Added minimum queue helpers to `atelier/storage/repositories.py`:
  - `fetch_next_runnable_task()`
  - `mark_task_running()`
  - `fetch_task_resource_binding()`
- `SimpleScheduler` now finds dependency-ready pending tasks, creates a `ResourceBinding`, and marks the task as `running`.
- Added `tests/test_scheduler_simple.py` before implementation and confirmed the first failure was `ModuleNotFoundError: No module named 'atelier.scheduler'`.
- Updated `README.md`, `docs/ARCHITECTURE.md`, `docs/APP_CODE_MAP.md`, and `docs/plan/plan_main_app_skeleton.md`.

Current Phase 7 boundary:

- Implemented: dependency-ready pending task claim, CPU resource binding, persisted `running` task status, persisted `ResourceBinding`.
- Not implemented: durable multi-process queue claiming, resource locks, priorities, concurrency, retries, failure recovery actions, real worker subprocess dispatch.

Validation run:

```powershell
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest discover -s tests`: 23 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_064008 [完成 Phase 6 最小业务闭环]

- Added minimal workflow graph models in `atelier/workflow/graph.py`:
  - `WorkflowGraph`
  - `WorkflowNode`
  - `WorkflowEdge`
  - `WorkflowPortRef`
- Added `ExecutionPlan` to `atelier/domain/execution_plan.py` and added default `phase_id` / `lane_id` to `ExecutionTask`.
- Added `build_linear_execution_plan()` in `atelier/planning/simple.py`.
- Added minimal SQLite persistence helpers in `atelier/storage/repositories.py`:
  - `persist_planned_execution()`
  - `record_worker_events()`
  - `fetch_task_event_types()`
  - `fetch_artifact_paths()`
  - `fetch_task_status()`
- Added `tests/test_phase6_minimal_loop.py` before implementation and confirmed the first failure was `ModuleNotFoundError: No module named 'atelier.planning'`.
- Added `tests/test_planning_simple.py` for simple planner behavior and empty graph rejection.
- Updated `README.md`, `docs/ARCHITECTURE.md`, `docs/APP_CODE_MAP.md`, and `docs/plan/plan_main_app_skeleton.md` to reflect that Phase 6 now has a first working minimum loop.

Current Phase 6 boundary:

- Implemented: `WorkflowGraph -> ExecutionPlan -> simulated Worker -> SQLite events/artifacts`.
- Not implemented: queue claiming, Scheduler, resource locks, real worker subprocesses, real adapters, failure recovery actions, GUI queue monitor.

Validation run:

```powershell
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest discover -s tests`: 22 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_062834 [按 AGENTS 规则中文化主计划]

- Reviewed `AGENTS.md` Planning Discipline against `docs/plan/plan_main_app_skeleton.md`.
- Confirmed the plan already used the correct location, main-plan filename prefix, and the required nine-section structure.
- Rewrote `docs/plan/plan_main_app_skeleton.md` in Chinese while preserving the AGENTS-required section skeleton through bilingual headings.
- Updated stale plan facts:
  - Current local Python is `Python 3.11.9`.
  - `.venv/` editable install exists.
  - Current validation baseline is 19 passing unittest tests.
  - `AppPaths` and app-level `create_runtime_store()` / `open_app_database()` exist.
- Added Phase 6 for the next minimum business loop: `WorkflowGraph -> ExecutionPlan -> simulated Worker -> SQLite events/artifacts`.

Validation run:

```powershell
git diff --check
.venv/Scripts/python -m unittest discover -s tests
```

Result:

- `git diff --check`: passed with only Windows CRLF conversion warnings.
- `.venv/Scripts/python -m unittest discover -s tests`: 19 tests passed.

## 20260503_062202 [接入 AppPaths 到 RuntimeStore 与 SQLite]

- Added `atelier/app/services.py` as app-level orchestration glue.
- Added `create_runtime_store(paths)` to create `RuntimeStore` from `AppPaths.data_root` after ensuring the shared data layout exists.
- Added `open_app_database(paths)` to open `AppPaths.database_path` and initialize the SQLite schema.
- Kept `runtime/` and `storage/` independent from `app/`; app layer performs the wiring.
- Added `tests/test_app_services.py` before implementation and confirmed the initial failure was `ModuleNotFoundError: No module named 'atelier.app.services'`.
- Fixed the SQLite test to close the connection explicitly because `sqlite3.Connection` as a context manager does not release the file handle on Windows.
- Updated `docs/APP_CODE_MAP.md` to include `atelier/app/services.py`, `tests/test_app_services.py`, and the new code file count.
- Updated `docs/plan/plan_main_app_skeleton.md` with Phase 5 for AppPaths integration.

Validation run:

```powershell
.venv/Scripts/python -m unittest tests.test_app_services
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `tests/test_app_services.py` passed after adding app-level factories and explicit SQLite connection close in the test.
- Final `.venv/Scripts/python -m unittest discover -s tests`: 19 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_060137 [建立开发 venv 与 AppPaths 路径管理]

- Created local `.venv/` for development and installed Atelier in editable mode with `.venv/Scripts/python -m pip install -e .`.
- Verified the current suite inside `.venv/` before adding new path code.
- Added `atelier/app/paths.py` with `AppPaths`:
  - `for_development(workspace_root)` resolves local development data to `.atelier/AtelierData`.
  - `from_data_root(data_root)` supports release/user-data roots supplied by future installers or settings.
  - Standard path properties cover runtime/model manifests, database, runtimes, models, plugins, cache, staging, and logs.
  - `ensure_data_dirs()` creates the shared local data directory layout without creating `.venv/`.
- Added `tests/test_app_paths.py` before implementation and confirmed the initial failure was `ModuleNotFoundError: No module named 'atelier.app.paths'`.
- Updated `docs/APP_CODE_MAP.md` to include `atelier/app/paths.py`, `tests/test_app_paths.py`, and the new code file count.

Validation run:

```powershell
.venv/Scripts/python -m pip install -e .
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- Editable install succeeded in `.venv/`.
- Existing suite passed in `.venv/` before `AppPaths`.
- `tests/test_app_paths.py` failed first for the expected missing module.
- `tests/test_app_paths.py` passed after adding `AppPaths`.
- Final `.venv/Scripts/python -m unittest discover -s tests`: 17 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_055526 [明确开发 venv 与 runtime 目录边界]

- Clarified the three environment layers in `docs/RUNTIME_ENVIRONMENT_SPEC.md`:
  - App Install Dir for packaged GUI runtime, PySide6, Qt plugins, DLLs, and application code.
  - AtelierData Dir for managed tool/backend/worker runtimes, models, plugins, cache, staging, logs, and database.
  - Dev Workspace for source code, `.venv/`, test caches, and developer-local `.atelier/AtelierData`.
- Documented that `atelier/runtime/` is source code for runtime management and must not store runtime binaries or virtual environments.
- Added `.venv/`, `venv/`, and `.atelier/` to `.gitignore`.
- Updated `docs/APP_CODE_MAP.md` with environment directory boundaries and `.gitignore` responsibilities.

Validation run:

```powershell
git diff --check
```

Result:

- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_050504 [首版 Python 骨架、runtime 基础与接手文档]

- Started the first executable Python skeleton after the documentation baseline commits `cdadba9` and `6316a75`.
- Added `pyproject.toml` with package metadata, Python version constraints, `pydantic` dependency, and planned optional groups for `dev`, `gui`, `scheduler`, and `storage`.
- Added `atelier/` package boundaries:
  - `app/` for future boot orchestration.
  - `core/` for small shared utilities.
  - `domain/` for pure pydantic execution/resource/runtime/worker-event models.
  - `runtime/` for managed runtime manifests, store, binding resolution, and health checks.
  - `security/` for package integrity helpers.
  - `storage/` for SQLite schema initialization.
  - `workers/` for a simulated worker event path.
  - `hardware/`, `i18n/`, `plugins/`, and `release/` as side-effect-free placeholder packages.
- Added `RuntimeStore` in `atelier/runtime/store.py` to persist local runtime and model manifests under an `AtelierData`-style directory layout.
- Added `RuntimeHealthChecker` in `atelier/runtime/health.py` to check declared component/model paths and SHA-256 mismatch states without touching global `PATH`.
- Added `sha256_file()` and `verify_sha256()` in `atelier/security/package_integrity.py`.
- Updated `RuntimeManager` so it can resolve from manifests loaded by `RuntimeStore`.
- Added first unittest coverage:
  - worker terminal status normalization.
  - runtime binding resolution.
  - runtime manifest store persistence.
  - runtime health path/hash checks.
  - package SHA-256 verification.
  - SQLite core table creation.
  - simulated worker event ordering.
- Added Python cache/build exclusions to `.gitignore`.
- Updated `README.md`, `docs/ARCHITECTURE.md`, and `docs/plan/plan_main_app_skeleton.md` so they no longer describe the skeleton/runtime layer as not started or empty.
- Added `docs/APP_CODE_MAP.md` as the current code tree and responsibility map.
- Added this `docs/RECENT_CHANGES.md` file as the durable change memory.

Validation run:

```powershell
python -m unittest discover -s tests
python -m compileall -q atelier tests
git diff --check
```

Result:

- `python -m unittest discover -s tests`: 14 tests passed.
- `python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

Known boundaries after this change:

- No real GUI exists yet.
- No real Scheduler exists yet.
- No real WorkflowGraph to ExecutionPlan planner exists yet.
- No real FFmpeg/model adapters exist yet.
- No SQLAlchemy repositories or migrations exist yet.
- No package download/install/update chain exists yet.
- Runtime health checks are local path/hash checks only; executable dry-run, backend compatibility, and repair flows are future work.
