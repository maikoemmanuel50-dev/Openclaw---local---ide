---
title: "Script-to-Visual Pipeline"
category: "Production Standards"
tags: ["pipeline", "visual-generation", "blender", "resolve", "copyright", "vo-sync"]
date: 2026-08-15
version: 1.0
---

# Script-to-Visual Pipeline

Converts episode narration scripts into timed visual generation prompts for Blender and Resolve, synced to VO audio timing with copyright clearance gating.

## Quick Start

```bash
python generate_visual_pipeline.py --episode 1
```

Outputs to `pipeline/`:
- `episode_N_pipeline.json` — master scene map with frame ranges, triggers, and clearance status
- `prompts/S##_blender.py` — per-scene Blender composition/animation prose prompts
- `exec/S##_exec.json` — **machine-executable Blender plan** (planes, Z-stack, textures, camera, keyframes, render contract) for direct Blender MCP consumption
- `scenes/resolve_overlays_all.json` — Fusion TextStat overlay specs (19 overlays)
- `copyright_gate_summary.json` — asset clearance audit

## Pipeline Flow

```
episode_N_script.md ──┐
                      ├── generate_visual_pipeline.py ──> pipeline/
teded_scene_spec_epN ─┤       │
                      │       ├── episode_N_pipeline.json
audio_design_map.yaml ┘       ├── prompts/S##_blender.py
                              ├── exec/S##_exec.json   ← executable plans
                              ├── scenes/resolve_overlays_all.json
                              └── copyright_gate_summary.json
```

### Stage 1: Script → Visual Prompts
- Parses `episode_N_script.md` for scene visual directions
- Cross-references `teded_scene_spec_ep01.md` for frame-level timing
- Generates per-scene Blender prompts with:
  - Layer stack (Z-depth ordered)
  - Camera motion type and duration
  - VO-synced element animation triggers
  - On-screen text with styles and timing
  - Asset checklist (existing vs. needs creation)
  - SFX trigger points
  - Music bed assignment
- **Also generates machine-executable plans** (`exec/S##_exec.json`):
  - Ordered steps: `import_plane` (Z-layer), `texture_plane` (existing/new), `camera` (motion + frame range), `animate` (VO triggers with keyframe ranges), `text_object`, `render`
  - Includes the shared render contract (Cycles, 1920×1080, 24fps, GPU, 64 samples, output to `renders/video_clips/masters/<folder>/frame_%04d.png`)

### Stage 2: Prompts → Frames
Prefer the executable plan (`exec/S##_exec.json`) for deterministic assembly;
fall back to the prose prompt for creative heavy-lifting:
```
# A) Deterministic — read exec plan and run its steps:
GET /api/pipeline/exec?scene=S03   → ordered Blender MCP steps
blender_execute_blender_code       → import planes, keyframes, camera, render

# B) Creative — use Blender MCP on the prose prompt:
blender_execute_blender_code → set up scene from prompt
blender_generate_hyper3d_model → create new 3D assets
blender_download_polyhaven_asset → CC0 environment assets
blender_download_sketchfab_model → prop/character models
```

### Stage 3: Frames → Sync
Resolve overlays sync text/stats to VO timing:
```
Fusion TextStat template → "$984M", "82%", "97%"
timeline_markers → VO word triggers as Resolve markers
```

## Source Files Required Per Episode

| File | Purpose | Location |
|------|---------|----------|
| `episode_N_script.md` | Narration + visual directions | `Africa Season 1/` |
| `teded_scene_spec_epN.md` | Frame-level scene breakdown | `Africa Season 1/docs/` |
| `audio_design_map.yaml` | VO timing + SFX triggers | `Africa Season 1/docs/` |
| `CLEARANCE_ALLOWLIST.json` | Copyright gate rules | `Africa Season 1/docs/` |

## Adding New Scenes

Edit `SCENES` dict in `generate_visual_pipeline.py`:

