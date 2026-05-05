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
from atelier.workflow.graph import WorkflowEdge, WorkflowGraph, WorkflowNode, WorkflowPortRef
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

    def test_materialization_blocks_when_upstream_artifact_candidates_are_ambiguous(self) -> None:
        from atelier.scheduler.handoff import materialize_downstream_task_inputs

        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-ambiguous",
                    name="Ambiguous Graph",
                    nodes=[
                        WorkflowNode(
                            node_id="node-upstream-a",
                            node_type="simulate.source",
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(components=["simulated"]),
                        ),
                        WorkflowNode(
                            node_id="node-upstream-b",
                            node_type="simulate.source",
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(components=["simulated"]),
                        ),
                        WorkflowNode(
                            node_id="node-export",
                            node_type="output.export",
                            params={"output_dir": str(paths.data_root / "exports")},
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(),
                        ),
                    ],
                    edges=[
                        WorkflowEdge(
                            edge_id="edge-a-export",
                            source=WorkflowPortRef(node_id="node-upstream-a", port_id="out"),
                            target=WorkflowPortRef(node_id="node-export", port_id="in"),
                        ),
                        WorkflowEdge(
                            edge_id="edge-b-export",
                            source=WorkflowPortRef(node_id="node-upstream-b", port_id="out"),
                            target=WorkflowPortRef(node_id="node-export", port_id="in"),
                        ),
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-ambiguous")
                upstream_a = plan.tasks[0]
                upstream_b = plan.tasks[1]
                export_task = plan.tasks[2]
                persist_planned_execution(
                    connection,
                    project_id="project-ambiguous",
                    project_name="Ambiguous Project",
                    project_root=str(paths.data_root),
                    job_id="job-ambiguous",
                    job_name="Ambiguous Job",
                    graph=graph,
                    plan=plan,
                )
                record_worker_events(
                    connection,
                    run_simulated_task(upstream_a, artifact_path="artifacts/a/output.json"),
                )
                record_worker_events(
                    connection,
                    run_simulated_task(upstream_b, artifact_path="artifacts/b/output.json"),
                )

                result = materialize_downstream_task_inputs(connection, export_task)

                self.assertEqual(result.status, "blocked")
                self.assertEqual(result.error_code, "UPSTREAM_ARTIFACT_AMBIGUOUS")
                self.assertNotIn("input_path", result.task.params)
            finally:
                connection.close()

    def test_materializes_output_export_input_path_from_single_upstream_artifact(self) -> None:
        from atelier.scheduler.handoff import materialize_downstream_task_inputs

        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-materialize",
                    name="Materialize Graph",
                    nodes=[
                        WorkflowNode(
                            node_id="node-upstream",
                            node_type="simulate.source",
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(components=["simulated"]),
                        ),
                        WorkflowNode(
                            node_id="node-export",
                            node_type="output.export",
                            params={"output_dir": str(paths.data_root / "exports")},
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(),
                        ),
                    ],
                    edges=[
                        WorkflowEdge(
                            edge_id="edge-upstream-export",
                            source=WorkflowPortRef(node_id="node-upstream", port_id="out"),
                            target=WorkflowPortRef(node_id="node-export", port_id="in"),
                        )
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-materialize")
                upstream_task = plan.tasks[0]
                export_task = plan.tasks[1]
                persist_planned_execution(
                    connection,
                    project_id="project-materialize",
                    project_name="Materialize Project",
                    project_root=str(paths.data_root),
                    job_id="job-materialize",
                    job_name="Materialize Job",
                    graph=graph,
                    plan=plan,
                )
                record_worker_events(
                    connection,
                    run_simulated_task(upstream_task, artifact_path="artifacts/node-upstream/output.json"),
                )

                result = materialize_downstream_task_inputs(connection, export_task)

                self.assertEqual(result.status, "ready")
                self.assertEqual(
                    result.task.params["input_path"],
                    "artifacts/node-upstream/output.json",
                )
                self.assertNotIn("input_path", export_task.params)
            finally:
                connection.close()


if __name__ == "__main__":
    unittest.main()
