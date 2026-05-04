from __future__ import annotations

import json
import os
import queue
import subprocess
import threading
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import TextIO

from atelier.core.time import utc_now_iso
from atelier.domain.worker_event import CompletedEvent, FailedEvent, StartedEvent
from atelier.workers.protocol import (
    WorkerEventPayload,
    WorkerProtocolError,
    parse_worker_event_json_line,
    parse_worker_event_stream,
)


@dataclass(frozen=True)
class WorkerProcessSpec:
    command_args: tuple[str, ...]
    task_file: Path
    work_dir: Path
    env: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class WorkerProcessResult:
    events: list[WorkerEventPayload]
    stderr: str
    returncode: int


@dataclass(frozen=True)
class WorkerLifecycleConfig:
    startup_timeout_seconds: float = 60.0
    heartbeat_timeout_seconds: float = 120.0
    terminate_grace_seconds: float = 15.0
    cancel_grace_seconds: float = 10.0


@dataclass(frozen=True)
class WorkerLifecycleResult:
    events: list[WorkerEventPayload]
    stderr: str
    returncode: int
    stderr_log_path: Path | None = None
    timed_out: bool = False
    cancelled: bool = False
    killed: bool = False


class WorkerProcessProtocolError(WorkerProtocolError):
    def __init__(self, message: str, *, stderr: str, returncode: int) -> None:
        super().__init__(message)
        self.stderr = stderr
        self.returncode = returncode


