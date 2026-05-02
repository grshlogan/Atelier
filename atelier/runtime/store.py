from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from atelier.runtime.manifest import ModelAssetManifest, RuntimeManifest


class RuntimeStore:
    def __init__(self, data_root: str | Path) -> None:
        self.data_root = Path(data_root)
        self.ensure_layout()

    @property
    def runtime_manifest_path(self) -> Path:
        return self.data_root / "runtimes" / "manifests" / "installed.json"

    @property
    def model_manifest_path(self) -> Path:
        return self.data_root / "models" / "manifests" / "installed.json"

    def ensure_layout(self) -> None:
        for path in (
            self.data_root / "runtimes" / "components",
            self.data_root / "runtimes" / "python-envs",
            self.data_root / "runtimes" / "manifests",
            self.data_root / "models" / "manifests",
            self.data_root / "plugins" / "installed",
            self.data_root / "plugins" / "disabled",
            self.data_root / "staging",
            self.data_root / "cache",
        ):
            path.mkdir(parents=True, exist_ok=True)

    def write_runtime_manifests(self, manifests: list[RuntimeManifest]) -> None:
        self._write_collection(
            self.runtime_manifest_path,
            "runtimes",
            [manifest.model_dump(mode="json") for manifest in manifests],
        )

    def load_runtime_manifests(self) -> list[RuntimeManifest]:
        payload = self._read_collection(self.runtime_manifest_path, "runtimes")
        return [RuntimeManifest.model_validate(item) for item in payload]

    def write_model_asset_manifests(self, manifests: list[ModelAssetManifest]) -> None:
        self._write_collection(
            self.model_manifest_path,
            "models",
            [manifest.model_dump(mode="json") for manifest in manifests],
        )

    def load_model_asset_manifests(self) -> list[ModelAssetManifest]:
        payload = self._read_collection(self.model_manifest_path, "models")
        return [ModelAssetManifest.model_validate(item) for item in payload]

    def _write_collection(self, path: Path, key: str, items: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(path.suffix + ".tmp")
        temp_path.write_text(
            json.dumps({"schema_version": "1", key: items}, indent=2),
            encoding="utf-8",
        )
        temp_path.replace(path)

    def _read_collection(self, path: Path, key: str) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
        items = payload.get(key, [])
        if not isinstance(items, list):
            raise ValueError(f"invalid runtime store collection: {key}")
        return items
