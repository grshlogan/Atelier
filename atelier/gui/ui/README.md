# AtelierUI

`atelier.gui.ui` is Atelier's local, project-specific UI foundation.

It is not a public UI library, not a PyPI package, and not a mature external dependency. It should ship only as Atelier runtime or core application code.

Current scope:

- `component_workbench_state.py`: pure Python catalog, story, token preview, typography preview, and intake checklist state for the dev-only component workbench.
- `component_workbench.py`: PySide6 dev-only workbench entry for reviewing AtelierUI candidates outside the product `MainWindow`.
- `theme_tokens.py`: pure Python visual tokens sourced from `DESIGN.md`.
- `widget_intake.py`: required review checklist for future self-painted widgets.

Rules:

- Do not import PySide6 from package import side effects.
- Do not run workers, FFmpeg, model inference, hardware scheduling, shell commands, or storage mutations.
- Do not add new self-painted widgets to this local library before user review.
- If reference projects or reference code exist, review them first and implement an Atelier-specific version without copying incompatible code.

Workbench launch:

```powershell
.venv\Scripts\python -m atelier.gui.ui.component_workbench
```

The workbench is a development/review surface only. Seeing a candidate there does not approve it for shared adoption.
