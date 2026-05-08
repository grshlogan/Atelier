# Atelier Recent Changes

> This file records meaningful project changes for future AI agents and developers. It is intentionally more durable than chat history. Keep entries concise, factual, and anchored to files or behavior that exists.

## 20260509_050259 [Thumbnail expand affordance line-only]

- Removed the rounded button face, border, gradient fill, and shadow from the collapsed `VideoInput` thumbnail expand affordance.
- Replaced the visual with a line-only four-corner expand mark, using rounded stroke caps over the thumbnail stack.
- Kept the existing proximity reveal behavior: 40 px enter distance, 64 px exit distance, thumbnail fade-down, and line fade-in.
- Updated plan and preview-artifact docs so the affordance is described as an expand line treatment instead of a button.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_video_input_collapsed_expand_affordance_is_line_only_corners
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_video_input_collapsed_expand_affordance_is_line_only_corners tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_video_input_collapsed_thumbnail_stack_reveals_expand_on_pointer_proximity
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
```

Result:

- Red-first focused test failed before implementation because `expand_affordance_snapshot()` lacked `visual_treatment`.
- Focused line-only + proximity tests: 2 tests passed.
- Component workbench tests: 34 tests passed.
- Component workbench + AtelierUI foundation + GUI smoke tests: 44 tests passed.
- Full unittest discovery: 166 tests passed.
- `compileall`: passed.

## 20260509_044609 [Collapsed video input thumbnail reveal]

- Updated `VideoInputCollapsedNodeCardItem` so the current vector collapsed card uses a three-thumbnail fallback stack instead of an empty right side.
- Moved the expand/collapse affordance from the bottom summary area onto the thumbnail stack, preserving the uniform `总时长 / 总大小 / 待处理` rhythm.
- Added pointer-proximity reveal behavior: 40 px enter distance fades the thumbnail stack down and the expand button in; 64 px exit distance fades back to thumbnails.
- Kept the GUI runtime boundary intact: no media reads, thumbnail generation, FFmpeg, Worker, Scheduler, SQLite, or `QPixmap` construction in the item paint path.
- Updated tests and docs to use `thumbnail_strategy = cached-preview-or-vector-fallback`.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_workcanvas_preview_hosts_thumbnail_stack_vector_collapsed_video_input_card tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_video_input_collapsed_thumbnail_stack_reveals_expand_on_pointer_proximity tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_video_input_collapsed_expand_affordance_is_line_only_corners
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\README.md, .\AGENTS.md, .\DESIGN.md, .\docs\*.md, .\docs\plan\*.md, .\docs\plan\gui_workbench\*.md, .\docs\design-md-references\*.md -Encoding UTF8 -Pattern '[ \t]+$'
git diff --check
```

Result:

- Focused red-first tests: failed before implementation for `thumbnail_strategy = none`, missing `thumbnail_stack_snapshot()`, and the old bottom-right expand rect; 3 tests passed after implementation.
- Component workbench tests: 34 tests passed.
- Component workbench + AtelierUI foundation + GUI smoke tests: 44 tests passed.
- Full unittest discovery: 166 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260509_033625 [Video input vector card selected style]

- Updated `VideoInputCollapsedNodeCardItem` so the current vector card is explicitly the selected state: thick blue border with a light glow.
- Added resting-state appearance tokens with a thin dark border and no glow for future non-selected rendering.
- Refined the vector card background to a restrained dark vertical gradient.
- Changed the bottom summary metrics to icon + title rows with values below, and added a drawn gradient expand/collapse affordance with a soft bottom shadow.
- Added snapshot coverage for appearance tokens, summary metric layout, and expand affordance geometry.
- Generated a local preview image at `.atelier/component-workbench/previews/video-input-vector-card-phase-m.png`.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_video_input_collapsed_appearance_separates_selected_and_resting_state tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_video_input_collapsed_summary_metrics_use_icon_title_rows tests.test_gui_atelier_ui_component_workbench.AtelierUIComponentWorkbenchWindowTests.test_video_input_collapsed_expand_affordance_is_line_only_corners
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\README.md, .\AGENTS.md, .\DESIGN.md, .\docs\*.md, .\docs\plan\*.md, .\docs\plan\gui_workbench\*.md, .\docs\design-md-references\*.md -Encoding UTF8 -Pattern '[ \t]+$'
git diff --check
```

Result:

- New focused tests: 3 tests passed.
- Component workbench tests: 32 tests passed.
- Component workbench + AtelierUI foundation + GUI smoke tests: 42 tests passed.
- Full unittest discovery: 164 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260509_025451 [Dark DESIGN.md reference]

- Added `docs/design-md-references/dark-tech-sharp.DESIGN.md` from the DESIGN.md reference library as a dark AI / developer-tool style reference.
- Updated `DESIGN.md` to list the new reference and explicitly constrain it to method-level inspiration, not Atelier's design source of truth.
- Added `docs/plan/plan_design_md_dark_reference.md` for the reference selection and verification record.

Validation run:

```powershell
Select-String -Path .\README.md, .\AGENTS.md, .\DESIGN.md, .\docs\*.md, .\docs\plan\*.md, .\docs\plan\gui_workbench\*.md, .\docs\design-md-references\*.md -Encoding UTF8 -Pattern '[ \t]+$'
git diff --check
```

Result:

- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260509_002000 [Vector card border-independent content layout]

- Split `VideoInputCollapsedNodeCardItem` border geometry from content geometry.
- Added `content_layout_snapshot()` for dev/test inspection of border rect, content rects, and divider lines.
- Changing `CARD_BORDER_WIDTH` now affects the border rect only; icon, title, status capsule, primary metric, and divider coordinates remain content-token driven.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
```

Result:

- Component workbench tests: 27 tests passed.
- Component workbench + AtelierUI foundation + GUI smoke tests: 37 tests passed.
- Full unittest discovery: 159 tests passed.
- `compileall`: passed.

## 20260509_001500 [Workbench fullscreen HUD stability]

- Added fullscreen WorkCanvas overlay controls so zoom and the paint-performance HUD remain visible in fullscreen mode.
- Fixed fullscreen HUD live-refresh jitter by giving the HUD stable geometry instead of resizing it on every performance text update.
- Added regression coverage for fullscreen HUD stability during repeated refreshes.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\README.md, .\AGENTS.md, .\DESIGN.md, .\docs\*.md, .\docs\plan\*.md, .\docs\plan\gui_workbench\*.md, .\docs\plan\gui_workbench\archive\component_workbench_phases\*.md -Encoding UTF8 -Pattern '[ \t]+$'
git diff --check
```

Result:

- Component workbench tests: 24 tests passed.
- Component workbench + AtelierUI foundation + GUI smoke tests: 34 tests passed.
- Full unittest discovery: 156 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260509_001000 [Workbench visible performance HUD and centered launch]

- Added a dev-only WorkCanvas performance HUD to the AtelierUI Component Workbench.
- The HUD displays zoom, WorkCanvas background paint time, tile cache hit / miss counts, tile key, viewport update mode, background / node AA state, and `VideoInputCollapsedNodeCardItem.paint()` timing.
- Enabled the existing WorkCanvas / node-card `debug_perf` snapshots by default inside the dev-only workbench preview so the HUD has live data.
- Changed `ComponentWorkbenchWindow` launch geometry to default to 1980 px × 1080 px and recenter on the current screen each time the window is shown instead of relying on a previous close position.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\README.md, .\AGENTS.md, .\DESIGN.md, .\docs\*.md, .\docs\plan\*.md, .\docs\plan\gui_workbench\*.md, .\docs\plan\gui_workbench\archive\component_workbench_phases\*.md -Encoding UTF8 -Pattern '[ \t]+$'
git diff --check
```

Result:

- Component workbench tests: 23 tests passed.
- Component workbench + AtelierUI foundation + GUI smoke tests: 33 tests passed.
- Full unittest discovery: 155 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260508_004000 [WorkCanvas paint performance instrumentation]

- Added `_WorkCanvasView.set_debug_perf()` and `debug_perf_snapshot()` for dev-only paint instrumentation.
- WorkCanvas background perf snapshots now include `drawBackground` time, tile cache hit / miss counters, tile key, zoom, viewport update mode, and background AA state.
- Added `_WorkCanvasView.set_viewport_update_mode_name()` with `minimal`, `bounding`, and `full` modes.
- Background grid drawing explicitly disables antialiasing while the vector node view keeps AA enabled for node painting.
- Added `VideoInputCollapsedNodeCardItem.set_debug_perf()` and `debug_perf_snapshot()` so node-card `paint()` timing is tracked separately from background grid timing.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\README.md, .\AGENTS.md, .\DESIGN.md, .\docs\*.md, .\docs\plan\*.md, .\docs\plan\gui_workbench\*.md, .\docs\plan\gui_workbench\archive\component_workbench_phases\*.md -Encoding UTF8 -Pattern '[ \t]+$'
git diff --check
```

Result:

- Component workbench tests: 21 tests passed.
- Component workbench + AtelierUI foundation + GUI smoke tests: 31 tests passed.
- Full unittest discovery: 153 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260508_003500 [WorkCanvas preview controls and grid performance]

- Changed the dev-only WorkCanvas preview so the central workbench surface no longer depends on an outer `QScrollArea`; the canvas handles pan / zoom itself.
- Fixed `QGraphicsScene` ownership for the non-fullscreen vector preview so `QGraphicsView.scene()` remains stable.
- Changed WorkCanvas grid drawing from scene-space loops to viewport / screen-space drawing with adaptive LOD.
- At low zoom, minor grid lines and dot intersections are skipped so zooming out does not increase grid primitive count.
- Changed small-grid painting to a cached tile / brush strategy, so normal panning no longer rebuilds full-viewport minor lines and dot primitives every paint.
- Preserved fullscreen preview and added stable properties for fullscreen `item_route`, `display_mode`, `thumbnail_strategy`, and `pan_interaction`.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\README.md, .\AGENTS.md, .\DESIGN.md, .\docs\*.md, .\docs\plan\*.md, .\docs\plan\gui_workbench\*.md, .\docs\plan\gui_workbench\archive\component_workbench_phases\*.md -Encoding UTF8 -Pattern '[ \t]+$'
git diff --check
```

Result:

- Component workbench tests: 19 tests passed.
- Component workbench + AtelierUI foundation + GUI smoke tests: 29 tests passed.
- Full unittest discovery: 151 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260508_003000 [Component workbench focused WorkCanvas tuning surface]

- Focused the active dev-only `AtelierUI Component Workbench` catalog on `VideoInputCard 候选`.
- Archived `WorkflowNodeItem 候选` and the visible `主题 Tokens` preview from the current workbench surface.
- Removed the visible right-side intake review checklist / note panel from the workbench UI; direct screenshots remain sufficient for the current polishing loop.
- Added WorkCanvas card-entry controls so `矢量内缩` and `旧版展开参考` are selected explicitly instead of being stacked together.
- Added a `全屏` WorkCanvas preview window for inspecting the thumbnail-free vector collapsed card in a larger canvas view.
- Added TDD coverage for catalog cleanup, hidden token / review surfaces, entry switching, and fullscreen preview.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\README.md, .\AGENTS.md, .\DESIGN.md, .\docs\*.md, .\docs\plan\*.md, .\docs\plan\gui_workbench\*.md, .\docs\plan\gui_workbench\archive\component_workbench_phases\*.md -Encoding UTF8 -Pattern '[ \t]+$'
git diff --check
```

Result:

- Component workbench tests: 16 tests passed.
- Component workbench + AtelierUI foundation + GUI smoke tests: 26 tests passed.
- Full unittest discovery: 148 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260508_002000 [VideoInput vector collapsed card]

- Added `docs/plan/gui_workbench/plan_video_input_vector_collapsed_card.md`.
- Added `atelier/gui/ui/workflow_canvas/node_cards/video_input_vector_card.py` with `VideoInputCollapsedNodeCardItem`.
- The new card is a `QGraphicsObject` / `paint()` WorkCanvas-route candidate with fixed 300 px × 200 px bounds and no thumbnail or thumbnail placeholder.
- Added `component-workbench-video-input-vector-preview` in the dev-only WorkCanvas preview area, while keeping the older QWidget candidate as visual reference.
- Added basic `+` / `-` / `100%` zoom controls and mouse-drag panning for the vector preview; zoom changes the `QGraphicsView` transform, not the card item's geometry.
- Added TDD coverage proving the WorkCanvas preview hosts the thumbnail-free collapsed vector item and records `thumbnail_strategy = none`.

## 20260508_001000 [WorkCanvas preview artifact and workbench preview area]

- Added `docs/WORKCANVAS_PREVIEW_ARTIFACT_SPEC.md`, recording ComfyUI-inspired preview artifact, thumbnail cache, lazy GUI drawing, and non-copy boundaries for Atelier WorkCanvas.
- Added `docs/plan/gui_workbench/plan_component_workbench_workcanvas_preview_area.md`.
- Extended the dev-only `AtelierUI` component workbench with `component-workbench-workcanvas-preview`, a self-painted WorkCanvas preview area that hosts the current `VideoInputCardCandidate`.
- The preview area declares `thumbnail_policy = cached-preview-artifact-only` and `gui_runtime_boundary = no-worker-no-ffmpeg-no-thumbnail-generation`.
- Added TDD coverage proving the workbench exposes the WorkCanvas preview area and hosts the video input node card inside it.

## 20260508_000000 [GUI workbench plan taxonomy]

- Created `docs/plan/gui_workbench/` as the dedicated home for GUI / AtelierUI / component workbench / UI polishing plans.
- Added `docs/plan/gui_workbench/README.md` as the current plan index and `docs/plan/gui_workbench/plan_gui_workbench_plan_taxonomy.md` as the taxonomy plan.
- Moved active GUI plans into `docs/plan/gui_workbench/`:
  - `plan_main_interactive_gui_workbench.md`.
  - `plan_workflow_canvas_foundation.md`.
  - `plan_atelier_ui_local_library_governance.md`.
  - `plan_atelier_ui_foundation.md`.
  - `plan_atelier_ui_component_workbench.md`.
  - `plan_atelier_ui_workflow_canvas_node_cards.md`.
- Archived completed component workbench phase plans and the one-off UI motion spec writing plan under `docs/plan/gui_workbench/archive/component_workbench_phases/`.
- Updated README, `docs/UI_MOTION_SPEC.md`, `docs/plan/plan_main_app_skeleton.md`, and active GUI plans so current entry links point to the new folder.

## 20260507_004000 [AtelierUI component workbench foundation]

- Created `docs/plan/plan_atelier_ui_component_workbench_foundation.md`.
- Added `tests/test_gui_atelier_ui_component_workbench.py` before implementation and confirmed the expected red state: `atelier.gui.ui.component_workbench_state` / `atelier.gui.ui.component_workbench` did not exist.
- Added `atelier/gui/ui/component_workbench_state.py` with pure-Python workbench state:
  - catalog entries.
  - token swatch views from `ATELIER_THEME_TOKENS`.
  - typography samples.
  - widget intake checklist steps.
  - candidate story metadata that keeps `WorkflowNodeItem Candidate` unapproved for shared adoption.
- Added `atelier/gui/ui/component_workbench.py` with a dev-only PySide6 `ComponentWorkbenchWindow`.
- Added the launch entry:

```powershell
.venv\Scripts\python -m atelier.gui.ui.component_workbench
```

Current boundary:

- Implemented: dev-only component workbench window with catalog, token preview, typography preview, intake checklist, candidate placeholder, and `--no-exec` test entry.
- Implemented: state module does not import PySide6.
- Not implemented: real self-painted widgets, parameter controls, motion playback, screenshot saving, Qt Designer plugin, or visual regression.
- Not changed: product `MainWindow` does not host the component workbench, and no candidate widget is approved for shared `AtelierUI` adoption.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
```

