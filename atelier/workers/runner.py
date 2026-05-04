from __future__ import annotations

import os
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from atelier.workers.protocol import WorkerEventPayload, WorkerProtocolError, parse_worker_event_stream


@dataclass(frozen=True)
class WorkerProcessSpec:
    command_args: tuple[str, ...]
    task_file: Path
    work_dir: Path
    env: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class WorkerProcessResult:
    events: list[WorkerEventPayload]
    stderr: str
    returncode: int


class WorkerProcessProtocolError(WorkerProtocolError):
    def __init__(self, message: str, *, stderr: str, returncode: int) -> None:
        super().__init__(message)
        self.stderr = stderr
        self.returncode = returncode


def run_worker_process(spec: WorkerProcessSpec) -> WorkerProcessResult:
    if not spec.command_args:
        raise ValueError("Worker command_args must not be empty")

    command = [*spec.command_args, "--task-file", str(spec.task_file)]
    process_env = {**os.environ, **dict(spec.env)}
    completed = subprocess.run(
        command,
        cwd=spec.work_dir,
        env=process_env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    try:
        events = parse_worker_event_stream(completed.stdout.splitlines(keepends=True))
    except WorkerProtocolError as exc:
        raise WorkerProcessProtocolError(
            f"Worker protocol error: {exc}",
            stderr=completed.stderr,
            returncode=completed.returncode,
        ) from exc

    return WorkerProcessResult(
        events=events,
        stderr=completed.stderr,
        returncode=completed.returncode,
    )
