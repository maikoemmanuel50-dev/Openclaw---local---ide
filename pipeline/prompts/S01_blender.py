# Blender Visual Prompt — S01: Cold Open
# Chapter: Dawn | Camera: Push-In
# Duration: 50s (1200 frames @ 24fps)
# Frame range: 0–1200
# Style: Hook + abstract overlay

## COMPOSITION (Layer Stack)
  Z=-2 [BG]: Dawn gradient sky (warm orange-purple)
  Z=-1 [MID]: CBD tower silhouettes (UAP Tower, Times Tower)
  Z=+0 [FG]: Matatu + motorbike silhouettes
  Z=+1 [OVERLAY]: Digital transaction paths
  Z=+2 [UI]: Nairobi location label + Silicon Savannah title

## CAMERA MOTION
- Type: Push-In
- Duration: 50s
- Frame range: 0–1200

## ELEMENT ANIMATIONS (VO-synced triggers)
  VO word "Nairobi" -> Location label: Fade in + slide up (frames 72-80)
  VO word "matatus" -> Matatu silhouettes: Subtle bounce 2px Y (frames 180-200)
  VO word "pockets" -> Transaction paths overlay: Fade in 0->0.7 opacity, paths animate L->R (frames 360-480)
  VO word "money has already moved" -> Path pulse: Glow pulse on path nodes (frames 540-600)
  VO word "phone" -> Path convergence: Lines converge to phone icon (frames 720-780)
  VO word "Silicon Savannah" -> Subtitle label: Fade in below Nairobi (frames 1140-1200)

## ON-SCREEN TEXT
  "Nairobi" [Label 36px] at 3s
  "Silicon Savannah" [Headline 72px] at 47s

## ASSETS REQUIRED
  [EXISTS] assets/canva/s1_dawn_skyline.png
  [EXISTS] assets/canva/s1_matatu_silhouettes.png
  [CREATE] assets/diagrams/s1_digital_paths.svg

## SFX TRIGGERS
  "matatus" -> matatu_horn.wav (-18 dB)
  "money has already moved" -> transaction_chime.wav (-18 dB)
  "scene_start" -> city_morning_ambient.wav (-24 dB)

## MUSIC
- Bed: ch01_dawn_pad.wav

## TRANSITION OUT
- Type: cut
