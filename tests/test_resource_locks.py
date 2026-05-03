from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from atelier.app.paths import AppPaths
from atelier.app.services import open_app_database
from atelier.domain.resources import HardwareSnapshot, ResourceRequest, RuntimeRequest
from atelier.domain.worker_event import FailedEvent
from atelier.planning.simple import build_linear_execution_plan
from atelier.scheduler.simple import SimpleScheduler
from atelier.storage.repositories import (
    fetch_active_resource_lock,
    fetch_stale_resource_locks,
    fetch_task_status,
    persist_planned_execution,
    record_worker_events,
    release_stale_resource_lock,
)
from atelier.workflow.graph import WorkflowGraph, WorkflowNode
from atelier.workers.simulated import run_simulated_task


class ResourceLockTests(unittest.TestCase):
    def test_scheduler_claim_creates_active_resource_lock(self) -> None:
        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-locks",
                    name="Lock Graph",
                    nodes=[
                        WorkflowNode(
                            node_id="node-lock",
                            node_type="simulate.echo",
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(components=["simulated"]),
                        )
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-locks")
                persist_planned_execution(
                    connection,
                    project_id="project-locks",
                    project_name="Lock Project",
                    project_root=str(paths.data_root),
                    job_id="job-locks",
                    job_name="Lock Job",
                    graph=graph,
                    plan=plan,
                )
                scheduler = SimpleScheduler(
                    HardwareSnapshot(cpu_cores=8, ram_total_mb=32768, ram_free_mb=24576)
                )

                claim = scheduler.claim_next_task(connection, plan.plan_id)

                self.assertIsNotNone(claim)
                lock = fetch_active_resource_lock(connection, claim.task.task_id)
                self.assertEqual(lock.task_id, claim.task.task_id)
                self.assertEqual(lock.device_id, "cpu")
                self.assertEqual(lock.lock_type, "task")
                self.assertIsNone(lock.vram_mb)
                self.assertIsNone(lock.released_at)
                self.assertTrue(lock.acquired_at.endswith("Z"))
            finally:
                connection.close()

    def test_completed_terminal_event_releases_active_resource_lock(self) -> None:
        with TemporaryDirectory() as temp_dir:
            connection, claim = self._claim_single_task(temp_dir)
            try:
                record_worker_events(
                    connection,
                    run_simulated_task(claim.task, artifact_path="artifacts/node-lock/output.json"),
                )

                with self.assertRaisesRegex(LookupError, "missing active resource lock"):
                    fetch_active_resource_lock(connection, claim.task.task_id)
                self.assertEqual(fetch_task_status(connection, claim.task.task_id), "completed")
            finally:
                connection.close()

    def test_cancelled_terminal_event_releases_active_resource_lock(self) -> None:
        with TemporaryDirectory() as temp_dir:
            connection, claim = self._claim_single_task(temp_dir)
            try:
                record_worker_events(
                    connection,
                    [
                        FailedEvent(
                            task_id=claim.task.task_id,
                            timestamp="2026-05-03T00:00:00Z",
                            seq=0,
                            error_code="CANCELLED",
                            message="cancelled by user",
                            recoverable=False,
                        )
                    ],
                )

                with self.assertRaisesRegex(LookupError, "missing active resource lock"):
                    fetch_active_resource_lock(connection, claim.task.task_id)
                self.assertEqual(fetch_task_status(connection, claim.task.task_id), "cancelled")
            finally:
                connection.close()

    def test_failed_terminal_event_releases_active_resource_lock(self) -> None:
        with TemporaryDirectory() as temp_dir:
            connection, claim = self._claim_single_task(temp_dir)
            try:
                record_worker_events(
                    connection,
                    [
                        FailedEvent(
                            task_id=claim.task.task_id,
                            timestamp="2026-05-03T00:00:00Z",
                            seq=0,
                            error_code="SIMULATED_FAILURE",
                            message="simulated failure",
                            recoverable=True,
                        )
                    ],
                )

                with self.assertRaisesRegex(LookupError, "missing active resource lock"):
                    fetch_active_resource_lock(connection, claim.task.task_id)
                self.assertEqual(fetch_task_status(connection, claim.task.task_id), "failed")
            finally:
                connection.close()

    def test_stale_resource_lock_can_be_detected_and_released(self) -> None:
        with TemporaryDirectory() as temp_dir:
            connection, claim = self._claim_single_task(temp_dir)
            try:
                connection.execute(
                    """
                    UPDATE resource_locks
                    SET heartbeat_at = ?, stale_after = ?
                    WHERE task_id = ?
                    """,
                    (
                        "2026-05-03T00:00:00Z",
                        "2026-05-03T00:01:00Z",
                        claim.task.task_id,
                    ),
                )
                connection.commit()

                stale_locks = fetch_stale_resource_locks(
                    connection,
                    now="2026-05-03T00:02:00Z",
                )

                self.assertEqual([lock.task_id for lock in stale_locks], [claim.task.task_id])
                self.assertEqual(stale_locks[0].stale_after, "2026-05-03T00:01:00Z")
                release_stale_resource_lock(
                    connection,
                    stale_locks[0].lock_id,
                    released_at="2026-05-03T00:02:30Z",
                )

                with self.assertRaisesRegex(LookupError, "missing active resource lock"):
                    fetch_active_resource_lock(connection, claim.task.task_id)
                self.assertEqual(
                    fetch_stale_resource_locks(connection, now="2026-05-03T00:03:00Z"),
                    [],
                )
                self.assertEqual(fetch_task_status(connection, claim.task.task_id), "running")
            finally:
                connection.close()

    def test_stale_resource_lock_release_rejects_non_stale_and_already_released_locks(self) -> None:
        with TemporaryDirectory() as temp_dir:
            connection, claim = self._claim_single_task(temp_dir)
            try:
                connection.execute(
                    """
                    UPDATE resource_locks
                    SET heartbeat_at = ?, stale_after = ?
                    WHERE task_id = ?
                    """,
                    (
                        "2026-05-03T00:00:00Z",
                        "2026-05-03T00:10:00Z",
                        claim.task.task_id,
                    ),
                )
                connection.commit()
                lock = fetch_active_resource_lock(connection, claim.task.task_id)

                with self.assertRaisesRegex(RuntimeError, "not stale or already released"):
                    release_stale_resource_lock(
                        connection,
                        lock.lock_id,
                        released_at="2026-05-03T00:02:00Z",
                    )

                self.assertEqual(
                    fetch_active_resource_lock(connection, claim.task.task_id).lock_id,
                    lock.lock_id,
                )

                release_stale_resource_lock(
                    connection,
                    lock.lock_id,
                    released_at="2026-05-03T00:11:00Z",
                )
                with self.assertRaisesRegex(RuntimeError, "not stale or already released"):
                    release_stale_resource_lock(
                        connection,
                        lock.lock_id,
                        released_at="2026-05-03T00:12:00Z",
                    )
            finally:
                connection.close()

    def _claim_single_task(self, temp_dir: str):
        paths = AppPaths.for_development(Path(temp_dir))
        connection = open_app_database(paths)
        graph = WorkflowGraph(
            graph_id="graph-locks",
            name="Lock Graph",
            nodes=[
                WorkflowNode(
                    node_id="node-lock",
                    node_type="simulate.echo",
                    resource_request=ResourceRequest(device_type="cpu"),
                    runtime_request=RuntimeRequest(components=["simulated"]),
                )
            ],
        )
        plan = build_linear_execution_plan(graph, plan_id="plan-locks")
        persist_planned_execution(
            connection,
            project_id="project-locks",
            project_name="Lock Project",
            project_root=str(paths.data_root),
            job_id="job-locks",
            job_name="Lock Job",
            graph=graph,
            plan=plan,
        )
        scheduler = SimpleScheduler(
            HardwareSnapshot(cpu_cores=8, ram_total_mb=32768, ram_free_mb=24576)
        )
        claim = scheduler.claim_next_task(connection, plan.plan_id)
        self.assertIsNotNone(claim)
        return connection, claim


if __name__ == "__main__":
    unittest.main()
