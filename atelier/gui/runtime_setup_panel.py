from __future__ import annotations

from pathlib import Path
from typing import Callable, Protocol

from atelier.runtime.registration import RuntimeRegistrationError
from atelier.gui.runtime_setup_state import RuntimeSetupItemView, build_runtime_setup_view_state
from atelier.runtime.setup import RuntimeSetupSnapshot

from PySide6.QtWidgets import QFileDialog, QLabel, QPushButton, QVBoxLayout, QWidget


class RuntimeSetupServiceProtocol(Protocol):
    def refresh_snapshot(self) -> RuntimeSetupSnapshot:
        ...

    def register_ffprobe_path(self, executable_path: str | Path) -> RuntimeSetupSnapshot:
        ...

    def register_ffmpeg_path(self, executable_path: str | Path) -> RuntimeSetupSnapshot:
        ...

    def register_worker_python_path(self, executable_path: str | Path) -> RuntimeSetupSnapshot:
        ...

    def register_demo_model_path(self, model_path: str | Path) -> RuntimeSetupSnapshot:
        ...


class RuntimeSetupPanel(QWidget):
    def __init__(
        self,
        snapshot: RuntimeSetupSnapshot | None = None,
        runtime_setup_service: RuntimeSetupServiceProtocol | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("runtime-setup-panel-content")
        self._service = runtime_setup_service
        self._snapshot = snapshot or RuntimeSetupSnapshot()

        layout = QVBoxLayout(self)
        self._summary_label = QLabel()
        self._summary_label.setObjectName("runtime-setup-summary")
        self._summary_label.setWordWrap(True)
        layout.addWidget(self._summary_label)

        self._error_label = QLabel()
        self._error_label.setObjectName("runtime-setup-error")
        self._error_label.setWordWrap(True)
        layout.addWidget(self._error_label)

        self._components_label = QLabel()
        self._components_label.setObjectName("runtime-setup-components")
        self._components_label.setWordWrap(True)
        layout.addWidget(self._components_label)

        self._models_label = QLabel()
        self._models_label.setObjectName("runtime-setup-models")
        self._models_label.setWordWrap(True)
        layout.addWidget(self._models_label)

        self._buttons = {
            "register_ffprobe": self._create_button(
                "runtime-setup-register-ffprobe",
                "Register FFprobe",
                lambda: self._choose_executable("Select FFprobe executable", self.register_ffprobe_path),
            ),
            "register_ffmpeg": self._create_button(
                "runtime-setup-register-ffmpeg",
                "Register FFmpeg",
                lambda: self._choose_executable("Select FFmpeg executable", self.register_ffmpeg_path),
            ),
            "register_worker_python": self._create_button(
                "runtime-setup-register-worker-python",
                "Register Worker Python",
                lambda: self._choose_executable(
                    "Select Worker Python executable",
                    self.register_worker_python_path,
                ),
            ),
            "register_demo_model": self._create_button(
                "runtime-setup-register-demo-model",
                "Register Demo Model",
                lambda: self._choose_directory("Select demo model directory", self.register_demo_model_path),
            ),
            "refresh": self._create_button(
                "runtime-setup-refresh",
                "Refresh",
                self.refresh_from_service,
            ),
        }
        for button in self._buttons.values():
            layout.addWidget(button)

        layout.addStretch(1)
        self.refresh_snapshot(self._snapshot)

    def refresh_snapshot(self, snapshot: RuntimeSetupSnapshot) -> None:
        self._snapshot = snapshot
        state = build_runtime_setup_view_state(snapshot)
        self._summary_label.setText(
            f"{state.summary.ready_runtime_count} / {state.summary.runtime_count} runtimes ready | "
            f"{state.summary.model_count} models | "
            f"{state.summary.problem_count} problems"
        )
        self._components_label.setText(
            _format_items(state.components, empty_text="No runtime components registered")
        )
        self._models_label.setText(_format_items(state.models, empty_text="No model assets registered"))
        for action_id, button in self._buttons.items():
            action = state.actions[action_id]
            button.setEnabled(bool(self._service is not None and action.enabled))
            button.setToolTip(action.disabled_reason)

    def refresh_from_service(self) -> None:
        if self._service is None:
            self._show_error("Runtime setup service is unavailable.")
            return
        self._error_label.setText("")
        self.refresh_snapshot(self._service.refresh_snapshot())

    def register_ffprobe_path(self, executable_path: str | Path) -> None:
        self._run_registration(lambda service: service.register_ffprobe_path(executable_path))

    def register_ffmpeg_path(self, executable_path: str | Path) -> None:
        self._run_registration(lambda service: service.register_ffmpeg_path(executable_path))

    def register_worker_python_path(self, executable_path: str | Path) -> None:
        self._run_registration(lambda service: service.register_worker_python_path(executable_path))

    def register_demo_model_path(self, model_path: str | Path) -> None:
        self._run_registration(lambda service: service.register_demo_model_path(model_path))

    def _create_button(
        self,
        object_name: str,
        label: str,
        callback: Callable[[], None],
    ) -> QPushButton:
        button = QPushButton(label)
        button.setObjectName(object_name)
        button.clicked.connect(callback)
        return button

    def _choose_executable(
        self,
        title: str,
        handler: Callable[[Path], None],
    ) -> None:
        selected_path, _ = QFileDialog.getOpenFileName(self, title)
        if selected_path:
            handler(Path(selected_path))

    def _choose_directory(
        self,
        title: str,
        handler: Callable[[Path], None],
    ) -> None:
        selected_path = QFileDialog.getExistingDirectory(self, title)
        if selected_path:
            handler(Path(selected_path))

    def _run_registration(
        self,
        action: Callable[[RuntimeSetupServiceProtocol], RuntimeSetupSnapshot],
    ) -> None:
        if self._service is None:
            self._show_error("Runtime setup service is unavailable.")
            return
        try:
            snapshot = action(self._service)
        except RuntimeRegistrationError as exc:
            self._show_error(str(exc))
            return
        self._error_label.setText("")
        self.refresh_snapshot(snapshot)

    def _show_error(self, message: str) -> None:
        self._error_label.setText(message)


def create_runtime_setup_panel(
    snapshot: RuntimeSetupSnapshot | None = None,
    runtime_setup_service: RuntimeSetupServiceProtocol | None = None,
) -> RuntimeSetupPanel:
    return RuntimeSetupPanel(snapshot, runtime_setup_service)


def _format_items(items: list[RuntimeSetupItemView], *, empty_text: str) -> str:
    if not items:
        return empty_text
    return "\n\n".join(_format_item(item) for item in items)


def _format_item(item: RuntimeSetupItemView) -> str:
    lines = [
        item.title,
        item.subtitle,
        item.status_label,
        *item.detail_lines,
    ]
    return "\n".join(line for line in lines if line)
