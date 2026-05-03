import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from atelier.app.paths import AppPaths
from atelier.gui.entry import check_gui_dependency
from atelier.gui.state_reader import WorkbenchSnapshot, WorkbenchTaskItem

GUI_AVAILABLE = check_gui_dependency().available

if GUI_AVAILABLE:
    from PySide6.QtWidgets import QApplication, QDockWidget, QLabel
    from atelier.gui.main_window import MainWindow
else:
    QApplication = None
    QLabel = None
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


if __name__ == "__main__":
    unittest.main()
