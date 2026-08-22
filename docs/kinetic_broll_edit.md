# Kinetic Fast-Paced Edit — B-Roll Driven (Ep 01)

**Mood:** Fast-paced · Kinetic · B-roll-driven  
**Hero still:** Yellow ball (continuous motif on V2)  
**Editors:** DaVinci Resolve (assembly) · Blender (plates / B-roll angles) · **Cursor IDE** (command center + MCP)

---

## Style Shift (from hold-heavy TED-Ed → kinetic)

| Old TED-Ed lean | Kinetic B-roll lean |
|-----------------|---------------------|
| 1.5–3s between meaningful changes | **0.4–1.2s** average shot length on B-roll track |
| Long parallax holds | Punchy cutaways; holds only on stats / ball transforms |
| Illustration-only purity | **B-roll heavy** with illustrated accents + ball |
| Soft chapter fades | Hard cuts + ball-carry + smash zooms |

**Hybrid rule:** VO spine stays clear. B-roll fires *under and around* the ball — never replaces the ball as hero.

---

## Track Layout (Resolve)

| Track | Content |
|-------|---------|
| **V1** | A-roll spine — Blender scene masters / Ken Burns heroes (trimmed tight) |
| **V2** | Yellow ball overlays (transforms, trails) — always above chaos |
| **V3** | Kinetic B-roll A (stock / Blender alt angles) — cut every 8–28 frames |
| **V4** | Kinetic B-roll B (insert / detail / texture) — nested flash cuts |
| **V5** | TextStat / labels / lower-thirds |
| **A1** | VO |
| **A2** | Music (ducked) |
| **A3–A5** | SFX / whooshes on cuts |

---

## Kinetic Pacing Spec

| Beat type | Shot length | Cut style |
|-----------|-------------|-----------|
| B-roll texture | **8–18 frames** (0.33–0.75s) | Hard cut |
| Detail insert (hands, UI, solar) | **12–24 frames** | Hard cut / match cut |
| Ball transform | **24–48 frames** hold after impact | Cut *on* impact |
| Stat slam ($984M, 82%, 97%) | **36–60 frames** readable hold | Crash zoom in |
| Chapter open | **18–30 frames** establishing then flood B-roll | J-cut VO |

**Average ASL (average shot length) target:** ~0.7–1.0s during story beats; ~1.5–2.0s only on stats.

---

## B-Roll Driven Coverage Map

Every VO clause should trigger **≥1 B-roll cutaway** unless a diagram/stat is on screen.

| Scene | B-roll pack (kinetic) | Cut density |
|-------|----------------------|-------------|
| S01 Cold Open | City dawn, traffic lights, matatu texture, phone pocket | High — open cold with 6–8 flashes in first 15s |
| S02 2007 | Retro phone, keypad CU, street kiosk, cash hands | Medium-high |
| S03 Hubs | Laptop keyboards, whiteboards, coworking walk | High |
| S04 Phone | Thumb scroll, app UI, screen glow | Very high (short inserts) |
| S05 Money | Abstract data, charts growing, neon city | Medium — protect chart readability |
| S06 Solar | Panels, sun flare, suburb roofs, PAYG phone | High |
| S07 Gap | Map stills + sparse B-roll (don’t fight 97%) | Low during slam |
| S08 Secondary | Dusty street, shop front, cyclist, quiet town | Medium-slow (contrast) |
| S09 Closer | Modern skyline, glass, dusk, travel | High + gold ball arcs |
| S10 End | Minimal — logo only | Still |

### Sources
- `assets/stock/` Mixkit (expand list)
- Canva stock / video (MCP)
- Blender: alternate camera renders as “synthetic B-roll”
- Hero PNGs with aggressive Ken Burns as filler kinetic plates

---

## Editorial Tricks (Kinetic)

1. **Montage clusters** — 4–6 B-roll hits in 2–3 seconds on list VO (“rent paid… stock bought… loan repaid”)
2. **Match on action** — ball exits frame right → B-roll wipe / next plate enters
3. **L-cut storms** — music/SFX continue over picture flurry
4. **Flash frame** — 1–2 frame white/gold flash on chapter smash (use sparingly)
5. **Speed ramp B-roll** — 150–200% on travel shots; 100% on faces/hands detail
6. **Nested cutaways** — V4 peeks for 6–10 frames inside a V3 shot
7. **Sound-designed cuts** — every hard cut gets a tick/whoosh (±2f)

---

## Yellow Ball vs B-Roll Priority

```
IF stat or ball_transform_active:
    V3/V4 opacity down or pause kinetic flood
ELSE IF VO is listing / sensory:
    V3/V4 kinetic flood ON
ALWAYS:
    V2 ball visible OR intentionally dimmed (S07–08)
```

---

## Blender Tasks (for kinetic packs)

Per scene, render **short B-roll takes** (2–4s each), not only the long master:

| Take | Camera | Length |
|------|--------|--------|
| Master | Existing preset | Full scene dur |
| B-roll tight | Push-in 2× speed | 48–72 frames |
| B-roll pan whip | Fast pan 20° | 24–36 frames |
| B-roll detail | Close FG layer | 36–48 frames |

Script hook: extend `render_scenes_mp4.py` → `render_kinetic_broll.py` (Cursor agent mission — see `docs/CURSOR_KINETIC_MISSION.md`).

---

## Resolve Tasks

1. Add V3/V4 if missing; name tracks `BROLL_A` / `BROLL_B`
2. Import `assets/stock/` + kinetic Blender clips
3. Build **Episode 01 - Kinetic** variant timeline (don’t destroy Assembly)
4. Place VO first; flood B-roll to VO verbs
5. Overlay ball on V2; TextStat on V5
6. Fairlight: cut ticks on every hard edit during montage clusters

---

## Success Criteria

- ASL ≤ 1.0s in S01, S03, S04, S06, S09  
- ≥ 40 discrete B-roll cuts in the episode  
- Ball never lost for >3s except intentional dim chapter  
- Stats still readable (no B-roll fighting $984M / 97%)  
- Feels Fast-paced / kinetic on mute *and* with music
