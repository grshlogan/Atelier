from __future__ import annotations

from atelier.domain.execution_plan import ExecutionTask
from atelier.domain.worker_event import (
    ArtifactEvent,
    ArtifactRef,
    CompletedEvent,
    ProgressEvent,
    StartedEvent,
    WorkerEvent,
)
from atelier.core.time import utc_now_iso


def run_simulated_task(task: ExecutionTask, artifact_path: str) -> list[WorkerEvent]:
    timestamp = utc_now_iso()
    artifact_id = f"{task.task_id}-artifact-0"
    artifact_ref = ArtifactRef(
        artifact_id=artifact_id,
        artifact_type="metadata",
        path=artifact_path,
    )
    return [
        StartedEvent(
            task_id=task.task_id,
            timestamp=timestamp,
            seq=0,
            worker_pid=0,
            worker_version="simulated",
            node_type=task.node_type,
        ),
        ProgressEvent(
            task_id=task.task_id,
            timestamp=timestamp,
            seq=1,
            current=1,
            total=1,
            unit="steps",
            percent=100.0,
            stage="simulate",
        ),
        ArtifactEvent(
            task_id=task.task_id,
            timestamp=timestamp,
            seq=2,
            artifact_id=artifact_id,
            artifact_type="metadata",
            path=artifact_path,
            metadata={"simulated": True},
        ),
        CompletedEvent(
            task_id=task.task_id,
            timestamp=timestamp,
            seq=3,
            artifacts=[artifact_ref],
            duration_seconds=0.0,
        ),
    ]
