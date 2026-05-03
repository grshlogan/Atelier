from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class WorkbenchTaskItem:
    task_id: str
    node_type: str
    status: str
    resource_device_id: str | None
    event_count: int
    artifact_paths: list[str]


@dataclass(frozen=True)
class WorkbenchSnapshot:
    tasks: list[WorkbenchTaskItem]


def read_workbench_snapshot(connection: sqlite3.Connection) -> WorkbenchSnapshot:
    rows = connection.execute(
        """
        SELECT
            task.task_id,
            task.node_type,
            task.status,
            task.resource_binding,
            COUNT(event.event_id) AS event_count
        FROM execution_tasks AS task
        LEFT JOIN task_events AS event
          ON event.task_id = task.task_id
        GROUP BY task.task_id
        ORDER BY task.created_at, task.task_id
        """
    ).fetchall()
    return WorkbenchSnapshot(
        tasks=[
            WorkbenchTaskItem(
                task_id=row[0],
                node_type=row[1],
                status=row[2],
                resource_device_id=_resource_device_id(row[3]),
                event_count=row[4],
                artifact_paths=_artifact_paths(connection, row[0]),
            )
            for row in rows
        ]
    )


def _resource_device_id(resource_binding_json: str | None) -> str | None:
    if resource_binding_json is None:
        return None
    return json.loads(resource_binding_json).get("device_id")


def _artifact_paths(connection: sqlite3.Connection, task_id: str) -> list[str]:
    rows = connection.execute(
        """
        SELECT path
        FROM artifacts
        WHERE task_id = ?
        ORDER BY created_at, artifact_id
        """,
        (task_id,),
    ).fetchall()
    return [row[0] for row in rows]
