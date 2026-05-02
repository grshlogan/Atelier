from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from atelier.domain.resources import ResourceBinding, ResourceRequest, RuntimeBinding, RuntimeRequest


TaskStatus = Literal[
    "pending",
    "queued",
    "running",
    "completed",
    "failed",
    "retry_pending",
    "skipped",
    "cancelled",
]


class ArtifactSlot(BaseModel):
    slot_id: str
    artifact_type: str
    expected_path: str | None = None


class FailurePolicy(BaseModel):
    on_failure: Literal["stop", "skip", "retry"] = "stop"
    max_retries: int = 0
    fallback_node_type: str | None = None


class ExecutionTask(BaseModel):
    task_id: str
    source_node_id: str
    node_type: str
    phase_id: str = "phase-1"
    lane_id: str = "lane-default"
    params: dict[str, Any] = Field(default_factory=dict)
    input_artifacts: list[str] = Field(default_factory=list)
    output_artifact_slots: list[ArtifactSlot] = Field(default_factory=list)
    resource_request: ResourceRequest
    runtime_request: RuntimeRequest
    resource_binding: ResourceBinding | None = None
    runtime_binding: RuntimeBinding | None = None
    status: TaskStatus = "pending"
    failure_policy: FailurePolicy = Field(default_factory=FailurePolicy)
    depends_on_tasks: list[str] = Field(default_factory=list)
    cache_key: str | None = None
    retry_count: int = 0
    started_at: str | None = None
    completed_at: str | None = None
    error_message: str | None = None


class ExecutionPlan(BaseModel):
    plan_id: str
    workflow_graph_id: str
    status: Literal["draft", "ready", "running", "completed", "failed"] = "ready"
    tasks: list[ExecutionTask] = Field(default_factory=list)
