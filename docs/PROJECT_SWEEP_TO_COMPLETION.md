# Project Sweep → Path to Completion

**Probed:** 2026-08-13 ~22:40  
**Episode:** Silicon Savannah (Africa Season 1)  
**Authority:** `PRODUCTION_STATUS.md` · `docs/PRE_4K_GATE.md` · `docs/COPYRIGHT_CLEARANCE.md`

---

## 1. Sweep verdict

| Axis | State |
|------|--------|
| Picture spine (V1) | **2/10** HQ clips playable (S01–S02). S03–S10 missing MP4s; S03 PNG masters **resuming frame 11→1080** |
| Kinetic / open30 | ✅ 84 placements, open30 on V3 0–720; YB waived |
| Fairlight A1–A5 | ✅ Rebuilt + A2 **tension/release bake** placed (`docs/AUDIO_MIX_STANDARDS.md`) |
| Copyright | ✅ Netflix bak + Safaricom mark art **quarantined**; allowlist updated |
| 4K | 🚫 HOLD until gate clears |
| GPU | One Blender **-b** HQ job; GUI preview stopped (was competing) |

---

## 2. Copyright actions (this pass)

**Moved to** `assets/_quarantine_copyright/` (not for FINAL / pace):

- `s10_africa_logo_netflix_bak.png`
- `inf_s04_safaricom_4g_bars.png`
- `x_s01_safaricom_share_chip.png`

**Cleared stacks (unchanged policy):** Mixkit · Unsplash · Poly Haven CC0 · project Blender · procedural music/SFX (`assets/audio/generate_*.py`) · Canva exports (user commercial entitlement).

**Policy files:** `docs/COPYRIGHT_CLEARANCE.md` · `docs/ATTRIBUTIONS.md` · `docs/CLEARANCE_ALLOWLIST.json` (now excludes `safaricom` / netflix).

Before public upload: confirm Canva plan allows commercial use; keep YouTube credit line per ATTRIBUTIONS.

---

## 3. Workflow load (remainder)

| Workstream | Effort | Blocker |
|------------|--------|---------|
| **HQ Cycles S03–S10** | Dominant — ~3–4k frames left @ **128** samples OptiX | GPU time / power |
| Watcher → merge_motion → finish_after_hq | Auto when **10/10** clips | HQ |
| Resolve V1 relink | Short | After HQ MP4s |
| Fairlight grade polish | Short | Picture lock |
| FINAL export (−14 LUFS) | Short | After relink + mix |
| Real VO swap | User | `docs/VO_INTAKE.md` |
| Meshy S07 giraffe | User asset | Gate #9 |
| Blender51 open30 CPU sidecar | Medium CPU | After GPU free |
| 4K | Blocked | Gate |

**ETA (order-of-magnitude @128 samples):** S03 alone ~1070 frames × ~1–2 min ≈ **18–36 h**, then S04–S10 similar — plan multi-day render with PNG resume (power-safe). Do **not** restart from frame 0.

---

## 4. Path to completion (ordered)

1. **Keep HQ running** — `scripts/resume_hq_s03_s10.ps1` · PNG resume in `render_scenes_mp4.py` · watcher `wait_hq_assemble.ps1`.
2. **No second GPU job** (no Resolve Deliver / GUI Cycles) until HQ idle.
3. At **10/10** clips: watcher runs merge_motion → finish_after_hq (FINAL assemble path).
4. **Resolve:** V1 relink new plates · spot-check V3/V4 (no quarantine names) · Fairlight listen pass.
5. **Verify delivery** vs `docs/DELIVERY_STANDARDS.md` (1080p, fps, AAC, −14 LUFS).
6. User: real VO via `swap_vo_stem.py` when ready; Meshy S07 when GLB lands.
7. Optional: open30 Blender51 CPU sidecar when GPU free.
8. Only then clear `PRE_4K_GATE` / remove 4K HOLD.

---

## 5. Re-implemented this session

- Fairlight overnight + `bake_a2_tension_release.py` (completed)
- Copyright quarantine + allowlist
- PNG **resume-from-missing** in `render_scenes_mp4.py`
- HQ redeploy @ **128** samples from frame **11** (kept frames 1–10)
- Freed GPU (killed preview `.blend`)
- Watcher confirmed alive

---

## 6. Definition of “episode complete” (SDR)

Playable `Africa_S1_Silicon_Savannah_FINAL.mp4` with HQ V1, kinetic density, Fairlight mix to standards, copyright-clean timeline, delivery numbers verified — **4K still gated**.
