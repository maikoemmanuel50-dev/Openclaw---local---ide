---
title: Blender 5.1 Manual
category: Software Manuals
tags: blender, eevee, cycles, rendering, optix, motion-graphics
source: docs/BLENDER_51_PHOTOREAL_STACK.md, docs/blender_51_efficiency_realism.md, docs/OBJECT_MOTION_LOCK.md + Blender 5.1 docs
---

# Blender 5.1 Manual (Silicon Savannah pipeline)

Blender is the scene/plate engine of this production. **Use Blender 5.1.2 only**
(`C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`). The `.blend`
file is 5.1-format — never open in Blender 4.4.

## Engine choice

- **Cycles** — physically-accurate path tracer. Use for photoreal plates,
  reflections, volumetrics, caustics. Promotion path: quality fix
  (`AFRICA_RENDER_ENGINE=CYCLES`) for the masters pass.
- **EEVEE** (Next, ray-traced) — real-time rasterizer. Excellent for motion
  graphics, stylized work, previz and fast iteration; then switch to Cycles for
  finals. Same shader nodes as Cycles, so lookdev ports cleanly.
- Iterate in EEVEE (seconds/frame), render finals in Cycles.

## Project render baseline (from `setup_cameras_and_render.py`)

- Resolution 1920x1080 @ 100%, **24 fps**, ~420s (7:00) across 10 scenes.
- Encode H.264 High, MPEG4. Masters promoted to PNG sequences (Cycles) in D5.

## HQ photoreal pass (`setup_hq_camera_lighting_render.py`)

- EEVEE raytracing: SCREEN method, quality 0.5, thickness 1.0, max roughness 0.75.
- TAA render 128 (hero 256), viewport 32; pixel filter 1.2.
- Denoise spatial+temporal+bilateral; shadows 4 rays/12 steps/pool 1024.
- Fast GI quality 0.5; bloom threshold 0.9, intensity 0.03, radius 4.0.
- View transform **AgX Medium-High Contrast**, display sRGB.

## Cycles quality targets

- Samples 256–512; noise threshold ~0.01; denoiser OIDN/OptiX with Albedo+Normal.
- `AFRICA_RENDER_ENGINE=CYCLES`, `AFRICA_MASTER_FRAMES=1`,
  `AFRICA_FORCE_RERENDER=1`, `AFRICA_DELIVERY_BITRATE=10M`.
- Pipeline request: 1080 first, 4K HOLD until PRE_4K_GATE clears.

## Per-scene camera defaults (24fps)

| Scene | Lens (mm) | f-stop |
|---|---|---|
| 01_ColdOpen | 35 | 5.6 |
| 02_Context2007 | 40 | 5.6 |
| 03_Beat1_Hubs | 40 | 5.0 |
| 04_Beat1_Phone | 50 | 4.0 |
| 05_Beat2_Money | 35 | 8.0 |
| 06_Beat2_Solar | 35 | 8.0 |
| 07_Beat3_Gap | 40 | 8.0 |
| 08_Beat3_SecondaryCity | 40 | 5.6 |
| 09_Closer | 35 | 5.6 |
| 10_EndCard | 50 | 8.0 |

Documentary-aesthetic DOF variants: 01→4.0, 02→5.0, 03→4.5, 04→3.5, 05→8.0,
06→5.6, 07→8.0, 08→4.0, 09→5.0, 10→8.0. DOF off for flat plates S02/S04/S10.

## Animation / motion rules (style bible)

- Ease-in/out 3–5 frames; easy 3–5f on all entrances/exits.
- Stat hold 36–48f min readable; camera drift 0.3–0.6% scale/frame.
- Icon stagger 12f (0.5s); pulse cycle 24f (1s).
- **Nothing moves without VO** — lock keyframes to `episode_01_vo.wav`.
- Motion locked natively: Geometry Nodes + Graph Editor (`OBJECT_MOTION_LOCK.md`).

## GPU / hardware

- RTX 4060 — OptiX acceleration in Cycles; CUDA/OptiX in Resolve.
- One GPU job at a time (Blender OR Resolve deliver). Never restart an
  in-progress render from frame 0 — resume or investigate.

## Learning resources

- Local: 16 Telegram Blender class videos → `docs/guides/04_tutorials_and_reference/telegram_blender_class_index.md`.
- Official manual: https://docs.blender.org/manual/en/5.1/ (EEVEE, Cycles pages).
- Rendering guides: superrendersfarm.com Blender Render Animation & Render
  Settings guides (2026) — samples, denoise, output, animation flicker.
- See `docs/guides/04_tutorials_and_reference/online_tutorial_library.md`.