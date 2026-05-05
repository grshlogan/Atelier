import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from atelier.adapters.base import AdapterContext, AdapterExecutionError
from atelier.adapters.command import CommandExecutionError, CommandResult, CommandSpec
from atelier.domain.execution_plan import ExecutionTask
from atelier.domain.resources import ResourceRequest, RuntimeBinding, RuntimeRequest

try:
    from atelier.adapters.ffmpeg import FFmpegAudioExtractAdapter
except ImportError:
    FFmpegAudioExtractAdapter = None


class FFmpegAudioExtractAdapterTests(unittest.TestCase):
    def test_runs_ffmpeg_from_runtime_binding_and_writes_audio_artifact(self) -> None:
        self.assertIsNotNone(FFmpegAudioExtractAdapter, "FFmpegAudioExtractAdapter should exist")
        assert FFmpegAudioExtractAdapter is not None
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_path = root / "input.mp4"
            input_path.write_bytes(b"fake media")
            captured_specs: list[CommandSpec] = []

            def fake_runner(spec: CommandSpec) -> CommandResult:
                captured_specs.append(spec)
                (spec.cwd / "audio.wav").write_bytes(b"fake wav")
                return CommandResult(returncode=0, stdout="", stderr="", redacted_command=[])

            adapter = FFmpegAudioExtractAdapter(command_runner=fake_runner)
            context = AdapterContext(
                task=_task(params={"input_path": str(input_path)}),
                runtime_binding=RuntimeBinding(
                    runtime_id="ffmpeg-local",
                    component_paths={"ffmpeg": "C:/Tools/ffmpeg.exe"},
                ),
                work_dir=root / "work",
            )

            result = adapter.run(context)

            self.assertEqual(len(captured_specs), 1)
            self.assertEqual(captured_specs[0].executable, Path("C:/Tools/ffmpeg.exe"))
            self.assertEqual(
                captured_specs[0].args,
                ["-y", "-i", str(input_path), "-vn", "audio.wav"],
            )
            self.assertEqual(captured_specs[0].cwd, root / "work")
            self.assertEqual(len(result.artifacts), 1)
            self.assertEqual(result.artifacts[0].artifact_type, "audio")
            self.assertEqual(result.artifacts[0].path, "audio.wav")
            self.assertTrue((root / "work" / "audio.wav").is_file())
            self.assertEqual(result.metadata["codec"], "pcm_s16le")

    def test_missing_runtime_path_is_structured_failure(self) -> None:
        self.assertIsNotNone(FFmpegAudioExtractAdapter, "FFmpegAudioExtractAdapter should exist")
        assert FFmpegAudioExtractAdapter is not None
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_path = root / "input.mp4"
            input_path.write_bytes(b"fake media")
            adapter = FFmpegAudioExtractAdapter(command_runner=_unused_runner)
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
        self.assertIsNotNone(FFmpegAudioExtractAdapter, "FFmpegAudioExtractAdapter should exist")
        assert FFmpegAudioExtractAdapter is not None
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            adapter = FFmpegAudioExtractAdapter(command_runner=_unused_runner)
            context = AdapterContext(
                task=_task(params={"input_path": str(root / "missing.mp4")}),
                runtime_binding=RuntimeBinding(
                    runtime_id="ffmpeg-local",
                    component_paths={"ffmpeg": "C:/Tools/ffmpeg.exe"},
                ),
                work_dir=root / "work",
            )

            with self.assertRaises(AdapterExecutionError) as raised:
                adapter.run(context)

            self.assertEqual(raised.exception.error_code, "INPUT_MISSING")
            self.assertFalse(raised.exception.recoverable)

    def test_ffmpeg_command_failure_is_structured_failure(self) -> None:
        self.assertIsNotNone(FFmpegAudioExtractAdapter, "FFmpegAudioExtractAdapter should exist")
        assert FFmpegAudioExtractAdapter is not None
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_path = root / "input.mp4"
            input_path.write_bytes(b"fake media")

            def failing_runner(spec: CommandSpec) -> CommandResult:
                raise CommandExecutionError(
                    "ffmpeg failed",
                    returncode=1,
                    stdout="",
                    stderr="no audio stream",
                    redacted_command=[str(spec.executable), *spec.redacted_args],
                )

            adapter = FFmpegAudioExtractAdapter(command_runner=failing_runner)
            context = AdapterContext(
                task=_task(params={"input_path": str(input_path)}),
                runtime_binding=RuntimeBinding(
                    runtime_id="ffmpeg-local",
                    component_paths={"ffmpeg": "C:/Tools/ffmpeg.exe"},
                ),
                work_dir=root / "work",
            )

            with self.assertRaises(AdapterExecutionError) as raised:
                adapter.run(context)

            self.assertEqual(raised.exception.error_code, "DEPENDENCY")
            self.assertTrue(raised.exception.recoverable)
            self.assertIn("no audio stream", raised.exception.message)

    def test_success_without_audio_output_is_structured_failure(self) -> None:
        self.assertIsNotNone(FFmpegAudioExtractAdapter, "FFmpegAudioExtractAdapter should exist")
        assert FFmpegAudioExtractAdapter is not None
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_path = root / "input.mp4"
            input_path.write_bytes(b"fake media")

            def no_output_runner(spec: CommandSpec) -> CommandResult:
                return CommandResult(returncode=0, stdout="", stderr="", redacted_command=[])

            adapter = FFmpegAudioExtractAdapter(command_runner=no_output_runner)
            context = AdapterContext(
                task=_task(params={"input_path": str(input_path)}),
                runtime_binding=RuntimeBinding(
                    runtime_id="ffmpeg-local",
                    component_paths={"ffmpeg": "C:/Tools/ffmpeg.exe"},
                ),
                work_dir=root / "work",
            )

            with self.assertRaises(AdapterExecutionError) as raised:
                adapter.run(context)

            self.assertEqual(raised.exception.error_code, "DEPENDENCY")
            self.assertTrue(raised.exception.recoverable)
            self.assertIn("did not create audio output", raised.exception.message)


def _task(params: dict[str, str]) -> ExecutionTask:
    return ExecutionTask(
        task_id="task-audio-extract",
        source_node_id="node-audio-extract",
        node_type="media.audio_extract",
        params=params,
        resource_request=ResourceRequest(device_type="cpu"),
        runtime_request=RuntimeRequest(components=["ffmpeg"], capabilities=["audio-extract"]),
    )


def _unused_runner(spec: CommandSpec) -> CommandResult:
    raise AssertionError("command runner should not be called")


if __name__ == "__main__":
    unittest.main()
