# Blender Visual Prompt — S03: Beat 1: The Hubs
# Chapter: Daylight | Camera: Parallax Drift L->R
# Duration: 45s (1080 frames @ 24fps)
# Frame range: 2280–3360
# Style: 3-factor enumeration

## COMPOSITION (Layer Stack)
  Z=-2 [BG]: Co-working interior
  Z=-1 [MID]: Desks, laptops, whiteboards
  Z=+0 [FG]: Plants, foreground desk edge
  Z=+1 [OVERLAY]: Hub cards
  Z=+2 [UI]: Card labels (iHub, Andela, NaiLab)

## CAMERA MOTION
- Type: Parallax Drift L->R
- Duration: 45s
- Frame range: 2280–3360

## ELEMENT ANIMATIONS (VO-synced triggers)
  VO word "iHub" -> Card 1 iHub 2010: Stagger slide-in delay 0 (frames 240-260)
  VO word "Andela" -> Card 2 Andela: Stagger slide-in delay 12f (frames 540-560)
  VO word "NaiLab" -> Card 3 NaiLab: Stagger slide-in delay 24f (frames 720-740)
  VO word "desks" -> Laptop screens: Screen flicker loop (frames continuous)
  VO word "whiteboards" -> Whiteboard lines: Draw-on (frames 400-480)

## ON-SCREEN TEXT
  "iHub 2010" [Label 36px] at 10s
  "Andela" [Label 36px] at 22s
  "NaiLab" [Label 36px] at 30s

## ASSETS REQUIRED
  [EXISTS] assets/canva/s3_coworking.png
  [CREATE] assets/diagrams/s3_hub_cards.svg

## SFX TRIGGERS
  "scene" -> coworking_chatter.wav (-24 dB)
  "desks" -> keyboard_clack.wav (-20 dB)

## MUSIC
- Bed: ch02_daylight_lofi.wav

## TRANSITION OUT
- Type: color_hold
