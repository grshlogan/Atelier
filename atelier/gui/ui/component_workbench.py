from __future__ import annotations

import argparse
import json
import time
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
    render_review_page_html,
)
from atelier.gui.ui.workflow_canvas.node_cards.video_input_card import VideoInputCardCandidate
from atelier.gui.ui.workflow_canvas.node_cards.video_input_vector_card import (
    COLLAPSED_CARD_HEIGHT,
    COLLAPSED_CARD_WIDTH,
    VideoInputCollapsedNodeCardItem,
)

ensure_gui_dependency()

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QBrush, QFont, QKeySequence, QPainter, QPen, QPixmap, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsScene,
    QGraphicsView,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


@dataclass(frozen=True)
class ReviewSnapshotResult:
    story_id: str
    screenshot_path: Path
    metadata_path: Path
    review_page_path: Path


# 控件画板默认启动窗口尺寸。
COMPONENT_WORKBENCH_DEFAULT_WIDTH = 1980
COMPONENT_WORKBENCH_DEFAULT_HEIGHT = 1080
WORKCANVAS_PERF_HUD_REFRESH_MS = 250

# WorkCanvas 缩放范围与步进。
WORKCANVAS_ZOOM_MIN = 0.25
WORKCANVAS_ZOOM_MAX = 4.0
WORKCANVAS_ZOOM_STEP_BUTTON = 0.25
WORKCANVAS_ZOOM_STEP_WHEEL = 1.15  # 滚轮一次缩放的乘法系数

# WorkCanvas 网格背景参数。
WORKCANVAS_BACKGROUND_COLOR = QColor("#08111E")
WORKCANVAS_GRID_SPACING = 24
WORKCANVAS_GRID_MAJOR_EVERY = 4
WORKCANVAS_GRID_MINOR_COLOR = QColor(42, 58, 80, 72)
WORKCANVAS_GRID_MAJOR_COLOR = QColor(59, 130, 246, 56)
WORKCANVAS_GRID_DOT_COLOR = QColor(116, 147, 190, 140)
WORKCANVAS_GRID_MIN_MINOR_SPACING_PX = 8.0
WORKCANVAS_GRID_MIN_MAJOR_SPACING_PX = 16.0
WORKCANVAS_GRID_MIN_DOT_SPACING_PX = 16.0
WORKCANVAS_GRID_TILE_CACHE_LIMIT = 12
WORKCANVAS_VIEWPORT_UPDATE_MODES = {
    "minimal": QGraphicsView.ViewportUpdateMode.MinimalViewportUpdate,
    "bounding": QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate,
    "full": QGraphicsView.ViewportUpdateMode.FullViewportUpdate,
}


@dataclass(frozen=True)
class WorkCanvasGridLod:
    minor_spacing_px: float
    major_spacing_px: float
    draw_minor: bool
    draw_dots: bool
    tile_size_px: int


