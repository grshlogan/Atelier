from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from atelier.runtime.health import RuntimeHealthChecker
from atelier.runtime.manifest import ModelAssetManifest, RuntimeManifest
from atelier.runtime.setup import build_runtime_setup_snapshot
from atelier.runtime.store import RuntimeStore


class RuntimeSetupSnapshotTests(unittest.TestCase):
    def test_builds_gui_readable_snapshot_from_store_and_health_checker(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            store = RuntimeStore(root)
            ffprobe = root / "runtimes" / "components" / "ffmpeg" / "bin" / "ffprobe.exe"
            ffprobe.parent.mkdir(parents=True)
            ffprobe.write_bytes(b"fake ffprobe")
            store.write_runtime_manifests(
                [
                    RuntimeManifest(
                        runtime_id="ffprobe-local",
                        component="ffprobe",
                        version="7.1.0",
                        display_name="FFprobe Local",
                        component_paths={"ffprobe": "runtimes/components/ffmpeg/bin/ffprobe.exe"},
                        capabilities=["metadata"],
                        profile_kind="local",
                    ),
                    RuntimeManifest(
                        runtime_id="ffmpeg-missing",
                        component="ffmpeg",
                        version="7.1.0",
                        display_name="FFmpeg Missing",
                        component_paths={"ffmpeg": "runtimes/components/ffmpeg/bin/ffmpeg.exe"},
                        capabilities=["video"],
                        profile_kind="local",
                    ),
                ]
            )
            model_dir = root / "models" / "asr" / "demo-asr"
            model_dir.mkdir(parents=True)
            store.write_model_asset_manifests(
                [
                    ModelAssetManifest(
                        model_id="demo-asr",
                        display_name="Demo ASR",
                        model_family="demo",
                        backend="simulated",
                        local_path="models/asr/demo-asr",
                        task_types=["asr"],
                        capabilities=["asr"],
                        profile_kind="local",
                    )
                ]
            )

            snapshot = build_runtime_setup_snapshot(
                store,
                RuntimeHealthChecker(root),
            )

            self.assertEqual(snapshot.runtime_count, 2)
            self.assertEqual(snapshot.model_count, 1)
            self.assertEqual(snapshot.ready_runtime_count, 1)
            self.assertEqual(snapshot.problem_count, 1)
            self.assertEqual(snapshot.runtimes[0].runtime_id, "ffprobe-local")
            self.assertEqual(snapshot.runtimes[0].status, "ready")
            self.assertEqual(snapshot.runtimes[0].capabilities, ["metadata"])
            self.assertEqual(snapshot.runtimes[1].runtime_id, "ffmpeg-missing")
            self.assertEqual(snapshot.runtimes[1].status, "missing")
            self.assertIn("missing component path", snapshot.runtimes[1].issues[0])
            self.assertIn("Register or repair", snapshot.runtimes[1].repair_hints[0])
            self.assertEqual(snapshot.models[0].model_id, "demo-asr")
            self.assertEqual(snapshot.models[0].status, "ready")
            self.assertEqual(snapshot.models[0].task_types, ["asr"])


if __name__ == "__main__":
    unittest.main()
