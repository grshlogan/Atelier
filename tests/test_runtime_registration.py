from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from atelier.runtime.registration import RuntimeRegistrationError, RuntimeRegistrationService
from atelier.runtime.store import RuntimeStore


class RuntimeRegistrationTests(unittest.TestCase):
    def test_registers_local_ffmpeg_tools_and_worker_python_profile(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            store = RuntimeStore(root)
            tool_root = root / "runtimes" / "components" / "ffmpeg" / "7.1.0" / "bin"
            tool_root.mkdir(parents=True)
            ffprobe = tool_root / "ffprobe.exe"
            ffmpeg = tool_root / "ffmpeg.exe"
            worker_python = root / "runtimes" / "python-envs" / "worker-dev" / "python.exe"
            ffprobe.write_bytes(b"fake ffprobe")
            ffmpeg.write_bytes(b"fake ffmpeg")
            worker_python.parent.mkdir(parents=True)
            worker_python.write_bytes(b"fake python")

            service = RuntimeRegistrationService(store)
            service.register_local_executable(
                runtime_id="ffprobe-local",
                component="ffprobe",
                executable_path=ffprobe,
                version="7.1.0",
                capabilities=["metadata", "video", "audio"],
                display_name="FFprobe Local",
            )
            service.register_local_executable(
                runtime_id="ffmpeg-local",
                component="ffmpeg",
                executable_path=ffmpeg,
                version="7.1.0",
                capabilities=["video", "audio", "mux"],
                display_name="FFmpeg Local",
            )
            service.register_worker_python(
                runtime_id="python-worker-dev",
                executable_path=worker_python,
                version="3.11",
            )

            ffprobe_manifest, ffmpeg_manifest, worker_manifest = store.load_runtime_manifests()
            self.assertEqual(ffprobe_manifest.component, "ffprobe")
            self.assertEqual(ffprobe_manifest.kind, "tool")
            self.assertEqual(ffprobe_manifest.profile_kind, "local")
            self.assertEqual(
                ffprobe_manifest.executable_paths["ffprobe"],
                "runtimes/components/ffmpeg/7.1.0/bin/ffprobe.exe",
            )
            self.assertEqual(ffmpeg_manifest.component_paths["ffmpeg"], ffmpeg_manifest.executable_paths["ffmpeg"])
            self.assertEqual(worker_manifest.component, "python.worker")
            self.assertEqual(worker_manifest.kind, "worker_env")
            self.assertEqual(worker_manifest.profile_kind, "dev")
            self.assertEqual(worker_manifest.executable_paths["python"], "runtimes/python-envs/worker-dev/python.exe")

    def test_registers_demo_model_directory(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            store = RuntimeStore(root)
            model_dir = root / "models" / "asr" / "demo-asr"
            model_dir.mkdir(parents=True)
            (model_dir / "model.bin").write_bytes(b"fake model")

            service = RuntimeRegistrationService(store)
            service.register_model_asset(
                model_id="demo-asr",
                local_path=model_dir,
                backend="simulated",
                version="1",
                display_name="Demo ASR",
                model_family="demo",
                task_types=["asr"],
                compatible_backends=["simulated"],
                capabilities=["asr"],
            )

            model = store.load_model_asset_manifests()[0]
            self.assertEqual(model.model_id, "demo-asr")
            self.assertEqual(model.local_path, "models/asr/demo-asr")
            self.assertEqual(model.profile_kind, "local")
            self.assertEqual(model.task_types, ["asr"])
            self.assertEqual(model.compatible_backends, ["simulated"])

    def test_rejects_empty_missing_traversal_and_duplicate_profiles(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            store = RuntimeStore(root)
            executable = root / "runtimes" / "components" / "ffprobe.exe"
            executable.parent.mkdir(parents=True, exist_ok=True)
            executable.write_bytes(b"fake")
            service = RuntimeRegistrationService(store)

            with self.assertRaisesRegex(RuntimeRegistrationError, "empty executable path"):
                service.register_local_executable(
                    runtime_id="empty",
                    component="ffprobe",
                    executable_path="",
                )
            with self.assertRaisesRegex(RuntimeRegistrationError, "missing executable path"):
                service.register_local_executable(
                    runtime_id="missing",
                    component="ffprobe",
                    executable_path=root / "missing.exe",
                )
            with self.assertRaisesRegex(RuntimeRegistrationError, "path traversal"):
                service.register_local_executable(
                    runtime_id="traversal",
                    component="ffprobe",
                    executable_path=Path("..") / "ffprobe.exe",
                )

            service.register_local_executable(
                runtime_id="ffprobe-local",
                component="ffprobe",
                executable_path=executable,
            )
            with self.assertRaisesRegex(RuntimeRegistrationError, "duplicate runtime id"):
                service.register_local_executable(
                    runtime_id="ffprobe-local",
                    component="ffprobe",
                    executable_path=executable,
                )

            model_dir = root / "models" / "demo"
            model_dir.mkdir(parents=True)
            service.register_model_asset(
                model_id="demo",
                local_path=model_dir,
                backend="simulated",
            )
            with self.assertRaisesRegex(RuntimeRegistrationError, "duplicate model id"):
                service.register_model_asset(
                    model_id="demo",
                    local_path=model_dir,
                    backend="simulated",
                )
            with self.assertRaisesRegex(RuntimeRegistrationError, "empty model path"):
                service.register_model_asset(
                    model_id="empty-model",
                    local_path="",
                    backend="simulated",
                )


if __name__ == "__main__":
    unittest.main()
