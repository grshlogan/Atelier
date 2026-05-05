from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import json
import time

from atelier.adapters.base import AdapterContext, AdapterExecutionError, AdapterResult, WorkerAdapter
from atelier.adapters.command import CommandExecutionError, CommandResult, CommandSpec, run_command
from atelier.domain.worker_event import ArtifactRef


CommandRunner = Callable[[CommandSpec], CommandResult]


class FFprobeMetadataAdapter(WorkerAdapter):
    node_type = "metadata.probe"
    adapter_version = "1"

    def __init__(self, command_runner: CommandRunner = run_command) -> None:
        self._command_runner = command_runner

    def run(self, context: AdapterContext) -> AdapterResult:
        started_at = time.monotonic()
        ffprobe_path = _required_component_path(context, "ffprobe")
        input_path = _required_input_path(context)
        context.work_dir.mkdir(parents=True, exist_ok=True)

        spec = CommandSpec(
            executable=ffprobe_path,
            args=[
                "-v",
                "error",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                str(input_path),
            ],
            cwd=context.work_dir,
            env=context.runtime_binding.env,
            redacted_args=[
                "-v",
                "error",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                str(input_path),
            ],
        )
        try:
            command_result = self._command_runner(spec)
        except CommandExecutionError as exc:
            raise AdapterExecutionError(
                f"ffprobe command failed: {exc.stderr.strip() or exc}",
                error_code="DEPENDENCY",
                recoverable=True,
            ) from exc

        try:
            payload = json.loads(command_result.stdout)
        except json.JSONDecodeError as exc:
            raise AdapterExecutionError(
                f"invalid ffprobe JSON: {exc.msg}",
                error_code="DEPENDENCY",
                recoverable=True,
            ) from exc
        if not isinstance(payload, dict):
            raise AdapterExecutionError(
                "invalid ffprobe JSON: expected object",
                error_code="DEPENDENCY",
                recoverable=True,
            )

        output_path = context.work_dir / "probe.json"
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        metadata = _summarize_probe(payload)
        artifact = ArtifactRef(
            artifact_id=f"{context.task.task_id}-metadata-probe",
            artifact_type="metadata",
            path="probe.json",
        )
        return AdapterResult(
            artifacts=[artifact],
            duration_seconds=time.monotonic() - started_at,
            metadata=metadata,
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


def _summarize_probe(payload: dict) -> dict:
    streams = payload.get("streams")
    if not isinstance(streams, list):
        streams = []
    format_payload = payload.get("format")
    if not isinstance(format_payload, dict):
        format_payload = {}

    video_streams = [stream for stream in streams if _stream_type(stream) == "video"]
    audio_streams = [stream for stream in streams if _stream_type(stream) == "audio"]
    subtitle_streams = [stream for stream in streams if _stream_type(stream) == "subtitle"]
    first_video = video_streams[0] if video_streams else {}
    if not isinstance(first_video, dict):
        first_video = {}

    return {
        "duration_sec": _duration(format_payload.get("duration")),
        "format_name": str(format_payload.get("format_name", "")),
        "video_streams": len(video_streams),
        "audio_streams": len(audio_streams),
        "subtitle_streams": len(subtitle_streams),
        "codec": str(first_video.get("codec_name", "")),
        "resolution": _resolution(first_video),
        "fps": _fps(first_video.get("avg_frame_rate")),
    }


def _stream_type(stream: object) -> str:
    if not isinstance(stream, dict):
        return ""
    value = stream.get("codec_type")
    return value if isinstance(value, str) else ""


def _duration(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _resolution(stream: dict) -> str:
    width = stream.get("width")
    height = stream.get("height")
    if isinstance(width, int) and isinstance(height, int):
        return f"{width}x{height}"
    return ""


def _fps(value: object) -> float | None:
    if not isinstance(value, str) or not value or value == "0/0":
        return None
    if "/" not in value:
        return _duration(value)
    numerator, denominator = value.split("/", 1)
    try:
        return float(numerator) / float(denominator)
    except (TypeError, ValueError, ZeroDivisionError):
        return None
