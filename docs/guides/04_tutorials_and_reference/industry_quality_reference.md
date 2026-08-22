---
title: Industry Quality Reference
category: Tutorials & References
tags: industry, standards, quality, benchmarks, 2026, quantitative
source: web research (2026) + Africa S1 delivery standards
---

# Industry Quality Reference (2026 benchmarks)

Quantitative floor/best-practice calibrations to keep this project at or above
industry quality bars. Formal delivery targets remain in `delivery_standards.md`.

## Video

- **Resolution/fps:** 1080p24 min for educational/web; 4K24 for flagship uploads.
  Never upscale below-native to fake it (project rule).
- **Encode:** H.264 High, closed GOP at half framerate; 8–12 Mbps 1080p VBR
  two-pass; 35–45 Mbps 4K — matches YouTube's recommended range (project
  standard).
- **Mastering:** keep uncompressed/high-bitrate master (DNxHR HQX preferred on
  Windows) before the compressed upload copy.

## Audio

- Broadcast/web loudness convention: **−14 LUFS** integrated, true peak
  ≤ −1 dBTP (matches streaming normalization behavior). −16 LUFS acceptable
  inside the pack for quieter mixes. 48 kHz / 24-bit project.

## Motion / editorial

- Readability holds (stat 36–48f) and narration-locked keyframes are the
  standard practice of top explainer studios (TED-Ed/Kurzgesagt style).
- Engagement research: documentary-style animation ≈ +23% engagement vs stock
  + basic text; 5–10 min micro-docs dominate faceless educational formats.
- Accessibility as standard: high contrast, clear captions, audio
  descriptions — treat as design principle, not afterthought.

## Art direction (top studios)

- Cohesive design system + unified visual identity = brand recognition
  (Kurzgesagt). Consistent palette per chapter/video; kinetic type synced to
  VO; morphing transitions; no 1s black fades.
- One focal idea per frame; clean node order in grade (correction → look).

## Tooling (2026)

- Free tools are production-grade: Blender (full 3D), DaVinci Resolve
  (edit/grade/Fairlight/Fusion/Deliver). Paid adds speed (CUDA/OptiX GPUs,
  licensed Resolve Studio extras), not correctness.

## Where to verify

- ffprobe on every deliverable (see `delivery_standards.md` definition of done).
- Resolve quality analyses live in the analysis dashboard / MCP (`media_analysis`).
- Update this card when newer benchmarks are found in research or Telegram
  examples contradict an entry (and fold into `PRODUCTION_STATUS.md`).