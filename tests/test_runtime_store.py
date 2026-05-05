from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from atelier.runtime.manager import RuntimeManager
from atelier.runtime.manifest import ModelAssetManifest, RuntimeManifest
from atelier.runtime.store import RuntimeStore
from atelier.domain.resources import RuntimeRequest


class RuntimeStoreTests(unittest.TestCase):
    def test_persists_and_loads_runtime_and_model_manifests(self) -> None:
        with TemporaryDirectory() as temp_dir:
            store = RuntimeStore(Path(temp_dir))
            runtime_manifest = RuntimeManifest(
                runtime_id="ffmpeg-7.1.0-windows-x86_64",
                component="ffmpeg",
                version="7.1.0",
                component_paths={"ffmpeg": "runtimes/components/ffmpeg/7.1.0/bin/ffmpeg.exe"},
                capabilities=["video", "audio", "cpu"],
            )
            model_manifest = ModelAssetManifest(
                model_id="demo-asr",
                backend="simulated",
                version="1",
                local_path="models/asr/demo-asr",
                capabilities=["asr"],
            )

            store.write_runtime_manifests([runtime_manifest])
            store.write_model_asset_manifests([model_manifest])

            loaded_runtime = store.load_runtime_manifests()[0]
            loaded_model = store.load_model_asset_manifests()[0]
            self.assertEqual(loaded_runtime.runtime_id, runtime_manifest.runtime_id)
            self.assertEqual(loaded_runtime.component_paths["ffmpeg"], runtime_manifest.component_paths["ffmpeg"])
            self.assertEqual(loaded_model.model_id, model_manifest.model_id)

    def test_persists_extended_runtime_and_model_manifest_fields(self) -> None:
        with TemporaryDirectory() as temp_dir:
            store = RuntimeStore(Path(temp_dir))
            runtime_manifest = RuntimeManifest(
                runtime_id="ffprobe-local-dev",
                component="ffprobe",
                version="7.1.0",
                kind="tool",
                display_name="FFprobe Local Dev",
                platform="windows-x86_64",
                component_paths={"ffprobe": "runtimes/components/ffmpeg/7.1.0/bin/ffprobe.exe"},
                executable_paths={"ffprobe": "runtimes/components/ffmpeg/7.1.0/bin/ffprobe.exe"},
                library_dirs=["runtimes/components/ffmpeg/7.1.0/bin"],
                env={"FFREPORT": "file=ffprobe.log"},
                capabilities=["metadata", "video", "audio"],
                backend_tags=["cpu"],
                integrity={"package_sha256": "abc123"},
                checksums={"ffprobe": "0" * 64},
                profile_kind="dev",
            )
            worker_runtime = RuntimeManifest(
                runtime_id="python-worker-dev",
                component="python.worker",
                version="3.11",
                kind="worker_env",
                display_name="Developer Worker Python",
                executable_paths={"python": ".venv/Scripts/python.exe"},
                capabilities=["worker", "python"],
                profile_kind="dev",
            )
            model_manifest = ModelAssetManifest(
                model_id="demo-asr",
                display_name="Demo ASR Model",
                model_family="demo",
                backend="simulated",
                version="1",
                local_path="models/asr/demo-asr",
                task_types=["asr"],
                compatible_backends=["simulated"],
                capabilities=["asr"],
                size_bytes=123,
                metadata={"language": "en"},
                profile_kind="local",
            )

            store.write_runtime_manifests([runtime_manifest, worker_runtime])
            store.write_model_asset_manifests([model_manifest])

            loaded_runtime, loaded_worker = store.load_runtime_manifests()
            loaded_model = store.load_model_asset_manifests()[0]
            self.assertEqual(loaded_runtime.kind, "tool")
            self.assertEqual(loaded_runtime.display_name, "FFprobe Local Dev")
            self.assertEqual(loaded_runtime.platform, "windows-x86_64")
            self.assertEqual(loaded_runtime.executable_paths["ffprobe"], runtime_manifest.executable_paths["ffprobe"])
            self.assertEqual(loaded_runtime.library_dirs, ["runtimes/components/ffmpeg/7.1.0/bin"])
            self.assertEqual(loaded_runtime.env["FFREPORT"], "file=ffprobe.log")
            self.assertEqual(loaded_runtime.backend_tags, ["cpu"])
            self.assertEqual(loaded_runtime.integrity["package_sha256"], "abc123")
            self.assertEqual(loaded_runtime.profile_kind, "dev")
            self.assertEqual(loaded_worker.kind, "worker_env")
            self.assertEqual(loaded_worker.executable_paths["python"], ".venv/Scripts/python.exe")
            self.assertEqual(loaded_model.display_name, "Demo ASR Model")
            self.assertEqual(loaded_model.model_family, "demo")
            self.assertEqual(loaded_model.task_types, ["asr"])
            self.assertEqual(loaded_model.compatible_backends, ["simulated"])
            self.assertEqual(loaded_model.size_bytes, 123)
            self.assertEqual(loaded_model.metadata["language"], "en")
            self.assertEqual(loaded_model.profile_kind, "local")

    def test_runtime_manager_can_resolve_from_store(self) -> None:
        with TemporaryDirectory() as temp_dir:
            store = RuntimeStore(Path(temp_dir))
            store.write_runtime_manifests(
                [
                    RuntimeManifest(
                        runtime_id="ffmpeg-7.1.0-windows-x86_64",
                        component="ffmpeg",
                        version="7.1.0",
                        component_paths={"ffmpeg": "runtimes/components/ffmpeg/7.1.0/bin/ffmpeg.exe"},
                        capabilities=["video", "audio", "cpu"],
                    )
                ]
            )

            binding = RuntimeManager.from_store(store).resolve(
                RuntimeRequest(components=["ffmpeg"], capabilities=["video"])
            )

            self.assertEqual(binding.runtime_id, "ffmpeg-7.1.0-windows-x86_64")
            self.assertEqual(
                binding.component_paths["ffmpeg"],
                "runtimes/components/ffmpeg/7.1.0/bin/ffmpeg.exe",
            )


if __name__ == "__main__":
    unittest.main()
