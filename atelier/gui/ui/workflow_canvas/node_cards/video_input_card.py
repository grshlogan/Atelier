from __future__ import annotations

from atelier.gui.entry import ensure_gui_dependency
from atelier.gui.ui.font_assets import load_atelier_ui_font_families

ensure_gui_dependency()

from PySide6.QtCore import QByteArray, QEasingCurve, QPointF, QSize, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen, QPixmap, QResizeEvent, QShowEvent
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QAbstractButton,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


# 状态胶囊的浅绿色半透明背景。
STATUS_CAPSULE_BACKGROUND = "rgba(221, 251, 230, 191)"
# 状态胶囊文字的绿色。
STATUS_CAPSULE_TEXT_COLOR = "#1F7A3E"
# 状态胶囊左右文字内边距。
STATUS_CAPSULE_HORIZONTAL_PADDING = 14
# 状态胶囊固定高度。
STATUS_CAPSULE_HEIGHT = 26
# 状态胶囊圆角半径，保持两端接近圆形。
STATUS_CAPSULE_RADIUS = 13
# 顶部介绍区和内容区之间的分割线颜色。
HEADER_DIVIDER_COLOR = "#2A3A50"
# 顶部标题文字字号，使用 Qt point size。
HEADER_TEXT_SIZE_PT = 13
# 状态胶囊文字字号，使用 Qt point size。
STATUS_TEXT_SIZE_PT = 13
# 节点标题和强调文字的蓝色。
TITLE_TEXT_COLOR = "#8AB7FF"
# 节点卡片外边框宽度。
CARD_BORDER_WIDTH = 3
# 节点卡片整体圆角半径。
CARD_RADIUS = 16
# 卡片内容相对外边框的左右内缩。
CARD_CONTENT_MARGIN_X = 7
# 展开态卡片宽度。
EXPANDED_CARD_WIDTH = 400
# 展开态卡片高度。
EXPANDED_CARD_HEIGHT = 600
# 内缩态卡片宽度。
COLLAPSED_CARD_WIDTH = 300
# 内缩态卡片高度。
COLLAPSED_CARD_HEIGHT = 200
# 展开态内容列宽度，等于 400 减去边框和左右内缩后的视觉宽度。
CARD_CONTENT_WIDTH = 380
# 视频输入路径区高度。
SOURCE_INPUT_SECTION_HEIGHT = 50
# 输入路径和浏览按钮所在行高度。
INPUT_ROW_HEIGHT = 50
# 输入框和浏览按钮的控件高度。
INPUT_CONTROL_HEIGHT = 40
# 输入路径框固定宽度。
INPUT_PATH_WIDTH = 275
# 浏览按钮固定宽度。
BROWSE_BUTTON_WIDTH = 100
# 右侧连接点直径。
OUTPUT_PORT_SIZE = 12
# 展开/缩小按钮尺寸。
EXPAND_TOGGLE_SIZE = 40
# 展开/缩小按钮圆角半径。
EXPAND_TOGGLE_RADIUS = 12
# 展开/缩小动画时长。
EXPAND_TOGGLE_ANIMATION_MS = 500
# 展开/缩小按钮渐变顶部颜色。
EXPAND_TOGGLE_GRADIENT_TOP = "#25344D"
# 展开/缩小按钮渐变底部颜色。
EXPAND_TOGGLE_GRADIENT_BOTTOM = "#101A2A"

