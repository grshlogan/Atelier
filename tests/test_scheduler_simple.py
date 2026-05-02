from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from atelier.app.paths import AppPaths
from atelier.app.services import open_app_database
from atelier.domain.resources import HardwareSnapshot, ResourceRequest, RuntimeRequest
from atelier.planning.simple import build_linear_execution_plan
from atelier.scheduler.simple import SimpleScheduler
from atelier.storage.repositories import (
    fetch_task_resource_binding,
    fetch_task_status,
    persist_planned_execution,
    record_worker_events,
)
from atelier.workflow.graph import WorkflowEdge, WorkflowGraph, WorkflowNode, WorkflowPortRef
from atelier.workers.simulated import run_simulated_task


class SimpleSchedulerTests(unittest.TestCase):
    def test_scheduler_claims_only_dependency_ready_tasks(self) -> None:
        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-scheduled",
                    name="Scheduled Graph",
                    nodes=[
                        WorkflowNode(
                            node_id="node-a",
                            node_type="simulate.source",
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(components=["simulated"]),
                        ),
                        WorkflowNode(
                            node_id="node-b",
                            node_type="simulate.echo",
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(components=["simulated"]),
                        ),
                    ],
                    edges=[
                        WorkflowEdge(
                            edge_id="edge-a-b",
                            source=WorkflowPortRef(node_id="node-a", port_id="out"),
                            target=WorkflowPortRef(node_id="node-b", port_id="in"),
                        )
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-scheduled")
                persist_planned_execution(
                    connection,
                    project_id="project-scheduled",
                    project_name="Scheduled Project",
                    project_root=str(paths.data_root),
                    job_id="job-scheduled",
                    job_name="Scheduled Job",
                    graph=graph,
                    plan=plan,
                )
                scheduler = SimpleScheduler(
                    HardwareSnapshot(cpu_cores=8, ram_total_mb=32768, ram_free_mb=24576)
                )

                first_claim = scheduler.claim_next_task(connection, plan.plan_id)

                self.assertIsNotNone(first_claim)
                self.assertEqual(first_claim.task.source_node_id, "node-a")
                self.assertEqual(first_claim.resource_binding.device_id, "cpu")
                self.assertEqual(fetch_task_status(connection, first_claim.task.task_id), "running")
                self.assertEqual(
                    fetch_task_resource_binding(connection, first_claim.task.task_id).device_id,
                    "cpu",
                )

                self.assertIsNone(scheduler.claim_next_task(connection, plan.plan_id))

                events = run_simulated_task(
                    first_claim.task,
                    artifact_path="artifacts/node-a/output.json",
                )
                record_worker_events(connection, events)

                second_claim = scheduler.claim_next_task(connection, plan.plan_id)

                self.assertIsNotNone(second_claim)
                self.assertEqual(second_claim.task.source_node_id, "node-b")
                self.assertEqual(fetch_task_status(connection, second_claim.task.task_id), "running")
            finally:
                connection.close()


if __name__ == "__main__":
    unittest.main()
