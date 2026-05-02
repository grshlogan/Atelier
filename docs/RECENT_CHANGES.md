# Atelier Recent Changes

> This file records meaningful project changes for future AI agents and developers. It is intentionally more durable than chat history. Keep entries concise, factual, and anchored to files or behavior that exists.

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