# 视频详情行卡片高度。
VIDEO_ITEM_CARD_HEIGHT = 80
# 视频详情行卡片的视觉内边距。
VIDEO_ITEM_CARD_PADDING = 5
# QFrame 边框会占 1px 内容坐标，这里补偿后让视觉边距仍为 5px。
VIDEO_ITEM_LAYOUT_MARGIN = VIDEO_ITEM_CARD_PADDING - 1
# 视频缩略图固定宽度。
VIDEO_ITEM_THUMB_W = 124
# 视频缩略图固定高度，保证上/下边距与左边距一致。
VIDEO_ITEM_THUMB_H = VIDEO_ITEM_CARD_HEIGHT - VIDEO_ITEM_CARD_PADDING * 2
# 多条视频详情行之间的垂直间距。
VIDEO_ITEM_CARD_SPACING = 5
# 视频文件名字号，使用 Qt point size。
VIDEO_ITEM_FILENAME_PT = 9
# 视频参数字号，使用 Qt point size。
VIDEO_ITEM_PARAM_PT = 8
# 视频参数小图标尺寸。
VIDEO_ITEM_ICON_SIZE = 12
# 视频参数图标颜色。
VIDEO_ITEM_INFO_COLOR = "#8AB7FF"
# 视频参数文字颜色。
VIDEO_ITEM_VALUE_COLOR = "#C8D8EE"
# 内缩态主体区域左右内边距。
COLLAPSED_MAIN_MARGIN_X = 10
# 内缩态主体区域上下内边距。
COLLAPSED_MAIN_MARGIN_Y = 8
# 内缩态顶部主信息行高度。
COLLAPSED_HERO_ROW_HEIGHT = 72
# 内缩态“视频数/32”主指标区域宽度。
COLLAPSED_PRIMARY_METRIC_WIDTH = 92
# 内缩态缩略图堆叠区域宽度。
COLLAPSED_THUMBNAIL_STACK_WIDTH = 108
# 内缩态缩略图堆叠区域高度。
COLLAPSED_THUMBNAIL_STACK_HEIGHT = 64
# 内缩态单张缩略图宽度。
COLLAPSED_THUMBNAIL_WIDTH = 72
# 内缩态单张缩略图高度。
COLLAPSED_THUMBNAIL_HEIGHT = 46
# 内缩态底部摘要指标图标尺寸。
COLLAPSED_STAT_ICON_SIZE = 18
# 内缩态底部摘要指标组之间的间距。
COLLAPSED_STAT_SPACING = 8
# 内缩态底部摘要指标标题字号。
COLLAPSED_STAT_TITLE_PT = 8
# 内缩态底部摘要指标数值字号。
COLLAPSED_STAT_VALUE_PT = 10
# 内缩态视频数量标题字号。
COLLAPSED_PRIMARY_TITLE_PT = 11
# 内缩态视频数量数值字号。
COLLAPSED_PRIMARY_VALUE_PT = 32
# 左上角视频输入主图标尺寸。
VIDEO_INPUT_CARD_ICON_SIZE = 48
# 左上角视频输入主图标线框颜色。
VIDEO_INPUT_CARD_ICON_STROKE_COLOR = "#726FA0"
# 左上角视频输入主图标线宽。
VIDEO_INPUT_CARD_ICON_STROKE_WIDTH = 1.75
# 左上角视频输入主图标内联 SVG，仅服务当前候选卡片。
VIDEO_INPUT_CARD_ICON_SVG = f"""\
<svg xmlns="http://www.w3.org/2000/svg" width="{VIDEO_INPUT_CARD_ICON_SIZE}" height="{VIDEO_INPUT_CARD_ICON_SIZE}" viewBox="0 0 48 48" fill="none">
  <title>Video input card icon</title>
  <g stroke="{VIDEO_INPUT_CARD_ICON_STROKE_COLOR}" stroke-width="{VIDEO_INPUT_CARD_ICON_STROKE_WIDTH}" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke">
    <rect x="9.5" y="11.5" width="29" height="25" rx="4"/>
    <path d="M16.5 11.5v25M31.5 11.5v25"/>
    <path d="M9.5 17.5h7M9.5 24h7M9.5 30.5h7"/>
    <path d="M31.5 17.5h7M31.5 24h7M31.5 30.5h7"/>
    <path d="M21 18.5L30 24L21 29.5z"/>
  </g>
</svg>
"""


def _make_param_icon(svg_body: str, size: int = VIDEO_ITEM_ICON_SIZE) -> QPixmap:
    """Render an inline SVG string to a QPixmap at the given size."""
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}">{svg_body}</svg>'
    )
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    try:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        renderer.render(painter)
    finally:
        painter.end()
    return pixmap


# 视频参数行小图标集合，使用 12x12 视窗和统一描边风格。
_IC = "#8AB7FF"  # 视频参数行小图标的基础颜色。
_SW = "1"  # 视频参数行小图标的线宽。
_PARAM_ICONS: dict[str, str] = {  # 视频参数行小图标的内联 SVG 片段，统一使用 12x12 视窗。
    # 分辨率图标：四宫格。
    "res": (
        f'<rect x="1" y="1" width="4" height="4" rx="0.5" fill="none" stroke="{_IC}" stroke-width="{_SW}"/>'
        f'<rect x="7" y="1" width="4" height="4" rx="0.5" fill="none" stroke="{_IC}" stroke-width="{_SW}"/>'
        f'<rect x="1" y="7" width="4" height="4" rx="0.5" fill="none" stroke="{_IC}" stroke-width="{_SW}"/>'
        f'<rect x="7" y="7" width="4" height="4" rx="0.5" fill="none" stroke="{_IC}" stroke-width="{_SW}"/>'
    ),
    # 帧率图标：播放三角。
    "fps": (
        f'<polygon points="2,1 11,6 2,11" fill="none" stroke="{_IC}" stroke-width="{_SW}" '
        f'stroke-linejoin="round"/>'
    ),
    # 时长图标：时钟。
    "dur": (
        f'<circle cx="6" cy="6" r="5" fill="none" stroke="{_IC}" stroke-width="{_SW}"/>'
        f'<line x1="6" y1="6" x2="6" y2="2.5" stroke="{_IC}" stroke-width="{_SW}" stroke-linecap="round"/>'
        f'<line x1="6" y1="6" x2="9" y2="7.5" stroke="{_IC}" stroke-width="{_SW}" stroke-linecap="round"/>'
    ),
    # 文件大小图标：折角文件。
    "size": (
        f'<path d="M2 1 h6 l2 2 v8 H2 Z" fill="none" stroke="{_IC}" stroke-width="{_SW}" stroke-linejoin="round"/>'
        f'<path d="M8 1 v2 h2" fill="none" stroke="{_IC}" stroke-width="{_SW}" stroke-linejoin="round"/>'
    ),
    # 编码格式图标：六边形。
    "codec": (
        f'<polygon points="6,1 10.5,3.5 10.5,8.5 6,11 1.5,8.5 1.5,3.5" '
        f'fill="none" stroke="{_IC}" stroke-width="{_SW}" stroke-linejoin="round"/>'
    ),
    # 码率图标：信号柱。
    "bitrate": (
        f'<rect x="1" y="8" width="2" height="3" rx="0.5" fill="{_IC}"/>'
        f'<rect x="4.5" y="5" width="2" height="6" rx="0.5" fill="{_IC}"/>'
        f'<rect x="8" y="2" width="2" height="9" rx="0.5" fill="{_IC}"/>'
    ),
    # 待处理图标：三条任务线。
    "pending": (
        f'<circle cx="2" cy="3" r="1" fill="{_IC}"/>'
        f'<circle cx="2" cy="6" r="1" fill="{_IC}"/>'
        f'<circle cx="2" cy="9" r="1" fill="{_IC}"/>'
        f'<path d="M5 3h6M5 6h6M5 9h6" fill="none" stroke="{_IC}" stroke-width="{_SW}" stroke-linecap="round"/>'
    ),
}


