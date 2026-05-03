from __future__ import annotations

import json
from collections.abc import Iterable
from typing import TypeAlias

from pydantic import ValidationError

from atelier.domain.worker_event import (
    ArtifactEvent,
    CompletedEvent,
    FailedEvent,
    HeartbeatEvent,
    LogEvent,
    ProgressEvent,
    StartedEvent,
)


WorkerEventPayload: TypeAlias = (
    StartedEvent
    | ProgressEvent
    | LogEvent
    | ArtifactEvent
    | CompletedEvent
    | FailedEvent
    | HeartbeatEvent
)


class WorkerProtocolError(ValueError):
    """Raised when a Worker stdout line is not a valid Atelier worker event."""


_EVENT_MODELS: dict[str, type[WorkerEventPayload]] = {
    "started": StartedEvent,
    "progress": ProgressEvent,
    "log": LogEvent,
    "heartbeat": HeartbeatEvent,
    "artifact": ArtifactEvent,
    "completed": CompletedEvent,
    "failed": FailedEvent,
}


def format_worker_event_json_line(event: WorkerEventPayload) -> str:
    payload = event.model_dump(mode="json", exclude_none=True)
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"


def parse_worker_event_json_line(line: str) -> WorkerEventPayload:
    try:
        payload = json.loads(line)
    except json.JSONDecodeError as exc:
        raise WorkerProtocolError(f"Invalid worker event JSON: {exc.msg}") from exc

    if not isinstance(payload, dict):
        raise WorkerProtocolError("Worker event JSON must be an object")

    event_type = payload.get("type")
    if not isinstance(event_type, str):
        raise WorkerProtocolError("Worker event JSON must include a string type")

    event_model = _EVENT_MODELS.get(event_type)
    if event_model is None:
        raise WorkerProtocolError(f"Unknown worker event type: {event_type}")

    try:
        return event_model.model_validate(payload)
    except ValidationError as exc:
        raise WorkerProtocolError(f"Invalid {event_type} worker event payload") from exc


def parse_worker_event_stream(lines: Iterable[str]) -> list[WorkerEventPayload]:
    events: list[WorkerEventPayload] = []
    terminal_seen = False

    for line in lines:
        event = parse_worker_event_json_line(line)
        expected_seq = len(events)

        if terminal_seen:
            raise WorkerProtocolError("Worker event stream contains events after terminal event")
        if expected_seq == 0 and not isinstance(event, StartedEvent):
            raise WorkerProtocolError("Worker event stream must start with a started event")
        if event.seq != expected_seq:
            raise WorkerProtocolError(f"Worker event seq must be contiguous: expected {expected_seq}, got {event.seq}")

        events.append(event)
        terminal_seen = isinstance(event, (CompletedEvent, FailedEvent))

    if not events:
        raise WorkerProtocolError("Worker event stream is empty")
    if not terminal_seen:
        raise WorkerProtocolError("Worker event stream must end with a terminal event")

    return events
