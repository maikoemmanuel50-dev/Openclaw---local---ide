# AFRICA Season 1 — TED-Ed Style Bible

**Reference:** [TED-Ed high-speed rail explainer](https://youtu.be/2A1IEBFt6Xg)  
**Series:** AFRICA — illustrated documentary motion-graphics  
**Episode 1 pilot:** Silicon Savannah (Nairobi / Kenya startup ecosystem)  
**Target runtime:** ~7 minutes @ 24fps (10,080 frames)

This document defines the visual, motion, transition, and audio language for Episode 1 and all future Season 1 episodes (Lagos, Kigali, Accra).

---

## 1. Design Philosophy

TED-Ed explainer style applied to AFRICA:

- **Narration drives everything.** No motion, label, or SFX without a script reason.
- **Symbolic over realistic.** Flat/2.5D illustration, not photorealism.
- **Minimal clutter.** One focal idea per frame; center-weighted composition.
- **Diagram clarity.** Complex ideas become labeled sequences, comparisons, or counters.
- **Honest narrative arc.** Complication before optimism — data before forecast.
- **Yellow ball as hero (Ep 1).** One transforming sphere carries the story.
- **Humanity = ball-head bodies.** Faceless torsos with the yellow ball as head (no facial features). Crowds use the same format — many yellow heads, faceless bodies. Never realistic humans or a second mascot.

---

## 2. Color Chapters

Each episode uses five palette chapters. Colors repeat within a chapter and shift at major narrative beats.

| Chapter | Scenes | Primary Colors | Mood | LUT Name |
|---------|--------|----------------|------|----------|
| **Dawn** | S01–S02 | `#E8845C` orange, `#7B6BA8` purple, `#F5D5A0` warm yellow | Origin, warmth, nostalgia | `LUT_Dawn.cube` |
| **Daylight** | S03–S04 | `#FFFFFF` white, `#4CAF50` green, `#E8F5E9` light green | Energy, builders, optimism | `LUT_Daylight.cube` |
| **DarkData** | S05–S06 | `#1A1A2E` charcoal, `#00E676` neon green, `#16213E` navy | Data, scale, contrast | `LUT_DarkData.cube` |
| **CoolTension** | S07–S08 | `#37474F` slate, `#FF6B35` accent neon, `#78909C` muted gray | Gap, inequality, quiet | `LUT_CoolTension.cube` |
| **HopefulDusk** | S09–S10 | `#1A237E` deep blue, `#FFD54F` gold, `#263238` charcoal | Global arrival, forecast | `LUT_HopefulDusk.cube` |

**Rule:** Background color continuity across a scene pair signals "same idea continues." A palette shift signals a new narrative chapter.

---

## 3. Typography

| Role | Font | Size (1080p) | Weight | Color | Stroke |
|------|------|--------------|--------|-------|--------|
| Headline | Inter | 72px | Bold (700) | `#FFFFFF` | 2px `#1A1A2E` |
| Stat / Number | Inter | 96px | Black (900) | `#00E676` or chapter accent | 3px `#1A1A2E` |
| Label / Caption | Inter | 36px | Medium (500) | `#FFFFFF` | 1px `#1A1A2E` |
| Subtitle | Nunito Sans | 28px | Regular (400) | `#B0BEC5` | none |
| End card | Inter | 120px | Black (900) | `#FFD54F` | none |

**Animation preset (TextStat):**
- Enter: slide up 24px + fade 0→1 over 8 frames (0.33s @ 24fps)
- Hold: 36–48 frames (1.5–2s) on stats
- Exit: fade 1→0 over 6 frames
- Easing: ease-out cubic (Blender: BEzier, Resolve Fusion: EaseOut)

**Placement:** Stats centered or lower-third; labels top-left or beside diagram elements. Never cover the focal illustration.

---

## 4. Motion Rules

| Rule | Value | Notes |
|------|-------|-------|
| Ease-in/out | 3–5 frames | All element entrances and exits |
| Stat hold | 36–48 frames | Minimum readable time for numbers |
| Camera drift speed | 0.3–0.6% scale/frame | Existing presets unchanged |
| Icon stagger delay | 12 frames (0.5s) | Between items in enumeration sequences |
| Pulse cycle | 24 frames (1s) | Map glow, highlight accents |
| Draw-on speed | 2 frames/segment | Whiteboard lines, diagram connectors |
| Nothing moves without VO | — | Lock all keyframes to VO word timestamps post-record |

**Element animation priority over camera:** Labels, icons, and diagram steps animate first; camera supports but does not carry the scene alone.

### Dynamic & vibrant (Ep 1)
Full playbook: [`docs/dynamic_vibrant_tricks.md`](dynamic_vibrant_tricks.md)

Quick rules:
- Something meaningful changes every **1.5–3s** (ball, label, camera, or accent)
- Energy comes from **contrast** (quiet S07–08 → explosive S09), not constant noise
- Squash/stretch + pulse on the yellow ball; crash-zoom only on stats
- Cut on ball impacts; J/L-cuts at chapter boundaries
- Audio hits within ±2 frames of picture cuts
- Micro-motion on plates (paths, shimmer, flicker) so nothing freezes >2s
- Vibrancy via chapter palette snaps + ball gold — not rainbow clutter

---

## 5. Transition Vocabulary

| Type | Duration | When to Use | Implementation |
|------|----------|-------------|----------------|
| `cut` | 0 frames | Chapter boundaries, VO sentence ends | Resolve edit point |
| `slide_wipe` | 6–10 frames (0.25–0.4s) | Within-chapter scene changes | FFmpeg `wipeleft` / Resolve wipe |
| `fade` | 6–8 frames | Soft emotional shifts | FFmpeg `fade` xfade |
| `color_hold` | 0 frames | Same chapter, continuous idea | Hard cut, matching bg color |
| `morph` | 12–18 frames | Concept A becomes concept B (chart→solar) | Blender shape key or Resolve Fusion |
| `fadeblack` | **Avoid** | Legacy only — replaced by cut/slide | Do not use between chapters |

**Chapter transition map (Episode 1):**

| From → To | Transition |
|-----------|------------|
| S01 → S02 | `cut` (on "Silicon Savannah") |
| S02 → S03 | `slide_wipe` right (on "blueprint") |
| S03 → S04 | `color_hold` cut (same Daylight chapter) |
| S04 → S05 | `cut` (chapter change to DarkData) |
| S05 → S06 | `morph` (chart bar → solar panel) |
| S06 → S07 | `cut` (chapter change to CoolTension) |
| S07 → S08 | `fade` 8 frames (map → street) |
| S08 → S09 | `cut` (chapter change to HopefulDusk) |
| S09 → S10 | `fade` 12 frames (skyline → end card) |

---

## 6. Audio Rules

| Layer | Level (relative to VO at 0dB) | Notes |
|-------|-------------------------------|-------|
| Voiceover | 0 dBFS (reference) | Always the loudest element |
| Music bed | -22 dBFS under VO | Swell to -10 dBFS in transitions |
| Ambient SFX | -24 dBFS | Continuous beds (traffic, chatter) |
| Punctuation SFX | -18 dBFS | One-shots on keywords (horn, chime, riser) |
| Stat impact SFX | -14 dBFS | Brief accent on $984M, 82%, 97% |

**Ducking automation:**
- Attack: 100ms when VO starts
- Release: 400ms when VO pauses
- Pre-reveal dip: music drops -6dB for 0.5s before big stat reveals (S07 97%)

**Music chapter beds:** One track per color chapter (5 total). Crossfade 2s between chapters at scene boundaries.

**SFX on words:** Every named entity, number, and action verb gets a subtle punctuation sound. See `docs/audio_design_map.yaml`.

---

## 7. Composition Templates

### 7.1 Hook (S01 pattern)
- Wide establishing shot + foreground silhouettes
- Push-in camera
- Abstract overlay appears mid-scene (transaction paths)
- Location label fades in

### 7.2 Historical Flashback + Diagram (S02 pattern)
- Retro palette shift
- 3-icon horizontal flow diagram
- Year label top-left
- Pan camera L→R

### 7.3 Enumeration (S03 pattern — mirrors TED-Ed "three factors")
- 3 labeled cards stagger in left-to-right
- Each card: icon + title + year
- Micro-motion on environment (screens flicker, lines draw)

### 7.4 Data Viz (S05 pattern)
- Dark background, neon accent bars
- Bars grow on VO sector names
- Counter animates to final stat
- Percentage callout glows on emphasis word

### 7.5 Map Reveal (S07 pattern — signature moment)
- Tight zoom on glowing point
- Slow zoom-out reveals context
- Stat slams center-screen
- Regional markers stay dim

### 7.6 Closer (S09 pattern)
- Palette warms to dusk
- Sequential icon fade-in (stylized, non-trademark)
- Music swell + percussion layer
- Forecast text on final line

---

## 8. Asset Naming Conventions

```
assets/
├── canva/          # Illustrated scene backgrounds (existing)
├── diagrams/       # SVG flow diagrams, card layouts, overlays
├── icons/          # Reusable icon set (phone, solar, map pin, etc.)
├── audio/
│   ├── music/      # ch01_dawn.wav … ch05_hopeful.wav
│   ├── sfx/        # Per-cue sound effects
│   └── vo/         # Narration track(s)
└── hdri/           # World lighting (existing)

templates/
├── blender/        # Reusable .blend rigs
└── resolve/        # Fusion macros, DRB presets, Fairlight templates
```

**File naming:** `{scene}_{element}_{variant}.{ext}` — e.g. `s2_mpesa_flow.svg`, `s5_chart_labels.png`

---

## 9. Reusable Templates (Series)

Built in Episode 1, reused in Episodes 2–5:

| Template | Path | Use |
|----------|------|-----|
| TextStat | `templates/resolve/TextStat.drfx` | Animated stat callout ($984M, 82%, 97%) |
| DiagramEnumerate | `templates/blender/DiagramEnumerate.blend` | 3-card stagger rig |
| DataVizBarChart | `templates/blender/DataVizBarChart.blend` | Parameterized bar chart |
| FlowDiagram | `templates/blender/FlowDiagram.blend` | 3-step horizontal flow |
| MapReveal | `templates/blender/MapReveal.blend` | Zoom-out + stat slam |
| ChapterLUT | `templates/resolve/luts/` | 5 chapter color grades |
| FairlightMix | `templates/resolve/FairlightMix.dra` | VO ducking + SFX bus layout |

---

## 10. Episode Adaptation Checklist

When starting a new city episode (Lagos, Kigali, Accra):

1. Copy `docs/teded_scene_spec_ep01.md` → `docs/teded_scene_spec_epXX.md`
2. Replace city-specific assets (skyline, map, local diagram content)
3. Update data viz numbers and sector labels
4. Record new VO; lock all keyframes to new audio
5. Swap chapter music beds if mood requires (keep 5-chapter structure)
6. Reuse all templates from `templates/`

---

## 11. Quality Checklist (Pre-Deliver)

- [ ] Every major stat appears as animated on-screen text synced to VO
- [ ] At least 3 diagram/enumeration beats per episode
- [ ] No 1s black fades between chapters
- [ ] Music bed continuous; ducks under VO
- [ ] SFX on all named entities and key numbers
- [ ] 5 chapter LUTs applied consistently
- [ ] All brand references stylized / non-trademark
- [ ] End card holds 8s with music resolve
