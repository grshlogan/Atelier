from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from atelier.app.paths import AppPaths
from atelier.app.services import open_app_database
from atelier.domain.resources import ResourceRequest, RuntimeRequest
from atelier.planning.simple import build_linear_execution_plan
from atelier.storage.repositories import (
    fetch_task_output_artifacts,
    persist_planned_execution,
    record_worker_events,
)
from atelier.workflow.graph import WorkflowGraph, WorkflowNode
from atelier.workers.simulated import run_simulated_task


class BackendWorkflowHandoffTests(unittest.TestCase):
    def test_fetch_task_output_artifacts_returns_persisted_output_links(self) -> None:
        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-handoff",
                    name="Handoff Graph",
                    nodes=[
                        WorkflowNode(
                            node_id="node-upstream",
                            node_type="simulate.source",
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(components=["simulated"]),
                        )
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-handoff")
                task = plan.tasks[0]
                persist_planned_execution(
                    connection,
                    project_id="project-handoff",
                    project_name="Handoff Project",
                    project_root=str(paths.data_root),
                    job_id="job-handoff",
                    job_name="Handoff Job",
                    graph=graph,
                    plan=plan,
                )
                record_worker_events(
                    connection,
                    run_simulated_task(task, artifact_path="artifacts/node-upstream/output.json"),
                )

                artifacts = fetch_task_output_artifacts(connection, task.task_id)

                self.assertEqual(len(artifacts), 1)
                self.assertEqual(artifacts[0].artifact_id, f"{task.task_id}-artifact-0")
                self.assertEqual(artifacts[0].artifact_type, "metadata")
                self.assertEqual(artifacts[0].path, "artifacts/node-upstream/output.json")
                self.assertEqual(artifacts[0].role, "output")

                metadata_artifacts = fetch_task_output_artifacts(
                    connection,
                    task.task_id,
                    artifact_type="metadata",
                )
                self.assertEqual([artifact.path for artifact in metadata_artifacts], [
                    "artifacts/node-upstream/output.json"
                ])
                self.assertEqual(
                    fetch_task_output_artifacts(
                        connection,
                        task.task_id,
                        artifact_type="audio",
                    ),
                    [],
                )
            finally:
                connection.close()


if __name__ == "__main__":
    unittest.main()
