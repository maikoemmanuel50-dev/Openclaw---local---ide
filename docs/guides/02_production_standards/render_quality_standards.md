---
title: Render & Quality Standards
category: Production Standards
tags: render, cycles, eevee, samples, denoise, gpu, quality, fidelity
source: docs/RENDER_QUALITY_FIX.md, docs/nvidia_gpu_workflow.md, setup_hq_camera_lighting_render.py
---

# Render & Quality Standards

Drives Blender output quality to delivery spec. The point of every rule: plates
must survive the finish pipeline without softening or generational loss.

## Engine & promotion policy

- **Blender 5.1.2 only.** Masters now render **Cycles** (quality fix path): set
  `AFRICA_RENDER_ENGINE=CYCLES`, `AFRICA_MASTER_FRAMES=1`,
  `AFRICA_FORCE_RERENDER=1`, `AFRICA_DELIVERY_BITRATE=10M`.
- Iterate in EEVEE; final in Cycles. No EEVEE-fallback on masters.

## Cycles numbers

- Max samples 256–512 · noise threshold ~0.01 · denoiser OIDN/OptiX with
  Albedo+Normal · pixel filter Blackman-Harris (crisp CGI).
- DOF tightening: S02/S04/S10 DOF off (flat plates); S01/S03/S06/S08 f/8 min;
  others f/6.3 min (documentary-lock values in `blender_5.1_manual.md`).

## HQ EEVEE preview defaults (for lookdev)

- TAA render 128 (hero 256) · viewport 32 · pixel filter 1.2.
- Raytracing SCREEN quality 0.5 · shadows 4 rays/12 steps/pool 1024.
- Denoise spatial+temporal+bilateral · bloom 0.9/0.03/4.0.
- View transform AgX Medium-High, display sRGB.

## Path/loss guards (fidelity)

- PNG/EXR sequences preferred for intermediates; avoid stacking H.264.
- Anti-pattern: Blender H.264 → ffmpeg Ken Burns → Resolve H.264 → YouTube
  H.264. Sharp path: PNG plates → Resolve V1 relink → deliver DNxHR HQX master
  + H.264 upload copy.
- Transparent plates (YB/V2 overlays) must be Film Transparent + RGBA PNG/EXR.

## GPU (RTX 4060)

- OptiX for Cycles; CUDA/OptiX for Resolve.
- One heavy GPU job at a time (Blender OR Resolve). Never restart in-progress
  renders from frame 0 — resume or investigate frames.
- Watch thermals/power: HP battery care + thermal rules in
  `docs/nvidia_gpu_workflow.md`.

## QC gate

Before "done": frame count = target · file plays · verify with qwen2.5vl
via `inspect_image` for visual artifacts · stamp into `PRODUCTION_STATUS.md`.