```python
"SN": {
    "name": "Scene Title",
    "chapter": "Dawn|Daylight|DarkData|CoolTension|HopefulDusk",
    "camera": "Push-In|Pan|Parallax Drift|Custom zoom-out|Static",
    "duration_sec": 50,
    "frames": 1200,  # duration_sec * 24
    "style": "TED-Ed pattern description",
    "composition_bg": "...",
    "composition_mid": "...",
    "composition_fg": "...",
    "composition_overlay": "...",
    "composition_ui": "...",
    "animation_triggers": [
        {"word": "VO word", "element": "Element name", "anim": "Animation desc", "frames": "start-end"},
    ],
    "sfx": [...],
    "music": "chapter_bed.wav",
    "text": [{"string": "Label", "style": "Label 36px", "timing_sec": 10}],
    "transition_out": {"type": "cut|morph|fade|slide_wipe"},
    "assets": {"existing": [...], "new": [...]},
}
```

## Copyright Clearance Gate

Assets are checked against `CLEARANCE_ALLOWLIST.json`:

- **APPROVED** — matches a cleared prefix (e.g., `s1_`, `s2_`, `k01_`) or Mixkit/Unsplash tag
- **NEEDS_CLEARANCE** — new asset without prefix match; human review required
- **BLOCKED** — matches `exclude_substrings` or `forbid_exact`; use `replacement_map`

### Clearing New Assets

1. Add the asset prefix to `allow_graded_hq_prefixes` if it's a production-created asset
2. Or add the Mixkit/Unsplash tag to the appropriate allow list
3. Re-run the pipeline to verify clearance

### Blocked Assets

If an asset is BLOCKED, check `replacement_map` for the approved substitute.

## Blender MCP Execution Path

For each scene prompt, the agent can:

1. **Read the prompt** from `pipeline/prompts/S##_blender.py`
2. **Set up Blender** via `blender_execute_blender_code` with:
   - Camera setup matching the scene's camera type
   - Layer stack from the composition table
   - Animation keyframes from the animation triggers
3. **Generate new assets** via:
   - `blender_generate_hyper3d_model` for 3D props/characters
   - `blender_download_polyhaven_asset` for HDRI/textures/models (CC0)
   - `blender_download_sketchfab_model` for specific models
4. **Render** via `render_all_scenes` or `render_scenes_mp4` (gated)

## Resolve Overlay Path

For text overlays ($984M, 82%, etc.):

1. Read `pipeline/scenes/resolve_overlays_all.json`
2. Use DaVinci Resolve MCP `timeline_item_fusion` to add Text+ nodes
3. Or use the existing TextStat template for stat callouts
4. Place at the timing_sec from the overlay spec

## Episode-2+ Reusability

The pipeline is episode-agnostic. For new episodes:

1. Create `episode_N_script.md` following the same format
2. Create `teded_scene_spec_epN.md` with frame-level breakdown
3. Create `audio_design_map.yaml` for the new episode
4. Update `SCENES` dict in `generate_visual_pipeline.py` with new scene definitions
5. Run: `python generate_visual_pipeline.py --episode N`

## Timing Reference

Frame ranges are cumulative from scene durations (`teded_scene_spec_epN.md` is
the authoritative source for per-scene durations; the audio map's section resets
are chapter anchors, not scene boundaries — only use durations for scene frames).

| Scene | Start Frame | End Frame | Duration | Chapter |
|-------|-------------|-----------|----------|---------|
| S01 | 0 | 1,200 | 50s | Dawn |
| S02 | 1,200 | 2,280 | 45s | Dawn |
| S03 | 2,280 | 3,360 | 45s | Daylight |
| S04 | 3,360 | 3,960 | 25s | Daylight |
| S05 | 3,960 | 5,040 | 45s | DarkData |
| S06 | 5,040 | 6,000 | 40s | DarkData |
| S07 | 6,000 | 7,200 | 50s | CoolTension |
| S08 | 7,200 | 8,040 | 35s | CoolTension |
| S09 | 8,040 | 9,720 | 70s | HopefulDusk |
| S10 | 9,720 | 10,080 | 15s | HopefulDusk |

**Total:** 10,080 frames (7:00 @ 24fps)
