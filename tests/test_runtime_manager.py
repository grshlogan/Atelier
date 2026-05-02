import unittest

from atelier.domain.resources import RuntimeRequest
from atelier.runtime.manager import RuntimeManager
from atelier.runtime.manifest import ModelAssetManifest, RuntimeManifest


class RuntimeManagerTests(unittest.TestCase):
    def test_resolves_runtime_binding_from_managed_manifests(self) -> None:
        manager = RuntimeManager(
            runtime_manifests=[
                RuntimeManifest(
                    runtime_id="ffmpeg-7.1.0",
                    component="ffmpeg",
                    version="7.1.0",
                    component_paths={"ffmpeg": "AtelierData/runtimes/ffmpeg/bin/ffmpeg.exe"},
                    capabilities=["video", "audio", "cpu"],
                )
            ],
            model_assets=[
                ModelAssetManifest(
                    model_id="demo-asr",
                    backend="simulated",
                    version="1",
                    local_path="AtelierData/models/demo-asr",
                    capabilities=["asr"],
                )
            ],
        )

        binding = manager.resolve(
            RuntimeRequest(
                components=["ffmpeg"],
                capabilities=["video"],
                model_ids=["demo-asr"],
            )
        )

        self.assertEqual(binding.component_paths["ffmpeg"], "AtelierData/runtimes/ffmpeg/bin/ffmpeg.exe")
        self.assertEqual(binding.model_paths["demo-asr"], "AtelierData/models/demo-asr")
        self.assertNotIn("PATH", binding.env)

    def test_missing_component_raises_runtime_error(self) -> None:
        manager = RuntimeManager(runtime_manifests=[], model_assets=[])

        with self.assertRaisesRegex(RuntimeError, "missing runtime component"):
            manager.resolve(RuntimeRequest(components=["ffmpeg"]))


if __name__ == "__main__":
    unittest.main()
