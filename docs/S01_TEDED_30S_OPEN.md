# S01 TED-Ed 30s infographic opening

**Reference:** [TED-Ed high-speed rail explainer](https://youtu.be/2A1IEBFt6Xg)  
**Craft:** [TED-Ed Animation Basics](https://ed.ted.com/ted_ed_collections/animation-basics) · whip [tutorial](https://xere.my/tutorials/whip-pan-transition/) · zoom blur [tutorial](https://cutsio.com/blog/zoom-transition-tutorial-in-davinci-resolve-smooth-zoom-blur-transition)  
**Deliverable:** `renders/paced_overlays/s01_teded_open_30s.mp4`  
**Verified:** 1920×1080 · H.264 High · **24 fps** · **720 frames** · **30.000 s** · silent (VO stays on A1)

**QC locks (do not bypass):** Blender **5.1.2** only · **4K HOLD** · user VO on A1 · yellow-base palette · shots **≤5s** · verify ffprobe before marking done · see `.cursor/rules/africa-s1-creative-gate.mdc` and `docs/PRE_4K_GATE.md`.

**Blender51 sidecar (optional plate):** `blend/africa_s1_teded_open30.blend` → `renders/paced_overlays/s01_teded_open30_blender51.mp4` (CPU Cycles; does not touch master blend or GPU HQ job).

This is a **V3/V4 kinetic overlay** for the first 30s of S01 (Africa whip window). It does **not** replace the Blender plate. HQ S01 render was left running.

## Grammar (match TED-Ed rail open)

| Rule | How we used it |
|------|----------------|
| One idea per cut | 10 beats, 2.0–4.0 s each (all ≤5 s) |
| Big type + diagram | Clock, factor cards, flow, split, title lockup |
| VO-led | Locked to cold-open script: 06:30 → matatus → pockets → money moved → Silicon Savannah |
| Cited stats | **82.1%** / **42.3M** — [CA Kenya Q2 FY2024/25](https://www.ca.go.ke/sites/default/files/2025-03/Sector%20Statistics%20Report%20Q2%202024-2025.pdf) |
| Yellow-base | `#FFD54F` on `#1A1408` |

## Beat sheet (24 fps)

| # | Time | Frames | On-screen | Trans | Still |
|---|------|--------|-----------|-------|-------|
| 01 | 0.0–2.0 | 48 | `06:30` · NAIROBI | hard cut | `open30_01_stat.png` |
| 02 | 2.0–4.5 | 60 | MATATUS · three cards | hard cut | `open30_02_label.png` |
| 03 | 4.5–7.0 | 60 | THE REAL MOTION ISN'T ON THE ROAD | whip | `open30_03_label.png` |
| 04 | 7.0–10.0 | 72 | PHONE → NETWORK → SYSTEM | zoom blur | `open30_04_flow.png` |
| 05 | 10.0–13.5 | 84 | **82.1%** mobile-money penetration | hard cut | `open30_05_stat.png` |
| 06 | 13.5–16.5 | 72 | **42.3M** subscriptions | hard cut | `open30_06_stat.png` |
| 07 | 16.5–20.0 | 84 | MONEY HAS ALREADY MOVED · RENT/STOCK/LOAN | hard cut | `open30_07_paths.png` |
| 08 | 20.0–23.0 | 72 | BANK BRANCH vs JUST A PHONE | hard cut | `open30_08_compare.png` |
| 09 | 23.0–27.0 | 96 | **SILICON SAVANNAH** lockup | whip | `open30_09_title.png` |
| 10 | 27.0–30.0 | 72 | **2007** bridge → S02 | cut | `open30_10_bridge.png` |

**Total:** 720f / 30.0 s.

## Paths

| Kind | Path |
|------|------|
| Stills | `assets/canva/kinetic/infographics/open30/` |
| Per-beat clips | `renders/paced_overlays/open30_*f.mp4` |
| Assembled open | `renders/paced_overlays/s01_teded_open_30s.mp4` |
| Manifest | `renders/quality/s01_teded_open30_manifest.json` |
| Generator | `scripts/generate_s01_teded_open30.py` |
| Sources | `docs/INFOGRAPHIC_SOURCES.md` |

## Canva polish shells (1920×1080)

Blank custom canvases in the connected Canva account — drop the matching PNG, restyle type, export PNG 1920×1080 (no upscale).

| Beat | Canva design id | Title |
|------|-----------------|-------|
| 06:30 / Nairobi | `DAHSJzAbXzM` | Africa S1 OPEN 06:30 Nairobi — TED-Ed hook |
| 82.1% stat | `DAHSJ2Y1PC0` | Africa S1 OPEN 82.1% mobile money — TED-Ed stat |
| Money moved | `DAHSJzxs1ls` | Africa S1 OPEN money already moved — TED-Ed paths |
| Title lockup | `DAHSJwY5FQc` | Africa S1 OPEN Silicon Savannah lockup |

Open from Canva **Recent**, or `https://www.canva.com/design/<id>/edit`.

## Resolve placement

- Timeline **0–720f** (first 30s of S01).
- **V3:** `s01_teded_open_30s.mp4` · Composite **Normal** · opacity **85–92%**.
- **Clear V3/V4** at Africa whip (~f720) so the plate reads.
- Do not cover VO; no AI voice.

## Qwen

CPU `qwen2.5-coder:14b` was used to draft beat-sheet JSON (`renders/quality/qwen_teded_open30.json` when complete). Timing above is the **locked** sheet used for the verified MP4.
