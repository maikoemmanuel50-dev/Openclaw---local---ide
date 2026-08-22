# Pre-4K additional deliverables (mandatory before 4K)

These sit **after** core gate rows #2–7 in `docs/PRE_4K_GATE.md` and **before** row #8 (4K).

| ID | Deliverable | Status | Action |
|----|-------------|--------|--------|
| **A** | **Real VO** — user recording on A1 | ⏳ Pending | Send WAV → `python scripts/swap_vo_stem.py <path>` → Fairlight re-run. See `docs/VO_INTAKE.md`. |
| **B** | **Meshy S07 giraffe** — Free-web GLB in scene | ⏳ Pending GLB | Drop `assets/meshy/scenes/S07/s07_giraffe.glb` → run `setup_meshy_s07_giraffe.py` (hides `MOTION_Walker_S07`). Wired in `merge_motion_after_hq.ps1`. |
| **C** | **S01 Africa whip** — alpha + motion HQ bake | ⏳ On re-render | Patched MP4 is interim only. `setup_fix_s01_africa_alpha.py` + object motion merge supersede on post-HQ S01 re-render. |
| **D** | **Blender51 30s open sidecar** — CPU Cycles plate | ⏳ Rendering | `blend/africa_s1_teded_open30.blend` → `renders/paced_overlays/s01_teded_open30_blender51.mp4` (720f @ 24fps). Monitor `renders/quality/teded_open30_render_log.txt`. Kinetic open already verified: `s01_teded_open_30s.mp4`. |

## Verification (definition of done)

| ID | Verify |
|----|--------|
| A | ffprobe 48 kHz · Fairlight −14 LUFS · A1 = user WAV |
| B | GLB in S07 · walker hidden · visible in motion review / HQ S07 plate |
| C | S01 f720–750 Africa title alpha whip, no black rectangle (ffprobe + spot-check) |
| D | open30_blender51: 1920×1080 · 720 frames · 30.0 s · plays |

## Automation

- **Post-HQ:** `merge_motion_after_hq.ps1` runs motion + S01 alpha + Meshy giraffe (if GLB present) before motion re-render.
- **Post-assemble:** `finish_after_hq.ps1` — Resolve + Fairlight on current VO stem.
- **After real VO:** user runs `swap_vo_stem.py` again → rebuild FINAL.
