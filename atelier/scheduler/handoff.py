from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Literal

from atelier.domain.execution_plan import ExecutionTask
from atelier.storage.repositories import fetch_task_dependency_ids, fetch_task_output_artifacts


MaterializationStatus = Literal["ready", "blocked"]


@dataclass(frozen=True)
class TaskInputMaterialization:
    status: MaterializationStatus
    task: ExecutionTask
    error_code: str = ""
    message: str = ""


def materialize_downstream_task_inputs(
    connection: sqlite3.Connection,
    task: ExecutionTask,
) -> TaskInputMaterialization:
    if task.node_type != "output.export" or task.params.get("input_path"):
        return TaskInputMaterialization(status="ready", task=task)

    artifact_type = task.params.get("artifact_type")
    if not isinstance(artifact_type, str) or not artifact_type.strip():
        artifact_type = None

    candidates = []
    for upstream_task_id in fetch_task_dependency_ids(connection, task.task_id):
        candidates.extend(
            fetch_task_output_artifacts(
                connection,
                upstream_task_id,
                artifact_type=artifact_type,
            )
        )

    if not candidates:
        return TaskInputMaterialization(
            status="blocked",
            task=task,
            error_code="UPSTREAM_ARTIFACT_MISSING",
            message=f"no upstream output artifact for task: {task.task_id}",
        )
    if len(candidates) > 1:
        return TaskInputMaterialization(
            status="blocked",
            task=task,
            error_code="UPSTREAM_ARTIFACT_AMBIGUOUS",
            message=f"multiple upstream output artifacts for task: {task.task_id}",
        )

    params = dict(task.params)
    params["input_path"] = candidates[0].path
    return TaskInputMaterialization(
        status="ready",
        task=task.model_copy(update={"params": params}),
    )
