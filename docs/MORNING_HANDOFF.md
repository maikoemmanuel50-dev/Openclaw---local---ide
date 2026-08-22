# Morning handoff — 2026-08-13

## Overnight (while you slept)
- HQ Blender 5.1 batch kept running (GUI closed for GPU)
- Watcher: `wait_hq_assemble.ps1` → `finish_after_hq.ps1` when 10/10 clips ready
- Hourly reports: `docs/HOURLY_PROGRESS.md` + `STATUS_HOURLY_LATEST.txt`
- Resolve picture: V2 YB + V3/V4 kinetic placed; V1 still old `built_clips` until HQ finishes (then auto-copy/relink)
- **Fairlight:** A1–A5 stems laid with documentary EQ baked in

## VO (locked for pipeline — swap anytime)
Active stem: `assets/audio/vo/episode_01_vo.wav` (placeholder bytes OK until final take).

When you have the real take:
1. Overwrite that file (or `python scripts/swap_vo_stem.py path\to\take.wav`)
2. Fairlight UI: A2 sidechain duck from A1 (~-12 dB) if not already set
3. Confirm V1 uses new HQ `built_clips` / `video_clips`
4. Spot-check camera moves + ball `#FFD54F`; protect $984M / 82% / 97% holds

## Camera / surfaces checklist
| Item | Target |
|------|--------|
| Camera F-curves | Bezier ease-in/out (no linear pops) |
| Lenses | Per-scene HQ table (35–50mm) |
| Photoplanes | Cover camera frustum (margin ~1.14) |
| Textures | Principled + Smart filter; no missing maps |
| Color | AgX Medium High Contrast |
| Samples | ≥128 EEVEE TAA + ray tracing |

## Fairlight — 5 minutes when you wake
Open Resolve → **Fairlight** → Episode 01 - Assembly

| Track | Content |
|-------|---------|
| A1 VO | Placeholder EQ'd (swap tomorrow) |
| A2 Music | Chapter beds, -22-ish |
| A3 Ambient | City/street/cowork/solar/drone |
| A4 Punctuation | Whooshes, risers, transitions |
| A5 Stats | Stat hits + release |

**Must do once in UI (API cannot):** A2 Dynamics → Compressor → sidechain from A1 · duck ~-12 dB · attack 100 ms · release 400 ms

Full notes: `templates/resolve/FairlightMix_README.md`  
Stems: `renders/audio_stems/fairlight/`

## Quality note on picture
Active V1 tabs still use pre-HQ `built_clips` — not final quality. Overnight HQ re-render replaces them; do not judge final look from current V1 until relink.

## 4K
Still HOLD (`docs/PRE_4K_GATE.md`) until real VO + HQ + Fairlight polish + FINAL rebuild.

## License-free stock cinematic (overnight)
- 29 Mixkit + Unsplash cuts, soft-pop graded, CRF 17, cinematic pans 10-16f
- Inserts only � timeline still ~10081f (~7:00 @ 24fps)
- Resolve folder Stock Cinematic on V3/V4; assets in assets/stock/license_free/
- Rebuild: python scripts/ingest_license_free_stock_cinematic.py