def run_worker_process(spec: WorkerProcessSpec) -> WorkerProcessResult:
    if not spec.command_args:
        raise ValueError("Worker command_args must not be empty")

    command = [*spec.command_args, "--task-file", str(spec.task_file)]
    process_env = {**os.environ, **dict(spec.env)}
    completed = subprocess.run(
        command,
        cwd=spec.work_dir,
        env=process_env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    try:
        events = parse_worker_event_stream(completed.stdout.splitlines(keepends=True))
    except WorkerProtocolError as exc:
        raise WorkerProcessProtocolError(
            f"Worker protocol error: {exc}",
            stderr=completed.stderr,
            returncode=completed.returncode,
        ) from exc

    return WorkerProcessResult(
        events=events,
        stderr=completed.stderr,
        returncode=completed.returncode,
    )


def run_worker_lifecycle(
    spec: WorkerProcessSpec,
    *,
    config: WorkerLifecycleConfig | None = None,
    cancel_event: threading.Event | None = None,
    stderr_log_path: Path | None = None,
) -> WorkerLifecycleResult:
    if not spec.command_args:
        raise ValueError("Worker command_args must not be empty")

    lifecycle_config = config or WorkerLifecycleConfig()
    command = [*spec.command_args, "--task-file", str(spec.task_file)]
    process_env = {**os.environ, **dict(spec.env)}
    process = subprocess.Popen(
        command,
        cwd=spec.work_dir,
        env=process_env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )

    stdout_queue: queue.Queue[str | None] = queue.Queue()
    stderr_chunks: list[str] = []
    stdout_thread = threading.Thread(
        target=_read_stdout_lines,
        args=(process.stdout, stdout_queue),
        daemon=True,
    )
    stderr_thread = threading.Thread(
        target=_read_stderr_text,
        args=(process.stderr, stderr_chunks),
        daemon=True,
    )
    stdout_thread.start()
    stderr_thread.start()

    events: list[WorkerEventPayload] = []
    terminal_seen = False
    stdout_closed = False
    deadline = time.monotonic() + lifecycle_config.startup_timeout_seconds
    cancel_sent = False
    cancel_deadline: float | None = None

    while True:
        now = time.monotonic()
        if cancel_event is not None and cancel_event.is_set() and not cancel_sent:
            _send_cancel_command(process.stdin)
            cancel_sent = True
            cancel_deadline = now + lifecycle_config.cancel_grace_seconds

        if cancel_deadline is not None and now >= cancel_deadline and not terminal_seen:
            return _finish_cancelled_process(
                process=process,
                stderr_thread=stderr_thread,
                stderr_chunks=stderr_chunks,
                events=events,
                task_id=_read_task_id(spec.task_file),
                terminate_grace_seconds=lifecycle_config.terminate_grace_seconds,
                stderr_log_path=stderr_log_path,
            )

        if process.poll() is not None and stdout_closed:
            break

        effective_deadline = deadline
        if cancel_deadline is not None:
            effective_deadline = min(effective_deadline, cancel_deadline)

        remaining_seconds = effective_deadline - time.monotonic()
        if remaining_seconds <= 0:
            return _finish_timed_out_process(
                process=process,
                stderr_thread=stderr_thread,
                stderr_chunks=stderr_chunks,
                events=events,
                task_id=_read_task_id(spec.task_file),
                terminate_grace_seconds=lifecycle_config.terminate_grace_seconds,
                stderr_log_path=stderr_log_path,
            )

        try:
            line = stdout_queue.get(timeout=min(remaining_seconds, 0.05))
        except queue.Empty:
            continue

        if line is None:
            stdout_closed = True
            continue

        try:
            event = parse_worker_event_json_line(line)
            _validate_lifecycle_event_order(event, events, terminal_seen)
        except WorkerProtocolError as exc:
            _close_stdin(process.stdin)
            process.terminate()
            try:
                process.wait(timeout=lifecycle_config.terminate_grace_seconds)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            stdout_thread.join(timeout=1.0)
            stderr_thread.join(timeout=1.0)
            stderr = "".join(stderr_chunks)
            _write_stderr_log(stderr, stderr_log_path)
            raise WorkerProcessProtocolError(
                f"Worker protocol error: {exc}",
                stderr=stderr,
                returncode=process.returncode or 0,
            ) from exc

        events.append(event)
        terminal_seen = isinstance(event, (CompletedEvent, FailedEvent))
        if terminal_seen:
            cancel_deadline = None
        deadline = time.monotonic() + lifecycle_config.heartbeat_timeout_seconds

    stdout_thread.join(timeout=1.0)
    stderr_thread.join(timeout=1.0)
    _close_stdin(process.stdin)
    stderr = "".join(stderr_chunks)
    actual_stderr_log_path = _write_stderr_log(stderr, stderr_log_path)

    if cancel_sent and not terminal_seen:
        events.append(
            _make_cancelled_event(
                task_id=_read_task_id(spec.task_file),
                seq=len(events),
                message="Worker exited after cancel request without a terminal event",
            )
        )
        terminal_seen = True

    if not events:
        raise WorkerProcessProtocolError(
            "Worker protocol error: Worker event stream is empty",
            stderr=stderr,
            returncode=process.returncode or 0,
        )
    if not terminal_seen:
        raise WorkerProcessProtocolError(
            "Worker protocol error: Worker event stream must end with a terminal event",
            stderr=stderr,
            returncode=process.returncode or 0,
        )

    return WorkerLifecycleResult(
        events=events,
        stderr=stderr,
        returncode=process.returncode or 0,
        stderr_log_path=actual_stderr_log_path,
        cancelled=cancel_sent or _events_include_cancelled(events),
    )


def _read_stdout_lines(stream: TextIO | None, output_queue: queue.Queue[str | None]) -> None:
    if stream is None:
        output_queue.put(None)
        return
    try:
        for line in stream:
            output_queue.put(line)
    finally:
        stream.close()
        output_queue.put(None)


def _read_stderr_text(stream: TextIO | None, chunks: list[str]) -> None:
    if stream is None:
        return
    try:
        chunks.append(stream.read())
    finally:
        stream.close()


def _validate_lifecycle_event_order(
    event: WorkerEventPayload,
    events: list[WorkerEventPayload],
    terminal_seen: bool,
) -> None:
    expected_seq = len(events)
    if terminal_seen:
        raise WorkerProtocolError("Worker event stream contains events after terminal event")
    if expected_seq == 0 and not isinstance(event, StartedEvent):
        raise WorkerProtocolError("Worker event stream must start with a started event")
    if event.seq != expected_seq:
        raise WorkerProtocolError(
            f"Worker event seq must be contiguous: expected {expected_seq}, got {event.seq}"
        )


def _finish_timed_out_process(
    *,
    process: subprocess.Popen[str],
    stderr_thread: threading.Thread,
    stderr_chunks: list[str],
    events: list[WorkerEventPayload],
    task_id: str,
    terminate_grace_seconds: float,
    stderr_log_path: Path | None,
) -> WorkerLifecycleResult:
    _close_stdin(process.stdin)
    process.terminate()
    killed = False
    try:
        process.wait(timeout=terminate_grace_seconds)
    except subprocess.TimeoutExpired:
        process.kill()
        killed = True
        process.wait()
    stderr_thread.join(timeout=1.0)

    timeout_event = FailedEvent(
        task_id=task_id,
        timestamp=utc_now_iso(),
        seq=len(events),
        error_code="TIMEOUT",
        message="Worker timed out waiting for stdout heartbeat or terminal event",
        recoverable=True,
        partial_artifacts=[],
    )
    stderr = "".join(stderr_chunks)
    return WorkerLifecycleResult(
        events=[*events, timeout_event],
        stderr=stderr,
        returncode=process.returncode or 0,
        stderr_log_path=_write_stderr_log(stderr, stderr_log_path),
        timed_out=True,
        killed=killed,
    )


def _finish_cancelled_process(
    *,
    process: subprocess.Popen[str],
    stderr_thread: threading.Thread,
    stderr_chunks: list[str],
    events: list[WorkerEventPayload],
    task_id: str,
    terminate_grace_seconds: float,
    stderr_log_path: Path | None,
) -> WorkerLifecycleResult:
    _close_stdin(process.stdin)
    process.terminate()
    killed = False
    try:
        process.wait(timeout=terminate_grace_seconds)
    except subprocess.TimeoutExpired:
        process.kill()
        killed = True
        process.wait()
    stderr_thread.join(timeout=1.0)

    cancelled_event = _make_cancelled_event(
        task_id=task_id,
        seq=len(events),
        message="Worker did not exit within cancel grace period",
    )
    stderr = "".join(stderr_chunks)
    return WorkerLifecycleResult(
        events=[*events, cancelled_event],
        stderr=stderr,
        returncode=process.returncode or 0,
        stderr_log_path=_write_stderr_log(stderr, stderr_log_path),
        cancelled=True,
        killed=killed,
    )


def _send_cancel_command(stream: TextIO | None) -> None:
    if stream is None or stream.closed:
        return
    try:
        stream.write(json.dumps({"type": "cancel"}, separators=(",", ":")) + "\n")
        stream.flush()
    except OSError:
        return


def _close_stdin(stream: TextIO | None) -> None:
    if stream is None or stream.closed:
        return
    try:
        stream.close()
    except OSError:
        return


def _make_cancelled_event(*, task_id: str, seq: int, message: str) -> FailedEvent:
    return FailedEvent(
        task_id=task_id,
        timestamp=utc_now_iso(),
        seq=seq,
        error_code="CANCELLED",
        message=message,
        recoverable=False,
        partial_artifacts=[],
    )


def _events_include_cancelled(events: list[WorkerEventPayload]) -> bool:
    return any(isinstance(event, FailedEvent) and event.error_code == "CANCELLED" for event in events)


def _write_stderr_log(stderr: str, stderr_log_path: Path | None) -> Path | None:
    if stderr_log_path is None:
        return None
    stderr_log_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_log_path.write_text(stderr, encoding="utf-8")
    return stderr_log_path


def _read_task_id(task_file: Path) -> str:
    try:
        payload = json.loads(task_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "unknown"
    task_id = payload.get("task_id")
    if isinstance(task_id, str):
        return task_id
    return "unknown"
