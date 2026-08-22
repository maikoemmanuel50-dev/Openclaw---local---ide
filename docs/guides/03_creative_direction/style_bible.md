---
title: Style Bible (TED-Ed Illustrated Documentary)
category: Creative Direction
tags: style, teded, kurzgesagt, narration-first, symbolism, typography, motion
source: docs/teded_style_bible.md, docs/fern_imperial_lemmino_hybrid.md
---

# Style Bible — TED-Ed Illustrated Documentary

This is the creative contract for Episode 1 and every future episode. **Style is
locked** (motion-graphics / illustrated-documentary), unless an explicit waiver
is recorded in `PRODUCTION_STATUS.md`.

## Design philosophy

- **Narration drives everything.** No motion without a script reason. Every
  visual answers "what is the narrator saying right now?"
- Symbolic over realistic — flat/2.5D illustration; one focal idea per frame,
  center-weighted composition; minimal clutter; diagram clarity.
- Honest narrative arc; hero = the yellow ball (`#FFD54F`); humanity = ball-head
  bodies (faceless torso + ball head). No faces, no competing mascots.

## Motion rules

- Ease-in/out 3–5 frames on all entrances/exits.
- Stat hold 36–48 frames (readable).
- Camera drift 0.3–0.6% scale/frame.
- Icon stagger 12 frames (0.5 s) between items · pulse cycle 24 frames (1 s) ·
  draw-on speed 2 frames/segment.
- Nothing moves without VO — lock keyframes to the VO stem timestamps.
- Kinetic ASL 0.4–1.0 s (0.7 avg).

## Transition vocabulary

| Transition | Frames |
|---|---|
| Cut | 0 |
| Slide wipe | 6–10 |
| Fade | 6–8 |
| Color hold | 0 |
| Morph | 12–18 |

Avoid fade-to-black (feels like a stop). 5 chapter color LUTs applied.

## Typography (1080p)

| Role | Font | Size | Weight |
|---|---|---|---|
| Headline | Inter | 72px | Bold |
| Stat / Number | Inter | 96px | Black |
| Label / Caption | Inter | 36px | Medium |
| Subtitle | Nunito Sans | 28px | Regular |
| End card | Inter | 120px | Black |

## Quality checklist (every episode)

- Every major stat on-screen synced to VO.
- ≥ 3 diagram/enumeration beats per episode.
- No 1s black fades; music continuous with ducking.
- SFX on all named entities; 5 chapter LUTs applied.
- All brand references stylized; end card holds 8 s.

## Reference tone

TED-Ed + Kurzgesagt (vector, morphing, parallax, readable fast cuts) with the
Fern / Imperial / Lemmino hybrid energy (`docs/fern_imperial_lemmino_hybrid.md`):
clean diagrams, confident pacing, information-forward narration.