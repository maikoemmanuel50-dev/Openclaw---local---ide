---
title: DaVinci Resolve Manual
category: Software Manuals
tags: davinci-resolve, edit, color, fairlight, fusion, deliver, mcp
source: docs/resolve_finish_workflow.md, resolve_spec.yaml, MCP tools
---

# DaVinci Resolve Manual (finishing + conform)

Resolve is the finishing system: relink plates, kinetic edit, grade, Fairlight
mix, deliver. External scripting is Studio-only — the Free edition reaches the
API via the in-app `resolve_bridge` (Workspace > Scripts), which the MCP server
uses automatically.

**MCP bridge: port 127.0.0.1:49632** (enabled via Workspace > Scripts >
resolve_bridge). Blender MCP: 127.0.0.1:9876.

## Project spec (`resolve_spec.yaml`)

- Timeline: 24 fps, 1920x1080. Two timelines: "Episode 01 - Assembly" and
  "Episode 01 - Kinetic".
- Kinetic track layout: V1 A-roll plates · V2 Yellow Ball (empty when waived) ·
  V3 BROLL_A (ASL 0.4–1.0s) · V4 BROLL_B · V5 TextStat.
- Scene boundary markers at frames 0, 1080, 2040, 3720, 5400, 6840, 8280.
- 5 chapter color LUTs: Dawn, Daylight, DarkData, CoolTension, HopefulDusk.
- Kinetic ASL ≈ 0.7s.

## Color page

- Correction before look: expose/contrast/white balance, read scopes, keep clean
  node order, then creative grading/LUT.
- Final look: Blender **AgX** plates + chapter soft-pop polish (Color page).
- `resolve_yellow_ball_markers.yaml`: 11 ball state markers S0–S10 on the
  timeline. With YB waived, V2 overlays stay **skipped** and markers stripped.

## Fairlight audio

- Track map: A1 VO (0 dB) · A2 Music (~-24 dB under VO) · A3 Ambient (~-28 dB) ·
  A4 Punctuation (~-18 dB) · A5 Stats (~-14 dB).
- Duck: A2 sidechain from A1, ~-12 dB, attack 15–30 ms, release 120–250 ms
  (see `docs/FAIRLIGHT_A2_SIDECHAIN.md`).
- Loudness → **-14 LUFS**, true peak ≤ -1 dBTP (check with loudness meters).

## Deliver page

- Verify against `docs/guides/02_production_standards/delivery_standards.md`.
- Prefer the advanced server's `deliverable_qc` and prepared delivery jobs.
- Never run a Resolve Deliver while Blender renders (one GPU job).

## Learning resources

- Official Blackmagic training (free, DR20/21): Edit, Color, Fairlight, Fusion,
  Deliver videos + downloadable PDF guides (Beginner's, Editor's, Colorist's,
  Fairlight Audio, VFX) at https://www.blackmagicdesign.com/products/davinciresolve/training
- DaVinci Resolve Club (hands-on, current-version tested): https://davinciresolveclub.com
- Editing-workflow video: "This Editing Workflow Will Save You HOURS in DaVinci
  Resolve 20" (youtu.be/i9O1fQtOb6M).
- Fast-growing studio pipeline details remain in
  `docs/guides/04_tutorials_and_reference/online_tutorial_library.md`.