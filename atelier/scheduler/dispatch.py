from __future__ import annotations

import sqlite3
import threading
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from atelier.core.time import utc_now_iso
from atelier.domain.execution_plan import TaskStatus
from atelier.domain.worker_event import FailedEvent
from atelier.scheduler.simple import ClaimedTask
from atelier.storage.repositories import fetch_task_status, record_worker_events
from atelier.workers.protocol import WorkerEventPayload
from atelier.workers.runner import (
    WorkerLifecycleConfig,
    WorkerProcessProtocolError,
    run_worker_lifecycle,
    run_worker_process,
)
from atelier.workers.task_file import build_worker_process_spec


@dataclass(frozen=True)
class WorkerDispatchResult:
    task_id: str
    events: list[WorkerEventPayload]
    stderr: str
    returncode: int
    task_status: TaskStatus
    stderr_log_path: Path | None = None
    timed_out: bool = False
    cancelled: bool = False
    killed: bool = False


def dispatch_claimed_task(
    connection: sqlite3.Connection,
    *,
    claimed_task: ClaimedTask,
    work_root: Path,
    command_args: tuple[str, ...],
    env: Mapping[str, str] | None = None,
    lifecycle_config: WorkerLifecycleConfig | None = None,
    cancel_event: threading.Event | None = None,
    stderr_log_path: Path | None = None,
) -> WorkerDispatchResult:
    task = claimed_task.task.model_copy(
        update={
            "resource_binding": claimed_task.resource_binding,
            "status": "running",
        }
    )
    spec = build_worker_process_spec(
        task,
        command_args=command_args,
        work_root=work_root,
        env=env,
    )
    use_lifecycle = (
        lifecycle_config is not None or cancel_event is not None or stderr_log_path is not None
    )
    try:
        if use_lifecycle:
            process_result = run_worker_lifecycle(
                spec,
                config=lifecycle_config,
                cancel_event=cancel_event,
                stderr_log_path=stderr_log_path,
            )
        else:
            process_result = run_worker_process(spec)
    except WorkerProcessProtocolError as exc:
        failed_event = FailedEvent(
            task_id=task.task_id,
            timestamp=utc_now_iso(),
            seq=0,
            error_code="INTERNAL",
            message=str(exc),
            recoverable=False,
        )
        record_worker_events(connection, [failed_event])
        return WorkerDispatchResult(
            task_id=task.task_id,
            events=[failed_event],
            stderr=exc.stderr,
            returncode=exc.returncode,
            task_status=fetch_task_status(connection, task.task_id),
            stderr_log_path=stderr_log_path,
        )

    record_worker_events(connection, process_result.events)
    task_status = fetch_task_status(connection, task.task_id)

    return WorkerDispatchResult(
        task_id=task.task_id,
        events=process_result.events,
        stderr=process_result.stderr,
        returncode=process_result.returncode,
        task_status=task_status,
        stderr_log_path=getattr(process_result, "stderr_log_path", None),
        timed_out=getattr(process_result, "timed_out", False),
        cancelled=getattr(process_result, "cancelled", False),
        killed=getattr(process_result, "killed", False),
    )
