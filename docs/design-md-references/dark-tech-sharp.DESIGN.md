# DESIGN.md — Dark Tech Sharp
**Style:** Dark Tech Sharp
**Use case:** Developer tools, SaaS dashboards, productivity apps, AI products
**By:** Zero to UI (02UI) — designmd.info

---

## Overview

This design system is built for products where the user needs to think, not be distracted. Everything earns its place. The background is near-black, not pure black — a deliberate choice that prevents eye fatigue and makes white text feel sharp rather than harsh. Typography does the heavy lifting. No decorative elements, no gradients for the sake of it. The layout is calm, confident, and precise. If something is on screen, it's there for a reason.

> **02UI Rationale:** The quietest room in the building is usually where the real work happens. This system is that room.

---

## Colors

| Role | Token | Hex | Usage |
|---|---|---|---|
| Background | `--color-bg` | `#0A0A0A` | Page background |
| Surface | `--color-surface` | `#141414` | Cards, panels, modals |
| Surface raised | `--color-surface-raised` | `#1C1C1C` | Hover states, secondary panels |
| Border | `--color-border` | `#2A2A2A` | Dividers, card outlines |
| Border subtle | `--color-border-subtle` | `#1F1F1F` | Secondary separators |
| Primary text | `--color-text-primary` | `#F5F5F5` | Headings, body copy |
| Secondary text | `--color-text-secondary` | `#888888` | Labels, metadata, captions |
| Muted text | `--color-text-muted` | `#555555` | Placeholder text, disabled states |
| Accent | `--color-accent` | `#FFFFFF` | Primary CTA, active states |
| Accent subtle | `--color-accent-subtle` | `#1A1A1A` | Accent surface, tag backgrounds |
| Error | `--color-error` | `#FF4444` | Destructive actions, error states |
| Success | `--color-success` | `#3ECF8E` | Confirmation, completion states |

**Do not use pure `#000000` or pure `#FFFFFF`.** The slight softening on both ends is intentional — it makes the contrast feel designed, not accidental.

---

## Typography

**Display / Hero**
- Font: `Inter` or `Geist` (variable weight)
- Weight: 400–500
- Size: 48px–72px
- Line height: 1.1
- Letter spacing: -0.02em
- Usage: Hero headlines only. Left-aligned. Never centred on product pages.

**Heading**
- Font: Same as display
- Weight: 500
- Size: 24px–36px
- Line height: 1.2
- Letter spacing: -0.01em

**Body**
- Font: Same family, regular weight
- Weight: 400
- Size: 15px–16px
- Line height: 1.6
- Letter spacing: 0

**Label / UI text**
- Weight: 500
- Size: 12px–13px
- Line height: 1.4
- Letter spacing: 0.01em
- Usage: Buttons, nav items, metadata tags

**Code / Mono**
- Font: `JetBrains Mono` or `Geist Mono`
- Size: 13px
- Line height: 1.7
- Usage: Code snippets, terminal output, file paths

> **02UI Rationale:** One typeface, multiple weights — that is discipline. The moment you add a second font family for decoration, you have already lost.

---

## Elevation

This system uses **border-based elevation**, not box shadows. Depth is communicated through subtle border contrast and background-colour steps, not light simulation.

| Level | Style | Usage |
|---|---|---|
| 0 — Flat | No border, bg `--color-bg` | Page base |
| 1 — Resting | `1px solid --color-border-subtle` | Cards, side panels |
| 2 — Raised | `1px solid --color-border` | Modals, dropdowns, active cards |
| 3 — Floating | `1px solid --color-border` + bg `--color-surface-raised` | Tooltips, command palettes |

Shadow is used **only** for floating elements like tooltips:
`box-shadow: 0 8px 32px rgba(0,0,0,0.6)`

> **02UI Rationale:** On a dark interface, shadows disappear. Borders are the honest way to show hierarchy.

---

## Components

### Buttons

| Variant | Background | Text | Border | Hover |
|---|---|---|---|---|
| Primary | `#FFFFFF` | `#0A0A0A` | none | `#E0E0E0` bg |
| Secondary | transparent | `#F5F5F5` | `1px solid --color-border` | `--color-surface-raised` bg |
| Ghost | transparent | `#888888` | none | text becomes `#F5F5F5` |
| Destructive | transparent | `#FF4444` | `1px solid #FF4444` | `rgba(255,68,68,0.1)` bg |

- Border radius: `6px`
- Padding: `8px 16px` (default), `6px 12px` (small)
- Font: label weight (500, 13px)
- No uppercase. Sentence case only.

### Inputs

- Background: `--color-surface`
- Border: `1px solid --color-border`
- Border radius: `6px`
- Padding: `10px 12px`
- Focus ring: `0 0 0 2px rgba(255,255,255,0.15)`
- Placeholder: `--color-text-muted`
- Label: above the input, 12px, `--color-text-secondary`

### Cards

- Background: `--color-surface`
- Border: `1px solid --color-border-subtle`
- Border radius: `8px`
- Padding: `20px 24px`
- Hover: border becomes `--color-border`
- No shadow on cards unless they are floating

### Navigation

- Top nav height: `52px`
- Background: `rgba(10,10,10,0.85)` with `backdrop-filter: blur(12px)`
- Logo: left, 16px from edge
- Nav links: centre, 14px, `--color-text-secondary`, hover becomes `--color-text-primary`
- CTA button: right, primary variant
- No bottom border on nav — let the blur do the work

### Tags / Badges

- Background: `--color-accent-subtle`
- Border: `1px solid --color-border`
- Border radius: `4px`
- Padding: `2px 8px`
- Font: 11px, weight 500, `--color-text-secondary`

---

## Do's and Don'ts

**Do:**
- Use negative space deliberately. Empty space is not wasted space — it is breathing room that makes content feel premium.
- Keep line lengths between 60–75 characters for body text. Wider than that and the eye gets lost.
- Use motion sparingly — fade in, 200ms ease, for panels and modals. Nothing bounces.
- Align everything to a consistent grid. 8px base unit.
- Dim secondary information visually — not everything needs to compete for attention.

**Don't:**
- Use coloured text as decoration. Colour on text means: clickable, error, or success. That is it.
- Add gradients to backgrounds. The dark surface is already doing the work.
- Use rounded corners above `8px` on desktop UI. Rounded corners signal "friendly." This product signals "precise."
- Mix font weights without purpose. Every weight choice should be explainable.
- Animate layout changes. If something moves, it should be revealing new information, not just moving.

---

*Free to use, adapt, and share. More files at designmd.info — by Zero to UI.*
