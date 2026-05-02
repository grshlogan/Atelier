from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from atelier.app.paths import AppPaths
from atelier.app.services import create_runtime_store, open_app_database
from atelier.storage.db import list_tables


class AppServicesTests(unittest.TestCase):
    def test_create_runtime_store_uses_app_paths_data_root(self) -> None:
        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))

            store = create_runtime_store(paths)

            self.assertEqual(store.data_root, paths.data_root)
            self.assertEqual(store.runtime_manifest_path, paths.runtime_manifest_path)
            self.assertTrue((paths.runtime_root / "manifests").is_dir())

    def test_open_app_database_uses_app_paths_database_path_and_initializes_schema(self) -> None:
        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))

            connection = open_app_database(paths)
            try:
                tables = list_tables(connection)
            finally:
                connection.close()

            self.assertTrue(paths.database_path.is_file())
            self.assertIn("projects", tables)
            self.assertIn("task_events", tables)
            self.assertIn("runtime_components", tables)


if __name__ == "__main__":
    unittest.main()
