from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from typing import Protocol


class WorkflowRunIntentServiceProtocol(Protocol):
    def request_run(self, plan_id: str) -> None:
        pass


class WorkflowRunIntentExecutor:
    def __init__(self, *, max_workers: int = 1) -> None:
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="atelier-gui-run-intent",
        )
        self._futures: list[Future[None]] = []

    def submit(
        self,
        *,
        service: WorkflowRunIntentServiceProtocol,
        plan_id: str,
    ) -> Future[None]:
        future = self._executor.submit(service.request_run, plan_id)
        self._futures.append(future)
        return future

    def shutdown(self, *, wait: bool = False) -> None:
        self._executor.shutdown(wait=wait, cancel_futures=True)
