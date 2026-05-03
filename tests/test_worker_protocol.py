import json
import unittest

from atelier.domain.worker_event import (
    CompletedEvent,
    HeartbeatEvent,
    LogEvent,
    ProgressEvent,
    StartedEvent,
)
from atelier.workers.protocol import (
    WorkerProtocolError,
    format_worker_event_json_line,
    parse_worker_event_stream,
    parse_worker_event_json_line,
)


class WorkerProtocolTests(unittest.TestCase):
    def test_serializes_worker_event_as_single_json_line(self) -> None:
        event = ProgressEvent(
            task_id="01TESTTASK0000000000000001",
            timestamp="2026-05-03T00:00:00Z",
            seq=1,
            current=25,
            total=100,
            unit="frames",
            percent=25.0,
            stage="decode",
            eta_seconds=12.5,
        )

        line = format_worker_event_json_line(event)

        self.assertTrue(line.endswith("\n"))
        self.assertNotIn("\n", line[:-1])
        payload = json.loads(line)
        self.assertEqual(payload["type"], "progress")
        self.assertEqual(payload["task_id"], "01TESTTASK0000000000000001")
        self.assertEqual(payload["percent"], 25.0)

    def test_parses_json_line_to_specific_event_model(self) -> None:
        line = (
            '{"type":"completed","task_id":"01TESTTASK0000000000000001",'
            '"timestamp":"2026-05-03T00:00:03Z","seq":3,'
            '"artifacts":[{"artifact_id":"01TESTART0000000000000001",'
            '"artifact_type":"subtitle","path":"01TESTTASK0000000000000001/out.srt"}],'
            '"duration_seconds":3.5}\n'
        )

        event = parse_worker_event_json_line(line)

        self.assertIsInstance(event, CompletedEvent)
        self.assertEqual(event.artifacts[0].artifact_type, "subtitle")
        self.assertEqual(event.duration_seconds, 3.5)

    def test_round_trips_protocol_log_and_heartbeat_events(self) -> None:
        events = [
            LogEvent(
                task_id="01TESTTASK0000000000000001",
                timestamp="2026-05-03T00:00:01Z",
                seq=1,
                level="info",
                message="loading model",
            ),
            HeartbeatEvent(
                task_id="01TESTTASK0000000000000001",
                timestamp="2026-05-03T00:00:02Z",
                seq=2,
                uptime_seconds=2.0,
                memory_mb=512.5,
                gpu_memory_mb=None,
            ),
            StartedEvent(
                task_id="01TESTTASK0000000000000001",
                timestamp="2026-05-03T00:00:00Z",
                seq=0,
                worker_pid=1234,
                worker_version="test",
                node_type="simulate.echo",
            ),
        ]

        parsed_events = [parse_worker_event_json_line(format_worker_event_json_line(event)) for event in events]

        self.assertIsInstance(parsed_events[0], LogEvent)
        self.assertEqual(parsed_events[0].message, "loading model")
        self.assertIsInstance(parsed_events[1], HeartbeatEvent)
        self.assertEqual(parsed_events[1].memory_mb, 512.5)
        self.assertIsInstance(parsed_events[2], StartedEvent)
        self.assertEqual(parsed_events[2].node_type, "simulate.echo")

    def test_rejects_malformed_non_object_and_unknown_event_lines(self) -> None:
        malformed_lines = [
            "not json\n",
            '["progress"]\n',
            '{"type":"unknown","task_id":"01TESTTASK0000000000000001","timestamp":"2026-05-03T00:00:00Z","seq":0}\n',
        ]

        for line in malformed_lines:
            with self.subTest(line=line):
                with self.assertRaises(WorkerProtocolError):
                    parse_worker_event_json_line(line)

    def test_parses_valid_worker_event_stream(self) -> None:
        lines = [
            format_worker_event_json_line(
                StartedEvent(
                    task_id="01TESTTASK0000000000000001",
                    timestamp="2026-05-03T00:00:00Z",
                    seq=0,
                    worker_pid=1234,
                    worker_version="test",
                    node_type="simulate.echo",
                )
            ),
            format_worker_event_json_line(
                LogEvent(
                    task_id="01TESTTASK0000000000000001",
                    timestamp="2026-05-03T00:00:01Z",
                    seq=1,
                    level="info",
                    message="running",
                )
            ),
            format_worker_event_json_line(
                CompletedEvent(
                    task_id="01TESTTASK0000000000000001",
                    timestamp="2026-05-03T00:00:02Z",
                    seq=2,
                    artifacts=[],
                    duration_seconds=2.0,
                )
            ),
        ]

        events = parse_worker_event_stream(lines)

        self.assertEqual([event.type for event in events], ["started", "log", "completed"])
        self.assertIsInstance(events[-1], CompletedEvent)

    def test_rejects_event_stream_without_started_first(self) -> None:
        lines = [
            format_worker_event_json_line(
                ProgressEvent(
                    task_id="01TESTTASK0000000000000001",
                    timestamp="2026-05-03T00:00:00Z",
                    seq=0,
                    current=1,
                    total=2,
                    unit="steps",
                    percent=50.0,
                )
            )
        ]

        with self.assertRaises(WorkerProtocolError):
            parse_worker_event_stream(lines)

    def test_rejects_event_stream_with_non_contiguous_sequence(self) -> None:
        lines = [
            format_worker_event_json_line(
                StartedEvent(
                    task_id="01TESTTASK0000000000000001",
                    timestamp="2026-05-03T00:00:00Z",
                    seq=0,
                    worker_pid=1234,
                    worker_version="test",
                    node_type="simulate.echo",
                )
            ),
            format_worker_event_json_line(
                CompletedEvent(
                    task_id="01TESTTASK0000000000000001",
                    timestamp="2026-05-03T00:00:02Z",
                    seq=2,
                    artifacts=[],
                    duration_seconds=2.0,
                )
            ),
        ]

        with self.assertRaises(WorkerProtocolError):
            parse_worker_event_stream(lines)

    def test_rejects_event_stream_without_terminal_event(self) -> None:
        lines = [
            format_worker_event_json_line(
                StartedEvent(
                    task_id="01TESTTASK0000000000000001",
                    timestamp="2026-05-03T00:00:00Z",
                    seq=0,
                    worker_pid=1234,
                    worker_version="test",
                    node_type="simulate.echo",
                )
            ),
            format_worker_event_json_line(
                HeartbeatEvent(
                    task_id="01TESTTASK0000000000000001",
                    timestamp="2026-05-03T00:00:01Z",
                    seq=1,
                    uptime_seconds=1.0,
                    memory_mb=256.0,
                )
            ),
        ]

        with self.assertRaises(WorkerProtocolError):
            parse_worker_event_stream(lines)

    def test_rejects_event_stream_after_terminal_event(self) -> None:
        lines = [
            format_worker_event_json_line(
                StartedEvent(
                    task_id="01TESTTASK0000000000000001",
                    timestamp="2026-05-03T00:00:00Z",
                    seq=0,
                    worker_pid=1234,
                    worker_version="test",
                    node_type="simulate.echo",
                )
            ),
            format_worker_event_json_line(
                CompletedEvent(
                    task_id="01TESTTASK0000000000000001",
                    timestamp="2026-05-03T00:00:01Z",
                    seq=1,
                    artifacts=[],
                    duration_seconds=1.0,
                )
            ),
            format_worker_event_json_line(
                LogEvent(
                    task_id="01TESTTASK0000000000000001",
                    timestamp="2026-05-03T00:00:02Z",
                    seq=2,
                    level="info",
                    message="too late",
                )
            ),
        ]

        with self.assertRaises(WorkerProtocolError):
            parse_worker_event_stream(lines)


if __name__ == "__main__":
    unittest.main()
