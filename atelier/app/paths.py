from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    data_root: Path
    workspace_root: Path | None = None

    @classmethod
    def for_development(cls, workspace_root: str | Path) -> AppPaths:
        root = Path(workspace_root)
        return cls(
            workspace_root=root,
            data_root=root / ".atelier" / "AtelierData",
        )

    @classmethod
    def from_data_root(cls, data_root: str | Path) -> AppPaths:
        return cls(data_root=Path(data_root))

    @property
    def runtime_root(self) -> Path:
        return self.data_root / "runtimes"

    @property
    def model_root(self) -> Path:
        return self.data_root / "models"

    @property
    def plugin_root(self) -> Path:
        return self.data_root / "plugins"

    @property
    def cache_root(self) -> Path:
        return self.data_root / "cache"

    @property
    def staging_root(self) -> Path:
        return self.data_root / "staging"

    @property
    def logs_root(self) -> Path:
        return self.data_root / "logs"

    @property
    def database_path(self) -> Path:
        return self.data_root / "atelier.sqlite3"

    @property
    def workspace_layouts_path(self) -> Path:
        return self.cache_root / "workspace-layouts.json"

    @property
    def runtime_manifest_path(self) -> Path:
        return self.runtime_root / "manifests" / "installed.json"

    @property
    def model_manifest_path(self) -> Path:
        return self.model_root / "manifests" / "installed.json"

    def ensure_data_dirs(self) -> None:
        for path in (
            self.data_root,
            self.runtime_root / "components",
            self.runtime_root / "python-envs",
            self.runtime_root / "manifests",
            self.model_root / "manifests",
            self.plugin_root / "installed",
            self.plugin_root / "disabled",
            self.cache_root,
            self.staging_root,
            self.logs_root,
        ):
            path.mkdir(parents=True, exist_ok=True)
