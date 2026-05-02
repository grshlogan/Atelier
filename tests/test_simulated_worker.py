import unittest

from atelier.domain.execution_plan import ExecutionTask
from atelier.domain.resources import ResourceRequest, RuntimeRequest
from atelier.workers.simulated import run_simulated_task


class SimulatedWorkerTests(unittest.TestCase):
    def test_simulated_worker_emits_ordered_json_line_events(self) -> None:
        task = ExecutionTask(
            task_id="01TESTTASK0000000000000001",
            source_node_id="01TESTNODE0000000000000001",
            node_type="simulate.echo",
            params={"message": "hello"},
            input_artifacts=[],
            output_artifact_slots=[],
            resource_request=ResourceRequest(device_type="cpu"),
            runtime_request=RuntimeRequest(components=["simulated"]),
        )

        events = list(run_simulated_task(task, artifact_path="01TESTTASK0000000000000001/output.txt"))

        self.assertEqual([event.type for event in events], ["started", "progress", "artifact", "completed"])
        self.assertEqual([event.seq for event in events], [0, 1, 2, 3])
        self.assertEqual(events[-1].artifacts[0].path, "01TESTTASK0000000000000001/output.txt")


if __name__ == "__main__":
    unittest.main()
