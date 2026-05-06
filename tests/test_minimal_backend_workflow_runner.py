import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from atelier.app.paths import AppPaths
from atelier.app.services import open_app_database
from atelier.domain.resources import HardwareSnapshot, ResourceRequest, RuntimeRequest
from atelier.planning.simple import build_linear_execution_plan
from atelier.runtime.manager import RuntimeManager
from atelier.runtime.manifest import RuntimeManifest
from atelier.scheduler.simple import SimpleScheduler
from atelier.scheduler.workflow_runner import run_sequential_workflow
from atelier.storage.repositories import (
    fetch_artifact_paths,
    fetch_failure_facts,
    fetch_task_artifact_links,
    fetch_task_status,
    persist_planned_execution,
)
from atelier.workflow.graph import WorkflowEdge, WorkflowGraph, WorkflowNode, WorkflowPortRef


class MinimalBackendWorkflowRunnerTests(unittest.TestCase):
    def test_runner_executes_audio_extract_then_output_export(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths.for_development(root)
            input_path = root / "input.mp4"
            input_path.write_bytes(b"fake media")
            fake_ffmpeg = _write_fake_ffmpeg_success(root)
            output_dir = root / "exports"
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-backend-runner",
                    name="Backend Runner",
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
                plan = build_linear_execution_plan(graph, plan_id="plan-backend-runner")
                audio_task = plan.tasks[0]
                export_task = plan.tasks[1]
                persist_planned_execution(
                    connection,
                    project_id="project-backend-runner",
                    project_name="Backend Runner Project",
                    project_root=str(paths.data_root),
                    job_id="job-backend-runner",
                    job_name="Backend Runner Job",
                    graph=graph,
                    plan=plan,
                )

                result = run_sequential_workflow(
                    connection,
                    plan_id=plan.plan_id,
                    scheduler=SimpleScheduler(
                        HardwareSnapshot(cpu_cores=4, ram_total_mb=8192, ram_free_mb=4096)
                    ),
                    runtime_manager=RuntimeManager(
                        runtime_manifests=[
                            RuntimeManifest(
                                runtime_id="ffmpeg-fake",
                                component="ffmpeg",
                                version="fake",
                                component_paths={"ffmpeg": str(fake_ffmpeg)},
                                executable_paths={"ffmpeg": str(fake_ffmpeg)},
                                capabilities=["audio-extract"],
                                profile_kind="local",
                            )
                        ]
                    ),
                    work_root=root / "worker-work",
                    command_args=(sys.executable, "-m", "atelier.workers.adapter_entry"),
                )

                self.assertEqual(result.status, "completed")
                self.assertEqual(result.dispatched_task_ids, [audio_task.task_id, export_task.task_id])
                self.assertEqual(fetch_task_status(connection, audio_task.task_id), "completed")
                self.assertEqual(fetch_task_status(connection, export_task.task_id), "completed")
                self.assertEqual(fetch_artifact_paths(connection, audio_task.task_id), ["audio.wav"])
                self.assertEqual(fetch_artifact_paths(connection, export_task.task_id), [
                    str(output_dir / "final.wav")
                ])
                self.assertEqual(fetch_task_artifact_links(connection, export_task.task_id), [
                    (f"{export_task.task_id}-final-output", "final_output")
                ])
                self.assertEqual((output_dir / "final.wav").read_text(encoding="utf-8").strip(), "fake wav")
            finally:
                connection.close()

    def test_runner_stops_when_a_task_fails(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths.for_development(root)
            input_path = root / "input.mp4"
            input_path.write_bytes(b"fake media")
            fake_ffmpeg = _write_fake_ffmpeg_failure(root)
            output_dir = root / "exports"
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-backend-runner-failed",
                    name="Backend Runner Failed",
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
                plan = build_linear_execution_plan(graph, plan_id="plan-backend-runner-failed")
                audio_task = plan.tasks[0]
                export_task = plan.tasks[1]
                persist_planned_execution(
                    connection,
                    project_id="project-backend-runner-failed",
                    project_name="Backend Runner Failed Project",
                    project_root=str(paths.data_root),
                    job_id="job-backend-runner-failed",
                    job_name="Backend Runner Failed Job",
                    graph=graph,
                    plan=plan,
                )

                result = run_sequential_workflow(
                    connection,
                    plan_id=plan.plan_id,
                    scheduler=SimpleScheduler(
                        HardwareSnapshot(cpu_cores=4, ram_total_mb=8192, ram_free_mb=4096)
                    ),
                    runtime_manager=RuntimeManager(
                        runtime_manifests=[
                            RuntimeManifest(
                                runtime_id="ffmpeg-fake-failed",
                                component="ffmpeg",
                                version="fake",
                                component_paths={"ffmpeg": str(fake_ffmpeg)},
                                executable_paths={"ffmpeg": str(fake_ffmpeg)},
                                capabilities=["audio-extract"],
                                profile_kind="local",
                            )
                        ]
                    ),
                    work_root=root / "worker-work",
                    command_args=(sys.executable, "-m", "atelier.workers.adapter_entry"),
                )
                facts = fetch_failure_facts(connection, audio_task.task_id)

                self.assertEqual(result.status, "failed")
                self.assertEqual(result.dispatched_task_ids, [audio_task.task_id])
                self.assertEqual(result.stopped_task_id, audio_task.task_id)
                self.assertEqual(fetch_task_status(connection, audio_task.task_id), "failed")
                self.assertEqual(fetch_task_status(connection, export_task.task_id), "pending")
                self.assertEqual(facts.error_code, "DEPENDENCY")
                self.assertFalse((output_dir / "final.wav").exists())
            finally:
                connection.close()


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
