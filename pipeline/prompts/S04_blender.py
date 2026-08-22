# Blender Visual Prompt — S04: Beat 1: Phone Close-Up
# Chapter: Daylight | Camera: Push-In tight
# Duration: 25s (600 frames @ 24fps)
# Frame range: 3360–3960
# Style: Close-up detail + concept label

## COMPOSITION (Layer Stack)
  Z=-2 [BG]: Soft blur
  Z=-1 [MID]: Hand + phone close-up
  Z=+1 [OVERLAY]: UI highlight boxes
  Z=+2 [UI]: Mobile-First label

## CAMERA MOTION
- Type: Push-In tight
- Duration: 25s
- Frame range: 3360–3960

## ELEMENT ANIMATIONS (VO-synced triggers)
  VO word "phone" -> Phone screen: UI scroll micro-animation thumb drag (frames 60-300)
  VO word "small screen" -> UI highlight boxes: Box draw-on around app elements (frames 180-240)
  VO word "Mobile-First" -> Label: Fade in + slide up (frames 360-380)

## ON-SCREEN TEXT
  "Mobile-First" [Headline 72px] at 15s

## ASSETS REQUIRED
  [EXISTS] assets/canva/s4_phone_hand.png

## SFX TRIGGERS
  "phone" -> ui_swipe.wav (? dB)

## MUSIC
- Bed: ch02_daylight_lofi.wav

## TRANSITION OUT
- Type: cut
