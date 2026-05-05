import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from atelier.app.paths import AppPaths
from atelier.app.services import create_runtime_setup_service
from atelier.gui.entry import check_gui_dependency
from atelier.runtime.setup import RuntimeComponentSnapshot, RuntimeSetupSnapshot

GUI_AVAILABLE = check_gui_dependency().available

if GUI_AVAILABLE:
    from PySide6.QtWidgets import QApplication, QDockWidget, QLabel, QPushButton
    from atelier.gui.main_window import MainWindow
else:
    QApplication = None
    QLabel = None
    QDockWidget = None
    QPushButton = None
    MainWindow = None


@unittest.skipUnless(GUI_AVAILABLE, "PySide6 is not installed")
class GuiRuntimeSetupTests(unittest.TestCase):
    def test_main_window_renders_runtime_setup_snapshot(self) -> None:
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        runtime_snapshot = RuntimeSetupSnapshot(
            runtimes=[
                RuntimeComponentSnapshot(
                    runtime_id="ffprobe-local",
                    component="ffprobe",
                    display_name="FFprobe Local",
                    version="7.1.0",
                    kind="tool",
                    profile_kind="local",
                    status="ready",
                    capabilities=["metadata"],
                    checked_paths={"ffprobe": "C:/Tools/ffprobe.exe"},
                )
            ]
        )

        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))
            window = MainWindow(app_paths=paths, runtime_setup_snapshot=runtime_snapshot)
            try:
                dock = window.findChild(QDockWidget, "runtime-setup-panel")
                self.assertIsNotNone(dock)
                self.assertEqual(dock.windowTitle(), "Runtime Setup")

                summary = dock.widget().findChild(QLabel, "runtime-setup-summary")
                components = dock.widget().findChild(QLabel, "runtime-setup-components")

                self.assertIn("1 / 1 runtimes ready", summary.text())
                self.assertIn("0 models", summary.text())
                self.assertIn("FFprobe Local", components.text())
                self.assertIn("Ready", components.text())
                self.assertIn("metadata", components.text())
            finally:
                window.close()

    def test_runtime_setup_panel_registers_ffmpeg_path_and_refreshes_snapshot(self) -> None:
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))
            ffmpeg = paths.data_root / "runtimes" / "components" / "ffmpeg.exe"
            ffmpeg.parent.mkdir(parents=True)
            ffmpeg.write_bytes(b"fake ffmpeg")
            service = create_runtime_setup_service(paths)

            window = MainWindow(
                app_paths=paths,
                runtime_setup_snapshot=service.refresh_snapshot(),
                runtime_setup_service=service,
            )
            try:
                dock = window.findChild(QDockWidget, "runtime-setup-panel")
                panel = dock.widget()
                register_button = panel.findChild(QPushButton, "runtime-setup-register-ffmpeg")

                self.assertTrue(register_button.isEnabled())

                panel.register_ffmpeg_path(ffmpeg)

                components = panel.findChild(QLabel, "runtime-setup-components")
                self.assertIn("FFmpeg Local", components.text())
                self.assertIn("Ready", components.text())
                self.assertIn("mux", components.text())
                self.assertFalse(register_button.isEnabled())
            finally:
                window.close()

    def test_runtime_setup_panel_displays_registration_error_without_crashing(self) -> None:
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        with TemporaryDirectory() as temp_dir:
            paths = AppPaths.for_development(Path(temp_dir))
            service = create_runtime_setup_service(paths)
            window = MainWindow(
                app_paths=paths,
                runtime_setup_snapshot=service.refresh_snapshot(),
                runtime_setup_service=service,
            )
            try:
                dock = window.findChild(QDockWidget, "runtime-setup-panel")
                panel = dock.widget()

                panel.register_ffprobe_path(paths.data_root / "missing-ffprobe.exe")

                error = panel.findChild(QLabel, "runtime-setup-error")
                components = panel.findChild(QLabel, "runtime-setup-components")
                self.assertIn("missing executable path", error.text())
                self.assertIn("No runtime components registered", components.text())
            finally:
                window.close()


if __name__ == "__main__":
    unittest.main()
