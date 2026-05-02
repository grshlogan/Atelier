from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from atelier.app.paths import AppPaths
from atelier.app.services import open_app_database
from atelier.domain.resources import ResourceRequest, RuntimeRequest
from atelier.planning.simple import build_linear_execution_plan
from atelier.storage.repositories import (
    fetch_artifact_paths,
    fetch_task_event_types,
    fetch_task_status,
    persist_planned_execution,
    record_worker_events,
)
from atelier.workflow.graph import WorkflowGraph, WorkflowNode
from atelier.workers.simulated import run_simulated_task


class Phase6MinimalLoopTests(unittest.TestCase):
    def test_sample_workflow_runs_simulated_worker_and_persists_events_and_artifact(self) -> None:
        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-sample",
                    name="Sample Workflow",
                    nodes=[
                        WorkflowNode(
                            node_id="node-echo",
                            node_type="simulate.echo",
                            params={"message": "hello"},
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(components=["simulated"]),
                        )
                    ],
                )

                plan = build_linear_execution_plan(graph, plan_id="plan-sample")
                task = plan.tasks[0]
                persist_planned_execution(
                    connection,
                    project_id="project-sample",
                    project_name="Sample Project",
                    project_root=str(paths.data_root),
                    job_id="job-sample",
                    job_name="Sample Job",
                    graph=graph,
                    plan=plan,
                )

                events = run_simulated_task(task, artifact_path="artifacts/node-echo/output.json")
                record_worker_events(connection, events)

                self.assertEqual(
                    fetch_task_event_types(connection, task.task_id),
                    ["started", "progress", "artifact", "completed"],
                )
                self.assertEqual(
                    fetch_artifact_paths(connection, task.task_id),
                    ["artifacts/node-echo/output.json"],
                )
                self.assertEqual(fetch_task_status(connection, task.task_id), "completed")
            finally:
                connection.close()


if __name__ == "__main__":
    unittest.main()
