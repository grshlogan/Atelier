import unittest

from atelier.adapters.base import AdapterContext, AdapterResult, WorkerAdapter
from atelier.adapters.registry import AdapterRegistry, AdapterRegistryError


class EchoAdapter(WorkerAdapter):
    node_type = "test.echo"
    adapter_version = "1"

    def run(self, context: AdapterContext) -> AdapterResult:
        return AdapterResult(artifacts=[], metadata={"node_type": context.task.node_type})


class AdapterRegistryTests(unittest.TestCase):
    def test_registers_and_resolves_adapter_by_node_type(self) -> None:
        registry = AdapterRegistry()
        adapter = EchoAdapter()

        registry.register(adapter)

        self.assertIs(registry.resolve("test.echo"), adapter)
        self.assertEqual(registry.node_types(), ["test.echo"])

    def test_rejects_duplicate_adapter_node_type(self) -> None:
        registry = AdapterRegistry()
        registry.register(EchoAdapter())

        with self.assertRaisesRegex(AdapterRegistryError, "duplicate adapter node_type"):
            registry.register(EchoAdapter())

    def test_missing_node_type_has_clear_error(self) -> None:
        registry = AdapterRegistry()

        with self.assertRaisesRegex(AdapterRegistryError, "missing adapter for node_type: metadata.probe"):
            registry.resolve("metadata.probe")


if __name__ == "__main__":
    unittest.main()
