# TED-Ed Style Scene Spec — Episode 01: Silicon Savannah

**Reference:** [TED-Ed high-speed rail explainer](https://youtu.be/2A1IEBFt6Xg)  
**Script:** [episode_1_script.md](../episode_1_script.md)  
**Style bible:** [teded_style_bible.md](teded_style_bible.md)  
**Audio map:** [audio_design_map.yaml](audio_design_map.yaml)  
**Target:** 7:00 @ 24fps (10,080 frames)

---

## Scene Index

| # | ID | Chapter | Duration (est.) | TED-Ed Pattern |
|---|-----|---------|-----------------|----------------|
| 1 | S01_ColdOpen | Dawn | 50s | Hook + abstract overlay |
| 2 | S02_Context2007 | Dawn | 45s | Historical flashback + diagram |
| 3 | S03_Beat1_Hubs | Daylight | 45s | 3-factor enumeration |
| 4 | S04_Beat1_Phone | Daylight | 25s | Close-up + concept label |
| 5 | S05_Beat2_Money | DarkData | 45s | Data viz + counter |
| 6 | S06_Beat2_Solar | DarkData | 40s | Supporting example |
| 7 | S07_Beat3_Gap | CoolTension | 50s | Map reveal + stat slam |
| 8 | S08_Beat3_SecondaryCity | CoolTension | 35s | Contrast / quiet beat |
| 9 | S09_Closer | HopefulDusk | 70s | Optimistic turn + icons |
| 10 | S10_EndCard | HopefulDusk | 15s | Series card |

---

## S01 — Cold Open

**Chapter:** Dawn | **Camera:** Push-In | **Duration:** 50s (1,200 frames)

### Narration Anchor
> Six-thirty in the morning in Nairobi… packed into matatus… the real motion isn't on the road. It's in people's pockets. Before most people here have had their first cup of tea, money has already moved… This is Nairobi… the Silicon Savannah.

### TED-Ed Analogue
Opening hook — iconic image + abstract concept overlay (like Shinkansen launch montage).

### Composition (layer stack)
| Layer | Z | Content |
|-------|---|---------|
| BG | -2 | Dawn gradient sky (`assets/canva/s1_dawn_skyline.png`) |
| Mid | -1 | CBD tower silhouettes |
| FG | 0 | Matatu + motorbike silhouettes (`assets/canva/s1_matatu_silhouettes.png`) |
| Overlay | 1 | Digital transaction paths (`assets/diagrams/s1_digital_paths.svg`) |
| UI | 2 | "Nairobi" location label |

### Element Animations
| Trigger (VO word) | Element | Animation | Frames (est.) |
|-------------------|---------|-----------|---------------|
| "Nairobi" | Location label | Fade in + slide up | 72–80 |
| "matatus" | Matatu silhouettes | Subtle bounce (2px Y) | 180–200 |
| "pockets" | Transaction paths overlay | Fade in 0→0.7 opacity, paths animate L→R | 360–480 |
| "money has already moved" | Path pulse | Glow pulse on path nodes | 540–600 |
| "phone" | Path convergence | Lines converge to phone icon | 720–780 |
| "Silicon Savannah" | Subtitle label | Fade in below "Nairobi" | 1140–1200 |

### On-Screen Text
| String | Style | Timing (post-VO-lock) |
|--------|-------|----------------------|
| `Nairobi` | Label 36px | ~3s |
| `Silicon Savannah` | Headline 72px | ~47s |

### Transition Out
**Type:** `cut` on final word "Silicon Savannah" → S02

### SFX Cues
| Word | SFX | Level |
|------|-----|-------|
| "matatus" | `matatu_horn.wav` | -18 dB |
| "money has already moved" | `transaction_chime.wav` | -18 dB |
| Scene start | `city_morning_ambient.wav` | -24 dB (continuous) |

### Music
Chapter bed: `ch01_dawn_pad.wav` — gentle synth pad rises from silence over first 5s.

### Assets
| Asset | Status | Path |
|-------|--------|------|
| Dawn skyline | Existing | `assets/canva/s1_dawn_skyline.png` |
| Matatu silhouettes | Existing | `assets/canva/s1_matatu_silhouettes.png` |
| Transaction paths | **New** | `assets/diagrams/s1_digital_paths.svg` |

### Authoring
- **Blender:** Camera push-in, parallax planes, transaction path overlay animation
- **Resolve:** Location labels (Fusion TextStat template)

---

## S02 — Context 2007

**Chapter:** Dawn | **Camera:** Pan L→R | **Duration:** 45s (1,080 frames)

### Narration Anchor
> That nickname isn't a marketing invention… In 2007, Safaricom launched M-Pesa… most Kenyans had no bank account… M-Pesa didn't try to get people into bank branches… sending money by text message… the quiet blueprint for almost everything that came after.

### TED-Ed Analogue
Historical flashback + labeled diagram (like "three main factors" intro structure).

### Composition
| Layer | Z | Content |
|-------|---|---------|
| BG | -2 | Warm retro yellow gradient |
| Mid | -1 | Phone kiosk illustration (`assets/canva/s2_kiosk_2007.png`) |
| FG | 0 | Nokia handsets on display |
| Overlay | 1 | M-Pesa flow diagram (`assets/diagrams/s2_mpesa_flow.svg`) |
| UI | 2 | "2007" year label, "M-PESA" title card |

### Element Animations
| Trigger | Element | Animation |
|---------|---------|-----------|
| "2007" | Year label | Slam in (scale 1.2→1.0) | 60–72 |
| "M-Pesa" | Title card "M-PESA" | Fade in center-top | 120–140 |
| "no bank account" | Flow step 1 (phone icon) | Slide in from left | 300–320 |
| "bank branches" | Flow step 2 (agent icon) | Slide in | 480–500 |
| "text message" | Flow step 3 (recipient icon) | Slide in | 660–680 |
| "blueprint" | Connector arrows | Draw-on animation | 960–1000 |

### On-Screen Text
| String | Style | Timing |
|--------|-------|--------|
| `2007` | Stat 96px | ~2.5s |
| `M-PESA` | Headline 72px | ~5s |
| `Phone → Agent → Recipient` | Label 36px | staggered 12–22s |

### Transition Out
**Type:** `slide_wipe` right on "blueprint" → S03 (8 frames)

### SFX Cues
| Word | SFX |
|------|-----|
| "M-Pesa" | `brand_sting.wav` |
| "text message" | `keypad_click.wav` |
| Scene | `street_bustle.wav` (continuous, -24 dB) |

### Music
Continue `ch01_dawn_pad.wav`; slight tempo lift at "M-Pesa" mention.

### Assets
| Asset | Status | Path |
|-------|--------|------|
| Kiosk 2007 | Existing | `assets/canva/s2_kiosk_2007.png` |
| M-Pesa flow diagram | **New** | `assets/diagrams/s2_mpesa_flow.svg` |
| Phone icon | **New** | `assets/icons/icon_phone.svg` |
| Agent icon | **New** | `assets/icons/icon_agent.svg` |

### Authoring
- **Blender:** Pan camera, flow diagram stagger animation, draw-on arrows
- **Resolve:** Year label, M-PESA title card

---

## S03 — Beat 1: The Hubs

**Chapter:** Daylight | **Camera:** Parallax Drift | **Duration:** 45s (1,080 frames)

### Narration Anchor
> If M-Pesa built the digital pipes… iHub—a co-working space… ground zero… Andela and NaiLab… training waves of developers…

### TED-Ed Analogue
3-factor enumeration (engines / aerodynamics / infrastructure → iHub / Andela / NaiLab).

### Composition
| Layer | Z | Content |
|-------|---|---------|
| BG | -2 | Co-working interior (`assets/canva/s3_coworking.png`) |
| Mid | -1 | Desks, laptops, whiteboards |
| FG | 0 | Plants, foreground desk edge |
| Overlay | 1 | Hub cards (`assets/diagrams/s3_hub_cards.svg`) |
| UI | 2 | Card labels |

### Element Animations
| Trigger | Element | Animation |
|---------|---------|-----------|
| "iHub" | Card 1 "iHub 2010" | Stagger slide-in (delay 0) | 240–260 |
| "Andela" | Card 2 "Andela" | Stagger slide-in (delay 12f) | 540–560 |
| "NaiLab" | Card 3 "NaiLab" | Stagger slide-in (delay 24f) | 720–740 |
| "desks" | Laptop screens | Screen flicker loop | continuous |
| "whiteboards" | Whiteboard lines | Draw-on | 400–480 |

### On-Screen Text
| String | Style | Timing |
|--------|-------|--------|
| `iHub 2010` | Label 36px | ~10s |
| `Andela` | Label 36px | ~22s |
| `NaiLab` | Label 36px | ~30s |

### Transition Out
**Type:** `color_hold` cut → S04 (same Daylight chapter)

### SFX / Music
- Ambient: `coworking_chatter.wav` (-24 dB)
- Keyboard clacks on "desks"
- Music: `ch02_daylight_lofi.wav` enters at scene start

### Assets
| Asset | Status | Path |
|-------|--------|------|
| Coworking interior | Existing | `assets/canva/s3_coworking.png` |
| Hub cards | **New** | `assets/diagrams/s3_hub_cards.svg` |

---

## S04 — Beat 1: Phone Close-Up

**Chapter:** Daylight | **Camera:** Push-In (tight) | **Duration:** 25s (600 frames)

### Narration Anchor
> Add a population that came online through a phone… designed for the small screen… the only computer that ever mattered.

### TED-Ed Analogue
Close-up detail + concept label (like aerodynamic body close-up).

### Composition
| Layer | Z | Content |
|-------|---|---------|
| BG | -1 | Soft blur |
| Mid | 0 | Hand + phone (`assets/canva/s4_phone_hand.png`) |
| Overlay | 1 | UI highlight boxes |
| UI | 2 | "Mobile-First" label |

### Element Animations
| Trigger | Element | Animation |
|---------|---------|-----------|
| "phone" | Phone screen | UI scroll micro-animation (thumb drag) | 60–300 |
| "small screen" | UI highlight boxes | Box draw-on around app elements | 180–240 |
| "Mobile-First" | Label | Fade in + slide up | 360–380 |

### On-Screen Text
| String | Style | Timing |
|--------|-------|--------|
| `Mobile-First` | Headline 72px | ~15s |

### Transition Out
**Type:** `cut` → S05 (chapter change to DarkData)

### SFX / Music
- Continue `ch02_daylight_lofi.wav`
- `ui_swipe.wav` on scroll animation

---

## S05 — Beat 2: The Money (PRIORITY)

**Chapter:** DarkData | **Camera:** Push-In | **Duration:** 45s (1,080 frames)

### Narration Anchor
> Here's where the story becomes measurable. In 2025 alone, Kenyan startups raised close to a billion dollars… Fintech still leads… eighty-two percent of that capital was concentrated in… climate-tech and energy-financing companies.

### TED-Ed Analogue
Data visualization with animated bars + stat counter (like speed comparison charts).

### Composition
| Layer | Z | Content |
|-------|---|---------|
| BG | -1 | Dark charcoal `#1A1A2E` |
| Mid | 0 | Geometry Nodes bar chart (4 sectors) |
| Overlay | 1 | Sector labels, stat callouts |
| UI | 2 | `$984M` counter, `82%` glow |

### Element Animations
| Trigger | Element | Animation |
|---------|---------|-----------|
| "measurable" | Chart frame | Fade in chart outline | 60–80 |
| "a billion dollars" | `$984M` counter | Count up 0→984 | 180–240 |
| "Fintech" | Fintech bar + label | Bar rises, label fades in | 360–400 |
| "Climate/Energy" | Climate bar + label | Bar rises (tallest), neon glow | 540–600 |
| "eighty-two percent" | `82%` callout | Slam in center, pulse glow | 780–840 |
| E-commerce, Logistics | Remaining bars | Rise sequentially | 420–520 |

### On-Screen Text
| String | Style | Timing |
|--------|-------|--------|
| `$984M` | Stat 96px neon green | ~7.5s |
| `Fintech` | Label 36px | ~15s |
| `Climate/Energy` | Label 36px | ~22s |
| `82%` | Stat 96px accent | ~32s |

### Transition Out
**Type:** `morph` — tallest bar morphs to solar panel silhouette → S06 (15 frames)

### SFX / Music
| Word | SFX |
|------|-----|
| Bar growth | `chart_riser.wav` |
| "$984M" | `stat_ping.wav` |
| "eighty-two percent" | `stat_impact.wav` |
| Music: `ch03_darkdata_electronic.wav` |

### Assets
| Asset | Status | Path |
|-------|--------|------|
| Bar chart (Geometry Nodes) | Existing | `blend/africa_s1_master_v01.blend` Scene 05 |
| Sector labels | **New** | Blender text objects / Resolve overlay |

### Authoring
- **Blender:** Bar animation, counter, label triggers, morph frame to S06
- **Resolve:** `$984M` and `82%` TextStat overlays (backup)

---

## S06 — Beat 2: Solar

**Chapter:** DarkData | **Camera:** Parallax Drift | **Duration:** 40s (960 frames)

### Narration Anchor
> Businesses like d.light, Sun King, M-KOPA, and BURN… financing solar panels and clean cookstoves… the M-Pesa instinct, aimed at energy instead of cash.

### TED-Ed Analogue
Supporting example after data (like maglev after speed comparison).

### Composition
| Layer | Z | Content |
|-------|---|---------|
| BG | -2 | Leafy suburb |
| Mid | -1 | Rooftop + solar panels (procedural) |
| FG | 0 | Solar glare overlay |
| UI | 1 | Company tags, "Pay-As-You-Go Solar" label |

### Element Animations
| Trigger | Element | Animation |
|---------|---------|-----------|
| Scene start | Solar panels | Reveal from S05 morph | 0–15 |
| "d.light" | Company tag 1 | Fade in lower-left | 120–140 |
| "Sun King" | Company tag 2 | Fade in | 200–220 |
| "M-KOPA" | Company tag 3 | Fade in | 280–300 |
| "BURN" | Company tag 4 | Fade in | 360–380 |
| "M-Pesa instinct" | "Pay-As-You-Go Solar" label | Fade in center | 600–640 |
| Continuous | Sun glare | Shimmer loop | all frames |

### On-Screen Text
| String | Style | Timing |
|--------|-------|--------|
| `Pay-As-You-Go Solar` | Headline 72px | ~25s |
| `d.light · Sun King · M-KOPA · BURN` | Label 28px | staggered 5–16s |

### Transition Out
**Type:** `cut` → S07 (chapter change to CoolTension)

### SFX / Music
- `solar_hum.wav` ambient (-24 dB)
- Continue `ch03_darkdata_electronic.wav`; fade at scene end

---

## S07 — Beat 3: The Gap (PRIORITY)

**Chapter:** CoolTension | **Camera:** Custom Zoom-Out | **Duration:** 50s (1,200 frames)

### Narration Anchor
> The overwhelming majority of Kenya's registered startups—around ninety-seven percent—are based in Nairobi. Step outside the capital… Mombasa, Kisumu, Eldoret, or Nakuru…

### TED-Ed Analogue
Map/infrastructure reveal — signature TED-Ed zoom-out moment.

### Composition
| Layer | Z | Content |
|-------|---|---------|
| BG | -2 | Kenya map (`assets/canva/s7_kenya_map.png`) |
| Mid | -1 | Regional city markers (dim) |
| Overlay | 0 | Nairobi glow pulse |
| UI | 1 | `97%` stat slam |

### Element Animations
| Trigger | Element | Animation |
|---------|---------|-----------|
| Scene start | Nairobi glow | Tight zoom, pulse intensifies | 0–120 |
| "ninety-seven percent" | `97%` stat | Slam center-screen, hold 2s | 360–420 |
| Zoom-out | Camera | Pull back to reveal full map | 120–600 |
| "Mombasa" | Mombasa marker | Dim blink (no glow) | 660–680 |
| "Kisumu" | Kisumu marker | Dim blink | 720–740 |
| "Eldoret" | Eldoret marker | Dim blink | 780–800 |
| "Nakuru" | Nakuru marker | Dim blink | 840–860 |

### On-Screen Text
| String | Style | Timing |
|--------|-------|--------|
| `97%` | Stat 96px neon accent | ~15s |
| `Nairobi` | Label 36px | ~3s (during zoom) |
| `Mombasa · Kisumu · Eldoret · Nakuru` | Subtitle 28px | staggered 27–36s |

### Transition Out
**Type:** `fade` 8 frames → S08

### SFX / Music
- **Pre-reveal dip:** music -6dB for 0.5s before "ninety-seven percent"
- `stat_impact.wav` on 97%
- `drone_ambient.wav` during zoom-out
- Music: `ch04_cooltension_drone.wav`

### Assets
| Asset | Status | Path |
|-------|--------|------|
| Kenya map | Existing | `assets/canva/s7_kenya_map.png` |
| Map pin icon | **New** | `assets/icons/icon_map_pin.svg` |

---

## S08 — Beat 3: Secondary City

**Chapter:** CoolTension | **Camera:** Parallax Drift | **Duration:** 35s (840 frames)

### Narration Anchor
> Even inside Nairobi, the money doesn't move evenly… the small, early-stage pre-seed checks… infrastructure, market access… unglamorous, repeatable systems…

### TED-Ed Analogue
Quiet contrast shot (like secondary city after map reveal).

### Composition
| Layer | Z | Content |
|-------|---|---------|
| BG | -2 | Desaturated regional street |
| Mid | -1 | Small shop, cyclist |
| UI | 1 | "Pre-seed gap" label |

### Element Animations
| Trigger | Element | Animation |
|---------|---------|-----------|
| Scene start | Full scene | Desaturate to 60% | 0–30 |
| "pre-seed" | "Pre-seed gap" label | Fade in lower-third | 300–340 |
| "infrastructure" | Empty seat icon | Fade in (metaphor) | 540–580 |

### On-Screen Text
| String | Style | Timing |
|--------|-------|--------|
| `Pre-seed gap` | Label 36px | ~12s |

### Transition Out
**Type:** `cut` → S09 (chapter change to HopefulDusk)

### SFX / Music
- Quiet street ambient only (-26 dB)
- Continue `ch04_cooltension_drone.wav`; minimal

---

## S09 — Closer (PRIORITY)

**Chapter:** HopefulDusk | **Camera:** Push-In | **Duration:** 70s (1,680 frames)

### Narration Anchor
> Microsoft picked Nairobi… Visa opened an innovation studio… three United Nations agencies… A nickname like Silicon Savannah… It's starting to look more like a forecast… dozens of them…

### TED-Ed Analogue
Optimistic closer with sequential reveals (like "countries expanding rail" ending).

### Composition
| Layer | Z | Content |
|-------|---|---------|
| BG | -2 | Dusk skyline (`assets/canva/s9_dusk_skyline.png`) |
| Mid | -1 | Modern glass facades |
| Overlay | 0 | Stylized logo silhouettes |
| UI | 1 | "Forecast" text |

### Element Animations
| Trigger | Element | Animation |
|---------|---------|-----------|
| "Microsoft" | Logo silhouette 1 | Fade in upper-left | 120–160 |
| "Visa" | Logo silhouette 2 | Fade in upper-right | 300–340 |
| "United Nations" | Logo silhouette 3 | Fade in center | 540–580 |
| "forecast" | "Forecast" text | Scale in 1.2→1.0 | 1200–1240 |
| "dozens of them" | City name tags | Fade in bottom strip | 1500–1600 |

### On-Screen Text
| String | Style | Timing |
|--------|-------|--------|
| `Forecast` | Headline 72px gold | ~50s |
| `Lagos · Kigali · Accra` | Subtitle 28px | ~62s |

### Transition Out
**Type:** `fade` 12 frames → S10

### SFX / Music
- Music swell: `ch05_hopeful_dusk.wav` + percussion layer at scene start
- `logo_fade.wav` on each icon entrance

---

## S10 — End Card

**Chapter:** HopefulDusk | **Camera:** Subtle Drift | **Duration:** 15s (360 frames)

### Narration Anchor
(none — music resolve only)

### Composition
| Layer | Z | Content |
|-------|---|---------|
| BG | -1 | Dark textured background |
| Mid | 0 | AFRICA wordmark only — no Netflix/subtitle lockup (`assets/canva/s10_africa_logo.png` v2) |
| UI | 1 | "Season 1" subtitle |

### Element Animations
| Element | Animation |
|---------|-----------|
| AFRICA logo | Hold center, subtle drift | 0–360 |
| "Season 1" | Fade in at 60f, hold | 60–360 |
| Final 60 frames | Fade to black | 300–360 |

### On-Screen Text
| String | Style | Timing |
|--------|-------|--------|
| `AFRICA` | Logo (asset) | 0–15s |
| `Season 1` | Subtitle 28px | ~2.5s |

### SFX / Music
- Final chord: `music_resolve.wav`
- Decay to silence over last 2s

---

## Asset Summary

### Existing (reuse)
- `assets/canva/s1_dawn_skyline.png`
- `assets/canva/s1_matatu_silhouettes.png`
- `assets/canva/s2_kiosk_2007.png`
- `assets/canva/s3_coworking.png`
- `assets/canva/s4_phone_hand.png`
- `assets/canva/s7_kenya_map.png`
- `assets/canva/s9_dusk_skyline.png`
- `assets/canva/s10_africa_logo.png`
- `blend/africa_s1_master_v01.blend` (Scenes 01–10)

### New (create)
- `assets/diagrams/s1_digital_paths.svg`
- `assets/diagrams/s2_mpesa_flow.svg`
- `assets/diagrams/s3_hub_cards.svg`
- `assets/diagrams/template_split_compare.svg`
- `assets/icons/icon_phone.svg`
- `assets/icons/icon_agent.svg`
- `assets/icons/icon_recipient.svg`
- `assets/icons/icon_solar.svg`
- `assets/icons/icon_map_pin.svg`
- `assets/audio/music/ch01_dawn_pad.wav` … `ch05_hopeful_dusk.wav`
- `assets/audio/sfx/` (25 cues — see audio_design_map.yaml)
- `assets/audio/vo/episode_01_vo.wav`

---

## Blender vs Resolve Split

| Effect | Blender | Resolve |
|--------|---------|---------|
| Camera motion | All scenes | — |
| Parallax planes | S01, S03, S06, S08 | — |
| Bar chart animation | S05 | — |
| Map zoom-out + pulse | S07 | — |
| Flow diagram stagger | S02 | — |
| Hub card stagger | S03 | — |
| Transaction path overlay | S01 | Backup: Fusion |
| Stat callouts ($984M, 82%, 97%) | S05, S07 | Fusion TextStat |
| Typography labels | Backup | Primary (Fusion) |
| Morph S05→S06 | S05/S06 | — |
| Color LUT conform | — | All scenes |
| VO + music + SFX mix | — | Fairlight |