Result:

- Red first: 4 errors because the new workbench modules were missing.
- Component workbench tests: 4 tests passed.
- Component workbench + AtelierUI foundation + GUI smoke tests: 14 tests passed.
- Full unittest discovery: 136 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

Follow-up:

- Updated the dev-only component workbench visible UI copy to Chinese instead of adding a partial i18n layer.
- Kept code identifiers, object names, command flags, token roles, and product model names in their original language.
- Added test assertions so the workbench title, catalog label, candidate review status, intake checklist text, and planned screenshot button stay Chinese until a real i18n boundary exists.

## 20260507_004500 [AtelierUI component workbench controls]

- Created `docs/plan/plan_atelier_ui_component_workbench_controls.md`.
- Extended `tests/test_gui_atelier_ui_component_workbench.py` before implementation and confirmed the expected red state:
  - `ComponentStoryView` did not expose `states` / `controls`.
  - the workbench window did not expose selected story preview labels.
  - the controls panel did not exist.
- Extended `atelier/gui/ui/component_workbench_state.py` with:
  - `ComponentStoryStateView`.
  - `ComponentControlView`.
  - story-level `states`.
  - story-level `controls`.
- Extended `atelier/gui/ui/component_workbench.py` so catalog selection updates:
  - selected story title.
  - selected story summary.
  - selected story states.
  - controls panel summary.

Current boundary:

- Implemented: catalog selection and metadata-only controls panel.
- Implemented: `WorkflowNodeItem 候选` exposes `normal` / `hovered` / `selected` states and `selected` / `hovered` / `density` controls.
- Not implemented: real self-painted widget drawing, parameter-driven rendering, motion playback, screenshot saving, review note persistence, or shared adoption approval.
- Not changed: product `MainWindow` still does not host this workbench.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

Result:

- Red first: missing controls / preview widgets caused expected failures.
- Component workbench tests: 5 tests passed after implementation.
- Component workbench + AtelierUI foundation + GUI smoke tests: 15 tests passed.
- Full unittest discovery: 137 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

Follow-up:

- Added root development launcher `open_atelier_ui_workbench.ps1`.
- The launcher locates the repository root, prefers `.venv\Scripts\python.exe`, and runs `-m atelier.gui.ui.component_workbench`.
- Extra PowerShell arguments are passed through to the workbench entry.
- Verified with `powershell -NoProfile -ExecutionPolicy Bypass -File .\open_atelier_ui_workbench.ps1 --no-exec`.

## 20260507_005000 [AtelierUI component workbench review snapshots]

- Created `docs/plan/plan_atelier_ui_component_workbench_screenshot.md`.
- Extended `tests/test_gui_atelier_ui_component_workbench.py` before implementation and confirmed the expected red state:
  - no `build_review_snapshot_record()`.
  - no injectable review output directory.
  - screenshot button was still disabled placeholder.
  - no review note editor.
- Extended `atelier/gui/ui/component_workbench_state.py` with JSON-safe review snapshot metadata.
- Extended `atelier/gui/ui/component_workbench.py` with:
  - review note editor.
  - enabled `保存截图和备注` action.
  - `save_review_snapshot()`.
  - PNG screenshot output.
  - JSON metadata output.

Current boundary:

