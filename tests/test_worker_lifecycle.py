import json
import sys
import tempfile
import threading
import textwrap
import unittest
from pathlib import Path

from atelier.workers.runner import (
    WorkerLifecycleConfig,
    WorkerProcessProtocolError,
    WorkerProcessSpec,
    run_worker_lifecycle,
)


class WorkerLifecycleTests(unittest.TestCase):
    def test_lifecycle_runner_returns_process_facts_without_changing_existing_runner_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work_dir = root / "work"
            work_dir.mkdir()
            task_file = root / "task.json"
            task_file.write_text(json.dumps({"task_id": "01LIFECYCLETEST000000000001"}), encoding="utf-8")
            script = root / "lifecycle_stub_worker.py"
            script.write_text(
                textwrap.dedent(
                    """
                    import argparse
                    import json
                    import sys
                    from pathlib import Path

                    parser = argparse.ArgumentParser()
                    parser.add_argument("--task-file", required=True)
                    args = parser.parse_args()
                    task_id = json.loads(Path(args.task_file).read_text(encoding="utf-8"))["task_id"]
                    sys.stderr.write("lifecycle stderr line\\n")
                    print(json.dumps({
                        "type": "started",
                        "task_id": task_id,
                        "timestamp": "2026-05-04T00:00:00Z",
                        "seq": 0,
                        "worker_pid": 1234,
                        "worker_version": "stub",
                        "node_type": "simulate.lifecycle"
                    }))
                    print(json.dumps({
                        "type": "completed",
                        "task_id": task_id,
                        "timestamp": "2026-05-04T00:00:01Z",
                        "seq": 1,
                        "artifacts": [],
                        "duration_seconds": 1.0
                    }))
                    """
                ),
                encoding="utf-8",
            )

            result = run_worker_lifecycle(
                WorkerProcessSpec(
                    command_args=(sys.executable, str(script)),
                    task_file=task_file,
                    work_dir=work_dir,
                ),
                config=WorkerLifecycleConfig(
                    startup_timeout_seconds=3.0,
                    heartbeat_timeout_seconds=4.0,
                    terminate_grace_seconds=5.0,
                ),
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual([event.type for event in result.events], ["started", "completed"])
        self.assertIn("lifecycle stderr line", result.stderr)
        self.assertIsNone(result.stderr_log_path)
        self.assertFalse(result.timed_out)
        self.assertFalse(result.cancelled)
        self.assertFalse(result.killed)

    def test_lifecycle_runner_times_out_silent_worker_with_structured_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work_dir = root / "work"
            work_dir.mkdir()
            task_file = root / "task.json"
            task_file.write_text(json.dumps({"task_id": "01LIFECYCLETIMEOUT000000001"}), encoding="utf-8")
            script = root / "silent_worker.py"
            script.write_text(
                textwrap.dedent(
                    """
                    import argparse
                    import time

                    parser = argparse.ArgumentParser()
                    parser.add_argument("--task-file", required=True)
                    parser.parse_args()
                    time.sleep(0.3)
                    """
                ),
                encoding="utf-8",
            )

            result = run_worker_lifecycle(
                WorkerProcessSpec(
                    command_args=(sys.executable, "-u", str(script)),
                    task_file=task_file,
                    work_dir=work_dir,
                ),
                config=WorkerLifecycleConfig(
                    startup_timeout_seconds=0.05,
                    heartbeat_timeout_seconds=0.05,
                    terminate_grace_seconds=0.05,
                ),
            )

        self.assertTrue(result.timed_out)
        self.assertFalse(result.cancelled)
        self.assertEqual([event.type for event in result.events], ["failed"])
        self.assertEqual(result.events[0].task_id, "01LIFECYCLETIMEOUT000000001")
        self.assertEqual(result.events[0].error_code, "TIMEOUT")
        self.assertIn("timed out", result.events[0].message)
        self.assertTrue(result.events[0].recoverable)

    def test_lifecycle_runner_keeps_worker_alive_after_heartbeat(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work_dir = root / "work"
            work_dir.mkdir()
            task_file = root / "task.json"
            task_file.write_text(json.dumps({"task_id": "01LIFECYCLEHEARTBEAT000001"}), encoding="utf-8")
            script = root / "heartbeat_worker.py"
            script.write_text(
                textwrap.dedent(
                    """
                    import argparse
                    import json
                    import time
                    from pathlib import Path

                    parser = argparse.ArgumentParser()
                    parser.add_argument("--task-file", required=True)
                    args = parser.parse_args()
                    task_id = json.loads(Path(args.task_file).read_text(encoding="utf-8"))["task_id"]
                    print(json.dumps({
                        "type": "started",
                        "task_id": task_id,
                        "timestamp": "2026-05-04T00:00:00Z",
                        "seq": 0,
                        "worker_pid": 1234,
                        "worker_version": "stub",
                        "node_type": "simulate.heartbeat"
                    }), flush=True)
                    time.sleep(0.04)
                    print(json.dumps({
                        "type": "heartbeat",
                        "task_id": task_id,
                        "timestamp": "2026-05-04T00:00:01Z",
                        "seq": 1,
                        "uptime_seconds": 1.0,
                        "memory_mb": 64.0
                    }), flush=True)
                    time.sleep(0.04)
                    print(json.dumps({
                        "type": "completed",
                        "task_id": task_id,
                        "timestamp": "2026-05-04T00:00:02Z",
                        "seq": 2,
                        "artifacts": [],
                        "duration_seconds": 2.0
                    }), flush=True)
                    """
                ),
                encoding="utf-8",
            )

            result = run_worker_lifecycle(
                WorkerProcessSpec(
                    command_args=(sys.executable, "-u", str(script)),
                    task_file=task_file,
                    work_dir=work_dir,
                ),
                config=WorkerLifecycleConfig(
                    startup_timeout_seconds=0.1,
                    heartbeat_timeout_seconds=0.1,
                    terminate_grace_seconds=0.05,
                ),
            )

        self.assertFalse(result.timed_out)
        self.assertFalse(result.killed)
        self.assertEqual([event.type for event in result.events], ["started", "heartbeat", "completed"])

    def test_lifecycle_runner_sends_cancel_to_cancel_aware_worker(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work_dir = root / "work"
            work_dir.mkdir()
            task_file = root / "task.json"
            task_file.write_text(json.dumps({"task_id": "01LIFECYCLECANCEL000000001"}), encoding="utf-8")
            script = root / "cancel_aware_worker.py"
            script.write_text(
                textwrap.dedent(
                    """
                    import argparse
                    import json
                    import sys
                    from pathlib import Path

                    parser = argparse.ArgumentParser()
                    parser.add_argument("--task-file", required=True)
                    args = parser.parse_args()
                    task_id = json.loads(Path(args.task_file).read_text(encoding="utf-8"))["task_id"]
                    print(json.dumps({
                        "type": "started",
                        "task_id": task_id,
                        "timestamp": "2026-05-04T00:00:00Z",
                        "seq": 0,
                        "worker_pid": 1234,
                        "worker_version": "stub",
                        "node_type": "simulate.cancel"
                    }), flush=True)
                    for line in sys.stdin:
                        command = json.loads(line)
                        if command.get("type") == "cancel":
                            print(json.dumps({
                                "type": "failed",
                                "task_id": task_id,
                                "timestamp": "2026-05-04T00:00:01Z",
                                "seq": 1,
                                "error_code": "CANCELLED",
                                "message": "cancelled by runner",
                                "recoverable": False,
                                "partial_artifacts": []
                            }), flush=True)
                            raise SystemExit(0)
                    """
                ),
                encoding="utf-8",
            )
            cancel_event = threading.Event()
            cancel_event.set()

            result = run_worker_lifecycle(
                WorkerProcessSpec(
                    command_args=(sys.executable, "-u", str(script)),
                    task_file=task_file,
                    work_dir=work_dir,
                ),
                config=WorkerLifecycleConfig(
                    startup_timeout_seconds=0.1,
                    heartbeat_timeout_seconds=1.0,
                    terminate_grace_seconds=0.05,
                    cancel_grace_seconds=0.2,
                ),
                cancel_event=cancel_event,
            )

        self.assertTrue(result.cancelled)
        self.assertFalse(result.timed_out)
        self.assertFalse(result.killed)
        self.assertEqual([event.type for event in result.events], ["started", "failed"])
        self.assertEqual(result.events[-1].error_code, "CANCELLED")
        self.assertEqual(result.returncode, 0)

    def test_lifecycle_runner_terminates_worker_that_ignores_cancel(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work_dir = root / "work"
            work_dir.mkdir()
            task_file = root / "task.json"
            task_file.write_text(json.dumps({"task_id": "01LIFECYCLESTUCKCANCEL001"}), encoding="utf-8")
            script = root / "stuck_cancel_worker.py"
            script.write_text(
                textwrap.dedent(
                    """
                    import argparse
                    import json
                    import time
                    from pathlib import Path

                    parser = argparse.ArgumentParser()
                    parser.add_argument("--task-file", required=True)
                    args = parser.parse_args()
                    task_id = json.loads(Path(args.task_file).read_text(encoding="utf-8"))["task_id"]
                    print(json.dumps({
                        "type": "started",
                        "task_id": task_id,
                        "timestamp": "2026-05-04T00:00:00Z",
                        "seq": 0,
                        "worker_pid": 1234,
                        "worker_version": "stub",
                        "node_type": "simulate.stuck_cancel"
                    }), flush=True)
                    time.sleep(1.0)
                    """
                ),
                encoding="utf-8",
            )
            cancel_event = threading.Event()
            cancel_event.set()

            result = run_worker_lifecycle(
                WorkerProcessSpec(
                    command_args=(sys.executable, "-u", str(script)),
                    task_file=task_file,
                    work_dir=work_dir,
                ),
                config=WorkerLifecycleConfig(
                    startup_timeout_seconds=0.1,
                    heartbeat_timeout_seconds=5.0,
                    terminate_grace_seconds=0.05,
                    cancel_grace_seconds=0.05,
                ),
                cancel_event=cancel_event,
            )

        self.assertTrue(result.cancelled)
        self.assertFalse(result.timed_out)
        self.assertEqual([event.type for event in result.events], ["started", "failed"])
        self.assertEqual(result.events[-1].error_code, "CANCELLED")
        self.assertNotEqual(result.returncode, 0)

    def test_lifecycle_runner_writes_stderr_to_log_path_without_using_it_for_events(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work_dir = root / "work"
            work_dir.mkdir()
            task_file = root / "task.json"
            task_file.write_text(json.dumps({"task_id": "01LIFECYCLESTDERR00000001"}), encoding="utf-8")
            stderr_log_path = root / "logs" / "worker.stderr.log"
            script = root / "stderr_worker.py"
            script.write_text(
                textwrap.dedent(
                    """
                    import argparse
                    import json
                    import sys
                    from pathlib import Path

                    parser = argparse.ArgumentParser()
                    parser.add_argument("--task-file", required=True)
                    args = parser.parse_args()
                    task_id = json.loads(Path(args.task_file).read_text(encoding="utf-8"))["task_id"]
                    sys.stderr.write("stderr detail one\\n")
                    sys.stderr.write("stderr detail two\\n")
                    print(json.dumps({
                        "type": "started",
                        "task_id": task_id,
                        "timestamp": "2026-05-04T00:00:00Z",
                        "seq": 0,
                        "worker_pid": 1234,
                        "worker_version": "stub",
                        "node_type": "simulate.stderr"
                    }), flush=True)
                    print(json.dumps({
                        "type": "completed",
                        "task_id": task_id,
                        "timestamp": "2026-05-04T00:00:01Z",
                        "seq": 1,
                        "artifacts": [],
                        "duration_seconds": 1.0
                    }), flush=True)
                    """
                ),
                encoding="utf-8",
            )

            result = run_worker_lifecycle(
                WorkerProcessSpec(
                    command_args=(sys.executable, "-u", str(script)),
                    task_file=task_file,
                    work_dir=work_dir,
                ),
                stderr_log_path=stderr_log_path,
            )

            stderr_log = stderr_log_path.read_text(encoding="utf-8")

        self.assertEqual([event.type for event in result.events], ["started", "completed"])
        self.assertEqual(result.stderr_log_path, stderr_log_path)
        self.assertIn("stderr detail one", result.stderr)
        self.assertIn("stderr detail two", stderr_log)

    def test_lifecycle_runner_stops_protocol_error_worker_and_writes_stderr_log(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work_dir = root / "work"
            work_dir.mkdir()
            task_file = root / "task.json"
            task_file.write_text(json.dumps({"task_id": "01LIFECYCLEBADSTDOUT00001"}), encoding="utf-8")
            stderr_log_path = root / "logs" / "protocol.stderr.log"
            script = root / "bad_stdout_hanging_worker.py"
            script.write_text(
                textwrap.dedent(
                    """
                    import sys
                    import time

                    sys.stderr.write("protocol detail before hang\\n")
                    print("not json", flush=True)
                    time.sleep(1.0)
                    """
                ),
                encoding="utf-8",
            )

            with self.assertRaises(WorkerProcessProtocolError) as context:
                run_worker_lifecycle(
                    WorkerProcessSpec(
                        command_args=(sys.executable, "-u", str(script)),
                        task_file=task_file,
                        work_dir=work_dir,
                    ),
                    config=WorkerLifecycleConfig(terminate_grace_seconds=0.05),
                    stderr_log_path=stderr_log_path,
                )

            stderr_log = stderr_log_path.read_text(encoding="utf-8")

        self.assertNotEqual(context.exception.returncode, 0)
        self.assertIn("protocol detail before hang", context.exception.stderr)
        self.assertIn("protocol detail before hang", stderr_log)


if __name__ == "__main__":
    unittest.main()
