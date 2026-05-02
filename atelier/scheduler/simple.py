from __future__ import annotations

from dataclasses import dataclass
import sqlite3

from atelier.domain.execution_plan import ExecutionTask
from atelier.domain.resources import HardwareSnapshot, ResourceBinding
from atelier.storage.repositories import fetch_next_runnable_task, mark_task_running


@dataclass(frozen=True)
class ClaimedTask:
    task: ExecutionTask
    resource_binding: ResourceBinding


class SimpleScheduler:
    def __init__(self, hardware_snapshot: HardwareSnapshot) -> None:
        self._hardware_snapshot = hardware_snapshot

    def claim_next_task(self, connection: sqlite3.Connection, plan_id: str) -> ClaimedTask | None:
        task = fetch_next_runnable_task(connection, plan_id)
        if task is None:
            return None

        resource_binding = self._bind_resources(task)
        mark_task_running(connection, task.task_id, resource_binding)
        return ClaimedTask(task=task, resource_binding=resource_binding)

    def _bind_resources(self, task: ExecutionTask) -> ResourceBinding:
        request = task.resource_request
        if request.device_type == "gpu":
            gpu = self._first_gpu_id()
            if gpu is None:
                raise RuntimeError(f"no GPU available for task: {task.task_id}")
            return ResourceBinding(device_id=gpu, binding_reason="simple scheduler selected first GPU")
        return ResourceBinding(
            device_id="cpu",
            binding_reason=(
                f"simple scheduler selected CPU from {self._hardware_snapshot.cpu_cores} cores"
            ),
        )

    def _first_gpu_id(self) -> str | None:
        if not self._hardware_snapshot.gpus:
            return None
        gpu = self._hardware_snapshot.gpus[0]
        device_id = gpu.get("device_id") or gpu.get("id") or gpu.get("name")
        if device_id is None:
            return None
        return str(device_id)
