from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from atelier.domain.execution_plan import ExecutionTask
from atelier.domain.resources import ResourceBinding, RuntimeBinding
from atelier.domain.worker_event import ArtifactRef


class AdapterValidationError(BaseModel):
    code: str
    message: str
    recoverable: bool = False


class AdapterExecutionError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        error_code: str,
        recoverable: bool,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.recoverable = recoverable


class AdapterContext(BaseModel):
    task: ExecutionTask
    runtime_binding: RuntimeBinding
    resource_binding: ResourceBinding | None = None
    work_dir: Path


class AdapterResult(BaseModel):
    artifacts: list[ArtifactRef] = Field(default_factory=list)
    duration_seconds: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkerAdapter(ABC):
    node_type: str
    adapter_version: str

    def validate(self, context: AdapterContext) -> list[AdapterValidationError]:
        return []

    def prepare(self, context: AdapterContext) -> None:
        context.work_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def run(self, context: AdapterContext) -> AdapterResult:
        raise NotImplementedError

    def cancel(self, context: AdapterContext) -> None:
        return None
