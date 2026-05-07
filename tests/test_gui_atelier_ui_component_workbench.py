import builtins
import importlib
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from atelier.gui.entry import check_gui_dependency

REPO_ROOT = Path(__file__).resolve().parents[1]
GUI_AVAILABLE = check_gui_dependency().available

if GUI_AVAILABLE:
    from PySide6.QtWidgets import QApplication, QLabel, QListWidget, QMainWindow, QPushButton, QTextEdit, QWidget
else:
    QApplication = None
    QLabel = None
    QListWidget = None
    QMainWindow = None
    QPushButton = None
    QTextEdit = None
    QWidget = None


class AtelierUIComponentWorkbenchStateTests(unittest.TestCase):
    def test_root_powershell_launcher_opens_component_workbench_module(self) -> None:
        launcher_path = REPO_ROOT / "open_atelier_ui_workbench.ps1"

        script = launcher_path.read_text(encoding="utf-8")

        self.assertIn(".venv", script)
        self.assertIn("python.exe", script)
        self.assertIn("atelier.gui.ui.component_workbench", script)
        self.assertIn("@Args", script)
        self.assertIn("Set-Location", script)

    def test_workbench_state_lists_catalog_stories_tokens_and_review_steps(self) -> None:
        state_module = importlib.import_module("atelier.gui.ui.component_workbench_state")

        state = state_module.build_component_workbench_state()

        self.assertEqual(state.window_title, "AtelierUI 控件画板")
        self.assertEqual([entry.entry_id for entry in state.catalog_entries], ["tokens", "workflow-node"])
        self.assertEqual(state.catalog_entries[0].label, "主题 Tokens")
        self.assertIn("card.background", [swatch.role for swatch in state.color_swatches])
        self.assertIn("workflow.selection", [swatch.role for swatch in state.color_swatches])
        self.assertIn("card_title", [sample.sample_id for sample in state.typography_samples])
        self.assertIn("user_review", [step.step_id for step in state.intake_steps])
        workflow_story = state.story_by_id("workflow-node")
        self.assertEqual(workflow_story.surface, "Workflow Canvas")
        self.assertEqual(workflow_story.label, "WorkflowNodeItem 候选")
        self.assertIn("用户审查", workflow_story.summary)
        self.assertFalse(workflow_story.shared_adoption_approved)
        self.assertEqual(
            [control.control_id for control in workflow_story.controls],
            ["selected", "hovered", "density"],
        )
        self.assertEqual([story_state.state_id for story_state in workflow_story.states], ["normal", "hovered", "selected"])
        selected_control = workflow_story.control_by_id("selected")
        self.assertEqual(selected_control.label, "选中态")
        self.assertEqual(selected_control.control_type, "toggle")
        self.assertEqual(selected_control.default_value, False)

    def test_review_snapshot_metadata_is_json_safe_and_omits_absolute_paths(self) -> None:
        state_module = importlib.import_module("atelier.gui.ui.component_workbench_state")
        state = state_module.build_component_workbench_state()

        snapshot = state_module.build_review_snapshot_record(
            state=state,
            story_id="workflow-node",
            reviewer_note="节点卡片阴影偏重，待调。",
            screenshot_filename="workflow-node-20260507T120000.png",
        )

        self.assertEqual(snapshot["story_id"], "workflow-node")
        self.assertEqual(snapshot["story_label"], "WorkflowNodeItem 候选")
        self.assertEqual(snapshot["reviewer_note"], "节点卡片阴影偏重，待调。")
        self.assertEqual(snapshot["screenshot_filename"], "workflow-node-20260507T120000.png")
        self.assertEqual(snapshot["controls"], ["selected", "hovered", "density"])
        self.assertNotIn(str(REPO_ROOT), str(snapshot))

    def test_workbench_state_does_not_import_pyside6(self) -> None:
        self._clear_workbench_modules()
        real_import = builtins.__import__

        def guarded_import(name, *args, **kwargs):
            if name.startswith("PySide6"):
                raise AssertionError("workbench state must not import PySide6")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=guarded_import):
            importlib.import_module("atelier.gui.ui.component_workbench_state")

    def _clear_workbench_modules(self) -> None:
        for module_name in list(sys.modules):
            if module_name.startswith("atelier.gui.ui.component_workbench"):
                sys.modules.pop(module_name)


