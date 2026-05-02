from __future__ import annotations

from atelier.domain.resources import RuntimeBinding, RuntimeRequest
from atelier.runtime.manifest import ModelAssetManifest, RuntimeManifest
from atelier.runtime.store import RuntimeStore


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
        runtime_ids: list[str] = []

        for component in request.components:
            manifest = self._find_component(component, request.capabilities)
            if manifest is None:
                raise RuntimeError(f"missing runtime component: {component}")
            component_paths.update(manifest.component_paths)
            runtime_ids.append(manifest.runtime_id)

        model_paths: dict[str, str] = {}
        for model_id in request.model_ids:
            model = self._find_model(model_id)
            if model is None:
                raise RuntimeError(f"missing model asset: {model_id}")
            model_paths[model.model_id] = model.local_path

        runtime_id = "+".join(runtime_ids) if runtime_ids else "runtime:none"
        return RuntimeBinding(
            runtime_id=runtime_id,
            component_paths=component_paths,
            model_paths=model_paths,
            env={},
            binding_reason="resolved from managed manifests",
        )

    def _find_component(
        self, component: str, requested_capabilities: list[str]
    ) -> RuntimeManifest | None:
        for manifest in self._runtimes:
            if manifest.status != "ready" or manifest.component != component:
                continue
            if not set(requested_capabilities).issubset(set(manifest.capabilities)):
                continue
            return manifest
        return None

    def _find_model(self, model_id: str) -> ModelAssetManifest | None:
        for model in self._models:
            if model.status == "ready" and model.model_id == model_id:
                return model
        return None
