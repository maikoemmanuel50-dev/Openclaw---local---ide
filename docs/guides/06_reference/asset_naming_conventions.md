---
title: Asset Naming & Conventions
category: Technical Reference
tags: naming, conventions, assets, paths, structure
source: style bible + project structure
---

# Asset Naming & Conventions

Keep every agent and file discoverable. Convention applies across episodes.

## Scenes & plates

- Scenes: `NN_SceneName` (01_ColdOpen, 02_Context2007, … 10_EndCard).
- Master plates: `renders/video_clips/masters/<SceneName>/frame_XXXX.png`
  (e.g. `03_Beat1_Hubs/frame_0398.png`). HQ plates go to `renders/hq_plates/`.
- Rendered clips: `<NN>_<SceneName>.mp4`.

## Audio

- VO stem: `assets/audio/vo/episode_01_vo.wav` (locks timing).
- Fairlight stems: A1 VO · A2 Music · A3 Ambient · A4 Punctuation · A5 Stats.
- Music/SFX in `assets/audio/`.

## Assets

- SVGs/icons in `assets/`; infographic sources per `docs/INFOGRAPHIC_SOURCES.md`.
- Canva PNG exports → `assets/canva/kinetic/canva_exports/`.
- Textures/HDRI/audio in `assets/` of the workspace root.

## Docs & status

- Live state: `PRODUCTION_STATUS.md` (authoritative). One status file per axis.
- Guides: `docs/guides/<NN>_<category>/...` — each file has YAML front matter
  (title/category/tags/source) so the IDE auto-indexes it.
- Video index: `docs/video_library/tutorial_index.json`.

## Resolve

- Timelines: "Episode 01 - Assembly", "Episode 01 - Kinetic".
- Tracks: V1 plates · V2 YB · V3/V4 b-roll · V5 TextStat; A1–A5 audio.

## Rules

- No spaces in new file names for render-critical artifacts (use `_` or `-`).
- Never copy the live `renders` tree into the workspace — always read from
  `AFRICA_RENDER_ROOT`.