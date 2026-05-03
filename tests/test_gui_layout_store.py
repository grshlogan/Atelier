from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from atelier.app.paths import AppPaths
from atelier.gui.layout_store import WorkspaceLayoutStore


class GuiLayoutStoreTests(unittest.TestCase):
    def test_workspace_layout_store_round_trips_geometry_and_state_bytes(self) -> None:
        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))
            store = WorkspaceLayoutStore(paths)

            store.save_layout("default", geometry=b"geometry-bytes", state=b"state-bytes")
            record = store.load_layout("default")

            self.assertIsNotNone(record)
            self.assertEqual(record.name, "default")
            self.assertEqual(record.geometry, b"geometry-bytes")
            self.assertEqual(record.state, b"state-bytes")
            self.assertEqual(store.layout_path, paths.workspace_layouts_path)
            self.assertTrue(paths.workspace_layouts_path.exists())

    def test_workspace_layout_store_returns_none_for_missing_layout(self) -> None:
        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))
            store = WorkspaceLayoutStore(paths)

            self.assertIsNone(store.load_layout("missing"))


if __name__ == "__main__":
    unittest.main()
