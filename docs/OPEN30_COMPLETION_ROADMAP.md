# S01 TED-Ed 30s Open — Completion Roadmap

**Authority:** `docs/S01_TEDED_30S_OPEN.md` · `docs/SCENES_LIBRARY_CUTS_ROADMAP.md` (S01 0–720f)

## Pipeline stack

| Layer | Tool | Output |
|-------|------|--------|
| **Graphics** | matplotlib + Canva (Composio) | `assets/canva/kinetic/infographics/open30/*.png` |
| **Stock** | Mixkit + local cuts (`inject_open30_stock_footage.py`) | `open30_stock_cuts/` |
| **Assembly** | ffmpeg beat concat | `s01_teded_open_30s_enhanced.mp4` |
| **Blender motion** | `setup_teded_open30_blender51.py` (CPU Cycles) | `s01_teded_open30_blender51.mp4` optional hero |
| **Episode merge** | `merge_open30_into_s01.py` | `01_ColdOpen_with_open30.mp4` |
| **Resolve edit** | `resolve_open30_timeline.py` + `resolve_pace_kinetic_yb.py` | V3 0–720f on Episode 01 |
| **Full finish** | `finish_after_hq.ps1` | FINAL with VO |

## Canva (Composio — connected)

Polish shells in Canva UI (1920×1080 export):

| Beat | Design ID |
|------|-----------|
| 06:30 Nairobi | `DAHSJzAbXzM` |
| 82.1% stat | `DAHSJ2Y1PC0` |
| Money moved | `DAHSJzxs1ls` |
| Title lockup | `DAHSJwY5FQc` |

After export: drop PNGs into `assets/canva/kinetic/infographics/open30/` and re-run `generate_s01_teded_open30.py`.

Composio API: `CANVA_POST_DESIGNS` + `CANVA_POST_EXPORTS` (account `canva_airway-sasin`).

## Stock beats injected

| Beat | Stock |
|------|-------|
| 01 06:30 | city dawn / aerial |
| 02 MATATUS | city walk |
| 04 PHONE | phone hands |
| 09 SILICON SAVANNAH | skyline clouds |

## Integration rules

1. Open covers **timeline 0–720f only** — VO clock unchanged.
2. **Skip** per-beat kinetic under 720f when open30 on V3 (`resolve_pace_kinetic_yb.py`).
3. **Clear** V3 at Africa whip (~f720) — bare plate reads.
4. Prefer **enhanced** open when present; fallback base `s01_teded_open_30s.mp4`.

## Commands (in order)

```powershell
python scripts/inject_open30_stock_footage.py
python scripts/merge_open30_into_s01.py --open renders/paced_overlays/s01_teded_open_30s_enhanced.mp4
python scripts/resolve_open30_timeline.py          # Resolve open
python scripts/import_open30_resolve.py
# After HQ 10/10:
powershell -File finish_after_hq.ps1
```

## Gate status

| Step | Status |
|------|--------|
| Base open30 MP4 verified (720f / 30s) | ✅ |
| Canva polish exports (4 shells via Composio) | ✅ |
| Stock injection (beats 01/02/04/09) | ✅ `s01_teded_open_30s_enhanced.mp4` |
| S01 stem merge | ✅ `01_ColdOpen_with_open30.mp4` |
| Blender51 sidecar polish | ✅ blend saved; CPU re-render queued |
| Resolve module timeline | ⏳ open Resolve → run scripts |
| Episode FINAL | ⏳ after HQ 10/10 |
