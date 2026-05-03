from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from atelier.app.paths import AppPaths
from atelier.app.services import open_app_database
from atelier.domain.resources import HardwareSnapshot, ResourceRequest, RuntimeRequest
from atelier.gui.state_reader import read_workbench_snapshot
from atelier.planning.simple import build_linear_execution_plan
from atelier.scheduler.simple import SimpleScheduler
from atelier.storage.repositories import persist_planned_execution, record_worker_events
from atelier.workflow.graph import WorkflowGraph, WorkflowNode
from atelier.workers.simulated import run_simulated_task


class GuiStateReaderTests(unittest.TestCase):
    def test_workbench_snapshot_reads_task_events_artifacts_and_resource_binding(self) -> None:
        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-gui-state",
                    name="GUI State Graph",
                    nodes=[
                        WorkflowNode(
                            node_id="node-gui-state",
                            node_type="simulate.echo",
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(components=["simulated"]),
                        )
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-gui-state")
                persist_planned_execution(
                    connection,
                    project_id="project-gui-state",
                    project_name="GUI State Project",
                    project_root=str(paths.data_root),
                    job_id="job-gui-state",
                    job_name="GUI State Job",
                    graph=graph,
                    plan=plan,
                )
                scheduler = SimpleScheduler(
                    HardwareSnapshot(cpu_cores=8, ram_total_mb=32768, ram_free_mb=24576)
                )
                claim = scheduler.claim_next_task(connection, plan.plan_id)
                self.assertIsNotNone(claim)
                record_worker_events(
                    connection,
                    run_simulated_task(
                        claim.task,
                        artifact_path="artifacts/node-gui-state/output.json",
                    ),
                )

                snapshot = read_workbench_snapshot(connection)

                self.assertEqual(len(snapshot.tasks), 1)
                task = snapshot.tasks[0]
                self.assertEqual(task.task_id, claim.task.task_id)
                self.assertEqual(task.node_type, "simulate.echo")
                self.assertEqual(task.status, "completed")
                self.assertEqual(task.resource_device_id, "cpu")
                self.assertEqual(task.event_count, 4)
                self.assertEqual(task.artifact_paths, ["artifacts/node-gui-state/output.json"])
            finally:
                connection.close()


if __name__ == "__main__":
    unittest.main()
