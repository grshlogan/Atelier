import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from atelier.adapters.base import AdapterContext, AdapterExecutionError
from atelier.adapters.command import CommandResult, CommandSpec
from atelier.adapters.ffprobe import FFprobeMetadataAdapter
from atelier.domain.execution_plan import ExecutionTask
from atelier.domain.resources import ResourceRequest, RuntimeBinding, RuntimeRequest


class FFprobeMetadataAdapterTests(unittest.TestCase):
    def test_runs_ffprobe_from_runtime_binding_and_writes_metadata_artifact(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_path = root / "input.mp4"
            input_path.write_bytes(b"fake media")
            captured_specs: list[CommandSpec] = []
            expected_payload = {
                "format": {
                    "duration": "12.5",
                    "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
                },
                "streams": [
                    {
                        "codec_type": "video",
                        "codec_name": "h264",
                        "width": 1920,
                        "height": 1080,
                        "avg_frame_rate": "30000/1001",
                    },
                    {
                        "codec_type": "audio",
                        "codec_name": "aac",
                    },
                ],
            }

            def fake_runner(spec: CommandSpec) -> CommandResult:
                captured_specs.append(spec)
                return CommandResult(
                    returncode=0,
                    stdout=json.dumps(expected_payload),
                    stderr="",
                    redacted_command=[],
                )

            adapter = FFprobeMetadataAdapter(command_runner=fake_runner)
            context = AdapterContext(
                task=_task(params={"input_path": str(input_path)}),
                runtime_binding=RuntimeBinding(
                    runtime_id="ffprobe-local",
                    component_paths={"ffprobe": "C:/Tools/ffprobe.exe"},
                ),
                work_dir=root / "work",
            )

            result = adapter.run(context)

            self.assertEqual(len(captured_specs), 1)
            self.assertEqual(captured_specs[0].executable, Path("C:/Tools/ffprobe.exe"))
            self.assertEqual(
                captured_specs[0].args,
                [
                    "-v",
                    "error",
                    "-print_format",
                    "json",
                    "-show_format",
                    "-show_streams",
                    str(input_path),
                ],
            )
            self.assertEqual(len(result.artifacts), 1)
            self.assertEqual(result.artifacts[0].artifact_type, "metadata")
            self.assertEqual(result.artifacts[0].path, "probe.json")
            self.assertEqual(result.metadata["duration_sec"], 12.5)
            self.assertEqual(result.metadata["format_name"], "mov,mp4,m4a,3gp,3g2,mj2")
            self.assertEqual(result.metadata["video_streams"], 1)
            self.assertEqual(result.metadata["audio_streams"], 1)
            self.assertEqual(result.metadata["resolution"], "1920x1080")
            self.assertEqual(result.metadata["fps"], 30000 / 1001)
            self.assertEqual(
                json.loads((root / "work" / "probe.json").read_text(encoding="utf-8")),
                expected_payload,
            )

    def test_missing_runtime_path_is_structured_failure(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_path = root / "input.mp4"
            input_path.write_bytes(b"fake media")
            adapter = FFprobeMetadataAdapter(command_runner=_unused_runner)
            context = AdapterContext(
                task=_task(params={"input_path": str(input_path)}),
                runtime_binding=RuntimeBinding(runtime_id="runtime:none", component_paths={}),
                work_dir=root / "work",
            )

            with self.assertRaises(AdapterExecutionError) as raised:
                adapter.run(context)

            self.assertEqual(raised.exception.error_code, "RUNTIME_MISSING")
            self.assertFalse(raised.exception.recoverable)

    def test_missing_input_path_is_structured_failure(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            adapter = FFprobeMetadataAdapter(command_runner=_unused_runner)
            context = AdapterContext(
                task=_task(params={"input_path": str(root / "missing.mp4")}),
                runtime_binding=RuntimeBinding(
                    runtime_id="ffprobe-local",
                    component_paths={"ffprobe": "C:/Tools/ffprobe.exe"},
                ),
                work_dir=root / "work",
            )

            with self.assertRaises(AdapterExecutionError) as raised:
                adapter.run(context)

            self.assertEqual(raised.exception.error_code, "INPUT_MISSING")
            self.assertFalse(raised.exception.recoverable)

    def test_invalid_ffprobe_json_is_structured_failure(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_path = root / "input.mp4"
            input_path.write_bytes(b"fake media")

            def invalid_json_runner(spec: CommandSpec) -> CommandResult:
                return CommandResult(
                    returncode=0,
                    stdout="not json",
                    stderr="",
                    redacted_command=[str(spec.executable), *spec.redacted_args],
                )

            adapter = FFprobeMetadataAdapter(command_runner=invalid_json_runner)
            context = AdapterContext(
                task=_task(params={"input_path": str(input_path)}),
                runtime_binding=RuntimeBinding(
                    runtime_id="ffprobe-local",
                    component_paths={"ffprobe": "C:/Tools/ffprobe.exe"},
                ),
                work_dir=root / "work",
            )

            with self.assertRaises(AdapterExecutionError) as raised:
                adapter.run(context)

            self.assertEqual(raised.exception.error_code, "DEPENDENCY")
            self.assertTrue(raised.exception.recoverable)
            self.assertIn("invalid ffprobe JSON", raised.exception.message)


def _task(params: dict[str, str]) -> ExecutionTask:
    return ExecutionTask(
        task_id="task-metadata-probe",
        source_node_id="node-metadata-probe",
        node_type="metadata.probe",
        params=params,
        resource_request=ResourceRequest(device_type="cpu"),
        runtime_request=RuntimeRequest(components=["ffprobe"], capabilities=["metadata"]),
    )


def _unused_runner(spec: CommandSpec) -> CommandResult:
    raise AssertionError("command runner should not be called")


if __name__ == "__main__":
    unittest.main()
