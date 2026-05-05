from __future__ import annotations

from dataclasses import dataclass

from atelier.runtime.setup import RuntimeSetupSnapshot


@dataclass(frozen=True)
class RuntimeSetupSummaryView:
    runtime_count: int
    model_count: int
    ready_runtime_count: int
    problem_count: int


@dataclass(frozen=True)
class RuntimeSetupItemView:
    item_id: str
    title: str
    subtitle: str
    status: str
    status_label: str
    detail_lines: list[str]


@dataclass(frozen=True)
class RuntimeSetupActionView:
    action_id: str
    label: str
    enabled: bool
    disabled_reason: str = ""


@dataclass(frozen=True)
class RuntimeSetupViewState:
    summary: RuntimeSetupSummaryView
    components: list[RuntimeSetupItemView]
    models: list[RuntimeSetupItemView]
    actions: dict[str, RuntimeSetupActionView]


def build_runtime_setup_view_state(snapshot: RuntimeSetupSnapshot) -> RuntimeSetupViewState:
    runtime_ids = {runtime.runtime_id for runtime in snapshot.runtimes}
    model_ids = {model.model_id for model in snapshot.models}
    return RuntimeSetupViewState(
        summary=RuntimeSetupSummaryView(
            runtime_count=snapshot.runtime_count,
            model_count=snapshot.model_count,
            ready_runtime_count=snapshot.ready_runtime_count,
            problem_count=snapshot.problem_count,
        ),
        components=[
            RuntimeSetupItemView(
                item_id=runtime.runtime_id,
                title=runtime.display_name or runtime.runtime_id,
                subtitle=_join_non_empty(runtime.component, runtime.version, runtime.profile_kind),
                status=runtime.status,
                status_label=_status_label(runtime.status),
                detail_lines=_runtime_detail_lines(
                    capabilities=runtime.capabilities,
                    issues=runtime.issues,
                    repair_hints=runtime.repair_hints,
                ),
            )
            for runtime in snapshot.runtimes
        ],
        models=[
            RuntimeSetupItemView(
                item_id=model.model_id,
                title=model.display_name or model.model_id,
                subtitle=_join_non_empty(model.backend, model.model_family, model.profile_kind),
                status=model.status,
                status_label=_status_label(model.status),
                detail_lines=_model_detail_lines(
                    task_types=model.task_types,
                    capabilities=model.capabilities,
                    issues=model.issues,
                    repair_hints=model.repair_hints,
                ),
            )
            for model in snapshot.models
        ],
        actions={
            "register_ffprobe": _registration_action(
                action_id="register_ffprobe",
                label="Register FFprobe",
                target_id="ffprobe-local",
                existing_ids=runtime_ids,
            ),
            "register_ffmpeg": _registration_action(
                action_id="register_ffmpeg",
                label="Register FFmpeg",
                target_id="ffmpeg-local",
                existing_ids=runtime_ids,
            ),
            "register_worker_python": _registration_action(
                action_id="register_worker_python",
                label="Register Worker Python",
                target_id="python-worker-dev",
                existing_ids=runtime_ids,
            ),
            "register_demo_model": _registration_action(
                action_id="register_demo_model",
                label="Register Demo Model",
                target_id="demo-model-local",
                existing_ids=model_ids,
            ),
            "refresh": RuntimeSetupActionView(
                action_id="refresh",
                label="Refresh",
                enabled=True,
            ),
        },
    )


def _registration_action(
    *,
    action_id: str,
    label: str,
    target_id: str,
    existing_ids: set[str],
) -> RuntimeSetupActionView:
    if target_id in existing_ids:
        return RuntimeSetupActionView(
            action_id=action_id,
            label=label,
            enabled=False,
            disabled_reason=f"{target_id} is already registered",
        )
    return RuntimeSetupActionView(action_id=action_id, label=label, enabled=True)


def _runtime_detail_lines(
    *,
    capabilities: list[str],
    issues: list[str],
    repair_hints: list[str],
) -> list[str]:
    lines = [*issues]
    lines.extend(f"hint: {hint}" for hint in repair_hints)
    if not lines and capabilities:
        lines.append(", ".join(capabilities))
    return lines


def _model_detail_lines(
    *,
    task_types: list[str],
    capabilities: list[str],
    issues: list[str],
    repair_hints: list[str],
) -> list[str]:
    lines = [*issues]
    lines.extend(f"hint: {hint}" for hint in repair_hints)
    if not lines:
        if task_types:
            lines.append(f"tasks: {', '.join(task_types)}")
        if capabilities:
            lines.append(f"capabilities: {', '.join(capabilities)}")
    return lines


def _join_non_empty(*values: str) -> str:
    return " | ".join(value for value in values if value)


def _status_label(status: str) -> str:
    return status.replace("_", " ").title()
