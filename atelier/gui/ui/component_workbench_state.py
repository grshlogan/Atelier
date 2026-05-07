from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from atelier.gui.ui.theme_tokens import ATELIER_THEME_TOKENS
from atelier.gui.ui.widget_intake import SELF_PAINTED_WIDGET_INTAKE_STEPS, WidgetIntakeStep


@dataclass(frozen=True)
class ComponentCatalogEntry:
    entry_id: str
    label: str
    surface: str


@dataclass(frozen=True)
class ColorSwatchView:
    role: str
    value: str


@dataclass(frozen=True)
class TypographySampleView:
    sample_id: str
    label: str
    size_px: int
    weight: int


@dataclass(frozen=True)
class ComponentStoryStateView:
    state_id: str
    label: str


@dataclass(frozen=True)
class ComponentControlView:
    control_id: str
    label: str
    control_type: str
    default_value: bool | str | int


@dataclass(frozen=True)
class ComponentStoryView:
    story_id: str
    label: str
    surface: str
    summary: str
    states: tuple[ComponentStoryStateView, ...] = ()
    controls: tuple[ComponentControlView, ...] = ()
    shared_adoption_approved: bool = False

    def control_by_id(self, control_id: str) -> ComponentControlView:
        for control in self.controls:
            if control.control_id == control_id:
                return control
        raise KeyError(f"未知 AtelierUI 控件画板 control: {control_id}")


@dataclass(frozen=True)
class ComponentWorkbenchState:
    window_title: str
    catalog_entries: tuple[ComponentCatalogEntry, ...]
    color_swatches: tuple[ColorSwatchView, ...]
    typography_samples: tuple[TypographySampleView, ...]
    intake_steps: tuple[WidgetIntakeStep, ...]
    stories: tuple[ComponentStoryView, ...]

    def story_by_id(self, story_id: str) -> ComponentStoryView:
        for story in self.stories:
            if story.story_id == story_id:
                return story
        raise KeyError(f"未知 AtelierUI 控件画板 story: {story_id}")


def build_review_snapshot_record(
    *,
    state: ComponentWorkbenchState,
    story_id: str,
    reviewer_note: str,
    screenshot_filename: str,
) -> dict[str, Any]:
    story = state.story_by_id(story_id)
    return {
        "story_id": story.story_id,
        "story_label": story.label,
        "surface": story.surface,
        "reviewer_note": reviewer_note,
        "screenshot_filename": screenshot_filename,
        "states": [story_state.state_id for story_state in story.states],
        "controls": [control.control_id for control in story.controls],
        "shared_adoption_approved": story.shared_adoption_approved,
    }


def build_component_workbench_state() -> ComponentWorkbenchState:
    color_roles = ATELIER_THEME_TOKENS.colors.role_map()
    typography = ATELIER_THEME_TOKENS.typography
    return ComponentWorkbenchState(
        window_title="AtelierUI 控件画板",
        catalog_entries=(
            ComponentCatalogEntry(
                entry_id="tokens",
                label="主题 Tokens",
                surface="AtelierUI",
            ),
            ComponentCatalogEntry(
                entry_id="workflow-node",
                label="WorkflowNodeItem 候选",
                surface="Workflow Canvas",
            ),
        ),
        color_swatches=tuple(
            ColorSwatchView(role=role, value=value)
            for role, value in color_roles.items()
            if role
            in {
                "canvas.background",
                "card.background",
                "card.hover",
                "border.strong",
                "text.primary",
                "workflow.selection",
                "status.danger",
            }
        ),
        typography_samples=(
            TypographySampleView(
                sample_id="card_title",
                label="卡片标题",
                size_px=typography.card_title.size_px,
                weight=typography.card_title.weight,
            ),
            TypographySampleView(
                sample_id="metadata",
                label="元信息",
                size_px=typography.metadata.size_px,
                weight=typography.metadata.weight,
            ),
        ),
        intake_steps=SELF_PAINTED_WIDGET_INTAKE_STEPS,
        stories=(
            ComponentStoryView(
                story_id="tokens",
                label="主题 Tokens",
                surface="AtelierUI",
                summary="预览颜色 token、字体样式、圆角和间距。",
                states=(
                    ComponentStoryStateView(state_id="default", label="默认"),
                ),
                controls=(
                    ComponentControlView(
                        control_id="background",
                        label="背景",
                        control_type="choice",
                        default_value="canvas.background",
                    ),
                ),
            ),
            ComponentStoryView(
                story_id="workflow-node",
                label="WorkflowNodeItem 候选",
                surface="Workflow Canvas",
                summary="未来自绘工作流节点卡片的占位 story，用户审查前不得共享入库。",
                states=(
                    ComponentStoryStateView(state_id="normal", label="默认态"),
                    ComponentStoryStateView(state_id="hovered", label="悬停态"),
                    ComponentStoryStateView(state_id="selected", label="选中态"),
                ),
                controls=(
                    ComponentControlView(
                        control_id="selected",
                        label="选中态",
                        control_type="toggle",
                        default_value=False,
                    ),
                    ComponentControlView(
                        control_id="hovered",
                        label="悬停态",
                        control_type="toggle",
                        default_value=False,
                    ),
                    ComponentControlView(
                        control_id="density",
                        label="密度",
                        control_type="choice",
                        default_value="compact",
                    ),
                ),
            ),
        ),
    )
