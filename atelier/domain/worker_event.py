from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class WorkerEvent(BaseModel):
    type: str
    task_id: str
    timestamp: str
    seq: int


class StartedEvent(WorkerEvent):
    type: Literal["started"] = "started"
    worker_pid: int = 0
    worker_version: str = "simulated"
    node_type: str = ""


class ProgressEvent(WorkerEvent):
    type: Literal["progress"] = "progress"
    current: int
    total: int
    unit: str
    percent: float
    stage: str = ""
    eta_seconds: float | None = None


class LogEvent(WorkerEvent):
    type: Literal["log"] = "log"
    level: Literal["debug", "info", "warning", "error"]
    message: str


class HeartbeatEvent(WorkerEvent):
    type: Literal["heartbeat"] = "heartbeat"
    uptime_seconds: float
    memory_mb: float
    gpu_memory_mb: float | None = None


class ArtifactRef(BaseModel):
    artifact_id: str
    artifact_type: str
    path: str


class ArtifactEvent(WorkerEvent):
    type: Literal["artifact"] = "artifact"
    artifact_id: str
    artifact_type: str
    path: str
    hash: str | None = None
    size_bytes: int | None = None
    metadata: dict = Field(default_factory=dict)


class CompletedEvent(WorkerEvent):
    type: Literal["completed"] = "completed"
    artifacts: list[ArtifactRef] = Field(default_factory=list)
    duration_seconds: float = 0.0


class FailedEvent(WorkerEvent):
    type: Literal["failed"] = "failed"
    error_code: str
    message: str
    recoverable: bool
    partial_artifacts: list[ArtifactRef] = Field(default_factory=list)


TerminalWorkerEvent = CompletedEvent | FailedEvent


def task_status_from_terminal_event(event: TerminalWorkerEvent) -> str:
    if isinstance(event, CompletedEvent):
        return "completed"
    if event.error_code == "CANCELLED":
        return "cancelled"
    return "failed"
