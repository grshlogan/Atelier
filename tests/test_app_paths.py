from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from atelier.app.paths import AppPaths


class AppPathsTests(unittest.TestCase):
    def test_development_paths_keep_data_under_local_atelier_dir(self) -> None:
        with TemporaryDirectory() as temp_dir:
            workspace_root = Path(temp_dir)

            paths = AppPaths.for_development(workspace_root)

            self.assertEqual(paths.workspace_root, workspace_root)
            self.assertEqual(paths.data_root, workspace_root / ".atelier" / "AtelierData")
            self.assertEqual(paths.runtime_root, paths.data_root / "runtimes")
            self.assertEqual(paths.model_root, paths.data_root / "models")
            self.assertEqual(paths.plugin_root, paths.data_root / "plugins")
            self.assertEqual(paths.database_path, paths.data_root / "atelier.sqlite3")
            self.assertEqual(
                paths.runtime_manifest_path,
                paths.data_root / "runtimes" / "manifests" / "installed.json",
            )
            self.assertFalse((workspace_root / ".venv").exists())

    def test_ensure_data_dirs_creates_shared_runtime_layout(self) -> None:
        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))

            paths.ensure_data_dirs()

            expected_dirs = [
                paths.data_root,
                paths.runtime_root / "components",
                paths.runtime_root / "python-envs",
                paths.runtime_root / "manifests",
                paths.model_root / "manifests",
                paths.plugin_root / "installed",
                paths.plugin_root / "disabled",
                paths.cache_root,
                paths.staging_root,
                paths.logs_root,
            ]
            for expected_dir in expected_dirs:
                self.assertTrue(expected_dir.is_dir(), f"missing directory: {expected_dir}")

    def test_from_data_root_supports_release_or_user_data_roots(self) -> None:
        with TemporaryDirectory() as temp_dir:
            data_root = Path(temp_dir) / "AtelierData"

            paths = AppPaths.from_data_root(data_root)

            self.assertIsNone(paths.workspace_root)
            self.assertEqual(paths.data_root, data_root)
            self.assertEqual(paths.model_manifest_path, data_root / "models" / "manifests" / "installed.json")


if __name__ == "__main__":
    unittest.main()
