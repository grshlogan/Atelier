from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

from atelier.domain.execution_plan import ExecutionTask
from atelier.workers.runner import WorkerProcessSpec


DEFAULT_WORKER_TASK_FILE_NAME = "task.json"


def write_worker_task_file(
    task: ExecutionTask,
    task_dir: Path,
    file_name: str = DEFAULT_WORKER_TASK_FILE_NAME,
) -> Path:
    task_dir.mkdir(parents=True, exist_ok=True)
    task_file = task_dir / file_name
    temp_file = task_dir / f"{file_name}.tmp"
    payload = task.model_dump(mode="json")

    temp_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temp_file.replace(task_file)
    return task_file


def build_worker_process_spec(
    task: ExecutionTask,
    command_args: tuple[str, ...],
    work_root: Path,
    env: Mapping[str, str] | None = None,
) -> WorkerProcessSpec:
    task_dir = work_root / task.task_id
    task_file = write_worker_task_file(task, task_dir)
    runtime_env = task.runtime_binding.env if task.runtime_binding is not None else {}
    merged_env = {**runtime_env, **dict(env or {})}

    return WorkerProcessSpec(
        command_args=command_args,
        task_file=task_file,
        work_dir=task_dir,
        env=merged_env,
    )
