import sqlite3
import unittest

from atelier.storage.db import initialize_database, list_tables


class StorageSchemaTests(unittest.TestCase):
    def test_initialize_database_creates_core_tables(self) -> None:
        connection = sqlite3.connect(":memory:")

        initialize_database(connection)

        tables = list_tables(connection)
        expected = {
            "projects",
            "jobs",
            "workflow_graphs",
            "execution_plans",
            "execution_tasks",
            "task_dependencies",
            "artifacts",
            "task_artifacts",
            "task_events",
            "resource_locks",
            "cache_entries",
            "presets",
            "runtime_components",
            "model_assets",
            "credential_refs",
        }
        self.assertTrue(expected.issubset(tables))


if __name__ == "__main__":
    unittest.main()
