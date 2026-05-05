import json
import sys
import threading
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from atelier.app.paths import AppPaths
from atelier.app.services import open_app_database
from atelier.domain.resources import HardwareSnapshot, ResourceRequest, RuntimeRequest
from atelier.planning.simple import build_linear_execution_plan
from atelier.scheduler.dispatch import dispatch_claimed_task
from atelier.scheduler.simple import SimpleScheduler
from atelier.storage.repositories import (
    fetch_active_resource_lock,
    fetch_artifact_paths,
    fetch_failure_facts,
    fetch_task_artifact_links,
    fetch_task_event_types,
    fetch_task_status,
    persist_planned_execution,
)
from atelier.workflow.graph import WorkflowGraph, WorkflowNode
from atelier.workers.runner import WorkerLifecycleConfig


class SchedulerWorkerRunnerIntegrationTests(unittest.TestCase):
    def test_dispatch_claimed_task_returns_runner_result_and_persisted_status(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths.for_development(root)
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-dispatch-shape",
                    name="Dispatch Shape",
                    nodes=[
                        WorkflowNode(
                            node_id="node-dispatch",
                            node_type="simulate.dispatch",
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(components=["simulated"]),
                        )
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-dispatch-shape")
                persist_planned_execution(
                    connection,
                    project_id="project-dispatch-shape",
                    project_name="Dispatch Shape Project",
                    project_root=str(paths.data_root),
                    job_id="job-dispatch-shape",
                    job_name="Dispatch Shape Job",
                    graph=graph,
                    plan=plan,
                )
                scheduler = SimpleScheduler(
                    HardwareSnapshot(cpu_cores=4, ram_total_mb=8192, ram_free_mb=4096)
                )
                claimed = scheduler.claim_next_task(connection, plan.plan_id)
                self.assertIsNotNone(claimed)
                assert claimed is not None
                self.assertEqual(fetch_task_status(connection, claimed.task.task_id), "running")

                script = root / "dispatch_stub_worker.py"
                script.write_text(
                    textwrap.dedent(
                        """
                        import argparse
                        import json
                        import os
                        import sys
                        from pathlib import Path

                        parser = argparse.ArgumentParser()
                        parser.add_argument("--task-file", required=True)
                        args = parser.parse_args()
                        payload = json.loads(Path(args.task_file).read_text(encoding="utf-8"))
                        task_id = payload["task_id"]
                        sys.stderr.write("dispatch helper stderr\\n")
                        print(json.dumps({
                            "type": "started",
                            "task_id": task_id,
                            "timestamp": "2026-05-04T00:00:00Z",
                            "seq": 0,
                            "worker_pid": 4321,
                            "worker_version": "stub",
                            "node_type": payload["node_type"],
                        }))
                        print(json.dumps({
                            "type": "log",
                            "task_id": task_id,
                            "timestamp": "2026-05-04T00:00:01Z",
                            "seq": 1,
                            "level": "info",
                            "message": f"{payload['status']}|{payload['resource_binding']['device_id']}|{os.environ.get('ATELIER_DISPATCH_TEST')}",
                        }))
                        print(json.dumps({
                            "type": "completed",
                            "task_id": task_id,
                            "timestamp": "2026-05-04T00:00:02Z",
                            "seq": 2,
                            "artifacts": [],
                            "duration_seconds": 2.0,
                        }))
                        """
                    ),
                    encoding="utf-8",
                )

                result = dispatch_claimed_task(
                    connection,
                    claimed_task=claimed,
                    work_root=root / "worker-work",
                    command_args=(sys.executable, str(script)),
                    env={"ATELIER_DISPATCH_TEST": "env-seen"},
                )

                task_file_payload = json.loads(
                    (root / "worker-work" / claimed.task.task_id / "task.json").read_text(
                        encoding="utf-8"
                    )
                )

                self.assertEqual(result.task_id, claimed.task.task_id)
                self.assertEqual(result.returncode, 0)
                self.assertEqual([event.type for event in result.events], ["started", "log", "completed"])
                self.assertEqual(result.events[1].message, "running|cpu|env-seen")
                self.assertIn("dispatch helper stderr", result.stderr)
                self.assertEqual(result.task_status, "completed")
                self.assertEqual(fetch_task_status(connection, claimed.task.task_id), "completed")
                self.assertEqual(
                    fetch_task_event_types(connection, claimed.task.task_id),
                    ["started", "log", "completed"],
                )
                self.assertEqual(task_file_payload["resource_binding"]["device_id"], "cpu")
                self.assertEqual(task_file_payload["status"], "running")
            finally:
                connection.close()

    def test_dispatch_claimed_task_can_use_lifecycle_runner_and_stderr_log_path(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths.for_development(root)
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-dispatch-lifecycle-completed",
                    name="Dispatch Lifecycle Completed",
                    nodes=[
                        WorkflowNode(
                            node_id="node-lifecycle-completed",
                            node_type="simulate.lifecycle_completed",
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(components=["simulated"]),
                        )
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-dispatch-lifecycle-completed")
                persist_planned_execution(
                    connection,
                    project_id="project-dispatch-lifecycle-completed",
                    project_name="Dispatch Lifecycle Completed Project",
                    project_root=str(paths.data_root),
                    job_id="job-dispatch-lifecycle-completed",
                    job_name="Dispatch Lifecycle Completed Job",
                    graph=graph,
                    plan=plan,
                )
                scheduler = SimpleScheduler(
                    HardwareSnapshot(cpu_cores=4, ram_total_mb=8192, ram_free_mb=4096)
                )
                claimed = scheduler.claim_next_task(connection, plan.plan_id)
                self.assertIsNotNone(claimed)
                assert claimed is not None

                script = root / "lifecycle_completed_worker.py"
                script.write_text(
                    textwrap.dedent(
                        """
                        import argparse
                        import json
                        import sys
                        from pathlib import Path

                        parser = argparse.ArgumentParser()
                        parser.add_argument("--task-file", required=True)
                        args = parser.parse_args()
                        payload = json.loads(Path(args.task_file).read_text(encoding="utf-8"))
                        task_id = payload["task_id"]
                        sys.stderr.write("lifecycle dispatch stderr\\n")
                        print(json.dumps({
                            "type": "started",
                            "task_id": task_id,
                            "timestamp": "2026-05-04T00:00:00Z",
                            "seq": 0,
                            "worker_pid": 4321,
                            "worker_version": "stub",
                            "node_type": payload["node_type"],
                        }), flush=True)
                        print(json.dumps({
                            "type": "completed",
                            "task_id": task_id,
                            "timestamp": "2026-05-04T00:00:01Z",
                            "seq": 1,
                            "artifacts": [],
                            "duration_seconds": 1.0,
                        }), flush=True)
                        """
                    ),
                    encoding="utf-8",
                )
                stderr_log_path = root / "logs" / "dispatch.stderr.log"

                result = dispatch_claimed_task(
                    connection,
                    claimed_task=claimed,
                    work_root=root / "worker-work",
                    command_args=(sys.executable, "-u", str(script)),
                    lifecycle_config=WorkerLifecycleConfig(
                        startup_timeout_seconds=1.0,
                        heartbeat_timeout_seconds=1.0,
                    ),
                    stderr_log_path=stderr_log_path,
                )

                stderr_log = stderr_log_path.read_text(encoding="utf-8")

                self.assertEqual(result.task_status, "completed")
                self.assertEqual([event.type for event in result.events], ["started", "completed"])
                self.assertEqual(result.stderr_log_path, stderr_log_path)
                self.assertFalse(result.timed_out)
                self.assertFalse(result.cancelled)
                self.assertFalse(result.killed)
                self.assertIn("lifecycle dispatch stderr", result.stderr)
                self.assertIn("lifecycle dispatch stderr", stderr_log)
                with self.assertRaisesRegex(LookupError, "missing active resource lock"):
                    fetch_active_resource_lock(connection, claimed.task.task_id)
            finally:
                connection.close()

    def test_lifecycle_dispatch_timeout_records_failure_and_releases_resource_lock(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths.for_development(root)
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-dispatch-lifecycle-timeout",
                    name="Dispatch Lifecycle Timeout",
                    nodes=[
                        WorkflowNode(
                            node_id="node-lifecycle-timeout",
                            node_type="simulate.lifecycle_timeout",
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(components=["simulated"]),
                        )
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-dispatch-lifecycle-timeout")
                persist_planned_execution(
                    connection,
                    project_id="project-dispatch-lifecycle-timeout",
                    project_name="Dispatch Lifecycle Timeout Project",
                    project_root=str(paths.data_root),
                    job_id="job-dispatch-lifecycle-timeout",
                    job_name="Dispatch Lifecycle Timeout Job",
                    graph=graph,
                    plan=plan,
                )
                scheduler = SimpleScheduler(
                    HardwareSnapshot(cpu_cores=4, ram_total_mb=8192, ram_free_mb=4096)
                )
                claimed = scheduler.claim_next_task(connection, plan.plan_id)
                self.assertIsNotNone(claimed)
                assert claimed is not None
                self.assertEqual(fetch_task_status(connection, claimed.task.task_id), "running")

                script = root / "silent_timeout_worker.py"
                script.write_text(
                    textwrap.dedent(
                        """
                        import argparse
                        import time

                        parser = argparse.ArgumentParser()
                        parser.add_argument("--task-file", required=True)
                        parser.parse_args()
                        time.sleep(0.3)
                        """
                    ),
                    encoding="utf-8",
                )
                stderr_log_path = root / "logs" / "timeout.stderr.log"

                result = dispatch_claimed_task(
                    connection,
                    claimed_task=claimed,
                    work_root=root / "worker-work",
                    command_args=(sys.executable, "-u", str(script)),
                    lifecycle_config=WorkerLifecycleConfig(
                        startup_timeout_seconds=0.05,
                        heartbeat_timeout_seconds=0.05,
                        terminate_grace_seconds=0.05,
                    ),
                    stderr_log_path=stderr_log_path,
                )
                facts = fetch_failure_facts(connection, claimed.task.task_id)

                self.assertTrue(result.timed_out)
                self.assertFalse(result.cancelled)
                self.assertEqual(result.task_status, "failed")
                self.assertEqual([event.type for event in result.events], ["failed"])
                self.assertEqual(result.events[0].error_code, "TIMEOUT")
                self.assertEqual(fetch_task_status(connection, claimed.task.task_id), "failed")
                self.assertEqual(fetch_task_event_types(connection, claimed.task.task_id), ["failed"])
                self.assertEqual(facts.error_code, "TIMEOUT")
                self.assertIn("timed out", facts.error_message)
                self.assertTrue(facts.recoverable)
                self.assertEqual(result.stderr_log_path, stderr_log_path)
                self.assertTrue(stderr_log_path.exists())
                with self.assertRaisesRegex(LookupError, "missing active resource lock"):
                    fetch_active_resource_lock(connection, claimed.task.task_id)
            finally:
                connection.close()

    def test_lifecycle_dispatch_cancel_aware_worker_records_cancelled_status(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths.for_development(root)
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-dispatch-lifecycle-cancel-aware",
                    name="Dispatch Lifecycle Cancel Aware",
                    nodes=[
                        WorkflowNode(
                            node_id="node-lifecycle-cancel-aware",
                            node_type="simulate.lifecycle_cancel_aware",
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(components=["simulated"]),
                        )
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-dispatch-lifecycle-cancel-aware")
                persist_planned_execution(
                    connection,
                    project_id="project-dispatch-lifecycle-cancel-aware",
                    project_name="Dispatch Lifecycle Cancel Aware Project",
                    project_root=str(paths.data_root),
                    job_id="job-dispatch-lifecycle-cancel-aware",
                    job_name="Dispatch Lifecycle Cancel Aware Job",
                    graph=graph,
                    plan=plan,
                )
                scheduler = SimpleScheduler(
                    HardwareSnapshot(cpu_cores=4, ram_total_mb=8192, ram_free_mb=4096)
                )
                claimed = scheduler.claim_next_task(connection, plan.plan_id)
                self.assertIsNotNone(claimed)
                assert claimed is not None

                script = root / "cancel_aware_dispatch_worker.py"
                script.write_text(
                    textwrap.dedent(
                        """
                        import argparse
                        import json
                        import sys
                        from pathlib import Path

                        parser = argparse.ArgumentParser()
                        parser.add_argument("--task-file", required=True)
                        args = parser.parse_args()
                        payload = json.loads(Path(args.task_file).read_text(encoding="utf-8"))
                        task_id = payload["task_id"]
                        print(json.dumps({
                            "type": "started",
                            "task_id": task_id,
                            "timestamp": "2026-05-04T00:00:00Z",
                            "seq": 0,
                            "worker_pid": 4321,
                            "worker_version": "stub",
                            "node_type": payload["node_type"],
                        }), flush=True)
                        for line in sys.stdin:
                            command = json.loads(line)
                            if command.get("type") == "cancel":
                                print(json.dumps({
                                    "type": "failed",
                                    "task_id": task_id,
                                    "timestamp": "2026-05-04T00:00:01Z",
                                    "seq": 1,
                                    "error_code": "CANCELLED",
                                    "message": "cancelled by dispatch test",
                                    "recoverable": False,
                                    "partial_artifacts": [],
                                }), flush=True)
                                raise SystemExit(0)
                        """
                    ),
                    encoding="utf-8",
                )
                cancel_event = threading.Event()
                cancel_event.set()

                result = dispatch_claimed_task(
                    connection,
                    claimed_task=claimed,
                    work_root=root / "worker-work",
                    command_args=(sys.executable, "-u", str(script)),
                    lifecycle_config=WorkerLifecycleConfig(
                        startup_timeout_seconds=0.5,
                        heartbeat_timeout_seconds=1.0,
                        terminate_grace_seconds=0.05,
                        cancel_grace_seconds=0.5,
                    ),
                    cancel_event=cancel_event,
                )
                facts = fetch_failure_facts(connection, claimed.task.task_id)

                self.assertTrue(result.cancelled)
                self.assertFalse(result.timed_out)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(result.task_status, "cancelled")
                self.assertEqual([event.type for event in result.events], ["started", "failed"])
                self.assertEqual(result.events[-1].error_code, "CANCELLED")
                self.assertEqual(fetch_task_status(connection, claimed.task.task_id), "cancelled")
                self.assertEqual(facts.error_code, "CANCELLED")
                self.assertEqual(facts.error_message, "cancelled by dispatch test")
                self.assertFalse(facts.recoverable)
                with self.assertRaisesRegex(LookupError, "missing active resource lock"):
                    fetch_active_resource_lock(connection, claimed.task.task_id)
            finally:
                connection.close()

    def test_lifecycle_dispatch_stuck_cancel_worker_records_cancelled_failure(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths.for_development(root)
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-dispatch-lifecycle-stuck-cancel",
                    name="Dispatch Lifecycle Stuck Cancel",
                    nodes=[
                        WorkflowNode(
                            node_id="node-lifecycle-stuck-cancel",
                            node_type="simulate.lifecycle_stuck_cancel",
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(components=["simulated"]),
                        )
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-dispatch-lifecycle-stuck-cancel")
                persist_planned_execution(
                    connection,
                    project_id="project-dispatch-lifecycle-stuck-cancel",
                    project_name="Dispatch Lifecycle Stuck Cancel Project",
                    project_root=str(paths.data_root),
                    job_id="job-dispatch-lifecycle-stuck-cancel",
                    job_name="Dispatch Lifecycle Stuck Cancel Job",
                    graph=graph,
                    plan=plan,
                )
                scheduler = SimpleScheduler(
                    HardwareSnapshot(cpu_cores=4, ram_total_mb=8192, ram_free_mb=4096)
                )
                claimed = scheduler.claim_next_task(connection, plan.plan_id)
                self.assertIsNotNone(claimed)
                assert claimed is not None

                script = root / "stuck_cancel_dispatch_worker.py"
                script.write_text(
                    textwrap.dedent(
                        """
                        import argparse
                        import json
                        import time
                        from pathlib import Path

                        parser = argparse.ArgumentParser()
                        parser.add_argument("--task-file", required=True)
                        args = parser.parse_args()
                        payload = json.loads(Path(args.task_file).read_text(encoding="utf-8"))
                        task_id = payload["task_id"]
                        print(json.dumps({
                            "type": "started",
                            "task_id": task_id,
                            "timestamp": "2026-05-04T00:00:00Z",
                            "seq": 0,
                            "worker_pid": 4321,
                            "worker_version": "stub",
                            "node_type": payload["node_type"],
                        }), flush=True)
                        time.sleep(1.0)
                        """
                    ),
                    encoding="utf-8",
                )
                cancel_event = threading.Event()
                cancel_event.set()

                result = dispatch_claimed_task(
                    connection,
                    claimed_task=claimed,
                    work_root=root / "worker-work",
                    command_args=(sys.executable, "-u", str(script)),
                    lifecycle_config=WorkerLifecycleConfig(
                        startup_timeout_seconds=0.5,
                        heartbeat_timeout_seconds=5.0,
                        terminate_grace_seconds=0.05,
                        cancel_grace_seconds=0.2,
                    ),
                    cancel_event=cancel_event,
                )
                facts = fetch_failure_facts(connection, claimed.task.task_id)

                self.assertTrue(result.cancelled)
                self.assertFalse(result.timed_out)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.task_status, "cancelled")
                self.assertEqual([event.type for event in result.events], ["started", "failed"])
                self.assertEqual(result.events[-1].error_code, "CANCELLED")
                self.assertEqual(fetch_task_status(connection, claimed.task.task_id), "cancelled")
                self.assertEqual(facts.error_code, "CANCELLED")
                self.assertIn("cancel grace period", facts.error_message)
                self.assertFalse(facts.recoverable)
                with self.assertRaisesRegex(LookupError, "missing active resource lock"):
                    fetch_active_resource_lock(connection, claimed.task.task_id)
            finally:
                connection.close()

    def test_failed_stub_worker_records_failure_and_releases_resource_lock(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths.for_development(root)
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-dispatch-failed",
                    name="Dispatch Failed",
                    nodes=[
                        WorkflowNode(
                            node_id="node-failed",
                            node_type="simulate.failed",
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(components=["simulated"]),
                        )
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-dispatch-failed")
                persist_planned_execution(
                    connection,
                    project_id="project-dispatch-failed",
                    project_name="Dispatch Failed Project",
                    project_root=str(paths.data_root),
                    job_id="job-dispatch-failed",
                    job_name="Dispatch Failed Job",
                    graph=graph,
                    plan=plan,
                )
                scheduler = SimpleScheduler(
                    HardwareSnapshot(cpu_cores=4, ram_total_mb=8192, ram_free_mb=4096)
                )
                claimed = scheduler.claim_next_task(connection, plan.plan_id)
                self.assertIsNotNone(claimed)
                assert claimed is not None

                script = root / "failed_stub_worker.py"
                script.write_text(
                    textwrap.dedent(
                        """
                        import argparse
                        import json
                        import sys
                        from pathlib import Path

                        parser = argparse.ArgumentParser()
                        parser.add_argument("--task-file", required=True)
                        args = parser.parse_args()
                        payload = json.loads(Path(args.task_file).read_text(encoding="utf-8"))
                        task_id = payload["task_id"]
                        sys.stderr.write("failed worker detail\\n")
                        print(json.dumps({
                            "type": "started",
                            "task_id": task_id,
                            "timestamp": "2026-05-04T00:00:00Z",
                            "seq": 0,
                            "worker_pid": 4321,
                            "worker_version": "stub",
                            "node_type": payload["node_type"],
                        }))
                        print(json.dumps({
                            "type": "failed",
                            "task_id": task_id,
                            "timestamp": "2026-05-04T00:00:01Z",
                            "seq": 1,
                            "error_code": "SIMULATED_FAILURE",
                            "message": "stub failed",
                            "recoverable": True,
                            "partial_artifacts": [],
                        }))
                        raise SystemExit(7)
                        """
                    ),
                    encoding="utf-8",
                )

                result = dispatch_claimed_task(
                    connection,
                    claimed_task=claimed,
                    work_root=root / "worker-work",
                    command_args=(sys.executable, str(script)),
                )
                facts = fetch_failure_facts(connection, claimed.task.task_id)

                self.assertEqual(result.returncode, 7)
                self.assertEqual(result.task_status, "failed")
                self.assertEqual([event.type for event in result.events], ["started", "failed"])
                self.assertIn("failed worker detail", result.stderr)
                self.assertEqual(fetch_task_status(connection, claimed.task.task_id), "failed")
                self.assertEqual(facts.error_code, "SIMULATED_FAILURE")
                self.assertEqual(facts.error_message, "stub failed")
                self.assertTrue(facts.recoverable)
                with self.assertRaisesRegex(LookupError, "missing active resource lock"):
                    fetch_active_resource_lock(connection, claimed.task.task_id)
            finally:
                connection.close()

    def test_protocol_error_records_internal_failure_and_releases_resource_lock(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths.for_development(root)
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-dispatch-protocol-error",
                    name="Dispatch Protocol Error",
                    nodes=[
                        WorkflowNode(
                            node_id="node-protocol-error",
                            node_type="simulate.protocol_error",
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(components=["simulated"]),
                        )
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-dispatch-protocol-error")
                persist_planned_execution(
                    connection,
                    project_id="project-dispatch-protocol-error",
                    project_name="Dispatch Protocol Error Project",
                    project_root=str(paths.data_root),
                    job_id="job-dispatch-protocol-error",
                    job_name="Dispatch Protocol Error Job",
                    graph=graph,
                    plan=plan,
                )
                scheduler = SimpleScheduler(
                    HardwareSnapshot(cpu_cores=4, ram_total_mb=8192, ram_free_mb=4096)
                )
                claimed = scheduler.claim_next_task(connection, plan.plan_id)
                self.assertIsNotNone(claimed)
                assert claimed is not None

                script = root / "bad_stdout_worker.py"
                script.write_text(
                    textwrap.dedent(
                        """
                        import sys

                        sys.stderr.write("protocol stderr detail\\n")
                        print("not json")
                        raise SystemExit(9)
                        """
                    ),
                    encoding="utf-8",
                )

                result = dispatch_claimed_task(
                    connection,
                    claimed_task=claimed,
                    work_root=root / "worker-work",
                    command_args=(sys.executable, str(script)),
                )
                facts = fetch_failure_facts(connection, claimed.task.task_id)

                self.assertEqual(result.returncode, 9)
                self.assertEqual(result.task_status, "failed")
                self.assertEqual([event.type for event in result.events], ["failed"])
                self.assertEqual(result.events[0].error_code, "INTERNAL")
                self.assertIn("Worker protocol error", result.events[0].message)
                self.assertIn("protocol stderr detail", result.stderr)
                self.assertEqual(fetch_task_status(connection, claimed.task.task_id), "failed")
                self.assertEqual(facts.error_code, "INTERNAL")
                self.assertIn("Worker protocol error", facts.error_message)
                self.assertFalse(facts.recoverable)
                with self.assertRaisesRegex(LookupError, "missing active resource lock"):
                    fetch_active_resource_lock(connection, claimed.task.task_id)
            finally:
                connection.close()

    def test_lifecycle_dispatch_protocol_error_records_internal_failure_and_stderr_log(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths.for_development(root)
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-dispatch-lifecycle-protocol-error",
                    name="Dispatch Lifecycle Protocol Error",
                    nodes=[
                        WorkflowNode(
                            node_id="node-lifecycle-protocol-error",
                            node_type="simulate.lifecycle_protocol_error",
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(components=["simulated"]),
                        )
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-dispatch-lifecycle-protocol-error")
                persist_planned_execution(
                    connection,
                    project_id="project-dispatch-lifecycle-protocol-error",
                    project_name="Dispatch Lifecycle Protocol Error Project",
                    project_root=str(paths.data_root),
                    job_id="job-dispatch-lifecycle-protocol-error",
                    job_name="Dispatch Lifecycle Protocol Error Job",
                    graph=graph,
                    plan=plan,
                )
                scheduler = SimpleScheduler(
                    HardwareSnapshot(cpu_cores=4, ram_total_mb=8192, ram_free_mb=4096)
                )
                claimed = scheduler.claim_next_task(connection, plan.plan_id)
                self.assertIsNotNone(claimed)
                assert claimed is not None

                script = root / "bad_lifecycle_stdout_worker.py"
                script.write_text(
                    textwrap.dedent(
                        """
                        import sys
                        import time

                        sys.stderr.write("lifecycle protocol stderr detail\\n")
                        print("not json", flush=True)
                        time.sleep(1.0)
                        """
                    ),
                    encoding="utf-8",
                )
                stderr_log_path = root / "logs" / "protocol.stderr.log"

                result = dispatch_claimed_task(
                    connection,
                    claimed_task=claimed,
                    work_root=root / "worker-work",
                    command_args=(sys.executable, "-u", str(script)),
                    lifecycle_config=WorkerLifecycleConfig(
                        startup_timeout_seconds=0.5,
                        heartbeat_timeout_seconds=0.5,
                        terminate_grace_seconds=0.05,
                    ),
                    stderr_log_path=stderr_log_path,
                )
                facts = fetch_failure_facts(connection, claimed.task.task_id)
                stderr_log = stderr_log_path.read_text(encoding="utf-8")

                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.task_status, "failed")
                self.assertEqual([event.type for event in result.events], ["failed"])
                self.assertEqual(result.events[0].error_code, "INTERNAL")
                self.assertIn("Worker protocol error", result.events[0].message)
                self.assertEqual(result.stderr_log_path, stderr_log_path)
                self.assertIn("lifecycle protocol stderr detail", result.stderr)
                self.assertIn("lifecycle protocol stderr detail", stderr_log)
                self.assertEqual(fetch_task_status(connection, claimed.task.task_id), "failed")
                self.assertEqual(facts.error_code, "INTERNAL")
                self.assertIn("Worker protocol error", facts.error_message)
                self.assertFalse(facts.recoverable)
                with self.assertRaisesRegex(LookupError, "missing active resource lock"):
                    fetch_active_resource_lock(connection, claimed.task.task_id)
            finally:
                connection.close()

    def test_completed_stub_worker_records_artifact_and_releases_resource_lock(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths.for_development(root)
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-dispatch-completed",
                    name="Dispatch Completed",
                    nodes=[
                        WorkflowNode(
                            node_id="node-completed",
                            node_type="simulate.completed",
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(components=["simulated"]),
                        )
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-dispatch-completed")
                persist_planned_execution(
                    connection,
                    project_id="project-dispatch-completed",
                    project_name="Dispatch Completed Project",
                    project_root=str(paths.data_root),
                    job_id="job-dispatch-completed",
                    job_name="Dispatch Completed Job",
                    graph=graph,
                    plan=plan,
                )
                scheduler = SimpleScheduler(
                    HardwareSnapshot(cpu_cores=4, ram_total_mb=8192, ram_free_mb=4096)
                )
                claimed = scheduler.claim_next_task(connection, plan.plan_id)
                self.assertIsNotNone(claimed)
                assert claimed is not None
                self.assertEqual(
                    fetch_active_resource_lock(connection, claimed.task.task_id).task_id,
                    claimed.task.task_id,
                )

                script = root / "completed_stub_worker.py"
                script.write_text(
                    textwrap.dedent(
                        """
                        import argparse
                        import json
                        from pathlib import Path

                        parser = argparse.ArgumentParser()
                        parser.add_argument("--task-file", required=True)
                        args = parser.parse_args()
                        payload = json.loads(Path(args.task_file).read_text(encoding="utf-8"))
                        task_id = payload["task_id"]
                        artifact_path = "artifacts/node-completed/output.json"
                        print(json.dumps({
                            "type": "started",
                            "task_id": task_id,
                            "timestamp": "2026-05-04T00:00:00Z",
                            "seq": 0,
                            "worker_pid": 4321,
                            "worker_version": "stub",
                            "node_type": payload["node_type"],
                        }))
                        print(json.dumps({
                            "type": "artifact",
                            "task_id": task_id,
                            "timestamp": "2026-05-04T00:00:01Z",
                            "seq": 1,
                            "artifact_id": f"{task_id}-artifact",
                            "artifact_type": "json",
                            "path": artifact_path,
                        }))
                        print(json.dumps({
                            "type": "completed",
                            "task_id": task_id,
                            "timestamp": "2026-05-04T00:00:02Z",
                            "seq": 2,
                            "artifacts": [{
                                "artifact_id": f"{task_id}-artifact",
                                "artifact_type": "json",
                                "path": artifact_path,
                            }],
                            "duration_seconds": 2.0,
                        }))
                        """
                    ),
                    encoding="utf-8",
                )

                result = dispatch_claimed_task(
                    connection,
                    claimed_task=claimed,
                    work_root=root / "worker-work",
                    command_args=(sys.executable, str(script)),
                )

                self.assertEqual(result.task_status, "completed")
                self.assertEqual([event.type for event in result.events], ["started", "artifact", "completed"])
                self.assertEqual(
                    fetch_task_event_types(connection, claimed.task.task_id),
                    ["started", "artifact", "completed"],
                )
                self.assertEqual(
                    fetch_artifact_paths(connection, claimed.task.task_id),
                    ["artifacts/node-completed/output.json"],
                )
                self.assertEqual(
                    fetch_task_artifact_links(connection, claimed.task.task_id),
                    [(f"{claimed.task.task_id}-artifact", "output")],
                )
                self.assertEqual(fetch_task_status(connection, claimed.task.task_id), "completed")
                with self.assertRaisesRegex(LookupError, "missing active resource lock"):
                    fetch_active_resource_lock(connection, claimed.task.task_id)
            finally:
                connection.close()


if __name__ == "__main__":
    unittest.main()
