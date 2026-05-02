from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Iterable

from atelier.core.time import utc_now_iso
from atelier.domain.execution_plan import ExecutionPlan, ExecutionTask
from atelier.domain.resources import ResourceBinding, ResourceRequest, RuntimeRequest
from atelier.domain.worker_event import (
    ArtifactEvent,
    CompletedEvent,
    FailedEvent,
    WorkerEvent,
    task_status_from_terminal_event,
)
from atelier.workflow.graph import WorkflowGraph


@dataclass(frozen=True)
class ResourceLockRecord:
    lock_id: str
    task_id: str
    device_id: str
    lock_type: str
    vram_mb: int | None
    acquired_at: str
    released_at: str | None


def persist_planned_execution(
    connection: sqlite3.Connection,
    *,
    project_id: str,
    project_name: str,
    project_root: str,
    job_id: str,
    job_name: str,
    graph: WorkflowGraph,
    plan: ExecutionPlan,
) -> None:
    now = utc_now_iso()
    connection.execute(
        """
        INSERT INTO projects (project_id, name, root_dir, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (project_id, project_name, project_root, now, now),
    )
    connection.execute(
        """
        INSERT INTO workflow_graphs
            (graph_id, name, description, graph_json, node_count, edge_count, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            graph.graph_id,
            graph.name,
            graph.description,
            _dump_json(graph),
            graph.node_count(),
            graph.edge_count(),
            now,
            now,
        ),
    )
    connection.execute(
        """
        INSERT INTO jobs
            (job_id, project_id, name, workflow_graph_id, execution_plan_id, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (job_id, project_id, job_name, graph.graph_id, plan.plan_id, "queued", now, now),
    )
    connection.execute(
        """
        INSERT INTO execution_plans
            (plan_id, job_id, workflow_graph_id, status, phases_json, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (plan.plan_id, job_id, graph.graph_id, plan.status, _dump_json({"phases": ["phase-1"]}), now, now),
    )
    for task in plan.tasks:
        _insert_execution_task(connection, plan.plan_id, task, now)
    connection.commit()


def record_worker_events(connection: sqlite3.Connection, events: Iterable[WorkerEvent]) -> None:
    for event in events:
        connection.execute(
            """
            INSERT INTO task_events (event_id, task_id, event_type, payload, seq, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                f"{event.task_id}-{event.seq}",
                event.task_id,
                event.type,
                _dump_json(event),
                event.seq,
                event.timestamp,
            ),
        )
        if isinstance(event, ArtifactEvent):
            _record_artifact_event(connection, event)
        if isinstance(event, CompletedEvent | FailedEvent):
            _update_task_from_terminal_event(connection, event)
    connection.commit()


def fetch_task_event_types(connection: sqlite3.Connection, task_id: str) -> list[str]:
    rows = connection.execute(
        "SELECT event_type FROM task_events WHERE task_id = ? ORDER BY seq",
        (task_id,),
    ).fetchall()
    return [row[0] for row in rows]


def fetch_artifact_paths(connection: sqlite3.Connection, task_id: str) -> list[str]:
    rows = connection.execute(
        "SELECT path FROM artifacts WHERE task_id = ? ORDER BY created_at, artifact_id",
        (task_id,),
    ).fetchall()
    return [row[0] for row in rows]


def fetch_task_status(connection: sqlite3.Connection, task_id: str) -> str:
    row = connection.execute(
        "SELECT status FROM execution_tasks WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    if row is None:
        raise LookupError(f"missing execution task: {task_id}")
    return row[0]


def fetch_next_runnable_task(connection: sqlite3.Connection, plan_id: str) -> ExecutionTask | None:
    rows = connection.execute(
        """
        SELECT
            task_id, phase_id, lane_id, source_node_id, node_type, params_json,
            resource_request, runtime_request, failure_policy, cache_key, retry_count
        FROM execution_tasks
        WHERE plan_id = ? AND status = 'pending'
        ORDER BY created_at, task_id
        """,
        (plan_id,),
    ).fetchall()
    for row in rows:
        task_id = row[0]
        if _dependencies_are_completed(connection, task_id):
            return _task_from_row(row)
    return None


def mark_task_running(
    connection: sqlite3.Connection,
    task_id: str,
    resource_binding: ResourceBinding,
) -> None:
    now = utc_now_iso()
    cursor = connection.execute(
        """
        UPDATE execution_tasks
        SET status = 'running',
            resource_binding = ?,
            started_at = ?,
            updated_at = ?
        WHERE task_id = ? AND status = 'pending'
        """,
        (_dump_json(resource_binding), now, now, task_id),
    )
    if cursor.rowcount == 0:
        raise RuntimeError(f"task is not claimable: {task_id}")
    connection.execute(
        """
        INSERT INTO resource_locks
            (lock_id, task_id, device_id, lock_type, vram_mb, acquired_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            f"{task_id}-resource-lock",
            task_id,
            resource_binding.device_id,
            "task",
            resource_binding.allocated_vram_mb,
            now,
        ),
    )
    connection.commit()


def fetch_task_resource_binding(connection: sqlite3.Connection, task_id: str) -> ResourceBinding:
    row = connection.execute(
        "SELECT resource_binding FROM execution_tasks WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    if row is None or row[0] is None:
        raise LookupError(f"missing task resource binding: {task_id}")
    return ResourceBinding.model_validate(json.loads(row[0]))


def fetch_active_resource_lock(connection: sqlite3.Connection, task_id: str) -> ResourceLockRecord:
    row = connection.execute(
        """
        SELECT lock_id, task_id, device_id, lock_type, vram_mb, acquired_at, released_at
        FROM resource_locks
        WHERE task_id = ? AND released_at IS NULL
        ORDER BY acquired_at DESC, lock_id DESC
        LIMIT 1
        """,
        (task_id,),
    ).fetchone()
    if row is None:
        raise LookupError(f"missing active resource lock: {task_id}")
    return ResourceLockRecord(
        lock_id=row[0],
        task_id=row[1],
        device_id=row[2],
        lock_type=row[3],
        vram_mb=row[4],
        acquired_at=row[5],
        released_at=row[6],
    )


def _insert_execution_task(
    connection: sqlite3.Connection,
    plan_id: str,
    task: ExecutionTask,
    timestamp: str,
) -> None:
    connection.execute(
        """
        INSERT INTO execution_tasks
            (
                task_id, plan_id, phase_id, lane_id, source_node_id, node_type,
                params_json, status, resource_request, resource_binding,
                runtime_request, runtime_binding, failure_policy, cache_key,
                retry_count, created_at, updated_at
            )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task.task_id,
            plan_id,
            task.phase_id,
            task.lane_id,
            task.source_node_id,
            task.node_type,
            _dump_json(task.params),
            task.status,
            _dump_json(task.resource_request),
            _dump_optional_json(task.resource_binding),
            _dump_json(task.runtime_request),
            _dump_optional_json(task.runtime_binding),
            _dump_json(task.failure_policy),
            task.cache_key,
            task.retry_count,
            timestamp,
            timestamp,
        ),
    )
    for depends_on_task_id in task.depends_on_tasks:
        connection.execute(
            """
            INSERT INTO task_dependencies (task_id, depends_on_task_id)
            VALUES (?, ?)
            """,
            (task.task_id, depends_on_task_id),
        )


def _record_artifact_event(connection: sqlite3.Connection, event: ArtifactEvent) -> None:
    connection.execute(
        """
        INSERT OR IGNORE INTO artifacts
            (artifact_id, task_id, artifact_type, path, hash, size_bytes, metadata_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event.artifact_id,
            event.task_id,
            event.artifact_type,
            event.path,
            event.hash,
            event.size_bytes,
            _dump_json(event.metadata),
            event.timestamp,
        ),
    )
    connection.execute(
        """
        INSERT OR IGNORE INTO task_artifacts
            (link_id, task_id, artifact_id, role, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            f"{event.task_id}-{event.artifact_id}-output",
            event.task_id,
            event.artifact_id,
            "output",
            event.timestamp,
        ),
    )


def _update_task_from_terminal_event(
    connection: sqlite3.Connection,
    event: CompletedEvent | FailedEvent,
) -> None:
    status = task_status_from_terminal_event(event)
    connection.execute(
        """
        UPDATE execution_tasks
        SET status = ?, completed_at = ?, updated_at = ?
        WHERE task_id = ?
        """,
        (
            status,
            event.timestamp,
            event.timestamp,
            event.task_id,
        ),
    )
    _release_resource_locks_for_task(connection, event.task_id, event.timestamp)


def _dump_json(value: object) -> str:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    return json.dumps(value, ensure_ascii=True, sort_keys=True)


def _dump_optional_json(value: object | None) -> str | None:
    if value is None:
        return None
    return _dump_json(value)


def _release_resource_locks_for_task(
    connection: sqlite3.Connection,
    task_id: str,
    timestamp: str,
) -> None:
    connection.execute(
        """
        UPDATE resource_locks
        SET released_at = ?,
            heartbeat_at = ?
        WHERE task_id = ?
          AND released_at IS NULL
        """,
        (timestamp, timestamp, task_id),
    )


def _dependencies_are_completed(connection: sqlite3.Connection, task_id: str) -> bool:
    row = connection.execute(
        """
        SELECT COUNT(*)
        FROM task_dependencies AS dependency
        JOIN execution_tasks AS upstream
          ON upstream.task_id = dependency.depends_on_task_id
        WHERE dependency.task_id = ?
          AND upstream.status != 'completed'
        """,
        (task_id,),
    ).fetchone()
    return row[0] == 0


def _task_from_row(row: sqlite3.Row | tuple) -> ExecutionTask:
    return ExecutionTask(
        task_id=row[0],
        phase_id=row[1],
        lane_id=row[2],
        source_node_id=row[3],
        node_type=row[4],
        params=json.loads(row[5]),
        resource_request=ResourceRequest.model_validate(json.loads(row[6])),
        runtime_request=RuntimeRequest.model_validate(json.loads(row[7])),
        failure_policy=json.loads(row[8]),
        cache_key=row[9],
        retry_count=row[10],
    )
