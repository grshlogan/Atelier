from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from atelier.gui.state_reader import WorkbenchSnapshot


@dataclass(frozen=True)
class WorkspacePanelSpec:
    object_name: str
    title: str
    area: Qt.DockWidgetArea
    body: str


DEFAULT_WORKSPACE_PANELS = (
    WorkspacePanelSpec(
        object_name="workflow-panel",
        title="Workflow",
        area=Qt.DockWidgetArea.LeftDockWidgetArea,
        body="Read-only workflow state",
    ),
    WorkspacePanelSpec(
        object_name="execution-panel",
        title="Execution",
        area=Qt.DockWidgetArea.RightDockWidgetArea,
        body="Read-only execution plan",
    ),
    WorkspacePanelSpec(
        object_name="queue-panel",
        title="Queue",
        area=Qt.DockWidgetArea.BottomDockWidgetArea,
        body="Read-only queue monitor",
    ),
    WorkspacePanelSpec(
        object_name="resources-runtime-panel",
        title="Resources / Runtime",
        area=Qt.DockWidgetArea.RightDockWidgetArea,
        body="Read-only resources and runtime",
    ),
)


def create_workspace_panel(
    spec: WorkspacePanelSpec,
    data_root: Path,
    snapshot: WorkbenchSnapshot | None = None,
) -> QWidget:
    panel = QWidget()
    panel.setObjectName(f"{spec.object_name}-content")

    layout = QVBoxLayout(panel)
    title = QLabel(spec.title)
    title.setObjectName(f"{spec.object_name}-title")
    body = QLabel(_panel_body(spec, data_root, snapshot))
    body.setObjectName(f"{spec.object_name}-body")
    body.setWordWrap(True)

    layout.addWidget(title)
    layout.addWidget(body)
    layout.addStretch(1)
    return panel


def _panel_body(
    spec: WorkspacePanelSpec,
    data_root: Path,
    snapshot: WorkbenchSnapshot | None,
) -> str:
    if spec.object_name != "queue-panel" or snapshot is None:
        return f"{spec.body}\nData: {data_root}"
    if not snapshot.tasks:
        return "No queued tasks"

    lines: list[str] = []
    for task in snapshot.tasks:
        resource = task.resource_device_id or "-"
        lines.append(
            f"{task.task_id} | {task.node_type} | {task.status} | "
            f"{resource} | events: {task.event_count}"
        )
        for artifact_path in task.artifact_paths:
            lines.append(f"artifact: {artifact_path}")
        for final_output_path in task.final_output_paths:
            lines.append(f"final output: {final_output_path}")
        if task.failure_error_code or task.failure_message:
            code = task.failure_error_code or "-"
            message = task.failure_message or "-"
            lines.append(f"failure: {code} | {message}")
    return "\n".join(lines)