- Implemented: manual dev-only PNG screenshot and JSON review snapshot output.
- Implemented: default output path is `.atelier/component-workbench/reviews/`.
- Implemented: tests can inject a temporary review output directory.
- Not implemented: visual diff, review approval state, database persistence, product export UI, or shared widget adoption.
- Not changed: product `MainWindow` still does not host this workbench.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
```

Result:

- Red first: missing review snapshot and screenshot UI caused expected failures.
- Component workbench tests: 8 tests passed after implementation.
- Component workbench + AtelierUI foundation + GUI smoke tests: 18 tests passed.
- Full unittest discovery: 140 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260507_005500 [AtelierUI review page plan and GitHub boundary]

- Created `docs/plan/plan_atelier_ui_component_workbench_review_page.md`.
- Planned a static HTML review page generated from the dev-only workbench PNG / JSON review snapshot.
- Extended `tests/test_gui_atelier_ui_component_workbench.py` before implementation and confirmed the expected red state:
  - no `review_page_filename` metadata.
  - no `render_review_page_html()`.
  - no `ReviewSnapshotResult.review_page_path`.
- Extended `atelier/gui/ui/component_workbench_state.py` with static review page HTML rendering.
- Extended `atelier/gui/ui/component_workbench.py` so `save_review_snapshot()` writes PNG, JSON, and HTML.
- Added a review page handoff label in the workbench UI so the latest HTML filename is visible after saving.
- Follow-up TDD slice added `metadata_filename` to the review snapshot contract so JSON and HTML both identify the sibling metadata file without absolute paths.
- Recorded the browser handoff decision:
  - Codex browser is useful for annotating static HTML review pages.
  - Codex browser should not become the real PySide6 widget runtime.
- Recorded the GitHub boundary:
  - Commit workbench source, tests, docs, and root development launcher.
  - Do not commit generated `.atelier/component-workbench/reviews/*.png`, `*.json`, or `*.html`.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Red first: missing review page metadata / renderer / result path caused expected failures.
- Browser handoff red first: missing review page path label caused expected failures.
- Metadata filename red first: `metadata_filename` assertions failed before the review snapshot contract was extended.
- Component workbench tests: 9 tests passed after implementation.
- Component workbench + AtelierUI foundation + GUI smoke tests: 19 tests passed.
- Full unittest discovery: 141 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260507_005800 [AtelierUI Workflow Canvas VideoInputCard candidate]

- Created `docs/plan/plan_atelier_ui_workflow_canvas_node_cards.md`.
- Added `atelier/gui/ui/workflow_canvas/node_cards/` as the parent directory for Workflow Canvas node card candidates.
- Added `atelier/gui/ui/workflow_canvas/node_cards/video_input_card.py` with the first dev-only `VideoInputCardCandidate` preview.
- Refined `VideoInputCardCandidate` to the current expanded-state review spec:
  - fixed 400 px × 600 px card size.
  - 16 px radius and 3 px border.
  - outward blue glow through a Qt drop shadow effect.
  - 50 px header section with an invisible left info container.
  - info container uses `atelier/assets/nodes/video_input.svg` plus title text only.
  - title weight matches the status text instead of using bold.
  - icon size is controlled by `ICON_TO_TITLE_FONT_HEIGHT_RATIO` in `video_input_card.py`.
  - 80 px × 30 px visible status capsule with 15 px radius and centered text.
  - stream section uses vertical centered sequencing with 5 px spacing.
  - 380 px × 75 px video preview card without the AI-generated video label.
  - input path box and 100 px browse button share a 40 px row with 5 px spacing.
  - input path box width is fixed to `400 - 100 - 10 - 10 - 5 = 275 px`.
- Extended `tests/test_gui_atelier_ui_component_workbench.py` before implementation and confirmed the expected red state:
  - catalog did not list `video-input-card`.
  - selecting the third catalog item did not show `VideoInputCard 候选`.
  - no `component-workbench-video-input-card` preview existed.
- Extended `atelier/gui/ui/component_workbench_state.py` so `VideoInputCard 候选` appears under `Workflow Canvas / Node Cards`.
- Extended `atelier/gui/ui/component_workbench.py` so the workbench renders the candidate card preview when that story is selected.

Current boundary:

- Implemented: review-only static expanded video input node card candidate in the dev-only workbench with fixed geometry and semantic Header / Stream sections.
- Implemented: story controls metadata for `selected`, `hovered`, `media_status`, and `thumbnail`.
- Not implemented: file picking, media probing, thumbnail extraction, WorkflowGraph node creation, real parameter-driven rendering, or product `MainWindow` usage.
- Not changed: candidate is not approved for shared `AtelierUI` adoption.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_component_workbench tests.test_gui_atelier_ui_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Red first: missing `video-input-card` story and preview caused expected failures.
- Expanded-state red first: card height was still 300 px before the expanded layout implementation.
- Geometry-adjustment red first: card border was still 4 px before the latest geometry pass.
- Header/icon red first: header was still 40 px before the latest header pass.
- Component workbench tests: 10 tests passed after implementation.
- Component workbench + AtelierUI foundation + GUI smoke tests: 20 tests passed.
- Full unittest discovery: 142 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260507_003500 [Rejected ECHO reference candidate]

- Updated `docs/UI_MOTION_SPEC.md` external code policy to require reference projects to be structurally clear, maintainable, reasonably stable, and license-clear before they enter Atelier's reference system.
- Recorded `Moekotori/ECHO` as a rejected reference candidate.

Current boundary:

- `Moekotori/ECHO` should not be used as a reference for Atelier GUI, AtelierUI, plugin architecture, release flow, or smoke checklist work.
- This is a documentation/governance decision only; no code changed.

Validation run:

```powershell
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260507_003300 [AtelierUI component workbench plan]

- Created `docs/plan/plan_atelier_ui_component_workbench.md`.
- Updated `docs/UI_MOTION_SPEC.md` with the rule that candidate self-painted widgets should be tuned in a dev-only component workbench, not inside the real product GUI.
- Updated `README.md` document index.

Current boundary:

- Implemented: planning and governance only.
- Not implemented: `.venv\Scripts\python -m atelier.gui.ui.component_workbench`.
- Current available GUI previews remain:
  - product workbench: `.venv\Scripts\python -m atelier.gui.app`.
  - icon preview: `atelier/assets/preview.html`.
  - Bezier helper: `atelier/assets/Main.py`, not a product component gallery.

Validation run:

```powershell
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260507_003000 [AtelierUI foundation]

- Created `docs/plan/plan_atelier_ui_foundation.md`.
- Added `tests/test_gui_atelier_ui_foundation.py` before implementation and confirmed the expected red state: `atelier.gui.ui` did not exist.
- Added `atelier/gui/ui/`:
  - `__init__.py`
  - `theme_tokens.py`
  - `widget_intake.py`
  - `README.md`
- Added pure Python `ATELIER_THEME_TOKENS` sourced from `DESIGN.md` baseline roles:
  - dark palette roles.
  - UI and monospace font stacks.
  - compact desktop typography tokens.
  - radius / spacing tokens.
  - first Workflow Canvas node card sizing tokens.
- Added `widget_intake.py` checklist for self-painted widget intake:
  - purpose.
  - reference review.
  - minimal test.
  - Atelier-specific implementation.
  - user review.
- Updated `README.md`, `docs/UI_MOTION_SPEC.md`, `docs/APP_CODE_MAP.md`, and main GUI plans to reflect that the local `AtelierUI` package now exists.

Current boundary:

- Implemented: pure Python tokens and intake checklist.
- Implemented: import path does not require PySide6.
- Not implemented: animation driver, runtime theme switching, overlay layer, queue delegate animation, or shared reviewed self-painted widgets.
- Not changed: `atelier/gui/workflow_canvas.py` still owns current Workflow Canvas rendering and has not been migrated to `AtelierUI`.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_foundation
.venv\Scripts\python -m unittest tests.test_gui_atelier_ui_foundation tests.test_gui_workflow_canvas_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Red first: 4 errors because `atelier.gui.ui` was missing.
- Green after implementation: 4 tests passed.
- AtelierUI foundation + Workflow Canvas foundation + GUI smoke tests: 14 tests passed.
- Full unittest discovery: 132 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260507_002500 [AtelierUI local library governance]

- Created `docs/plan/plan_atelier_ui_local_library_governance.md`.
- Updated `AGENTS.md` with the non-negotiable GUI rule that Atelier must keep a local project-specific UI library direction for self-painted widgets, animation effects, theme tokens, overlays, and shared motion helpers.
- Updated `docs/UI_MOTION_SPEC.md` so `AtelierUI` is explicitly:
  - project-specific Atelier code.
  - packaged only with the application runtime or core code.
  - not a mature reusable external library.
  - gated by user review before new self-painted widgets are adopted as shared components.
- Updated GUI plans to record that self-painted widgets should reference existing open-source/code examples first, then implement Atelier-specific PySide6-native versions without copying incompatible code.
- Updated `docs/APP_CODE_MAP.md` to record the governance boundary and to align the code tree with the current Workflow Canvas foundation files.

Boundary at the time of this governance update:

- Implemented: documentation and planning governance only.
- Not implemented then: `atelier/gui/ui/`, `AnimationDriver`, theme tokens, overlay layer, queue delegate animation, or reviewed shared self-painted widget modules.
- Not changed: existing `atelier/gui/workflow_canvas.py` remains a feature-level Workflow Canvas foundation module.

Follow-up:

- `20260507_003000 [AtelierUI foundation]` later added `atelier/gui/ui/` with pure Python theme tokens and a widget intake checklist.

Validation run:

```powershell
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md, .\AGENTS.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260507_002000 [Workflow Canvas foundation]

- Created `docs/plan/plan_workflow_canvas_foundation.md`.
- Added `tests/test_gui_workflow_canvas_foundation.py` with TDD red/green coverage for:
  - `WorkflowGraph -> WorkflowCanvasViewModel` separation.
  - rendering node card visual items and edge visual items.
  - node selection as GUI visual state.
  - `MainWindow` central view integration with injected `WorkflowGraph`.
- Added `atelier/gui/workflow_canvas.py` with:
  - `WorkflowCanvasViewModel`, `WorkflowCanvasNodeView`, and `WorkflowCanvasEdgeView`.
  - `build_workflow_canvas_view_model(graph)`.
  - `WorkflowCanvas`, a `QGraphicsView` / `QGraphicsScene` based canvas.
  - GUI-only node selection state and `selection_changed` signal.
- Updated `atelier/gui/main_window.py` so the central view uses `WorkflowCanvas` instead of a pure placeholder while preserving the existing run-intent control boundary.
- Updated `docs/APP_CODE_MAP.md` with the new GUI canvas module and boundaries.

Current boundary:

- Implemented: minimal PySide6-native Workflow Canvas can render a graph's nodes and edges.
- Implemented: graph data and visual state are separated; selection does not mutate `WorkflowGraph`.
- Implemented: `MainWindow` can accept an injected `WorkflowGraph` and render it centrally.
- Not implemented: graph editing, drag persistence, port validation, dynamic Inspector forms, Execution Canvas, or workflow execution from the canvas.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_gui_workflow_canvas_foundation
.venv\Scripts\python -m unittest tests.test_gui_workflow_canvas_foundation tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Workflow Canvas foundation tests: 3 tests passed after the first green slice.
- Workflow Canvas foundation + GUI smoke tests: 10 tests passed after `MainWindow` integration.
- Full unittest discovery: 128 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260507_001000 [Interactive GUI workbench main plan]

- Created `docs/plan/plan_main_interactive_gui_workbench.md`.
- Updated `docs/plan/plan_main_app_skeleton.md` to link the GUI-specific main plan.
- Updated `README.md` to include the GUI-specific main plan in the document index.
- Recorded the working split:
  - GUI-focused conversation owns interactive workbench, Workflow Canvas, Execution Canvas, Queue Monitor, Inspector, workspace, visual behavior, and motion.
  - Global/backend conversation owns broader project guidance and backend execution systems.
- Recorded the next GUI direction as `workflow_canvas_foundation`.

Current boundary:

- Planned next: create and execute `docs/plan/plan_workflow_canvas_foundation.md`.
- Not prioritized: `gui_file_import_output_intent`, because a low-completion demo path is less useful than building the real card-based Workflow Canvas foundation.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_gui_workflow_run_intent tests.test_gui_smoke tests.test_gui_app_entry tests.test_gui_workflow_run_entry
.venv\Scripts\python -m compileall -q atelier tests
.venv\Scripts\python -m unittest discover -s tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- GUI intent/smoke/app-entry/run-entry tests: 11 tests passed.
- `compileall`: passed.
- Full unittest discovery: 124 tests passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260506_004000 [GUI workflow run entry boundary]

- Created `docs/plan/plan_gui_minimal_run_workflow_entry.md`.
- Updated `docs/plan/plan_main_app_skeleton.md` to list it as the 13th follow-up plan.
- Continued Phase A with the first app service slice:
  - added `atelier/app/workflow_run.py`.
  - added `tests/test_gui_workflow_run_entry.py`.
- Added `WorkflowRunAppService`, which accepts a persisted `plan_id`, builds `SimpleScheduler`, builds `RuntimeManager.from_store()`, and calls `run_sequential_workflow()`.
- Continued Phase B with the first Queue panel visibility slice:
  - updated `atelier/gui/workspace.py` to display final output paths and failure facts from `WorkbenchSnapshot`.
  - extended `tests/test_gui_smoke.py`.
- Continued Phase C with the first GUI run-control slice:
  - updated `atelier/gui/main_window.py` to accept an active plan id and injected run-intent service protocol.
  - added a central run button that calls `request_run(plan_id)`.
  - extended `tests/test_gui_smoke.py`.
- Continued Phase D with the first non-blocking run-intent slice:
  - added `atelier/gui/workflow_run_intent.py`.
  - added `tests/test_gui_workflow_run_intent.py`.
  - updated `MainWindow` to submit run intents through `WorkflowRunIntentExecutor`.
- Completed Phase E documentation alignment for this plan.

Current boundary:

- Implemented: GUI-facing app service boundary can run a persisted fake `media.audio_extract -> output.export` plan and return structured `WorkflowRunResult`.
- Implemented: Queue panel can expose final output paths and failure facts that `state_reader` already reads.
- Implemented: minimal GUI run control can submit a run intent through an injected protocol without constructing backend runner dependencies in `MainWindow`.
- Implemented: minimal background execution boundary keeps slow `request_run(plan_id)` calls out of the Qt click handler.
- Not implemented: durable run queue, retry/cancel/recovery actions, file picker, full Workflow Canvas editing, progress callbacks, or Qt signal-based snapshot refresh.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_gui_workflow_run_entry
.venv\Scripts\python -m unittest tests.test_gui_workflow_run_entry tests.test_minimal_backend_workflow_runner tests.test_gui_state_reader
.venv\Scripts\python -m unittest tests.test_gui_smoke
.venv\Scripts\python -m unittest tests.test_gui_app_entry
.venv\Scripts\python -m unittest tests.test_gui_smoke tests.test_gui_app_entry
.venv\Scripts\python -m unittest tests.test_gui_workflow_run_intent tests.test_gui_smoke
.venv\Scripts\python -m unittest tests.test_gui_workflow_run_entry tests.test_gui_smoke tests.test_minimal_backend_workflow_runner tests.test_gui_state_reader
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- GUI workflow run entry tests: 1 test passed.
- GUI workflow run entry + backend runner + state reader tests: 6 tests passed.
- GUI smoke tests: 4 tests passed.
- GUI smoke tests after run-control slice: 5 tests passed.
- GUI app entry tests: 3 tests passed.
- GUI smoke + app entry tests: 8 tests passed.
- GUI workflow run intent + smoke tests: 7 tests passed.
- GUI run entry + GUI smoke + backend runner + state reader tests: 11 tests passed.
- Full unittest discovery: 124 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260506_003500 [Workbench snapshot explains runner outputs]

- Continued `docs/plan/plan_minimal_backend_workflow_runner.md` Phase D.
- Extended `atelier/gui/state_reader.py` so `WorkbenchTaskItem` includes:
  - `final_output_paths`.
  - `failure_error_code`.
  - `failure_message`.
- Kept the new fields defaulted so existing manual `WorkbenchTaskItem` construction remains compatible.
- Extended `tests/test_gui_state_reader.py` to verify read-only snapshots can explain:
  - final output paths after fake `media.audio_extract -> output.export` completes.
  - failure code/message after the backend runner stops on a failed upstream task.

Current boundary:

- Implemented: read-only queue snapshot fields needed to inspect runner output/failure states.
- Not implemented: GUI run button, workflow editing, recovery action execution, richer blocked-state persistence, or visual/screenshot verification.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_backend_workflow_handoff tests.test_minimal_backend_workflow_runner tests.test_gui_state_reader
.venv\Scripts\python -m unittest tests.test_gui_state_reader tests.test_gui_smoke
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Backend workflow handoff + runner + state reader tests: 8 tests passed.
- GUI state reader + smoke tests: 6 tests passed.
- Full unittest discovery: 119 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260506_003000 [Minimal sequential backend workflow runner]

- Continued `docs/plan/plan_minimal_backend_workflow_runner.md` Phase C.
- Added `atelier/scheduler/workflow_runner.py` with:
  - `WorkflowRunResult`.
  - `run_sequential_workflow()`.
- Added `fetch_plan_task_statuses()` in `atelier/storage/repositories.py`.
- Updated artifact handoff path resolution so relative upstream artifact paths are resolved against `work_root / upstream_task_id / artifact_path` when preparing downstream dispatch.
- Added `tests/test_minimal_backend_workflow_runner.py`.

Implemented path:

```text
SimpleScheduler.claim_next_task()
  -> materialize_downstream_task_inputs()
  -> RuntimeManager.resolve()
  -> dispatch_claimed_task()
  -> WorkerEvent / SQLite
  -> next task
```

Current boundary:

- Implemented: sequential fake `media.audio_extract -> output.export` backend workflow and stop-on-task-failure behavior.
- Not implemented: concurrent queue workers, retry/recovery execution, GUI run entry, lifecycle timeout/cancel options in the workflow runner, separate workflow-run persistence, or rich blocked-state persistence.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_backend_workflow_handoff tests.test_minimal_backend_workflow_runner
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Backend workflow handoff + runner tests: 5 tests passed.
- Full unittest discovery: 117 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260506_002500 [Downstream artifact input materialization]

- Continued `docs/plan/plan_minimal_backend_workflow_runner.md` Phase B.
- Added `atelier/scheduler/handoff.py` with:
  - `TaskInputMaterialization`.
  - `materialize_downstream_task_inputs()`.
- Added `fetch_task_dependency_ids()` in `atelier/storage/repositories.py`.
- Extended `tests/test_backend_workflow_handoff.py` to cover:
  - injecting `output.export.input_path` from one persisted upstream role=`output` artifact.
  - preserving the original `ExecutionTask.params`.
  - blocking ambiguous multi-upstream artifact candidates with `UPSTREAM_ARTIFACT_AMBIGUOUS`.

Current boundary:

- Implemented: minimum dispatch-preparation materialization for `output.export.input_path`.
- Not implemented: full port-level mapping, broad node param materialization, claim/dispatch loop, retry/recovery execution, GUI run entry, or filesystem artifact discovery.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_backend_workflow_handoff
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Backend workflow handoff tests: 3 tests passed.
- Full unittest discovery: 115 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260506_002000 [Minimal backend workflow runner plan]

- Created `docs/plan/plan_minimal_backend_workflow_runner.md`.
- Lightly executed Phase A with the first artifact handoff query:
  - added `TaskArtifactRecord`.
  - added `fetch_task_output_artifacts()` in `atelier/storage/repositories.py`.
  - added `tests/test_backend_workflow_handoff.py`.
- Scope remains intentionally narrow: this only queries persisted role=`output` artifacts for an upstream task and supports `artifact_type` filtering. It does not materialize downstream params or run a claim/dispatch loop yet.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_backend_workflow_handoff
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Backend workflow handoff tests: 1 test passed.
- Full unittest discovery: 113 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260506_001500 [Output export ArtifactFinalizer workflow]

- Created and executed `docs/plan/plan_output_export_finalizer.md` Phase A-C.
- Added `atelier/adapters/finalize.py` with `ArtifactFinalizerAdapter` for `output.export`.
- Registered `output.export` in `atelier/adapters/builtins.py`.
- Updated `atelier/storage/repositories.py` so `ArtifactEvent.metadata.role == "final_output"` is persisted as `task_artifacts.role = "final_output"`.
- Implemented the first final output path:
  - reads staged artifact path from `input_path`.
  - writes only to `output_dir`.
  - accepts optional safe `filename`.
  - rejects output conflicts instead of overwriting user files.
  - verifies size and SHA-256 after copy.
  - returns a final output artifact and maps conflict/path/input failures to structured adapter failures.
- Added tests:
  - `tests/test_artifact_finalizer_adapter.py`
  - `tests/test_output_export_workflow.py`
- Updated `README.md`, `docs/ADAPTER_SPEC.md`, `docs/ARTIFACT_LIFECYCLE_SPEC.md`, `docs/FFMPEG_ADAPTER_SPEC.md`, `docs/WORKER_PROTOCOL.md`, `docs/APP_CODE_MAP.md`, and `docs/plan/plan_main_app_skeleton.md`.

Current boundary:

- Implemented: existing staged artifact -> safe copy -> final output artifact -> WorkerEvent -> SQLite `final_output` link.
- Not implemented: GUI export dialog, multi-artifact export, move semantics, output naming templates, artifact resolver from upstream `task_artifacts`, overwrite/rename UI, mux/burn, FFmpeg transcode export, or cleanup of staged sources.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_artifact_finalizer_adapter tests.test_output_export_workflow tests.test_minimal_audio_extract_workflow tests.test_phase6_minimal_loop
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Output export adapter tests: 5 tests passed.
- Output export workflow tests: 2 tests passed.
- Full unittest discovery: 112 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260506_001000 [FFmpeg audio extract adapter workflow]

- Created and executed `docs/plan/plan_ffmpeg_audio_extract_adapter.md` Phase A-B.
- Added `atelier/adapters/ffmpeg.py` with `FFmpegAudioExtractAdapter` for `media.audio_extract`.
- Registered `media.audio_extract` in `atelier/adapters/builtins.py`.
- Implemented the first staged audio artifact path:
  - reads `ffmpeg` path from `RuntimeBinding.component_paths`.
  - validates `input_path`.
  - runs typed FFmpeg command without shell strings.
  - writes `audio.wav` under the task work directory.
  - returns an audio artifact and maps missing runtime/input, command failure, and missing output to structured adapter failures.
- Added tests:
  - `tests/test_ffmpeg_audio_extract_adapter.py`
  - `tests/test_minimal_audio_extract_workflow.py`
- Updated `README.md`, `docs/ADAPTER_SPEC.md`, `docs/FFMPEG_ADAPTER_SPEC.md`, `docs/APP_CODE_MAP.md`, and `docs/plan/plan_main_app_skeleton.md`.

Current boundary:

- Implemented: fake-FFmpeg `media.audio_extract` backend workflow through `WorkflowGraph -> ExecutionPlan -> Scheduler claim -> RuntimeManager RuntimeBinding -> task.json -> AdapterRegistry -> FFmpegAudioExtractAdapter -> WorkerEvent/Artifact -> SQLite`.
- Not implemented: real FFmpeg smoke test, no-audio policy, FFmpeg progress pipe, cancel long transcode, GUI trigger, final export, subtitle mux/burn, ASR, OCR, Translate Agent, enhancement adapters, plugin adapter discovery, production adapter cancellation, or retry/recovery action execution.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_ffmpeg_audio_extract_adapter tests.test_minimal_audio_extract_workflow
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Audio extract adapter/workflow tests: 7 tests passed.
- Full unittest discovery: 105 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260505_008000 [Minimal metadata probe adapter workflow]

- Completed `docs/plan/plan_minimal_adapter_probe_workflow.md` Phase A-F.
- Added the first adapter foundation:
  - `atelier/adapters/base.py`
  - `atelier/adapters/registry.py`
  - `atelier/adapters/command.py`
  - `atelier/adapters/ffprobe.py`
  - `atelier/adapters/builtins.py`
- Added `atelier/workers/adapter_entry.py`, a task-file based adapter worker entrypoint that emits Worker JSON Lines.
- Updated `atelier/scheduler/dispatch.py` so `dispatch_claimed_task()` can receive a RuntimeManager-produced `RuntimeBinding` and write it into worker `task.json`.
- Implemented `metadata.probe` / `FFprobeMetadataAdapter`:
  - reads `ffprobe` path from `RuntimeBinding.component_paths`.
  - validates `input_path`.
  - runs typed ffprobe command without shell strings.
  - parses ffprobe JSON and writes `probe.json` under the task work directory.
  - returns a metadata artifact and maps missing runtime/input, command failure, and invalid JSON to structured adapter failures.
- Added tests:
  - `tests/test_adapter_registry.py`
  - `tests/test_command_executor.py`
  - `tests/test_ffprobe_metadata_adapter.py`
  - `tests/test_minimal_probe_workflow.py`
- Updated `docs/ADAPTER_SPEC.md`, `docs/FFMPEG_ADAPTER_SPEC.md`, `docs/APP_CODE_MAP.md`, and `docs/plan/plan_main_app_skeleton.md`.

Current boundary:

- Implemented: first fake-ffprobe `metadata.probe` backend workflow through `WorkflowGraph -> ExecutionPlan -> Scheduler claim -> RuntimeManager RuntimeBinding -> task.json -> AdapterRegistry -> FFprobeMetadataAdapter -> WorkerEvent/Artifact -> SQLite`.
- Not implemented: GUI trigger, real ffprobe smoke test, video transcode, audio extract, subtitle mux/burn, ASR, OCR, Translate Agent, enhancement adapters, plugin adapter discovery, production adapter cancellation, or retry/recovery action execution.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_adapter_registry tests.test_command_executor tests.test_ffprobe_metadata_adapter tests.test_minimal_probe_workflow
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Adapter/probe tests: 11 tests passed.
- Full unittest discovery: 98 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260505_005000 [Runtime manifest Phase A 字段加固]

- Started `docs/plan/plan_runtime_management_foundation.md` Phase A.
- Extended `atelier/runtime/manifest.py`:
  - `RuntimeManifest` now captures runtime kind, display name, platform, executable paths, library dirs, scoped env, backend tags, integrity metadata, and profile kind.
  - `ModelAssetManifest` now captures display name, model family, task types, compatible backends, size bytes, metadata, and profile kind.
- Extended `tests/test_runtime_store.py` to verify rich runtime/model manifest fields for `ffprobe`, `python.worker-dev`, and a demo model asset while keeping existing minimal manifest behavior compatible.
- Updated `docs/RUNTIME_ENVIRONMENT_SPEC.md`, `docs/APP_CODE_MAP.md`, and `docs/plan/plan_runtime_management_foundation.md`.

Runtime folder decision:

- Runtime management source code lives in `atelier/runtime/`.
- Runtime data lives under `AppPaths.data_root / "runtimes"`.
- In development, that resolves to `.atelier/AtelierData/runtimes/` under the workspace.

Current boundary:

- Implemented: manifest schema field expansion and persistence tests.
- Not implemented: runtime registration service, dry-run health checks, RuntimeSetupSnapshot, GUI runtime setup actions, adapter registry, or real external tool execution.

## 20260505_005500 [Runtime registration Phase B]

- Added `atelier/runtime/registration.py` with `RuntimeRegistrationService`.
- Added `tests/test_runtime_registration.py`.
- Runtime registration can now write local profiles into `RuntimeStore` for:
  - `ffprobe` / `ffmpeg` local executable profiles.
  - `python.worker-dev` development Worker Python profile.
  - local demo model directory profile.
- Registration rejects empty paths, missing paths, relative path traversal, duplicate runtime ids, and duplicate model ids.
- Updated `docs/RUNTIME_ENVIRONMENT_SPEC.md`, `docs/APP_CODE_MAP.md`, and `docs/plan/plan_runtime_management_foundation.md`.

Current boundary:

- Implemented: manifest-only local runtime/model profile registration.
- Not implemented: runtime download/install, dry-run executable health checks, runtime repair, RuntimeSetupSnapshot, GUI runtime setup actions, AdapterRegistry, or real adapter execution.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_runtime_registration tests.test_runtime_store tests.test_runtime_manager tests.test_runtime_health
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Runtime registration/store/manager/health tests: 12 tests passed.
- Full unittest discovery: 75 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260505_006000 [Runtime health Phase C repair hints and dry-run]

- Extended `atelier/runtime/health.py`:
  - `RuntimeHealthReport` now includes `repair_hints`.
  - `RuntimeHealthChecker.check_runtime()` accepts caller-provided `dry_run_args`.
  - dry-run probes use list-based `subprocess.run()` without `shell=True`.
- Extended `tests/test_runtime_health.py` to cover:
  - missing runtime repair hints.
  - checksum mismatch repair hints.
  - dry-run success and dry-run failure.
- Updated `docs/RUNTIME_ENVIRONMENT_SPEC.md`, `docs/APP_CODE_MAP.md`, and `docs/plan/plan_runtime_management_foundation.md`.

Current boundary:

- Implemented: path/hash health checks, GUI-readable repair hints, and caller-provided safe dry-run probes.
- Not implemented: automatic dry-run command selection, runtime repair/install, GPU driver/backend compatibility checks, RuntimeSetupSnapshot, GUI runtime setup actions, AdapterRegistry, or real adapter execution.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_runtime_health tests.test_runtime_registration tests.test_runtime_store tests.test_runtime_manager
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Runtime health/registration/store/manager tests: 13 tests passed.
- Full unittest discovery: 76 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260505_006500 [Runtime resolution Phase D diagnostics]

- Extended `atelier/runtime/manager.py`:
  - Added `RuntimeResolutionError` with `subject_id` and `reason`.
  - `RuntimeManager.resolve()` now merges manifest-scoped env into `RuntimeBinding.env`.
  - Runtime resolution now distinguishes missing component, disabled/non-ready runtime, capability mismatch, missing model asset, and non-ready model asset cases.
- Extended `tests/test_runtime_manager.py` for scoped env and diagnostic resolution errors.
- Updated `docs/RUNTIME_ENVIRONMENT_SPEC.md`, `docs/APP_CODE_MAP.md`, and `docs/plan/plan_runtime_management_foundation.md`.

Current boundary:

- Implemented: diagnostic runtime/model resolution and scoped env binding.
- Not implemented: health-gated resolution, backend tag selection, RuntimeSetupSnapshot, GUI runtime setup actions, AdapterRegistry, or real adapter execution.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_runtime_manager tests.test_runtime_health tests.test_runtime_registration tests.test_runtime_store
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Runtime manager/health/registration/store tests: 16 tests passed.
- Full unittest discovery: 79 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260505_007000 [Runtime setup snapshot Phase E]

- Added `atelier/runtime/setup.py`.
- Added `tests/test_runtime_setup_snapshot.py`.
- Runtime setup snapshot support now includes:
  - `RuntimeComponentSnapshot`
  - `ModelAssetSnapshot`
  - `RuntimeSetupSnapshot`
  - `build_runtime_setup_snapshot(store, checker)`
- Snapshot construction loads manifests from `RuntimeStore` and attaches health status, issues, repair hints, and checked paths from `RuntimeHealthChecker`.
- Updated `docs/APP_CODE_MAP.md`, `docs/plan/plan_runtime_management_foundation.md`, and `docs/plan/plan_main_app_skeleton.md`.

Current boundary:

- Implemented: GUI-readable runtime/model setup snapshot service.
- Not implemented: PySide6 runtime setup UI, registration actions from GUI, runtime repair/install, AdapterRegistry, or real adapter execution.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_runtime_setup_snapshot tests.test_runtime_manager tests.test_runtime_health tests.test_runtime_registration tests.test_runtime_store
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Runtime setup/manager/health/registration/store tests: 17 tests passed.
- Full unittest discovery: 80 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260505_007500 [Initial actionable GUI Runtime Setup]

- Completed `docs/plan/plan_initial_actionable_gui_runtime_setup.md` Phase A-D.
- Added `atelier/gui/runtime_setup_state.py` with PySide-independent Runtime Setup view state for summary counts, runtime/model display rows, status labels, detail lines, and action enabled state.
- Added `atelier/gui/runtime_setup_panel.py` with the first actionable `Runtime Setup` dock:
  - displays `RuntimeSetupSnapshot` status, issues, and repair hints.
  - exposes buttons for local `ffprobe`, `ffmpeg`, Worker Python, demo model directory, and refresh.
  - sends registration/refresh actions to an app service and renders `RuntimeRegistrationError` diagnostics.
- Added `atelier/app/runtime_setup.py` and `create_runtime_setup_service(paths)` so GUI actions go through `RuntimeRegistrationService`, `RuntimeHealthChecker`, and snapshot refresh instead of writing manifests or building commands in widgets.
- Updated `atelier/gui/app.py` and `atelier/gui/main_window.py` so the development launch path wires `RuntimeSetupAppService` into `MainWindow`.
- Added tests:
  - `tests/test_app_runtime_setup_service.py`
  - `tests/test_gui_runtime_setup_state.py`
  - `tests/test_gui_runtime_setup.py`
  - extended `tests/test_gui_app_entry.py` and `tests/test_gui_smoke.py`
- Updated `docs/APP_CODE_MAP.md`, `docs/Atelier_Main_UI_Spec.md`, `docs/plan/plan_initial_actionable_gui_runtime_setup.md`, and `docs/plan/plan_main_app_skeleton.md`.

Current boundary:

- Implemented: minimal local runtime/model registration entry from GUI, snapshot refresh, diagnostic error display, and offscreen Qt coverage.
- Not implemented: real workflow execution, Scheduler/Worker launch from GUI, runtime download/install/repair, plugin installation UI, full Settings system, theme polish, or real adapter execution.

Validation run:

```powershell
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Full unittest discovery: 87 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260505_004500 [归档一次性完成计划文档]

- Created `docs/plan/archive/one_off_completed_plans_20260505.zip`.
- Archived six completed one-off import/alignment/planning documents that no longer drive active implementation phases:
  - `plan_brand_icon_pack_import.md`
  - `plan_external_tool_integration_spec.md`
  - `plan_scheduling_docs_import.md`
  - `plan_split_docs_v2_import_alignment.md`
  - `plan_translate_agent_spec_alignment.md`
  - `plan_ui_design_source_alignment.md`
- Kept active implementation and follow-up plans in `docs/plan/`, including the main app skeleton plan, historical implementation plans, and the new Runtime / actionable GUI / minimal adapter workflow plans.

Current boundary:

- Implemented: archive packaging and active plan folder cleanup.
- Not implemented: deletion of durable specs or RECENT_CHANGES history.

## 20260505_004000 [新增 Runtime 管理与最简 adapter 后续计划]

- Added `docs/plan/plan_runtime_management_foundation.md` as the next implementation plan before testing a minimal real workflow.
- Added `docs/plan/plan_initial_actionable_gui_runtime_setup.md` as the follow-up plan for a minimal actionable Runtime Setup GUI surface.
- Added `docs/plan/plan_minimal_adapter_probe_workflow.md` as the follow-up plan for the first real adapter workflow using `metadata.probe` / ffprobe.
- Updated `docs/plan/plan_main_app_skeleton.md` execution order so Runtime management comes before actionable GUI and minimal adapter work.

Decision:

- Do not start a real adapter or workflow test before RuntimeManager can register, health-check, resolve, and expose local runtime/model profiles.
- The first real adapter should be metadata probe rather than ASR/OCR/translation/video enhancement, because it validates runtime path, typed command, artifact, and dispatch boundaries at lower risk.

Current boundary:

- Implemented: planning only.
- Not implemented: runtime registration service, RuntimeSetupSnapshot, actionable GUI, AdapterRegistry, CommandSpec executor, FFprobeMetadataAdapter, or minimal real workflow.

## 20260505_003000 [完成 lifecycle dispatch timeout/cancel/protocol-error 覆盖]

- Aligned `docs/plan/plan_scheduler_lifecycle_dispatch_integration.md` with the new external tool integration boundary:
  - this plan remains limited to the claimed-task Scheduler dispatch seam.
  - real external tools, plugin backends, RuntimeManager automatic backend selection, and real adapters remain out of scope.
- Extended `tests/test_scheduler_worker_runner_integration.py` with integration coverage for lifecycle dispatch:
  - silent worker timeout persists `FailedEvent(error_code="TIMEOUT")`, marks the task `failed`, preserves stderr log path, and releases the active resource lock.
  - cancel-aware worker persists `CANCELLED`, normalizes task status to `cancelled`, and releases the active resource lock.
  - stuck cancel worker is terminated after cancel grace, persists `CANCELLED`, normalizes task status to `cancelled`, and releases the active resource lock.
  - lifecycle protocol error persists `FailedEvent(error_code="INTERNAL")`, preserves stderr log details, marks the task `failed`, and releases the active resource lock.
- Updated `docs/WORKER_PROTOCOL.md`, `docs/APP_CODE_MAP.md`, and `docs/plan/plan_main_app_skeleton.md`.

Current boundary:

- Implemented: claimed-task dispatch persistence for lifecycle completed, timeout, cancel, failed, and protocol-error stub worker paths.
- Not implemented: GUI cancellation wiring, automatic claim loop, retry/recovery action execution, real adapters, external tool profiles, plugin backend execution, or production process tree governance.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_scheduler_worker_runner_integration tests.test_worker_lifecycle tests.test_worker_runner
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
Select-String -Path .\docs\*.md, .\docs\plan\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Related runner / dispatch tests: 19 tests passed.
- Full unittest discovery: 71 tests passed.
- `compileall`: passed.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260505_002000 [规划第三方外部工具接入边界]

- Added `docs/EXTERNAL_TOOL_INTEGRATION_SPEC.md` to define how third-party tools, local CLI tools, local SDKs, remote providers, managed runtimes, and plugin-provided backends enter Atelier.
- Added `docs/plan/plan_external_tool_integration_spec.md`.
- Recorded the core decision:
  - external tool execution is an independent adapter/runtime/worker contract.
  - the plugin system is the contribution, packaging, permission, registration, enable/disable, and update layer.
- Updated `README.md`, `docs/ADAPTER_SPEC.md`, `docs/PLUGIN_SYSTEM_SPEC.md`, `docs/RUNTIME_ENVIRONMENT_SPEC.md`, and `docs/SECURITY_PRIVACY_SPEC.md` so LADA-like video repair tools, translation providers, OCR backends, ASR backends, and video enhancement tools share the same architecture path.

Current boundary:

- Implemented: documentation/spec alignment only.
- Not implemented: `ExternalToolKind`, `ExternalToolBinding`, `AdapterRegistry`, external tool profile UI, real plugin manifest parser, real LADA-like adapter, or third-party backend execution.

Validation run:

```powershell
Select-String -Path .\docs\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260505_001500 [导入 Split Docs v2 并对齐主要卡片目录]

- Read `C:\Users\Administrator\Downloads\atelier_split_docs_v2\README.md` and `DOC_ALIGNMENT_NOTES.md`.
- Moved 11 split docs v2 planning documents into `docs/`:
  - `PRODUCT_FLOW_SPEC.md`
  - `MVP_ACCEPTANCE_SPEC.md`
  - `ADAPTER_SPEC.md`
  - `FFMPEG_ADAPTER_SPEC.md`
  - `ASR_ADAPTER_SPEC.md`
  - `OCR_ADAPTER_SPEC.md`
  - `VIDEO_ENHANCE_ADAPTER_SPEC.md`
  - `ARTIFACT_LIFECYCLE_SPEC.md`
  - `UI_STATE_SPEC.md`
  - `ONBOARDING_RUNTIME_SETUP_SPEC.md`
  - `DOC_ALIGNMENT_NOTES.md`
- Kept the external pack `README.md` in the download folder as import context instead of adding `docs/README.md`.
- Added `.gitignore` entries for temporary user-provided SVG drafts:
  - `atelier/assets/brand/001.svg`
  - `atelier/assets/brand/01.svg`
- Updated the canonical main built-in node list in `docs/WORKFLOW_NODE_SPEC.md`:
  - input: `input.video`, `input.audio`, `input.subtitle`
  - preprocessing: `media.audio_extract`
  - subtitle: `asr.whisper`, `ocr.recognition`, `translate.llm`, `subtitle.review`, `subtitle.normalize`
  - video: `enhance.realesrgan`, `enhance.rife`
  - compose: `compose.mux_subtitle`, `compose.burn_subtitle`, `compose.mux_audio`
  - output: `output.export`
- Updated `README.md`, `PRODUCT_FLOW_SPEC.md`, `BATCH_PIPELINE_SCHEDULING_SPEC.md`, `HARDWARE_SCHEDULING_PAGE_SPEC.md`, `ADAPTER_SPEC.md`, `FFMPEG_ADAPTER_SPEC.md`, `WORKER_PROTOCOL.md`, `RUNTIME_ENVIRONMENT_SPEC.md`, `EXECUTION_PLAN_SPEC.md`, `SCHEDULING_PRESETS_SPEC.md`, `ARTIFACT_LIFECYCLE_SPEC.md`, `DOC_ALIGNMENT_NOTES.md`, and `TRANSLATE_AGENT_SPEC.md` to align OCR and the main card catalog.
- Added `docs/plan/plan_split_docs_v2_import_alignment.md`.

Current boundary:

- Implemented: documentation import, exact SVG ignore rules, and planning/spec alignment.
- Not implemented: real adapters, OCR runtime, FFmpeg command builders, product flow UI, UI state machine, onboarding setup, MVP test harness, or Scheduler policy code.

Validation run:

```powershell
Get-FileHash C:\Users\Administrator\Downloads\atelier_split_docs_v2\*.md
Get-FileHash .\docs\<imported split docs>
git check-ignore -v atelier/assets/brand/001.svg atelier/assets/brand/01.svg
git check-ignore -v atelier/assets/brand/atelier_icon_full.svg
Select-String -Path .\docs\*.md, .\README.md, .\.gitignore -Pattern '[ \t]+$'
git diff --check
```

Result:

- Initial move hashes matched for the imported split docs before follow-up alignment edits.
- `001.svg` and `01.svg` are ignored by `.gitignore`.
- `atelier_icon_full.svg` is not ignored, so tracked brand SVG assets remain eligible for commit.
- Trailing whitespace scan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260505_000500 [纳入 Translate Agent 专项规格]

- Added `docs/TRANSLATE_AGENT_SPEC.md` as the planning source for the `Translate Agent` card focused on SRT / OCR-context subtitle translation.
- Updated `README.md` so the document index includes `TRANSLATE_AGENT_SPEC.md` and the product scope records future OCR subtitle / screen-text recognition.
- Updated `docs/WORKFLOW_NODE_SPEC.md` with:
  - `ocr.recognition`
  - `subtitle.normalize`
  - `ocr_text_track` port data type
  - optional `ocr_context_in` input for `translate.llm`
  - explicit boundary that OCR Recognition remains its own node / adapter / plugin path.
- Updated `docs/WORKER_PROTOCOL.md` and `docs/DATABASE_SCHEMA.md` so `ocr_text_track` and Translate Agent fusion / warnings metadata have a documented artifact path.
- Updated `docs/Atelier_Main_UI_Spec.md` so the selected `Translate Agent` card and Inspector express ASR/OCR fusion rather than a single plain translation service.
- Updated `docs/APP_CODE_MAP.md` and added `docs/plan/plan_translate_agent_spec_alignment.md`.

Current boundary:

- Implemented: documentation/spec alignment only.
- Not implemented: OCR Recognition adapter, Translate Agent models, provider clients, Scheduler optional/degraded dependencies, real GUI controls, or Worker adapter execution.

Validation run:

```powershell
Select-String -Path .\docs\*.md, .\README.md -Pattern '[ \t]+$'
git diff --check
```

Result:

- Trailing whitespace scan for docs and `README.md`: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260504_058500 [对齐品牌 SVG 与 PNG 参考渲染]

- Used the user-provided PNG renders in `atelier/assets/brand/` as visual references:
  - `01.png` for `atelier_icon_full.svg`
  - `02.png` for `atelier_logo_standard.svg`
  - `03.png` for `atelier_logo_compact.svg`
  - `04.png` for `atelier_logo_mono.svg` and tray variants
- Redrew the six brand SVG files as pure vector assets with larger rounded `A` geometry, multi-lane workflow lines, node blocks, transparent SVG mask cutouts, and stronger full-icon glow:
  - `atelier_icon_full.svg`
  - `atelier_logo_standard.svg`
  - `atelier_logo_compact.svg`
  - `atelier_logo_mono.svg`
  - `atelier_tray_dark.svg`
  - `atelier_tray_light.svg`
- Updated `atelier/assets/icon_manifest.json` with four `brand_reference` entries for the PNG references.
- Updated `atelier/assets/brand/preview.html` so the SVG variants and PNG references can be compared in one local preview page.
- Updated `atelier/assets/brand/README.md`, `atelier/assets/README.md`, `DESIGN.md`, `docs/APP_CODE_MAP.md`, and `docs/plan/plan_brand_icon_pack_import.md` to record that the PNG files are visual reference renders and runtime UI should still prefer SVG.

Current boundary:

- Implemented: SVG visual realignment and documentation updates.
- Not implemented: raster export pipeline, installer icon generation, Qt `.qrc`, IconManager, or runtime icon loading.
- Note: after this change, the brand SVG files intentionally no longer match the original imported SVG hashes from `C:\Users\Administrator\Downloads\atelier_icon_pack`.

Validation run:

```powershell
Get-ChildItem .\atelier\assets\brand -Filter *.svg | ForEach-Object { [xml](Get-Content -Raw -Encoding UTF8 $_.FullName) | Out-Null }
Select-String -Path .\atelier\assets\brand\*.svg -Pattern '<image|<script|font-face|base64'
git diff --check
```

Result:

- All six brand SVG files parse as XML.
- Forbidden raster/script/font/base64 pattern scan returned no matches.
- `atelier/assets/icon_manifest.json`: valid JSON with 90 entries, including 6 `brand` entries and 4 `brand_reference` entries.
- Trailing whitespace scan for touched brand assets and docs: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260504_058000 [导入 Atelier 软件品牌图标]

- Read external icon pack README at `C:\Users\Administrator\Downloads\atelier_icon_pack\README.md`.
- Imported the Atelier software brand icon pack into `atelier/assets/brand/`:
  - `atelier_icon_full.svg`
  - `atelier_logo_standard.svg`
  - `atelier_logo_compact.svg`
  - `atelier_logo_mono.svg`
  - `atelier_tray_dark.svg`
  - `atelier_tray_light.svg`
  - `preview.html`
  - `README.md`
- Updated `atelier/assets/icon_manifest.json` with `brand` category entries.
- Updated `atelier/assets/README.md`, `DESIGN.md`, `docs/Atelier_Main_UI_Spec.md`, `README.md`, and `docs/APP_CODE_MAP.md` to distinguish software brand icons from UI functional icons.
- Added `docs/plan/plan_brand_icon_pack_import.md`.

Current boundary:

- Implemented: brand icon asset import and documentation alignment.
- Not implemented: Qt `.qrc`, IconManager, runtime icon loading, Windows `.ico`, macOS `.icns`, PNG export sizes, installer integration, or tray integration.

Validation run:

```powershell
Get-FileHash C:\Users\Administrator\Downloads\atelier_icon_pack\*.svg
Get-FileHash .\atelier\assets\brand\*.svg
git diff --check
```

Result:

- Imported SVG hashes match the external source files:
  - `atelier_icon_full.svg`: `9570CB40B277308DFE6DE3A56EAEEFB121DE0321DE6EE9B1C3BF777CB044B129`
  - `atelier_logo_standard.svg`: `66895AB1AB985FA5D776E809A184B3D29F85AA152997BF49580D2261C3D2551B`
  - `atelier_logo_compact.svg`: `6F457284BB8871BF34687F4D3840976798872F93D913845BCD378DCF20D9D9D7`
  - `atelier_logo_mono.svg`: `57870087FE3FA666BF1DBB1451ED91378D8C829FB5BF71DD362B7CBB1B44445F`
  - `atelier_tray_dark.svg`: `A50CBF0BF63BD014B98DE54B5638706EB7D0BDB034D3C31E27BA2F7F53D4D831`
  - `atelier_tray_light.svg`: `D942336A7B1F275CD83BEB40CAA154C56655BD5944AE5F51E88FFA4353BE4E9F`
- Imported `README.md` and `preview.html` hashes also match external source files.
- `atelier/assets/icon_manifest.json`: valid JSON with 86 entries, including 6 `brand` entries.
- Trailing whitespace scan for brand assets and import plan: no matches.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260504_057500 [导入 Scheduling Docs Pack]

- Read external docs pack README at `C:\Users\Administrator\Downloads\atelier_scheduling_docs\README.md`.
- Imported the three scheduling planning docs into `docs/`:
  - `docs/BATCH_PIPELINE_SCHEDULING_SPEC.md`
  - `docs/HARDWARE_SCHEDULING_PAGE_SPEC.md`
  - `docs/SCHEDULING_PRESETS_SPEC.md`
- Added `docs/plan/plan_scheduling_docs_import.md` to record the import objective, scope, constraints, and verification.
- Updated `README.md` document index so the new scheduling specs are discoverable.

Current boundary:

- Implemented: documentation import and index update only.
- Not implemented: batch pipeline scheduler, SchedulingPageSnapshot builder, Hardware Scheduling UI page, scheduling presets runtime model, Scheduler waiting reason generation, or preset application behavior.

Validation run:

```powershell
Get-FileHash C:\Users\Administrator\Downloads\atelier_scheduling_docs\*.md
Get-FileHash .\docs\BATCH_PIPELINE_SCHEDULING_SPEC.md
Get-FileHash .\docs\HARDWARE_SCHEDULING_PAGE_SPEC.md
Get-FileHash .\docs\SCHEDULING_PRESETS_SPEC.md
git diff --check
```

Result:

- Imported doc hashes match the external source files:
  - `BATCH_PIPELINE_SCHEDULING_SPEC.md`: `AE5626513C60227B6E3950FE1F968EEBCA8C83BD210836F4458706ABD73B74F0`
  - `HARDWARE_SCHEDULING_PAGE_SPEC.md`: `8278E87CF98940B9E8C8E3BFC2F9F73BD04E50772CC277015D1229870C180F15`
  - `SCHEDULING_PRESETS_SPEC.md`: `120C40583D82F63E77EFAC70E9B7D67E2F7E70F911F234A82B1A4D77F903606B`
- Trailing whitespace scan for imported docs and import plan: no matches.
- `git diff --check`: passed for tracked modifications with only Windows CRLF conversion warnings.

## 20260504_057000 [进入 Scheduler Lifecycle Dispatch Integration Phase A]

- Added `docs/plan/plan_scheduler_lifecycle_dispatch_integration.md` as the next plan after worker lifecycle controls.
- Extended `tests/test_scheduler_worker_runner_integration.py` before implementation and confirmed the first failure was `dispatch_claimed_task()` not accepting `lifecycle_config`.
- Updated `atelier/scheduler/dispatch.py` so `dispatch_claimed_task()`:
  - preserves the existing minimum runner path when lifecycle options are not supplied;
  - uses `run_worker_lifecycle()` when `lifecycle_config`, `cancel_event`, or `stderr_log_path` is supplied;
  - returns `stderr_log_path`, `timed_out`, `cancelled`, and `killed` on `WorkerDispatchResult`.
- Updated `docs/APP_CODE_MAP.md` and `docs/plan/plan_main_app_skeleton.md`.

Current Phase A boundary:

- Implemented: completed stub worker dispatch path can opt into lifecycle runner and stderr log path.
- Not implemented: timeout dispatch persistence, cancel dispatch persistence, lifecycle protocol-error dispatch persistence, automatic dispatch loop, GUI cancellation, retry/recovery actions, or real adapters.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_scheduler_worker_runner_integration
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
git diff --check
```

Result:

- `tests.test_scheduler_worker_runner_integration`: passed after the expected initial missing-parameter failure.
- `tests.test_scheduler_worker_runner_integration tests.test_worker_lifecycle tests.test_worker_runner`: 15 tests passed.
- `.venv\Scripts\python -m unittest discover -s tests`: 67 tests passed.
- `.venv\Scripts\python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260504_056500 [补充 Worker Lifecycle Protocol Error 收束]

- Added `docs/plan/plan_worker_lifecycle_controls.md` Phase F after reviewing the completed lifecycle plan.
- Extended `tests/test_worker_lifecycle.py` before implementation and confirmed the first failure was the protocol-error path not writing stderr log and waiting for the bad worker to exit naturally.
- Updated `run_worker_lifecycle()` so malformed stdout or event-order protocol errors:
  - terminate the offending worker;
  - kill it if it ignores terminate within `terminate_grace_seconds`;
  - preserve stderr and return code on `WorkerProcessProtocolError`;
  - write stderr to the caller-provided `stderr_log_path`.
- Updated `docs/WORKER_PROTOCOL.md`, `docs/APP_CODE_MAP.md`, `docs/plan/plan_main_app_skeleton.md`, and `docs/plan/plan_worker_lifecycle_controls.md`.

Current boundary:

- Implemented: protocol-error worker termination and stderr log preservation for lifecycle runner.
- Not implemented: Scheduler dispatch integration with lifecycle runner, GUI cancellation, pause, adapter-specific cancellation, process tree governance, retry/recovery action execution, or real adapters.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_worker_lifecycle
.venv\Scripts\python -m unittest tests.test_worker_lifecycle tests.test_worker_runner
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
git diff --check
```

Result:

- `tests.test_worker_lifecycle`: 7 tests passed after the expected initial protocol-error stderr-log failure.
- `tests.test_worker_lifecycle tests.test_worker_runner`: 10 tests passed.
- `.venv\Scripts\python -m unittest discover -s tests`: 66 tests passed.
- `.venv\Scripts\python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260504_056000 [执行 Worker Lifecycle Controls Phase C-D-E]

- Continued `docs/plan/plan_worker_lifecycle_controls.md` through Phase C, Phase D, and Phase E after Phase B passed.
- Extended `tests/test_worker_lifecycle.py` before implementation and confirmed the first Phase C failure was `run_worker_lifecycle()` missing `cancel_event`.
- Added minimum cancel control to `run_worker_lifecycle()`:
  - accepts a caller-provided `threading.Event`;
  - sends `{"type":"cancel"}` over worker stdin when cancellation is requested;
  - treats a cancel-aware `FailedEvent(error_code="CANCELLED")` as cancelled;
  - terminates and, if needed, kills workers that ignore cancel beyond `cancel_grace_seconds`;
  - returns structured `CANCELLED` failure facts for forced cancellation.
- Extended `tests/test_worker_lifecycle.py` before implementation for Phase D and confirmed `stderr_log_path` was missing.
- Added optional stderr log persistence through `run_worker_lifecycle(stderr_log_path=...)`; stderr remains available in the result string and is written to the caller-provided log path.
- Updated `docs/WORKER_PROTOCOL.md`, `docs/APP_CODE_MAP.md`, `docs/plan/plan_main_app_skeleton.md`, and `docs/plan/plan_worker_lifecycle_controls.md`.

Current boundary:

- Implemented: lifecycle runner interface, incremental stdout, startup/heartbeat timeout, structured `TIMEOUT`, minimum stdin cancel, cancel grace terminate/kill behavior, structured `CANCELLED`, and optional stderr file persistence.
- Not implemented: GUI/Scheduler cancellation wiring, pause, adapter-specific cancellation, process-tree/job-object governance, retry/recovery action execution, log viewer UI, or real FFmpeg/model adapters.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_worker_lifecycle
.venv\Scripts\python -m unittest tests.test_worker_lifecycle tests.test_worker_runner
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
git diff --check
```

Result:

- `tests.test_worker_lifecycle`: 6 tests passed after the expected Phase C/D missing-interface failures.
- `tests.test_worker_lifecycle tests.test_worker_runner`: 9 tests passed.
- `.venv\Scripts\python -m unittest discover -s tests`: 65 tests passed.
- `.venv\Scripts\python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260504_055500 [执行 Worker Lifecycle Controls Phase B]

- Continued `docs/plan/plan_worker_lifecycle_controls.md` Phase B after Phase A passed.
- Extended `tests/test_worker_lifecycle.py` before implementation and confirmed the first failure was silent worker timeout still escaping as `WorkerProcessProtocolError` for an empty stdout event stream.
- Reworked `run_worker_lifecycle()` in `atelier/workers/runner.py` to:
  - start workers with `subprocess.Popen()`;
  - read stdout JSON Lines incrementally;
  - enforce startup/heartbeat deadlines from `WorkerLifecycleConfig`;
  - convert silent timeout into `FailedEvent(error_code="TIMEOUT", recoverable=True)`;
  - terminate the timed-out worker and kill it if it does not exit within `terminate_grace_seconds`;
  - close stdin/stdout/stderr pipes cleanly.
- Added heartbeat keep-alive coverage so normal heartbeat output refreshes the deadline and does not become a timeout.
- Updated `docs/WORKER_PROTOCOL.md`, `docs/APP_CODE_MAP.md`, `docs/plan/plan_main_app_skeleton.md`, and `docs/plan/plan_worker_lifecycle_controls.md`.

Current Phase B boundary:

- Implemented: incremental stdout reading, startup/heartbeat timeout handling, structured `TIMEOUT` failure event, timeout terminate/kill behavior, and heartbeat keep-alive coverage.
- Not implemented: stdin cancel control, user-initiated cancellation semantics, stderr file persistence, Scheduler dispatch integration, GUI cancellation, or real adapters.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_worker_lifecycle
.venv\Scripts\python -m unittest tests.test_worker_lifecycle tests.test_worker_runner
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
git diff --check
```

Result:

- `tests.test_worker_lifecycle`: 3 tests passed after the expected initial timeout failure.
- `tests.test_worker_lifecycle tests.test_worker_runner`: 6 tests passed.
- `.venv\Scripts\python -m unittest discover -s tests`: 62 tests passed.
- `.venv\Scripts\python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260504_055000 [执行 Worker Lifecycle Controls Phase A]

- Continued `docs/plan/plan_worker_lifecycle_controls.md` after `plan_scheduler_worker_runner_integration.md` was completed.
- Added `tests/test_worker_lifecycle.py` before implementation and confirmed the first failure was missing `WorkerLifecycleConfig` from `atelier.workers.runner`.
- Added Phase A lifecycle runner interface shape in `atelier/workers/runner.py`:
  - `WorkerLifecycleConfig`
  - `WorkerLifecycleResult`
  - `run_worker_lifecycle()`
- `run_worker_lifecycle()` currently preserves existing minimum runner behavior by delegating to `run_worker_process()` and returning lifecycle facts: events, stderr, return code, optional stderr log path, timed_out, cancelled, and killed.
- Updated `docs/WORKER_PROTOCOL.md`, `docs/APP_CODE_MAP.md`, `docs/plan/plan_main_app_skeleton.md`, and `docs/plan/plan_worker_lifecycle_controls.md`.

Current Phase A boundary:

- Implemented: lifecycle configuration/result API shape and compatibility entry point over the existing stub subprocess runner.
- Not implemented: incremental stdout reading, startup timeout enforcement, heartbeat timeout, stdin cancel control, terminate/kill escalation, stderr file persistence, Scheduler dispatch integration, GUI cancellation, or real adapters.

Validation run:

```powershell
.venv\Scripts\python -m unittest tests.test_worker_lifecycle
.venv\Scripts\python -m unittest tests.test_worker_lifecycle tests.test_worker_runner
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
git diff --check
```

Result:

- `tests.test_worker_lifecycle`: passed after the expected initial missing-interface failure.
- `tests.test_worker_lifecycle tests.test_worker_runner`: 4 tests passed.
- `.venv\Scripts\python -m unittest discover -s tests`: 60 tests passed.
- `.venv\Scripts\python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260504_054000 [补充 Atelier 图标库事实]

- Confirmed `atelier/assets/` is the current Atelier UI icon library.
- Updated `atelier/assets/README.md` to:
  - remove the old non-Atelier product name;
  - document `icon_manifest.json`, `atelier_icons_sprite.svg`, and `preview.html`;
  - clarify that icons are 24 × 24 `currentColor` SVG line icons for dark-first workstation UI;
  - state that the directory is a resource library, not an implemented Qt `.qrc`, IconManager, icon cache, or runtime recoloring system.
- Updated `DESIGN.md`, `docs/Atelier_Main_UI_Spec.md`, and `docs/UI_WORKSPACE_SPEC.md` to make `atelier/assets/` the icon source for toolbar, navigation, workflow nodes, queue, hardware, status, inspector, and system surfaces.
- Updated `README.md`, `docs/APP_CODE_MAP.md`, and `docs/plan/plan_main_app_skeleton.md` so handoff docs now record the icon library without adding non-code assets to the Python code file count.
- Updated `docs/plan/plan_ui_design_source_alignment.md` with the asset-library decision and boundary.

Current boundary:

- Implemented: documentation and resource ownership alignment for the existing SVG icon library.
- Not implemented: Qt `.qrc` registration, IconManager, icon caching, runtime theme recoloring, or icon usage in real GUI widgets.

Validation run:

```powershell
# Checked repository text for the old non-Atelier product name.
.venv\Scripts\python -m unittest discover -s tests
.venv\Scripts\python -m compileall -q atelier tests
git diff --check
```

Result:

- Old non-Atelier product-name search: no matches outside ignored local/git directories.
- `.venv\Scripts\python -m unittest discover -s tests`: 59 tests passed.
- `.venv\Scripts\python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260504_053000 [对齐主 UI 设计事实源]

- Added `docs/plan/plan_ui_design_source_alignment.md` before editing design docs.
- Reviewed the new `docs/Atelier_Main_UI_Spec.md`, root `DESIGN.md`, `docs/UI_WORKSPACE_SPEC.md`, and the sidebar reference at `E:\AI\AiVideoSRTGui\app\gui\sidebar_navigation.py`.
- Updated `DESIGN.md` so:
  - default Atelier UI theme is dark-first;
  - light theme is preserved as future theme switching;
  - `DESIGN.md` remains the design source of truth;
  - `docs/Atelier_Main_UI_Spec.md` is the main UI drawing / concept implementation spec;
  - `docs/design-md-references/` is a constructive suggestion source only;
  - Workflow Page / card-line-flow graph is the primary UI stage;
  - Queue Monitor, Hardware Resources, and Card Detailed Settings are embeddable/floating panels.
- Updated `docs/Atelier_Main_UI_Spec.md` so:
  - product name is only `Atelier`;
  - fixed coordinates are concept drawing coordinates, not immutable product geometry;
  - top bar order, collapsible sidebar, Workflow child pages, and embeddable/floating panels align with `DESIGN.md`.
- Updated `README.md` and `docs/UI_WORKSPACE_SPEC.md` to include the new UI spec relationship and sidebar/workspace rules.

Current boundary:

- Implemented: documentation alignment only.
- Not implemented: actual dark theme, real Workflow Canvas drawing, collapsible sidebar code, panel docking UI, theme switching, or visual verification.

Validation run:

```powershell
git diff --check
```

Result:

- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260504_052000 [执行 Scheduler Worker Runner Phase C]

- Continued `docs/plan/plan_scheduler_worker_runner_integration.md` Phase C before implementation.
- Extended `tests/test_scheduler_worker_runner_integration.py` before implementation and confirmed the first failure was `dispatch_claimed_task()` still letting malformed stdout escape as `WorkerProtocolError`.
- Added `WorkerProcessProtocolError` in `atelier/workers/runner.py`; it subclasses `WorkerProtocolError` and preserves stderr plus return code when stdout event validation fails.
- Updated `dispatch_claimed_task()` in `atelier/scheduler/dispatch.py` so `WorkerProcessProtocolError` is converted into a persisted `FailedEvent(error_code="INTERNAL", recoverable=False)`.
- Valid failed stub worker dispatch coverage now verifies failure facts, stderr, return code, failed status, and resource lock release.
- Protocol-error dispatch coverage now verifies malformed stdout records an internal failed event, preserves stderr/return code, marks the task failed, and releases the active resource lock.
- Updated `docs/APP_CODE_MAP.md`, `docs/plan/plan_main_app_skeleton.md`, and `docs/plan/plan_scheduler_worker_runner_integration.md`.

Current Phase C boundary:

- Implemented: valid failed worker stream persistence and protocol-error-to-failed-event persistence for the narrow claimed-task dispatch seam.
- Not implemented: automatic claim loop, RuntimeManager command selection, real adapters, timeout, cancel, kill escalation, stderr file persistence, retry/recovery orchestration, or GUI execution.

Validation run:

```powershell
.venv/Scripts/python -m unittest tests.test_scheduler_worker_runner_integration tests.test_worker_runner
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest tests.test_scheduler_worker_runner_integration tests.test_worker_runner`: 7 tests passed.
- `.venv/Scripts/python -m unittest discover -s tests`: 59 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260504_051000 [执行 Scheduler Worker Runner Phase B]

- Continued `docs/plan/plan_scheduler_worker_runner_integration.md` Phase B before implementation.
- Extended `tests/test_scheduler_worker_runner_integration.py` before implementation and confirmed the first failure was missing `fetch_task_artifact_links`.
- Added `fetch_task_artifact_links()` in `atelier/storage/repositories.py` to verify `task_artifacts` links without changing artifact write behavior.
- Completed stub worker dispatch coverage now verifies:
  - `started -> artifact -> completed` events are persisted to `task_events`;
  - artifact paths are persisted to `artifacts`;
  - output artifact links are persisted to `task_artifacts`;
  - task status becomes `completed`;
  - active resource lock is released.
- Updated `docs/APP_CODE_MAP.md`, `docs/plan/plan_main_app_skeleton.md`, and `docs/plan/plan_scheduler_worker_runner_integration.md`.

Current Phase B boundary:

- Implemented: completed stub worker dispatch path with event, artifact, task-artifact link, terminal status, and lock release verification.
- Not implemented: valid failed worker path, protocol-error conversion to `FailedEvent`, automatic claim loop, RuntimeManager command selection, real adapters, timeout, cancel, kill escalation, stderr file persistence, retry/recovery orchestration, or GUI execution.

Validation run:

```powershell
.venv/Scripts/python -m unittest tests.test_scheduler_worker_runner_integration
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest tests.test_scheduler_worker_runner_integration`: 2 tests passed.
- `.venv/Scripts/python -m unittest discover -s tests`: 57 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260504_050000 [执行 Scheduler Worker Runner Phase A]

- Continued `docs/plan/plan_scheduler_worker_runner_integration.md` Phase A before implementation.
- Added `tests/test_scheduler_worker_runner_integration.py` before implementation and confirmed the first failure was missing `atelier.scheduler.dispatch`.
- Added `atelier/scheduler/dispatch.py` with:
  - `WorkerDispatchResult`
  - `dispatch_claimed_task()`
- `dispatch_claimed_task()` accepts an already claimed `ClaimedTask`, copies the Scheduler-provided `ResourceBinding` onto the task payload, writes `task.json`, runs the supplied stub worker command through `run_worker_process()`, persists returned events through `record_worker_events()`, and returns task id, parsed events, stderr, return code, and final SQLite task status.
- Updated `docs/APP_CODE_MAP.md`, `docs/plan/plan_main_app_skeleton.md`, and `docs/plan/plan_scheduler_worker_runner_integration.md`.

Current Phase A boundary:

- Implemented: first claimed-task dispatch seam from Scheduler claim to `task.json`, runner, SQLite event persistence, and structured dispatch result.
- Not implemented: completed artifact-path coverage, failed worker path, protocol-error conversion to `FailedEvent`, automatic claim loop, RuntimeManager command selection, real adapters, timeout, cancel, kill escalation, stderr file persistence, retry/recovery orchestration, or GUI execution.

Validation run:

```powershell
.venv/Scripts/python -m unittest tests.test_scheduler_worker_runner_integration
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest tests.test_scheduler_worker_runner_integration`: 1 test passed.
- `.venv/Scripts/python -m unittest discover -s tests`: 56 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260504_044000 [新增后续两个 Worker 计划]

- Added `docs/plan/plan_scheduler_worker_runner_integration.md`.
  - Execution order: first.
  - Scope: connect `SimpleScheduler` claim, `task.json`, `run_worker_process()`, and `record_worker_events()` into a stub-worker dispatch loop.
  - Boundary: no real FFmpeg/model adapter, no RuntimeManager command selection, no GUI execution, no timeout/cancel lifecycle controls.
- Added `docs/plan/plan_worker_lifecycle_controls.md`.
  - Execution order: second.
  - Scope: add worker startup/heartbeat timeout, cancel, terminate/kill escalation, and stderr file persistence.
  - Boundary: should run after scheduler-runner integration and still use stub workers before real adapters.
- Updated `docs/plan/plan_main_app_skeleton.md` and `docs/plan/plan_worker_protocol_runner.md` to link the two plans in order.

Validation run:

```powershell
git diff --check
```

Result:

- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260504_043336 [执行 Worker Protocol Phase E]

- Extended `docs/plan/plan_worker_protocol_runner.md` with Phase E before implementation.
- Added `tests/test_worker_task_file.py` before implementation and confirmed the first failure was missing `atelier.workers.task_file`.
- Added `atelier/workers/task_file.py` with:
  - `write_worker_task_file()`
  - `build_worker_process_spec()`
  - `DEFAULT_WORKER_TASK_FILE_NAME`
- `write_worker_task_file()` serializes a full `ExecutionTask` to `task.json` through a temporary file and atomic replace.
- `build_worker_process_spec()` creates `{work_root}/{task_id}`, writes `task.json`, and returns a `WorkerProcessSpec`.
- Worker env generation now includes `ExecutionTask.runtime_binding.env`; explicit caller env overrides duplicate keys.
- Updated `README.md`, `docs/APP_CODE_MAP.md`, `docs/WORKER_PROTOCOL.md`, `docs/plan/plan_main_app_skeleton.md`, and `docs/plan/plan_worker_protocol_runner.md`.

Current Phase E boundary:

- Implemented: `ExecutionTask -> task.json -> WorkerProcessSpec` bridge.
- Not implemented: Scheduler integration, RuntimeManager path resolution, worker execution, timeout, cancel, retry/recovery orchestration, or real adapters.

Validation run:

```powershell
.venv/Scripts/python -m unittest tests.test_worker_task_file
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest tests.test_worker_task_file`: 2 tests passed.
- `.venv/Scripts/python -m unittest discover -s tests`: 55 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260504_004244 [执行 Worker Protocol Phase C]

- Continued `docs/plan/plan_worker_protocol_runner.md` Phase C before implementation.
- Added `tests/test_worker_runner.py` before implementation and confirmed the first failure was missing `atelier.workers.runner`.
- Added `atelier/workers/runner.py` with:
  - `WorkerProcessSpec`
  - `WorkerProcessResult`
  - `run_worker_process()`
- The minimum runner now starts a typed command with `--task-file`, sets `cwd=work_dir`, merges supplied env variables, captures stdout/stderr, validates stdout through `parse_worker_event_stream()`, and returns the process exit code.
- Tests use temporary Python stub workers only; no real FFmpeg/model adapter is invoked.
- Updated `README.md`, `docs/APP_CODE_MAP.md`, `docs/WORKER_PROTOCOL.md`, `docs/plan/plan_main_app_skeleton.md`, and `docs/plan/plan_worker_protocol_runner.md`.

Current Phase C boundary:

- Implemented: minimum subprocess runner boundary, stdout event validation, stderr capture, return code capture, and protocol error propagation for malformed stdout.
- Not implemented: Scheduler integration, RuntimeManager path resolution, stdin cancel/pause, heartbeat timeout, kill escalation, stderr file persistence, retry/recovery orchestration, or real worker adapters.

Validation run:

```powershell
.venv/Scripts/python -m unittest tests.test_worker_runner
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest tests.test_worker_runner`: 3 tests passed.
- `.venv/Scripts/python -m unittest discover -s tests`: 53 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed.

## 20260504_003223 [执行 Worker Protocol Phase B]

- Continued `docs/plan/plan_worker_protocol_runner.md` Phase B before implementation.
- Extended `tests/test_worker_protocol.py` before implementation and confirmed the first failure was missing `parse_worker_event_stream`.
- Added `parse_worker_event_stream()` in `atelier/workers/protocol.py`.
- Worker event stream validation now enforces:
  - first event must be `started`;
  - `seq` must be contiguous from 0;
  - stream must end with `completed` or `failed`;
  - no events may appear after a terminal event.
- Updated `README.md`, `docs/APP_CODE_MAP.md`, `docs/WORKER_PROTOCOL.md`, `docs/plan/plan_main_app_skeleton.md`, and `docs/plan/plan_worker_protocol_runner.md`.

Current Phase B boundary:

- Implemented: minimal stdout JSON Lines event stream lifecycle validation.
- Not implemented: subprocess runner, stdin cancel/pause control, heartbeat timeout kill logic, stderr capture, real worker adapters, or real FFmpeg/model execution.

Validation run:

```powershell
.venv/Scripts/python -m unittest tests.test_worker_protocol
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest tests.test_worker_protocol`: 9 tests passed.
- `.venv/Scripts/python -m unittest discover -s tests`: 50 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_124750 [执行 Worker Protocol Phase A]

- Added `docs/plan/plan_worker_protocol_runner.md` before implementation.
- Added `tests/test_worker_protocol.py` before implementation and confirmed the first failure was missing `HeartbeatEvent` / `LogEvent` from `atelier.domain.worker_event`.
- Added `LogEvent` and `HeartbeatEvent` to `atelier/domain/worker_event.py`.
- Added `atelier/workers/protocol.py` with:
  - `format_worker_event_json_line()`
  - `parse_worker_event_json_line()`
  - `WorkerProtocolError`
- Worker protocol helpers now serialize typed worker events to newline-terminated JSON Lines and parse single JSON Lines back to concrete event models by `type`.
- Malformed JSON, non-object JSON, missing/invalid event type, unknown event type, and invalid event payloads fail explicitly.
- Updated `docs/WORKER_PROTOCOL.md` from “planning / not implemented” to “partially implemented”.
- Updated `README.md`, `docs/APP_CODE_MAP.md`, and `docs/plan/plan_main_app_skeleton.md`.

Current Phase A boundary:

- Implemented: single-event Worker JSON Lines encode/decode, `log` / `heartbeat` event models, and protocol error boundary.
- Not implemented: whole-stream lifecycle validation, subprocess runner, stdin cancel/pause control, heartbeat timeout kill logic, stderr capture, real worker adapters, or real FFmpeg/model execution.

Validation run:

```powershell
.venv/Scripts/python -m unittest tests.test_worker_protocol
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest tests.test_worker_protocol`: 4 tests passed.
- `.venv/Scripts/python -m unittest discover -s tests`: 45 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_092651 [执行只读 PySide6 工作台 Phase F]

- Extended `docs/plan/plan_readonly_pyside6_workbench.md` with Phase F before implementation.
- Added `tests/test_gui_app_entry.py` before implementation and confirmed the first failure was missing `atelier.gui.app`.
- Added `atelier/gui/app.py` as the formal development launch entry for the read-only workbench.
- Launch entry now supports `.venv/Scripts/python -m atelier.gui.app`.
- Added CLI options:
  - `--workspace-root`
  - `--data-root`
  - `--no-restore-layout`
- `build_launch_context()` opens SQLite, reads a `WorkbenchSnapshot`, creates `MainWindow`, and optionally restores workspace layout without entering the Qt event loop.
- `main()` shows the window and enters the Qt event loop only at the launch boundary.
- Updated `docs/APP_CODE_MAP.md` and `docs/plan/plan_readonly_pyside6_workbench.md`.

Current Phase F boundary:

- Implemented: formal development GUI entry, launch args, snapshot-backed window creation, optional layout restore, and offscreen smoke validation.
- Not implemented: packaged application entry, app icon/resource bundling, single-instance behavior, tray/menu system, startup error UI, or real task execution from GUI.

Validation run:

```powershell
.venv/Scripts/python -m unittest tests.test_gui_app_entry
.venv/Scripts/python -m unittest tests.test_gui_smoke
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest tests.test_gui_app_entry`: 2 tests passed.
- `.venv/Scripts/python -m unittest tests.test_gui_smoke`: 3 tests passed.
- `.venv/Scripts/python -m unittest discover -s tests`: 41 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.
- offscreen `atelier.gui.app.main(["--workspace-root", ".", "--no-restore-layout"])` timer smoke: passed.

## 20260503_091411 [执行只读 PySide6 工作台 Phase E]

- Extended `docs/plan/plan_readonly_pyside6_workbench.md` with Phase E before implementation.
- Added `tests/test_gui_layout_store.py` before implementation and confirmed the first failure was missing `atelier.gui.layout_store`.
- Added `AppPaths.workspace_layouts_path` so workspace layout persistence uses the managed `AtelierData/cache` root.
- Added `atelier/gui/layout_store.py` with `WorkspaceLayoutStore` and `WorkspaceLayoutRecord`.
- Added `MainWindow.save_workspace_layout()` and `MainWindow.restore_workspace_layout()` for Qt geometry/state bytes.
- Extended `tests/test_gui_smoke.py` to verify `MainWindow` can save and restore a stored layout.
- Updated `docs/APP_CODE_MAP.md`, `docs/plan/plan_main_app_skeleton.md`, and `docs/plan/plan_readonly_pyside6_workbench.md`.

Current Phase E boundary:

- Implemented: minimal named workspace layout save/load and `MainWindow` save/restore integration.
- Not implemented: workspace preset UI, panel visibility management, layout migration, multi-profile layout policies, or screenshot-level visual verification.

Validation run:

```powershell
.venv/Scripts/python -m unittest tests.test_gui_layout_store
.venv/Scripts/python -m unittest tests.test_gui_smoke
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest tests.test_gui_layout_store`: 2 tests passed.
- `.venv/Scripts/python -m unittest tests.test_gui_smoke`: 3 tests passed.
- `.venv/Scripts/python -m unittest discover -s tests`: 39 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_084529 [执行只读 PySide6 工作台 Phase A-D]

- Started execution of `docs/plan/plan_readonly_pyside6_workbench.md` after completing the resource locks / failure recovery plan.
- Added `tests/test_gui_optional_dependency.py` before implementation and confirmed the first failure was `ModuleNotFoundError: No module named 'atelier.gui'`.
- Added `atelier/gui/__init__.py` and `atelier/gui/entry.py`.
- Added `check_gui_dependency()` and `ensure_gui_dependency()` so GUI entry code can be imported without PySide6 installed and missing GUI extras produce a clear install command.
- Kept PySide6 as an optional dependency under `pyproject.toml` `gui` extras; it is not a core hard dependency.
- Installed GUI extras in the local development `.venv` with `.venv/Scripts/python -m pip install -e ".[gui]"`; PySide6 6.11.0 is now available locally.
- Added `tests/test_gui_smoke.py` before implementation and confirmed the first failure was missing `atelier.gui.main_window`.
- Added `atelier/gui/main_window.py` and `atelier/gui/workspace.py` with a read-only `QMainWindow` shell and workflow / execution / queue / resources-runtime docks.
- Added `tests/test_gui_state_reader.py` before implementation and confirmed the first failure was missing `atelier.gui.state_reader`.
- Added `atelier/gui/state_reader.py` with `WorkbenchSnapshot`, `WorkbenchTaskItem`, and `read_workbench_snapshot()`.
- Updated `MainWindow` so Queue panel can render task id, node type, status, resource device, event count, and artifact path from a `WorkbenchSnapshot`.
- Updated `docs/APP_CODE_MAP.md`, `docs/plan/plan_main_app_skeleton.md`, `docs/plan/plan_readonly_pyside6_workbench.md`, and `README.md`.

Current GUI boundary:

- Implemented: optional GUI dependency detection, read-only `MainWindow`, four dockable workstation panels, read-only SQLite view model, and offscreen construction tests.
- Not implemented: real Workflow Canvas drawing/editing, task start actions, Scheduler/worker control from GUI, theme system, i18n catalog, dock layout persistence, screenshot-level visual verification, or real runtime/model panels.

Validation run:

```powershell
.venv/Scripts/python -m pip install -e ".[gui]"
.venv/Scripts/python -m unittest tests.test_gui_optional_dependency
.venv/Scripts/python -m unittest tests.test_gui_smoke
.venv/Scripts/python -m unittest tests.test_gui_state_reader
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m pip install -e ".[gui]"`: passed; PySide6 6.11.0 installed in local `.venv`.
- `.venv/Scripts/python -m unittest tests.test_gui_optional_dependency`: 2 tests passed.
- `.venv/Scripts/python -m unittest tests.test_gui_smoke`: 2 tests passed.
- `.venv/Scripts/python -m unittest tests.test_gui_state_reader`: 1 test passed.
- `.venv/Scripts/python -m unittest discover -s tests`: 36 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_080447 [执行 resource locks Phase D]

- Extended `tests/test_resource_locks.py` before implementation and confirmed the first failure was the missing `fetch_stale_resource_locks` repository helper.
- Added `StaleResourceLockRecord`, `fetch_stale_resource_locks()`, and `release_stale_resource_lock()` in `atelier/storage/repositories.py`.
- Stale detection now returns unreleased locks whose `stale_after` timestamp is older than or equal to the supplied `now`.
- Stale release marks the lock released by `lock_id` and leaves the task status unchanged, preserving crash recovery as a later explicit decision.
- Added guard coverage confirming stale release rejects locks that are not stale yet or were already released.
- Updated `docs/APP_CODE_MAP.md`, `docs/plan/plan_main_app_skeleton.md`, and `docs/plan/plan_resource_locks_failure_recovery.md`.

Current Phase D boundary:

- Implemented: stale resource lock detection, explicit stale lock release, and release guards for non-stale/already-released locks.
- Not implemented: crash recovery scan orchestration, retry execution, worker subprocess supervision, or GUI recovery panels.

Validation run:

```powershell
.venv/Scripts/python -m unittest tests.test_resource_locks
.venv/Scripts/python -m unittest tests.test_failure_recovery
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest tests.test_resource_locks`: 6 tests passed.
- `.venv/Scripts/python -m unittest tests.test_failure_recovery`: 2 tests passed.
- `.venv/Scripts/python -m unittest discover -s tests`: 31 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_075217 [执行 resource locks Phase C]

- Added `tests/test_failure_recovery.py` before implementation and confirmed the first failure was the missing `fetch_failure_facts` repository helper.
- Added `FailureFacts`, `RecoveryOption`, `fetch_failure_facts()`, and `suggest_recovery_options()` in `atelier/storage/repositories.py`.
- Updated `record_worker_events()` so `FailedEvent.partial_artifacts` are persisted as `partial` artifacts linked through `task_artifacts`.
- Updated terminal failure persistence so `execution_tasks.error_code` and `execution_tasks.error_message` are populated from `FailedEvent`.
- Updated `docs/APP_CODE_MAP.md`, `docs/plan/plan_main_app_skeleton.md`, and `docs/plan/plan_resource_locks_failure_recovery.md`.

Current Phase C boundary:

- Implemented: failed task facts, partial artifact path query, recoverable retry/use-partial suggestions, and non-recoverable inspect/export suggestions.
- Not implemented yet: stale lock detection, retry execution, GUI recovery panels, and real worker subprocess recovery.

Validation run:

```powershell
.venv/Scripts/python -m unittest tests.test_resource_locks
.venv/Scripts/python -m unittest tests.test_failure_recovery
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest tests.test_resource_locks`: 4 tests passed.
- `.venv/Scripts/python -m unittest tests.test_failure_recovery`: 2 tests passed.
- `.venv/Scripts/python -m unittest discover -s tests`: 29 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_073409 [执行 resource locks Phase A]

- Started execution of `docs/plan/plan_resource_locks_failure_recovery.md`.
- Added `tests/test_resource_locks.py` before implementation and confirmed the first failure was missing `fetch_active_resource_lock`.
- Added `ResourceLockRecord` and `fetch_active_resource_lock()` in `atelier/storage/repositories.py`.
- Updated `mark_task_running()` so Scheduler claim now creates an active `resource_locks` row in the same claim path.
- Updated `docs/APP_CODE_MAP.md` and `docs/plan/plan_resource_locks_failure_recovery.md`.

Current Phase A boundary:

- Implemented: Scheduler claim creates a queryable active resource lock.
- Not implemented yet: terminal event lock release, failure facts, recovery options, stale lock detection.

Validation run:

```powershell
.venv/Scripts/python -m unittest tests.test_resource_locks
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest tests.test_resource_locks`: passed.
- `.venv/Scripts/python -m unittest discover -s tests`: 24 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_074057 [执行 resource locks Phase B]

- Extended `tests/test_resource_locks.py` before implementation to cover terminal event lock release for:
  - `CompletedEvent`
  - `FailedEvent(error_code="CANCELLED")`
  - ordinary recoverable `FailedEvent`
- Confirmed the expected red state: task status was updated but active locks were not released.
- Updated `record_worker_events()` terminal event path in `atelier/storage/repositories.py` so active resource locks are released after task status is updated.
- Updated `docs/plan/plan_resource_locks_failure_recovery.md`.

Current Phase B boundary:

- Implemented: completed / cancelled / failed terminal events release active locks.
- Not implemented yet: failed task facts, recovery options, stale lock detection.

Validation run:

```powershell
.venv/Scripts/python -m unittest tests.test_resource_locks
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest tests.test_resource_locks`: 4 tests passed.
- `.venv/Scripts/python -m unittest discover -s tests`: 27 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_072200 [分发后续两个子计划]

- Added `docs/plan/plan_resource_locks_failure_recovery.md`.
  - Execution order: first.
  - Scope: resource locks, terminal event lock release, failure facts, recovery options, stale lock detection.
  - Boundary: no real worker subprocesses, no production multi-process locking, no GUI recovery panel.
- Added `docs/plan/plan_readonly_pyside6_workbench.md`.
  - Execution order: second.
  - Scope: read-only PySide6 workbench shell that renders existing SQLite / runtime / queue state.
  - Boundary: no heavy task execution in GUI, no real Workflow Canvas editing, no FFmpeg/model work.
- Updated `docs/plan/plan_main_app_skeleton.md` Child Plans to link both sub-plans and record the intended execution order.

Validation run:

```powershell
git diff --check
```

Result:

- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_065626 [完成 Phase 7 最小 queue / Scheduler claim]

- Added `atelier/scheduler/simple.py` with `SimpleScheduler` and `ClaimedTask`.
- Added minimum queue helpers to `atelier/storage/repositories.py`:
  - `fetch_next_runnable_task()`
  - `mark_task_running()`
  - `fetch_task_resource_binding()`
- `SimpleScheduler` now finds dependency-ready pending tasks, creates a `ResourceBinding`, and marks the task as `running`.
- Added `tests/test_scheduler_simple.py` before implementation and confirmed the first failure was `ModuleNotFoundError: No module named 'atelier.scheduler'`.
- Updated `README.md`, `docs/ARCHITECTURE.md`, `docs/APP_CODE_MAP.md`, and `docs/plan/plan_main_app_skeleton.md`.

Current Phase 7 boundary:

- Implemented: dependency-ready pending task claim, CPU resource binding, persisted `running` task status, persisted `ResourceBinding`.
- Not implemented: durable multi-process queue claiming, resource locks, priorities, concurrency, retries, failure recovery actions, real worker subprocess dispatch.

Validation run:

```powershell
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest discover -s tests`: 23 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_064008 [完成 Phase 6 最小业务闭环]

- Added minimal workflow graph models in `atelier/workflow/graph.py`:
  - `WorkflowGraph`
  - `WorkflowNode`
  - `WorkflowEdge`
  - `WorkflowPortRef`
- Added `ExecutionPlan` to `atelier/domain/execution_plan.py` and added default `phase_id` / `lane_id` to `ExecutionTask`.
- Added `build_linear_execution_plan()` in `atelier/planning/simple.py`.
- Added minimal SQLite persistence helpers in `atelier/storage/repositories.py`:
  - `persist_planned_execution()`
  - `record_worker_events()`
  - `fetch_task_event_types()`
  - `fetch_artifact_paths()`
  - `fetch_task_status()`
- Added `tests/test_phase6_minimal_loop.py` before implementation and confirmed the first failure was `ModuleNotFoundError: No module named 'atelier.planning'`.
- Added `tests/test_planning_simple.py` for simple planner behavior and empty graph rejection.
- Updated `README.md`, `docs/ARCHITECTURE.md`, `docs/APP_CODE_MAP.md`, and `docs/plan/plan_main_app_skeleton.md` to reflect that Phase 6 now has a first working minimum loop.

Current Phase 6 boundary:

- Implemented: `WorkflowGraph -> ExecutionPlan -> simulated Worker -> SQLite events/artifacts`.
- Not implemented: queue claiming, Scheduler, resource locks, real worker subprocesses, real adapters, failure recovery actions, GUI queue monitor.

Validation run:

```powershell
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `.venv/Scripts/python -m unittest discover -s tests`: 22 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_062834 [按 AGENTS 规则中文化主计划]

- Reviewed `AGENTS.md` Planning Discipline against `docs/plan/plan_main_app_skeleton.md`.
- Confirmed the plan already used the correct location, main-plan filename prefix, and the required nine-section structure.
- Rewrote `docs/plan/plan_main_app_skeleton.md` in Chinese while preserving the AGENTS-required section skeleton through bilingual headings.
- Updated stale plan facts:
  - Current local Python is `Python 3.11.9`.
  - `.venv/` editable install exists.
  - Current validation baseline is 19 passing unittest tests.
  - `AppPaths` and app-level `create_runtime_store()` / `open_app_database()` exist.
- Added Phase 6 for the next minimum business loop: `WorkflowGraph -> ExecutionPlan -> simulated Worker -> SQLite events/artifacts`.

Validation run:

```powershell
git diff --check
.venv/Scripts/python -m unittest discover -s tests
```

Result:

- `git diff --check`: passed with only Windows CRLF conversion warnings.
- `.venv/Scripts/python -m unittest discover -s tests`: 19 tests passed.

## 20260503_062202 [接入 AppPaths 到 RuntimeStore 与 SQLite]

- Added `atelier/app/services.py` as app-level orchestration glue.
- Added `create_runtime_store(paths)` to create `RuntimeStore` from `AppPaths.data_root` after ensuring the shared data layout exists.
- Added `open_app_database(paths)` to open `AppPaths.database_path` and initialize the SQLite schema.
- Kept `runtime/` and `storage/` independent from `app/`; app layer performs the wiring.
- Added `tests/test_app_services.py` before implementation and confirmed the initial failure was `ModuleNotFoundError: No module named 'atelier.app.services'`.
- Fixed the SQLite test to close the connection explicitly because `sqlite3.Connection` as a context manager does not release the file handle on Windows.
- Updated `docs/APP_CODE_MAP.md` to include `atelier/app/services.py`, `tests/test_app_services.py`, and the new code file count.
- Updated `docs/plan/plan_main_app_skeleton.md` with Phase 5 for AppPaths integration.

Validation run:

```powershell
.venv/Scripts/python -m unittest tests.test_app_services
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- `tests/test_app_services.py` passed after adding app-level factories and explicit SQLite connection close in the test.
- Final `.venv/Scripts/python -m unittest discover -s tests`: 19 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_060137 [建立开发 venv 与 AppPaths 路径管理]

- Created local `.venv/` for development and installed Atelier in editable mode with `.venv/Scripts/python -m pip install -e .`.
- Verified the current suite inside `.venv/` before adding new path code.
- Added `atelier/app/paths.py` with `AppPaths`:
  - `for_development(workspace_root)` resolves local development data to `.atelier/AtelierData`.
  - `from_data_root(data_root)` supports release/user-data roots supplied by future installers or settings.
  - Standard path properties cover runtime/model manifests, database, runtimes, models, plugins, cache, staging, and logs.
  - `ensure_data_dirs()` creates the shared local data directory layout without creating `.venv/`.
- Added `tests/test_app_paths.py` before implementation and confirmed the initial failure was `ModuleNotFoundError: No module named 'atelier.app.paths'`.
- Updated `docs/APP_CODE_MAP.md` to include `atelier/app/paths.py`, `tests/test_app_paths.py`, and the new code file count.

Validation run:

```powershell
.venv/Scripts/python -m pip install -e .
.venv/Scripts/python -m unittest discover -s tests
.venv/Scripts/python -m compileall -q atelier tests
git diff --check
```

Result:

- Editable install succeeded in `.venv/`.
- Existing suite passed in `.venv/` before `AppPaths`.
- `tests/test_app_paths.py` failed first for the expected missing module.
- `tests/test_app_paths.py` passed after adding `AppPaths`.
- Final `.venv/Scripts/python -m unittest discover -s tests`: 17 tests passed.
- `.venv/Scripts/python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_055526 [明确开发 venv 与 runtime 目录边界]

- Clarified the three environment layers in `docs/RUNTIME_ENVIRONMENT_SPEC.md`:
  - App Install Dir for packaged GUI runtime, PySide6, Qt plugins, DLLs, and application code.
  - AtelierData Dir for managed tool/backend/worker runtimes, models, plugins, cache, staging, logs, and database.
  - Dev Workspace for source code, `.venv/`, test caches, and developer-local `.atelier/AtelierData`.
- Documented that `atelier/runtime/` is source code for runtime management and must not store runtime binaries or virtual environments.
- Added `.venv/`, `venv/`, and `.atelier/` to `.gitignore`.
- Updated `docs/APP_CODE_MAP.md` with environment directory boundaries and `.gitignore` responsibilities.

Validation run:

```powershell
git diff --check
```

Result:

- `git diff --check`: passed with only Windows CRLF conversion warnings.

## 20260503_050504 [首版 Python 骨架、runtime 基础与接手文档]

- Started the first executable Python skeleton after the documentation baseline commits `cdadba9` and `6316a75`.
- Added `pyproject.toml` with package metadata, Python version constraints, `pydantic` dependency, and planned optional groups for `dev`, `gui`, `scheduler`, and `storage`.
- Added `atelier/` package boundaries:
  - `app/` for future boot orchestration.
  - `core/` for small shared utilities.
  - `domain/` for pure pydantic execution/resource/runtime/worker-event models.
  - `runtime/` for managed runtime manifests, store, binding resolution, and health checks.
  - `security/` for package integrity helpers.
  - `storage/` for SQLite schema initialization.
  - `workers/` for a simulated worker event path.
  - `hardware/`, `i18n/`, `plugins/`, and `release/` as side-effect-free placeholder packages.
- Added `RuntimeStore` in `atelier/runtime/store.py` to persist local runtime and model manifests under an `AtelierData`-style directory layout.
- Added `RuntimeHealthChecker` in `atelier/runtime/health.py` to check declared component/model paths and SHA-256 mismatch states without touching global `PATH`.
- Added `sha256_file()` and `verify_sha256()` in `atelier/security/package_integrity.py`.
- Updated `RuntimeManager` so it can resolve from manifests loaded by `RuntimeStore`.
- Added first unittest coverage:
  - worker terminal status normalization.
  - runtime binding resolution.
  - runtime manifest store persistence.
  - runtime health path/hash checks.
  - package SHA-256 verification.
  - SQLite core table creation.
  - simulated worker event ordering.
- Added Python cache/build exclusions to `.gitignore`.
- Updated `README.md`, `docs/ARCHITECTURE.md`, and `docs/plan/plan_main_app_skeleton.md` so they no longer describe the skeleton/runtime layer as not started or empty.
- Added `docs/APP_CODE_MAP.md` as the current code tree and responsibility map.
- Added this `docs/RECENT_CHANGES.md` file as the durable change memory.

Validation run:

```powershell
python -m unittest discover -s tests
python -m compileall -q atelier tests
git diff --check
```

Result:

- `python -m unittest discover -s tests`: 14 tests passed.
- `python -m compileall -q atelier tests`: passed.
- `git diff --check`: passed with only Windows CRLF conversion warnings.

Known boundaries after this change:

- No real GUI exists yet.
- No real Scheduler exists yet.
- No real WorkflowGraph to ExecutionPlan planner exists yet.
- No real FFmpeg/model adapters exist yet.
- No SQLAlchemy repositories or migrations exist yet.
- No package download/install/update chain exists yet.
- Runtime health checks are local path/hash checks only; executable dry-run, backend compatibility, and repair flows are future work.
