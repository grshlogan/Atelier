from __future__ import annotations

import os
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from atelier.workers.protocol import WorkerEventPayload, parse_worker_event_stream


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
    events = parse_worker_event_stream(completed.stdout.splitlines(keepends=True))

    return WorkerProcessResult(
        events=events,
        stderr=completed.stderr,
        returncode=completed.returncode,
    )
