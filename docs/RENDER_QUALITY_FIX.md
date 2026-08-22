# Render quality fix — Cycles + delivery encode (post-batch)

**Problem:** Raw `video_clips/*.mp4` from the in-flight EEVEE batch read soft (~2 Mbps, single V1 plate).  
**Fix:** Cycles + OptiX masters → 2-pass H.264 @ **10 Mbps** (8–12 range per `docs/DELIVERY_STANDARDS.md`).

## Environment (set before `render_scenes_mp4.py`)

| Variable | Value | Effect |
|----------|-------|--------|
| `AFRICA_RENDER_ENGINE` | `CYCLES` | GPU Cycles + OptiX/OIDN from arch lock |
| `AFRICA_MASTER_FRAMES` | `1` | PNG masters in `renders/video_clips/masters/<scene>/` |
| `AFRICA_FORCE_RERENDER` | `1` | Replace EEVEE clips |
| `AFRICA_DELIVERY_BITRATE` | `10M` | 2-pass ffmpeg target |

## Pipeline order (automated)

1. **Current EEVEE batch** — S03–S10 finish without restart (legacy script loaded at launch).
2. **`merge_motion_after_hq.ps1`** (after 10/10):
   - `setup_tighten_dof_parallax.py` — f/8+ parallax; DOF off S02/S04 flat plates
   - Motion merge + S01 alpha + optional Meshy giraffe
   - **Cycles re-render all 10** + ffmpeg delivery
   - **`resolve_s02_kinetic_preview.py`** — V1 + S02 kinetic on Resolve timeline
3. **`finish_after_hq.ps1`** — full episode assemble + V3/V4 + Fairlight

## Manual early S02 preview (GPU free)

```powershell
powershell -File scripts/post_batch_cycles_fix.ps1 -Phase s02
```

Waits for no `blender -b`, re-renders S02 Cycles, builds Resolve preview timeline.

## Interim Resolve preview (EEVEE S02, no GPU)

While batch runs:

```powershell
python scripts/resolve_s02_kinetic_preview.py
```

Open timeline **S02 Kinetic Preview** in Resolve → Deliver to `renders/quality/s02_kinetic_preview.mp4`.

## DOF

| Scene | Change |
|-------|--------|
| S02, S04, S10 | DOF **off** (flat illustrated plates) |
| S01, S03, S06, S08 | f/8 minimum |
| Others | f/6.3 minimum |

Report: `renders/quality/dof_tighten_report.json`
