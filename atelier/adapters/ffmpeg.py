from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import time

from atelier.adapters.base import AdapterContext, AdapterExecutionError, AdapterResult, WorkerAdapter
from atelier.adapters.command import CommandExecutionError, CommandResult, CommandSpec, run_command
from atelier.domain.worker_event import ArtifactRef


CommandRunner = Callable[[CommandSpec], CommandResult]


class FFmpegAudioExtractAdapter(WorkerAdapter):
    node_type = "media.audio_extract"
    adapter_version = "1"

    def __init__(self, command_runner: CommandRunner = run_command) -> None:
        self._command_runner = command_runner

    def run(self, context: AdapterContext) -> AdapterResult:
        started_at = time.monotonic()
        ffmpeg_path = _required_component_path(context, "ffmpeg")
        input_path = _required_input_path(context)
        context.work_dir.mkdir(parents=True, exist_ok=True)
        output_name = "audio.wav"
        output_path = context.work_dir / output_name

        spec = CommandSpec(
            executable=ffmpeg_path,
            args=[
                "-y",
                "-i",
                str(input_path),
                "-vn",
                output_name,
            ],
            cwd=context.work_dir,
            env=context.runtime_binding.env,
            redacted_args=[
                "-y",
                "-i",
                str(input_path),
                "-vn",
                output_name,
            ],
        )
        try:
            self._command_runner(spec)
        except CommandExecutionError as exc:
            raise AdapterExecutionError(
                f"ffmpeg command failed: {exc.stderr.strip() or exc}",
                error_code="DEPENDENCY",
                recoverable=True,
            ) from exc

        if not output_path.is_file():
            raise AdapterExecutionError(
                f"ffmpeg command did not create audio output: {output_name}",
                error_code="DEPENDENCY",
                recoverable=True,
            )

        artifact = ArtifactRef(
            artifact_id=f"{context.task.task_id}-audio-extract",
            artifact_type="audio",
            path=output_name,
        )
        return AdapterResult(
            artifacts=[artifact],
            duration_seconds=time.monotonic() - started_at,
            metadata={
                "codec": "pcm_s16le",
            },
        )


def _required_component_path(context: AdapterContext, component: str) -> Path:
    raw_path = context.runtime_binding.component_paths.get(component)
    if not raw_path:
        raise AdapterExecutionError(
            f"missing runtime component path: {component}",
            error_code="RUNTIME_MISSING",
            recoverable=False,
        )
    return Path(raw_path)


def _required_input_path(context: AdapterContext) -> Path:
    raw_path = context.task.params.get("input_path")
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise AdapterExecutionError(
            "missing input_path param",
            error_code="INPUT_MISSING",
            recoverable=False,
        )
    path = Path(raw_path)
    if not path.exists() or not path.is_file():
        raise AdapterExecutionError(
            f"missing input file: {raw_path}",
            error_code="INPUT_MISSING",
            recoverable=False,
        )
    return path
