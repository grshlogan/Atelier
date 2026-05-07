"""Atelier-specific local UI foundation.

This package is for shared Atelier GUI tokens and reviewed UI helpers only. It is
not a public UI library and should stay free of Qt import side effects.
"""

from atelier.gui.ui.theme_tokens import ATELIER_THEME_TOKENS, color
from atelier.gui.ui.widget_intake import (
    SELF_PAINTED_WIDGET_INTAKE_STEPS,
    is_approved_for_shared_adoption,
    required_intake_step_ids,
    requires_user_review_before_shared_adoption,
)

__all__ = [
    "ATELIER_THEME_TOKENS",
    "SELF_PAINTED_WIDGET_INTAKE_STEPS",
    "color",
    "is_approved_for_shared_adoption",
    "required_intake_step_ids",
    "requires_user_review_before_shared_adoption",
]
