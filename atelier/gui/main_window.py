from __future__ import annotations

from atelier.app.paths import AppPaths
from atelier.gui.entry import ensure_gui_dependency

ensure_gui_dependency()

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtWidgets import QLabel, QDockWidget, QMainWindow

from atelier.gui.layout_store import WorkspaceLayoutStore
from atelier.gui.state_reader import WorkbenchSnapshot
from atelier.gui.workspace import DEFAULT_WORKSPACE_PANELS, create_workspace_panel


class MainWindow(QMainWindow):
    def __init__(self, app_paths: AppPaths, snapshot: WorkbenchSnapshot | None = None) -> None:
        super().__init__()
        self.app_paths = app_paths
        self.snapshot = snapshot
        self.setObjectName("atelier-main-window")
        self.setWindowTitle("Atelier")
        self.resize(1440, 900)
        self.setCentralWidget(self._create_workstation_center())
        self._install_workspace_docks()

    def _create_workstation_center(self) -> QLabel:
        center = QLabel("Workflow Canvas")
        center.setObjectName("workflow-canvas-placeholder")
        center.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return center

    def _install_workspace_docks(self) -> None:
        for spec in DEFAULT_WORKSPACE_PANELS:
            dock = QDockWidget(spec.title, self)
            dock.setObjectName(spec.object_name)
            dock.setFeatures(
                QDockWidget.DockWidgetFeature.DockWidgetMovable
                | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            )
            dock.setWidget(create_workspace_panel(spec, self.app_paths.data_root, self.snapshot))
            self.addDockWidget(spec.area, dock)

    def save_workspace_layout(
        self,
        store: WorkspaceLayoutStore,
        *,
        name: str = "default",
    ) -> None:
        store.save_layout(
            name,
            geometry=bytes(self.saveGeometry()),
            state=bytes(self.saveState()),
        )

    def restore_workspace_layout(
        self,
        store: WorkspaceLayoutStore,
        *,
        name: str = "default",
    ) -> bool:
        record = store.load_layout(name)
        if record is None:
            return False
        geometry_restored = self.restoreGeometry(QByteArray(record.geometry))
        state_restored = self.restoreState(QByteArray(record.state))
        return bool(geometry_restored and state_restored)
