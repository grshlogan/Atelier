from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from atelier.runtime.manager import RuntimeManager
from atelier.scheduler.dispatch import dispatch_claimed_task
from atelier.scheduler.handoff import materialize_downstream_task_inputs
from atelier.scheduler.simple import ClaimedTask, SimpleScheduler
from atelier.storage.repositories import fetch_plan_task_statuses


WorkflowRunStatus = Literal["completed", "failed", "blocked"]


@dataclass(frozen=True)
class WorkflowRunResult:
    plan_id: str
    status: WorkflowRunStatus
    dispatched_task_ids: list[str] = field(default_factory=list)
    stopped_task_id: str = ""
    error_code: str = ""
    message: str = ""


def run_sequential_workflow(
    connection: sqlite3.Connection,
    *,
    plan_id: str,
    scheduler: SimpleScheduler,
    runtime_manager: RuntimeManager,
    work_root: Path,
    command_args: Sequence[str],
    max_steps: int = 100,
) -> WorkflowRunResult:
    dispatched_task_ids: list[str] = []
    command_tuple = tuple(command_args)

    for _ in range(max_steps):
        claimed = scheduler.claim_next_task(connection, plan_id)
        if claimed is None:
            if _all_tasks_completed(connection, plan_id):
                return WorkflowRunResult(
                    plan_id=plan_id,
                    status="completed",
                    dispatched_task_ids=dispatched_task_ids,
                )
            return WorkflowRunResult(
                plan_id=plan_id,
                status="blocked",
                dispatched_task_ids=dispatched_task_ids,
                error_code="NO_RUNNABLE_TASK",
                message="no runnable task is available",
            )

        materialized = materialize_downstream_task_inputs(
            connection,
            claimed.task,
            work_root=work_root,
        )
        if materialized.status == "blocked":
            return WorkflowRunResult(
                plan_id=plan_id,
                status="blocked",
                dispatched_task_ids=dispatched_task_ids,
                stopped_task_id=claimed.task.task_id,
                error_code=materialized.error_code,
                message=materialized.message,
            )

        prepared_claim = ClaimedTask(
            task=materialized.task,
            resource_binding=claimed.resource_binding,
        )
        runtime_binding = runtime_manager.resolve(materialized.task.runtime_request)
        dispatch_result = dispatch_claimed_task(
            connection,
            claimed_task=prepared_claim,
            work_root=work_root,
            command_args=command_tuple,
            runtime_binding=runtime_binding,
        )
        dispatched_task_ids.append(dispatch_result.task_id)
        if dispatch_result.task_status == "failed":
            return WorkflowRunResult(
                plan_id=plan_id,
                status="failed",
                dispatched_task_ids=dispatched_task_ids,
                stopped_task_id=dispatch_result.task_id,
                error_code="TASK_FAILED",
                message=f"task failed: {dispatch_result.task_id}",
            )
        if dispatch_result.task_status == "cancelled":
            return WorkflowRunResult(
                plan_id=plan_id,
                status="failed",
                dispatched_task_ids=dispatched_task_ids,
                stopped_task_id=dispatch_result.task_id,
                error_code="TASK_CANCELLED",
                message=f"task cancelled: {dispatch_result.task_id}",
            )

    return WorkflowRunResult(
        plan_id=plan_id,
        status="blocked",
        dispatched_task_ids=dispatched_task_ids,
        error_code="STEP_LIMIT_REACHED",
        message=f"workflow runner reached max_steps={max_steps}",
    )


def _all_tasks_completed(connection: sqlite3.Connection, plan_id: str) -> bool:
    statuses = fetch_plan_task_statuses(connection, plan_id)
    return bool(statuses) and all(status == "completed" for _, status in statuses)
