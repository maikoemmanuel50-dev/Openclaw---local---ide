# Real VO intake — required before 4K

**Active stem:** `assets/audio/vo/episode_01_vo.wav`  
**Current:** placeholder bytes (timing lock only)  
**Target:** your recorded performance, **48 kHz** WAV, stereo or mono, **~390 s** aligned to episode script.

## What to send

1. Final WAV file (path or drop into project), e.g.  
   `assets/audio/vo/incoming/episode_01_vo_final.wav`
2. Confirm it replaces the placeholder on **A1** (same edit timing as `docs/teded_scene_spec_ep01.md` / Resolve markers).

## Agent / user steps after file arrives

```powershell
cd "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
python scripts/swap_vo_stem.py "assets\audio\vo\incoming\episode_01_vo_final.wav"
```

This copies to `episode_01_vo.wav`, updates `ACTIVE_VO.txt`, and re-runs `scripts/resolve_fairlight_overnight.py` (Fairlight stems + A1 place).

Then verify loudness per `docs/DELIVERY_STANDARDS.md` (**−14 LUFS** integrated, true peak **≤ −1 dBTP**).

## Gate

PRE-4K row **#1b** — ⏳ **pending your recording**. Picture finish may proceed on placeholder; **4K blocked** until real VO swapped and Fairlight re-verified.
