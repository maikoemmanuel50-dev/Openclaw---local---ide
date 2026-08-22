# Dynamic & Vibrant Editorial + Animation Tricks

**Goal:** Silicon Savannah feels alive — energy, color, and rhythm — without clutter or a second hero.  
**Constraint:** Yellow ball remains the only protagonist.  
**Stack:** Cavalry / Fusion (ball) · Blender (plates) · Resolve Edit/Fusion/Fairlight/Color

---

## 1. Rhythm Rules (Editorial)

Dynamic ≠ constant motion. **Contrast** creates energy.

| Trick | How | Where |
|-------|-----|-------|
| **Breathing cuts** | Alternate dense 2–4s idea bursts with 0.5–1s holds | After each major VO sentence |
| **J-cuts / L-cuts** | Let VO start before picture change (or trail after) | Chapter boundaries S02→S03, S06→S07 |
| **Cut on the ball** | Change shot when the ball lands, splits, or impacts | Every `YB_*` marker |
| **Hard cut on numbers** | No dissolve into $984M / 82% / 97% | S05, S07 |
| **Speed ramp (subtle)** | 110% for 8–12 frames on ball travel; 100% on land | S01 rise, S05 inflate |
| **Never** | 1s black fades between chapters | Already banned in style bible |

**Pacing target (kinetic mode):** Average shot length **0.4–1.0s** on B-roll tracks; holds **1.5–2.5s** only on stats / ball transforms. See [`docs/kinetic_broll_edit.md`](kinetic_broll_edit.md).

**Pacing target (diagram mode):** Something meaningful changes every **1.5–3 seconds** when B-roll is paused for charts/maps.

---

## 2. Yellow Ball Motion (Animation Hero)

Use TED-Ed **timing + spacing** so the ball feels physical and vibrant.

| Trick | Spec | Effect |
|-------|------|--------|
| **Squash & stretch** | 85% height / 115% width on impact; reverse on launch | Coin morph (S02), bar hit (S05) |
| **Anticipation** | 4–6 frames pull-back before big move | Before 97% slam, before reignite |
| **Follow-through** | Soft glow / trail overshoots 3–5 frames | After orbit split, after gold arcs |
| **Secondary pulse** | Scale 1.00 → 1.06 → 1.00 every 24f when “alive” | S01, S04, S06, S09 |
| **Trail / motion blur** | Short gold ribbon (8–12f) only while moving fast | Travel beats only |
| **Color flash** | Fill pops to `#FFF8E1` for 2f on SFX hit | Stat impacts |
| **Orbit stagger** | 12f delay between hub nodes | S03 energy without chaos |
| **Dim ≠ dead** | S07–08: slower pulse (36f), lower chroma — still moves | Quiet contrast makes S09 pop |

**Cavalry / Fusion:** Prefer procedural pulse + ease curves over linear keys.

---

## 3. Camera & Parallax (Support, Don’t Steal)

| Trick | Spec | Scenes |
|-------|------|--------|
| **Push + ball rise** | Camera push-in while ball rises (compound energy) | S01, S09 |
| **Parallax micro-drift** | FG moves 1.2× mid speed | S03, S06, S08 |
| **Crash zoom (tiny)** | 1.0 → 1.08 over 6f on stat slam | S05 82%, S07 97% |
| **Dutch tilt — avoid** | Breaks documentary clarity | — |
| **Handheld — avoid** | Use controlled ease only | — |

---

## 4. Color & Vibrancy (Without Neon Soup)

| Trick | How |
|-------|-----|
| **Chapter snap** | Hard palette change at chapter cuts (Dawn → Daylight → DarkData…) |
| **Ball as constant accent** | `#FFD54F` always readable against chapter LUT |
| **Saturation contrast** | S07–08 desaturate background 30–40%; ball stays warmer → S09 flood of gold feels huge |
| **Accent pop frames** | 1–2 frames of boosted midtones on whoosh transitions (Resolve Color keyframes) |
| **Neon only in DarkData** | `#00E676` for chart energy; don’t spill neon into Dawn |
| **Avoid** | Purple glow, cream paper look, flat grey everything |

