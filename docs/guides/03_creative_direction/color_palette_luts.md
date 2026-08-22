---
title: Color Palette & Chapter LUTs
category: Creative Direction
tags: color, palette, lut, chapters, hex, grade
source: docs/teded_style_bible.md, docs/dynamic_vibrant_tricks.md
---

# Color Palette & Chapter LUTs

Five narrative chapters, five palettes, five LUTs. Background color continuity
across a scene pair = "same idea continues"; palette shift = new chapter.

## Chapters

| Chapter | Scenes | Palette | LUT |
|---|---|---|---|
| Dawn | S01–S02 | `#E8845C` orange · `#7B6BA8` purple · `#F5D5A0` warm yellow | `LUT_Dawn.cube` |
| Daylight | S03–S04 | `#FFFFFF` white · `#4CAF50` green · `#E8F5E9` light green | `LUT_Daylight.cube` |
| DarkData | S05–S06 | `#1A1A2E` charcoal · `#00E676` neon green · `#16213E` navy | `LUT_DarkData.cube` |
| CoolTension | S07–S08 | `#37474F` slate · `#FF6B35` accent · `#78909C` muted gray | `LUT_CoolTension.cube` |
| HopefulDusk | S09–S10 | `#1A237E` deep blue · `#FFD54F` gold · `#263238` charcoal | `LUT_HopefulDusk.cube` |

## Hero colors

- **Yellow ball identity:** `#FFD54F` (white highlight, `#F9A825` shadow).
- Base design system: soft-but-vivid with a yellow base.

## Rules

- Neon only in DarkData. Do not spill neon into Dawn.
- S07–S08: desaturate background 30–40%; hero stays warm → S09 gold flood reads
  as release.
- Accent pop frames: 1–2 frames of boosted midtones on whoosh transitions.
- Chapter snap at chapter cuts (no ramps across a chapter boundary).
- Blender AgX Medium-High → soft-pop polish per chapter in Resolve Color.