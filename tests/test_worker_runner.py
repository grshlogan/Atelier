import json
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from atelier.workers.protocol import WorkerProtocolError
from atelier.workers.runner import WorkerProcessSpec, run_worker_process


class WorkerRunnerTests(unittest.TestCase):
    def test_runner_passes_task_file_work_dir_and_env_to_stub_worker(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work_dir = root / "work"
            work_dir.mkdir()
            task_file = root / "task.json"
            task_file.write_text(json.dumps({"task_id": "01TESTTASK0000000000000001"}), encoding="utf-8")
            script = root / "stub_worker.py"
            script.write_text(
                textwrap.dedent(
                    """
                    import argparse
                    import json
                    import os
                    import sys
                    from pathlib import Path

                    parser = argparse.ArgumentParser()
                    parser.add_argument("--task-file", required=True)
                    args = parser.parse_args()
                    task_id = json.loads(Path(args.task_file).read_text(encoding="utf-8"))["task_id"]
                    sys.stderr.write("stub stderr line\\n")
                    print(json.dumps({
                        "type": "started",
                        "task_id": task_id,
                        "timestamp": "2026-05-04T00:00:00Z",
                        "seq": 0,
                        "worker_pid": 1234,
                        "worker_version": "stub",
                        "node_type": "simulate.echo"
                    }))
                    print(json.dumps({
                        "type": "log",
                        "task_id": task_id,
                        "timestamp": "2026-05-04T00:00:01Z",
                        "seq": 1,
                        "level": "info",
                        "message": f"{os.environ.get('ATELIER_TEST_FLAG')}|{Path.cwd().name}"
                    }))
                    print(json.dumps({
                        "type": "completed",
                        "task_id": task_id,
                        "timestamp": "2026-05-04T00:00:02Z",
                        "seq": 2,
                        "artifacts": [],
                        "duration_seconds": 2.0
                    }))
                    """
                ),
                encoding="utf-8",
            )

            result = run_worker_process(
                WorkerProcessSpec(
                    command_args=(sys.executable, str(script)),
                    task_file=task_file,
                    work_dir=work_dir,
                    env={"ATELIER_TEST_FLAG": "env-seen"},
                )
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual([event.type for event in result.events], ["started", "log", "completed"])
        self.assertEqual(result.events[1].message, "env-seen|work")
        self.assertIn("stub stderr line", result.stderr)

    def test_runner_returns_nonzero_exit_code_with_valid_failed_event_stream(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work_dir = root / "work"
            work_dir.mkdir()
            task_file = root / "task.json"
            task_file.write_text(json.dumps({"task_id": "01TESTTASK0000000000000002"}), encoding="utf-8")
            script = root / "failed_stub_worker.py"
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
                    sys.stderr.write("failure detail\\n")
                    print(json.dumps({
                        "type": "started",
                        "task_id": task_id,
                        "timestamp": "2026-05-04T00:00:00Z",
                        "seq": 0,
                        "worker_pid": 1234,
                        "worker_version": "stub",
                        "node_type": "simulate.fail"
                    }))
                    print(json.dumps({
                        "type": "failed",
                        "task_id": task_id,
                        "timestamp": "2026-05-04T00:00:01Z",
                        "seq": 1,
                        "error_code": "INTERNAL",
                        "message": "stub failed",
                        "recoverable": True,
                        "partial_artifacts": []
                    }))
                    raise SystemExit(7)
                    """
                ),
                encoding="utf-8",
            )

            result = run_worker_process(
                WorkerProcessSpec(
                    command_args=(sys.executable, str(script)),
                    task_file=task_file,
                    work_dir=work_dir,
                )
            )

        self.assertEqual(result.returncode, 7)
        self.assertEqual(result.events[-1].type, "failed")
        self.assertIn("failure detail", result.stderr)

    def test_runner_raises_protocol_error_for_invalid_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work_dir = root / "work"
            work_dir.mkdir()
            task_file = root / "task.json"
            task_file.write_text("{}", encoding="utf-8")
            script = root / "bad_stdout_worker.py"
            script.write_text("print('not json')\n", encoding="utf-8")

            with self.assertRaises(WorkerProtocolError):
                run_worker_process(
                    WorkerProcessSpec(
                        command_args=(sys.executable, str(script)),
                        task_file=task_file,
                        work_dir=work_dir,
                    )
                )


if __name__ == "__main__":
    unittest.main()
