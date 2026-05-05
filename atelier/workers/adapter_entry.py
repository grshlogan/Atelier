from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Sequence

from atelier.adapters.base import AdapterContext, AdapterExecutionError
from atelier.adapters.builtins import create_builtin_adapter_registry
from atelier.adapters.registry import AdapterRegistry, AdapterRegistryError
from atelier.core.time import utc_now_iso
from atelier.domain.execution_plan import ExecutionTask
from atelier.domain.worker_event import ArtifactEvent, CompletedEvent, FailedEvent, StartedEvent
from atelier.workers.protocol import format_worker_event_json_line


def run_adapter_task_file(
    task_file: Path,
    *,
    registry: AdapterRegistry | None = None,
) -> list[StartedEvent | ArtifactEvent | CompletedEvent | FailedEvent]:
    task = ExecutionTask.model_validate(json.loads(task_file.read_text(encoding="utf-8")))
    active_registry = registry or create_builtin_adapter_registry()
    events: list[StartedEvent | ArtifactEvent | CompletedEvent | FailedEvent] = [
        StartedEvent(
            task_id=task.task_id,
            timestamp=utc_now_iso(),
            seq=0,
            worker_pid=os.getpid(),
            worker_version="adapter-entry:1",
            node_type=task.node_type,
        )
    ]
    if task.runtime_binding is None:
        events.append(
            FailedEvent(
                task_id=task.task_id,
                timestamp=utc_now_iso(),
                seq=1,
                error_code="RUNTIME_MISSING",
                message="task has no runtime binding",
                recoverable=False,
            )
        )
        return events

    try:
        adapter = active_registry.resolve(task.node_type)
        context = AdapterContext(
            task=task,
            runtime_binding=task.runtime_binding,
            resource_binding=task.resource_binding,
            work_dir=task_file.parent,
        )
        adapter.prepare(context)
        result = adapter.run(context)
    except AdapterExecutionError as exc:
        events.append(
            FailedEvent(
                task_id=task.task_id,
                timestamp=utc_now_iso(),
                seq=1,
                error_code=exc.error_code,
                message=exc.message,
                recoverable=exc.recoverable,
            )
        )
        return events
    except AdapterRegistryError as exc:
        events.append(
            FailedEvent(
                task_id=task.task_id,
                timestamp=utc_now_iso(),
                seq=1,
                error_code="INTERNAL",
                message=str(exc),
                recoverable=False,
            )
        )
        return events

    for artifact in result.artifacts:
        events.append(
            ArtifactEvent(
                task_id=task.task_id,
                timestamp=utc_now_iso(),
                seq=len(events),
                artifact_id=artifact.artifact_id,
                artifact_type=artifact.artifact_type,
                path=artifact.path,
                metadata=result.metadata,
            )
        )
    events.append(
        CompletedEvent(
            task_id=task.task_id,
            timestamp=utc_now_iso(),
            seq=len(events),
            artifacts=result.artifacts,
            duration_seconds=result.duration_seconds,
        )
    )
    return events


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run an Atelier worker adapter task.")
    parser.add_argument("--task-file", type=Path, required=True)
    args = parser.parse_args(argv)

    events = run_adapter_task_file(args.task_file)
    for event in events:
        sys.stdout.write(format_worker_event_json_line(event))
        sys.stdout.flush()
    return 1 if isinstance(events[-1], FailedEvent) else 0


if __name__ == "__main__":
    raise SystemExit(main())
