# Africa S1 — Fairlight Audio Excellence Pack

Industry-grade documentary VO + bed mix for Episode 01.  
Complements: `docs/FAIRLIGHT_A2_SIDECHAIN.md` · baked duck on `A2_music_eq_ducked.wav`.

## Target mix (YouTube / web documentary)

| Bus | Role | Target |
|-----|------|--------|
| A1 VO | Lead | ~**−16 LUFS** integrated (stem loudnorm); peaks under **−1.5 dBTP** |
| A2 Music | Bed | Sit **~−12 dB** under VO when speaking (baked sidechain) |
| A3 Ambient | Air | −24 dB class trim; HPF so it doesn’t mud VO |
| A4 Punctuation | Hits | Short; never mask consonants |
| A5 Stats | Accents | Brief impacts under VO pauses |

## Processing chain we enforce (baked + Fairlight)

**VO (A1)** — TED-Ed / Vox / Bloomberg clarity path  
1. Clip gain into a sane range  
2. **HPF ~80–100 Hz** (kill rumble)  
3. Cut boxiness **~250–400 Hz** before boosting  
4. Light presence **~2.5–4 kHz** only if needed  
5. Gentle compression (not squash)  
6. De-ess if harsh S’s  
7. Loudness normalize to delivery target  

**Music (A2)**  
1. Soft HPF  
2. **Scoop ~2–4 kHz** so VO consonants have a pocket  
3. Sidechain / Ducker / baked `sidechaincompress` ≈ **−12 dB** under VO  
4. Attack fast enough for consonants; release **120–250 ms** (no pump)

## Online tutorials & how-tos (bookmark)

| Resource | Use for |
|----------|---------|
| [Fairlight Audio Guide (Resolve Club)](https://davinciresolveclub.com/davinci-resolve-fairlight-audio/) | Full workflow: clip gain → HPF → EQ → dynamics → loudness |
| [Fairlight Pro Editing & Mixing Guide 2026 (Pixflow)](https://pixflow.net/blog/davinci-resolve-fairlight-audio-guide/) | Mixer, cut-before-boost EQ, Chain FX (Resolve 20+) |
| [Automatic ducking & Foley (Cutsio)](https://cutsio.com/blog/davinci-resolve-fairlight-automatic-ducking-foley) | Track FX **Ducker**: −6…−12 dB, recovery, threshold |
| [Larry Jordan — Duck music under dialog](https://larryjordan.com/articles/automatically-duck-background-music-under-dialog-in-davinci-resolve/) | Sidechain compressor Source = dialog; ratio 3:1–5:1 |
| [Sidechaining Made Easy — Resolve 19 (YouTube)](https://www.youtube.com/watch?v=8hlzCGD-dSM) | Visual sidechain routing walkthrough |

## Fairlight FX / plugins to prefer (stock first)

Use **Fairlight FX** before third-party (keeps project portable):

| Need | Fairlight FX / tool |
|------|---------------------|
| Dialogue cleanup | Noise Reduction, Dialogue Processor (Studio where available) |
| Level evening | Dialogue Leveler / Dynamics compressor |
| Harsh S | De-Esser |
| Music under VO | **Ducker** track FX **or** Dynamics sidechain |
| Surgical EQ | Track EQ or Fairlight FX EQ |
| Limiting | Soft limiter on bus before deliver |

Optional third-party (only if already licensed): iZotope RX Dialogue Isolate, Waves NS1, FabFilter Pro-Q — **not required** for this episode.

## Already executed in this project

- EQ-baked stems: `renders/audio_stems/fairlight/A1_vo_eq.wav` … `A5_*.wav`  
- **A2 ducked stem on timeline:** `A2_music_eq_ducked.wav` (ffmpeg sidechaincompress; API can’t set Fairlight graphs)  
- Backup unducked: `A2_music_eq_pre_sidechain.bak.wav`  
- Script: `scripts/bake_a2_sidechain_duck.py` · overnight place: `scripts/resolve_fairlight_overnight.py`

## Morning audio QA (after HQ)

1. Solo A1+A2 — VO readable, duck natural  
2. Full mix — SFX don’t mask VO  
3. Loudness meter on Fairlight: aim ~−14 to −16 LUFS for YouTube doc  
4. If final VO arrives: `python scripts/swap_vo_stem.py` then re-bake A2 duck  

## Do not overnight

- Deliver / 4K while HQ Blender is running  
- Add heavy Studio AI Voice Isolation during HQ (GPU contention)
