# Africa Season 1 — Delivery Standards

Quantifiable targets for every episode delivered from this project. These are **hard numbers**, not style guidance — **verify against them** before marking a render or export “done” in `PRODUCTION_STATUS.md`.

**Related:** `.cursor/rules/africa-s1-delivery-standards.mdc` · `docs/PRE_4K_GATE.md` · `docs/FIDELITY_EXECUTION_GUIDE.md` · `.cursor/rules/africa-s1-agent-rules.mdc`

**Pipeline hooks (current phase):**
- Scene plates: Blender 5.1 → 1920×1080 @ project fps (24) via `render_scenes_mp4.py`
- Archive assemble: `assemble_final_video.py` → CRF 14 H.264 High + Rec.709 tags + GOP 12
- YouTube sibling: same script writes `*_YT1080.mp4` ~**10 Mbps** 2-pass VBR
- FINAL mux: `assemble_with_audio.py` → AAC-LC **320 kbps** / **48 kHz** stereo (loudness −14 LUFS still Fairlight/ffmpeg grade step)

---

## Video (current SDR / non-4K phase)

| Parameter | Target |
|-----------|--------|
| **Resolution** | **1920×1080** minimum. Never upscale from a lower native render to fake this. |
| **Frame rate** | Match the Blender project’s native fps **exactly**, end to end (Blender → Resolve → export). Do **not** conform 24↔30 at any stage — it inflates file size ~25% with no quality gain, and mismatched source/output frame rates get penalized by YouTube’s encoder. |
| **Codec / container** | H.264, **High Profile**, MP4 container, **closed GOP at half the frame rate**. |
| **Bitrate** | **8–12 Mbps** for 1080p, VBR (**2-pass**). Use the top of the range for high-motion kinetic/stock-heavy scenes. |
| **Chroma / bit depth** | 4:2:0, **8-bit** minimum (SDR — no HDR/10-bit requirement at this phase). |
| **Color space** | **Rec. 709**. |

---

## Audio

| Parameter | Target |
|-----------|--------|
| **Sample rate** | **48 kHz** |
| **Codec** | **AAC-LC** |
| **Bitrate** | **320–384 kbps**, stereo |
| **Loudness** | **−14 LUFS** integrated |
| **True peak** | **≤ −1 dBTP** |

YouTube turns down audio louder than −14 LUFS but does **not** boost quiet audio — **undershooting the target is worse than overshooting it**.

---

## Safe margins

| Zone | Margin |
|------|--------|
| **Title-safe** (text, key graphics) | Keep inside the center **80%** of frame (10% margin on all sides). |
| **Action-safe** (non-critical action) | Keep inside the center **90%** of frame. |
| **Caption / lower-third exclusion** | Avoid the bottom **~15%** of frame for primary content — captions and progress bar. |
| **Watermark exclusion** | Avoid the top-right **~15%** corner for anything essential — channel watermark / subscribe prompt. |

---

## Pipeline consistency (internal, before export)

| Check | Requirement |
|-------|-------------|
| **Canva exports** | Must match project resolution (**1920×1080**) exactly at export time — no upscaling on ingest into Resolve. |
| **Frame rate at every stage** | Blender render, Canva export, Resolve timeline, and final export must all share **one** fps value. Confirm **before** assembly, not after. |
| **Master file** | Keep an uncompressed / high-bitrate **master** before the YouTube-spec export — the export settings above are a **delivery** format, not the archive copy. |

---

## Out of scope until PRE_4K_GATE closes

**4K**, **HDR**, and **Rec. 2020** targets do **not** apply yet. Don’t substitute 4K bitrate/resolution numbers into current-phase work — see `docs/PRE_4K_GATE.md`.

---

## Verification checklist (before “done”)

- [ ] `ffprobe`: 1920×1080, fps = project native (expected **24**), yuv420p  
- [ ] Video: H.264 High, ~8–12 Mbps (or master retained separately at higher rate)  
- [ ] Audio (if present): 48 kHz AAC-LC, 320–384 kbps stereo  
- [ ] Loudness: ≈ −14 LUFS, true peak ≤ −1 dBTP  
- [ ] Duration matches scene/episode target; file plays  
- [ ] TextStat / titles inside title-safe; critical action inside action-safe  

*Stamp results into `PRODUCTION_STATUS.md` when verified — launching a job is not verification.*
