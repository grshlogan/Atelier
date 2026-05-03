import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from atelier.gui.entry import check_gui_dependency

GUI_AVAILABLE = check_gui_dependency().available

if GUI_AVAILABLE:
    from PySide6.QtWidgets import QApplication
    from atelier.gui.app import build_launch_context, parse_launch_args
else:
    QApplication = None
    build_launch_context = None
    parse_launch_args = None


@unittest.skipUnless(GUI_AVAILABLE, "PySide6 is not installed")
class GuiAppEntryTests(unittest.TestCase):
    def test_parse_launch_args_supports_workspace_root_and_no_restore(self) -> None:
        with TemporaryDirectory() as temp_dir:
            args = parse_launch_args(["--workspace-root", temp_dir, "--no-restore-layout"])

            self.assertEqual(args.workspace_root, Path(temp_dir))
            self.assertIsNone(args.data_root)
            self.assertFalse(args.restore_layout)

    def test_build_launch_context_creates_main_window_without_running_event_loop(self) -> None:
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        with TemporaryDirectory() as temp_dir:
            context = build_launch_context(
                parse_launch_args(["--workspace-root", temp_dir, "--no-restore-layout"])
            )
            try:
                self.assertEqual(context.window.windowTitle(), "Atelier")
                self.assertEqual(context.window.app_paths.workspace_root, Path(temp_dir))
                self.assertEqual(len(context.snapshot.tasks), 0)
                self.assertFalse(context.layout_restored)
            finally:
                context.connection.close()
                context.window.close()


if __name__ == "__main__":
    unittest.main()
