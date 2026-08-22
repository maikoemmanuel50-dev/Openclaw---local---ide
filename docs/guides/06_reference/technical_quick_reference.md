---
title: Technical Quick Reference
category: Technical Reference
tags: cheat-sheet, numbers, quick-reference, delivery, audio, color, motion
source: consolidated from Africa S1 docs + guides
---

# Technical Quick Reference (cheat sheet)

One-page hard numbers for the whole pipeline. Canon: `delivery_standards.md`,
`audio_mix_standards.md`, `render_quality_standards.md`, `style_bible.md`.

## Video

- 1920×1080 · 24 fps exact · H.264 High · MP4 · closed GOP =
  half framerate · 8–12 Mbps (2-pass VBR) · yuv420p · Rec. 709.
- Near-lossless: `-crf 18 -preset slow -pix_fmt yuv420p`.
- 4K (gate-cleared only): 3840×2160, 35–45 Mbps. Archive: DNxHR HQX.

## Audio

- 48 kHz · 24-bit · AAC-LC 320–384 kbps stereo · −14 LUFS integrated ·
  true peak ≤ −1 dBTP.
- A1 VO 0 dB · A2 Music −24 dB · A3 Ambient −28 dB · A4 Punch −18 dB ·
  A5 Stats −14 dB. Duck −12 dB (att 15–30 ms, rel 120–250 ms).

## Color

- 5 chapter LUTs: Dawn, Daylight, DarkData, CoolTension, HopefulDusk.
- Yellow ball #FFD54F (highlight white, shadow #F9A825).
- AgX Medium-High in Blender; soft-pop per chapter in Resolve.
- Title-safe center 80% · action-safe 90% · caption/watermark exclusion zones 15%.

## Motion

- Ease 3–5f · stat hold 36–48f · drift 0.3–0.6%/frame · icon stagger 12f ·
  pulse 24f · draw-on 2f/segment · kinetic ASL 0.7 s.
- Transitions: cut 0 · slide 6–10f · fade 6–8f · morph 12–18f.

## Render

- Blender 5.1.2 only · one GPU job at a time · cycles 256–512 samples ·
  OIDN/OptiX denoise · threshold 0.01 · EEVEE TAA 128 (hero 256).

## Resolve

- 24fps timeline · V1 plates · V2 YB (waived → empty) · V3/V4 B-roll ·
  V5 TextStat · A1–A5 audio · markers at 0/1080/2040/3720/5400/6840/8280.