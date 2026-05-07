from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from atelier.gui.entry import ensure_gui_dependency
from atelier.gui.ui.component_workbench_state import (
    ColorSwatchView,
    ComponentWorkbenchState,
    build_review_snapshot_record,
    build_component_workbench_state,
)

ensure_gui_dependency()

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


@dataclass(frozen=True)
class ReviewSnapshotResult:
    story_id: str
    screenshot_path: Path
    metadata_path: Path


class ComponentWorkbenchWindow(QMainWindow):
    def __init__(
        self,
        state: ComponentWorkbenchState | None = None,
        parent=None,
        review_output_dir: Path | None = None,
    ) -> None:
        super().__init__(parent)
        self._state = state or build_component_workbench_state()
        self._selected_story_id = self._state.catalog_entries[0].entry_id
        self._review_output_dir = review_output_dir or Path.cwd() / ".atelier" / "component-workbench" / "reviews"
        self._selected_story_title: QLabel | None = None
        self._selected_story_summary: QLabel | None = None
        self._selected_story_states: QLabel | None = None
        self._controls_summary: QLabel | None = None
        self._review_note: QTextEdit | None = None
        self.setObjectName("atelier-ui-component-workbench")
        self.setWindowTitle(self._state.window_title)
        self.resize(1180, 760)
        self.setCentralWidget(self._build_root())

    def state(self) -> ComponentWorkbenchState:
        return self._state

    def _build_root(self) -> QWidget:
        root = QWidget()
        root.setObjectName("component-workbench-root")
        layout = QHBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        layout.addWidget(self._build_catalog(), 0)
        layout.addWidget(self._build_preview(), 1)
        layout.addWidget(self._build_review_panel(), 0)
        return root

    def _build_catalog(self) -> QListWidget:
        catalog = QListWidget()
        catalog.setObjectName("component-workbench-catalog")
        catalog.setFixedWidth(240)
        for entry in self._state.catalog_entries:
            item = QListWidgetItem(f"{entry.label}\n{entry.surface}")
            item.setData(Qt.ItemDataRole.UserRole, entry.entry_id)
            catalog.addItem(item)
        catalog.currentRowChanged.connect(self._handle_catalog_row_changed)
        catalog.setCurrentRow(0)
        return catalog

    def _build_preview(self) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setObjectName("component-workbench-preview")
        scroll.setWidgetResizable(True)
        content = QWidget()
        content.setObjectName("component-workbench-preview-content")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        story = self._selected_story()
        title = QLabel(story.label)
        title.setObjectName("component-workbench-selected-story-title")
        title_font = title.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        self._selected_story_title = title
        summary = QLabel(story.summary)
        summary.setObjectName("component-workbench-selected-story-summary")
        summary.setWordWrap(True)
        layout.addWidget(summary)
        self._selected_story_summary = summary
        states = QLabel(self._format_states(story))
        states.setObjectName("component-workbench-selected-story-states")
        states.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(states)
        self._selected_story_states = states
        layout.addWidget(self._build_token_preview())
        layout.addWidget(self._build_typography_preview())
        layout.addWidget(self._build_candidate_placeholder())
        layout.addStretch(1)

        scroll.setWidget(content)
        return scroll

    def _build_token_preview(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("component-workbench-token-preview")
        grid = QGridLayout(panel)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        for index, swatch in enumerate(self._state.color_swatches):
            row = index // 2
            column = (index % 2) * 2
            grid.addWidget(_ColorSwatch(swatch), row, column)
            label = QLabel(f"{swatch.role}\n{swatch.value}")
            label.setObjectName(f"component-workbench-swatch-label-{swatch.role}")
            grid.addWidget(label, row, column + 1)
        return panel

    def _build_typography_preview(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("component-workbench-typography-preview")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        for sample in self._state.typography_samples:
            label = QLabel(f"{sample.label} / {sample.size_px}px / {sample.weight}")
            label.setObjectName(f"component-workbench-type-{sample.sample_id}")
            font = QFont()
            font.setPointSize(max(8, sample.size_px))
            font.setWeight(QFont.Weight(sample.weight))
            label.setFont(font)
            layout.addWidget(label)
        return panel

    def _build_candidate_placeholder(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("component-workbench-candidate-placeholder")
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)
        story = self._state.story_by_id("workflow-node")
        layout.addWidget(QLabel(story.label))
        layout.addWidget(QLabel(story.summary))
        review = QLabel("共享采用：等待用户审查")
        review.setObjectName("component-workbench-candidate-review-status")
        layout.addWidget(review)
        return panel

    def _build_review_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("component-workbench-review-panel")
        panel.setFixedWidth(300)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        header = QLabel("入库审查清单")
        header.setObjectName("component-workbench-intake-title")
        layout.addWidget(header)
        layout.addWidget(self._build_controls_panel())
        checklist = QLabel(
            "\n".join(f"{step.step_id}: {step.title}" for step in self._state.intake_steps)
        )
        checklist.setObjectName("component-workbench-intake-checklist")
        checklist.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(checklist)
        note = QTextEdit()
        note.setObjectName("component-workbench-review-note")
        note.setPlaceholderText("记录这次控件审查的观察和调整建议")
        note.setFixedHeight(96)
        layout.addWidget(note)
        self._review_note = note
        save_review = QPushButton("保存截图和备注")
        save_review.setObjectName("component-workbench-save-review")
        save_review.clicked.connect(self.save_review_snapshot)
        layout.addWidget(save_review)
        layout.addStretch(1)
        return panel

    def _build_controls_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("component-workbench-controls-panel")
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        header = QLabel("当前 Story 控制项")
        header.setObjectName("component-workbench-controls-title")
        layout.addWidget(header)
        summary = QLabel(self._format_controls(self._selected_story()))
        summary.setObjectName("component-workbench-controls-summary")
        summary.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        summary.setWordWrap(True)
        layout.addWidget(summary)
        self._controls_summary = summary
        return panel

    def _selected_story(self):
        return self._state.story_by_id(self._selected_story_id)

    def _handle_catalog_row_changed(self, row: int) -> None:
        if row < 0 or row >= len(self._state.catalog_entries):
            return
        self._selected_story_id = self._state.catalog_entries[row].entry_id
        self._refresh_selected_story()

    def _refresh_selected_story(self) -> None:
        story = self._selected_story()
        if self._selected_story_title is not None:
            self._selected_story_title.setText(story.label)
        if self._selected_story_summary is not None:
            self._selected_story_summary.setText(story.summary)
        if self._selected_story_states is not None:
            self._selected_story_states.setText(self._format_states(story))
        if self._controls_summary is not None:
            self._controls_summary.setText(self._format_controls(story))

    def _format_states(self, story) -> str:
        if not story.states:
            return "状态：未定义"
        return "状态：" + " / ".join(f"{state.state_id}: {state.label}" for state in story.states)

    def _format_controls(self, story) -> str:
        if not story.controls:
            return "暂无控制项"
        return "\n".join(
            f"{control.control_id}: {control.label} / {control.control_type} / 默认 {control.default_value}"
            for control in story.controls
        )

    def save_review_snapshot(self) -> ReviewSnapshotResult:
        self._review_output_dir.mkdir(parents=True, exist_ok=True)
        story = self._selected_story()
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        safe_story_id = "".join(char if char.isalnum() or char in "-_" else "-" for char in story.story_id)
        screenshot_filename = f"{safe_story_id}-{stamp}.png"
        metadata_filename = f"{safe_story_id}-{stamp}.json"
        screenshot_path = self._review_output_dir / screenshot_filename
        metadata_path = self._review_output_dir / metadata_filename

        pixmap = self.grab()
        pixmap.save(str(screenshot_path), "PNG")

        note = self._review_note.toPlainText().strip() if self._review_note is not None else ""
        record = build_review_snapshot_record(
            state=self._state,
            story_id=story.story_id,
            reviewer_note=note,
            screenshot_filename=screenshot_filename,
        )
        metadata_path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return ReviewSnapshotResult(
            story_id=story.story_id,
            screenshot_path=screenshot_path,
            metadata_path=metadata_path,
        )


class _ColorSwatch(QFrame):
    def __init__(self, swatch: ColorSwatchView) -> None:
        super().__init__()
        self.setObjectName(f"component-workbench-swatch-{swatch.role}")
        self.setFixedSize(36, 24)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(swatch.value))
        self.setPalette(palette)
        self.setAutoFillBackground(True)


def build_component_workbench_window(review_output_dir: Path | None = None) -> ComponentWorkbenchWindow:
    return ComponentWorkbenchWindow(
        build_component_workbench_state(),
        review_output_dir=review_output_dir,
    )


def parse_workbench_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="启动 AtelierUI 控件画板。")
    parser.add_argument(
        "--no-exec",
        action="store_true",
        help="构造控件画板窗口后直接返回，不进入 Qt 事件循环。",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_workbench_args(argv)
    app = QApplication.instance() or QApplication([])
    window = build_component_workbench_window()
    if args.no_exec:
        window.close()
        return 0
    window.show()
    return int(app.exec())


if __name__ == "__main__":
    raise SystemExit(main())
