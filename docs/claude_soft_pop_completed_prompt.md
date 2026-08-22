# Claude Soft-Pop Prompt — Completed for AFRICA Season 1

**Source chat (Claude Desktop):** *Describing fast-paced video editing*  
**Captured:** 2026-08-12 (window OCR + IndexedDB fragments + Claude palette widget)  
**Project lock:** Silicon Savannah · yellow ball hero · Cursor IDE as command center · Blender / Resolve / Cavalry

This file turns the open Claude dialogue into a **production-ready prompt** plus **nuggets** and **concrete implementations** already mapped to this repo.

---

## 1. Recovered Claude dialogue (cleaned)

### User (core ask)

> If I already have yellow as a colour in my composition, but [want it to feel] soft but pop — like *Blue Eye Samurai*, *Frieren*, or *Kirikou* — give me an idea to execute this art style and colour scheme through an MCP [Blender].

Also in the same chat thread:

> How do we describe a video that has a lot of frames such that you’re not looking at a particular thing for too long?

### Claude memory summary (channel)

- Reviving a YouTube channel (motion-graphics / short documentary)
- Season focus: **Africa**; Episode 1: **Kenya startup scene (Silicon Savannah)**
- Want **soft yet vibrant** color (Blue Eye Samurai / Frieren / Kirikou DNA)
- Yellow already in the composition — must **pop without fighting** the soft base
- Prefer **Blender via MCP** (+ other AI tools) for paced production
- Prefer **recorded VO** over AI voice; motion-graphics / illustration over heavy character acting

### Claude soft-pop palette widget (`soft_pop_*`)

