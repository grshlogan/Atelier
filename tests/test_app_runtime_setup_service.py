from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from atelier.app.paths import AppPaths
from atelier.app.services import create_runtime_setup_service
from atelier.runtime.registration import RuntimeRegistrationError


class AppRuntimeSetupServiceTests(unittest.TestCase):
    def test_registers_local_runtime_and_returns_refreshed_snapshot(self) -> None:
        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))
            ffmpeg = paths.data_root / "runtimes" / "components" / "ffmpeg.exe"
            ffmpeg.parent.mkdir(parents=True)
            ffmpeg.write_bytes(b"fake ffmpeg")

            service = create_runtime_setup_service(paths)
            snapshot = service.register_ffmpeg_path(ffmpeg)

            self.assertEqual(snapshot.runtime_count, 1)
            self.assertEqual(snapshot.ready_runtime_count, 1)
            self.assertEqual(snapshot.runtimes[0].runtime_id, "ffmpeg-local")
            self.assertEqual(snapshot.runtimes[0].component, "ffmpeg")
            self.assertIn("mux", snapshot.runtimes[0].capabilities)

    def test_missing_registration_path_raises_diagnostic_error(self) -> None:
        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))
            service = create_runtime_setup_service(paths)

            with self.assertRaisesRegex(RuntimeRegistrationError, "missing executable path"):
                service.register_ffprobe_path(paths.data_root / "missing-ffprobe.exe")


if __name__ == "__main__":
    unittest.main()
