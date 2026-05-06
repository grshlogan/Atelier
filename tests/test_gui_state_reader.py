import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from atelier.app.paths import AppPaths
from atelier.app.services import open_app_database
from atelier.domain.resources import HardwareSnapshot, ResourceRequest, RuntimeRequest
from atelier.gui.state_reader import read_workbench_snapshot
from atelier.planning.simple import build_linear_execution_plan
from atelier.runtime.manager import RuntimeManager
from atelier.runtime.manifest import RuntimeManifest
from atelier.scheduler.simple import SimpleScheduler
from atelier.scheduler.workflow_runner import run_sequential_workflow
from atelier.storage.repositories import persist_planned_execution, record_worker_events
from atelier.workflow.graph import WorkflowEdge, WorkflowGraph, WorkflowNode, WorkflowPortRef
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

    def test_workbench_snapshot_reads_final_output_paths_from_backend_runner(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths.for_development(root)
            input_path = root / "input.mp4"
            input_path.write_bytes(b"fake media")
            fake_ffmpeg = _write_fake_ffmpeg_success(root)
            output_dir = root / "exports"
            connection = open_app_database(paths)
            try:
                graph = _audio_export_graph(
                    graph_id="graph-gui-runner",
                    name="GUI Runner",
                    input_path=input_path,
                    output_dir=output_dir,
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-gui-runner")
                persist_planned_execution(
                    connection,
                    project_id="project-gui-runner",
                    project_name="GUI Runner Project",
                    project_root=str(paths.data_root),
                    job_id="job-gui-runner",
                    job_name="GUI Runner Job",
                    graph=graph,
                    plan=plan,
                )

                run_sequential_workflow(
                    connection,
                    plan_id=plan.plan_id,
                    scheduler=SimpleScheduler(
                        HardwareSnapshot(cpu_cores=4, ram_total_mb=8192, ram_free_mb=4096)
                    ),
                    runtime_manager=RuntimeManager(
                        runtime_manifests=[_runtime_manifest(fake_ffmpeg)]
                    ),
                    work_root=root / "worker-work",
                    command_args=(sys.executable, "-m", "atelier.workers.adapter_entry"),
                )

                snapshot = read_workbench_snapshot(connection)
                tasks_by_type = {task.node_type: task for task in snapshot.tasks}
                export_task = tasks_by_type["output.export"]

                self.assertEqual(export_task.final_output_paths, [str(output_dir / "final.wav")])
                self.assertIsNone(export_task.failure_error_code)
                self.assertIsNone(export_task.failure_message)
            finally:
                connection.close()

    def test_workbench_snapshot_reads_failure_facts_from_backend_runner(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths.for_development(root)
            input_path = root / "input.mp4"
            input_path.write_bytes(b"fake media")
            fake_ffmpeg = _write_fake_ffmpeg_failure(root)
            output_dir = root / "exports"
            connection = open_app_database(paths)
            try:
                graph = _audio_export_graph(
                    graph_id="graph-gui-runner-failed",
                    name="GUI Runner Failed",
                    input_path=input_path,
                    output_dir=output_dir,
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-gui-runner-failed")
                persist_planned_execution(
                    connection,
                    project_id="project-gui-runner-failed",
                    project_name="GUI Runner Failed Project",
                    project_root=str(paths.data_root),
                    job_id="job-gui-runner-failed",
                    job_name="GUI Runner Failed Job",
                    graph=graph,
                    plan=plan,
                )

                run_sequential_workflow(
                    connection,
                    plan_id=plan.plan_id,
                    scheduler=SimpleScheduler(
                        HardwareSnapshot(cpu_cores=4, ram_total_mb=8192, ram_free_mb=4096)
                    ),
                    runtime_manager=RuntimeManager(
                        runtime_manifests=[_runtime_manifest(fake_ffmpeg)]
                    ),
                    work_root=root / "worker-work",
                    command_args=(sys.executable, "-m", "atelier.workers.adapter_entry"),
                )

                snapshot = read_workbench_snapshot(connection)
                tasks_by_type = {task.node_type: task for task in snapshot.tasks}
                audio_task = tasks_by_type["media.audio_extract"]
                export_task = tasks_by_type["output.export"]

                self.assertEqual(audio_task.failure_error_code, "DEPENDENCY")
                self.assertIn("no audio stream", audio_task.failure_message or "")
                self.assertEqual(audio_task.final_output_paths, [])
                self.assertEqual(export_task.status, "pending")
                self.assertIsNone(export_task.failure_error_code)
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


def _write_fake_ffmpeg_failure(root: Path) -> Path:
    fake_ffmpeg = root / "fake_ffmpeg_failed.cmd"
    fake_ffmpeg.write_text("@echo no audio stream 1>&2\n@exit /b 1\n", encoding="ascii")
    return fake_ffmpeg


if __name__ == "__main__":
    unittest.main()
