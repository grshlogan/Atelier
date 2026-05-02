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
