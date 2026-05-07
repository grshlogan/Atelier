from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ColorTokens:
    app_background: str = "#08111D"
    top_bar: str = "#09131F"
    sidebar: str = "#0A1420"
    canvas_background: str = "#0A1422"
    panel_background: str = "#0D1826"
    panel_background_raised: str = "#111D2C"
    card_background: str = "#172332"
    card_hover: str = "#1C2B3D"
    border: str = "#223247"
    border_subtle: str = "#182638"
    border_strong: str = "#2A3A50"
    text_primary: str = "#F3F7FB"
    text_secondary: str = "#B7C2D2"
    text_muted: str = "#7F8EA3"
    text_disabled: str = "#526174"
    primary_blue: str = "#3B82F6"
    primary_blue_light: str = "#60A5FA"
    agent_violet: str = "#A78BFA"
    cyan_accent: str = "#38BDF8"
    success: str = "#39C86A"
    warning: str = "#F6C85F"
    danger: str = "#F87171"
    pending: str = "#7A8797"

    def role_map(self) -> dict[str, str]:
        return {
            "app.background": self.app_background,
            "top_bar.background": self.top_bar,
            "sidebar.background": self.sidebar,
            "canvas.background": self.canvas_background,
            "panel.background": self.panel_background,
            "panel.background_raised": self.panel_background_raised,
            "card.background": self.card_background,
            "card.hover": self.card_hover,
            "border.default": self.border,
            "border.subtle": self.border_subtle,
            "border.strong": self.border_strong,
            "text.primary": self.text_primary,
            "text.secondary": self.text_secondary,
            "text.muted": self.text_muted,
            "text.disabled": self.text_disabled,
            "workflow.selection": self.primary_blue,
            "workflow.connection": self.primary_blue_light,
            "agent.accent": self.agent_violet,
            "media.accent": self.cyan_accent,
            "status.success": self.success,
            "status.warning": self.warning,
            "status.danger": self.danger,
            "status.pending": self.pending,
        }


@dataclass(frozen=True)
class FontTokens:
    ui: tuple[str, ...] = ("Segoe UI", "Microsoft YaHei UI", "system-ui", "sans-serif")
    mono: tuple[str, ...] = ("Cascadia Mono", "Consolas", "Courier New", "monospace")


@dataclass(frozen=True)
class TypographyToken:
    size_px: int
    weight: int


@dataclass(frozen=True)
class TypographyTokens:
    window_title: TypographyToken = TypographyToken(size_px=14, weight=700)
    page_title: TypographyToken = TypographyToken(size_px=20, weight=750)
    panel_title: TypographyToken = TypographyToken(size_px=15, weight=700)
    card_title: TypographyToken = TypographyToken(size_px=14, weight=650)
    body: TypographyToken = TypographyToken(size_px=13, weight=500)
    caption: TypographyToken = TypographyToken(size_px=12, weight=500)
    metadata: TypographyToken = TypographyToken(size_px=11, weight=500)
    metric: TypographyToken = TypographyToken(size_px=32, weight=700)
    log_code: TypographyToken = TypographyToken(size_px=12, weight=400)


@dataclass(frozen=True)
class RadiusTokens:
    panel_px: int = 6
    card_px: int = 6
    control_px: int = 5
    badge_px: int = 4


@dataclass(frozen=True)
class SpacingTokens:
    xxs_px: int = 4
    xs_px: int = 6
    sm_px: int = 8
    md_px: int = 12
    lg_px: int = 16
    xl_px: int = 24


@dataclass(frozen=True)
class WorkflowCanvasTokens:
    node_card_width_px: int = 160
    node_card_height_px: int = 84
    node_gap_x_px: int = 220
    node_gap_y_px: int = 130
    scene_margin_px: int = 48


@dataclass(frozen=True)
class ThemeTokens:
    colors: ColorTokens = ColorTokens()
    fonts: FontTokens = FontTokens()
    typography: TypographyTokens = TypographyTokens()
    radius: RadiusTokens = RadiusTokens()
    spacing: SpacingTokens = SpacingTokens()
    workflow_canvas: WorkflowCanvasTokens = WorkflowCanvasTokens()


ATELIER_THEME_TOKENS = ThemeTokens()


def color(role: str) -> str:
    role_map = ATELIER_THEME_TOKENS.colors.role_map()
    try:
        return role_map[role]
    except KeyError as exc:
        raise KeyError(f"Unknown AtelierUI color role: {role}") from exc
