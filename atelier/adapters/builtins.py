from __future__ import annotations

from atelier.adapters.ffprobe import FFprobeMetadataAdapter
from atelier.adapters.registry import AdapterRegistry


def create_builtin_adapter_registry() -> AdapterRegistry:
    registry = AdapterRegistry()
    registry.register(FFprobeMetadataAdapter())
    return registry
