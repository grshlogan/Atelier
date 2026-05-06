import time
import unittest

from atelier.gui.workflow_run_intent import WorkflowRunIntentExecutor


class GuiWorkflowRunIntentExecutorTests(unittest.TestCase):
    def test_executor_submits_run_intent_without_waiting_for_completion(self) -> None:
        service = _SlowRunIntentService()
        executor = WorkflowRunIntentExecutor()
        try:
            started_at = time.perf_counter()
            future = executor.submit(service=service, plan_id="plan-background")
            elapsed = time.perf_counter() - started_at

            self.assertLess(elapsed, 0.2)
            self.assertFalse(future.done())
            self.assertEqual(future.result(timeout=2), None)
            self.assertEqual(service.requested_plan_ids, ["plan-background"])
        finally:
            executor.shutdown(wait=True)


class _SlowRunIntentService:
    def __init__(self) -> None:
        self.requested_plan_ids: list[str] = []

    def request_run(self, plan_id: str) -> None:
        time.sleep(0.5)
        self.requested_plan_ids.append(plan_id)


if __name__ == "__main__":
    unittest.main()