class _WorkCanvasView(QGraphicsView):
    """WorkCanvas 预览的 QGraphicsView 子类，承载滚轮缩放、ESC 退出全屏和网格背景。"""

    def __init__(
        self,
        scene: QGraphicsScene,
        *,
        on_zoom_changed,
        on_exit_fullscreen=None,
        parent=None,
    ) -> None:
        super().__init__(scene, parent)
        self._scene_ref = scene
        self._on_zoom_changed = on_zoom_changed
        self._on_exit_fullscreen = on_exit_fullscreen
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setInteractive(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setBackgroundBrush(WORKCANVAS_BACKGROUND_COLOR)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.MinimalViewportUpdate)
        self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, True)
        self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontSavePainterState, True)
        self.setProperty("debug_perf", False)
        self.setProperty("viewport_update_mode", "minimal")
        self.setProperty("grid_render_space", "viewport")
        self.setProperty("grid_lod_strategy", "adaptive-screen-space")
        self.setProperty("grid_paint_strategy", "cached-tile-brush")
        self.setProperty("grid_full_viewport_primitive_loop", False)
        self.setProperty("grid_min_minor_spacing_px", WORKCANVAS_GRID_MIN_MINOR_SPACING_PX)
        self.setProperty("grid_min_major_spacing_px", WORKCANVAS_GRID_MIN_MAJOR_SPACING_PX)
        self.setProperty("grid_min_dot_spacing_px", WORKCANVAS_GRID_MIN_DOT_SPACING_PX)
        self.setProperty("grid_tile_cache_limit", WORKCANVAS_GRID_TILE_CACHE_LIMIT)
        self._grid_tile_cache: dict[tuple[int, int, bool, bool], QPixmap] = {}
        self._debug_perf = False
        self._last_draw_background_ms = 0.0
        self._tile_cache_hits = 0
        self._tile_cache_misses = 0
        self._last_tile_key: tuple[int, int, bool, bool] | None = None
        self._last_zoom = 1.0
        self._last_background_antialiasing = False
        self._initial_centered = False

    def set_debug_perf(self, enabled: bool) -> None:
        self._debug_perf = bool(enabled)
        self.setProperty("debug_perf", self._debug_perf)

    def debug_perf_snapshot(self) -> dict[str, object]:
        return {
            "debug_perf": self._debug_perf,
            "draw_background_ms": self._last_draw_background_ms,
            "tile_cache_hits": self._tile_cache_hits,
            "tile_cache_misses": self._tile_cache_misses,
            "tile_key": self._last_tile_key,
            "zoom": self._last_zoom,
            "viewport_update_mode": self.property("viewport_update_mode"),
            "background_antialiasing": self._last_background_antialiasing,
        }

    def set_viewport_update_mode_name(self, mode_name: str) -> None:
        try:
            mode = WORKCANVAS_VIEWPORT_UPDATE_MODES[mode_name]
        except KeyError as exc:
            raise ValueError(f"未知 WorkCanvas viewport update mode: {mode_name}") from exc
        self.setViewportUpdateMode(mode)
        self.setProperty("viewport_update_mode", mode_name)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        if not self._initial_centered:
            self.centerOn(0, 0)
            self._initial_centered = True

    def grid_lod_for_scale(self, scale: float) -> WorkCanvasGridLod:
        safe_scale = max(0.01, abs(scale))
        minor_spacing = WORKCANVAS_GRID_SPACING * safe_scale
        major_spacing = minor_spacing * WORKCANVAS_GRID_MAJOR_EVERY
        while major_spacing < WORKCANVAS_GRID_MIN_MAJOR_SPACING_PX:
            major_spacing *= WORKCANVAS_GRID_MAJOR_EVERY
        return WorkCanvasGridLod(
            minor_spacing_px=minor_spacing,
            major_spacing_px=major_spacing,
            draw_minor=minor_spacing >= WORKCANVAS_GRID_MIN_MINOR_SPACING_PX,
            draw_dots=minor_spacing >= WORKCANVAS_GRID_MIN_DOT_SPACING_PX,
            tile_size_px=max(1, int(round(major_spacing))),
        )

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:  # noqa: N802
        del rect
        started_at = time.perf_counter() if self._debug_perf else 0.0
        painter.save()
        try:
            painter.resetTransform()
            viewport_rect = self.viewport().rect()
            painter.fillRect(viewport_rect, WORKCANVAS_BACKGROUND_COLOR)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            self._last_background_antialiasing = painter.testRenderHint(
                QPainter.RenderHint.Antialiasing
            )

            scale = self.transform().m11()
            self._last_zoom = scale
            origin = self.mapFromScene(QPointF(0.0, 0.0))
            tile = self.grid_tile_for_scale(scale)
            painter.setBrushOrigin(origin)
            painter.fillRect(viewport_rect, QBrush(tile))
        finally:
            painter.restore()
            if self._debug_perf:
                self._last_draw_background_ms = (time.perf_counter() - started_at) * 1000.0

    def grid_tile_cache_size(self) -> int:
        return len(self._grid_tile_cache)

    def grid_tile_for_scale(self, scale: float) -> QPixmap:
        self._last_zoom = scale
        return self._grid_tile_for_lod(self.grid_lod_for_scale(scale))

    def _grid_tile_cache_key(self, lod: WorkCanvasGridLod) -> tuple[int, int, bool, bool]:
        minor_spacing = max(1, int(round(lod.minor_spacing_px))) if lod.draw_minor else 0
        return (lod.tile_size_px, minor_spacing, lod.draw_minor, lod.draw_dots)

    def _grid_tile_for_lod(self, lod: WorkCanvasGridLod) -> QPixmap:
        key = self._grid_tile_cache_key(lod)
        self._last_tile_key = key
        cached = self._grid_tile_cache.get(key)
        if cached is not None:
            self._tile_cache_hits += 1
            return cached
        self._tile_cache_misses += 1
        if len(self._grid_tile_cache) >= WORKCANVAS_GRID_TILE_CACHE_LIMIT:
            self._grid_tile_cache.clear()
        tile = self._build_grid_tile(lod)
        self._grid_tile_cache[key] = tile
        return tile

    def _build_grid_tile(self, lod: WorkCanvasGridLod) -> QPixmap:
        tile_size = max(1, lod.tile_size_px)
        tile = QPixmap(tile_size, tile_size)
        tile.fill(Qt.GlobalColor.transparent)

        painter = QPainter(tile)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            if lod.draw_minor:
                minor_spacing = max(1, int(round(lod.minor_spacing_px)))
                painter.setPen(QPen(WORKCANVAS_GRID_MINOR_COLOR, 1))
                x = 0
                while x < tile_size:
                    painter.drawLine(x, 0, x, tile_size)
                    x += minor_spacing
                y = 0
                while y < tile_size:
                    painter.drawLine(0, y, tile_size, y)
                    y += minor_spacing

            painter.setPen(QPen(WORKCANVAS_GRID_MAJOR_COLOR, 1))
            painter.drawLine(0, 0, 0, tile_size)
            painter.drawLine(0, 0, tile_size, 0)

            if lod.draw_dots:
                minor_spacing = max(1, int(round(lod.minor_spacing_px)))
                painter.setPen(QPen(WORKCANVAS_GRID_DOT_COLOR, 1))
                x = 0
                while x < tile_size:
                    y = 0
                    while y < tile_size:
                        painter.drawPoint(x, y)
                        y += minor_spacing
                    x += minor_spacing
        finally:
            painter.end()
        return tile

    def wheelEvent(self, event) -> None:  # noqa: N802
        delta = event.angleDelta().y()
        if delta == 0:
            event.ignore()
            return
        factor = WORKCANVAS_ZOOM_STEP_WHEEL if delta > 0 else 1.0 / WORKCANVAS_ZOOM_STEP_WHEEL
        current = self.transform().m11()
        target = max(WORKCANVAS_ZOOM_MIN, min(WORKCANVAS_ZOOM_MAX, current * factor))
        if abs(target - current) < 1e-4:
            event.accept()
            return
        self.resetTransform()
        self.scale(target, target)
        if self._on_zoom_changed is not None:
            self._on_zoom_changed(target)
        event.accept()

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape and self._on_exit_fullscreen is not None:
            self._on_exit_fullscreen()
            event.accept()
            return
        super().keyPressEvent(event)


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
        self._video_input_card: VideoInputCardCandidate | None = None
        self._video_input_vector_preview: QGraphicsView | None = None
        self._video_input_vector_item: VideoInputCollapsedNodeCardItem | None = None
        self._workcanvas_perf_hud: QLabel | None = None
        self._active_card_entry = "vector-collapsed"
        self._workcanvas_fullscreen_window: QMainWindow | None = None
        self._workcanvas_fullscreen_view: QGraphicsView | None = None
        self._workcanvas_fullscreen_item: VideoInputCollapsedNodeCardItem | None = None
        self._workcanvas_fullscreen_zoom_label: QLabel | None = None
        self._workcanvas_fullscreen_perf_hud: QLabel | None = None
        self._workcanvas_zoom_label: QLabel | None = None
        self._workcanvas_zoom_scale = 1.0
        self._workcanvas_perf_timer: QTimer | None = None
        self._review_note: QTextEdit | None = None
        self._review_page_path_label: QLabel | None = None
        self.setObjectName("atelier-ui-component-workbench")
        self.setWindowTitle(self._state.window_title)
        self.resize(COMPONENT_WORKBENCH_DEFAULT_WIDTH, COMPONENT_WORKBENCH_DEFAULT_HEIGHT)
        self.setCentralWidget(self._build_root())
        self._workcanvas_perf_timer = QTimer(self)
        self._workcanvas_perf_timer.setInterval(WORKCANVAS_PERF_HUD_REFRESH_MS)
        self._workcanvas_perf_timer.timeout.connect(self.refresh_workcanvas_perf_hud)
        self._workcanvas_perf_timer.start()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._apply_default_launch_geometry()

    def _apply_default_launch_geometry(self) -> None:
        self.resize(COMPONENT_WORKBENCH_DEFAULT_WIDTH, COMPONENT_WORKBENCH_DEFAULT_HEIGHT)
        screen = self.screen() or QApplication.primaryScreen()
        if screen is None:
            return
        frame = self.frameGeometry()
        frame.moveCenter(screen.availableGeometry().center())
        self.move(frame.topLeft())

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

    def _build_preview(self) -> QWidget:
        content = QWidget()
        content.setObjectName("component-workbench-preview")
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
        layout.addWidget(self._build_workcanvas_preview_area(), 1)
        layout.addStretch(1)

        return content

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

    def _build_video_input_card_candidate(self) -> VideoInputCardCandidate:
        card = VideoInputCardCandidate()
        card.setVisible(
            self._selected_story_id == "video-input-card"
            and self._active_card_entry == "legacy-expanded"
        )
        self._video_input_card = card
        return card

    def _build_workcanvas_preview_area(self) -> QWidget:
        area = _WorkCanvasPreviewSurface()
        area.setObjectName("component-workbench-workcanvas-preview")
        area.setProperty("surface_role", "dev-workcanvas-preview")
        area.setProperty("rendering_route", "workcanvas-vector-target")
        area.setProperty("thumbnail_policy", "cached-preview-artifact-only")
        area.setProperty("gui_runtime_boundary", "no-worker-no-ffmpeg-no-thumbnail-generation")
        area.setProperty("reference_model", "comfyui-preview-cache-not-free-graph")
        area.setProperty("outer_scroll_policy", "none-canvas-handles-pan")
        area.setProperty("grid_pattern", "line-and-dot-grid")
        area.setProperty("grid_spacing_px", WORKCANVAS_GRID_SPACING)
        area.setProperty("major_grid_every", WORKCANVAS_GRID_MAJOR_EVERY)

        layout = QVBoxLayout(area)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(8)

        title = QLabel("WorkCanvas 预览区")
        title.setObjectName("component-workbench-workcanvas-preview-title")
        title_font = title.font()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #F3F7FB; background: transparent;")
        layout.addWidget(title)

        policy = QLabel("缩略图只读取缓存预览，不生成缩略图，不执行 workflow。")
        policy.setObjectName("component-workbench-workcanvas-preview-policy")
        policy.setWordWrap(True)
        policy.setStyleSheet("color: #9FB3C8; background: transparent;")
        layout.addWidget(policy)
        layout.addWidget(self._build_workcanvas_card_entry_controls())
        layout.addWidget(self._build_workcanvas_zoom_controls())
        layout.addWidget(self._build_workcanvas_perf_hud())

        stage = QFrame()
        stage.setObjectName("component-workbench-workcanvas-stage")
        stage.setProperty("layout_model", "canvas-fill-area")
        stage.setProperty("controls_visibility", "nonfullscreen-visible")
        stage.setMinimumHeight(360)
        stage.setStyleSheet("background: transparent; border: none;")
        stage_layout = QVBoxLayout(stage)
        stage_layout.setContentsMargins(0, 0, 0, 0)
        stage_layout.setSpacing(0)
        stage_layout.addWidget(self._build_video_input_vector_preview())
        stage_layout.addWidget(
            self._build_video_input_card_candidate(),
            alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
        )
        layout.addWidget(stage, 1)
        return area

    def _build_workcanvas_card_entry_controls(self) -> QWidget:
        controls = QWidget()
        controls.setObjectName("component-workbench-card-entry-controls")
        controls.setProperty("control_role", "workcanvas-card-entry")
        layout = QHBoxLayout(controls)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        vector_entry = QPushButton("矢量内缩")
        vector_entry.setObjectName("component-workbench-card-entry-vector-collapsed")
        vector_entry.clicked.connect(lambda: self._set_workcanvas_card_entry("vector-collapsed"))
        legacy_entry = QPushButton("旧版展开参考")
        legacy_entry.setObjectName("component-workbench-card-entry-legacy-expanded")
        legacy_entry.clicked.connect(lambda: self._set_workcanvas_card_entry("legacy-expanded"))

        layout.addWidget(QLabel("卡片："))
        layout.addWidget(vector_entry)
        layout.addWidget(legacy_entry)
        layout.addStretch(1)
        return controls

    def _build_workcanvas_zoom_controls(self) -> QWidget:
        controls = QWidget()
        controls.setObjectName("component-workbench-workcanvas-zoom-controls")
        controls.setProperty("control_role", "workcanvas-basic-zoom")
        layout = QHBoxLayout(controls)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        label = QLabel("100%")
        label.setObjectName("component-workbench-workcanvas-zoom-label")
        label.setMinimumWidth(44)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #F3F7FB; background: transparent;")
        self._workcanvas_zoom_label = label

        zoom_out = QPushButton("-")
        zoom_out.setObjectName("component-workbench-workcanvas-zoom-out")
        zoom_out.clicked.connect(lambda: self._zoom_workcanvas_preview_by(-0.25))
        zoom_reset = QPushButton("100%")
        zoom_reset.setObjectName("component-workbench-workcanvas-zoom-reset")
        zoom_reset.clicked.connect(lambda: self._set_workcanvas_zoom_scale(1.0))
        zoom_in = QPushButton("+")
        zoom_in.setObjectName("component-workbench-workcanvas-zoom-in")
        zoom_in.clicked.connect(lambda: self._zoom_workcanvas_preview_by(0.25))
        fullscreen = QPushButton("全屏")
        fullscreen.setObjectName("component-workbench-workcanvas-fullscreen")
        fullscreen.clicked.connect(self._open_workcanvas_fullscreen)

        layout.addWidget(QLabel("缩放："))
        layout.addWidget(label)
        layout.addWidget(zoom_out)
        layout.addWidget(zoom_reset)
        layout.addWidget(zoom_in)
        layout.addWidget(fullscreen)
        layout.addStretch(1)
        return controls

    def _build_workcanvas_perf_hud(self) -> QLabel:
        hud = QLabel("性能 HUD：等待绘制")
        hud.setObjectName("component-workbench-workcanvas-perf-hud")
        hud.setProperty("surface_role", "workcanvas-dev-perf-hud")
        hud.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        hud.setWordWrap(True)
        hud.setStyleSheet(
            """
            QLabel#component-workbench-workcanvas-perf-hud {
              background: rgba(8, 17, 30, 210);
              color: #CDE4FF;
              border: 1px solid rgba(59, 130, 246, 130);
              border-radius: 8px;
              padding: 6px 8px;
              font-family: "Consolas", "Microsoft YaHei UI", monospace;
            }
            """
        )
        self._workcanvas_perf_hud = hud
        return hud

    def _build_video_input_vector_preview(self) -> QGraphicsView:
        scene = QGraphicsScene(self)
        item = VideoInputCollapsedNodeCardItem()
        item.set_debug_perf(True)
        scene.addItem(item)
        item.setPos(-COLLAPSED_CARD_WIDTH / 2, -COLLAPSED_CARD_HEIGHT / 2)
        scene.setSceneRect(-2000, -2000, 4000, 4000)
        self._video_input_vector_item = item

        preview = _WorkCanvasView(
            scene,
            on_zoom_changed=self._handle_view_zoom_changed,
        )
        preview.set_debug_perf(True)
        preview.setObjectName("component-workbench-video-input-vector-preview")
        preview.setProperty("item_route", "qgraphicsitem-paint")
        preview.setProperty("display_mode", "collapsed")
        preview.setProperty("thumbnail_strategy", "cached-preview-or-vector-fallback")
        preview.setProperty("gui_runtime_boundary", "draw-only-no-thumbnail-generation")
        preview.setProperty("pan_interaction", "mouse-drag")
        preview.setProperty("zoom_min", WORKCANVAS_ZOOM_MIN)
        preview.setProperty("zoom_max", WORKCANVAS_ZOOM_MAX)
        preview.setProperty("zoom_step", WORKCANVAS_ZOOM_STEP_BUTTON)
        preview.setSceneRect(scene.sceneRect())
        preview.setMinimumSize(480, 320)
        preview.setStyleSheet(
            """
            QGraphicsView#component-workbench-video-input-vector-preview {
              background: #08111E;
              border: 1px solid rgba(42, 58, 80, 120);
              border-radius: 8px;
            }
            """
        )
        preview.setVisible(
            self._selected_story_id == "video-input-card"
            and self._active_card_entry == "vector-collapsed"
        )
        preview.centerOn(0, 0)
        self._video_input_vector_preview = preview
        self._apply_workcanvas_zoom_scale()
        self.refresh_workcanvas_perf_hud()
        return preview

    def _set_workcanvas_card_entry(self, entry_id: str) -> None:
        self._active_card_entry = entry_id
        self._sync_workcanvas_card_entry_visibility()

    def _sync_workcanvas_card_entry_visibility(self) -> None:
        show_video_story = self._selected_story_id == "video-input-card"
        if self._video_input_vector_preview is not None:
            self._video_input_vector_preview.setVisible(
                show_video_story and self._active_card_entry == "vector-collapsed"
            )
        if self._video_input_card is not None:
            self._video_input_card.setVisible(
                show_video_story and self._active_card_entry == "legacy-expanded"
            )

    def _open_workcanvas_fullscreen(self) -> None:
        if self._workcanvas_fullscreen_window is not None:
            self._close_workcanvas_fullscreen()
            return

        window = QMainWindow(self)
        window.setObjectName("component-workbench-workcanvas-fullscreen-window")
        window.setWindowTitle("WorkCanvas 预览区 — 全屏")
        window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

        scene = QGraphicsScene(window)
        item = VideoInputCollapsedNodeCardItem()
        item.set_debug_perf(True)
        scene.addItem(item)
        item.setPos(-COLLAPSED_CARD_WIDTH / 2, -COLLAPSED_CARD_HEIGHT / 2)
        scene.setSceneRect(-4000, -4000, 8000, 8000)

        view = _WorkCanvasView(
            scene,
            on_zoom_changed=self._handle_view_zoom_changed,
            on_exit_fullscreen=self._close_workcanvas_fullscreen,
        )
        view.set_debug_perf(True)
        view.setObjectName("component-workbench-video-input-vector-preview-fullscreen")
        view.setProperty("item_route", "qgraphicsitem-paint")
        view.setProperty("display_mode", "collapsed")
        view.setProperty("thumbnail_strategy", "cached-preview-or-vector-fallback")
        view.setProperty("pan_interaction", "mouse-drag")
        view.setSceneRect(scene.sceneRect())
        view.setStyleSheet("QGraphicsView { background: #08111E; border: none; }")
        view.scale(self._workcanvas_zoom_scale, self._workcanvas_zoom_scale)
        view.centerOn(0, 0)
        window.setCentralWidget(view)

        toolbar = self._build_fullscreen_workcanvas_toolbar(view)
        perf_hud = self._build_fullscreen_workcanvas_perf_hud(view)

        # 浮动退出按钮
        exit_button = QPushButton("退出全屏 (Esc)", view)
        exit_button.setObjectName("component-workbench-workcanvas-fullscreen-exit")
        exit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_button.setStyleSheet(
            """
            QPushButton#component-workbench-workcanvas-fullscreen-exit {
              background: rgba(20, 32, 50, 220);
              color: #F3F7FB;
              border: 1px solid rgba(59, 130, 246, 140);
              border-radius: 8px;
              padding: 6px 12px;
            }
            QPushButton#component-workbench-workcanvas-fullscreen-exit:hover {
              background: rgba(40, 60, 90, 235);
            }
            """
        )
        exit_button.clicked.connect(self._close_workcanvas_fullscreen)
        exit_button.adjustSize()
        for overlay in (toolbar, perf_hud, exit_button):
            overlay.raise_()
            overlay.show()

        # ESC 全局快捷键，避免 view 焦点丢失时退不出来
        shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), window)
        shortcut.activated.connect(self._close_workcanvas_fullscreen)

        window.closeEvent = self._make_fullscreen_close_event(window.closeEvent)
        window.resizeEvent = self._make_fullscreen_resize_event(
            view,
            toolbar,
            perf_hud,
            exit_button,
            window.resizeEvent,
        )

        self._workcanvas_fullscreen_window = window
        self._workcanvas_fullscreen_view = view
        self._workcanvas_fullscreen_item = item
        self._sync_zoom_label()
        self.refresh_workcanvas_perf_hud()
        view.setFocus()
        window.showFullScreen()
        self._position_fullscreen_overlays(view, toolbar, perf_hud, exit_button)

    def _build_fullscreen_workcanvas_toolbar(self, parent: QWidget) -> QWidget:
        toolbar = QWidget(parent)
        toolbar.setObjectName("component-workbench-workcanvas-fullscreen-toolbar")
        toolbar.setProperty("surface_role", "workcanvas-fullscreen-controls")
        toolbar.setStyleSheet(
            """
            QWidget#component-workbench-workcanvas-fullscreen-toolbar {
              background: rgba(8, 17, 30, 220);
              border: 1px solid rgba(59, 130, 246, 130);
              border-radius: 8px;
            }
            """
        )
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)

        title = QLabel("WorkCanvas 预览区")
        title.setStyleSheet("color: #F3F7FB; background: transparent; font-weight: 650;")
        label = QLabel(f"{round(self._workcanvas_zoom_scale * 100):d}%")
        label.setObjectName("component-workbench-workcanvas-fullscreen-zoom-label")
        label.setMinimumWidth(44)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #F3F7FB; background: transparent;")
        self._workcanvas_fullscreen_zoom_label = label

        zoom_out = QPushButton("-")
        zoom_out.setObjectName("component-workbench-workcanvas-fullscreen-zoom-out")
        zoom_out.clicked.connect(lambda: self._zoom_workcanvas_preview_by(-0.25))
        zoom_reset = QPushButton("100%")
        zoom_reset.setObjectName("component-workbench-workcanvas-fullscreen-zoom-reset")
        zoom_reset.clicked.connect(lambda: self._set_workcanvas_zoom_scale(1.0))
        zoom_in = QPushButton("+")
        zoom_in.setObjectName("component-workbench-workcanvas-fullscreen-zoom-in")
        zoom_in.clicked.connect(lambda: self._zoom_workcanvas_preview_by(0.25))
        for button in (zoom_out, zoom_reset, zoom_in):
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet(
                """
                QPushButton {
                  min-width: 72px;
                  background: rgba(205, 228, 255, 225);
                  color: #08111E;
                  border: none;
                  border-radius: 5px;
                  padding: 4px 10px;
                }
                QPushButton:hover {
                  background: rgba(243, 247, 251, 240);
                }
                """
            )

        layout.addWidget(title)
        layout.addSpacing(16)
        layout.addWidget(QLabel("缩放："))
        layout.addWidget(label)
        layout.addWidget(zoom_out)
        layout.addWidget(zoom_reset)
        layout.addWidget(zoom_in)
        toolbar.adjustSize()
        return toolbar

    def _build_fullscreen_workcanvas_perf_hud(self, parent: QWidget) -> QLabel:
        hud = QLabel("性能 HUD：等待绘制", parent)
        hud.setObjectName("component-workbench-workcanvas-perf-hud-fullscreen")
        hud.setProperty("surface_role", "workcanvas-dev-perf-hud")
        hud.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        hud.setWordWrap(False)
        hud.setStyleSheet(
            """
            QLabel#component-workbench-workcanvas-perf-hud-fullscreen {
              background: rgba(8, 17, 30, 220);
              color: #CDE4FF;
              border: 1px solid rgba(59, 130, 246, 130);
              border-radius: 8px;
              padding: 6px 8px;
              font-family: "Consolas", "Microsoft YaHei UI", monospace;
            }
            """
        )
        hud.adjustSize()
        self._workcanvas_fullscreen_perf_hud = hud
        return hud

    def _make_fullscreen_close_event(self, original_close_event):
        def handler(event) -> None:
            self._workcanvas_fullscreen_window = None
            self._workcanvas_fullscreen_view = None
            self._workcanvas_fullscreen_item = None
            self._workcanvas_fullscreen_zoom_label = None
            self._workcanvas_fullscreen_perf_hud = None
            if original_close_event is not None:
                original_close_event(event)
            else:
                event.accept()
        return handler

    def _make_fullscreen_resize_event(
        self,
        view: QGraphicsView,
        toolbar: QWidget,
        hud: QLabel,
        button: QPushButton,
        original_resize_event,
    ):
        def handler(event) -> None:
            if original_resize_event is not None:
                original_resize_event(event)
            else:
                event.accept()
            self._position_fullscreen_overlays(view, toolbar, hud, button)
        return handler

    def _position_fullscreen_overlays(
        self,
        view: QGraphicsView,
        toolbar: QWidget,
        hud: QLabel,
        button: QPushButton,
    ) -> None:
        toolbar.adjustSize()
        hud.adjustSize()
        button.adjustSize()
        hud.setFixedSize(max(420, view.width() - 32), max(30, hud.sizeHint().height()))
        toolbar.move(16, 16)
        hud.move(16, toolbar.y() + toolbar.height() + 8)
        button.move(max(16, view.width() - button.width() - 16), 16)

    def _close_workcanvas_fullscreen(self) -> None:
        window = self._workcanvas_fullscreen_window
        if window is None:
            return
        self._workcanvas_fullscreen_window = None
        self._workcanvas_fullscreen_view = None
        self._workcanvas_fullscreen_item = None
        self._workcanvas_fullscreen_zoom_label = None
        self._workcanvas_fullscreen_perf_hud = None
        window.close()

    def _handle_view_zoom_changed(self, scale: float) -> None:
        self._workcanvas_zoom_scale = max(WORKCANVAS_ZOOM_MIN, min(WORKCANVAS_ZOOM_MAX, scale))
        self._sync_zoom_label()

    def _sync_zoom_label(self) -> None:
        if self._workcanvas_zoom_label is not None:
            self._workcanvas_zoom_label.setText(f"{round(self._workcanvas_zoom_scale * 100):d}%")
        if self._workcanvas_fullscreen_zoom_label is not None:
            self._workcanvas_fullscreen_zoom_label.setText(
                f"{round(self._workcanvas_zoom_scale * 100):d}%"
            )
        self.refresh_workcanvas_perf_hud()

    def _zoom_workcanvas_preview_by(self, delta: float) -> None:
        self._set_workcanvas_zoom_scale(self._workcanvas_zoom_scale + delta)

    def _set_workcanvas_zoom_scale(self, scale: float) -> None:
        self._workcanvas_zoom_scale = min(WORKCANVAS_ZOOM_MAX, max(WORKCANVAS_ZOOM_MIN, scale))
        self._apply_workcanvas_zoom_scale()
        self._sync_zoom_label()

    def _apply_workcanvas_zoom_scale(self) -> None:
        if self._video_input_vector_preview is not None:
            self._video_input_vector_preview.resetTransform()
            self._video_input_vector_preview.scale(
                self._workcanvas_zoom_scale,
                self._workcanvas_zoom_scale,
            )
        if self._workcanvas_fullscreen_view is not None:
            self._workcanvas_fullscreen_view.resetTransform()
            self._workcanvas_fullscreen_view.scale(
                self._workcanvas_zoom_scale,
                self._workcanvas_zoom_scale,
            )
        self.refresh_workcanvas_perf_hud()

    def refresh_workcanvas_perf_hud(self) -> None:
        if self._workcanvas_perf_hud is not None and self._video_input_vector_preview is not None:
            self._workcanvas_perf_hud.setText(
                self._format_workcanvas_perf_text(
                    self._video_input_vector_preview,
                    self._video_input_vector_item,
                )
            )
        if self._workcanvas_fullscreen_perf_hud is not None and self._workcanvas_fullscreen_view is not None:
            self._workcanvas_fullscreen_perf_hud.setText(
                self._format_workcanvas_perf_text(
                    self._workcanvas_fullscreen_view,
                    self._workcanvas_fullscreen_item,
                )
            )

    def _format_workcanvas_perf_text(
        self,
        view: _WorkCanvasView,
        item: VideoInputCollapsedNodeCardItem | None,
    ) -> str:
        view_snapshot = view.debug_perf_snapshot()
        item_snapshot = item.debug_perf_snapshot() if item is not None else {}
        zoom_percent = round(float(view_snapshot.get("zoom", view.transform().m11())) * 100)
        tile_key = view_snapshot.get("tile_key")
        tile_key_text = "-" if tile_key is None else str(tile_key)
        bg_aa = "on" if view_snapshot.get("background_antialiasing") else "off"
        node_aa = "on" if item_snapshot.get("antialiasing") else "off"
        background_time = self._format_ms_with_fps(
            float(view_snapshot.get("draw_background_ms", 0.0))
        )
        node_time = self._format_ms_with_fps(float(item_snapshot.get("paint_ms", 0.0)))
        return (
            f"性能 HUD | 缩放 {zoom_percent}% | "
            f"背景 {background_time} | "
            f"tile 命中 {view_snapshot.get('tile_cache_hits', 0)}/"
            f"{view_snapshot.get('tile_cache_misses', 0)} | "
            f"key {tile_key_text} | "
            f"update {view_snapshot.get('viewport_update_mode', 'minimal')} | "
            f"AA 背景 {bg_aa} / 节点 {node_aa} | "
            f"节点 {node_time}"
        )

    def _format_ms_with_fps(self, elapsed_ms: float) -> str:
        if elapsed_ms <= 0.0:
            return f"{elapsed_ms:.2f} ms / -- fps"
        return f"{elapsed_ms:.2f} ms / {round(1000.0 / elapsed_ms):d} fps"

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
        review_page_path = QLabel("Review page：尚未生成")
        review_page_path.setObjectName("component-workbench-review-page-path")
        review_page_path.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        review_page_path.setWordWrap(True)
        layout.addWidget(review_page_path)
        self._review_page_path_label = review_page_path
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
        self._sync_workcanvas_card_entry_visibility()

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
        review_page_filename = f"{safe_story_id}-{stamp}.html"
        screenshot_path = self._review_output_dir / screenshot_filename
        metadata_path = self._review_output_dir / metadata_filename
        review_page_path = self._review_output_dir / review_page_filename

        pixmap = self.grab()
        pixmap.save(str(screenshot_path), "PNG")

        note = self._review_note.toPlainText().strip() if self._review_note is not None else ""
        record = build_review_snapshot_record(
            state=self._state,
            story_id=story.story_id,
            reviewer_note=note,
            screenshot_filename=screenshot_filename,
            metadata_filename=metadata_filename,
            review_page_filename=review_page_filename,
        )
        metadata_path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        review_page_path.write_text(
            render_review_page_html(record),
            encoding="utf-8",
        )
        if self._review_page_path_label is not None:
            self._review_page_path_label.setText(f"Review page：{review_page_filename}")
        return ReviewSnapshotResult(
            story_id=story.story_id,
            screenshot_path=screenshot_path,
            metadata_path=metadata_path,
            review_page_path=review_page_path,
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


class _WorkCanvasPreviewSurface(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(420)
        self.setStyleSheet(
            "QFrame { background: #08111E; border: 1px solid #2A3A50; border-radius: 8px; }"
        )


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
