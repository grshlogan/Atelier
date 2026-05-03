from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from pathlib import Path

from atelier.app.paths import AppPaths


@dataclass(frozen=True)
class WorkspaceLayoutRecord:
    name: str
    geometry: bytes
    state: bytes


class WorkspaceLayoutStore:
    def __init__(self, app_paths: AppPaths) -> None:
        self._app_paths = app_paths

    @property
    def layout_path(self) -> Path:
        return self._app_paths.workspace_layouts_path

    def save_layout(self, name: str, *, geometry: bytes, state: bytes) -> None:
        records = self._load_all()
        records[name] = {
            "geometry": _encode_bytes(geometry),
            "state": _encode_bytes(state),
        }
        self.layout_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.layout_path.with_suffix(".tmp")
        temporary_path.write_text(json.dumps(records, ensure_ascii=True, indent=2), encoding="utf-8")
        temporary_path.replace(self.layout_path)

    def load_layout(self, name: str) -> WorkspaceLayoutRecord | None:
        payload = self._load_all().get(name)
        if payload is None:
            return None
        return WorkspaceLayoutRecord(
            name=name,
            geometry=_decode_bytes(payload["geometry"]),
            state=_decode_bytes(payload["state"]),
        )

    def _load_all(self) -> dict:
        if not self.layout_path.exists():
            return {}
        return json.loads(self.layout_path.read_text(encoding="utf-8"))


def _encode_bytes(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _decode_bytes(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"))
