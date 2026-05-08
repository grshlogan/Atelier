from __future__ import annotations

from dataclasses import dataclass
from html import escape
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
    metadata_filename: str,
    review_page_filename: str,
) -> dict[str, Any]:
    story = state.story_by_id(story_id)
    return {
        "story_id": story.story_id,
        "story_label": story.label,
        "surface": story.surface,
        "reviewer_note": reviewer_note,
        "screenshot_filename": screenshot_filename,
        "metadata_filename": metadata_filename,
        "review_page_filename": review_page_filename,
        "states": [story_state.state_id for story_state in story.states],
        "controls": [control.control_id for control in story.controls],
        "shared_adoption_approved": story.shared_adoption_approved,
    }


def render_review_page_html(snapshot: dict[str, Any]) -> str:
    states = "\n".join(
        f"<li><code>{escape(str(state_id))}</code></li>"
        for state_id in snapshot.get("states", ())
    )
    controls = "\n".join(
        f"<li><code>{escape(str(control_id))}</code></li>"
        for control_id in snapshot.get("controls", ())
    )
    approved = "是" if snapshot.get("shared_adoption_approved") else "否"
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AtelierUI 控件画板审查页</title>
  <style>
    body {{
      margin: 0;
      background: #0A1422;
      color: #F3F7FB;
      font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
      line-height: 1.5;
    }}
    main {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 320px;
      gap: 16px;
      padding: 16px;
    }}
    img {{
      width: 100%;
      height: auto;
      border: 1px solid #2A3A50;
      background: #172332;
    }}
    aside {{
      border: 1px solid #2A3A50;
      padding: 12px;
      background: #172332;
    }}
    h1, h2 {{
      margin: 0 0 12px;
    }}
    dl {{
      margin: 0;
    }}
    dt {{
      margin-top: 10px;
      color: #9FB3C8;
    }}
    dd {{
      margin: 2px 0 0;
    }}
    code {{
      color: #93C5FD;
    }}
    .note {{
      white-space: pre-wrap;
      border: 1px solid #2A3A50;
      padding: 8px;
      background: #0E1A2A;
    }}
  </style>
</head>
<body>
  <main>
    <section>
      <h1>AtelierUI 控件画板审查页</h1>
      <img src="{escape(str(snapshot["screenshot_filename"]))}" alt="控件画板截图">
    </section>
    <aside>
      <h2>{escape(str(snapshot["story_label"]))}</h2>
      <dl>
        <dt>Story ID</dt>
        <dd><code>{escape(str(snapshot["story_id"]))}</code></dd>
        <dt>Surface</dt>
        <dd>{escape(str(snapshot["surface"]))}</dd>
        <dt>共享入库已批准</dt>
        <dd>{approved}</dd>
        <dt>截图文件</dt>
        <dd><code>{escape(str(snapshot["screenshot_filename"]))}</code></dd>
        <dt>Metadata</dt>
        <dd><code>{escape(str(snapshot["metadata_filename"]))}</code></dd>
        <dt>Review Page</dt>
        <dd><code>{escape(str(snapshot["review_page_filename"]))}</code></dd>
      </dl>
      <h2>States</h2>
      <ul>{states}</ul>
      <h2>Controls</h2>
      <ul>{controls}</ul>
      <h2>审查备注</h2>
      <div class="note">{escape(str(snapshot["reviewer_note"]))}</div>
    </aside>
  </main>
</body>
</html>
"""


def build_component_workbench_state() -> ComponentWorkbenchState:
    color_roles = ATELIER_THEME_TOKENS.colors.role_map()
    typography = ATELIER_THEME_TOKENS.typography
    return ComponentWorkbenchState(
        window_title="AtelierUI 控件画板",
        catalog_entries=(
            ComponentCatalogEntry(
                entry_id="video-input-card",
                label="VideoInputCard 候选",
                surface="Workflow Canvas / Node Cards",
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
                story_id="video-input-card",
                label="VideoInputCard 候选",
                surface="Workflow Canvas / Node Cards",
                summary="视频输入节点卡片候选稿，只表达选择媒体 intent，用户审查前不得共享入库。",
                states=(
                    ComponentStoryStateView(state_id="empty", label="未选择媒体"),
                    ComponentStoryStateView(state_id="selected", label="选中态"),
                    ComponentStoryStateView(state_id="hovered", label="悬停态"),
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
                        control_id="media_status",
                        label="媒体状态",
                        control_type="choice",
                        default_value="empty",
                    ),
                    ComponentControlView(
                        control_id="thumbnail",
                        label="缩略图",
                        control_type="choice",
                        default_value="placeholder",
                    ),
                ),
            ),
        ),
    )
