# Unique morph + Canva shells (CPU / limited GPU)

**GPU policy:** Blender HQ keeps the GPU. Morph generation uses `CUDA_VISIBLE_DEVICES=-1` + `libx264` software encode at **BelowNormal** priority.

**Craft refs:** [36SIUe_mOZU](https://youtu.be/36SIUe_mOZU) · [o5zHIYLqDIw](https://youtu.be/o5zHIYLqDIw) · [Canva short j4YAXZRluW4](https://www.youtube.com/shorts/j4YAXZRluW4) · [SC_3fG4mvQs](https://www.youtube.com/shorts/SC_3fG4mvQs) · [uBBmbdPbfhw](https://www.youtube.com/watch?v=uBBmbdPbfhw) · [FOnx6eTfKB8](https://www.youtube.com/watch?v=FOnx6eTfKB8)

## Uniqueness rule (hard)

Every still, extra graphic, and morph clip has a **unique asset id**. Registry: `renders/quality/UNIQUE_ASSET_REGISTRY.json` (802 ids, 20 clips, 20 extras). Byte-identical plateau frames inside a morph sequence are allowed; **no clip/still is reused across scenes**.

**Verified 2026-08-13:** 20 MP4s in `renders/paced_overlays/morph_unique/` · pack `episode_morph_pack_preview.mp4` = 1920×1080 24fps 720f.

## Morph transitions (yellow word/number → chart)

| Scene | Clip id | Word → chart |
|-------|---------|--------------|
| S01 | `morph_s01_821_to_pie` | 82.1% → pie |
| S01 | `morph_s01_423m_to_bars` | 42.3M → bars |
| S02 | `morph_s02_2007_to_flow` | 2007 → flow |
| S02 | `morph_s02_3582m_to_donut` | 35.8M → donut |
| S03 | `morph_s03_ihub_to_cards` | iHub → cards |
| S03 | `morph_s03_32b_to_bars` | $3.2B → bars |
| S04 | `morph_s04_phone_to_pie` | PHONE → pie |
| S04 | `morph_s04_93_to_donut` | 93% → donut |
| S05 | `morph_s05_984m_to_pie` | $984M → pie |
| S05 | `morph_s05_82_to_bars` | 82% → bars |
| S06 | `morph_s06_79_to_donut` | 79% → donut |
| S06 | `morph_s06_solar_to_pie` | SOLAR → pie |
| S07 | `morph_s07_974_to_pie` | 97.4% → pie |
| S07 | `morph_s07_gap_to_bars` | GAP → bars |
| S08 | `morph_s08_quiet_to_split` | QUIET → split |
| S08 | `morph_s08_30_to_donut` | >30% → donut |
| S09 | `morph_s09_number1_to_bars` | #1 → bars |
| S09 | `morph_s09_75_to_pie` | 75 → pie |
| S10 | `morph_s10_africa_to_arc` | AFRICA → arc |
| S10 | `morph_s10_end_to_trio` | END → trio |

**Paths:** frames `assets/canva/kinetic/infographics/morph_unique/<id>/` · clips `renders/paced_overlays/morph_unique/` · preview pack `renders/paced_overlays/episode_morph_pack_preview.mp4`

## Extra unique stills (S01–S10)

Folder: `assets/canva/kinetic/infographics/extra_unique/` (`x_sXX_*` — never reused in morphs or open30).

## Canva shells (1920×1080) — Composio

| Scene | Design id | Title |
|-------|-----------|-------|
| S01 | `DAHSJ52eKwA` | morph 82.1 → pie |
| S02 | `DAHSJ8sJrF8` | morph 2007 → flow |
| S03 | `DAHSJ8Vg49s` | morph 3.2B → bars |
| S04 | `DAHSJ9_QvhM` | morph PHONE → pie |
| S05 | `DAHSJ6Y0y0s` | morph 984M → pie |
| S06 | `DAHSJ61Ixeg` | morph 79 → donut |
| S07 | `DAHSJ6iAoLk` | morph 97.4 → pie |
| S08 | `DAHSJ6IecGQ` | morph QUIET split |
| S09 | `DAHSJ4P_0YQ` | morph #1 bars |
| S10 | `DAHSJwiX92Y` | morph AFRICA arc |

Drop the matching final morph frame into Canva Recents → polish → export **exact 1920×1080 PNG** (no upscale).

## Resolve use

- Place each morph clip once on **V3/V4** at the VO word/number hit for that scene only.
- Max hold ≤5 s (clips are ~1.25–1.7 s).
- Do not reuse a clip on another scene.
