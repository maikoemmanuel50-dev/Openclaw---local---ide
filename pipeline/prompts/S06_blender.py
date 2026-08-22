# Blender Visual Prompt — S06: Beat 2: Solar
# Chapter: DarkData | Camera: Parallax Drift
# Duration: 40s (960 frames @ 24fps)
# Frame range: 5040–6000
# Style: Supporting example after data

## COMPOSITION (Layer Stack)
  Z=-2 [BG]: Leafy suburb
  Z=-1 [MID]: Rooftop + solar panels procedural
  Z=+0 [FG]: Solar glare overlay
  Z=+2 [UI]: Company tags + Pay-As-You-Go Solar label

## CAMERA MOTION
- Type: Parallax Drift
- Duration: 40s
- Frame range: 5040–6000

## ELEMENT ANIMATIONS (VO-synced triggers)
  VO word "d.light Sun King" -> Company tags: Stagger fade-in (frames 120-200)
  VO word "solar panels" -> Panel array: Glare sweep L->R (frames 300-420)
  VO word "daily payment" -> Payment flow icon: Coin stack build (frames 540-660)
  VO word "M-Pesa instinct" -> Callback connector: Draw-on arrow from S02 flow (frames 780-840)

## ON-SCREEN TEXT
  "Pay-As-You-Go Solar" [Headline 72px] at 22s

## ASSETS REQUIRED
  [CREATE] assets/diagrams/s6_solar_flow.svg

## SFX TRIGGERS
  "scene" -> solar_hum.wav (-24 dB)
  "solar panels" -> glare_sweep.wav (-20 dB)

## MUSIC
- Bed: ch03_darkdata_electronic.wav

## TRANSITION OUT
- Type: fade_to_black
