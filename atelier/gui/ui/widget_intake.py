from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WidgetIntakeStep:
    step_id: str
    title: str
    required: bool = True


SELF_PAINTED_WIDGET_INTAKE_STEPS: tuple[WidgetIntakeStep, ...] = (
    WidgetIntakeStep(
        step_id="purpose",
        title="说明控件目的、所属界面、调用位置和不负责的边界",
    ),
    WidgetIntakeStep(
        step_id="reference_review",
        title="先调研参考项目或参考代码，再设计 Atelier 专属版本",
    ),
    WidgetIntakeStep(
        step_id="minimal_test",
        title="实现前先补失败的单元测试、GUI smoke 或可复查视觉验证路径",
    ),
    WidgetIntakeStep(
        step_id="atelier_specific_implementation",
        title="实现最小 PySide6-native 候选，不复制不兼容代码",
    ),
    WidgetIntakeStep(
        step_id="user_review",
        title="共享入库和产品调用前必须经过用户审查",
    ),
)


def required_intake_step_ids() -> tuple[str, ...]:
    return tuple(step.step_id for step in SELF_PAINTED_WIDGET_INTAKE_STEPS if step.required)


def requires_user_review_before_shared_adoption(candidate_name: str) -> bool:
    return bool(candidate_name.strip())


def is_approved_for_shared_adoption(candidate_name: str) -> bool:
    return False
