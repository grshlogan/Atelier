from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


DeviceType = Literal["gpu", "cpu", "any"]


class ResourceRequest(BaseModel):
    device_type: DeviceType = "any"
    vram_mb: int | None = None
    exclusive: bool = False
    cpu_cores: int | None = None
    ram_mb: int | None = None


class ResourceBinding(BaseModel):
    device_id: str
    allocated_vram_mb: int | None = None
    shared_with: list[str] = Field(default_factory=list)
    binding_reason: str = ""


class RuntimeRequest(BaseModel):
    components: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    model_ids: list[str] = Field(default_factory=list)


class RuntimeBinding(BaseModel):
    runtime_id: str
    component_paths: dict[str, str] = Field(default_factory=dict)
    model_paths: dict[str, str] = Field(default_factory=dict)
    env: dict[str, str] = Field(default_factory=dict)
    binding_reason: str = ""


class HardwareSnapshot(BaseModel):
    gpus: list[dict] = Field(default_factory=list)
    cpu_cores: int = 0
    ram_total_mb: int = 0
    ram_free_mb: int = 0
    captured_at: str = ""
