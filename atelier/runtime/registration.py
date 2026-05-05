from __future__ import annotations

from pathlib import Path
from typing import Any

from atelier.runtime.manifest import ModelAssetManifest, RuntimeKind, RuntimeManifest, RuntimeProfileKind
from atelier.runtime.store import RuntimeStore


class RuntimeRegistrationError(ValueError):
    pass


class RuntimeRegistrationService:
    def __init__(self, store: RuntimeStore) -> None:
        self.store = store
        self.data_root = store.data_root.resolve()

    def register_local_executable(
        self,
        *,
        runtime_id: str,
        component: str,
        executable_path: str | Path,
        version: str = "",
        capabilities: list[str] | None = None,
        display_name: str = "",
        executable_name: str | None = None,
        kind: RuntimeKind = "tool",
        profile_kind: RuntimeProfileKind = "local",
        platform: str = "",
        backend_tags: list[str] | None = None,
        env: dict[str, str] | None = None,
    ) -> RuntimeManifest:
        self._ensure_runtime_id_available(runtime_id)
        executable = self._validate_existing_path(
            executable_path,
            label="executable",
            must_be_file=True,
        )
        key = executable_name or component
        manifest_path = self._manifest_path(executable)
        library_dir = self._manifest_path(executable.parent)
        manifest = RuntimeManifest(
            runtime_id=runtime_id,
            component=component,
            version=version,
            kind=kind,
            display_name=display_name,
            platform=platform,
            component_paths={key: manifest_path},
            executable_paths={key: manifest_path},
            library_dirs=[library_dir],
            env=env or {},
            capabilities=capabilities or [],
            backend_tags=backend_tags or [],
            status="ready",
            profile_kind=profile_kind,
        )
        manifests = self.store.load_runtime_manifests()
        self.store.write_runtime_manifests([*manifests, manifest])
        return manifest

    def register_worker_python(
        self,
        *,
        runtime_id: str,
        executable_path: str | Path,
        version: str = "",
    ) -> RuntimeManifest:
        return self.register_local_executable(
            runtime_id=runtime_id,
            component="python.worker",
            executable_path=executable_path,
            version=version,
            capabilities=["worker", "python"],
            display_name="Developer Worker Python",
            executable_name="python",
            kind="worker_env",
            profile_kind="dev",
        )

    def register_model_asset(
        self,
        *,
        model_id: str,
        local_path: str | Path,
        backend: str,
        version: str = "",
        display_name: str = "",
        model_family: str = "",
        task_types: list[str] | None = None,
        compatible_backends: list[str] | None = None,
        capabilities: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        profile_kind: RuntimeProfileKind = "local",
    ) -> ModelAssetManifest:
        self._ensure_model_id_available(model_id)
        model_path = self._validate_existing_path(
            local_path,
            label="model",
            must_be_file=False,
        )
        size_bytes = model_path.stat().st_size if model_path.is_file() else None
        manifest = ModelAssetManifest(
            model_id=model_id,
            display_name=display_name,
            model_family=model_family,
            backend=backend,
            version=version,
            local_path=self._manifest_path(model_path),
            task_types=task_types or [],
            compatible_backends=compatible_backends or [backend],
            capabilities=capabilities or [],
            size_bytes=size_bytes,
            metadata=metadata or {},
            status="ready",
            profile_kind=profile_kind,
        )
        manifests = self.store.load_model_asset_manifests()
        self.store.write_model_asset_manifests([*manifests, manifest])
        return manifest

    def _ensure_runtime_id_available(self, runtime_id: str) -> None:
        if not runtime_id.strip():
            raise RuntimeRegistrationError("empty runtime id")
        for manifest in self.store.load_runtime_manifests():
            if manifest.runtime_id == runtime_id:
                raise RuntimeRegistrationError(f"duplicate runtime id: {runtime_id}")

    def _ensure_model_id_available(self, model_id: str) -> None:
        if not model_id.strip():
            raise RuntimeRegistrationError("empty model id")
        for manifest in self.store.load_model_asset_manifests():
            if manifest.model_id == model_id:
                raise RuntimeRegistrationError(f"duplicate model id: {model_id}")

    def _validate_existing_path(
        self,
        raw_path: str | Path,
        *,
        label: str,
        must_be_file: bool,
    ) -> Path:
        if isinstance(raw_path, str) and not raw_path.strip():
            raise RuntimeRegistrationError(f"empty {label} path")
        path = Path(raw_path)
        if not str(path).strip():
            raise RuntimeRegistrationError(f"empty {label} path")
        if not path.is_absolute() and ".." in path.parts:
            raise RuntimeRegistrationError(f"{label} path traversal is not allowed")
        resolved = path.resolve() if path.is_absolute() else (self.data_root / path).resolve()
        if not resolved.exists():
            raise RuntimeRegistrationError(f"missing {label} path: {raw_path}")
        if must_be_file and not resolved.is_file():
            raise RuntimeRegistrationError(f"{label} path is not a file: {raw_path}")
        return resolved

    def _manifest_path(self, path: Path) -> str:
        try:
            return path.relative_to(self.data_root).as_posix()
        except ValueError:
            return str(path)
