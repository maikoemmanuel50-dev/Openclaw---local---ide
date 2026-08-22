# Blender Visual Prompt — S02: Context 2007
# Chapter: Dawn | Camera: Pan L->R
# Duration: 45s (1080 frames @ 24fps)
# Frame range: 1200–2280
# Style: Historical flashback + diagram

## COMPOSITION (Layer Stack)
  Z=-2 [BG]: Warm retro yellow gradient
  Z=-1 [MID]: Phone kiosk illustration
  Z=+0 [FG]: Nokia handsets on display
  Z=+1 [OVERLAY]: M-Pesa flow diagram
  Z=+2 [UI]: 2007 year label + M-PESA title card

## CAMERA MOTION
- Type: Pan L->R
- Duration: 45s
- Frame range: 1200–2280

## ELEMENT ANIMATIONS (VO-synced triggers)
  VO word "2007" -> Year label: Slam in scale 1.2->1.0 (frames 60-72)
  VO word "M-Pesa" -> Title card M-PESA: Fade in center-top (frames 120-140)
  VO word "no bank account" -> Flow step 1 phone icon: Slide in from left (frames 300-320)
  VO word "bank branches" -> Flow step 2 agent icon: Slide in (frames 480-500)
  VO word "text message" -> Flow step 3 recipient icon: Slide in (frames 660-680)
  VO word "blueprint" -> Connector arrows: Draw-on animation (frames 960-1000)

## ON-SCREEN TEXT
  "2007" [Stat 96px] at 2.5s
  "M-PESA" [Headline 72px] at 5s
  "Phone -> Agent -> Recipient" [Label 36px staggered] at 12-22s

## ASSETS REQUIRED
  [EXISTS] assets/canva/s2_kiosk_2007.png
  [CREATE] assets/diagrams/s2_mpesa_flow.svg
  [CREATE] assets/icons/icon_phone.svg
  [CREATE] assets/icons/icon_agent.svg

## SFX TRIGGERS
  "M-Pesa" -> brand_sting.wav (? dB)
  "text message" -> keypad_click.wav (? dB)
  "scene" -> street_bustle.wav (-24 dB)

## MUSIC
- Bed: ch01_dawn_pad.wav

## TRANSITION OUT
- Type: slide_wipe
