---
title: Fidelity Pipeline
category: Production Standards
tags: pipelines, png, exr, h264, dnshr, relink, generational-loss
source: docs/FIDELITY_EXECUTION_GUIDE.md, docs/resolve_finish_workflow.md
---

# Fidelity Pipeline (sharper end-to-end)

The delivery looks as good as the weakest link. Keep every stage lossless until
the final encode.

## The sharp path

1. Blender renders **PNG/EXR sequences** to `renders/hq_plates/` (AgX, sRGB).
2. Resolve **V1 relink** to those plates (not H.264 seconds).
3. Kinetic V3/V4, TextStat V5, Fairlight — all in Resolve.
4. Deliver **DNxHR HQX master** (archive) + separate H.264 upload copy.

## Generational-loss anti-pattern

Blender H.264 → ffmpeg Ken Burns → Resolve H.264 → YouTube H.264 = triple loss.
Each H.264 re-encode softens and bandings images. Stack the pipeline instead.

## Related rules

- Every major stat on-screen is synced to VO; no 1s black fades; end card holds 8s.
- Confirm fps/size before assembly (`DELIVERY_STANDARDS.md`).
- The watcher: `wait_hq_assemble.ps1` assembles when 10/10 scenes are complete
  (`finish_after_hq`). Read progress from `AFRICA_RENDER_ROOT` — never copy the
  live `renders` tree into this workspace.