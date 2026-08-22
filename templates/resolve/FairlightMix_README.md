# Fairlight Mix — Overnight Documentary Layout (TED-Ed / Vox / Bloomberg / WSJ)

**Timeline:** Episode 01 - Assembly  
**Stems:** `renders/audio_stems/fairlight/`  
**Script:** `scripts/resolve_fairlight_overnight.py`

## Why stems are pre-EQ'd
Resolve's public scripting API **cannot** edit Fairlight plugin graphs (Track EQ, Dynamics curves).  
So EQ matching documentary practice is **baked into stems**, then tracks are leveled in Fairlight.  
You still use Fairlight for: sidechain ducking, final EQ taste, bus compression, deliver.

## Track map

| Track | Name | Stem | Target | Role |
|-------|------|------|--------|------|
| A1 | VO | `A1_vo_eq.wav` | 0 dBFS | Narration spine (placeholder until real VO) |
| A2 | Music | `A2_music_eq.wav` | -22 dBFS | Chapter beds, ducked under VO |
| A3 | Ambient | `A3_ambient_eq.wav` | -24 dBFS | City / street / cowork / solar / drone |
| A4 | Punctuation | `A4_punctuation_eq.wav` | -18 dBFS | Whooshes, risers, UI, transitions |
| A5 | Stats | `A5_stats_eq.wav` | -14 dBFS | Stat slams + release hits |

## Baked EQ (documentary)
- **VO:** HPF 100 Hz · cut mud 200 Hz · presence +2.5 dB @ 3 kHz · air +1 dB @ 7.5 kHz · loudnorm ~-16 LUFS
- **Music:** HPF 80 Hz · cut 250 Hz · gentle -1.5 dB @ 4 kHz (leave VO pocket) · loudnorm ~-22 LUFS
- **Ambient:** HPF 120 · LPF 6 kHz · soft mid dip (bed under VO)
- **Punctuation:** HPF 150 · slight sparkle @ 5 kHz
- **Stats:** weight @ 120 Hz + presence @ 2 kHz

## Fairlight UI — do this in the morning (5 min)
1. Open **Fairlight** page on Episode 01.
2. Select **A2 Music** → Dynamics → Compressor → **Sidechain** from **A1 VO**  
   - Ratio ~4:1 · Threshold so duck ≈ **-12 dB** under speech · Attack **100 ms** · Release **400 ms**
3. Optional Track EQ polish: A1 slight de-ess if harsh; A2 extra dip 2–4 kHz while VO speaks.
4. Bus: light master limiter TP **-1.0 dB**.
5. When real VO arrives: replace A1 with `assets/audio/vo/episode_01_vo.wav`, re-run stem script or slip A1, re-check duck.

## References (study → execute)
- TED-Ed explainer beds: sparse beds, hard cut whooshes, silence before big reveals
- Vox: ambient beds always under VO; whoosh on picture cuts
- Bloomberg QuickTake / WSJ: data riser → impact hit → hold
- Blackmagic: Fairlight audio fundamentals / sidechain compressor docs in Resolve manual

## Blender note
Keep **picture** in Blender (5.1); keep **mix** in Fairlight. Blender VSE is not the mix bus for this episode.

## Automated rebuild
```
python assets/audio/generate_tension_release_sfx.py
python scripts/resolve_fairlight_overnight.py
```
Also: `python assemble_with_audio.py` writes a muxed preview FINAL (ffmpeg) — Fairlight remains source of truth for delivery mix.
