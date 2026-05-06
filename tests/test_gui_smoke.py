import os
import time
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from atelier.app.paths import AppPaths
from atelier.gui.entry import check_gui_dependency
from atelier.gui.layout_store import WorkspaceLayoutStore
from atelier.gui.state_reader import WorkbenchSnapshot, WorkbenchTaskItem

GUI_AVAILABLE = check_gui_dependency().available

if GUI_AVAILABLE:
    from PySide6.QtWidgets import QApplication, QDockWidget, QLabel, QPushButton
    from atelier.gui.main_window import MainWindow
else:
    QApplication = None
    QLabel = None
    QPushButton = None
    QDockWidget = None
    MainWindow = None


@unittest.skipUnless(GUI_AVAILABLE, "PySide6 is not installed")
class GuiSmokeTests(unittest.TestCase):
    def test_main_window_constructs_with_read_only_workspace_docks(self) -> None:
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))

            window = MainWindow(app_paths=paths)
            try:
                docks = {dock.objectName(): dock for dock in window.findChildren(QDockWidget)}

                self.assertEqual(window.windowTitle(), "Atelier")
                self.assertEqual(window.objectName(), "atelier-main-window")
                self.assertEqual(window.app_paths, paths)
                self.assertEqual(
                    set(docks),
                    {
                        "workflow-panel",
                        "execution-panel",
                        "queue-panel",
                        "resources-runtime-panel",
                        "runtime-setup-panel",
                    },
                )
                self.assertTrue(
                    all(
                        dock.features() & QDockWidget.DockWidgetFeature.DockWidgetMovable
                        for dock in docks.values()
                    )
                )
                self.assertTrue(
                    all(
                        dock.features() & QDockWidget.DockWidgetFeature.DockWidgetFloatable
                        for dock in docks.values()
                    )
                )
            finally:
                window.close()

    def test_main_window_queue_panel_renders_read_only_task_snapshot(self) -> None:
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        snapshot = WorkbenchSnapshot(
            tasks=[
                WorkbenchTaskItem(
                    task_id="task-node-gui-state",
                    node_type="simulate.echo",
                    status="completed",
                    resource_device_id="cpu",
                    event_count=4,
                    artifact_paths=["artifacts/node-gui-state/output.json"],
                )
            ]
        )
        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))

            window = MainWindow(app_paths=paths, snapshot=snapshot)
            try:
                body = window.findChild(QDockWidget, "queue-panel").widget().findChild(
                    QLabel,
                    "queue-panel-body",
                )

                self.assertIn("task-node-gui-state", body.text())
                self.assertIn("completed", body.text())
                self.assertIn("cpu", body.text())
                self.assertIn("artifacts/node-gui-state/output.json", body.text())
            finally:
                window.close()

    def test_main_window_queue_panel_renders_outputs_and_failure_facts(self) -> None:
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        snapshot = WorkbenchSnapshot(
            tasks=[
                WorkbenchTaskItem(
                    task_id="task-export",
                    node_type="output.export",
                    status="completed",
                    resource_device_id="cpu",
                    event_count=3,
                    artifact_paths=["worker/task-export/final.wav"],
                    final_output_paths=["exports/final.wav"],
                ),
                WorkbenchTaskItem(
                    task_id="task-audio",
                    node_type="media.audio_extract",
                    status="failed",
                    resource_device_id="cpu",
                    event_count=2,
                    artifact_paths=[],
                    failure_error_code="DEPENDENCY",
                    failure_message="no audio stream",
                ),
            ]
        )
        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))

            window = MainWindow(app_paths=paths, snapshot=snapshot)
            try:
                body = window.findChild(QDockWidget, "queue-panel").widget().findChild(
                    QLabel,
                    "queue-panel-body",
                )

                self.assertIn("final output: exports/final.wav", body.text())
                self.assertIn("failure: DEPENDENCY | no audio stream", body.text())
            finally:
                window.close()

    def test_main_window_run_button_submits_workflow_run_intent(self) -> None:
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        run_service = _FakeWorkflowRunIntentService()
        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))

            window = MainWindow(
                app_paths=paths,
                active_plan_id="plan-gui-intent",
                workflow_run_intent_service=run_service,
            )
            try:
                button = window.findChild(QPushButton, "workflow-run-intent-button")
                status = window.findChild(QLabel, "workflow-run-intent-status")

                self.assertIsNotNone(button)
                self.assertTrue(button.isEnabled())

                button.click()

                self.assertEqual(run_service.requested_plan_ids, ["plan-gui-intent"])
                self.assertIn("Run requested: plan-gui-intent", status.text())
            finally:
                window.close()

    def test_main_window_run_button_does_not_block_on_run_intent_completion(self) -> None:
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        run_service = _SlowWorkflowRunIntentService()
        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))

            window = MainWindow(
                app_paths=paths,
                active_plan_id="plan-gui-nonblocking",
                workflow_run_intent_service=run_service,
            )
            try:
                button = window.findChild(QPushButton, "workflow-run-intent-button")
                status = window.findChild(QLabel, "workflow-run-intent-status")

                started_at = time.perf_counter()
                button.click()
                elapsed = time.perf_counter() - started_at

                self.assertLess(elapsed, 0.2)
                self.assertEqual(run_service.requested_plan_ids, ["plan-gui-nonblocking"])
                self.assertIn("Run requested: plan-gui-nonblocking", status.text())
            finally:
                window.close()

    def test_main_window_saves_and_restores_workspace_layout(self) -> None:
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))
            store = WorkspaceLayoutStore(paths)

            window = MainWindow(app_paths=paths)
            try:
                window.resize(1280, 720)
                window.save_workspace_layout(store, name="default")

                record = store.load_layout("default")
                self.assertIsNotNone(record)
                self.assertGreater(len(record.geometry), 0)
                self.assertGreater(len(record.state), 0)
            finally:
                window.close()

            restored_window = MainWindow(app_paths=paths)
            try:
                self.assertTrue(restored_window.restore_workspace_layout(store, name="default"))
            finally:
                restored_window.close()


class _FakeWorkflowRunIntentService:
    def __init__(self) -> None:
        self.requested_plan_ids: list[str] = []

    def request_run(self, plan_id: str) -> None:
        self.requested_plan_ids.append(plan_id)


class _SlowWorkflowRunIntentService(_FakeWorkflowRunIntentService):
    def request_run(self, plan_id: str) -> None:
        super().request_run(plan_id)
        time.sleep(0.5)


if __name__ == "__main__":
    unittest.main()
