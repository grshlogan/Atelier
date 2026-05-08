from __future__ import annotations

import time
from dataclasses import dataclass

from atelier.gui.entry import ensure_gui_dependency
from atelier.gui.ui.font_assets import load_atelier_ui_font_families

ensure_gui_dependency()

from PySide6.QtCore import QEasingCurve, QPointF, QRectF, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QFont, QFontMetrics, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsObject, QStyleOptionGraphicsItem, QWidget


# 内缩态卡片宽度，保持 WorkCanvas 轻节点尺寸。
COLLAPSED_CARD_WIDTH = 300
# 内缩态卡片高度，首版只容纳标题、状态和摘要指标。
COLLAPSED_CARD_HEIGHT = 200
# 卡片圆角半径。
CARD_RADIUS = 16
# 选中态卡片外边框宽度。
CARD_BORDER_WIDTH = 3
# 非选中态卡片外边框宽度。
CARD_RESTING_BORDER_WIDTH = 1
# 选中态卡片外边框颜色。
CARD_SELECTED_BORDER_COLOR = "#3B82F6"
# 非选中态卡片外边框颜色。
CARD_RESTING_BORDER_COLOR = "#2A3A50"
# 选中态蓝色辉光宽度。
CARD_SELECTED_GLOW_WIDTH = 10
# 选中态蓝色辉光颜色。
CARD_SELECTED_GLOW_COLOR = "#3B82F6"
# 卡片背景渐变顶部颜色。
CARD_BACKGROUND_TOP_COLOR = "#182A3D"
# 卡片背景渐变中部颜色。
CARD_BACKGROUND_MID_COLOR = "#111D2C"
# 卡片背景渐变底部颜色。
CARD_BACKGROUND_BOTTOM_COLOR = "#0B1524"
# 顶部标题区高度。
HEADER_HEIGHT = 56
# 卡片内容左右内边距。
CONTENT_MARGIN_X = 20
# 顶部分割线左端点，使用内容内边距而不是贴住边框。
HEADER_DIVIDER_LEFT_X = CONTENT_MARGIN_X
# 顶部分割线右端点，和左端保持对称内缩。
HEADER_DIVIDER_RIGHT_X = COLLAPSED_CARD_WIDTH - CONTENT_MARGIN_X
# 状态胶囊左右内边距。
STATUS_CAPSULE_PADDING_X = 12
# 状态胶囊高度。
STATUS_CAPSULE_HEIGHT = 28
# 状态胶囊圆角半径。
STATUS_CAPSULE_RADIUS = 14
# 标题图标尺寸。
TITLE_ICON_SIZE = 32
# 视频图标左侧胶片竖线相对 X。
VIDEO_ICON_LEFT_REEL_OFFSET_X = 9
# 视频图标右侧胶片竖线相对 X。
VIDEO_ICON_RIGHT_REEL_OFFSET_X = 23
# 视频图标播放三角形左侧相对 X。
VIDEO_ICON_PLAY_LEFT_OFFSET_X = 12
# 视频图标播放三角形右侧相对 X。
VIDEO_ICON_PLAY_RIGHT_OFFSET_X = 21
# 视频图标播放三角形上端相对 Y。
VIDEO_ICON_PLAY_TOP_OFFSET_Y = 10
# 视频图标播放三角形下端相对 Y。
VIDEO_ICON_PLAY_BOTTOM_OFFSET_Y = 22
# 标题文字字号，使用 Qt point size。
TITLE_TEXT_PT = 13
# 状态文字字号，使用 Qt point size。
STATUS_TEXT_PT = 14
# 红框标注文字的字重。
REVIEW_RED_TEXT_WEIGHT = QFont.Weight.Normal
# 黄色标注状态文字的字重。
REVIEW_YELLOW_STATUS_WEIGHT = QFont.Weight.Medium
# 主指标标题字号。
PRIMARY_LABEL_PT = 11
# 主指标数字字号。
PRIMARY_VALUE_PT = 32
# 主指标标题绘制矩形的 Y 坐标。
PRIMARY_LABEL_RECT_Y = 72
# 主指标数字绘制矩形的 Y 坐标。
PRIMARY_VALUE_RECT_Y = 84
# 底部摘要分割线 Y 坐标。
SUMMARY_DIVIDER_Y = 145
# 底部摘要分割线左端点，和顶部分割线保持一致。
SUMMARY_DIVIDER_LEFT_X = HEADER_DIVIDER_LEFT_X
# 底部摘要分割线右端点，和顶部分割线保持一致。
SUMMARY_DIVIDER_RIGHT_X = HEADER_DIVIDER_RIGHT_X
# 底部摘要标题字号。
SUMMARY_LABEL_PT = 10
# 底部摘要数值字号。
SUMMARY_VALUE_PT = 12
# 底部摘要图标尺寸。
SUMMARY_ICON_SIZE = 14
# 底部摘要图标和标题间距。
SUMMARY_ICON_TITLE_GAP = 4
# 底部摘要标题行 Y 坐标。
SUMMARY_TITLE_ROW_Y = 154
# 底部摘要标题行高度。
SUMMARY_TITLE_ROW_HEIGHT = 14
# 底部摘要数值行 Y 坐标。
SUMMARY_VALUE_ROW_Y = 172
# 底部摘要数值行高度。
SUMMARY_VALUE_ROW_HEIGHT = 18
# 展开线条命中/绘制区域尺寸。
EXPAND_AFFORDANCE_SIZE = 40
# 展开线条颜色。
EXPAND_AFFORDANCE_LINE_COLOR = "#60A5FA"
# 展开线条宽度。
EXPAND_AFFORDANCE_LINE_WIDTH = 3.0
# 四角展开线条长度。
EXPAND_AFFORDANCE_CORNER_LENGTH = 8.0
# 四角展开线条相对绘制区域的内缩。
EXPAND_AFFORDANCE_INSET = 8.0
# 内缩态缩略图堆叠区域 X 坐标。
THUMBNAIL_STACK_X = 150.0
# 内缩态缩略图堆叠区域 Y 坐标。
THUMBNAIL_STACK_Y = 72.0
# 内缩态缩略图堆叠区域宽度。
THUMBNAIL_STACK_WIDTH = 130.0
# 内缩态缩略图堆叠区域高度。
THUMBNAIL_STACK_HEIGHT = 66.0
# 单张缩略图 fallback 宽度。
THUMBNAIL_WIDTH = 86.0
# 单张缩略图 fallback 高度。
THUMBNAIL_HEIGHT = 52.0
# 鼠标进入缩略图区外扩多少像素后淡入展开线条。
THUMBNAIL_EXPAND_ENTER_DISTANCE_PX = 40
# 鼠标离开缩略图区外扩多少像素后淡回缩略图。
THUMBNAIL_EXPAND_EXIT_DISTANCE_PX = 64
# 缩略图 / 展开线条交叉淡入淡出时长。
THUMBNAIL_EXPAND_REVEAL_MS = 160
# 展开线条淡入后缩略图仍保留的透明度，避免用户丢失“视频组”语义。
THUMBNAIL_REVEALED_OPACITY = 0.35