Resolve Color: use **node keyframes** for micro vibrancy pulses synced to music hits — not a global “make it punchy” grade.

---

## 5. Typography Motion (Make Facts Feel Alive)

| Trick | Spec |
|-------|------|
| **Count-up** | $0 → $984M over ~45–60f eased | 
| **Slam scale** | 1.25 → 1.0 over 5f with ease-out on 82% / 97% |
| **Stagger labels** | 8–12f between Fintech / Climate / hubs |
| **Kinetic underline** | 6f draw-on under key phrase |
| **Ball → text** | Ball touches or births the stat (ball expands into `$984M`) |

---

## 6. Transition Spice (Still TED-Ed Clean)

| From → To | Trick |
|-----------|-------|
| S01 → S02 | Ball *carries* the cut (ball exits frame / enters next) |
| S02 → S03 | Wipe *shaped by* ball trail (wipeleft 6–8f) |
| S04 → S05 | Hard cut + dark plate snap (chapter energy shift) |
| S05 → S06 | Morph ball → sun-disk (no black) |
| S08 → S09 | Cut on silence → music swell + ball reignite |

**Match cut:** End S06 on yellow sun-disk center; open S07 with ball as Nairobi glow (same screen position).

---

## 7. Audio = Perceived Dynamism

Picture feels faster when audio is rhythmic.

| Trick | Spec |
|-------|------|
| **Hit the cut** | Soft whoosh or tick within ±2f of edit |
| **Ball SFX vocabulary** | Rise = soft shimmer; impact = ping; split = triple tick; dim = low filter |
| **Music energy curve** | Dawn soft → Daylight lo-fi drive → DarkData pulse → Tension drone → Hopeful swell |
| **Pre-reveal dip** | −6 dB for 0.5s before 97% (already in audio map) |
| **Silence as punch** | 8–12f near-quiet before Forecast |
| **Sidechain feel** | Music ducks under VO fast (100ms); pops up on pauses |

---

## 8. Micro-Motion Backgrounds (Always Alive)

Never let plates freeze for >2s without *something*:

- Transaction path dashes crawling (S01)  
- Screen flicker 2% opacity (S03)  
- Chart bars breathing ±2% after grow (S05)  
- Solar shimmer loop (S06)  
- Map pulse (S07)  
- Dust / light particles very subtle (S08–S09)  

Cap particle opacity ≤15% so the ball stays dominant.

---

## 9. “Vibrant Checklist” Per Scene

| Scene | Must-have energy beat |
|-------|----------------------|
| S01 | Ball rise + path crawl + matatu SFX |
| S02 | Squash-to-coin + keypad rhythm |
| S03 | Triple orbit stagger |
| S04 | Ball enters UI + swipe SFX |
| S05 | Count-up + bar grow + 82% slam |
| S06 | Sun morph + shimmer |
| S07 | Anticipation → 97% crash zoom |
| S08 | Slow roll (contrast) |
| S09 | Reignite + gold arcs + music swell |
| S10 | Settle + chord — then stop (earned stillness) |

---

## 10. What Not to Do (Kills Clarity)

- Constant camera shake  
- Too many simultaneous labels  
- Rainbow gradients everywhere  
- Long crossfades  
- Second mascot / acting character  
- Music that never ducks for VO  

---

## Implementation Order (Resolve-first)

1. Lock VO → place `YB_*` markers  
2. Animate ball transforms on V2 (Cavalry/Fusion) with squash/pulse  
3. Add TextStat slam/count-up on stats  
4. Shorten transitions; ball-carry cuts  
5. Fairlight: whooshes on cuts + chapter music energy curve  
6. Color: chapter LUTs + micro saturation pulses on hits  
7. Playback test: scrub — if any 3s window feels static, add micro-motion or a ball pulse
