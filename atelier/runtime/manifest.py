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


class RuntimeManifest(BaseModel):
    runtime_id: str
    component: str
    version: str
    component_paths: dict[str, str] = Field(default_factory=dict)
    capabilities: list[str] = Field(default_factory=list)
    checksums: dict[str, str] = Field(default_factory=dict)
    status: RuntimeStatus = "ready"


class ModelAssetManifest(BaseModel):
    model_id: str
    backend: str
    version: str = ""
    local_path: str
    capabilities: list[str] = Field(default_factory=list)
    sha256: str | None = None
    status: RuntimeStatus = "ready"
