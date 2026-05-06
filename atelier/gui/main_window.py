from __future__ import annotations

from atelier.app.paths import AppPaths
from atelier.gui.entry import ensure_gui_dependency

ensure_gui_dependency()

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtWidgets import QLabel, QDockWidget, QMainWindow, QPushButton, QVBoxLayout, QWidget

from atelier.gui.layout_store import WorkspaceLayoutStore
from atelier.gui.runtime_setup_panel import RuntimeSetupServiceProtocol, create_runtime_setup_panel
from atelier.gui.state_reader import WorkbenchSnapshot
from atelier.gui.workflow_run_intent import WorkflowRunIntentExecutor, WorkflowRunIntentServiceProtocol
from atelier.gui.workspace import DEFAULT_WORKSPACE_PANELS, create_workspace_panel
from atelier.runtime.setup import RuntimeSetupSnapshot


class MainWindow(QMainWindow):
    def __init__(
        self,
        app_paths: AppPaths,
        snapshot: WorkbenchSnapshot | None = None,
        runtime_setup_snapshot: RuntimeSetupSnapshot | None = None,
        runtime_setup_service: RuntimeSetupServiceProtocol | None = None,
        active_plan_id: str | None = None,
        workflow_run_intent_service: WorkflowRunIntentServiceProtocol | None = None,
        workflow_run_intent_executor: WorkflowRunIntentExecutor | None = None,
    ) -> None:
        super().__init__()
        self.app_paths = app_paths
        self.snapshot = snapshot
        self.runtime_setup_snapshot = runtime_setup_snapshot
        self.runtime_setup_service = runtime_setup_service
        self.active_plan_id = active_plan_id
        self.workflow_run_intent_service = workflow_run_intent_service
        self.workflow_run_intent_executor = workflow_run_intent_executor
        self._owns_workflow_run_intent_executor = workflow_run_intent_executor is None
        self.workflow_run_status_label: QLabel | None = None
        self.setObjectName("atelier-main-window")
        self.setWindowTitle("Atelier")
        self.resize(1440, 900)
        self.setCentralWidget(self._create_workstation_center())
        self._install_workspace_docks()
        self._install_runtime_setup_dock()

    def _create_workstation_center(self) -> QWidget:
        center = QWidget()
        center.setObjectName("workflow-canvas-placeholder")
        layout = QVBoxLayout(center)
        title = QLabel("Workflow Canvas")
        title.setObjectName("workflow-canvas-title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        run_button = QPushButton("Run Workflow")
        run_button.setObjectName("workflow-run-intent-button")
        run_button.setEnabled(
            self.active_plan_id is not None and self.workflow_run_intent_service is not None
        )
        run_button.clicked.connect(self._request_workflow_run)
        self.workflow_run_status_label = QLabel("No workflow run requested")
        self.workflow_run_status_label.setObjectName("workflow-run-intent-status")
        self.workflow_run_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)
        layout.addWidget(title)
        layout.addWidget(run_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.workflow_run_status_label)
        layout.addStretch(1)
        return center

    def _request_workflow_run(self) -> None:
        if self.active_plan_id is None or self.workflow_run_intent_service is None:
            return
        executor = self._workflow_run_intent_executor()
        executor.submit(
            service=self.workflow_run_intent_service,
            plan_id=self.active_plan_id,
        )
        if self.workflow_run_status_label is not None:
            self.workflow_run_status_label.setText(f"Run requested: {self.active_plan_id}")

    def _workflow_run_intent_executor(self) -> WorkflowRunIntentExecutor:
        if self.workflow_run_intent_executor is None:
            self.workflow_run_intent_executor = WorkflowRunIntentExecutor()
        return self.workflow_run_intent_executor

    def closeEvent(self, event) -> None:  # noqa: N802
        if self._owns_workflow_run_intent_executor and self.workflow_run_intent_executor is not None:
            self.workflow_run_intent_executor.shutdown(wait=False)
        super().closeEvent(event)

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

    def _install_runtime_setup_dock(self) -> None:
        dock = QDockWidget("Runtime Setup", self)
        dock.setObjectName("runtime-setup-panel")
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        dock.setWidget(
            create_runtime_setup_panel(
                self.runtime_setup_snapshot,
                self.runtime_setup_service,
            )
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

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
