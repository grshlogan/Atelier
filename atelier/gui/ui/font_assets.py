from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from pathlib import Path

from atelier.gui.entry import ensure_gui_dependency

ensure_gui_dependency()

from PySide6.QtGui import QFontDatabase


@dataclass(frozen=True)
class AtelierUIFontFamilies:
    ui: str
    ui_light: str
    ui_regular: str
    ui_medium: str
    ui_semibold: str
    ui_bold: str


def _fonts_root() -> Path:
    return Path(__file__).resolve().parents[2] / "assets" / "fonts"


def _choose_stable_family_name(families: list[str]) -> str:
    for family in families:
        if family.isascii() and family:
            return family
    return families[0]


def _load_font_family(path: Path) -> str:
    font_id = QFontDatabase.addApplicationFont(str(path))
    if font_id < 0:
        raise RuntimeError(f"Failed to load font asset: {path}")
    families = QFontDatabase.applicationFontFamilies(font_id)
    if not families:
        raise RuntimeError(f"Font asset reported no family name: {path}")
    return _choose_stable_family_name(families)


@cache
def load_atelier_ui_font_families() -> AtelierUIFontFamilies:
    root = _fonts_root()
    jiangcheng_root = root / "jiangcheng_yuanti"
    ui_light = _load_font_family(jiangcheng_root / "JiangChengYuanTi-300W.ttf")
    ui_regular = _load_font_family(jiangcheng_root / "JiangChengYuanTi-400W.ttf")
    ui_medium = _load_font_family(jiangcheng_root / "JiangChengYuanTi-500W.ttf")
    ui_semibold = _load_font_family(jiangcheng_root / "JiangChengYuanTi-600W.ttf")
    ui_bold = _load_font_family(jiangcheng_root / "JiangChengYuanTi-700W.ttf")
    return AtelierUIFontFamilies(
        ui=ui_regular,
        ui_light=ui_light,
        ui_regular=ui_regular,
        ui_medium=ui_medium,
        ui_semibold=ui_semibold,
        ui_bold=ui_bold,
    )