@unittest.skipUnless(GUI_AVAILABLE, "PySide6 is not installed")
class AtelierUIComponentWorkbenchWindowTests(unittest.TestCase):
    def test_build_workbench_window_renders_dev_only_gallery_without_product_main_window(self) -> None:
        component_workbench = importlib.import_module("atelier.gui.ui.component_workbench")
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        window = component_workbench.build_component_workbench_window()
        try:
            self.assertEqual(window.objectName(), "atelier-ui-component-workbench")
            self.assertEqual(window.windowTitle(), "AtelierUI 控件画板")
            self.assertIsInstance(window, QMainWindow)

            catalog = window.findChild(QListWidget, "component-workbench-catalog")
            token_preview = window.findChild(QWidget, "component-workbench-token-preview")
            checklist = window.findChild(QLabel, "component-workbench-intake-checklist")
            review_status = window.findChild(QLabel, "component-workbench-candidate-review-status")
            screenshot = window.findChild(QWidget, "component-workbench-screenshot-planned")
            save_review = window.findChild(QPushButton, "component-workbench-save-review")
            review_note = window.findChild(QTextEdit, "component-workbench-review-note")
            controls_panel = window.findChild(QWidget, "component-workbench-controls-panel")
            selected_story_title = window.findChild(QLabel, "component-workbench-selected-story-title")
            selected_story_summary = window.findChild(QLabel, "component-workbench-selected-story-summary")
            product_window = window.findChild(QMainWindow, "atelier-main-window")

            self.assertIsNotNone(catalog)
            self.assertEqual(catalog.count(), 2)
            self.assertIn("主题 Tokens", catalog.item(0).text())
            self.assertIsNotNone(token_preview)
            self.assertIn("user_review", checklist.text())
            self.assertIn("用户审查", checklist.text())
            self.assertIn("共享采用：等待用户审查", review_status.text())
            self.assertIsNone(screenshot)
            self.assertEqual(save_review.text(), "保存截图和备注")
            self.assertTrue(save_review.isEnabled())
            self.assertEqual(review_note.placeholderText(), "记录这次控件审查的观察和调整建议")
            self.assertIsNotNone(controls_panel)
            self.assertEqual(selected_story_title.text(), "主题 Tokens")
            self.assertIn("预览颜色 token", selected_story_summary.text())
            self.assertIsNone(product_window)
        finally:
            window.close()

    def test_save_review_snapshot_writes_png_and_json_to_review_directory(self) -> None:
        component_workbench = importlib.import_module("atelier.gui.ui.component_workbench")
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        with tempfile.TemporaryDirectory() as temp_dir:
            window = component_workbench.build_component_workbench_window(review_output_dir=Path(temp_dir))
            try:
                catalog = window.findChild(QListWidget, "component-workbench-catalog")
                review_note = window.findChild(QTextEdit, "component-workbench-review-note")

                catalog.setCurrentRow(1)
                review_note.setPlainText("节点卡片边框需要再轻一点。")
                app.processEvents()

                result = window.save_review_snapshot()

                self.assertEqual(result.story_id, "workflow-node")
                self.assertTrue(result.screenshot_path.exists())
                self.assertTrue(result.metadata_path.exists())
                self.assertEqual(result.screenshot_path.suffix, ".png")
                metadata_text = result.metadata_path.read_text(encoding="utf-8")
                self.assertIn('"story_id": "workflow-node"', metadata_text)
                self.assertIn("节点卡片边框需要再轻一点。", metadata_text)
                self.assertNotIn(str(REPO_ROOT), metadata_text)
            finally:
                window.close()

    def test_catalog_selection_updates_selected_story_preview_and_controls_panel(self) -> None:
        component_workbench = importlib.import_module("atelier.gui.ui.component_workbench")
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        window = component_workbench.build_component_workbench_window()
        try:
            catalog = window.findChild(QListWidget, "component-workbench-catalog")
            selected_story_title = window.findChild(QLabel, "component-workbench-selected-story-title")
            selected_story_summary = window.findChild(QLabel, "component-workbench-selected-story-summary")
            selected_states = window.findChild(QLabel, "component-workbench-selected-story-states")
            controls_panel = window.findChild(QWidget, "component-workbench-controls-panel")
            controls_summary = window.findChild(QLabel, "component-workbench-controls-summary")

            catalog.setCurrentRow(1)
            app.processEvents()

            self.assertEqual(selected_story_title.text(), "WorkflowNodeItem 候选")
            self.assertIn("用户审查前不得共享入库", selected_story_summary.text())
            self.assertIn("normal", selected_states.text())
            self.assertIn("selected", selected_states.text())
            self.assertIsNotNone(controls_panel)
            self.assertIn("selected: 选中态", controls_summary.text())
            self.assertIn("hovered: 悬停态", controls_summary.text())
            self.assertIn("density: 密度", controls_summary.text())
        finally:
            window.close()

    def test_launch_entry_supports_no_exec_for_tests(self) -> None:
        component_workbench = importlib.import_module("atelier.gui.ui.component_workbench")

        result = component_workbench.main(["--no-exec"])

        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
