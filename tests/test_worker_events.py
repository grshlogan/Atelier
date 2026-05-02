import unittest

from atelier.domain.worker_event import FailedEvent, task_status_from_terminal_event


class WorkerEventTests(unittest.TestCase):
    def test_cancelled_failure_normalizes_to_cancelled_task_status(self) -> None:
        event = FailedEvent(
            task_id="01TESTTASK0000000000000001",
            timestamp="2026-05-03T00:00:00Z",
            seq=3,
            error_code="CANCELLED",
            message="cancelled by user",
            recoverable=False,
        )

        self.assertEqual(task_status_from_terminal_event(event), "cancelled")

    def test_interrupted_failure_stays_failed_but_recoverable(self) -> None:
        event = FailedEvent(
            task_id="01TESTTASK0000000000000001",
            timestamp="2026-05-03T00:00:00Z",
            seq=4,
            error_code="INTERRUPTED",
            message="worker process disappeared",
            recoverable=True,
        )

        self.assertEqual(task_status_from_terminal_event(event), "failed")
        self.assertTrue(event.recoverable)


if __name__ == "__main__":
    unittest.main()
