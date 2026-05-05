from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


RuntimeStatus = Literal[
    "missing",
    "installing",
    "ready",
    "broken",
    "disabled",
    "incompatible",
    "update_available",
]

RuntimeKind = Literal["app", "tool", "backend", "worker_env", "model_backend", "external_tool"]
RuntimeProfileKind = Literal["managed", "local", "dev", "plugin"]


class RuntimeManifest(BaseModel):
    runtime_id: str
    component: str
    version: str
    kind: RuntimeKind = "tool"
    display_name: str = ""
    platform: str = ""
    component_paths: dict[str, str] = Field(default_factory=dict)
    executable_paths: dict[str, str] = Field(default_factory=dict)
    library_dirs: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)
    capabilities: list[str] = Field(default_factory=list)
    backend_tags: list[str] = Field(default_factory=list)
    checksums: dict[str, str] = Field(default_factory=dict)
    integrity: dict[str, str] = Field(default_factory=dict)
    status: RuntimeStatus = "ready"
    profile_kind: RuntimeProfileKind = "managed"


class ModelAssetManifest(BaseModel):
    model_id: str
    display_name: str = ""
    model_family: str = ""
    backend: str
    version: str = ""
    local_path: str
    task_types: list[str] = Field(default_factory=list)
    compatible_backends: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    sha256: str | None = None
    size_bytes: int | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
    status: RuntimeStatus = "ready"
    profile_kind: RuntimeProfileKind = "managed"
