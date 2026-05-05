import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from atelier.app.paths import AppPaths
from atelier.app.services import open_app_database
from atelier.domain.resources import HardwareSnapshot, ResourceRequest, RuntimeRequest
from atelier.planning.simple import build_linear_execution_plan
from atelier.runtime.manager import RuntimeManager
from atelier.scheduler.dispatch import dispatch_claimed_task
from atelier.scheduler.simple import SimpleScheduler
from atelier.storage.repositories import (
    fetch_artifact_paths,
    fetch_failure_facts,
    fetch_task_artifact_links,
    fetch_task_event_types,
    fetch_task_status,
    persist_planned_execution,
)
from atelier.workflow.graph import WorkflowGraph, WorkflowNode


class OutputExportWorkflowTests(unittest.TestCase):
    def test_output_export_dispatch_persists_final_output_artifact_link(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths.for_development(root)
            staged = root / "worker-work" / "upstream-task" / "audio.wav"
            staged.parent.mkdir(parents=True)
            staged.write_bytes(b"fake wav")
            output_dir = root / "exports"
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-output-export",
                    name="Output Export",
                    nodes=[
                        WorkflowNode(
                            node_id="node-output-export",
                            node_type="output.export",
                            params={
                                "input_path": str(staged),
                                "output_dir": str(output_dir),
                                "filename": "final.wav",
                                "artifact_type": "audio",
                            },
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(),
                        )
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-output-export")
                persist_planned_execution(
                    connection,
                    project_id="project-output-export",
                    project_name="Output Export Project",
                    project_root=str(paths.data_root),
                    job_id="job-output-export",
                    job_name="Output Export Job",
                    graph=graph,
                    plan=plan,
                )
                claimed = SimpleScheduler(
                    HardwareSnapshot(cpu_cores=4, ram_total_mb=8192, ram_free_mb=4096)
                ).claim_next_task(connection, plan.plan_id)
                self.assertIsNotNone(claimed)
                assert claimed is not None
                runtime_binding = RuntimeManager().resolve(claimed.task.runtime_request)

                result = dispatch_claimed_task(
                    connection,
                    claimed_task=claimed,
                    work_root=root / "worker-work",
                    command_args=(sys.executable, "-m", "atelier.workers.adapter_entry"),
                    runtime_binding=runtime_binding,
                )

                final_path = output_dir / "final.wav"
                self.assertEqual(result.task_status, "completed")
                self.assertEqual([event.type for event in result.events], ["started", "artifact", "completed"])
                self.assertEqual(fetch_task_status(connection, claimed.task.task_id), "completed")
                self.assertEqual(
                    fetch_task_event_types(connection, claimed.task.task_id),
                    ["started", "artifact", "completed"],
                )
                self.assertEqual(fetch_artifact_paths(connection, claimed.task.task_id), [str(final_path)])
                self.assertEqual(fetch_task_artifact_links(connection, claimed.task.task_id), [
                    (f"{claimed.task.task_id}-final-output", "final_output")
                ])
                self.assertEqual(final_path.read_bytes(), b"fake wav")
            finally:
                connection.close()

    def test_output_export_conflict_persists_structured_failure(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths.for_development(root)
            staged = root / "worker-work" / "upstream-task" / "audio.wav"
            staged.parent.mkdir(parents=True)
            staged.write_bytes(b"new wav")
            output_dir = root / "exports"
            output_dir.mkdir()
            (output_dir / "audio.wav").write_bytes(b"existing")
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-output-export-conflict",
                    name="Output Export Conflict",
                    nodes=[
                        WorkflowNode(
                            node_id="node-output-export-conflict",
                            node_type="output.export",
                            params={
                                "input_path": str(staged),
                                "output_dir": str(output_dir),
                                "artifact_type": "audio",
                            },
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(),
                        )
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-output-export-conflict")
                persist_planned_execution(
                    connection,
                    project_id="project-output-export-conflict",
                    project_name="Output Export Conflict Project",
                    project_root=str(paths.data_root),
                    job_id="job-output-export-conflict",
                    job_name="Output Export Conflict Job",
                    graph=graph,
                    plan=plan,
                )
                claimed = SimpleScheduler(
                    HardwareSnapshot(cpu_cores=4, ram_total_mb=8192, ram_free_mb=4096)
                ).claim_next_task(connection, plan.plan_id)
                self.assertIsNotNone(claimed)
                assert claimed is not None
                runtime_binding = RuntimeManager().resolve(claimed.task.runtime_request)

                result = dispatch_claimed_task(
                    connection,
                    claimed_task=claimed,
                    work_root=root / "worker-work",
                    command_args=(sys.executable, "-m", "atelier.workers.adapter_entry"),
                    runtime_binding=runtime_binding,
                )
                facts = fetch_failure_facts(connection, claimed.task.task_id)

                self.assertEqual(result.task_status, "failed")
                self.assertEqual([event.type for event in result.events], ["started", "failed"])
                self.assertEqual(facts.error_code, "OUTPUT_CONFLICT")
                self.assertIn("already exists", facts.error_message)
                self.assertTrue(facts.recoverable)
                self.assertEqual((output_dir / "audio.wav").read_bytes(), b"existing")
            finally:
                connection.close()


if __name__ == "__main__":
    unittest.main()
