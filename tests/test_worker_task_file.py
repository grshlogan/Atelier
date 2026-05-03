import json
import tempfile
import unittest
from pathlib import Path

from atelier.domain.execution_plan import ExecutionTask
from atelier.domain.resources import ResourceBinding, ResourceRequest, RuntimeBinding, RuntimeRequest
from atelier.workers.task_file import build_worker_process_spec, write_worker_task_file


def _task_with_bindings() -> ExecutionTask:
    return ExecutionTask(
        task_id="01TESTTASK0000000000000001",
        source_node_id="01TESTNODE0000000000000001",
        node_type="simulate.echo",
        params={"message": "hello"},
        input_artifacts=["input/video.mp4"],
        output_artifact_slots=[],
        resource_request=ResourceRequest(device_type="cpu", cpu_cores=2),
        runtime_request=RuntimeRequest(components=["simulated"]),
        resource_binding=ResourceBinding(device_id="cpu:0", binding_reason="test"),
        runtime_binding=RuntimeBinding(
            runtime_id="runtime-simulated",
            component_paths={"simulated": "runtimes/simulated/bin/simulated.exe"},
            model_paths={"stub-model": "models/stub/model.bin"},
            env={"ATELIER_RUNTIME_FLAG": "runtime-env", "SHARED": "runtime"},
            binding_reason="test",
        ),
        status="running",
    )


class WorkerTaskFileTests(unittest.TestCase):
    def test_writes_execution_task_json_to_task_work_dir(self) -> None:
        task = _task_with_bindings()

        with tempfile.TemporaryDirectory() as temp_dir:
            task_dir = Path(temp_dir) / task.task_id

            task_file = write_worker_task_file(task, task_dir)
            payload = json.loads(task_file.read_text(encoding="utf-8"))

        self.assertEqual(task_file.name, "task.json")
        self.assertEqual(payload["task_id"], task.task_id)
        self.assertEqual(payload["node_type"], "simulate.echo")
        self.assertEqual(payload["params"], {"message": "hello"})
        self.assertEqual(payload["resource_binding"]["device_id"], "cpu:0")
        self.assertEqual(payload["runtime_binding"]["runtime_id"], "runtime-simulated")
        self.assertEqual(
            payload["runtime_binding"]["component_paths"]["simulated"],
            "runtimes/simulated/bin/simulated.exe",
        )

    def test_builds_worker_process_spec_without_running_worker(self) -> None:
        task = _task_with_bindings()

        with tempfile.TemporaryDirectory() as temp_dir:
            work_root = Path(temp_dir)

            spec = build_worker_process_spec(
                task,
                command_args=("python", "-m", "atelier.workers.run"),
                work_root=work_root,
                env={"SHARED": "override", "EXTRA": "extra-env"},
            )
            payload = json.loads(spec.task_file.read_text(encoding="utf-8"))

        self.assertEqual(spec.command_args, ("python", "-m", "atelier.workers.run"))
        self.assertEqual(spec.work_dir.name, task.task_id)
        self.assertEqual(spec.task_file.name, "task.json")
        self.assertEqual(payload["task_id"], task.task_id)
        self.assertEqual(spec.env["ATELIER_RUNTIME_FLAG"], "runtime-env")
        self.assertEqual(spec.env["SHARED"], "override")
        self.assertEqual(spec.env["EXTRA"], "extra-env")


if __name__ == "__main__":
    unittest.main()
