# Blender Visual Prompt — S05: Beat 2: The Money
# Chapter: DarkData | Camera: Push-In
# Duration: 45s (1080 frames @ 24fps)
# Frame range: 3960–5040
# Style: Data viz + animated bars + stat counter

## COMPOSITION (Layer Stack)
  Z=-2 [BG]: Dark charcoal #1A1A2E
  Z=-1 [MID]: Geometry Nodes bar chart (4 sectors)
  Z=+1 [OVERLAY]: Sector labels, stat callouts
  Z=+2 [UI]: $984M counter + 82% glow

## CAMERA MOTION
- Type: Push-In
- Duration: 45s
- Frame range: 3960–5040

## ELEMENT ANIMATIONS (VO-synced triggers)
  VO word "measurable" -> Chart frame: Fade in chart outline (frames 60-80)
  VO word "a billion dollars" -> $984M counter: Count up 0->984 (frames 180-240)
  VO word "Fintech" -> Fintech bar + label: Bar rises label fades in (frames 360-400)
  VO word "Climate/Energy" -> Climate bar + label: Bar rises tallest neon glow (frames 540-600)
  VO word "eighty-two percent" -> 82% callout: Slam in center pulse glow (frames 780-840)
  VO word "E-commerce Logistics" -> Remaining bars: Rise sequentially (frames 420-520)

## ON-SCREEN TEXT
  "$984M" [Stat 96px neon green] at 7.5s
  "Fintech" [Label 36px] at 15s
  "Climate/Energy" [Label 36px] at 22s
  "82%" [Stat 96px accent] at 32s

## ASSETS REQUIRED
  [EXISTS] blend/africa_s1_master_v01.blend Scene 05
  [CREATE] Blender text objects / Resolve overlay for sector labels

## SFX TRIGGERS
  "bar growth" -> chart_riser.wav (? dB)
  "$984M" -> stat_ping.wav (? dB)
  "eighty-two percent" -> stat_impact.wav (? dB)

## MUSIC
- Bed: ch03_darkdata_electronic.wav

## TRANSITION OUT
- Type: morph
