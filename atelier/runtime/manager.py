from __future__ import annotations

from atelier.domain.resources import RuntimeBinding, RuntimeRequest
from atelier.runtime.manifest import ModelAssetManifest, RuntimeManifest
from atelier.runtime.store import RuntimeStore


class RuntimeResolutionError(RuntimeError):
    def __init__(self, message: str, *, subject_id: str, reason: str) -> None:
        super().__init__(message)
        self.subject_id = subject_id
        self.reason = reason


class RuntimeManager:
    def __init__(
        self,
        runtime_manifests: list[RuntimeManifest] | None = None,
        model_assets: list[ModelAssetManifest] | None = None,
    ) -> None:
        self._runtimes = runtime_manifests or []
        self._models = model_assets or []

    @classmethod
    def from_store(cls, store: RuntimeStore) -> RuntimeManager:
        return cls(
            runtime_manifests=store.load_runtime_manifests(),
            model_assets=store.load_model_asset_manifests(),
        )

    def resolve(self, request: RuntimeRequest) -> RuntimeBinding:
        component_paths: dict[str, str] = {}
        env: dict[str, str] = {}
        runtime_ids: list[str] = []

        for component in request.components:
            manifest = self._resolve_component(component, request.capabilities)
            component_paths.update(manifest.component_paths)
            env.update(manifest.env)
            runtime_ids.append(manifest.runtime_id)

        model_paths: dict[str, str] = {}
        for model_id in request.model_ids:
            model = self._resolve_model(model_id)
            model_paths[model.model_id] = model.local_path

        runtime_id = "+".join(runtime_ids) if runtime_ids else "runtime:none"
        return RuntimeBinding(
            runtime_id=runtime_id,
            component_paths=component_paths,
            model_paths=model_paths,
            env=env,
            binding_reason="resolved from managed manifests",
        )

    def _resolve_component(self, component: str, requested_capabilities: list[str]) -> RuntimeManifest:
        candidates = [manifest for manifest in self._runtimes if manifest.component == component]
        if not candidates:
            raise RuntimeResolutionError(
                f"missing runtime component: {component}",
                subject_id=component,
                reason="missing_component",
            )

        ready_candidates = [manifest for manifest in candidates if manifest.status == "ready"]
        if not ready_candidates:
            status = candidates[0].status
            raise RuntimeResolutionError(
                f"runtime component is {status}: {component}",
                subject_id=component,
                reason=status,
            )

        requested = set(requested_capabilities)
        for manifest in ready_candidates:
            if requested.issubset(set(manifest.capabilities)):
                return manifest

        available = set().union(*(set(manifest.capabilities) for manifest in ready_candidates))
        missing = sorted(requested - available)
        raise RuntimeResolutionError(
            f"runtime component missing capabilities: {component} ({', '.join(missing)})",
            subject_id=component,
            reason="capability_mismatch",
        )

    def _resolve_model(self, model_id: str) -> ModelAssetManifest:
        candidates = [model for model in self._models if model.model_id == model_id]
        if not candidates:
            raise RuntimeResolutionError(
                f"missing model asset: {model_id}",
                subject_id=model_id,
                reason="missing_model",
            )
        for model in candidates:
            if model.status == "ready":
                return model
        status = candidates[0].status
        raise RuntimeResolutionError(
            f"model asset is {status}: {model_id}",
            subject_id=model_id,
            reason=status,
        )
