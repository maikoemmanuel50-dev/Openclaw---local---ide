# Dynamic Edit & Transitions — Africa S1 Ep01

**Hard rule:** no picture hold / B-roll cut exceeds **5.0 s** (≤ **120 frames** @ 24 fps).  
Preferred kinetic ASL: **0.4–2.0 s** (10–48f). Stat slams may hold up to **5 s** max, then cut.

**Refs (style + technique):**
- [TED-Ed / high-speed rail explainer](https://youtu.be/2A1IEBFt6Xg) — VO-led, illustration + rapid concept cuts  
- [https://youtu.be/xV82vkJ5Pjw](https://youtu.be/xV82vkJ5Pjw) — kinetic / dynamic pacing reference  
- [https://youtu.be/CbUjuwhQPKs](https://youtu.be/CbUjuwhQPKs) — transition / montage energy reference  
- Resolve how-tos: [whip pan](https://xere.my/tutorials/whip-pan-transition/), [zoom blur](https://cutsio.com/blog/zoom-transition-tutorial-in-davinci-resolve-smooth-zoom-blur-transition), [adjustment-clip whip](https://nofilmschool.com/editing-tips-davinci-reslove)

TED-Ed timing/spacing basics (animation rhythm): [TED-Ed Animation Basics](https://ed.ted.com/ted_ed_collections/animation-basics).

---

## What “≤5 seconds” means on our timeline

| Layer | Rule |
|-------|------|
| **V1** Blender plate | May roll continuously under VO, but **viewer-facing picture** must change ≥ every **5 s** via V3/V4 insert, TextStat, or hard cut. |
| **V3/V4** kinetic/stock | Clip length **10–48f** typical; **hard max 120f**. |
| **V5** TextStat | Readable hold ≤ **5 s**, then out or swap. |
| **Scene→scene** | Dedicated transition (below), usually **6–15f** — never a 5s dissolve. |

---

## Transition toolkit (use these)

| Name | Length | When | How (Resolve) |
|------|--------|------|----------------|
| **Hard cut** | 0f | Default noun flash, list VO | Straight cut; match VO syllable |
| **Match cut** | 0f | Shape/motion continuity (bar→panel, phone→phone) | Cut on similar framing / motion vector |
| **Whip / smear** | 6–10f | Chapter energy, Africa@30s energy | Adjustment clip + Transform X + Directional Blur peak at cut ([tutorial](https://xere.my/tutorials/whip-pan-transition/)) |
| **Zoom blur** | 8–12f | Into close-up / data | Adjustment clip Fusion: Transform scale + Directional Blur ([tutorial](https://cutsio.com/blog/zoom-transition-tutorial-in-davinci-resolve-smooth-zoom-blur-transition)) |
| **Slide wipe** | 8f | S02→S03 “blueprint” | Built-in wipe or Fusion slide |
| **Color hold** | 2–4f | S03→S04 same chapter | Freeze grade, hard cut under |
| **Morph / graphic** | 12–15f | S05→S06 bar→solar | Blender handoff + hard cut mid-morph |
| **Fade** | 8–12f | S07→S08, S09→S10 only | Short fade — not chapter black |

**Avoid:** long dissolves, 1s black chapter cards, multi-second Smooth Cuts.

---

## Per-scene OUT transitions (locked)

| From → To | Transition | Max |
|-----------|------------|-----|
| S01 → S02 | Hard cut | 0f |
| S02 → S03 | Slide wipe R | 8f |
| S03 → S04 | Color hold + cut | ≤4f |
| S04 → S05 | Hard cut (chapter) | 0f |
| S05 → S06 | Morph | 15f |
| S06 → S07 | Hard cut | 0f |
| S07 → S08 | Fade | 8f |
| S08 → S09 | Hard cut | 0f |
| S09 → S10 | Fade | 12f |
| S10 → black | Fade | ≤15f |

---

## Cadence recipe (TED-Ed / kinetic hybrid)

1. On each VO clause, fire a **new** still or stock cut (unique asset).  
2. If VO runs >5 s without a noun, insert texture B-roll anyway (city grain, fiber, abstract).  
3. Protect only: `$984M`, `82%`, `97%`, Africa whip settle — still ≤5 s.  
4. Cut **on** emphasis words; transition **between** chapters with whip/wipe/morph — not during dense lists.

---

## Verify before “done”

- No timeline clip on V3/V4 longer than **120f**  
- No >5 s stretch without a visible picture change  
- Transitions match table above  
- Delivery: `docs/DELIVERY_STANDARDS.md`
