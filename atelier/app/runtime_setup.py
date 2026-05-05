from __future__ import annotations

from pathlib import Path

from atelier.runtime.health import RuntimeHealthChecker
from atelier.runtime.registration import RuntimeRegistrationService
from atelier.runtime.setup import RuntimeSetupSnapshot, build_runtime_setup_snapshot
from atelier.runtime.store import RuntimeStore


class RuntimeSetupAppService:
    def __init__(self, store: RuntimeStore, checker: RuntimeHealthChecker) -> None:
        self.store = store
        self.checker = checker
        self.registration = RuntimeRegistrationService(store)

    def refresh_snapshot(self) -> RuntimeSetupSnapshot:
        return build_runtime_setup_snapshot(self.store, self.checker)

    def register_ffprobe_path(self, executable_path: str | Path) -> RuntimeSetupSnapshot:
        self.registration.register_local_executable(
            runtime_id="ffprobe-local",
            component="ffprobe",
            executable_path=executable_path,
            display_name="FFprobe Local",
            executable_name="ffprobe",
            capabilities=["metadata", "video", "audio"],
        )
        return self.refresh_snapshot()

    def register_ffmpeg_path(self, executable_path: str | Path) -> RuntimeSetupSnapshot:
        self.registration.register_local_executable(
            runtime_id="ffmpeg-local",
            component="ffmpeg",
            executable_path=executable_path,
            display_name="FFmpeg Local",
            executable_name="ffmpeg",
            capabilities=["video", "audio", "mux"],
        )
        return self.refresh_snapshot()

    def register_worker_python_path(self, executable_path: str | Path) -> RuntimeSetupSnapshot:
        self.registration.register_worker_python(
            runtime_id="python-worker-dev",
            executable_path=executable_path,
        )
        return self.refresh_snapshot()

    def register_demo_model_path(self, model_path: str | Path) -> RuntimeSetupSnapshot:
        self.registration.register_model_asset(
            model_id="demo-model-local",
            local_path=model_path,
            backend="simulated",
            display_name="Demo Model",
            model_family="demo",
            task_types=["demo"],
            compatible_backends=["simulated"],
            capabilities=["demo"],
        )
        return self.refresh_snapshot()
