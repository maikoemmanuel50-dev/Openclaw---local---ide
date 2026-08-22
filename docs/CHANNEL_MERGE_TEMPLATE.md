# Animation + Stock Merge Template (Fern · Imperial · LEMMiNO · TED-Ed)

**Project use:** Africa S1 Ep01 — Resolve V1 Blender plates · V2 yellow ball · V3/V4 kinetic stills/stock · V5 TextStat  
**Related:** `docs/CURSOR_KINETIC_MISSION.md` · `docs/FIDELITY_EXECUTION_GUIDE.md` · `docs/PRE_4K_GATE.md` · `docs/DOCUMENTARY_AESTHETIC_LOCK.md`  
**Video refs:** [Fern/Neo/Imperial faceless edit](https://youtu.be/Jmcg5ZSU8a8) · [Aesthetic YT 3D docs](https://youtu.be/YJdGgpZoiAA) · [tinynocky 18-day pipeline](https://youtu.be/tCTkkHGRpNk)

---

## Channel pattern cheat-sheet

| Channel | How they merge animation + photos/stock | Cut density |
|---------|------------------------------------------|-------------|
| **Fern** | Short **3–10s** motion beats (parallax stills, maps, docs, light 3D) between VO beats; atmospheric grain/vignette unifies CGI + photo; ~40–50 graphic inserts per long episode | High — many brief inserts |
| **Imperial** (YT finance/edutainment style) | Talking-head or VO spine + **clean custom 2D/3D explainers** + curated stock; data viz and maps carry concepts; smooth fluid transitions | Medium-high |
| **LEMMiNO** | Faceless VO; **abstract motion graphics** + carefully chosen **archival stills** (not literal people-walking B-roll); cinematic restraint; graphics feel templated once look is locked | Medium — deliberate holds |
| **TED-Ed** | VO-first; **purpose-built illustration/animation** as primary picture; minimal literal stock; when photos appear they are **treated** (grade, crop, abstract) to match the design system | Medium — beats follow script beats |

### Shared “template” (what we copy for Africa S1)

1. **Spine track (V1):** continuous animated world (Blender scenes) — Fern/TED-Ed 3D base.  
2. **Hero motif (V2):** one recurring symbol (our **yellow ball** / YB-Body) — LEMMiNO-style abstract continuity.  
3. **Cut density layer (V3/V4):** short stills + light Dynamic Zoom / Ken Burns — Fern insert density without fighting V1.  
4. **Text/stat (V5):** kinetic labels only on protected holds ($984M / 82% / 97%).  
5. **Unify:** one grade + subtle grain so CGI plates and generated stills feel same show.

---

## Cut recipe (ASL targets)

| Beat type | Duration | Media |
|-----------|----------|--------|
| Montage / energy | **0.4–1.0s** | Graded still or 2–3s clip with push-in |
| Concept explain | **1.5–3s** | Blender plate or Canva diagram |
| Stat slam | **36–60 frames** | Hold — no dense B-roll over numbers |
| Quiet contrast (S08) | **2–4s** | Soft still, slow zoom |

**Do not:** 1s black chapter fades · faces/acting cast · Mixkit dependency · soft multi-reencoded Ken Burns masters.

---

## Layer sandwich (Resolve)

```
V5  TextStat / captions          (sparse)
V4  Kinetic B — alternate stills (0.4–1.0s)
V3  Kinetic A — primary stills   (0.4–1.0s)
V2  Yellow ball / YB-Body        (hero only)
V1  Blender scene plates         (spine)
A1  VO
```

**Merge trick (Fern/Imperial):** On VO nouns (“matatu”, “phone”, “solar”, “hub”), cut a **matching still** on V3 for ~12–24 frames while V1 keeps rolling underneath at lower opacity **or** hard-cut replace if plate is static.

**Merge trick (LEMMiNO):** Prefer **metaphor** images (circuit-as-savannah, glowing nodes, abstract maps) over literal street crowds.

**Merge trick (TED-Ed):** Same color bible / soft-pop as Blender; treat AI/Canva stills as **designed frames**, not raw photo dumps.

---

## Asset pipeline (this project)

1. Generate 16:9 stills → `assets/stock/kinetic/` (Gemini + Canva).  
2. Optional Canva polish (crop, color wash, AFRICA grade) → export PNG 1920×1080.  
3. Import Media Pool folder **Kinetic_Stills**.  
4. Place on V3/V4 at markers; Dynamic Zoom 105%→112% max (subtle).  
5. Preview: `python assemble_kinetic_preview.py` when wired.

### Shot list buckets (generate into these)

| Prefix | Scene | Visual ideas (no faces) |
|--------|-------|-------------------------|
| `k_s01_` | Cold open | Dawn Nairobi skyline silhouette, matatu exterior abstract, phone glow pocket metaphor |
| `k_s02_` | 2007 | Soft vintage tech desk, early feature phone still life, dusty CRT glow |
| `k_s03_` | Hubs | Co-working desks empty, fiber cable macro, neon “hub” signage abstract |
| `k_s04_` | Phone | Handless phone UI glow, M-Pesa-style abstract green UI (no logos) |
| `k_s05_` | Money | Coin cascade abstract, chart bars soft-pop, vault-of-light |
| `k_s06_` | Solar | Rooftop panels, sun flare on silicon, yellow ball as sun analogue |
| `k_s07_` | Gap | Dark map with sparse nodes, cable gap metaphor |
| `k_s08_` | Secondary | Quiet kiosk night, single bulb, empty street abstract |
| `k_s09_` | Closer | Warm dusk skyline, constellation of nodes, hopeful grid |

---

## Sources

- Fern-style editor brief (parallax, maps, 3–10s sequences): [FilmLocal Fern-style role](https://filmlocal.com/job/freelance-video-editor-documentary-fern-style-kyle-newscape-studios/)  
- Fern 3D/AE reconstruction culture: [SigmaStory on Fern](https://sigmastory.in/fern-proves-high-end-3d-animation-and-documentaries-are-the-future-of-youtube/)  
- LEMMiNO abstract + archival (not literal B-roll): [BecomeViral LEMMiNO case](https://becomeviral.com/blog/lemmino-case-study)  
- TED-Ed animation process: [Making a TED-Ed Lesson: Animation](https://ed.ted.com/lessons/making-a-ted-ed-lesson-animation) · [Einstein minimalism](https://blog.ed.ted.com/2015/01/13/designing-einstein-2-animators-use-minimalist-style-to-illustrate-history/)  
- Imperial / edutainment hybrid cited in hiring briefs: [YT Jobs Imperial-inspired style](https://ytjobs.co/job/39466) · interview+stock+animation: [Velvet Green / Grantham](https://www.velvetgreen.xyz/client-stories/climate-documentaries)
