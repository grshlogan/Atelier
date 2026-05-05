from __future__ import annotations

from pydantic import BaseModel, Field

from atelier.runtime.health import RuntimeHealthChecker
from atelier.runtime.manifest import RuntimeStatus
from atelier.runtime.store import RuntimeStore


class RuntimeComponentSnapshot(BaseModel):
    runtime_id: str
    component: str
    display_name: str = ""
    version: str = ""
    kind: str = ""
    profile_kind: str = ""
    status: RuntimeStatus
    capabilities: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    repair_hints: list[str] = Field(default_factory=list)
    checked_paths: dict[str, str] = Field(default_factory=dict)


class ModelAssetSnapshot(BaseModel):
    model_id: str
    display_name: str = ""
    model_family: str = ""
    backend: str = ""
    version: str = ""
    profile_kind: str = ""
    status: RuntimeStatus
    task_types: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    repair_hints: list[str] = Field(default_factory=list)
    checked_paths: dict[str, str] = Field(default_factory=dict)


class RuntimeSetupSnapshot(BaseModel):
    runtimes: list[RuntimeComponentSnapshot] = Field(default_factory=list)
    models: list[ModelAssetSnapshot] = Field(default_factory=list)

    @property
    def runtime_count(self) -> int:
        return len(self.runtimes)

    @property
    def model_count(self) -> int:
        return len(self.models)

    @property
    def ready_runtime_count(self) -> int:
        return sum(1 for runtime in self.runtimes if runtime.status == "ready")

    @property
    def problem_count(self) -> int:
        runtime_problems = sum(1 for runtime in self.runtimes if runtime.status != "ready")
        model_problems = sum(1 for model in self.models if model.status != "ready")
        return runtime_problems + model_problems


def build_runtime_setup_snapshot(
    store: RuntimeStore,
    checker: RuntimeHealthChecker,
) -> RuntimeSetupSnapshot:
    runtimes: list[RuntimeComponentSnapshot] = []
    for manifest in store.load_runtime_manifests():
        report = checker.check_runtime(manifest)
        runtimes.append(
            RuntimeComponentSnapshot(
                runtime_id=manifest.runtime_id,
                component=manifest.component,
                display_name=manifest.display_name,
                version=manifest.version,
                kind=manifest.kind,
                profile_kind=manifest.profile_kind,
                status=report.status,
                capabilities=manifest.capabilities,
                issues=report.issues,
                repair_hints=report.repair_hints,
                checked_paths=report.checked_paths,
            )
        )

    models: list[ModelAssetSnapshot] = []
    for manifest in store.load_model_asset_manifests():
        report = checker.check_model_asset(manifest)
        models.append(
            ModelAssetSnapshot(
                model_id=manifest.model_id,
                display_name=manifest.display_name,
                model_family=manifest.model_family,
                backend=manifest.backend,
                version=manifest.version,
                profile_kind=manifest.profile_kind,
                status=report.status,
                task_types=manifest.task_types,
                capabilities=manifest.capabilities,
                issues=report.issues,
                repair_hints=report.repair_hints,
                checked_paths=report.checked_paths,
            )
        )

    return RuntimeSetupSnapshot(runtimes=runtimes, models=models)
