import builtins
from dataclasses import fields
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
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QPainter, QPixmap
    from PySide6.QtWidgets import (
        QAbstractButton,
        QApplication,
        QGraphicsView,
        QLabel,
        QListWidget,
        QMainWindow,
        QPushButton,
        QScrollArea,
        QStyleOptionGraphicsItem,
        QTextEdit,
        QWidget,
    )
else:
    QAbstractButton = None
    QApplication = None
    QGraphicsView = None
    QLabel = None
    QPointF = None
    QListWidget = None
    QMainWindow = None
    QPainter = None
    QPixmap = None
    QPushButton = None
    QScrollArea = None
    QStyleOptionGraphicsItem = None
    Qt = None
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
        self.assertEqual([entry.entry_id for entry in state.catalog_entries], ["video-input-card"])
        self.assertEqual(state.catalog_entries[0].label, "VideoInputCard 候选")
        self.assertIn("card.background", [swatch.role for swatch in state.color_swatches])
        self.assertIn("workflow.selection", [swatch.role for swatch in state.color_swatches])
        self.assertIn("card_title", [sample.sample_id for sample in state.typography_samples])
        self.assertIn("user_review", [step.step_id for step in state.intake_steps])
        with self.assertRaises(KeyError):
            state.story_by_id("workflow-node")
        video_input_story = state.story_by_id("video-input-card")
        self.assertEqual(video_input_story.label, "VideoInputCard 候选")
        self.assertEqual(video_input_story.surface, "Workflow Canvas / Node Cards")
        self.assertFalse(video_input_story.shared_adoption_approved)
        self.assertEqual(
            [control.control_id for control in video_input_story.controls],
            ["selected", "hovered", "media_status", "thumbnail"],
        )

    def test_review_snapshot_metadata_is_json_safe_and_omits_absolute_paths(self) -> None:
        state_module = importlib.import_module("atelier.gui.ui.component_workbench_state")
        state = state_module.build_component_workbench_state()

        snapshot = state_module.build_review_snapshot_record(
            state=state,
            story_id="video-input-card",
            reviewer_note="节点卡片阴影偏重，待调。",
            screenshot_filename="video-input-card-20260507T120000.png",
            metadata_filename="video-input-card-20260507T120000.json",
            review_page_filename="video-input-card-20260507T120000.html",
        )

        self.assertEqual(snapshot["story_id"], "video-input-card")
        self.assertEqual(snapshot["story_label"], "VideoInputCard 候选")
        self.assertEqual(snapshot["reviewer_note"], "节点卡片阴影偏重，待调。")
        self.assertEqual(snapshot["screenshot_filename"], "video-input-card-20260507T120000.png")
        self.assertEqual(snapshot["metadata_filename"], "video-input-card-20260507T120000.json")
        self.assertEqual(snapshot["review_page_filename"], "video-input-card-20260507T120000.html")
        self.assertEqual(snapshot["controls"], ["selected", "hovered", "media_status", "thumbnail"])
        self.assertNotIn(str(REPO_ROOT), str(snapshot))

    def test_review_page_html_contains_snapshot_fields_without_absolute_paths(self) -> None:
        state_module = importlib.import_module("atelier.gui.ui.component_workbench_state")
        state = state_module.build_component_workbench_state()
        snapshot = state_module.build_review_snapshot_record(
            state=state,
            story_id="video-input-card",
            reviewer_note="节点卡片阴影偏重，待调。",
            screenshot_filename="video-input-card-20260507T120000.png",
            metadata_filename="video-input-card-20260507T120000.json",
            review_page_filename="video-input-card-20260507T120000.html",
        )

        html = state_module.render_review_page_html(snapshot)

        self.assertIn("<!doctype html>", html.lower())
        self.assertIn("AtelierUI 控件画板审查页", html)
        self.assertIn("video-input-card-20260507T120000.png", html)
        self.assertIn("video-input-card-20260507T120000.json", html)
        self.assertIn("VideoInputCard 候选", html)
        self.assertIn("selected", html)
        self.assertIn("节点卡片阴影偏重，待调。", html)
        self.assertNotIn(str(REPO_ROOT), html)

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
            review_page_path = window.findChild(QLabel, "component-workbench-review-page-path")
            controls_panel = window.findChild(QWidget, "component-workbench-controls-panel")
            review_panel = window.findChild(QWidget, "component-workbench-review-panel")
            selected_story_title = window.findChild(QLabel, "component-workbench-selected-story-title")
            selected_story_summary = window.findChild(QLabel, "component-workbench-selected-story-summary")
            product_window = window.findChild(QMainWindow, "atelier-main-window")

            self.assertIsNotNone(catalog)
            self.assertEqual(catalog.count(), 1)
            self.assertIn("VideoInputCard 候选", catalog.item(0).text())
            self.assertIsNone(token_preview)
            self.assertIsNone(checklist)
            self.assertIsNone(review_status)
            self.assertIsNone(screenshot)
            self.assertIsNone(save_review)
            self.assertIsNone(review_note)
            self.assertIsNone(review_page_path)
            self.assertIsNone(controls_panel)
            self.assertIsNone(review_panel)
            self.assertEqual(selected_story_title.text(), "VideoInputCard 候选")
            self.assertIn("视频输入节点卡片", selected_story_summary.text())
            self.assertIsNone(product_window)
        finally:
            window.close()

    def test_workbench_default_launch_geometry_is_1980x1080_and_recenters(self) -> None:
        component_workbench = importlib.import_module("atelier.gui.ui.component_workbench")
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        first_window = component_workbench.build_component_workbench_window()
        try:
            first_window.show()
            app.processEvents()

            screen = first_window.screen() or app.primaryScreen()
            expected_center = screen.availableGeometry().center()

            self.assertEqual(first_window.width(), component_workbench.COMPONENT_WORKBENCH_DEFAULT_WIDTH)
            self.assertEqual(first_window.height(), component_workbench.COMPONENT_WORKBENCH_DEFAULT_HEIGHT)
            self.assertLessEqual(abs(first_window.frameGeometry().center().x() - expected_center.x()), 4)
            self.assertLessEqual(abs(first_window.frameGeometry().center().y() - expected_center.y()), 4)

            first_window.move(12, 18)
            app.processEvents()
        finally:
            first_window.close()

        second_window = component_workbench.build_component_workbench_window()
        try:
            second_window.show()
            app.processEvents()

            screen = second_window.screen() or app.primaryScreen()
            expected_center = screen.availableGeometry().center()

            self.assertEqual(second_window.width(), component_workbench.COMPONENT_WORKBENCH_DEFAULT_WIDTH)
            self.assertEqual(second_window.height(), component_workbench.COMPONENT_WORKBENCH_DEFAULT_HEIGHT)
            self.assertLessEqual(abs(second_window.frameGeometry().center().x() - expected_center.x()), 4)
            self.assertLessEqual(abs(second_window.frameGeometry().center().y() - expected_center.y()), 4)
        finally:
            second_window.close()

    def test_video_input_card_candidate_renders_inside_workflow_canvas_node_cards_preview(self) -> None:
        component_workbench = importlib.import_module("atelier.gui.ui.component_workbench")
        font_assets_module = importlib.import_module("atelier.gui.ui.font_assets")
        video_input_card_module = importlib.import_module(
            "atelier.gui.ui.workflow_canvas.node_cards.video_input_card"
        )
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        window = component_workbench.build_component_workbench_window()
        try:
            catalog = window.findChild(QListWidget, "component-workbench-catalog")
            selected_story_title = window.findChild(QLabel, "component-workbench-selected-story-title")
            selected_story_summary = window.findChild(QLabel, "component-workbench-selected-story-summary")
            video_card = window.findChild(QWidget, "component-workbench-video-input-card")
            card_title = window.findChild(QLabel, "video-input-card-title")
            media_status = window.findChild(QLabel, "video-input-card-media-status")
            icon = window.findChild(QLabel, "video-input-card-icon")
            header = window.findChild(QWidget, "video-input-card-header-section")
            header_divider = window.findChild(QWidget, "video-input-card-header-divider")
            info_box = window.findChild(QWidget, "video-input-card-info-box")
            status_capsule = window.findChild(QWidget, "video-input-card-status-capsule")
            status_text = window.findChild(QLabel, "video-input-card-status-text")
            output_port = window.findChild(QWidget, "video-input-card-output-port")
            expand_toggle = window.findChild(QAbstractButton, "video-input-card-expand-toggle")
            stream_section = window.findChild(QWidget, "video-input-card-stream-section")
            source_input_section = window.findChild(QWidget, "video-input-card-source-input-section")
            browser_section = window.findChild(QWidget, "video-input-card-browser-section")
            video_item_cards = window.findChildren(QWidget, "video-item-card")
            video_item_thumbnails = window.findChildren(QWidget, "video-item-thumbnail")
            video_item_metadata_grids = window.findChildren(QWidget, "video-item-metadata-grid")
            video_item_filenames = window.findChildren(QLabel, "video-item-filename")
            input_row = window.findChild(QWidget, "video-input-card-input-row")
            input_box = window.findChild(QWidget, "video-input-card-input-path-box")
            input_path = window.findChild(QLabel, "video-input-card-input-path")
            browse_button = window.findChild(QPushButton, "video-input-card-browse-button")
            controls_summary = window.findChild(QLabel, "component-workbench-controls-summary")
            legacy_entry = window.findChild(QPushButton, "component-workbench-card-entry-legacy-expanded")

            catalog.setCurrentRow(0)
            app.processEvents()
            legacy_entry.click()
            app.processEvents()
            font_families = font_assets_module.load_atelier_ui_font_families()

            self.assertEqual(selected_story_title.text(), "VideoInputCard 候选")
            self.assertIn("视频输入节点卡片", selected_story_summary.text())
            self.assertIsNotNone(video_card)
            self.assertEqual(video_card.minimumWidth(), 400)
            self.assertEqual(video_card.maximumWidth(), 400)
            self.assertEqual(video_card.minimumHeight(), 600)
            self.assertEqual(video_card.maximumHeight(), 600)
            self.assertIn("border-radius: 16px", video_card.styleSheet())
            self.assertIn("border: 3px", video_card.styleSheet())
            self.assertIn(font_families.ui, video_card.styleSheet())
            self.assertIsNotNone(video_card.graphicsEffect())
            self.assertEqual(header.minimumHeight(), 50)
            self.assertEqual(header.maximumHeight(), 50)
            self.assertIsNotNone(header_divider)
            self.assertEqual(header_divider.property("visible_divider"), True)
            self.assertEqual(header_divider.minimumHeight(), 1)
            self.assertEqual(header_divider.maximumHeight(), 1)
            self.assertIn("#2A3A50", header_divider.styleSheet())
            self.assertIsNotNone(output_port)
            self.assertEqual(output_port.property("placement"), "right-of-header-divider")
            self.assertEqual(output_port.minimumWidth(), 12)
            self.assertEqual(output_port.maximumWidth(), 12)
            self.assertEqual(output_port.minimumHeight(), 12)
            self.assertEqual(output_port.maximumHeight(), 12)
            self.assertEqual(
                output_port.geometry().center().y(),
                header_divider.geometry().center().y(),
            )
            self.assertEqual(
                output_port.geometry().center().x(),
                video_card.width() - video_input_card_module.CARD_BORDER_WIDTH // 2,
            )
            self.assertIn("#172332", output_port.styleSheet())
            self.assertIn("#3B82F6", output_port.styleSheet())
            self.assertIsNotNone(expand_toggle)
            self.assertEqual(expand_toggle.minimumWidth(), 40)
            self.assertEqual(expand_toggle.maximumWidth(), 40)
            self.assertEqual(expand_toggle.minimumHeight(), 40)
            self.assertEqual(expand_toggle.maximumHeight(), 40)
            self.assertEqual(expand_toggle.property("corner_radius"), 12)
            self.assertEqual(expand_toggle.property("icon_source"), "python-painter")
            self.assertEqual(expand_toggle.property("background_treatment"), "vertical-gradient")
            self.assertEqual(expand_toggle.property("gradient_top_color"), "#25344D")
            self.assertEqual(expand_toggle.property("gradient_bottom_color"), "#101A2A")
            self.assertEqual(expand_toggle.property("mode_icon"), "collapse")
            self.assertEqual(expand_toggle.property("animation_driver"), "QVariantAnimation")
            self.assertEqual(video_card.property("animation_driver"), "QVariantAnimation")
            self.assertEqual(
                expand_toggle.geometry().x() + expand_toggle.geometry().width(),
                video_card.width()
                - video_input_card_module.CARD_BORDER_WIDTH
                - video_input_card_module.CARD_CONTENT_MARGIN_X,
            )
            self.assertEqual(
                expand_toggle.geometry().y() + expand_toggle.geometry().height(),
                video_card.height()
                - video_input_card_module.CARD_BORDER_WIDTH
                - video_input_card_module.CARD_CONTENT_MARGIN_X,
            )
            self.assertEqual(card_title.text(), "视频输入")
            self.assertTrue(font_families.ui)
            self.assertNotEqual(font_families.ui, "Noto Sans SC")
            self.assertNotEqual(font_families.ui, "JetBrains Mono")
            self.assertFalse(hasattr(font_families, "mono"))
            self.assertTrue(hasattr(font_families, "ui_light"))
            self.assertTrue(hasattr(font_families, "ui_regular"))
            self.assertTrue(hasattr(font_families, "ui_medium"))
            self.assertTrue(hasattr(font_families, "ui_semibold"))
            self.assertTrue(hasattr(font_families, "ui_bold"))
            self.assertFalse((REPO_ROOT / "atelier" / "assets" / "fonts" / "noto_sans_sc").exists())
            self.assertFalse((REPO_ROOT / "atelier" / "assets" / "fonts" / "jetbrains_mono").exists())
            font_root = REPO_ROOT / "atelier" / "assets" / "fonts" / "jiangcheng_yuanti"
            self.assertTrue(font_root.exists())
            self.assertTrue((font_root / "JiangChengYuanTi-300W.ttf").exists())
            self.assertTrue((font_root / "JiangChengYuanTi-400W.ttf").exists())
            self.assertTrue((font_root / "JiangChengYuanTi-500W.ttf").exists())
            self.assertTrue((font_root / "JiangChengYuanTi-600W.ttf").exists())
            self.assertTrue((font_root / "JiangChengYuanTi-700W.ttf").exists())
            self.assertEqual(card_title.font().family(), font_families.ui_light)
            self.assertFalse(card_title.font().bold())
            self.assertEqual(card_title.font().pointSize(), video_input_card_module.HEADER_TEXT_SIZE_PT)
            self.assertEqual(card_title.font().pixelSize(), -1)
            self.assertIn("#8AB7FF", card_title.styleSheet())
            self.assertNotIn("font-size", card_title.styleSheet())
            self.assertNotIn("font-weight", card_title.styleSheet())
            self.assertIsNone(media_status)
            self.assertEqual(info_box.property("visible_frame"), False)
            self.assertEqual(info_box.property("placement"), "left-center")
            self.assertEqual(info_box.property("width_policy"), "hug-content")
            self.assertFalse(hasattr(video_input_card_module, "ICON_TO_TITLE_FONT_HEIGHT_RATIO"))
            expected_icon_size = 48
            self.assertIsNone(icon.property("icon_size_ratio"))
            self.assertEqual(icon.property("size_source"), "inline-svg")
            self.assertEqual(icon.property("asset_path"), None)
            icon_svg = video_input_card_module.VIDEO_INPUT_CARD_ICON_SVG
            self.assertFalse(
                (
                    REPO_ROOT
                    / "atelier"
                    / "gui"
                    / "ui"
                    / "workflow_canvas"
                    / "node_cards"
                    / "assets"
                ).exists()
            )
            self.assertEqual(video_input_card_module.VIDEO_INPUT_CARD_ICON_SIZE, expected_icon_size)
            self.assertEqual(icon.property("stroke_color"), "#726FA0")
            self.assertEqual(icon.property("stroke_width"), video_input_card_module.VIDEO_INPUT_CARD_ICON_STROKE_WIDTH)
            self.assertEqual(icon.minimumWidth(), expected_icon_size)
            self.assertEqual(icon.maximumWidth(), expected_icon_size)
            self.assertEqual(icon.minimumHeight(), expected_icon_size)
            self.assertEqual(icon.maximumHeight(), expected_icon_size)
            self.assertIn('width="48"', icon_svg)
            self.assertIn('height="48"', icon_svg)
            self.assertIn('stroke="#726FA0"', icon_svg)
            self.assertIn('<path d="M21 18.5L30 24L21 29.5z"/>', icon_svg)
            self.assertFalse(icon.pixmap().isNull())
            self.assertEqual(icon.alignment(), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.assertEqual(card_title.alignment(), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.assertEqual(status_capsule.property("placement"), "right-center")
            self.assertEqual(status_capsule.property("width_policy"), "text-width-plus-padding")
            self.assertEqual(
                status_capsule.property("horizontal_padding_px"),
                video_input_card_module.STATUS_CAPSULE_HORIZONTAL_PADDING,
            )
            expected_capsule_width = (
                status_text.fontMetrics().horizontalAdvance(status_text.text())
                + status_capsule.property("horizontal_padding_px") * 2
            )
            self.assertEqual(status_capsule.minimumWidth(), expected_capsule_width)
            self.assertEqual(status_capsule.maximumWidth(), expected_capsule_width)
            self.assertEqual(status_capsule.minimumHeight(), video_input_card_module.STATUS_CAPSULE_HEIGHT)
            self.assertEqual(status_capsule.maximumHeight(), video_input_card_module.STATUS_CAPSULE_HEIGHT)
            self.assertIn(
                f"border-radius: {video_input_card_module.STATUS_CAPSULE_RADIUS}px",
                status_capsule.styleSheet(),
            )
            self.assertIn("rgba(221, 251, 230, 191)", status_capsule.styleSheet())
            self.assertEqual(status_text.text(), "正常")
            self.assertEqual(status_text.font().family(), font_families.ui_light)
            self.assertFalse(status_text.font().bold())
            self.assertEqual(status_text.font().pointSize(), video_input_card_module.STATUS_TEXT_SIZE_PT)
            self.assertEqual(status_text.font().pixelSize(), -1)
            self.assertIn("#1F7A3E", status_text.styleSheet())
            self.assertNotIn("font-size", status_text.styleSheet())
            self.assertNotIn("font-weight", status_text.styleSheet())
            self.assertEqual(status_text.alignment(), Qt.AlignmentFlag.AlignCenter)
            self.assertEqual(input_path.font().family(), font_families.ui_regular)
            self.assertEqual(browse_button.font().family(), font_families.ui_regular)
            self.assertEqual(stream_section.property("flow"), "vertical-center-sequence")
            self.assertEqual(stream_section.property("section_spacing_px"), 5)
            self.assertEqual(source_input_section.property("section_role"), "source-input")
            self.assertEqual(source_input_section.minimumHeight(), 50)
            self.assertEqual(source_input_section.maximumHeight(), 50)
            self.assertEqual(input_row.minimumWidth(), 380)
            self.assertEqual(input_row.maximumWidth(), 380)
            self.assertEqual(input_row.minimumHeight(), 50)
            self.assertEqual(input_row.maximumHeight(), 50)
            self.assertEqual(input_box.property("frame_mode"), "immersive")
            self.assertEqual(input_box.property("editing"), False)
            self.assertIn("border: none", input_box.styleSheet())
            self.assertIn("background: transparent", input_box.styleSheet())
            self.assertEqual(input_box.property("left_edge_anchor"), "video-input-card-info-box.left")
            self.assertEqual(input_box.minimumWidth(), 275)
            self.assertEqual(input_box.maximumWidth(), 275)
            self.assertEqual(input_box.minimumHeight(), 40)
            self.assertEqual(input_box.maximumHeight(), 40)
            self.assertEqual(browse_button.property("right_edge_anchor"), "video-input-card-status-capsule.right_tangent")
            self.assertEqual(browse_button.minimumWidth(), 100)
            self.assertEqual(browse_button.maximumWidth(), 100)
            self.assertEqual(browse_button.minimumHeight(), 40)
            self.assertEqual(browse_button.maximumHeight(), 40)
            self.assertEqual(input_box.width() + browse_button.width() + 5, input_row.width())
            self.assertEqual(browser_section.property("section_role"), "browser-detail")
            self.assertEqual(browser_section.property("expanded_only"), True)
            self.assertEqual(browser_section.property("visual_frame"), False)
            self.assertEqual(browser_section.property("visual_treatment"), "none")
            self.assertFalse(browser_section.isHidden())
            self.assertNotIn("rgba(14, 26, 42, 128)", browser_section.styleSheet())
            self.assertNotIn("border: 1px", browser_section.styleSheet())
            self.assertNotIn("border-radius", browser_section.styleSheet())
            self.assertEqual(len(video_item_cards), 4)
            self.assertEqual(len(video_item_thumbnails), 4)
            self.assertEqual(len(video_item_metadata_grids), 4)
            first_video_item = video_item_cards[0]
            first_thumbnail = video_item_thumbnails[0]
            first_metadata_grid = video_item_metadata_grids[0]
            self.assertEqual(first_video_item.property("layout_model"), "thumbnail-left-details-grid")
            self.assertEqual(first_video_item.property("outer_padding_px"), 5)
            self.assertEqual(first_video_item.minimumWidth(), 380)
            self.assertEqual(first_video_item.maximumWidth(), 380)
            self.assertEqual(first_video_item.minimumHeight(), 80)
            self.assertEqual(first_video_item.maximumHeight(), 80)
            self.assertEqual(first_video_item.geometry().x(), 0)
            self.assertLessEqual(first_video_item.geometry().x() + first_video_item.geometry().width(), browser_section.width())
            self.assertEqual(first_thumbnail.property("placement"), "left-center")
            self.assertEqual(first_thumbnail.property("content_model"), "thumbnail-only")
            self.assertEqual(first_thumbnail.property("duration_overlay"), False)
            self.assertEqual(first_thumbnail.findChildren(QLabel), [])
            self.assertIn("border-radius: 6px", first_thumbnail.styleSheet())
            self.assertEqual(first_thumbnail.geometry().x(), first_video_item.property("outer_padding_px"))
            self.assertEqual(first_thumbnail.geometry().y(), first_video_item.property("outer_padding_px"))
            self.assertEqual(
                first_video_item.height() - (first_thumbnail.geometry().y() + first_thumbnail.geometry().height()),
                first_video_item.property("outer_padding_px"),
            )
            self.assertEqual(first_metadata_grid.property("layout_model"), "qgrid-3x2")
            self.assertEqual(first_metadata_grid.property("row_count"), 3)
            self.assertEqual(first_metadata_grid.property("column_count"), 2)
            self.assertEqual(video_item_filenames[0].font().family(), font_families.ui_light)
            self.assertGreaterEqual(stream_section.width(), first_video_item.width())
            self.assertGreaterEqual(stream_section.width(), input_row.width())
            self.assertLessEqual(first_video_item.geometry().x() + first_video_item.geometry().width(), browser_section.width())
            self.assertLessEqual(input_row.geometry().x() + input_row.geometry().width(), stream_section.width())
            self.assertIsNone(window.findChild(QWidget, "video-input-card-preview-card"))
            self.assertIsNone(window.findChild(QLabel, "video-input-card-video-label"))
            self.assertIsNone(controls_summary)
        finally:
            window.close()

    def test_workbench_exposes_workcanvas_preview_area_for_node_card(self) -> None:
        component_workbench = importlib.import_module("atelier.gui.ui.component_workbench")
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        window = component_workbench.build_component_workbench_window()
        try:
            catalog = window.findChild(QListWidget, "component-workbench-catalog")
            preview_area = window.findChild(QWidget, "component-workbench-workcanvas-preview")
            preview_title = window.findChild(QLabel, "component-workbench-workcanvas-preview-title")
            preview_policy = window.findChild(QLabel, "component-workbench-workcanvas-preview-policy")
            preview_stage = window.findChild(QWidget, "component-workbench-workcanvas-stage")
            preview_shell = window.findChild(QWidget, "component-workbench-preview")

            catalog.setCurrentRow(0)
            app.processEvents()

            self.assertIsNotNone(preview_shell)
            self.assertNotIsInstance(preview_shell, QScrollArea)
            self.assertEqual(preview_area.property("outer_scroll_policy"), "none-canvas-handles-pan")
            self.assertIsNotNone(preview_area)
            self.assertEqual(preview_area.property("surface_role"), "dev-workcanvas-preview")
            self.assertEqual(preview_area.property("rendering_route"), "workcanvas-vector-target")
            self.assertEqual(preview_area.property("thumbnail_policy"), "cached-preview-artifact-only")
            self.assertEqual(
                preview_area.property("gui_runtime_boundary"),
                "no-worker-no-ffmpeg-no-thumbnail-generation",
            )
            self.assertEqual(preview_area.property("reference_model"), "comfyui-preview-cache-not-free-graph")
            self.assertEqual(preview_area.property("grid_pattern"), "line-and-dot-grid")
            self.assertEqual(preview_area.property("grid_spacing_px"), 24)
            self.assertEqual(preview_area.property("major_grid_every"), 4)
            self.assertIsNotNone(preview_title)
            self.assertEqual(preview_title.text(), "WorkCanvas 预览区")
            self.assertIsNotNone(preview_policy)
            self.assertIn("缓存预览", preview_policy.text())
            self.assertIn("不生成缩略图", preview_policy.text())
            self.assertIsNotNone(preview_stage)
            video_card = preview_stage.findChild(QWidget, "component-workbench-video-input-card")
            vector_preview = preview_stage.findChild(QGraphicsView, "component-workbench-video-input-vector-preview")
            vector_entry = window.findChild(QPushButton, "component-workbench-card-entry-vector-collapsed")
            legacy_entry = window.findChild(QPushButton, "component-workbench-card-entry-legacy-expanded")
            self.assertEqual(preview_stage.property("layout_model"), "canvas-fill-area")
            self.assertEqual(preview_stage.property("controls_visibility"), "nonfullscreen-visible")
            self.assertGreaterEqual(preview_stage.minimumHeight(), 360)
            self.assertIsNotNone(vector_entry)
            self.assertIsNotNone(legacy_entry)
            self.assertIsNotNone(vector_preview)
            self.assertFalse(vector_preview.isHidden())
            self.assertIsNotNone(video_card)
            self.assertTrue(video_card.isHidden())
            legacy_entry.click()
            app.processEvents()
            self.assertTrue(vector_preview.isHidden())
            self.assertFalse(video_card.isHidden())
        finally:
            window.close()

    def test_workcanvas_preview_hosts_thumbnail_stack_vector_collapsed_video_input_card(self) -> None:
        component_workbench = importlib.import_module("atelier.gui.ui.component_workbench")
        vector_card_module = importlib.import_module(
            "atelier.gui.ui.workflow_canvas.node_cards.video_input_vector_card"
        )
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        window = component_workbench.build_component_workbench_window()
        try:
            catalog = window.findChild(QListWidget, "component-workbench-catalog")
            vector_preview = window.findChild(QGraphicsView, "component-workbench-video-input-vector-preview")

            catalog.setCurrentRow(0)
            app.processEvents()

            self.assertIsNotNone(vector_preview)
            self.assertEqual(vector_preview.property("item_route"), "qgraphicsitem-paint")
            self.assertEqual(vector_preview.property("display_mode"), "collapsed")
            self.assertEqual(vector_preview.property("thumbnail_strategy"), "cached-preview-or-vector-fallback")
            self.assertEqual(vector_preview.property("gui_runtime_boundary"), "draw-only-no-thumbnail-generation")
            vector_items = [
                item
                for item in vector_preview.scene().items()
                if item.data(0) == "video-input-collapsed-node-card"
            ]
            self.assertEqual(len(vector_items), 1)
            vector_item = vector_items[0]
            self.assertEqual(vector_item.data(1), "thumbnail-stack-collapsed")
            self.assertEqual(vector_item.property("item_route"), "qgraphicsitem-paint")
            self.assertEqual(vector_item.property("thumbnail_strategy"), "cached-preview-or-vector-fallback")
            self.assertEqual(vector_item.property("display_mode"), "collapsed")
            self.assertEqual(vector_item.boundingRect().width(), vector_card_module.COLLAPSED_CARD_WIDTH)
            self.assertEqual(vector_item.boundingRect().height(), vector_card_module.COLLAPSED_CARD_HEIGHT)
            self.assertEqual(vector_item.property("thumbnail_count"), 3)
            self.assertTrue(vector_item.property("has_thumbnail_stack"))
            thumbnail_stack = vector_item.thumbnail_stack_snapshot()
            self.assertEqual(thumbnail_stack["thumbnail_count"], 3)
            self.assertEqual(thumbnail_stack["source_policy"], "cached-preview-or-vector-fallback")
            self.assertEqual(thumbnail_stack["gui_runtime_boundary"], "no-thumbnail-generation")
            self.assertEqual(
                thumbnail_stack["stack_rect"],
                (
                    vector_card_module.THUMBNAIL_STACK_X,
                    vector_card_module.THUMBNAIL_STACK_Y,
                    vector_card_module.THUMBNAIL_STACK_WIDTH,
                    vector_card_module.THUMBNAIL_STACK_HEIGHT,
                ),
            )
        finally:
            window.close()

    def test_workcanvas_nonfullscreen_controls_remain_visible_in_compact_window(self) -> None:
        component_workbench = importlib.import_module("atelier.gui.ui.component_workbench")
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        window = component_workbench.build_component_workbench_window()
        try:
            window.resize(920, 560)
            window.show()
            app.processEvents()

            card_controls = window.findChild(QWidget, "component-workbench-card-entry-controls")
            zoom_controls = window.findChild(QWidget, "component-workbench-workcanvas-zoom-controls")
            vector_preview = window.findChild(QGraphicsView, "component-workbench-video-input-vector-preview")

            self.assertIsNotNone(card_controls)
            self.assertIsNotNone(zoom_controls)
            self.assertIsNotNone(vector_preview)
            self.assertTrue(card_controls.isVisibleTo(window))
            self.assertTrue(zoom_controls.isVisibleTo(window))
            self.assertLess(card_controls.mapTo(window, card_controls.rect().topLeft()).y(), window.height())
            self.assertLess(zoom_controls.mapTo(window, zoom_controls.rect().topLeft()).y(), window.height())
            self.assertGreater(vector_preview.viewport().height(), 240)
        finally:
            window.close()

    def test_workcanvas_grid_uses_viewport_lod_when_zoomed_out(self) -> None:
        component_workbench = importlib.import_module("atelier.gui.ui.component_workbench")
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        window = component_workbench.build_component_workbench_window()
        try:
            vector_preview = window.findChild(QGraphicsView, "component-workbench-video-input-vector-preview")

            self.assertIsNotNone(vector_preview)
            self.assertEqual(vector_preview.property("grid_render_space"), "viewport")
            self.assertEqual(vector_preview.property("grid_lod_strategy"), "adaptive-screen-space")
            zoomed_out = vector_preview.grid_lod_for_scale(0.25)
            normal = vector_preview.grid_lod_for_scale(1.0)

            self.assertFalse(zoomed_out.draw_minor)
            self.assertFalse(zoomed_out.draw_dots)
            self.assertGreaterEqual(zoomed_out.major_spacing_px, component_workbench.WORKCANVAS_GRID_MIN_MAJOR_SPACING_PX)
            self.assertTrue(normal.draw_minor)
            self.assertTrue(normal.draw_dots)
        finally:
            window.close()

    def test_workcanvas_grid_uses_cached_tile_instead_of_full_viewport_primitives(self) -> None:
        component_workbench = importlib.import_module("atelier.gui.ui.component_workbench")
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        window = component_workbench.build_component_workbench_window()
        try:
            vector_preview = window.findChild(QGraphicsView, "component-workbench-video-input-vector-preview")

            self.assertIsNotNone(vector_preview)
            self.assertEqual(vector_preview.property("grid_paint_strategy"), "cached-tile-brush")
            self.assertEqual(vector_preview.property("grid_full_viewport_primitive_loop"), False)
            normal_tile = vector_preview.grid_tile_for_scale(1.0)
            normal_tile_again = vector_preview.grid_tile_for_scale(1.0)
            zoomed_out_tile = vector_preview.grid_tile_for_scale(0.25)

            self.assertEqual(normal_tile.cacheKey(), normal_tile_again.cacheKey())
            self.assertLessEqual(
                vector_preview.grid_tile_cache_size(),
                component_workbench.WORKCANVAS_GRID_TILE_CACHE_LIMIT,
            )
            self.assertGreater(normal_tile.width(), zoomed_out_tile.width())
            self.assertGreater(normal_tile.height(), zoomed_out_tile.height())
        finally:
            window.close()

    def test_workcanvas_perf_hud_is_visible_and_reports_background_and_node_paint(self) -> None:
        component_workbench = importlib.import_module("atelier.gui.ui.component_workbench")
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        window = component_workbench.build_component_workbench_window()
        try:
            window.show()
            app.processEvents()

            vector_preview = window.findChild(QGraphicsView, "component-workbench-video-input-vector-preview")
            hud = window.findChild(QLabel, "component-workbench-workcanvas-perf-hud")

            self.assertIsNotNone(vector_preview)
            self.assertIsNotNone(hud)
            self.assertTrue(hud.isVisibleTo(window))
            self.assertEqual(hud.property("surface_role"), "workcanvas-dev-perf-hud")
            self.assertTrue(vector_preview.property("debug_perf"))

            vector_item = next(
                item
                for item in vector_preview.scene().items()
                if item.data(0) == "video-input-collapsed-node-card"
            )
            self.assertTrue(vector_item.property("debug_perf"))

            vector_preview.scale(1.25, 1.25)
            tile = QPixmap(160, 120)
            painter = QPainter(tile)
            try:
                vector_preview.drawBackground(painter, vector_preview.sceneRect())
                vector_item.paint(painter, QStyleOptionGraphicsItem())
            finally:
                painter.end()

            vector_preview._last_draw_background_ms = 16.67
            vector_item._last_paint_ms = 8.33
            window.refresh_workcanvas_perf_hud()
            text = hud.text()

            self.assertIn("缩放 125%", text)
            self.assertIn("背景 16.67 ms / 60 fps", text)
            self.assertIn("tile 命中", text)
            self.assertIn("key", text)
            self.assertIn("update minimal", text)
            self.assertIn("AA 背景 off / 节点 on", text)
            self.assertIn("节点 8.33 ms / 120 fps", text)
        finally:
            window.close()

    def test_workcanvas_view_debug_perf_tracks_background_and_update_mode(self) -> None:
        component_workbench = importlib.import_module("atelier.gui.ui.component_workbench")
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        window = component_workbench.build_component_workbench_window()
        try:
            vector_preview = window.findChild(QGraphicsView, "component-workbench-video-input-vector-preview")
            self.assertIsNotNone(vector_preview)

            vector_preview.set_debug_perf(True)
            vector_preview.set_viewport_update_mode_name("bounding")
            vector_preview.scale(1.25, 1.25)
            tile = QPixmap(160, 120)
            painter = QPainter(tile)
            try:
                vector_preview.drawBackground(painter, vector_preview.sceneRect())
            finally:
                painter.end()
            vector_preview.grid_tile_for_scale(1.25)

            snapshot = vector_preview.debug_perf_snapshot()
            self.assertTrue(snapshot["debug_perf"])
            self.assertEqual(snapshot["viewport_update_mode"], "bounding")
            self.assertEqual(
                vector_preview.viewportUpdateMode(),
                QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate,
            )
            self.assertGreaterEqual(snapshot["draw_background_ms"], 0.0)
            self.assertGreaterEqual(snapshot["tile_cache_hits"], 1)
            self.assertGreaterEqual(snapshot["tile_cache_misses"], 1)
            self.assertIsInstance(snapshot["tile_key"], tuple)
            self.assertAlmostEqual(snapshot["zoom"], 1.25)
            self.assertFalse(snapshot["background_antialiasing"])

            vector_preview.set_viewport_update_mode_name("full")
            self.assertEqual(vector_preview.debug_perf_snapshot()["viewport_update_mode"], "full")
            self.assertEqual(
                vector_preview.viewportUpdateMode(),
                QGraphicsView.ViewportUpdateMode.FullViewportUpdate,
            )

            vector_preview.set_viewport_update_mode_name("minimal")
            self.assertEqual(vector_preview.debug_perf_snapshot()["viewport_update_mode"], "minimal")
            self.assertEqual(
                vector_preview.viewportUpdateMode(),
                QGraphicsView.ViewportUpdateMode.MinimalViewportUpdate,
            )
        finally:
            window.close()

    def test_video_input_collapsed_item_debug_perf_tracks_paint_time(self) -> None:
        vector_card_module = importlib.import_module(
            "atelier.gui.ui.workflow_canvas.node_cards.video_input_vector_card"
        )
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        item = vector_card_module.VideoInputCollapsedNodeCardItem()
        item.set_debug_perf(True)
        pixmap = QPixmap(
            vector_card_module.COLLAPSED_CARD_WIDTH,
            vector_card_module.COLLAPSED_CARD_HEIGHT,
        )
        painter = QPainter(pixmap)
        try:
            item.paint(painter, QStyleOptionGraphicsItem())
        finally:
            painter.end()

        snapshot = item.debug_perf_snapshot()
        self.assertTrue(snapshot["debug_perf"])
        self.assertEqual(snapshot["paint_count"], 1)
        self.assertGreaterEqual(snapshot["paint_ms"], 0.0)
        self.assertTrue(snapshot["antialiasing"])

    def test_video_input_collapsed_primary_metric_sits_higher_in_body(self) -> None:
        vector_card_module = importlib.import_module(
            "atelier.gui.ui.workflow_canvas.node_cards.video_input_vector_card"
        )

        self.assertLess(
            vector_card_module.PRIMARY_LABEL_RECT_Y,
            vector_card_module.PRIMARY_VALUE_RECT_Y,
        )
        self.assertLess(vector_card_module.PRIMARY_VALUE_RECT_Y, 153)

    def test_video_input_collapsed_dividers_share_same_length(self) -> None:
        vector_card_module = importlib.import_module(
            "atelier.gui.ui.workflow_canvas.node_cards.video_input_vector_card"
        )

        self.assertEqual(
            vector_card_module.SUMMARY_DIVIDER_LEFT_X,
            vector_card_module.CONTENT_MARGIN_X,
        )
        self.assertEqual(
            vector_card_module.SUMMARY_DIVIDER_RIGHT_X,
            vector_card_module.COLLAPSED_CARD_WIDTH - vector_card_module.CONTENT_MARGIN_X,
        )
        self.assertEqual(vector_card_module.HEADER_DIVIDER_LEFT_X, vector_card_module.SUMMARY_DIVIDER_LEFT_X)
        self.assertEqual(vector_card_module.HEADER_DIVIDER_RIGHT_X, vector_card_module.SUMMARY_DIVIDER_RIGHT_X)

    def test_video_input_collapsed_content_layout_does_not_depend_on_border_width(self) -> None:
        vector_card_module = importlib.import_module(
            "atelier.gui.ui.workflow_canvas.node_cards.video_input_vector_card"
        )
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        original_border_width = vector_card_module.CARD_BORDER_WIDTH
        try:
            item = vector_card_module.VideoInputCollapsedNodeCardItem()
            baseline = item.content_layout_snapshot()

            vector_card_module.CARD_BORDER_WIDTH = original_border_width + 6
            thicker_border = item.content_layout_snapshot()

            self.assertNotEqual(thicker_border["border_rect"], baseline["border_rect"])
            for key in (
                "icon_rect",
                "title_rect",
                "status_rect",
                "primary_label_rect",
                "primary_value_rect",
                "header_divider_line",
                "summary_divider_line",
            ):
                self.assertEqual(thicker_border[key], baseline[key])
        finally:
            vector_card_module.CARD_BORDER_WIDTH = original_border_width

    def test_video_input_collapsed_icon_play_triangle_is_centered(self) -> None:
        vector_card_module = importlib.import_module(
            "atelier.gui.ui.workflow_canvas.node_cards.video_input_vector_card"
        )
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        item = vector_card_module.VideoInputCollapsedNodeCardItem()
        icon = item.video_icon_layout_snapshot()
        triangle = icon["play_triangle_points"]
        triangle_centroid_x = sum(point[0] for point in triangle) / len(triangle)

        self.assertAlmostEqual(triangle_centroid_x, icon["media_panel_center_x"], delta=1.0)
        self.assertLess(triangle[1][0], icon["right_reel_x"])

    def test_video_input_collapsed_font_weights_follow_review_marks(self) -> None:
        vector_card_module = importlib.import_module(
            "atelier.gui.ui.workflow_canvas.node_cards.video_input_vector_card"
        )
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        item = vector_card_module.VideoInputCollapsedNodeCardItem()
        fonts = item.font_role_snapshot()

        self.assertEqual(fonts["title_weight"], 400)
        self.assertEqual(fonts["primary_label_weight"], 400)
        self.assertEqual(fonts["summary_label_weight"], 400)
        self.assertEqual(fonts["status_weight"], 500)

    def test_video_input_collapsed_appearance_separates_selected_and_resting_state(self) -> None:
        vector_card_module = importlib.import_module(
            "atelier.gui.ui.workflow_canvas.node_cards.video_input_vector_card"
        )
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        view_model_fields = [
            field.name for field in fields(vector_card_module.VideoInputCollapsedNodeCardViewModel)
        ]
        self.assertIn("selected", view_model_fields)
        self.assertTrue(hasattr(vector_card_module.VideoInputCollapsedNodeCardItem, "appearance_snapshot"))
        selected_item = vector_card_module.VideoInputCollapsedNodeCardItem()
        resting_item = vector_card_module.VideoInputCollapsedNodeCardItem(
            vector_card_module.VideoInputCollapsedNodeCardViewModel(selected=False)
        )

        selected = selected_item.appearance_snapshot()
        resting = resting_item.appearance_snapshot()

        self.assertTrue(selected["selected"])
        self.assertEqual(selected["border_width"], 3)
        self.assertEqual(selected["border_color"], "#3B82F6")
        self.assertTrue(selected["glow_enabled"])
        self.assertGreater(selected["glow_width"], selected["border_width"])
        self.assertEqual(selected["background_gradient"], ("#182A3D", "#111D2C", "#0B1524"))
        self.assertFalse(resting["selected"])
        self.assertEqual(resting["border_width"], 1)
        self.assertEqual(resting["border_color"], "#2A3A50")
        self.assertFalse(resting["glow_enabled"])

    def test_video_input_collapsed_summary_metrics_use_icon_title_rows(self) -> None:
        vector_card_module = importlib.import_module(
            "atelier.gui.ui.workflow_canvas.node_cards.video_input_vector_card"
        )
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        item = vector_card_module.VideoInputCollapsedNodeCardItem()
        self.assertTrue(
            hasattr(vector_card_module.VideoInputCollapsedNodeCardItem, "summary_metric_layout_snapshot")
        )
        layout = item.summary_metric_layout_snapshot()

        self.assertEqual([metric["label"] for metric in layout["metrics"]], ["总时长", "总大小", "待处理"])
        self.assertEqual([metric["icon_role"] for metric in layout["metrics"]], ["duration", "size", "pending"])
        self.assertEqual(layout["title_row_model"], "icon-left-title-right")
        self.assertEqual(layout["value_row_model"], "value-below-title-row")
        self.assertEqual(layout["metrics_right_x"], vector_card_module.COLLAPSED_CARD_WIDTH - vector_card_module.CONTENT_MARGIN_X)
        self.assertEqual(layout["expand_control_placement"], "thumbnail-stack-overlay")
        self.assertGreaterEqual(
            vector_card_module.SUMMARY_ICON_SIZE,
            vector_card_module.SUMMARY_TITLE_ROW_HEIGHT,
        )
        for metric in layout["metrics"]:
            icon_x, icon_y, icon_w, icon_h = metric["icon_rect"]
            title_x, title_y, title_w, title_h = metric["title_rect"]
            value_x, value_y, value_w, value_h = metric["value_rect"]
            self.assertLess(icon_x + icon_w, title_x)
            self.assertEqual(icon_h, vector_card_module.SUMMARY_ICON_SIZE)
            self.assertEqual(title_y, icon_y)
            self.assertGreater(value_y, title_y + title_h - 1)
            self.assertGreaterEqual(value_w, title_w)

    def test_video_input_collapsed_pending_icon_has_even_line_spacing(self) -> None:
        vector_card_module = importlib.import_module(
            "atelier.gui.ui.workflow_canvas.node_cards.video_input_vector_card"
        )
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        item = vector_card_module.VideoInputCollapsedNodeCardItem()
        layout = item.summary_metric_layout_snapshot()
        pending = next(metric for metric in layout["metrics"] if metric["icon_role"] == "pending")
        y_positions = pending["icon_mark_y_positions"]

        self.assertEqual(len(y_positions), 3)
        self.assertAlmostEqual(y_positions[1] - y_positions[0], y_positions[2] - y_positions[1])

    def test_video_input_collapsed_expand_affordance_is_line_only_corners(self) -> None:
        vector_card_module = importlib.import_module(
            "atelier.gui.ui.workflow_canvas.node_cards.video_input_vector_card"
        )
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        item = vector_card_module.VideoInputCollapsedNodeCardItem()
        self.assertTrue(
            hasattr(vector_card_module.VideoInputCollapsedNodeCardItem, "expand_affordance_snapshot")
        )
        button = item.expand_affordance_snapshot()
        divider_y = item.content_layout_snapshot()["summary_divider_line"][1]

        self.assertEqual(button["rect"], (195.0, 85.0, 40.0, 40.0))
        self.assertEqual(button["visual_treatment"], "line-only")
        self.assertEqual(button["line_style"], "four-corner-expand")
        self.assertEqual(button["background_treatment"], "none")
        self.assertEqual(button["shadow"], "none")
        self.assertEqual(button["icon_source"], "python-painter")
        self.assertEqual(button["mode_icon"], "expand")
        self.assertEqual(button["placement"], "thumbnail-stack-overlay")
        self.assertEqual(button["trigger"], "pointer-proximity")
        self.assertEqual(button["enter_distance_px"], 40)
        self.assertEqual(button["exit_distance_px"], 64)
        self.assertEqual(button["opacity"], 0.0)
        self.assertEqual(button["stroke_color"], "#60A5FA")
        self.assertEqual(button["stroke_width"], 3.0)
        self.assertEqual(button["stroke_cap"], "round")
        self.assertEqual(button["corner_count"], 4)
        self.assertEqual(button["segment_count"], 8)
        self.assertLess(button["rect"][1], divider_y)

    def test_video_input_collapsed_thumbnail_stack_reveals_expand_on_pointer_proximity(self) -> None:
        vector_card_module = importlib.import_module(
            "atelier.gui.ui.workflow_canvas.node_cards.video_input_vector_card"
        )
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        item = vector_card_module.VideoInputCollapsedNodeCardItem()
        stack = item.thumbnail_stack_snapshot()
        stack_x, stack_y, stack_w, stack_h = stack["stack_rect"]
        stack_center = QPointF(stack_x + stack_w / 2, stack_y + stack_h / 2)
        inside_exit_outside_enter = QPointF(stack_x - 52, stack_y + stack_h / 2)
        outside_exit = QPointF(stack_x - 70, stack_y + stack_h / 2)

        self.assertEqual(stack["interaction_state"], "thumbnail-stack")
        self.assertEqual(stack["thumbnail_opacity"], 1.0)
        self.assertEqual(stack["expand_affordance_opacity"], 0.0)

        item.update_thumbnail_proximity(stack_center, animated=False)
        revealed = item.thumbnail_stack_snapshot()

        self.assertEqual(revealed["interaction_state"], "expand-revealed")
        self.assertLess(revealed["thumbnail_opacity"], 1.0)
        self.assertEqual(revealed["expand_affordance_opacity"], 1.0)

        item.update_thumbnail_proximity(inside_exit_outside_enter, animated=False)
        self.assertEqual(item.thumbnail_stack_snapshot()["interaction_state"], "expand-revealed")

        item.update_thumbnail_proximity(outside_exit, animated=False)
        hidden = item.thumbnail_stack_snapshot()

        self.assertEqual(hidden["interaction_state"], "thumbnail-stack")
        self.assertEqual(hidden["thumbnail_opacity"], 1.0)
        self.assertEqual(hidden["expand_affordance_opacity"], 0.0)

    def test_workcanvas_vector_preview_supports_basic_zoom_controls(self) -> None:
        component_workbench = importlib.import_module("atelier.gui.ui.component_workbench")
        vector_card_module = importlib.import_module(
            "atelier.gui.ui.workflow_canvas.node_cards.video_input_vector_card"
        )
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        window = component_workbench.build_component_workbench_window()
        try:
            catalog = window.findChild(QListWidget, "component-workbench-catalog")
            vector_preview = window.findChild(QGraphicsView, "component-workbench-video-input-vector-preview")
            zoom_label = window.findChild(QLabel, "component-workbench-workcanvas-zoom-label")
            zoom_in = window.findChild(QPushButton, "component-workbench-workcanvas-zoom-in")
            zoom_out = window.findChild(QPushButton, "component-workbench-workcanvas-zoom-out")
            zoom_reset = window.findChild(QPushButton, "component-workbench-workcanvas-zoom-reset")
            full_screen = window.findChild(QPushButton, "component-workbench-workcanvas-fullscreen")

            catalog.setCurrentRow(0)
            app.processEvents()

            vector_item = next(
                item
                for item in vector_preview.scene().items()
                if item.data(0) == "video-input-collapsed-node-card"
            )
            self.assertIsNotNone(zoom_label)
            self.assertIsNotNone(zoom_in)
            self.assertIsNotNone(zoom_out)
            self.assertIsNotNone(zoom_reset)
            self.assertIsNotNone(full_screen)
            self.assertEqual(full_screen.text(), "全屏")
            self.assertEqual(zoom_label.text(), "100%")
            self.assertEqual(vector_preview.property("zoom_min"), 0.25)
            self.assertEqual(vector_preview.property("zoom_max"), 4.0)
            self.assertEqual(vector_preview.property("zoom_step"), 0.25)
            self.assertEqual(vector_preview.property("pan_interaction"), "mouse-drag")
            self.assertEqual(vector_preview.dragMode(), QGraphicsView.DragMode.ScrollHandDrag)
            self.assertGreater(vector_preview.sceneRect().width(), vector_preview.viewport().width())
            self.assertGreater(vector_preview.sceneRect().height(), vector_preview.viewport().height())
            self.assertEqual(vector_item.boundingRect().width(), vector_card_module.COLLAPSED_CARD_WIDTH)
            self.assertEqual(vector_item.boundingRect().height(), vector_card_module.COLLAPSED_CARD_HEIGHT)

            zoom_in.click()
            app.processEvents()

            self.assertEqual(zoom_label.text(), "125%")
            self.assertAlmostEqual(vector_preview.transform().m11(), 1.25)
            self.assertAlmostEqual(vector_preview.transform().m22(), 1.25)
            self.assertEqual(vector_item.boundingRect().width(), vector_card_module.COLLAPSED_CARD_WIDTH)
            self.assertEqual(vector_item.boundingRect().height(), vector_card_module.COLLAPSED_CARD_HEIGHT)

            zoom_out.click()
            app.processEvents()
            zoom_out.click()
            app.processEvents()

            self.assertEqual(zoom_label.text(), "75%")
            self.assertAlmostEqual(vector_preview.transform().m11(), 0.75)

            zoom_reset.click()
            app.processEvents()

            self.assertEqual(zoom_label.text(), "100%")
            self.assertAlmostEqual(vector_preview.transform().m11(), 1.0)
        finally:
            window.close()

    def test_workcanvas_fullscreen_button_opens_dedicated_preview_window(self) -> None:
        component_workbench = importlib.import_module("atelier.gui.ui.component_workbench")
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        window = component_workbench.build_component_workbench_window()
        try:
            full_screen = window.findChild(QPushButton, "component-workbench-workcanvas-fullscreen")

            full_screen.click()
            app.processEvents()

            full_screen_window = window.findChild(QMainWindow, "component-workbench-workcanvas-fullscreen-window")
            self.assertIsNotNone(full_screen_window)
            self.assertTrue(full_screen_window.isFullScreen())
            full_screen_preview = full_screen_window.findChild(
                QGraphicsView,
                "component-workbench-video-input-vector-preview-fullscreen",
            )
            fullscreen_toolbar = full_screen_window.findChild(
                QWidget,
                "component-workbench-workcanvas-fullscreen-toolbar",
            )
            fullscreen_zoom_label = full_screen_window.findChild(
                QLabel,
                "component-workbench-workcanvas-fullscreen-zoom-label",
            )
            fullscreen_zoom_in = full_screen_window.findChild(
                QPushButton,
                "component-workbench-workcanvas-fullscreen-zoom-in",
            )
            fullscreen_zoom_reset = full_screen_window.findChild(
                QPushButton,
                "component-workbench-workcanvas-fullscreen-zoom-reset",
            )
            fullscreen_perf_hud = full_screen_window.findChild(
                QLabel,
                "component-workbench-workcanvas-perf-hud-fullscreen",
            )
            self.assertIsNotNone(full_screen_preview)
            self.assertEqual(full_screen_preview.property("item_route"), "qgraphicsitem-paint")
            self.assertEqual(full_screen_preview.property("thumbnail_strategy"), "cached-preview-or-vector-fallback")
            self.assertIsNotNone(fullscreen_toolbar)
            self.assertIsNotNone(fullscreen_zoom_label)
            self.assertIsNotNone(fullscreen_zoom_in)
            self.assertIsNotNone(fullscreen_zoom_reset)
            self.assertIsNotNone(fullscreen_perf_hud)
            self.assertTrue(fullscreen_toolbar.isVisibleTo(full_screen_window))
            self.assertTrue(fullscreen_perf_hud.isVisibleTo(full_screen_window))
            self.assertEqual(fullscreen_toolbar.property("surface_role"), "workcanvas-fullscreen-controls")
            self.assertEqual(fullscreen_perf_hud.property("surface_role"), "workcanvas-dev-perf-hud")
            self.assertIn("性能 HUD", fullscreen_perf_hud.text())
            self.assertEqual(fullscreen_zoom_label.text(), "100%")

            fullscreen_zoom_in.click()
            app.processEvents()

            self.assertEqual(fullscreen_zoom_label.text(), "125%")
            self.assertAlmostEqual(full_screen_preview.transform().m11(), 1.25)

            fullscreen_zoom_reset.click()
            app.processEvents()

            self.assertEqual(fullscreen_zoom_label.text(), "100%")
            self.assertAlmostEqual(full_screen_preview.transform().m11(), 1.0)
        finally:
            window.close()

    def test_workcanvas_fullscreen_perf_hud_does_not_resize_on_live_refresh(self) -> None:
        component_workbench = importlib.import_module("atelier.gui.ui.component_workbench")
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        window = component_workbench.build_component_workbench_window()
        try:
            full_screen = window.findChild(QPushButton, "component-workbench-workcanvas-fullscreen")
            full_screen.click()
            app.processEvents()

            full_screen_window = window.findChild(QMainWindow, "component-workbench-workcanvas-fullscreen-window")
            full_screen_preview = full_screen_window.findChild(
                QGraphicsView,
                "component-workbench-video-input-vector-preview-fullscreen",
            )
            fullscreen_perf_hud = full_screen_window.findChild(
                QLabel,
                "component-workbench-workcanvas-perf-hud-fullscreen",
            )
            self.assertIsNotNone(full_screen_preview)
            self.assertIsNotNone(fullscreen_perf_hud)

            full_screen_preview._last_draw_background_ms = 0.27
            window.refresh_workcanvas_perf_hud()
            stable_size = fullscreen_perf_hud.size()

            full_screen_preview._last_draw_background_ms = 1234.56
            window.refresh_workcanvas_perf_hud()

            self.assertEqual(fullscreen_perf_hud.size(), stable_size)
        finally:
            window.close()

    def test_video_input_card_candidate_supports_collapsed_preview_mode(self) -> None:
        video_input_card_module = importlib.import_module(
            "atelier.gui.ui.workflow_canvas.node_cards.video_input_card"
        )
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        card = video_input_card_module.VideoInputCardCandidate(expanded=False)
        try:
            card.show()
            app.processEvents()
            browser_section = card.findChild(QWidget, "video-input-card-browser-section")
            collapsed_main = card.findChild(QWidget, "video-input-card-collapsed-main-section")
            collapsed_summary = card.findChild(QLabel, "video-input-card-collapsed-summary")
            primary_metric = card.findChild(QWidget, "video-input-card-collapsed-primary-metric")
            primary_metric_title = card.findChild(QLabel, "video-input-card-collapsed-primary-title")
            primary_metric_value = card.findChild(QLabel, "video-input-card-collapsed-primary-value")
            thumbnail_stack = card.findChild(QWidget, "video-input-card-collapsed-thumbnail-stack")
            thumbnails = card.findChildren(QWidget, "video-input-card-collapsed-thumbnail")
            stat_metrics = card.findChildren(QWidget, "video-input-card-collapsed-stat")
            stat_title_rows = card.findChildren(QWidget, "video-input-card-collapsed-stat-title-row")
            stat_icons = card.findChildren(QLabel, "video-input-card-collapsed-stat-icon")
            stat_titles = card.findChildren(QLabel, "video-input-card-collapsed-stat-title")
            stat_values = card.findChildren(QLabel, "video-input-card-collapsed-stat-value")
            source_input_section = card.findChild(QWidget, "video-input-card-source-input-section")
            header_divider = card.findChild(QWidget, "video-input-card-header-divider")
            output_port = card.findChild(QWidget, "video-input-card-output-port")
            expand_toggle = card.findChild(QAbstractButton, "video-input-card-expand-toggle")

            self.assertEqual(card.property("display_mode"), "collapsed")
            self.assertEqual(card.minimumWidth(), 300)
            self.assertEqual(card.maximumWidth(), 300)
            self.assertEqual(card.minimumHeight(), 200)
            self.assertEqual(card.maximumHeight(), 200)
            self.assertTrue(source_input_section.isHidden())
            self.assertTrue(browser_section.isHidden())
            self.assertIsNotNone(collapsed_main)
            self.assertFalse(collapsed_main.isHidden())
            self.assertEqual(collapsed_main.property("section_role"), "collapsed-main")
            self.assertEqual(collapsed_main.property("layout_model"), "collapsed-summary-hero")
            self.assertIsNone(collapsed_summary)
            self.assertIsNotNone(primary_metric)
            self.assertEqual(primary_metric.property("placement"), "middle-left")
            self.assertEqual(primary_metric.property("layout_model"), "vertical-text-stack")
            self.assertEqual(primary_metric_title.text(), "视频数")
            self.assertEqual(primary_metric_value.text(), "32")
            self.assertEqual(primary_metric_value.property("visual_role"), "hero-number")
            self.assertIsNotNone(thumbnail_stack)
            self.assertEqual(thumbnail_stack.property("placement"), "middle-right")
            self.assertEqual(thumbnail_stack.property("thumbnail_count"), 3)
            self.assertEqual(len(thumbnails), 3)
            for thumbnail in thumbnails:
                self.assertEqual(thumbnail.property("size_source"), "inline-svg-rendered-size")
                self.assertEqual(thumbnail.minimumWidth(), video_input_card_module.COLLAPSED_THUMBNAIL_WIDTH)
                self.assertEqual(thumbnail.minimumHeight(), video_input_card_module.COLLAPSED_THUMBNAIL_HEIGHT)
            self.assertEqual(len(stat_metrics), 3)
            self.assertEqual(len(stat_title_rows), 3)
            self.assertEqual(len(stat_icons), 3)
            self.assertEqual([metric.property("metric_id") for metric in stat_metrics], ["duration", "size", "pending"])
            for metric in stat_metrics:
                self.assertEqual(metric.property("layout_model"), "icon-title-row-value-stack")
            for title_row in stat_title_rows:
                self.assertEqual(title_row.property("layout_model"), "icon-title-inline")
            for stat_icon in stat_icons:
                self.assertEqual(stat_icon.property("size_source"), "inline-svg-rendered-size")
                self.assertEqual(stat_icon.minimumWidth(), video_input_card_module.COLLAPSED_STAT_ICON_SIZE)
                self.assertEqual(stat_icon.minimumHeight(), video_input_card_module.COLLAPSED_STAT_ICON_SIZE)
            self.assertEqual([label.text() for label in stat_titles], ["总时长", "总大小", "待处理"])
            self.assertEqual([label.text() for label in stat_values], ["05:27:18", "48.6 GB", "6"])
            self.assertEqual(output_port.geometry().center().y(), header_divider.geometry().center().y())
            self.assertEqual(
                output_port.geometry().center().x(),
                card.width() - video_input_card_module.CARD_BORDER_WIDTH // 2,
            )
            self.assertIsNotNone(expand_toggle)
            self.assertEqual(expand_toggle.minimumWidth(), 40)
            self.assertEqual(expand_toggle.maximumWidth(), 40)
            self.assertEqual(expand_toggle.minimumHeight(), 40)
            self.assertEqual(expand_toggle.maximumHeight(), 40)
            self.assertEqual(expand_toggle.property("corner_radius"), 12)
            self.assertEqual(expand_toggle.property("icon_source"), "python-painter")
            self.assertEqual(expand_toggle.property("background_treatment"), "vertical-gradient")
            self.assertEqual(expand_toggle.property("gradient_top_color"), "#25344D")
            self.assertEqual(expand_toggle.property("gradient_bottom_color"), "#101A2A")
            self.assertEqual(expand_toggle.property("mode_icon"), "expand")
            self.assertEqual(expand_toggle.property("animation_driver"), "QVariantAnimation")
            self.assertEqual(
                expand_toggle.geometry().x() + expand_toggle.geometry().width(),
                card.width()
                - video_input_card_module.CARD_BORDER_WIDTH
                - video_input_card_module.CARD_CONTENT_MARGIN_X,
            )
            self.assertEqual(
                expand_toggle.geometry().y() + expand_toggle.geometry().height(),
                card.height()
                - video_input_card_module.CARD_BORDER_WIDTH
                - video_input_card_module.CARD_CONTENT_MARGIN_X,
            )
        finally:
            card.close()

    def test_video_input_card_expand_toggle_switches_mode_with_python_animation(self) -> None:
        video_input_card_module = importlib.import_module(
            "atelier.gui.ui.workflow_canvas.node_cards.video_input_card"
        )
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        card = video_input_card_module.VideoInputCardCandidate(expanded=True)
        try:
            card.show()
            app.processEvents()
            expand_toggle = card.findChild(QAbstractButton, "video-input-card-expand-toggle")
            browser_section = card.findChild(QWidget, "video-input-card-browser-section")
            collapsed_main = card.findChild(QWidget, "video-input-card-collapsed-main-section")

            self.assertIsNotNone(expand_toggle)
            self.assertEqual(card.property("animation_driver"), "QVariantAnimation")
            self.assertEqual(card.property("animation_duration_ms"), video_input_card_module.EXPAND_TOGGLE_ANIMATION_MS)

            expand_toggle.click()
            app.processEvents()

            self.assertEqual(card.property("display_mode"), "collapsed")
            self.assertEqual(expand_toggle.property("mode_icon"), "expand")
            self.assertTrue(browser_section.isHidden())
            self.assertFalse(collapsed_main.isHidden())
            self.assertEqual(card.property("animation_last_target"), "collapsed")

            card.set_expanded(True, animated=False)
            app.processEvents()

            self.assertEqual(card.property("display_mode"), "expanded")
            self.assertEqual(expand_toggle.property("mode_icon"), "collapse")
            self.assertEqual(card.width(), video_input_card_module.EXPANDED_CARD_WIDTH)
            self.assertEqual(card.height(), video_input_card_module.EXPANDED_CARD_HEIGHT)
            self.assertEqual(card.property("animation_last_target"), "expanded")
        finally:
            card.close()

    def test_save_review_snapshot_writes_png_and_json_to_review_directory(self) -> None:
        component_workbench = importlib.import_module("atelier.gui.ui.component_workbench")
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)

        with tempfile.TemporaryDirectory() as temp_dir:
            window = component_workbench.build_component_workbench_window(review_output_dir=Path(temp_dir))
            try:
                catalog = window.findChild(QListWidget, "component-workbench-catalog")
                review_note = window.findChild(QTextEdit, "component-workbench-review-note")

                catalog.setCurrentRow(0)
                app.processEvents()

                self.assertIsNone(review_note)
                result = window.save_review_snapshot()

                self.assertEqual(result.story_id, "video-input-card")
                self.assertTrue(result.screenshot_path.exists())
                self.assertTrue(result.metadata_path.exists())
                self.assertTrue(result.review_page_path.exists())
                self.assertEqual(result.screenshot_path.suffix, ".png")
                self.assertEqual(result.review_page_path.suffix, ".html")
                metadata_text = result.metadata_path.read_text(encoding="utf-8")
                self.assertIn('"story_id": "video-input-card"', metadata_text)
                self.assertIn('"metadata_filename"', metadata_text)
                self.assertIn('"review_page_filename"', metadata_text)
                self.assertNotIn(str(REPO_ROOT), metadata_text)
                review_page_text = result.review_page_path.read_text(encoding="utf-8")
                self.assertIn("AtelierUI 控件画板审查页", review_page_text)
                self.assertIn(result.screenshot_path.name, review_page_text)
                self.assertIn(result.metadata_path.name, review_page_text)
                self.assertNotIn(str(REPO_ROOT), review_page_text)
                review_page_path = window.findChild(QLabel, "component-workbench-review-page-path")
                self.assertIsNone(review_page_path)
            finally:
                window.close()

    def test_catalog_archives_generic_candidate_and_keeps_video_input_focused(self) -> None:
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

            catalog.setCurrentRow(0)
            app.processEvents()

            self.assertEqual(catalog.count(), 1)
            self.assertEqual(selected_story_title.text(), "VideoInputCard 候选")
            self.assertIn("视频输入节点卡片", selected_story_summary.text())
            self.assertIn("empty", selected_states.text())
            self.assertIn("selected", selected_states.text())
            self.assertIsNone(controls_panel)
            self.assertIsNone(controls_summary)
        finally:
            window.close()

    def test_launch_entry_supports_no_exec_for_tests(self) -> None:
        component_workbench = importlib.import_module("atelier.gui.ui.component_workbench")

        result = component_workbench.main(["--no-exec"])

        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
