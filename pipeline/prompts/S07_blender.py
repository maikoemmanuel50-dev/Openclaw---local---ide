# Blender Visual Prompt — S07: Beat 3: The Gap
# Chapter: CoolTension | Camera: Custom zoom-out
# Duration: 50s (1200 frames @ 24fps)
# Frame range: 6000–7200
# Style: Map reveal + stat slam

## COMPOSITION (Layer Stack)
  Z=-2 [BG]: High-contrast Kenya map dark muted
  Z=-1 [MID]: Nairobi glowing beacon pulsing
  Z=+1 [OVERLAY]: Dim markers Mombasa Kisumu Eldoret Nakuru
  Z=+2 [UI]: 97% stat callout

## CAMERA MOTION
- Type: Custom zoom-out
- Duration: 50s
- Frame range: 6000–7200

## ELEMENT ANIMATIONS (VO-synced triggers)
  VO word "Nairobi" -> Beacon pulse: Glow pulse intensity cycle (frames 60-300)
  VO word "Mombasa Kisumu" -> Dim city markers: Sequential fade-in muted (frames 360-540)
  VO word "ninety-seven percent" -> 97% callout: Slam in + hold 36f (frames 720-780)
  VO word "funding" -> Funding trail lines: Draw-on from Nairobi to cities (frames 900-1080)

## ON-SCREEN TEXT
  "97%" [Stat 96px] at 30s

## ASSETS REQUIRED
  [CREATE] assets/maps/kenya_map_hi_contrast.svg

## SFX TRIGGERS
  "scene" -> drone_ambient.wav (-26 dB)
  "ninety-seven percent" -> stat_impact.wav (-14 dB)

## MUSIC
- Bed: ch04_cooltension_drone.wav

## TRANSITION OUT
- Type: parallax_drift
