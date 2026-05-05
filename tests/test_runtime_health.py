from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

from atelier.runtime.health import RuntimeHealthChecker
from atelier.runtime.manifest import ModelAssetManifest, RuntimeManifest
from atelier.security.package_integrity import sha256_file


class RuntimeHealthTests(unittest.TestCase):
    def test_runtime_is_ready_when_declared_paths_exist_and_hashes_match(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            executable = root / "runtimes" / "components" / "ffmpeg" / "7.1.0" / "bin" / "ffmpeg.exe"
            executable.parent.mkdir(parents=True)
            executable.write_bytes(b"demo executable")
            manifest = RuntimeManifest(
                runtime_id="ffmpeg-7.1.0-windows-x86_64",
                component="ffmpeg",
                version="7.1.0",
                component_paths={"ffmpeg": "runtimes/components/ffmpeg/7.1.0/bin/ffmpeg.exe"},
                capabilities=["video"],
                checksums={"ffmpeg": sha256_file(executable)},
            )

            report = RuntimeHealthChecker(root).check_runtime(manifest)

            self.assertEqual(report.status, "ready")
            self.assertEqual(report.issues, [])

    def test_runtime_reports_missing_manifest_path(self) -> None:
        with TemporaryDirectory() as temp_dir:
            manifest = RuntimeManifest(
                runtime_id="ffmpeg-7.1.0-windows-x86_64",
                component="ffmpeg",
                version="7.1.0",
                component_paths={"ffmpeg": "runtimes/components/ffmpeg/7.1.0/bin/ffmpeg.exe"},
                capabilities=["video"],
            )

            report = RuntimeHealthChecker(Path(temp_dir)).check_runtime(manifest)

            self.assertEqual(report.status, "missing")
            self.assertIn("missing component path: ffmpeg", report.issues)
            self.assertIn("Register or repair the ffmpeg runtime path.", report.repair_hints)

    def test_runtime_reports_checksum_mismatch(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            executable = root / "runtimes" / "components" / "ffmpeg" / "7.1.0" / "bin" / "ffmpeg.exe"
            executable.parent.mkdir(parents=True)
            executable.write_bytes(b"demo executable")
            manifest = RuntimeManifest(
                runtime_id="ffmpeg-7.1.0-windows-x86_64",
                component="ffmpeg",
                version="7.1.0",
                component_paths={"ffmpeg": "runtimes/components/ffmpeg/7.1.0/bin/ffmpeg.exe"},
                capabilities=["video"],
                checksums={"ffmpeg": "0" * 64},
            )

            report = RuntimeHealthChecker(root).check_runtime(manifest)

            self.assertEqual(report.status, "broken")
            self.assertIn("checksum mismatch: ffmpeg", report.issues)
            self.assertIn("Reinstall or replace the ffmpeg runtime component.", report.repair_hints)

    def test_runtime_dry_run_probe_reports_ready_and_failure_without_shell(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            probe = root / "runtimes" / "components" / "probe" / "probe.py"
            probe.parent.mkdir(parents=True)
            probe.write_text(
                "import sys\n"
                "raise SystemExit(0 if '--version' in sys.argv else 7)\n",
                encoding="utf-8",
            )
            manifest = RuntimeManifest(
                runtime_id="probe-local",
                component="probe",
                version="1",
                component_paths={"python": sys.executable},
                executable_paths={"python": sys.executable},
                capabilities=["metadata"],
            )
            checker = RuntimeHealthChecker(root)

            ready = checker.check_runtime(
                manifest,
                dry_run_args={"python": [str(probe), "--version"]},
            )
            broken = checker.check_runtime(
                manifest,
                dry_run_args={"python": [str(probe)]},
            )

            self.assertEqual(ready.status, "ready")
            self.assertEqual(ready.issues, [])
            self.assertEqual(broken.status, "broken")
            self.assertIn("dry-run failed: python", broken.issues)
            self.assertIn("Check the python runtime configuration and probe arguments.", broken.repair_hints)

    def test_model_asset_health_checks_local_path(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            model_path = root / "models" / "asr" / "demo-asr"
            model_path.mkdir(parents=True)
            manifest = ModelAssetManifest(
                model_id="demo-asr",
                backend="simulated",
                version="1",
                local_path="models/asr/demo-asr",
                capabilities=["asr"],
            )

            report = RuntimeHealthChecker(root).check_model_asset(manifest)

            self.assertEqual(report.status, "ready")


if __name__ == "__main__":
    unittest.main()