| Role | Hex | Notes |
|------|-----|-------|
| **Dominant (mustard yellow)** | `#D9A441` | Soft pop yellow (Claude proposal) |
| **Secondary (dusty indigo)** | `#2E3A50` | Deep field / night plates |
| **Accent** | `#C1552E` | Terracotta punch |
| **Accent · alt** | `#7D2E3B` | Plum / blood-indigo accent |
| **Light neutral** | `#F1E4C8` | Warm cream paper |
| **Dark charcoal** | `#262019` | Soft black (not pure #000) |

Claude loading copy: *“Mixing mustard & dusty indigo”* · *“Test pops of terracotta and plum”*.

---

## 2. Completed master prompt (paste into Cursor / Blender MCP / Cavalry)

Use this as the single art-direction brief:

```text
PROJECT: AFRICA Season 1 — Episode 01 “Silicon Savannah” (~7 min, 24fps, 10 scenes).
HERO: One yellow ball only (#FFD54F production gold). When humanity is needed, morph into
faceless charcoal torsos with the yellow ball as the head (YB-Body). No faces. No second mascot.

ART STYLE — “SOFT POP AFRICA” (Blue Eye Samurai × Frieren × Kirikou × TED-Ed):
- Soft yet vibrant: matte fields, watercolor-soft edges on backgrounds, ink-clean silhouettes on hero.
- Yellow must POP: one hard gold accent in an otherwise restrained indigo/charcoal world
  (Blue Eye Samurai: deep indigo/black punctuated by gold/red; Frieren: soft pastels/blues;
   Kirikou: warm earth, simple graphic shapes, African storybook clarity).
- Soft base palette (fields): dusty indigo #2E3A50, warm cream #F1E4C8, soft charcoal #262019.
- Pop accents (sparingly): hero ball #FFD54F (or mustard #D9A441 for softer plates),
  terracotta #C1552E, plum #7D2E3B, growth neon #00E676 only in DarkData chapter.
- Never purple-on-white generic AI look. Never flat single-color full frames without atmosphere.
- Symbolic 2.5D / motion-graphics, not photoreal. Narration drives every motion.

KINETIC EDIT LANGUAGE (answer to “lots of frames / never linger”):
- Call it: kinetic B-roll montage / high ASL density edit.
- Target ASL 0.4–1.0s on B-roll; protect stats with 36–60f holds; ball transforms 24–48f.
- Resolve tracks: V1 plates, V2 yellow ball / YB-Body, V3–V4 kinetic B-roll, V5 titles.
- Hard cuts + ball-carry between chapters; smash only on stats.

MCP / PIPELINE CONSTRAINTS:
- Command center: Cursor IDE (not other IDEs).
- Blender MCP for scene plates, overlays, synthetic B-roll cameras.
- DaVinci Resolve for editorial / Fairlight; Cavalry preferred for ball morph + crowd stagger.
- One heavy GPU job at a time (RTX 4060 8GB). Leave Blender closed during Resolve ball work.

OUTPUT THIS TURN:
1) Confirm palette chapter mapping (Dawn→HopefulDusk) vs soft-pop hexes.
2) List scene-by-scene where yellow POP vs soft field dominates.
3) Emit concrete Blender/Cavalry/Resolve steps for one hero beat (S01 crowd → ball).
```

---

## 3. Nuggets (actionable)

1. **Rename the look:** “Soft Pop Africa” — soft fields, one popping yellow hero. Stops “more saturation everywhere.”
2. **Two yellows, one hero:** Production hero stays `#FFD54F`. Use Claude mustard `#D9A441` only on *background* sun washes / paper textures so the ball still wins contrast.
3. **Indigo is the stage:** `#2E3A50` / `#1A1A2E` carry DarkData + night — gold only on the ball and key labels.
4. **Terracotta / plum = rare punctuation** (S02 coin flash, S08 tension, end-card underlines) — Blue Eye Samurai “red/gold puncture,” not wallpaper.
5. **Kirikou rule:** simple graphic humans = YB-Body (ball head + slab torso). Storybook clarity, zero facial detail.
6. **Frieren rule:** soft edge light, gentle bloom on backgrounds; keep hero edges crisp so yellow reads.
7. **Name the edit style:** “kinetic B-roll montage” / “high cut-density explainer” — not “fast random cuts.”
8. **Hold budget:** only stats + ball morphs may linger; everything else is flash coverage under VO.
9. **MCP instruction pattern:** “soft field materials + emissive ball + limited accent lights” beats vague “make it anime.”
10. **Channel cadence:** 2–3 shorts/docs per week → reuse soft-pop LUT + YB-Body kit; don’t reinvent palette each episode.

---

## 4. Implementations in this repo (already / next)

| Nugget | Where it lives | Status |
|--------|----------------|--------|
| Yellow ball hero + YB-Body | `docs/yellow_ball_throughline.md`, `assets/yellow_ball/` | Done (SVG masters) |
| How to place on timeline | `docs/how_to_use_yellow_ball_in_video.md` | Done |
| TED-Ed chapter palettes | `docs/teded_style_bible.md` | Done — merge soft-pop hexes below |
| Kinetic / “don’t linger” edit | `docs/kinetic_broll_edit.md`, `docs/CURSOR_KINETIC_MISSION.md` | Done |
| Soft-pop Claude palette | This doc + Claude widget `#D9A441…` | Captured |
| Blender text overlays | `setup_teded_elements.py` | Ran (blend saved) |
| Audio beds / SFX | `assets/audio/` | Done (placeholder VO) |
| Resolve V2 markers / tracks | `resolve_spec.yaml` · Episode 01 Kinetic | **Next** — MCP add_track previously timed out |
| PNG export of YB-Body | `assets/yellow_ball/export/` | **Next** |
| Overnight kinetic re-render | `render_kinetic_broll.py` | Pending GPU-free window |

### Soft-pop → existing chapter bridge

| Chapter | Keep from style bible | Soft-pop inject |
|---------|----------------------|-----------------|
| Dawn S01–S02 | `#E8845C`, warm yellow | Cream paper `#F1E4C8`; ball `#FFD54F` pops |
| Daylight S03–S04 | greens / white | Dusty indigo shadows `#2E3A50` under soft light |
| DarkData S05–S06 | charcoal + neon green | Mustard only on orb rim; no cream wash |
| CoolTension S07–S08 | slate + neon orange | Plum `#7D2E3B` / terracotta `#C1552E` punctuation |
| HopefulDusk S09–S10 | deep blue + gold | Indigo field + beacon ball; cream title cards |

---

## 5. One-beat execution recipe (S01 — soft pop + kinetic)

1. **V1:** Dawn plate (warm cream/indigo gradient, soft edges).
2. **V2:** Sun-seed ball `#FFD54F` rises 24–36f → morph 12–18f into **YB-Body crowd**.
3. **V3:** 6–8 kinetic flashes (matatu / pocket / street) @ 8–18f each under VO.
4. **Color:** Field ≤60% luminance; ball peak ≥ the brightest non-specular object.
5. **SFX:** soft whoosh on morph; hard tick only on first crowd bob.
6. **Do not** put faces, second mascots, or purple UI chrome in frame.

---

## 6. Paste-ready Blender MCP micro-prompt

```text
In the active Silicon Savannah scene, keep world/background materials matte soft-pop
(dusty indigo #2E3A50, cream #F1E4C8, charcoal #262019). Hero object is ONLY the yellow
ball (#FFD54F, slight emission 0.2–0.4). No character faces. If a human beat is required,
instance YB-Body (faceless torso + ball head). Limit accent lights to terracotta/plum.
Render ball on a separate view layer for Resolve V2. Prefer EEVEE, 24fps, 1920x1080.
```

---

## 7. Capture artifacts (local)

- `docs/_claude_window_capture.png` / `_claude_window_capture2.png`
- `docs/_claude_ocr.txt`
- `docs/_claude_blob_copy/` (IndexedDB snapshot; binary — not human-readable source of truth)

If Claude chat updates, re-OCR the window or paste the reply here to extend §1.
