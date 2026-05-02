# Atelier Recent Changes

> This file records meaningful project changes for future AI agents and developers. It is intentionally more durable than chat history. Keep entries concise, factual, and anchored to files or behavior that exists.

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
