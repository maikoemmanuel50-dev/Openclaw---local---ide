# Resume after power loss — Africa S1

**Updated:** 2026-08-13 ~23:10 EAT  
**Project:** `C:\Users\HP\OneDrive\The Vault\Africa Season 1`

## Automatic safeguards (armed)

| Safeguard | How |
|-----------|-----|
| **PNG masters** | HQ writes `renders/video_clips/masters/<scene>/frame_####.png` — survive hard power cuts |
| **Resume from missing frame** | `render_scenes_mp4.py` → `next_missing_frame()` — never wipe prior PNGs unless `AFRICA_FORCE_RERENDER=1` |
| **Auto-resume on logon** | `STARTUP_AUTO_RESUME.cmd` in Windows **Startup** folder + Scheduled Task `AfricaS1_PowerAutoResume` |
| **Orchestrator** | `scripts/power_outage_auto_resume.ps1` — quarantine bad MP4s, write checkpoint, start HQ + watcher if needed |
| **HQ launcher** | `scripts/resume_hq_s03_s10.ps1` — S03–S10 only @64 samples, skips S01/S02 |
| **Watcher** | `wait_hq_assemble.ps1` → merge + `finish_after_hq.ps1` at 10/10 |
| **Checkpoint file** | `STATUS_POWER_CHECKPOINT.txt` (mp4 ready + png counts) |

### After power returns

1. Sign into Windows (task + Startup run automatically).  
2. Or manually:
```powershell
cd "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
powershell -File scripts\power_outage_auto_resume.ps1
```
3. Plug into AC before expecting full GPU speed.  
4. Confirm: `STATUS_POWER_CHECKPOINT.txt`, Blender `-b` process, `wait_hq_assemble_log.txt`.

### Do not

- Delete `renders/video_clips/masters/`  
- Set `AFRICA_FORCE_RERENDER=1`  
- Start a second Blender/Resolve Deliver job while HQ is running  
- Trust mid-write `.mp4` without `ffprobe` (auto-resume quarantines them)

---

## Verified after outage (2026-08-13 19:15)

| Asset | Status |
|-------|--------|
| S01 `01_ColdOpen.mp4` | ✅ 1200f / 50s playable |
| S01 + open `01_ColdOpen_with_open30.mp4` | ✅ 1200f / 50s |
| S02 `02_Context2007.mp4` | ✅ 1080f / 45s |
| Enhanced open 30s | ✅ 720f / 30s |
| Partial stem | ✅ 2280f / 95s (S01–S03 concat — S03 portion may be truncated) |
| Fairlight stems | ✅ WAV files present |
| S03 `03_Beat1_Hubs.mp4` | ❌ **corrupt** (moov missing — killed mid-write ~702/1080) |
| Blender51 sidecar MP4 | ❌ **corrupt** (killed ~587/720) |
| Blender / Resolve | Not running after boot |

## Safe on disk (verified before shutdown)

| Asset | Path | Notes |
|-------|------|-------|
| Enhanced 30s open | `renders/paced_overlays/s01_teded_open_30s_enhanced.mp4` | 720f / 30s |
| S01 + open merge | `renders/video_clips/01_ColdOpen_with_open30.mp4` | ~40 MB |
| Base open + manifest | `s01_teded_open_30s.mp4`, `renders/quality/s01_teded_open30_manifest.json` | |
| Partial episode stem | `renders/quality/episode_stem_partial.mp4` | 3 scenes (S01–S03) |
| Built clips mirror | `renders/built_clips/01–03_*.mp4` | For Resolve V1 |
| Fairlight stems | `renders/audio_stems/fairlight/` | Built offline |
| Blends | `blend/africa_s1_master_v01.blend`, `blend/africa_s1_teded_open30.blend` | Master saved |

## May be incomplete / corrupt after hard shutdown

| Item | Action on resume |
|------|------------------|
| `s01_teded_open30_blender51.mp4` | **Delete if unplayable**, re-render CPU only (see below) |
| HQ `renders/video_clips/04–10_*.mp4` | Check frame/size; **do not restart completed scenes from frame 0** |
| In-flight HQ scene | Resume or continue batch — inspect `sasa_hq_rerender_log.txt` |

## HQ batch rules (do not violate)

