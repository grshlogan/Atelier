from __future__ import annotations

import importlib.util
from dataclasses import dataclass


GUI_EXTRA_INSTALL_COMMAND = '.venv/Scripts/python -m pip install -e ".[gui]"'
PYSIDE6_PACKAGE_NAME = "PySide6"


@dataclass(frozen=True)
class GuiDependencyStatus:
    package_name: str
    available: bool
    install_command: str


def check_gui_dependency() -> GuiDependencyStatus:
    return GuiDependencyStatus(
        package_name=PYSIDE6_PACKAGE_NAME,
        available=importlib.util.find_spec(PYSIDE6_PACKAGE_NAME) is not None,
        install_command=GUI_EXTRA_INSTALL_COMMAND,
    )


def ensure_gui_dependency() -> None:
    status = check_gui_dependency()
    if status.available:
        return
    raise RuntimeError(
        f"{status.package_name} is not installed. Install GUI extras with: "
        f"{status.install_command}"
    )
