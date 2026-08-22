# PRE-4K GATE — Official Remaining Steps (DO NOT BYPASS)

**Source of truth:** Active Cursor workspace creative direction (synced 2026-08-12).  
**Rule:** Do **not** start, resume, or deliver a **4K** batch until every gate below is ✅ or explicitly waived by the user in-chat.

**Blender binary (mandatory):**  
`C:\Program Files\Blender Foundation\Blender 5.1\blender.exe` (5.1.2)  
Never use Blender 4.4 for this project — the `.blend` is 5.1-format.

---

## Gate checklist (must complete before 4K)

| # | Step | Status | Owner |
|---|------|--------|-------|
| 1 | **VO timing lock** — `assets/audio/vo/episode_01_vo.wav` active (placeholder bytes locked 2026-08-13; swap final take later via `scripts/swap_vo_stem.py`) | ✅ WAIVED for pipeline — treat as locked stem | User waived; swap later |
| 2 | **HQ Blender re-render** — Cycles + OptiX masters, 2-pass **8–12 Mbps** delivery (supersedes in-flight EEVEE ~2 Mbps); see `docs/RENDER_QUALITY_FIX.md` | ⏳ S03 PNG resume (~29/1080) @ **64** samples; S01/S02 playable; Startup auto-resume armed | Agent + Blender 5.1 |
| 3 | **Refresh Resolve V1** — relink timeline to new MP4s (especially `10_EndCard`) | ⏳ S01/S02 in built_clips; full relink after 10/10 | Resolve |
| 4 | **V3/V4 kinetic cuts** — place ~36 graded stills on timeline (V2 ball track must not stay empty); Mixkit pack failed — use local kinetic assets | ✅ **84 placed**, 0 misses, open30 V3 0–720; YB waived → V2 empty OK | Resolve |
| 5 | **Yellow ball / YB-Body overlays** — markers exist; replace cube bodies with proper mannequin/YB-Body; composite morphs on V2 | ✅ WAIVED (`AFRICA_NO_YELLOW_BALL=1` / status) | User waiver |
| 6 | **Fairlight + grade** — final mix/grade on locked VO stem; re-run after any VO swap | ⏳ A1–A5 rebuilt; A2 duck+gap swell baked (`bake_a2_tension_release.py`); grade after picture lock | Resolve |
| 7 | **Rebuild FINAL** — re-export `Africa_S1_Silicon_Savannah_FINAL.mp4` after above | ⏳ | Scripts + Resolve |
| **1b** | **Real VO recording** — user WAV → `scripts/swap_vo_stem.py` → Fairlight re-run | ⏳ | **User** — see `docs/VO_INTAKE.md` |
| **9** | **Meshy S07 giraffe** — GLB → `assets/meshy/scenes/S07/` · hide `MOTION_Walker_S07` | ⏳ GLB pending | User + `setup_meshy_s07_giraffe.py` |
| **10** | **S01 Africa whip HQ bake** — alpha asset + motion (supersedes patched MP4) | ⏳ post-HQ re-render | `setup_fix_s01_africa_alpha.py` in merge chain |
| **11** | **Blender51 30s open sidecar** — CPU `s01_teded_open30_blender51.mp4` (720f) | ⏳ CPU render | `scripts/render_teded_open30_cpu.ps1` |
| 8 | **Then 4K** — only after #1–7 **and #1b, 9–11** (or user waiver): `render_scenes_4k.py` via **Blender 5.1** | 🚫 HOLD | — |

**Additional detail:** `docs/PRE_4K_ADDITIONAL_DELIVERABLES.md`

---

## Already animated in Blender (do not re-litigate)

| Sequence | What moves |
|----------|------------|
| Cameras (all 10) | Push-in, pan, parallax, map zoom-out, end-card drift |
| S05 chart | Geometry Nodes bars + $984M / 82% labels |
| S06 solar | Panel reveal / glare |
| S07 map | Zoom + 97% / city markers |
| TED-Ed overlays | Labels, hub cards, forecast text fades |
| S05→S06 | Bar→solar morph (spec’d) |

## Not finished as timeline layers (must uptake)

- Yellow ball rise / coin / orb / morph beats — markers only; overlay pack incomplete  
- YB-Body crowd / builder / founder morphs — not production quality  
- Ken Burns on new graded stills  
- Cavalry ball rig  
- Fern mannequin walk/breath  

**Docs to obey:**  
`docs/CURSOR_KINETIC_MISSION.md` · `docs/yellow_ball_throughline.md` · `docs/how_to_use_yellow_ball_in_video.md` · `docs/production_stack_checklist.md` · `docs/resolve_finish_workflow.md` · `docs/teded_style_bible.md` · `docs/teded_scene_spec_ep01.md` · `docs/FIDELITY_EXECUTION_GUIDE.md` (sharpness / codec path)

---

## Agent anti-bypass rules

1. If asked to “just render 4K” while this gate is open → **refuse**, summarize open rows, offer next creative task.  
2. Prefer **Resolve V1/V2/V3–V4** editorial + YB overlays over another low-quality ffmpeg Ken Burns master.  
3. Yellow ball is the **only hero**; YB-Body = faceless torso + ball head (no faces).  
4. VO timing: `episode_01_vo.wav` is the locked stem (may be placeholder bytes); swap with `scripts/swap_vo_stem.py` — do not block picture finish on a new recording.  
5. One heavy GPU job at a time (Blender **or** Resolve Deliver).  
6. All Blender CLI: **5.1 only**.

When gate clears, set `STATUS_PRE4K_GATE_CLEARED.txt` then run 4K with Blender 5.1.
