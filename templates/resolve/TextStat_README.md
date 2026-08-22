# TextStat — Animated Stat Callout (Fusion Macro)

Reusable TED-Ed style stat overlay for AFRICA Season 1.

## Usage in DaVinci Resolve Fusion

1. Open **Episode 01 - Assembly** timeline
2. Go to **Fusion** page on a clip with a stat moment
3. Add **Text+** node or import this macro
4. Set parameters:

| Parameter | Value | Notes |
|-----------|-------|-------|
| Font | Inter Bold | Install from Google Fonts |
| Size | 96 (stats) / 36 (labels) | Scale for 1080p |
| Color | `#00E676` (stats) / `#FFFFFF` (labels) | Chapter accent override |
| Stroke | 3px `#1A1A2E` | Readability on any bg |
| Animation In | Move Y +24→0, Opacity 0→1, 8 frames | Ease Out |
| Hold | 36-48 frames | Minimum readable time |
| Animation Out | Opacity 1→0, 6 frames | Optional |

## Stat Moments (Episode 01)

| Stat | Scene | Approx Time | Color |
|------|-------|-------------|-------|
| `$984M` | S05 | ~2:50 | `#00E676` |
| `82%` | S05 | ~3:15 | `#FF6B35` |
| `97%` | S07 | ~4:08 | `#FF6B35` |
| `2007` | S02 | ~0:52 | `#E8845C` |
| `Forecast` | S09 | ~6:00 | `#FFD54F` |

## Keyframes (Fusion)

```
Frame 0:   Position Y = 0.52, Opacity = 0
Frame 8:   Position Y = 0.48, Opacity = 1  (ease out)
Frame 44:  Hold
Frame 50:  Opacity = 0  (optional exit)
```

## Episode 2 Adaptation

Copy macro, change stat strings and colors per city chapter palette.
See `docs/teded_style_bible.md` for chapter colors.