@dataclass(frozen=True)
class VideoInputCollapsedNodeCardViewModel:
    title: str = "视频输入"
    status_label: str = "正常"
    video_count: int = 32
    total_duration: str = "05:29:18"
    total_size: str = "48.6 GB"
    pending_count: int = 6
    selected: bool = True
    expanded: bool = False


class VideoInputCollapsedNodeCardItem(QGraphicsObject):
    """Collapsed VideoInput card for the WorkCanvas vector route."""

    def __init__(
        self,
        view_model: VideoInputCollapsedNodeCardViewModel | None = None,
        parent: QGraphicsObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.view_model = view_model or VideoInputCollapsedNodeCardViewModel()
        self._font_families = load_atelier_ui_font_families()
        self.setData(0, "video-input-collapsed-node-card")
        self.setData(1, "thumbnail-stack-collapsed")
        self.setProperty("item_route", "qgraphicsitem-paint")
        self.setProperty("display_mode", "collapsed")
        self.setProperty("thumbnail_strategy", "cached-preview-or-vector-fallback")
        self.setProperty("thumbnail_count", 3)
        self.setProperty("has_thumbnail_stack", True)
        self.setProperty("has_thumbnail_placeholder", False)
        self.setProperty("gui_runtime_boundary", "draw-only-no-thumbnail-generation")
        self.setProperty("selected", self.view_model.selected)
        self.setProperty("debug_perf", False)
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._debug_perf = False
        self._last_paint_ms = 0.0
        self._paint_count = 0
        self._last_paint_antialiasing = False
        self._thumbnail_proximity_active = False
        self._expand_reveal = 0.0
        self._proximity_animation = QVariantAnimation(self)
        self._proximity_animation.setDuration(THUMBNAIL_EXPAND_REVEAL_MS)
        self._proximity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._proximity_animation.valueChanged.connect(self._set_expand_reveal)
        self._sync_expand_reveal_properties()

    def set_debug_perf(self, enabled: bool) -> None:
        self._debug_perf = bool(enabled)
        self.setProperty("debug_perf", self._debug_perf)

    def debug_perf_snapshot(self) -> dict[str, object]:
        return {
            "debug_perf": self._debug_perf,
            "paint_count": self._paint_count,
            "paint_ms": self._last_paint_ms,
            "antialiasing": self._last_paint_antialiasing,
        }

    def boundingRect(self) -> QRectF:  # noqa: N802
        return QRectF(0, 0, COLLAPSED_CARD_WIDTH, COLLAPSED_CARD_HEIGHT)

    def content_layout_snapshot(self) -> dict[str, tuple[float, ...]]:
        status_font = self._font(STATUS_TEXT_PT, self._font_families.ui_regular)
        return {
            "border_rect": self._rect_tuple(self._border_rect()),
            "icon_rect": self._rect_tuple(self._icon_rect()),
            "title_rect": self._rect_tuple(self._title_rect()),
            "status_rect": self._rect_tuple(
                self._status_rect_for_metrics(QFontMetrics(status_font))
            ),
            "primary_label_rect": self._rect_tuple(self._primary_label_rect()),
            "primary_value_rect": self._rect_tuple(self._primary_value_rect()),
            "header_divider_line": self._header_divider_line(),
            "summary_divider_line": self._summary_divider_line(),
        }

    def video_icon_layout_snapshot(self) -> dict[str, object]:
        icon_rect = self._icon_rect()
        left_reel_x = icon_rect.left() + VIDEO_ICON_LEFT_REEL_OFFSET_X
        right_reel_x = icon_rect.left() + VIDEO_ICON_RIGHT_REEL_OFFSET_X
        return {
            "icon_rect": self._rect_tuple(icon_rect),
            "left_reel_x": left_reel_x,
            "right_reel_x": right_reel_x,
            "media_panel_center_x": (left_reel_x + right_reel_x) / 2,
            "play_triangle_points": self._video_icon_play_triangle_points(icon_rect),
        }

    def font_role_snapshot(self) -> dict[str, int]:
        title_font = self._font(
            TITLE_TEXT_PT,
            self._font_families.ui_regular,
            REVIEW_RED_TEXT_WEIGHT,
        )
        status_font = self._font(
            STATUS_TEXT_PT,
            self._font_families.ui_medium,
            REVIEW_YELLOW_STATUS_WEIGHT,
        )
        primary_label_font = self._font(
            PRIMARY_LABEL_PT,
            self._font_families.ui_regular,
            REVIEW_RED_TEXT_WEIGHT,
        )
        summary_label_font = self._font(
            SUMMARY_LABEL_PT,
            self._font_families.ui_regular,
            REVIEW_RED_TEXT_WEIGHT,
        )
        return {
            "title_weight": self._font_weight_value(title_font),
            "status_weight": self._font_weight_value(status_font),
            "primary_label_weight": self._font_weight_value(primary_label_font),
            "summary_label_weight": self._font_weight_value(summary_label_font),
        }

    def appearance_snapshot(self) -> dict[str, object]:
        return {
            "selected": self.view_model.selected,
            "border_width": self._current_border_width(),
            "border_color": self._current_border_color(),
            "glow_enabled": self.view_model.selected,
            "glow_width": CARD_SELECTED_GLOW_WIDTH if self.view_model.selected else 0,
            "background_gradient": (
                CARD_BACKGROUND_TOP_COLOR,
                CARD_BACKGROUND_MID_COLOR,
                CARD_BACKGROUND_BOTTOM_COLOR,
            ),
        }

    def summary_metric_layout_snapshot(self) -> dict[str, object]:
        return {
            "title_row_model": "icon-left-title-right",
            "value_row_model": "value-below-title-row",
            "metrics_right_x": self._summary_metrics_right_x(),
            "expand_control_placement": "thumbnail-stack-overlay",
            "metrics": [
                {
                    "label": layout["label"],
                    "value": layout["value"],
                    "icon_role": layout["icon_role"],
                    "icon_rect": self._rect_tuple(layout["icon_rect"]),
                    "icon_mark_y_positions": self._summary_icon_mark_y_positions(
                        layout["icon_role"],
                        layout["icon_rect"],
                    ),
                    "title_rect": self._rect_tuple(layout["title_rect"]),
                    "value_rect": self._rect_tuple(layout["value_rect"]),
                }
                for layout in self._summary_metric_layouts()
            ],
        }

    def expand_affordance_snapshot(self) -> dict[str, object]:
        return {
            "rect": self._rect_tuple(self._expand_button_rect()),
            "visual_treatment": "line-only",
            "line_style": "four-corner-expand",
            "background_treatment": "none",
            "shadow": "none",
            "icon_source": "python-painter",
            "mode_icon": "collapse" if self.view_model.expanded else "expand",
            "placement": "thumbnail-stack-overlay",
            "trigger": "pointer-proximity",
            "enter_distance_px": THUMBNAIL_EXPAND_ENTER_DISTANCE_PX,
            "exit_distance_px": THUMBNAIL_EXPAND_EXIT_DISTANCE_PX,
            "opacity": self._expand_affordance_opacity(),
            "stroke_color": EXPAND_AFFORDANCE_LINE_COLOR,
            "stroke_width": EXPAND_AFFORDANCE_LINE_WIDTH,
            "stroke_cap": "round",
            "corner_count": 4,
            "segment_count": 8,
        }

    def thumbnail_stack_snapshot(self) -> dict[str, object]:
        return {
            "stack_rect": self._rect_tuple(self._thumbnail_stack_rect()),
            "thumbnail_count": 3,
            "source_policy": "cached-preview-or-vector-fallback",
            "gui_runtime_boundary": "no-thumbnail-generation",
            "interaction": "proximity-reveal-expand",
            "interaction_state": (
                "expand-revealed" if self._thumbnail_proximity_active else "thumbnail-stack"
            ),
            "enter_distance_px": THUMBNAIL_EXPAND_ENTER_DISTANCE_PX,
            "exit_distance_px": THUMBNAIL_EXPAND_EXIT_DISTANCE_PX,
            "thumbnail_opacity": self._thumbnail_stack_opacity(),
            "expand_affordance_opacity": self._expand_affordance_opacity(),
            "expand_affordance_rect": self._rect_tuple(self._expand_button_rect()),
            "thumbnails": [
                {
                    "depth_index": layout["depth_index"],
                    "rect": self._rect_tuple(layout["rect"]),
                    "accent": layout["accent"],
                    "source": "vector-fallback",
                }
                for layout in self._thumbnail_layouts()
            ],
        }

    def update_thumbnail_proximity(self, position: QPointF, *, animated: bool = True) -> None:
        hot_rect = self._thumbnail_stack_rect()
        distance = (
            THUMBNAIL_EXPAND_EXIT_DISTANCE_PX
            if self._thumbnail_proximity_active
            else THUMBNAIL_EXPAND_ENTER_DISTANCE_PX
        )
        should_reveal = hot_rect.adjusted(
            -distance,
            -distance,
            distance,
            distance,
        ).contains(position)
        self._set_thumbnail_proximity_active(should_reveal, animated=animated)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: QWidget | None = None,
    ) -> None:
        del option, widget
        started_at = time.perf_counter() if self._debug_perf else 0.0
        painter.save()
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            self._last_paint_antialiasing = painter.testRenderHint(
                QPainter.RenderHint.Antialiasing
            )
            self._paint_card_background(painter)
            self._paint_header(painter)
            self._paint_primary_metric(painter)
            self._paint_thumbnail_stack(painter)
            self._paint_summary_metrics(painter)
            self._paint_expand_affordance(painter)
        finally:
            painter.restore()
            if self._debug_perf:
                self._paint_count += 1
                self._last_paint_ms = (time.perf_counter() - started_at) * 1000.0

    def hoverMoveEvent(self, event) -> None:  # type: ignore[override]
        self.update_thumbnail_proximity(event.pos(), animated=True)
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event) -> None:  # type: ignore[override]
        self._set_thumbnail_proximity_active(False, animated=True)
        super().hoverLeaveEvent(event)

    def _paint_card_background(self, painter: QPainter) -> None:
        rect = self._border_rect()
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor(CARD_BACKGROUND_TOP_COLOR))
        gradient.setColorAt(0.55, QColor(CARD_BACKGROUND_MID_COLOR))
        gradient.setColorAt(1.0, QColor(CARD_BACKGROUND_BOTTOM_COLOR))
        if self.view_model.selected:
            self._paint_selected_glow(painter)
        painter.setBrush(gradient)
        painter.setPen(QPen(QColor(self._current_border_color()), self._current_border_width()))
        painter.drawRoundedRect(rect, CARD_RADIUS, CARD_RADIUS)

    def _paint_selected_glow(self, painter: QPainter) -> None:
        painter.save()
        try:
            painter.setBrush(Qt.BrushStyle.NoBrush)
            for width, alpha in ((CARD_SELECTED_GLOW_WIDTH, 34), (6, 48), (3, 64)):
                color = QColor(CARD_SELECTED_GLOW_COLOR)
                color.setAlpha(alpha)
                painter.setPen(QPen(color, width))
                inset = width / 2
                glow_rect = self.boundingRect().adjusted(inset, inset, -inset, -inset)
                painter.drawRoundedRect(glow_rect, CARD_RADIUS, CARD_RADIUS)
        finally:
            painter.restore()

    def _paint_header(self, painter: QPainter) -> None:
        painter.setPen(QPen(QColor("#2A3A50"), 1))
        painter.drawLine(*self._header_divider_line())

        icon_rect = self._icon_rect()
        self._paint_video_icon(painter, icon_rect)

        title_font = self._font(
            TITLE_TEXT_PT,
            self._font_families.ui_regular,
            REVIEW_RED_TEXT_WEIGHT,
        )
        painter.setFont(title_font)
        painter.setPen(QColor("#8AB7FF"))
        painter.drawText(
            self._title_rect(),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.view_model.title,
        )

        status_font = self._font(
            STATUS_TEXT_PT,
            self._font_families.ui_medium,
            REVIEW_YELLOW_STATUS_WEIGHT,
        )
        painter.setFont(status_font)
        status_rect = self._status_rect_for_metrics(painter.fontMetrics())
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(221, 251, 230, 210))
        painter.drawRoundedRect(status_rect, STATUS_CAPSULE_RADIUS, STATUS_CAPSULE_RADIUS)
        painter.setPen(QColor("#1F7A3E"))
        painter.drawText(status_rect, Qt.AlignmentFlag.AlignCenter, self.view_model.status_label)

    def _paint_video_icon(self, painter: QPainter, rect: QRectF) -> None:
        painter.save()
        try:
            painter.setPen(QPen(QColor("#726FA0"), 1.4))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect.adjusted(2, 4, -2, -4), 4, 4)
            painter.drawLine(
                rect.left() + VIDEO_ICON_LEFT_REEL_OFFSET_X,
                rect.top() + 4,
                rect.left() + VIDEO_ICON_LEFT_REEL_OFFSET_X,
                rect.bottom() - 4,
            )
            painter.drawLine(
                rect.left() + VIDEO_ICON_RIGHT_REEL_OFFSET_X,
                rect.top() + 4,
                rect.left() + VIDEO_ICON_RIGHT_REEL_OFFSET_X,
                rect.bottom() - 4,
            )
            play_points = self._video_icon_play_triangle_points(rect)
            play = QPainterPath()
            play.moveTo(*play_points[0])
            play.lineTo(*play_points[1])
            play.lineTo(*play_points[2])
            play.closeSubpath()
            painter.drawPath(play)
        finally:
            painter.restore()

    def _paint_primary_metric(self, painter: QPainter) -> None:
        label_font = self._font(
            PRIMARY_LABEL_PT,
            self._font_families.ui_regular,
            REVIEW_RED_TEXT_WEIGHT,
        )
        value_font = self._font(
            PRIMARY_VALUE_PT,
            self._font_families.ui_semibold,
            QFont.Weight.DemiBold,
        )
        painter.setPen(QColor("#9FB3C8"))
        painter.setFont(label_font)
        painter.drawText(
            self._primary_label_rect(),
            Qt.AlignmentFlag.AlignLeft,
            "视频数",
        )
        painter.setPen(QColor("#6EA3FF"))
        painter.setFont(value_font)
        painter.drawText(
            self._primary_value_rect(),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            str(self.view_model.video_count),
        )

    def _paint_thumbnail_stack(self, painter: QPainter) -> None:
        painter.save()
        try:
            painter.setOpacity(self._thumbnail_stack_opacity())
            for layout in self._thumbnail_layouts():
                self._paint_thumbnail(painter, layout)
        finally:
            painter.restore()

    def _paint_thumbnail(self, painter: QPainter, layout: dict[str, object]) -> None:
        rect = layout["rect"]
        accent = str(layout["accent"])
        horizon = str(layout["horizon"])
        painter.save()
        try:
            gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            gradient.setColorAt(0.0, QColor("#B8D7F6"))
            gradient.setColorAt(0.48, QColor(horizon))
            gradient.setColorAt(1.0, QColor("#0B1522"))
            painter.setPen(QPen(QColor(accent), 1.4))
            painter.setBrush(gradient)
            painter.drawRoundedRect(rect, 7, 7)

            mountain = QPainterPath()
            mountain.moveTo(rect.left(), rect.bottom() - 14)
            mountain.lineTo(rect.left() + rect.width() * 0.28, rect.top() + rect.height() * 0.45)
            mountain.lineTo(rect.left() + rect.width() * 0.52, rect.bottom() - 17)
            mountain.lineTo(rect.left() + rect.width() * 0.74, rect.top() + rect.height() * 0.34)
            mountain.lineTo(rect.right(), rect.bottom() - 20)
            mountain.lineTo(rect.right(), rect.bottom())
            mountain.lineTo(rect.left(), rect.bottom())
            mountain.closeSubpath()
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(20, 34, 53, 205))
            painter.drawPath(mountain)

            if layout["depth_index"] == 2:
                self._paint_thumbnail_play_hint(painter, rect)
        finally:
            painter.restore()

    def _paint_thumbnail_play_hint(self, painter: QPainter, rect: QRectF) -> None:
        center = rect.center()
        painter.setPen(Qt.PenStyle.NoPen)
        play_backdrop = QColor("#06101E")
        play_backdrop.setAlpha(150)
        painter.setBrush(play_backdrop)
        painter.drawEllipse(center, 13, 13)

        play = QPainterPath()
        play.moveTo(center.x() - 4, center.y() - 7)
        play.lineTo(center.x() + 7, center.y())
        play.lineTo(center.x() - 4, center.y() + 7)
        play.closeSubpath()
        painter.setBrush(QColor("#F3F7FB"))
        painter.drawPath(play)

        duration_rect = QRectF(rect.left() + 6, rect.bottom() - 18, 38, 14)
        duration_backdrop = QColor("#06101E")
        duration_backdrop.setAlpha(170)
        painter.setBrush(duration_backdrop)
        painter.drawRoundedRect(duration_rect, 5, 5)
        duration_font = self._font(8, self._font_families.ui_regular)
        painter.setFont(duration_font)
        painter.setPen(QColor("#F3F7FB"))
        painter.drawText(duration_rect, Qt.AlignmentFlag.AlignCenter, "00:15")

    def _paint_summary_metrics(self, painter: QPainter) -> None:
        painter.setPen(QPen(QColor("#20324A"), 1))
        painter.drawLine(*self._summary_divider_line())
        label_font = self._font(
            SUMMARY_LABEL_PT,
            self._font_families.ui_regular,
            REVIEW_RED_TEXT_WEIGHT,
        )
        value_font = self._font(
            SUMMARY_VALUE_PT,
            self._font_families.ui_regular,
            QFont.Weight.Normal,
        )
        for layout in self._summary_metric_layouts():
            self._paint_summary_icon(painter, layout["icon_role"], layout["icon_rect"])
            painter.setPen(QColor("#9FB3C8"))
            painter.setFont(label_font)
            painter.drawText(
                layout["title_rect"],
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                layout["label"],
            )
            painter.setPen(QColor("#F3F7FB"))
            painter.setFont(value_font)
            painter.drawText(
                layout["value_rect"],
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                layout["value"],
            )

    def _paint_summary_icon(self, painter: QPainter, role: str, rect: QRectF) -> None:
        painter.save()
        try:
            colors = {
                "duration": "#7E8BFF",
                "size": "#38BDF8",
                "pending": "#A78BFA",
            }
            painter.setPen(QPen(QColor(colors[role]), 1.2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            if role == "duration":
                painter.drawEllipse(rect)
                center = rect.center()
                painter.drawLine(center.x(), center.y(), center.x(), rect.top() + 2)
                painter.drawLine(center.x(), center.y(), rect.right() - 2, center.y())
            elif role == "size":
                painter.drawRoundedRect(rect.adjusted(0.5, 1.5, -0.5, -1.5), 2, 2)
                painter.drawLine(
                    rect.left() + 2,
                    rect.center().y(),
                    rect.right() - 2,
                    rect.center().y(),
                )
            else:
                pen = QPen(QColor(colors[role]), 2.0)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                painter.setPen(pen)
                for y in self._summary_icon_mark_y_positions(role, rect):
                    painter.drawLine(rect.left() + 1.5, y, rect.left() + 2.5, y)
                    painter.drawLine(rect.left() + 5, y, rect.right() - 0.5, y)
        finally:
            painter.restore()

    def _paint_expand_affordance(self, painter: QPainter) -> None:
        rect = self._expand_button_rect()
        opacity = self._expand_affordance_opacity()
        if opacity <= 0:
            return
        painter.save()
        try:
            painter.setOpacity(opacity)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            pen = QPen(QColor(EXPAND_AFFORDANCE_LINE_COLOR), EXPAND_AFFORDANCE_LINE_WIDTH)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            self._paint_expand_corner_lines(painter, rect)
        finally:
            painter.restore()

    def _paint_expand_corner_lines(self, painter: QPainter, rect: QRectF) -> None:
        inset = EXPAND_AFFORDANCE_INSET
        length = EXPAND_AFFORDANCE_CORNER_LENGTH
        left = rect.left() + inset
        right = rect.right() - inset
        top = rect.top() + inset
        bottom = rect.bottom() - inset

        painter.drawLine(QPointF(left, top + length), QPointF(left, top))
        painter.drawLine(QPointF(left, top), QPointF(left + length, top))

        painter.drawLine(QPointF(right - length, top), QPointF(right, top))
        painter.drawLine(QPointF(right, top), QPointF(right, top + length))

        painter.drawLine(QPointF(left, bottom - length), QPointF(left, bottom))
        painter.drawLine(QPointF(left, bottom), QPointF(left + length, bottom))

        painter.drawLine(QPointF(right - length, bottom), QPointF(right, bottom))
        painter.drawLine(QPointF(right, bottom), QPointF(right, bottom - length))

    def _font(
        self,
        point_size: int,
        family: str,
        weight: QFont.Weight = QFont.Weight.Normal,
    ) -> QFont:
        font = QFont(family)
        font.setPointSize(point_size)
        font.setWeight(weight)
        return font

    def _font_weight_value(self, font: QFont) -> int:
        weight = font.weight()
        return weight.value if hasattr(weight, "value") else int(weight)

    def _border_rect(self) -> QRectF:
        half_border = self._current_border_width() / 2
        return self.boundingRect().adjusted(
            half_border,
            half_border,
            -half_border,
            -half_border,
        )

    def _current_border_width(self) -> int:
        return CARD_BORDER_WIDTH if self.view_model.selected else CARD_RESTING_BORDER_WIDTH

    def _current_border_color(self) -> str:
        return CARD_SELECTED_BORDER_COLOR if self.view_model.selected else CARD_RESTING_BORDER_COLOR

    def _icon_rect(self) -> QRectF:
        return QRectF(CONTENT_MARGIN_X, 13, TITLE_ICON_SIZE, TITLE_ICON_SIZE)

    def _video_icon_play_triangle_points(self, rect: QRectF) -> tuple[tuple[float, float], ...]:
        return (
            (
                rect.left() + VIDEO_ICON_PLAY_LEFT_OFFSET_X,
                rect.top() + VIDEO_ICON_PLAY_TOP_OFFSET_Y,
            ),
            (
                rect.left() + VIDEO_ICON_PLAY_RIGHT_OFFSET_X,
                rect.center().y(),
            ),
            (
                rect.left() + VIDEO_ICON_PLAY_LEFT_OFFSET_X,
                rect.top() + VIDEO_ICON_PLAY_BOTTOM_OFFSET_Y,
            ),
        )

    def _title_rect(self) -> QRectF:
        return QRectF(self._icon_rect().right() + 10, 0, 120, HEADER_HEIGHT)

    def _status_rect_for_metrics(self, metrics: QFontMetrics) -> QRectF:
        status_width = (
            metrics.horizontalAdvance(self.view_model.status_label)
            + STATUS_CAPSULE_PADDING_X * 2
        )
        return QRectF(
            COLLAPSED_CARD_WIDTH - CONTENT_MARGIN_X - status_width,
            (HEADER_HEIGHT - STATUS_CAPSULE_HEIGHT) / 2,
            status_width,
            STATUS_CAPSULE_HEIGHT,
        )

    def _primary_label_rect(self) -> QRectF:
        return QRectF(CONTENT_MARGIN_X, PRIMARY_LABEL_RECT_Y, 96, 22)

    def _primary_value_rect(self) -> QRectF:
        return QRectF(CONTENT_MARGIN_X, PRIMARY_VALUE_RECT_Y, 110, 50)

    def _header_divider_line(self) -> tuple[float, float, float, float]:
        return (HEADER_DIVIDER_LEFT_X, HEADER_HEIGHT, HEADER_DIVIDER_RIGHT_X, HEADER_HEIGHT)

    def _summary_divider_line(self) -> tuple[float, float, float, float]:
        return (
            SUMMARY_DIVIDER_LEFT_X,
            SUMMARY_DIVIDER_Y,
            SUMMARY_DIVIDER_RIGHT_X,
            SUMMARY_DIVIDER_Y,
        )

    def _summary_metric_specs(self) -> tuple[tuple[str, str, str], ...]:
        return (
            ("duration", "总时长", self.view_model.total_duration),
            ("size", "总大小", self.view_model.total_size),
            ("pending", "待处理", str(self.view_model.pending_count)),
        )

    def _summary_metrics_right_x(self) -> float:
        return COLLAPSED_CARD_WIDTH - CONTENT_MARGIN_X

    def _summary_metric_layouts(self) -> list[dict[str, object]]:
        label_font = self._font(
            SUMMARY_LABEL_PT,
            self._font_families.ui_regular,
            REVIEW_RED_TEXT_WEIGHT,
        )
        metrics = QFontMetrics(label_font)
        metrics_left = CONTENT_MARGIN_X
        metrics_right = self._summary_metrics_right_x()
        column_width = (metrics_right - metrics_left) / 3
        layouts: list[dict[str, object]] = []
        for index, (icon_role, label, value) in enumerate(self._summary_metric_specs()):
            column_left = metrics_left + column_width * index
            title_width = metrics.horizontalAdvance(label)
            group_width = SUMMARY_ICON_SIZE + SUMMARY_ICON_TITLE_GAP + title_width
            group_left = column_left + (column_width - group_width) / 2
            icon_rect = QRectF(
                group_left,
                SUMMARY_TITLE_ROW_Y,
                SUMMARY_ICON_SIZE,
                SUMMARY_ICON_SIZE,
            )
            title_rect = QRectF(
                icon_rect.right() + SUMMARY_ICON_TITLE_GAP,
                SUMMARY_TITLE_ROW_Y,
                title_width,
                SUMMARY_TITLE_ROW_HEIGHT,
            )
            value_rect = QRectF(
                column_left,
                SUMMARY_VALUE_ROW_Y,
                column_width,
                SUMMARY_VALUE_ROW_HEIGHT,
            )
            layouts.append(
                {
                    "icon_role": icon_role,
                    "label": label,
                    "value": value,
                    "icon_rect": icon_rect,
                    "title_rect": title_rect,
                    "value_rect": value_rect,
                }
            )
        return layouts

    def _summary_icon_mark_y_positions(self, role: str, rect: QRectF) -> tuple[float, ...]:
        if role != "pending":
            return ()
        return (
            rect.top() + 3,
            rect.center().y(),
            rect.bottom() - 3,
        )

    def _expand_button_rect(self) -> QRectF:
        center = self._thumbnail_stack_rect().center()
        return QRectF(
            center.x() - EXPAND_AFFORDANCE_SIZE / 2,
            center.y() - EXPAND_AFFORDANCE_SIZE / 2,
            EXPAND_AFFORDANCE_SIZE,
            EXPAND_AFFORDANCE_SIZE,
        )

    def _thumbnail_stack_rect(self) -> QRectF:
        return QRectF(
            THUMBNAIL_STACK_X,
            THUMBNAIL_STACK_Y,
            THUMBNAIL_STACK_WIDTH,
            THUMBNAIL_STACK_HEIGHT,
        )

    def _thumbnail_layouts(self) -> list[dict[str, object]]:
        specs = (
            (0, 42.0, 0.0, "#344B70", "#334D68"),
            (1, 22.0, 7.0, "#4D6D9A", "#426A88"),
            (2, 0.0, 14.0, "#83A3D7", "#557EA8"),
        )
        stack_rect = self._thumbnail_stack_rect()
        return [
            {
                "depth_index": depth_index,
                "rect": QRectF(
                    stack_rect.left() + offset_x,
                    stack_rect.top() + offset_y,
                    THUMBNAIL_WIDTH,
                    THUMBNAIL_HEIGHT,
                ),
                "accent": accent,
                "horizon": horizon,
            }
            for depth_index, offset_x, offset_y, accent, horizon in specs
        ]

    def _thumbnail_stack_opacity(self) -> float:
        return round(1.0 - (1.0 - THUMBNAIL_REVEALED_OPACITY) * self._expand_reveal, 3)

    def _expand_affordance_opacity(self) -> float:
        return round(self._expand_reveal, 3)

    def _set_thumbnail_proximity_active(self, active: bool, *, animated: bool) -> None:
        if self._thumbnail_proximity_active == active and (
            (active and self._expand_reveal == 1.0)
            or (not active and self._expand_reveal == 0.0)
        ):
            return
        self._thumbnail_proximity_active = active
        target = 1.0 if active else 0.0
        if not animated:
            self._proximity_animation.stop()
            self._set_expand_reveal(target)
            return

        self._proximity_animation.stop()
        self._proximity_animation.setStartValue(self._expand_reveal)
        self._proximity_animation.setEndValue(target)
        self._proximity_animation.start()

    def _set_expand_reveal(self, value: object) -> None:
        self._expand_reveal = max(0.0, min(1.0, float(value)))
        self._sync_expand_reveal_properties()
        self.update()

    def _sync_expand_reveal_properties(self) -> None:
        self.setProperty(
            "thumbnail_interaction_state",
            "expand-revealed" if self._thumbnail_proximity_active else "thumbnail-stack",
        )
        self.setProperty("thumbnail_opacity", self._thumbnail_stack_opacity())
        self.setProperty("expand_affordance_opacity", self._expand_affordance_opacity())

    def _rect_tuple(self, rect: QRectF) -> tuple[float, float, float, float]:
        return (rect.x(), rect.y(), rect.width(), rect.height())
