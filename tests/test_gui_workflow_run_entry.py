import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from atelier.app.paths import AppPaths
from atelier.app.services import create_runtime_store, open_app_database
from atelier.app.workflow_run import WorkflowRunAppService
from atelier.domain.resources import HardwareSnapshot, ResourceRequest, RuntimeRequest
from atelier.gui.state_reader import read_workbench_snapshot
from atelier.planning.simple import build_linear_execution_plan
from atelier.runtime.manifest import RuntimeManifest
from atelier.storage.repositories import persist_planned_execution
from atelier.workflow.graph import WorkflowEdge, WorkflowGraph, WorkflowNode, WorkflowPortRef


class GuiWorkflowRunEntryTests(unittest.TestCase):
    def test_app_service_runs_persisted_audio_export_plan_through_backend_runner(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths.for_development(root)
            input_path = root / "input.mp4"
            input_path.write_bytes(b"fake media")
            fake_ffmpeg = _write_fake_ffmpeg_success(root)
            output_dir = root / "exports"
            connection = open_app_database(paths)
            try:
                runtime_store = create_runtime_store(paths)
                runtime_store.write_runtime_manifests([_runtime_manifest(fake_ffmpeg)])
                graph = _audio_export_graph(
                    graph_id="graph-gui-run-entry",
                    name="GUI Run Entry",
                    input_path=input_path,
                    output_dir=output_dir,
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-gui-run-entry")
                persist_planned_execution(
                    connection,
                    project_id="project-gui-run-entry",
                    project_name="GUI Run Entry Project",
                    project_root=str(paths.data_root),
                    job_id="job-gui-run-entry",
                    job_name="GUI Run Entry Job",
                    graph=graph,
                    plan=plan,
                )
                service = WorkflowRunAppService(
                    connection=connection,
                    runtime_store=runtime_store,
                    hardware_snapshot=HardwareSnapshot(
                        cpu_cores=4,
                        ram_total_mb=8192,
                        ram_free_mb=4096,
                    ),
                    work_root=root / "worker-work",
                    command_args=(sys.executable, "-m", "atelier.workers.adapter_entry"),
                )

                result = service.run_plan(plan.plan_id)

                self.assertEqual(result.status, "completed")
                self.assertEqual(
                    result.dispatched_task_ids,
                    [task.task_id for task in plan.tasks],
                )
                self.assertFalse(hasattr(result, "stdout"))
                snapshot = read_workbench_snapshot(connection)
                tasks_by_type = {task.node_type: task for task in snapshot.tasks}
                self.assertEqual(
                    tasks_by_type["output.export"].final_output_paths,
                    [str(output_dir / "final.wav")],
                )
                self.assertEqual((output_dir / "final.wav").read_text(encoding="ascii"), "fake wav\n")
            finally:
                connection.close()


def _audio_export_graph(
    *,
    graph_id: str,
    name: str,
    input_path: Path,
    output_dir: Path,
) -> WorkflowGraph:
    return WorkflowGraph(
        graph_id=graph_id,
        name=name,
        nodes=[
            WorkflowNode(
                node_id="node-audio",
                node_type="media.audio_extract",
                params={"input_path": str(input_path)},
                resource_request=ResourceRequest(device_type="cpu"),
                runtime_request=RuntimeRequest(
                    components=["ffmpeg"],
                    capabilities=["audio-extract"],
                ),
            ),
            WorkflowNode(
                node_id="node-export",
                node_type="output.export",
                params={
                    "output_dir": str(output_dir),
                    "filename": "final.wav",
                    "artifact_type": "audio",
                },
                resource_request=ResourceRequest(device_type="cpu"),
                runtime_request=RuntimeRequest(),
            ),
        ],
        edges=[
            WorkflowEdge(
                edge_id="edge-audio-export",
                source=WorkflowPortRef(node_id="node-audio", port_id="audio"),
                target=WorkflowPortRef(node_id="node-export", port_id="input"),
            )
        ],
    )


def _runtime_manifest(fake_ffmpeg: Path) -> RuntimeManifest:
    return RuntimeManifest(
        runtime_id=f"ffmpeg-fake-{fake_ffmpeg.stem}",
        component="ffmpeg",
        version="fake",
        component_paths={"ffmpeg": str(fake_ffmpeg)},
        executable_paths={"ffmpeg": str(fake_ffmpeg)},
        capabilities=["audio-extract"],
        profile_kind="local",
    )


def _write_fake_ffmpeg_success(root: Path) -> Path:
    fake_ffmpeg = root / "fake_ffmpeg.cmd"
    fake_ffmpeg.write_text("@echo fake wav>audio.wav\n", encoding="ascii")
    return fake_ffmpeg


if __name__ == "__main__":
    unittest.main()
