from __future__ import annotations

from atelier.adapters.base import WorkerAdapter


class AdapterRegistryError(LookupError):
    pass


class AdapterRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, WorkerAdapter] = {}

    def register(self, adapter: WorkerAdapter) -> None:
        node_type = adapter.node_type
        if node_type in self._adapters:
            raise AdapterRegistryError(f"duplicate adapter node_type: {node_type}")
        self._adapters[node_type] = adapter

    def resolve(self, node_type: str) -> WorkerAdapter:
        try:
            return self._adapters[node_type]
        except KeyError as exc:
            raise AdapterRegistryError(f"missing adapter for node_type: {node_type}") from exc

    def node_types(self) -> list[str]:
        return sorted(self._adapters)
