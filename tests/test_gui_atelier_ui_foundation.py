import builtins
import importlib
import sys
import unittest
from dataclasses import FrozenInstanceError
from unittest.mock import patch


class AtelierUIFoundationTests(unittest.TestCase):
    def test_theme_tokens_expose_design_palette_roles(self) -> None:
        theme_tokens = importlib.import_module("atelier.gui.ui.theme_tokens")

        tokens = theme_tokens.ATELIER_THEME_TOKENS

        self.assertEqual(tokens.colors.canvas_background, "#0A1422")
        self.assertEqual(tokens.colors.card_background, "#172332")
        self.assertEqual(tokens.colors.card_hover, "#1C2B3D")
        self.assertEqual(tokens.colors.border_strong, "#2A3A50")
        self.assertEqual(tokens.colors.text_primary, "#F3F7FB")
        self.assertEqual(tokens.colors.danger, "#F87171")
        self.assertEqual(theme_tokens.color("card.background"), "#172332")
        self.assertEqual(theme_tokens.color("workflow.selection"), "#3B82F6")
        with self.assertRaises(KeyError):
            theme_tokens.color("missing.role")

    def test_theme_tokens_are_immutable_and_pyside_independent(self) -> None:
        self._clear_atelier_ui_modules()
        real_import = builtins.__import__

        def guarded_import(name, *args, **kwargs):
            if name.startswith("PySide6"):
                raise AssertionError("atelier.gui.ui theme tokens must not import PySide6")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=guarded_import):
            theme_tokens = importlib.import_module("atelier.gui.ui.theme_tokens")

        with self.assertRaises(FrozenInstanceError):
            theme_tokens.ATELIER_THEME_TOKENS.colors.card_background = "#FFFFFF"

    def test_typography_shape_and_canvas_tokens_have_desktop_workbench_density(self) -> None:
        theme_tokens = importlib.import_module("atelier.gui.ui.theme_tokens")
        tokens = theme_tokens.ATELIER_THEME_TOKENS

        self.assertEqual(tokens.fonts.ui[0], "Segoe UI")
        self.assertIn("Microsoft YaHei UI", tokens.fonts.ui)
        self.assertEqual(tokens.typography.card_title.size_px, 14)
        self.assertEqual(tokens.typography.card_title.weight, 650)
        self.assertEqual(tokens.typography.metadata.size_px, 11)
        self.assertLessEqual(tokens.radius.card_px, 8)
        self.assertEqual(tokens.workflow_canvas.node_card_width_px, 160)
        self.assertEqual(tokens.workflow_canvas.node_card_height_px, 84)
        self.assertEqual(tokens.workflow_canvas.node_gap_x_px, 220)

    def test_self_painted_widget_intake_requires_reference_test_and_user_review(self) -> None:
        widget_intake = importlib.import_module("atelier.gui.ui.widget_intake")

        step_ids = widget_intake.required_intake_step_ids()

        self.assertEqual(
            step_ids,
            (
                "purpose",
                "reference_review",
                "minimal_test",
                "atelier_specific_implementation",
                "user_review",
            ),
        )
        self.assertTrue(
            widget_intake.requires_user_review_before_shared_adoption("WorkflowNodeItem")
        )
        self.assertFalse(widget_intake.is_approved_for_shared_adoption("WorkflowNodeItem"))

    def _clear_atelier_ui_modules(self) -> None:
        for module_name in list(sys.modules):
            if module_name.startswith("atelier.gui.ui"):
                sys.modules.pop(module_name)


if __name__ == "__main__":
    unittest.main()
