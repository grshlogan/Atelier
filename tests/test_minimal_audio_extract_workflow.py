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
from atelier.scheduler.dispatch import dispatch_claimed_task
from atelier.scheduler.simple import SimpleScheduler
from atelier.storage.repositories import (
    fetch_artifact_paths,
    fetch_failure_facts,
    fetch_task_event_types,
    fetch_task_status,
    persist_planned_execution,
)
from atelier.workflow.graph import WorkflowGraph, WorkflowNode


class MinimalAudioExtractWorkflowTests(unittest.TestCase):
    def test_audio_extract_worker_dispatch_persists_artifact_and_completed_status(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths.for_development(root)
            input_path = root / "input.mp4"
            input_path.write_bytes(b"fake media")
            fake_ffmpeg = _write_fake_ffmpeg_success(root)
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-audio-extract",
                    name="Audio Extract",
                    nodes=[
                        WorkflowNode(
                            node_id="node-audio-extract",
                            node_type="media.audio_extract",
                            params={"input_path": str(input_path)},
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(
                                components=["ffmpeg"],
                                capabilities=["audio-extract"],
                            ),
                        )
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-audio-extract")
                persist_planned_execution(
                    connection,
                    project_id="project-audio-extract",
                    project_name="Audio Extract Project",
                    project_root=str(paths.data_root),
                    job_id="job-audio-extract",
                    job_name="Audio Extract Job",
                    graph=graph,
                    plan=plan,
                )
                claimed = SimpleScheduler(
                    HardwareSnapshot(cpu_cores=4, ram_total_mb=8192, ram_free_mb=4096)
                ).claim_next_task(connection, plan.plan_id)
                self.assertIsNotNone(claimed)
                assert claimed is not None
                runtime_binding = RuntimeManager(
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
                ).resolve(claimed.task.runtime_request)

                result = dispatch_claimed_task(
                    connection,
                    claimed_task=claimed,
                    work_root=root / "worker-work",
                    command_args=(sys.executable, "-m", "atelier.workers.adapter_entry"),
                    runtime_binding=runtime_binding,
                )

                self.assertEqual(result.task_status, "completed")
                self.assertEqual([event.type for event in result.events], ["started", "artifact", "completed"])
                self.assertEqual(fetch_task_status(connection, claimed.task.task_id), "completed")
                self.assertEqual(
                    fetch_task_event_types(connection, claimed.task.task_id),
                    ["started", "artifact", "completed"],
                )
                self.assertEqual(fetch_artifact_paths(connection, claimed.task.task_id), ["audio.wav"])
                self.assertEqual(
                    (root / "worker-work" / claimed.task.task_id / "audio.wav").read_text(encoding="utf-8").strip(),
                    "fake wav",
                )
            finally:
                connection.close()

    def test_failing_ffmpeg_persists_structured_failure(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths.for_development(root)
            input_path = root / "input.mp4"
            input_path.write_bytes(b"fake media")
            fake_ffmpeg = _write_fake_ffmpeg_failure(root)
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-audio-extract-failed",
                    name="Audio Extract Failed",
                    nodes=[
                        WorkflowNode(
                            node_id="node-audio-extract-failed",
                            node_type="media.audio_extract",
                            params={"input_path": str(input_path)},
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(
                                components=["ffmpeg"],
                                capabilities=["audio-extract"],
                            ),
                        )
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-audio-extract-failed")
                persist_planned_execution(
                    connection,
                    project_id="project-audio-extract-failed",
                    project_name="Audio Extract Failed Project",
                    project_root=str(paths.data_root),
                    job_id="job-audio-extract-failed",
                    job_name="Audio Extract Failed Job",
                    graph=graph,
                    plan=plan,
                )
                claimed = SimpleScheduler(
                    HardwareSnapshot(cpu_cores=4, ram_total_mb=8192, ram_free_mb=4096)
                ).claim_next_task(connection, plan.plan_id)
                self.assertIsNotNone(claimed)
                assert claimed is not None
                runtime_binding = RuntimeManager(
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
                ).resolve(claimed.task.runtime_request)

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
                self.assertEqual(facts.error_code, "DEPENDENCY")
                self.assertIn("no audio stream", facts.error_message)
                self.assertTrue(facts.recoverable)
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
