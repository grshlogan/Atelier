# UI Motion Spec Plan

## Objective

Write `docs/UI_MOTION_SPEC.md` to define Atelier's project-specific UI motion system and open-source reference boundaries.

## Scope

- Document-only change.
- Cover `AtelierUI` motion concepts: theme tokens, easing curves, animation driver, motion values, overlay layer, self-painted widgets, queue delegate animation, and page transition manager.
- Classify the provided open-source animation references as learning sources, not current dependencies.

## Current Facts

- `DESIGN.md` is the design source of truth.
- `docs/Atelier_Main_UI_Spec.md` contains first-pass motion timings and PySide6 implementation suggestions.
- `docs/UI_WORKSPACE_SPEC.md` defines the dockable workspace and collapsible sidebar direction.
- Current GUI code is a minimal PySide6 `QMainWindow` with dock widgets and no implemented motion layer.

## Constraints

- Atelier remains PySide6 Widgets first.
- Do not introduce a mature reusable UI library.
- Do not claim any open-source project has been imported or vendored.
- Treat GPL or unlicensed reference projects as read-only inspiration unless a future legal review says otherwise.

## Execution Plan

1. Add the motion spec with status, source-of-truth relationship, reference list, library boundary, implementation model, performance rules, and future phases.
2. Verify the document is readable and references real local files and public project URLs.

## Child Plans

None.

## Verification

- Read the created Markdown file.
- Run `git diff -- docs/UI_MOTION_SPEC.md docs/plan/plan_ui_motion_spec.md`.

## Progress / Decisions

- Decision: write a project-specific `AtelierUI` spec, not a general-purpose UI toolkit proposal.
- Completed `docs/UI_MOTION_SPEC.md` with motion tokens, driver boundaries, component responsibilities, implementation phases, validation guidance, and open-source reference policy.
- Added `docs/UI_MOTION_SPEC.md` to the `README.md` document index.
- Validation performed: read `docs/UI_MOTION_SPEC.md` with `Get-Content -Encoding UTF8`; checked `git status --short`.

## Blockers

None.