def _render_svg_icon_pixmap(svg: str, icon_size: int) -> QPixmap:
    return _render_svg_pixmap(svg, icon_size, icon_size)


def _render_svg_pixmap(svg: str, width: int, height: int) -> QPixmap:
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    try:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        renderer.render(painter)
    finally:
        painter.end()
    return pixmap


def _collapsed_thumbnail_svg(width: int, height: int, *, accent: str, horizon: str) -> str:
    return f"""\
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="{height}" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#B8D7F6"/>
      <stop offset="0.48" stop-color="{horizon}"/>
      <stop offset="1" stop-color="#0B1522"/>
    </linearGradient>
  </defs>
  <rect x="0.75" y="0.75" width="{width - 1.5}" height="{height - 1.5}" rx="7" fill="url(#sky)" stroke="{accent}" stroke-width="1.5"/>
  <path d="M0 {height * 0.7:.1f} L{width * 0.3:.1f} {height * 0.45:.1f} L{width * 0.54:.1f} {height * 0.63:.1f} L{width * 0.74:.1f} {height * 0.36:.1f} L{width} {height * 0.58:.1f} V{height} H0 Z" fill="#142235" fill-opacity="0.78"/>
  <circle cx="{width * 0.72:.1f}" cy="{height * 0.27:.1f}" r="{height * 0.09:.1f}" fill="#F3F7FB" fill-opacity="0.48"/>
</svg>
"""


