# Atelier SVG Icon Pack

This pack contains pure SVG vector assets for the Atelier app icon system.

## Files

| File | Purpose |
|---|---|
| `atelier_icon_full.svg` | Full app icon / installer / about page / desktop concept |
| `atelier_logo_standard.svg` | Top-left app header logo / welcome page / medium UI brand mark |
| `atelier_logo_compact.svg` | Small-size UI mark, suitable for 16–32 px contexts |
| `atelier_logo_mono.svg` | `currentColor` monochrome source, useful for theming |
| `atelier_tray_dark.svg` | White monochrome tray/icon mark for dark UI |
| `atelier_tray_light.svg` | Dark monochrome tray/icon mark for light UI |
| `01.png` | Visual reference render for `atelier_icon_full.svg` |
| `02.png` | Visual reference render for `atelier_logo_standard.svg` |
| `03.png` | Visual reference render for `atelier_logo_compact.svg` |
| `04.png` | Visual reference render for `atelier_logo_mono.svg` and tray variants |

## Brand idea

Atelier icon language:

```text
A + Flow + Scheduling
```

The full icon keeps the premium glowing app-tile feeling. The standard and compact variants reduce detail for interface usage. The monochrome variants remove gradients for tray, disabled, high-contrast, and documentation use.

The PNG files are reference renders for visual alignment. Runtime UI should prefer the SVG files unless an installer, operating-system package, or export pipeline explicitly needs raster output.

## Implementation notes

- These files are pure SVG.
- No embedded raster images.
- No external fonts.
- No scripts.
- The SVG files are manually aligned to the PNG reference renders while remaining pure vector assets.
- Small-size icons should use `atelier_logo_compact.svg` or tray variants instead of simply scaling down `atelier_icon_full.svg`.

## Suggested export sizes

```text
PNG: 16, 20, 24, 32, 48, 64, 128, 256, 512, 1024
Windows ICO: include 16, 24, 32, 48, 64, 128, 256
macOS ICNS: export from 16 through 1024
```
