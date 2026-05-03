import unittest
from unittest.mock import patch

from atelier.gui.entry import GUI_EXTRA_INSTALL_COMMAND, check_gui_dependency, ensure_gui_dependency


class GuiOptionalDependencyTests(unittest.TestCase):
    def test_gui_module_import_reports_current_pyside6_status(self) -> None:
        status = check_gui_dependency()

        self.assertEqual(status.package_name, "PySide6")
        self.assertEqual(status.install_command, GUI_EXTRA_INSTALL_COMMAND)
        self.assertIsInstance(status.available, bool)

    def test_gui_dependency_error_points_to_gui_extra_install_command(self) -> None:
        with patch("atelier.gui.entry.importlib.util.find_spec", return_value=None):
            with self.assertRaisesRegex(RuntimeError, r"\.\[gui\]"):
                ensure_gui_dependency()


if __name__ == "__main__":
    unittest.main()
