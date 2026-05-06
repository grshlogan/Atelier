from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from pathlib import Path

from atelier.domain.resources import HardwareSnapshot
from atelier.runtime.manager import RuntimeManager
from atelier.runtime.store import RuntimeStore
from atelier.scheduler.simple import SimpleScheduler
from atelier.scheduler.workflow_runner import WorkflowRunResult, run_sequential_workflow


class WorkflowRunAppService:
    def __init__(
        self,
        *,
        connection: sqlite3.Connection,
        runtime_store: RuntimeStore,
        hardware_snapshot: HardwareSnapshot,
        work_root: Path,
        command_args: Sequence[str],
    ) -> None:
        self.connection = connection
        self.runtime_store = runtime_store
        self.hardware_snapshot = hardware_snapshot
        self.work_root = Path(work_root)
        self.command_args = tuple(command_args)

    def run_plan(self, plan_id: str, *, max_steps: int = 100) -> WorkflowRunResult:
        scheduler = SimpleScheduler(self.hardware_snapshot)
        runtime_manager = RuntimeManager.from_store(self.runtime_store)
        return run_sequential_workflow(
            self.connection,
            plan_id=plan_id,
            scheduler=scheduler,
            runtime_manager=runtime_manager,
            work_root=self.work_root,
            command_args=self.command_args,
            max_steps=max_steps,
        )