1. **One GPU job at a time** — Blender **or** Resolve Deliver.
2. **Never restart an in-progress HQ render from frame 0** unless user explicitly requests engine switch.
3. **4K HOLD** until `docs/PRE_4K_GATE.md` closes.

## Resume order

### 1. Power / HP Victus
- Plug in, confirm charging (check MyHP / OMEN — disable 80% battery cap if needed).
- OneDrive sync: wait until project folder shows synced if you use cloud backup.

### 2. Check HQ progress
```powershell
cd "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
Get-ChildItem renders\video_clips\*.mp4 | Where-Object Length -gt 200KB
Get-Content sasa_hq_rerender_log.txt -Tail 5 -ErrorAction SilentlyContinue
```
If **10/10** clips ready → `powershell -File wait_hq_assemble.ps1` (or `finish_after_hq.ps1` if watcher already finished).

**S03 is corrupt after this outage.** Rename it, then relaunch **S03–S10 only** (S01/S02 are playable — do not restart them from frame 0):

```powershell
cd "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
Rename-Item "renders\video_clips\03_Beat1_Hubs.mp4" "03_Beat1_Hubs_CORRUPT_outage.mp4" -ErrorAction SilentlyContinue
$env:AFRICA_ONLY_SCENES='03_Beat1_Hubs,04_Beat1_Phone,05_Beat2_Money,06_Beat2_Solar,07_Beat3_Gap,08_Beat3_SecondaryCity,09_Closer,10_EndCard'
# Prefer PNG masters (survives next outage): AFRICA_MASTER_FRAMES=1
# See docs/RENDER_QUALITY_FIX.md — start only when charging
```

### 3. Blender51 open30 sidecar (optional, CPU only)
Only when **no GPU HQ job** running:
```powershell
$env:CUDA_VISIBLE_DEVICES='-1'
Remove-Item "renders\paced_overlays\s01_teded_open30_blender51.mp4" -ErrorAction SilentlyContinue
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b "blend\africa_s1_teded_open30.blend" -P "render_open30_blender51_cpu.py"
```

### 4. Resolve deliverables
1. Open Resolve → open project **Africa S1 - Silicon Savannah**.
2. **Workspace → Scripts → `resolve_bridge`** (once per session).
3. Tell Cursor **"bridge is up"** OR run **Workspace → Scripts → Utility → `AfricaS1_RunDeliverables`**.

Guide: `docs/RESOLVE_MCP_CONNECT.md`

### 5. Open30 already in pipeline
No rebuild needed unless you change Canva PNGs:
```powershell
python scripts/inject_open30_stock_footage.py
python scripts/merge_open30_into_s01.py
```

## Outage-safe operating rules (near-term)

1. **Charge first.** Victus was discharging at ~47% while plugged in (Battery Care / thermal). Confirm the battery icon says **Charging** before GPU work.
2. **One scene at a time** if more cuts are likely — finish S03, save, then start S04.
3. **PNG masters** (`AFRICA_MASTER_FRAMES=1`) survive a hard power cut; ffmpeg mux at the end. Direct H.264 MP4 (S03, blender51 sidecar) dies without a moov atom.
4. **Do not** run HQ Blender + Resolve Deliver + CPU sidecar together.
5. **Checkpoint after each scene:** ffprobe the new MP4; if `moov atom not found`, rename it and re-render that scene only.
6. **Resolve:** open project → **Workspace → Scripts → `resolve_bridge`** only when you have a stable session.
7. **4K HOLD.** Optional sidecar only on CPU with `CUDA_VISIBLE_DEVICES=-1` and **no** HQ GPU job.

## Last known progress (~17:00; verified 19:15)

- **HQ clips:** 3/10 (S01, S02, S03 on disk)
- **Open30 CPU render:** ~587/720 (may need restart — sidecar optional)
- **Resolve MCP bridge:** not listening (port 49632) — run `resolve_bridge` in Resolve
- **Hourly Telegram loop:** stopped (user aborted)

## Authority docs

- `PRODUCTION_STATUS.md`
- `docs/OPEN30_COMPLETION_ROADMAP.md`
- `docs/PRE_4K_GATE.md`
- `finish_after_hq.ps1` / `wait_hq_assemble.ps1`
