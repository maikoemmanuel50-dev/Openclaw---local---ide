# DataVizBarChart — Parameterized Bar Chart

Reusable Geometry Nodes bar chart from Scene 05.

## File
`templates/blender/DataVizBarChart.blend` (extract from Scene 05)

## Input Parameters
| Input | Ep01 Value | Description |
|-------|-----------|-------------|
| Total | $984M | Counter target |
| Sector 1 | Fintech | Label + bar height |
| Sector 2 | Climate/Energy | Highlight bar (82%) |
| Sector 3 | E-commerce | Standard bar |
| Sector 4 | Logistics | Standard bar |
| Highlight % | 82% | Callout stat |

## Text Overlays
- `$984M` counter: keyframe scale fade at VO "a billion dollars"
- `82%` callout: keyframe at VO "eighty-two percent"
- Sector labels: stagger with bar growth

## Episode 2 Adaptation
Replace sector names and values in Geometry Nodes input panel.
Counter animates 0 → target over 60 frames.
