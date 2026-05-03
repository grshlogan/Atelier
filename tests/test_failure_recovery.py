from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest

from atelier.app.paths import AppPaths
from atelier.app.services import open_app_database
from atelier.domain.resources import HardwareSnapshot, ResourceRequest, RuntimeRequest
from atelier.domain.worker_event import ArtifactRef, FailedEvent
from atelier.planning.simple import build_linear_execution_plan
from atelier.scheduler.simple import SimpleScheduler
from atelier.storage.repositories import (
    fetch_failure_facts,
    persist_planned_execution,
    record_worker_events,
    suggest_recovery_options,
)
from atelier.workflow.graph import WorkflowGraph, WorkflowNode


class FailureRecoveryTests(unittest.TestCase):
    def test_recoverable_failed_task_exposes_facts_and_retry_options(self) -> None:
        with TemporaryDirectory() as temp_dir:
            connection, task_id = self._claim_single_task(temp_dir)
            try:
                record_worker_events(
                    connection,
                    [
                        FailedEvent(
                            task_id=task_id,
                            timestamp="2026-05-03T00:00:00Z",
                            seq=0,
                            error_code="CUDA_OOM",
                            message="GPU memory exhausted",
                            recoverable=True,
                            partial_artifacts=[
                                ArtifactRef(
                                    artifact_id="artifact-partial-srt",
                                    artifact_type="subtitle.partial",
                                    path="artifacts/node-failure/partial.srt",
                                )
                            ],
                        )
                    ],
                )

                facts = fetch_failure_facts(connection, task_id)
                options = suggest_recovery_options(connection, task_id)

                self.assertEqual(facts.error_code, "CUDA_OOM")
                self.assertEqual(facts.error_message, "GPU memory exhausted")
                self.assertTrue(facts.recoverable)
                self.assertEqual(facts.partial_artifact_paths, ["artifacts/node-failure/partial.srt"])
                self.assertIn("retry", [option.action for option in options])
                self.assertIn("use_partial_artifacts", [option.action for option in options])

            finally:
                connection.close()

    def test_non_recoverable_failed_task_exposes_read_only_options_without_retry(self) -> None:
        with TemporaryDirectory() as temp_dir:
            connection, task_id = self._claim_single_task(temp_dir)
            try:
                record_worker_events(
                    connection,
                    [
                        FailedEvent(
                            task_id=task_id,
                            timestamp="2026-05-03T00:00:00Z",
                            seq=0,
                            error_code="UNSUPPORTED_CODEC",
                            message="Input codec is unsupported by this worker",
                            recoverable=False,
                            partial_artifacts=[
                                ArtifactRef(
                                    artifact_id="artifact-diagnostics",
                                    artifact_type="diagnostic.log",
                                    path="artifacts/node-failure/diagnostics.txt",
                                )
                            ],
                        )
                    ],
                )

                facts = fetch_failure_facts(connection, task_id)
                options = suggest_recovery_options(connection, task_id)
                actions = [option.action for option in options]

                self.assertFalse(facts.recoverable)
                self.assertEqual(
                    facts.partial_artifact_paths,
                    ["artifacts/node-failure/diagnostics.txt"],
                )
                self.assertNotIn("retry", actions)
                self.assertIn("inspect_failure", actions)
                self.assertIn("export_partial_artifacts", actions)

            finally:
                connection.close()

    def _claim_single_task(self, temp_dir: str) -> tuple[sqlite3.Connection, str]:
        paths = AppPaths.for_development(Path(temp_dir))
        connection = open_app_database(paths)
        graph = WorkflowGraph(
            graph_id="graph-failure",
            name="Failure Graph",
            nodes=[
                WorkflowNode(
                    node_id="node-failure",
                    node_type="simulate.failure",
                    resource_request=ResourceRequest(device_type="cpu"),
                    runtime_request=RuntimeRequest(components=["simulated"]),
                )
            ],
        )
        plan = build_linear_execution_plan(graph, plan_id="plan-failure")
        persist_planned_execution(
            connection,
            project_id="project-failure",
            project_name="Failure Project",
            project_root=str(paths.data_root),
            job_id="job-failure",
            job_name="Failure Job",
            graph=graph,
            plan=plan,
        )
        scheduler = SimpleScheduler(
            HardwareSnapshot(cpu_cores=8, ram_total_mb=32768, ram_free_mb=24576)
        )
        claim = scheduler.claim_next_task(connection, plan.plan_id)
        self.assertIsNotNone(claim)
        return connection, claim.task.task_id


if __name__ == "__main__":
    unittest.main()