class ExpandCollapseButton(QAbstractButton):
    """Self-painted expand/collapse toggle for the dev-only node card candidate."""

    def __init__(self, *, expanded: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._rotation = 0.0 if expanded else 180.0
        self._icon_animation = QVariantAnimation(self)
        self._icon_animation.setDuration(EXPAND_TOGGLE_ANIMATION_MS)
        self._icon_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._icon_animation.valueChanged.connect(self._set_icon_rotation)
        self.setObjectName("video-input-card-expand-toggle")
        self.setFixedSize(EXPAND_TOGGLE_SIZE, EXPAND_TOGGLE_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setProperty("corner_radius", EXPAND_TOGGLE_RADIUS)
        self.setProperty("icon_source", "python-painter")
        self.setProperty("animation_driver", "QVariantAnimation")
        self.setProperty("background_treatment", "vertical-gradient")
        self.setProperty("gradient_top_color", EXPAND_TOGGLE_GRADIENT_TOP)
        self.setProperty("gradient_bottom_color", EXPAND_TOGGLE_GRADIENT_BOTTOM)
        self.set_expanded(expanded, animated=False)

    def set_expanded(self, expanded: bool, *, animated: bool) -> None:
        self.setProperty("mode_icon", "collapse" if expanded else "expand")
        self.setToolTip("缩小卡片" if expanded else "展开卡片")
        target_rotation = 0.0 if expanded else 180.0
        if not animated:
            self._icon_animation.stop()
            self._set_icon_rotation(target_rotation)
            return

        self._icon_animation.stop()
        self._icon_animation.setStartValue(self._rotation)
        self._icon_animation.setEndValue(target_rotation)
        self._icon_animation.start()

    def _set_icon_rotation(self, value: object) -> None:
        self._rotation = float(value)
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        del event
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            rect = self.rect().adjusted(0, 0, -1, -1)
            background = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            background.setColorAt(0, QColor("#30415F" if self.isDown() else EXPAND_TOGGLE_GRADIENT_TOP))
            background.setColorAt(1, QColor("#0B1320" if self.isDown() else EXPAND_TOGGLE_GRADIENT_BOTTOM))
            border = QColor("#2A3A50")
            painter.setBrush(background)
            painter.setPen(QPen(border, 1))
            painter.drawRoundedRect(rect, EXPAND_TOGGLE_RADIUS, EXPAND_TOGGLE_RADIUS)

            painter.translate(QPointF(self.width() / 2, self.height() / 2))
            painter.rotate(self._rotation)
            pen = QPen(QColor(TITLE_TEXT_COLOR), 2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(QPointF(-8, 4), QPointF(0, -4))
            painter.drawLine(QPointF(0, -4), QPointF(8, 4))
        finally:
            painter.end()


class VideoInputCardCandidate(QFrame):
    """Dev-only expanded preview for the Workflow Canvas video input node card."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        expanded: bool = True,
        path_editing: bool = False,
    ) -> None:
        super().__init__(parent)
        self._expanded = expanded
        self._target_expanded = expanded
        self._path_editing = path_editing
        self._font_families = load_atelier_ui_font_families()
        self.setObjectName("component-workbench-video-input-card")
        self.setProperty("display_mode", "expanded" if expanded else "collapsed")
        self.setProperty("animation_driver", "QVariantAnimation")
        self.setProperty("animation_duration_ms", EXPAND_TOGGLE_ANIMATION_MS)
        self.setProperty("animation_last_target", "expanded" if expanded else "collapsed")
        self.setFixedSize(
            EXPANDED_CARD_WIDTH if expanded else COLLAPSED_CARD_WIDTH,
            EXPANDED_CARD_HEIGHT if expanded else COLLAPSED_CARD_HEIGHT,
        )
        self._card_size_animation = QVariantAnimation(self)
        self._card_size_animation.setDuration(EXPAND_TOGGLE_ANIMATION_MS)
        self._card_size_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._card_size_animation.valueChanged.connect(self._apply_animated_card_size)
        self._card_size_animation.finished.connect(self._finish_card_size_animation)
        self.setStyleSheet(
            f"""
            #component-workbench-video-input-card {{
              background: #172332;
              border: {CARD_BORDER_WIDTH}px solid #3B82F6;
              border-radius: {CARD_RADIUS}px;
              color: #F3F7FB;
              font-family: "{self._font_families.ui}";
            }}
            #component-workbench-video-input-card QLabel {{
              color: #F3F7FB;
            }}
            #video-input-card-browse-button {{
              background: #0E1A2A;
              color: #F3F7FB;
              border: 1px solid #2A3A50;
              border-radius: 10px;
              font-family: "{self._font_families.ui}";
            }}
            """
        )
        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(28)
        glow.setOffset(0, 0)
        glow.setColor(QColor(59, 130, 246, 185))
        self.setGraphicsEffect(glow)

        layout = QVBoxLayout(self)
        self._layout = layout
        layout.setContentsMargins(CARD_CONTENT_MARGIN_X, 0, CARD_CONTENT_MARGIN_X, 12 if expanded else 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_header_section())
        self._header_divider = self._build_header_divider()
        layout.addWidget(self._header_divider)
        layout.addWidget(self._build_stream_section(), 1)
        self._output_port = self._build_output_port()
        self._expand_toggle = ExpandCollapseButton(expanded=self._expanded, parent=self)
        self._expand_toggle.clicked.connect(self._toggle_expanded)
        self._position_overlay_controls()

    def _build_header_section(self) -> QWidget:
        section = QWidget()
        section.setObjectName("video-input-card-header-section")
        section.setFixedHeight(50)
        layout = QHBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        info_box = QWidget()
        info_box.setObjectName("video-input-card-info-box")
        info_box.setProperty("visible_frame", False)
        info_box.setProperty("placement", "left-center")
        info_box.setProperty("width_policy", "hug-content")
        info_box.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        info_layout = QHBoxLayout(info_box)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(6)

        title = QLabel("视频输入")
        title.setObjectName("video-input-card-title")
        title_font = title.font()
        title_font.setFamily(self._font_families.ui_regular)
        title_font.setPointSize(HEADER_TEXT_SIZE_PT)
        title_font.setBold(False)
        title.setFont(title_font)
        title.setStyleSheet(
            f"""
            #video-input-card-title {{
              color: {TITLE_TEXT_COLOR};
            }}
            """
        )
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        icon = QLabel()
        icon.setObjectName("video-input-card-icon")
        icon.setProperty("size_source", "inline-svg")
        icon.setProperty("stroke_color", VIDEO_INPUT_CARD_ICON_STROKE_COLOR)
        icon.setProperty("stroke_width", VIDEO_INPUT_CARD_ICON_STROKE_WIDTH)
        icon.setFixedSize(VIDEO_INPUT_CARD_ICON_SIZE, VIDEO_INPUT_CARD_ICON_SIZE)
        icon.setPixmap(_render_svg_icon_pixmap(VIDEO_INPUT_CARD_ICON_SVG, VIDEO_INPUT_CARD_ICON_SIZE))
        icon.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        info_layout.addWidget(icon, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        info_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        status_capsule = QFrame()
        status_capsule.setObjectName("video-input-card-status-capsule")
        status_capsule.setProperty("placement", "right-center")
        status_capsule.setProperty("width_policy", "text-width-plus-padding")
        status_capsule.setProperty("horizontal_padding_px", STATUS_CAPSULE_HORIZONTAL_PADDING)
        status_capsule.setStyleSheet(
            f"""
            #video-input-card-status-capsule {{
              background: {STATUS_CAPSULE_BACKGROUND};
              border-radius: {STATUS_CAPSULE_RADIUS}px;
            }}
            """
        )
        capsule_layout = QHBoxLayout(status_capsule)
        capsule_layout.setContentsMargins(0, 0, 0, 0)
        status_text = QLabel("正常")
        status_text.setObjectName("video-input-card-status-text")
        status_font = status_text.font()
        status_font.setFamily(self._font_families.ui_medium)
        status_font.setPointSize(STATUS_TEXT_SIZE_PT)
        status_font.setBold(False)
        status_text.setFont(status_font)
        status_text.setStyleSheet(
            f"""
            #video-input-card-status-text {{
              color: {STATUS_CAPSULE_TEXT_COLOR};
            }}
            """
        )
        status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_capsule_width = (
            status_text.fontMetrics().horizontalAdvance(status_text.text())
            + STATUS_CAPSULE_HORIZONTAL_PADDING * 2
        )
        status_capsule.setFixedSize(status_capsule_width, STATUS_CAPSULE_HEIGHT)
        capsule_layout.addWidget(status_text)

        layout.addWidget(info_box, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addStretch(1)
        layout.addWidget(status_capsule, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return section

    def _build_output_port(self) -> QFrame:
        port = QFrame(self)
        port.setObjectName("video-input-card-output-port")
        port.setProperty("placement", "right-of-header-divider")
        port.setFixedSize(OUTPUT_PORT_SIZE, OUTPUT_PORT_SIZE)
        port.setStyleSheet(
            """
            #video-input-card-output-port {
              background: #172332;
              border: 2px solid #3B82F6;
              border-radius: 6px;
            }
            """
        )
        port.raise_()
        return port

    def _position_output_port(self) -> None:
        if not hasattr(self, "_output_port") or not hasattr(self, "_header_divider"):
            return
        divider_center = self._header_divider.geometry().center()
        port_center_offset_x = (self._output_port.width() - 1) // 2
        port_center_offset_y = (self._output_port.height() - 1) // 2
        x = self.width() - CARD_BORDER_WIDTH // 2 - port_center_offset_x
        y = divider_center.y() - port_center_offset_y
        self._output_port.move(x, y)
        self._output_port.raise_()

    def _position_expand_toggle(self) -> None:
        if not hasattr(self, "_expand_toggle"):
            return
        x = self.width() - CARD_BORDER_WIDTH - CARD_CONTENT_MARGIN_X - self._expand_toggle.width()
        y = self.height() - CARD_BORDER_WIDTH - CARD_CONTENT_MARGIN_X - self._expand_toggle.height()
        self._expand_toggle.move(x, y)
        self._expand_toggle.raise_()

    def _position_overlay_controls(self) -> None:
        self._position_output_port()
        self._position_expand_toggle()

    def _target_card_size(self, expanded: bool) -> QSize:
        return QSize(
            EXPANDED_CARD_WIDTH if expanded else COLLAPSED_CARD_WIDTH,
            EXPANDED_CARD_HEIGHT if expanded else COLLAPSED_CARD_HEIGHT,
        )

    def _apply_animated_card_size(self, value: object) -> None:
        if isinstance(value, QSize):
            self.setFixedSize(value)
            self._position_overlay_controls()

    def _finish_card_size_animation(self) -> None:
        self._apply_animated_card_size(self._target_card_size(self._target_expanded))

    def _sync_expanded_sections(self) -> None:
        if hasattr(self, "_source_input_section"):
            self._source_input_section.setVisible(self._expanded)
        if hasattr(self, "_browser_section"):
            self._browser_section.setVisible(self._expanded)
        if hasattr(self, "_collapsed_main_section"):
            self._collapsed_main_section.setVisible(not self._expanded)
        self._layout.setContentsMargins(CARD_CONTENT_MARGIN_X, 0, CARD_CONTENT_MARGIN_X, 12 if self._expanded else 0)

    def _toggle_expanded(self) -> None:
        self.set_expanded(not self._expanded, animated=True)

    def set_expanded(self, expanded: bool, *, animated: bool = True) -> None:
        self._expanded = expanded
        self._target_expanded = expanded
        target_name = "expanded" if expanded else "collapsed"
        self.setProperty("display_mode", target_name)
        self.setProperty("animation_last_target", target_name)
        self._sync_expanded_sections()
        self._expand_toggle.set_expanded(expanded, animated=animated)

        target_size = self._target_card_size(expanded)
        if not animated:
            self._card_size_animation.stop()
            self._apply_animated_card_size(target_size)
            return

        self._card_size_animation.stop()
        self._card_size_animation.setStartValue(self.size())
        self._card_size_animation.setEndValue(target_size)
        self._card_size_animation.start()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._position_overlay_controls()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self._position_overlay_controls()

    def setVisible(self, visible: bool) -> None:
        super().setVisible(visible)
        if visible:
            self._position_overlay_controls()

    def _build_header_divider(self) -> QFrame:
        divider = QFrame()
        divider.setObjectName("video-input-card-header-divider")
        divider.setProperty("visible_divider", True)
        divider.setFixedHeight(1)
        divider.setStyleSheet(
            f"""
            #video-input-card-header-divider {{
              background: {HEADER_DIVIDER_COLOR};
              border: none;
            }}
            """
        )
        return divider

    def _build_stream_section(self) -> QWidget:
        section = QWidget()
        section.setObjectName("video-input-card-stream-section")
        section.setProperty("flow", "vertical-center-sequence")
        section.setProperty("section_spacing_px", 5)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 5, 0, 0)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self._source_input_section = self._build_source_input_section()
        self._browser_section = self._build_browser_section()
        self._collapsed_main_section = self._build_collapsed_main_section()
        layout.addWidget(self._source_input_section, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self._browser_section, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self._collapsed_main_section, 1)
        return section

    def _build_source_input_section(self) -> QWidget:
        section = QWidget()
        section.setObjectName("video-input-card-source-input-section")
        section.setProperty("section_role", "source-input")
        section.setFixedSize(CARD_CONTENT_WIDTH, SOURCE_INPUT_SECTION_HEIGHT)
        section.setVisible(self._expanded)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        input_row = QWidget()
        input_row.setObjectName("video-input-card-input-row")
        input_row.setFixedSize(CARD_CONTENT_WIDTH, INPUT_ROW_HEIGHT)
        row_layout = QHBoxLayout(input_row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(5)
        row_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        input_box = QFrame()
        input_box.setObjectName("video-input-card-input-path-box")
        input_box.setProperty("left_edge_anchor", "video-input-card-info-box.left")
        input_box.setProperty("frame_mode", "immersive")
        input_box.setProperty("editing", self._path_editing)
        input_box.setFixedSize(INPUT_PATH_WIDTH, INPUT_CONTROL_HEIGHT)
        if self._path_editing:
            input_box.setStyleSheet(
                """
                #video-input-card-input-path-box {
                  background: rgba(14, 26, 42, 180);
                  border: 1px solid #2A3A50;
                  border-radius: 10px;
                }
                """
            )
        else:
            input_box.setStyleSheet(
                """
                #video-input-card-input-path-box {
                  background: transparent;
                  border: none;
                  border-radius: 10px;
                }
                """
            )
        input_layout = QHBoxLayout(input_box)
        input_layout.setContentsMargins(12, 0, 12, 0)
        input_path = QLabel("/Media/Travel/01_Alpine_Lake.mp4")
        input_path.setObjectName("video-input-card-input-path")
        input_path_font = input_path.font()
        input_path_font.setFamily(self._font_families.ui_regular)
        input_path.setFont(input_path_font)
        input_path.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        input_layout.addWidget(input_path)

        browse_button = QPushButton("浏览")
        browse_button.setObjectName("video-input-card-browse-button")
        browse_font = browse_button.font()
        browse_font.setFamily(self._font_families.ui_regular)
        browse_button.setFont(browse_font)
        browse_button.setProperty("right_edge_anchor", "video-input-card-status-capsule.right_tangent")
        browse_button.setFixedSize(BROWSE_BUTTON_WIDTH, INPUT_CONTROL_HEIGHT)

        row_layout.addWidget(input_box)
        row_layout.addWidget(browse_button)
        layout.addWidget(input_row, alignment=Qt.AlignmentFlag.AlignCenter)
        return section

    def _build_video_item_card(
        self,
        filename: str,
        resolution: str,
        fps: str,
        duration: str,
        size: str,
        codec: str,
        bitrate: str,
        selected: bool = False,
    ) -> QFrame:
        SELECTED_BORDER = "#3B82F6"  # 当前选中视频详情行的边框色。
        NORMAL_BORDER = "rgba(42,58,80,160)"  # 普通视频详情行的边框色。

        card = QFrame()
        card.setObjectName("video-item-card")
        card.setProperty("layout_model", "thumbnail-left-details-grid")
        card.setProperty("outer_padding_px", VIDEO_ITEM_CARD_PADDING)
        card.setFixedSize(CARD_CONTENT_WIDTH, VIDEO_ITEM_CARD_HEIGHT)
        card.setStyleSheet(
            f"""
            QFrame#video-item-card {{
              background: {"rgba(30,50,80,180)" if selected else "rgba(14,26,42,120)"};
              border: {"1px solid " + SELECTED_BORDER if selected else "1px solid " + NORMAL_BORDER};
              border-radius: 10px;
            }}
            """
        )

        outer = QHBoxLayout(card)
        outer.setContentsMargins(VIDEO_ITEM_LAYOUT_MARGIN, VIDEO_ITEM_LAYOUT_MARGIN, 8, VIDEO_ITEM_LAYOUT_MARGIN)
        outer.setSpacing(10)

        # thumbnail
        thumb = QFrame()
        thumb.setObjectName("video-item-thumbnail")
        thumb.setProperty("placement", "left-center")
        thumb.setProperty("content_model", "thumbnail-only")
        thumb.setProperty("duration_overlay", False)
        thumb.setFixedSize(VIDEO_ITEM_THUMB_W, VIDEO_ITEM_THUMB_H)
        thumb.setStyleSheet(
            """
            QFrame#video-item-thumbnail {
              background: #0A1520;
              border: 1px solid rgba(42,58,80,200);
              border-radius: 6px;
            }
            """
        )
        outer.addWidget(thumb, alignment=Qt.AlignmentFlag.AlignVCenter)

        # info column
        info_col = QVBoxLayout()
        info_col.setContentsMargins(0, 0, 0, 0)
        info_col.setSpacing(2)

        fn_label = QLabel(filename)
        fn_label.setObjectName("video-item-filename")
        fn_font = fn_label.font()
        fn_font.setFamily(self._font_families.ui_light)
        fn_font.setPointSize(VIDEO_ITEM_FILENAME_PT)
        fn_label.setFont(fn_font)
        fn_label.setStyleSheet("color: #F3F7FB; border: none; background: transparent;")
        fn_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        info_col.addWidget(fn_label)

        grid_w = QWidget()
        grid_w.setObjectName("video-item-metadata-grid")
        grid_w.setProperty("layout_model", "qgrid-3x2")
        grid_w.setProperty("row_count", 3)
        grid_w.setProperty("column_count", 2)
        grid_w.setStyleSheet("background: transparent; border: none;")
        grid = QGridLayout(grid_w)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(2)

        params = [
            ("res", resolution, "fps", fps),
            ("dur", duration,   "size", size),
            ("codec", codec,    "bitrate", bitrate),
        ]
        for row_i, (ik0, v0, ik1, v1) in enumerate(params):
            for col_i, (ik, val) in enumerate([(ik0, v0), (ik1, v1)]):
                cell_w = QWidget()
                cell_w.setStyleSheet("background: transparent; border: none;")
                cell_layout = QHBoxLayout(cell_w)
                cell_layout.setContentsMargins(0, 0, 0, 0)
                cell_layout.setSpacing(4)

                ic_lbl = QLabel()
                ic_lbl.setFixedSize(VIDEO_ITEM_ICON_SIZE, VIDEO_ITEM_ICON_SIZE)
                ic_lbl.setPixmap(_make_param_icon(_PARAM_ICONS[ik]))
                ic_lbl.setStyleSheet("background: transparent; border: none;")

                v_lbl = QLabel(val)
                v_font = v_lbl.font()
                v_font.setFamily(self._font_families.ui_light)
                v_font.setPointSize(VIDEO_ITEM_PARAM_PT)
                v_lbl.setFont(v_font)
                v_lbl.setStyleSheet(f"color: {VIDEO_ITEM_VALUE_COLOR}; background: transparent; border: none;")

                cell_layout.addWidget(ic_lbl)
                cell_layout.addWidget(v_lbl)
                cell_layout.addStretch(1)
                grid.addWidget(cell_w, row_i, col_i)

        info_col.addWidget(grid_w)
        info_col.addStretch(1)
        outer.addLayout(info_col)
        return card

    def _build_browser_section(self) -> QFrame:
        section = QFrame()
        section.setObjectName("video-input-card-browser-section")
        section.setProperty("section_role", "browser-detail")
        section.setProperty("expanded_only", True)
        section.setProperty("visual_frame", False)
        section.setProperty("visual_treatment", "none")
        section.setFixedWidth(CARD_CONTENT_WIDTH)
        section.setVisible(self._expanded)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(VIDEO_ITEM_CARD_SPACING)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        videos = [
            ("01_Alpine_Lake.mp4",    "3840×2160 (16:9)", "29.97 fps", "00:12:45", "1.28 GB",   "H.264 (High)", "81.70 Mbps", True),
            ("02_City_Night.mp4",     "1920×1080 (16:9)", "30.00 fps", "00:08:31", "512.45 MB", "H.265 (HEVC)", "24.36 Mbps", False),
            ("03_Coastline_Drone.mp4","3840×2160 (16:9)", "23.98 fps", "00:11:23", "1.05 GB",   "H.264 (High)", "67.24 Mbps", False),
            ("04_Forest_Trail.mp4",   "1920×1080 (16:9)", "24.00 fps", "00:07:18", "372.18 MB", "H.264 (Main)", "15.36 Mbps", False),
        ]
        for v in videos:
            layout.addWidget(self._build_video_item_card(*v))

        return section

    def _build_collapsed_main_section(self) -> QFrame:
        section = QFrame()
        section.setObjectName("video-input-card-collapsed-main-section")
        section.setProperty("section_role", "collapsed-main")
        section.setProperty("layout_model", "collapsed-summary-hero")
        section.setVisible(not self._expanded)
        section.setStyleSheet(
            """
            #video-input-card-collapsed-main-section {
              background: transparent;
              border: none;
            }
            """
        )
        layout = QVBoxLayout(section)
        layout.setContentsMargins(
            COLLAPSED_MAIN_MARGIN_X,
            COLLAPSED_MAIN_MARGIN_Y,
            COLLAPSED_MAIN_MARGIN_X,
            COLLAPSED_MAIN_MARGIN_Y,
        )
        layout.setSpacing(4)

        hero_row = QWidget()
        hero_row.setObjectName("video-input-card-collapsed-hero-row")
        hero_row.setFixedHeight(COLLAPSED_HERO_ROW_HEIGHT)
        hero_layout = QHBoxLayout(hero_row)
        hero_layout.setContentsMargins(0, 0, 0, 0)
        hero_layout.setSpacing(0)
        hero_layout.addWidget(
            self._build_collapsed_primary_metric(),
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )
        hero_layout.addStretch(1)
        hero_layout.addWidget(
            self._build_collapsed_thumbnail_stack(),
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        layout.addWidget(hero_row)

        divider = QFrame()
        divider.setObjectName("video-input-card-collapsed-summary-divider")
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: #22344D; border: none;")
        layout.addWidget(divider)

        stats_row = QWidget()
        stats_row.setObjectName("video-input-card-collapsed-stats-row")
        stats_layout = QHBoxLayout(stats_row)
        stats_layout.setContentsMargins(0, 0, EXPAND_TOGGLE_SIZE + 8, 0)
        stats_layout.setSpacing(COLLAPSED_STAT_SPACING)
        stats_layout.addWidget(self._build_collapsed_stat("duration", "dur", "总时长", "05:27:18"))
        stats_layout.addWidget(self._build_collapsed_stat("size", "size", "总大小", "48.6 GB"))
        stats_layout.addWidget(self._build_collapsed_stat("pending", "pending", "待处理", "6"))
        stats_layout.addStretch(1)
        layout.addWidget(stats_row, 1)
        return section

    def _build_collapsed_primary_metric(self) -> QWidget:
        metric = QWidget()
        metric.setObjectName("video-input-card-collapsed-primary-metric")
        metric.setProperty("placement", "middle-left")
        metric.setProperty("layout_model", "vertical-text-stack")
        metric.setFixedWidth(COLLAPSED_PRIMARY_METRIC_WIDTH)
        layout = QVBoxLayout(metric)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        title = QLabel("视频数")
        title.setObjectName("video-input-card-collapsed-primary-title")
        title_font = title.font()
        title_font.setFamily(self._font_families.ui_light)
        title_font.setPointSize(COLLAPSED_PRIMARY_TITLE_PT)
        title.setFont(title_font)
        title.setStyleSheet("color: #9BAEC8;")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        value = QLabel("32")
        value.setObjectName("video-input-card-collapsed-primary-value")
        value.setProperty("visual_role", "hero-number")
        value_font = value.font()
        value_font.setFamily(self._font_families.ui_semibold)
        value_font.setPointSize(COLLAPSED_PRIMARY_VALUE_PT)
        value.setFont(value_font)
        value.setStyleSheet("color: #6FA4FF;")
        value.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(title)
        layout.addWidget(value)
        return metric

    def _build_collapsed_thumbnail_stack(self) -> QWidget:
        stack = QWidget()
        stack.setObjectName("video-input-card-collapsed-thumbnail-stack")
        stack.setProperty("placement", "middle-right")
        stack.setProperty("thumbnail_count", 3)
        stack.setFixedSize(COLLAPSED_THUMBNAIL_STACK_WIDTH, COLLAPSED_THUMBNAIL_STACK_HEIGHT)
        specs = [
            (34, 0, "#344B70", "#334D68"),
            (18, 9, "#4D6D9A", "#426A88"),
            (0, 18, "#83A3D7", "#557EA8"),
        ]
        for index, (x, y, accent, horizon) in enumerate(specs):
            thumbnail = QLabel(stack)
            thumbnail.setObjectName("video-input-card-collapsed-thumbnail")
            thumbnail.setProperty("size_source", "inline-svg-rendered-size")
            thumbnail.setProperty("depth_index", index)
            thumbnail.setFixedSize(COLLAPSED_THUMBNAIL_WIDTH, COLLAPSED_THUMBNAIL_HEIGHT)
            thumbnail.setPixmap(
                _render_svg_pixmap(
                    _collapsed_thumbnail_svg(
                        COLLAPSED_THUMBNAIL_WIDTH,
                        COLLAPSED_THUMBNAIL_HEIGHT,
                        accent=accent,
                        horizon=horizon,
                    ),
                    COLLAPSED_THUMBNAIL_WIDTH,
                    COLLAPSED_THUMBNAIL_HEIGHT,
                )
            )
            thumbnail.move(x, y)
            thumbnail.raise_()
        return stack

    def _build_collapsed_stat(self, metric_id: str, icon_key: str, title_text: str, value_text: str) -> QWidget:
        metric = QWidget()
        metric.setObjectName("video-input-card-collapsed-stat")
        metric.setProperty("metric_id", metric_id)
        metric.setProperty("layout_model", "icon-title-row-value-stack")
        layout = QVBoxLayout(metric)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title_row = QWidget()
        title_row.setObjectName("video-input-card-collapsed-stat-title-row")
        title_row.setProperty("layout_model", "icon-title-inline")
        title_layout = QHBoxLayout(title_row)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)

        icon = QLabel()
        icon.setObjectName("video-input-card-collapsed-stat-icon")
        icon.setProperty("size_source", "inline-svg-rendered-size")
        icon.setFixedSize(COLLAPSED_STAT_ICON_SIZE, COLLAPSED_STAT_ICON_SIZE)
        icon.setPixmap(_make_param_icon(_PARAM_ICONS[icon_key], COLLAPSED_STAT_ICON_SIZE))

        title = QLabel(title_text)
        title.setObjectName("video-input-card-collapsed-stat-title")
        title_font = title.font()
        title_font.setFamily(self._font_families.ui_light)
        title_font.setPointSize(COLLAPSED_STAT_TITLE_PT)
        title.setFont(title_font)
        title.setStyleSheet("color: #9BAEC8;")

        value = QLabel(value_text)
        value.setObjectName("video-input-card-collapsed-stat-value")
        value_font = value.font()
        value_font.setFamily(self._font_families.ui_regular)
        value_font.setPointSize(COLLAPSED_STAT_VALUE_PT)
        value.setFont(value_font)
        value.setStyleSheet("color: #F3F7FB;")
        value.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        title_layout.addWidget(icon, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title_layout.addStretch(1)
        layout.addWidget(title_row)
        layout.addWidget(value)
        return metric
