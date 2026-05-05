import json
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


class MinimalProbeWorkflowTests(unittest.TestCase):
    def test_metadata_probe_worker_dispatch_persists_artifact_and_completed_status(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths.for_development(root)
            input_path = root / "input.mp4"
            input_path.write_bytes(b"fake media")
            fake_ffprobe = _write_fake_ffprobe(
                root,
                {
                    "format": {"duration": "1.25", "format_name": "mov,mp4"},
                    "streams": [
                        {
                            "codec_type": "video",
                            "codec_name": "h264",
                            "width": 1280,
                            "height": 720,
                            "avg_frame_rate": "25/1",
                        }
                    ],
                },
            )
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-metadata-probe",
                    name="Metadata Probe",
                    nodes=[
                        WorkflowNode(
                            node_id="node-probe",
                            node_type="metadata.probe",
                            params={"input_path": str(input_path)},
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(
                                components=["ffprobe"],
                                capabilities=["metadata"],
                            ),
                        )
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-metadata-probe")
                persist_planned_execution(
                    connection,
                    project_id="project-metadata-probe",
                    project_name="Metadata Probe Project",
                    project_root=str(paths.data_root),
                    job_id="job-metadata-probe",
                    job_name="Metadata Probe Job",
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
                            runtime_id="ffprobe-fake",
                            component="ffprobe",
                            version="fake",
                            component_paths={"ffprobe": str(fake_ffprobe)},
                            executable_paths={"ffprobe": str(fake_ffprobe)},
                            capabilities=["metadata"],
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
                self.assertEqual(fetch_artifact_paths(connection, claimed.task.task_id), ["probe.json"])
                probe_json = root / "worker-work" / claimed.task.task_id / "probe.json"
                task_json = root / "worker-work" / claimed.task.task_id / "task.json"
                self.assertEqual(json.loads(probe_json.read_text(encoding="utf-8"))["format"]["duration"], "1.25")
                self.assertEqual(
                    json.loads(task_json.read_text(encoding="utf-8"))["runtime_binding"]["component_paths"][
                        "ffprobe"
                    ],
                    str(fake_ffprobe),
                )
            finally:
                connection.close()

    def test_malformed_ffprobe_output_persists_structured_failure(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = AppPaths.for_development(root)
            input_path = root / "input.mp4"
            input_path.write_bytes(b"fake media")
            fake_ffprobe = root / "fake_ffprobe.cmd"
            fake_ffprobe.write_text("@echo not json\n", encoding="ascii")
            connection = open_app_database(paths)
            try:
                graph = WorkflowGraph(
                    graph_id="graph-metadata-probe-invalid",
                    name="Metadata Probe Invalid",
                    nodes=[
                        WorkflowNode(
                            node_id="node-probe-invalid",
                            node_type="metadata.probe",
                            params={"input_path": str(input_path)},
                            resource_request=ResourceRequest(device_type="cpu"),
                            runtime_request=RuntimeRequest(
                                components=["ffprobe"],
                                capabilities=["metadata"],
                            ),
                        )
                    ],
                )
                plan = build_linear_execution_plan(graph, plan_id="plan-metadata-probe-invalid")
                persist_planned_execution(
                    connection,
                    project_id="project-metadata-probe-invalid",
                    project_name="Metadata Probe Invalid Project",
                    project_root=str(paths.data_root),
                    job_id="job-metadata-probe-invalid",
                    job_name="Metadata Probe Invalid Job",
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
                            runtime_id="ffprobe-fake-invalid",
                            component="ffprobe",
                            version="fake",
                            component_paths={"ffprobe": str(fake_ffprobe)},
                            executable_paths={"ffprobe": str(fake_ffprobe)},
                            capabilities=["metadata"],
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
                self.assertIn("invalid ffprobe JSON", facts.error_message)
                self.assertTrue(facts.recoverable)
            finally:
                connection.close()


def _write_fake_ffprobe(root: Path, payload: dict) -> Path:
    fake_ffprobe = root / "fake_ffprobe.cmd"
    fake_ffprobe.write_text(f"@echo {json.dumps(payload)}\n", encoding="ascii")
    return fake_ffprobe


if __name__ == "__main__":
    unittest.main()
