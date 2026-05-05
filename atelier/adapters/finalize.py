from __future__ import annotations

from pathlib import Path
import shutil
import time

from atelier.adapters.base import AdapterContext, AdapterExecutionError, AdapterResult, WorkerAdapter
from atelier.domain.worker_event import ArtifactRef
from atelier.security.package_integrity import sha256_file


class ArtifactFinalizerAdapter(WorkerAdapter):
    node_type = "output.export"
    adapter_version = "1"

    def run(self, context: AdapterContext) -> AdapterResult:
        started_at = time.monotonic()
        source_path = _required_input_path(context)
        output_dir = _required_output_dir(context)
        filename = _safe_output_filename(context, source_path)
        artifact_type = _artifact_type(context)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename

        if output_path.exists():
            raise AdapterExecutionError(
                f"output file already exists: {output_path}",
                error_code="OUTPUT_CONFLICT",
                recoverable=True,
            )

        shutil.copy2(source_path, output_path)
        source_size = source_path.stat().st_size
        output_size = output_path.stat().st_size
        source_hash = sha256_file(source_path)
        output_hash = sha256_file(output_path)
        if source_size != output_size or source_hash != output_hash:
            raise AdapterExecutionError(
                f"final output verification failed: {output_path}",
                error_code="INTERNAL",
                recoverable=False,
            )

        artifact = ArtifactRef(
            artifact_id=f"{context.task.task_id}-final-output",
            artifact_type=artifact_type,
            path=str(output_path),
        )
        return AdapterResult(
            artifacts=[artifact],
            duration_seconds=time.monotonic() - started_at,
            metadata={
                "role": "final_output",
                "source_path": str(source_path),
                "size_bytes": output_size,
                "sha256": output_hash,
            },
        )


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


def _required_output_dir(context: AdapterContext) -> Path:
    raw_path = context.task.params.get("output_dir")
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise AdapterExecutionError(
            "missing output_dir param",
            error_code="PERMISSION",
            recoverable=False,
        )
    return Path(raw_path)


def _safe_output_filename(context: AdapterContext, source_path: Path) -> str:
    raw_filename = context.task.params.get("filename")
    if raw_filename is None or raw_filename == "":
        raw_filename = source_path.name
    if not isinstance(raw_filename, str) or not raw_filename.strip():
        raise AdapterExecutionError(
            "missing output filename",
            error_code="PERMISSION",
            recoverable=False,
        )
    candidate = Path(raw_filename)
    if candidate.is_absolute() or candidate.name != raw_filename or ".." in candidate.parts:
        raise AdapterExecutionError(
            f"unsafe output filename: {raw_filename}",
            error_code="PERMISSION",
            recoverable=False,
        )
    return raw_filename


def _artifact_type(context: AdapterContext) -> str:
    raw_artifact_type = context.task.params.get("artifact_type", "video")
    if not isinstance(raw_artifact_type, str) or not raw_artifact_type.strip():
        return "video"
    return raw_artifact_type
