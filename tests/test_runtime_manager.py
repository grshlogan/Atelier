import unittest

from atelier.domain.resources import RuntimeRequest
from atelier.runtime.manager import RuntimeManager, RuntimeResolutionError
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

    def test_resolution_merges_scoped_runtime_env_without_global_path_lookup(self) -> None:
        manager = RuntimeManager(
            runtime_manifests=[
                RuntimeManifest(
                    runtime_id="ffprobe-local",
                    component="ffprobe",
                    version="7.1.0",
                    component_paths={"ffprobe": "runtimes/components/ffmpeg/bin/ffprobe.exe"},
                    capabilities=["metadata"],
                    env={"ATELIER_FFPROBE_HOME": "runtimes/components/ffmpeg"},
                )
            ]
        )

        binding = manager.resolve(RuntimeRequest(components=["ffprobe"], capabilities=["metadata"]))

        self.assertEqual(binding.runtime_id, "ffprobe-local")
        self.assertEqual(binding.component_paths["ffprobe"], "runtimes/components/ffmpeg/bin/ffprobe.exe")
        self.assertEqual(binding.env["ATELIER_FFPROBE_HOME"], "runtimes/components/ffmpeg")
        self.assertNotIn("Path", binding.env)

    def test_resolution_error_records_subject_and_reason_for_disabled_or_mismatched_runtime(self) -> None:
        disabled_manager = RuntimeManager(
            runtime_manifests=[
                RuntimeManifest(
                    runtime_id="ffprobe-disabled",
                    component="ffprobe",
                    version="7.1.0",
                    status="disabled",
                    capabilities=["metadata"],
                )
            ]
        )
        mismatch_manager = RuntimeManager(
            runtime_manifests=[
                RuntimeManifest(
                    runtime_id="ffprobe-ready",
                    component="ffprobe",
                    version="7.1.0",
                    status="ready",
                    capabilities=["metadata"],
                )
            ]
        )

        with self.assertRaises(RuntimeResolutionError) as disabled_context:
            disabled_manager.resolve(RuntimeRequest(components=["ffprobe"], capabilities=["metadata"]))
        with self.assertRaises(RuntimeResolutionError) as mismatch_context:
            mismatch_manager.resolve(RuntimeRequest(components=["ffprobe"], capabilities=["subtitle"]))

        self.assertEqual(disabled_context.exception.subject_id, "ffprobe")
        self.assertEqual(disabled_context.exception.reason, "disabled")
        self.assertIn("runtime component is disabled", str(disabled_context.exception))
        self.assertEqual(mismatch_context.exception.subject_id, "ffprobe")
        self.assertEqual(mismatch_context.exception.reason, "capability_mismatch")
        self.assertIn("missing capabilities", str(mismatch_context.exception))

    def test_resolution_error_records_missing_model_asset(self) -> None:
        manager = RuntimeManager(model_assets=[])

        with self.assertRaises(RuntimeResolutionError) as context:
            manager.resolve(RuntimeRequest(model_ids=["missing-model"]))

        self.assertEqual(context.exception.subject_id, "missing-model")
        self.assertEqual(context.exception.reason, "missing_model")


if __name__ == "__main__":
    unittest.main()
