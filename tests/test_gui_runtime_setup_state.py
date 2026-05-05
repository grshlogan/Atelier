import unittest

from atelier.gui.runtime_setup_state import build_runtime_setup_view_state
from atelier.runtime.setup import (
    ModelAssetSnapshot,
    RuntimeComponentSnapshot,
    RuntimeSetupSnapshot,
)


class GuiRuntimeSetupStateTests(unittest.TestCase):
    def test_builds_gui_view_state_from_runtime_setup_snapshot(self) -> None:
        snapshot = RuntimeSetupSnapshot(
            runtimes=[
                RuntimeComponentSnapshot(
                    runtime_id="ffprobe-local",
                    component="ffprobe",
                    display_name="FFprobe Local",
                    version="7.1.0",
                    kind="tool",
                    profile_kind="local",
                    status="ready",
                    capabilities=["metadata", "video"],
                    checked_paths={"ffprobe": "C:/Tools/ffprobe.exe"},
                ),
                RuntimeComponentSnapshot(
                    runtime_id="python-worker-dev",
                    component="python.worker",
                    display_name="Developer Worker Python",
                    version="3.11",
                    kind="worker_env",
                    profile_kind="dev",
                    status="missing",
                    capabilities=["worker", "python"],
                    issues=["missing component path: python"],
                    repair_hints=["Register or repair the python.worker runtime path."],
                ),
            ],
            models=[
                ModelAssetSnapshot(
                    model_id="demo-asr",
                    display_name="Demo ASR",
                    model_family="demo",
                    backend="simulated",
                    version="1",
                    profile_kind="local",
                    status="ready",
                    task_types=["asr"],
                    capabilities=["asr"],
                )
            ],
        )

        state = build_runtime_setup_view_state(snapshot)

        self.assertEqual(state.summary.runtime_count, 2)
        self.assertEqual(state.summary.model_count, 1)
        self.assertEqual(state.summary.ready_runtime_count, 1)
        self.assertEqual(state.summary.problem_count, 1)
        self.assertEqual(state.components[0].title, "FFprobe Local")
        self.assertEqual(state.components[0].subtitle, "ffprobe | 7.1.0 | local")
        self.assertEqual(state.components[0].status_label, "Ready")
        self.assertEqual(state.components[0].detail_lines, ["metadata, video"])
        self.assertEqual(state.components[1].status_label, "Missing")
        self.assertIn("missing component path: python", state.components[1].detail_lines)
        self.assertIn("Register or repair", state.components[1].detail_lines[-1])
        self.assertEqual(state.models[0].title, "Demo ASR")
        self.assertEqual(state.models[0].subtitle, "simulated | demo | local")
        self.assertEqual(state.models[0].detail_lines, ["tasks: asr", "capabilities: asr"])
        self.assertFalse(state.actions["register_ffprobe"].enabled)
        self.assertFalse(state.actions["register_worker_python"].enabled)
        self.assertTrue(state.actions["register_ffmpeg"].enabled)
        self.assertTrue(state.actions["register_demo_model"].enabled)
        self.assertTrue(state.actions["refresh"].enabled)


if __name__ == "__main__":
    unittest.main()
