from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from atelier.app.paths import AppPaths
from atelier.app.runtime_setup import RuntimeSetupAppService
from atelier.app.services import create_runtime_setup_service, open_app_database
from atelier.gui.entry import ensure_gui_dependency
from atelier.runtime.setup import RuntimeSetupSnapshot

ensure_gui_dependency()

from PySide6.QtWidgets import QApplication

from atelier.gui.layout_store import WorkspaceLayoutStore
from atelier.gui.main_window import MainWindow
from atelier.gui.state_reader import WorkbenchSnapshot, read_workbench_snapshot


@dataclass(frozen=True)
class LaunchArgs:
    workspace_root: Path | None
    data_root: Path | None
    restore_layout: bool


@dataclass(frozen=True)
class GuiLaunchContext:
    app_paths: AppPaths
    connection: sqlite3.Connection
    snapshot: WorkbenchSnapshot
    runtime_setup_snapshot: RuntimeSetupSnapshot
    runtime_setup_service: RuntimeSetupAppService
    window: MainWindow
    layout_restored: bool


def parse_launch_args(argv: Sequence[str] | None = None) -> LaunchArgs:
    parser = argparse.ArgumentParser(description="Launch the Atelier read-only workbench.")
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path("."),
        help="Workspace root used for development AppPaths.",
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=None,
        help="Explicit AtelierData root. Overrides --workspace-root when supplied.",
    )
    parser.add_argument(
        "--no-restore-layout",
        action="store_false",
        dest="restore_layout",
        help="Do not restore the saved workspace layout.",
    )
    parser.set_defaults(restore_layout=True)
    namespace = parser.parse_args(argv)
    return LaunchArgs(
        workspace_root=namespace.workspace_root,
        data_root=namespace.data_root,
        restore_layout=namespace.restore_layout,
    )


def resolve_app_paths(args: LaunchArgs) -> AppPaths:
    if args.data_root is not None:
        return AppPaths.from_data_root(args.data_root)
    workspace_root = args.workspace_root or Path(".")
    return AppPaths.for_development(workspace_root)


def build_launch_context(args: LaunchArgs) -> GuiLaunchContext:
    app_paths = resolve_app_paths(args)
    connection = open_app_database(app_paths)
    snapshot = read_workbench_snapshot(connection)
    runtime_setup_service = create_runtime_setup_service(app_paths)
    runtime_setup_snapshot = runtime_setup_service.refresh_snapshot()
    window = MainWindow(
        app_paths=app_paths,
        snapshot=snapshot,
        runtime_setup_snapshot=runtime_setup_snapshot,
        runtime_setup_service=runtime_setup_service,
    )
    layout_restored = False
    if args.restore_layout:
        layout_restored = window.restore_workspace_layout(WorkspaceLayoutStore(app_paths))
    return GuiLaunchContext(
        app_paths=app_paths,
        connection=connection,
        snapshot=snapshot,
        runtime_setup_snapshot=runtime_setup_snapshot,
        runtime_setup_service=runtime_setup_service,
        window=window,
        layout_restored=layout_restored,
    )


def main(argv: Sequence[str] | None = None) -> int:
    app = QApplication.instance() or QApplication([])
    context = build_launch_context(parse_launch_args(argv))
    try:
        context.window.show()
        return int(app.exec())
    finally:
        context.connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
