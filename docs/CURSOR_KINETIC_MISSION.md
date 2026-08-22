# Cursor IDE Mission — Kinetic B-Roll Edit (Africa S1)

**Command center:** Cursor IDE (this chat / Agent mode)  
**Workspace:** `C:\Users\HP\OneDrive\The Vault\Africa Season 1`  
**Apps under Cursor control:** Blender (CLI scripts) · DaVinci Resolve (MCP) · Canva (Composio MCP) · FFmpeg

---

## Mission

Build a **fast-paced, kinetic, B-roll-driven** picture cut for Episode 01 *Silicon Savannah*, while keeping the **yellow ball as the only hero**.

Read first:
- `docs/kinetic_broll_edit.md`
- `docs/yellow_ball_throughline.md`
- `docs/dynamic_vibrant_tricks.md`
- `docs/nvidia_gpu_workflow.md`

---

## Cursor agent task order

### 1. Stock / synthetic B-roll
- Prefer local heroes + Ken Burns kinetic pulses (`assemble_kinetic_preview.py`)
- Optional: Canva MCP stock / `assets/download_kinetic_broll.py` when CDNs allow
- Output folder: `assets/stock/kinetic/` and/or `renders/kinetic_build/`

### 2. Blender kinetic takes
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b "blend\africa_s1_master_v01.blend" -P "setup_nvidia_gpu.py"
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b "blend\africa_s1_master_v01.blend" -P "render_kinetic_broll.py"
```
Output: `renders/kinetic_broll/`  
One heavy GPU job at a time (don’t Deliver in Resolve simultaneously).

### 3. Resolve editorial (MCP)
- Project: `Africa Season 1`
- Create/use timeline: **Episode 01 - Kinetic**
- Tracks: V1 spine · V2 yellow ball · V3/V4 B-roll · V5 TextStat
- VO-first; ASL ~0.4–1.0s on B-roll; protect stats (36–60f holds)
- Markers per `resolve_spec.yaml` → `Episode 01 - Kinetic`

### 4. Preview assemble
```powershell
python assemble_kinetic_preview.py
```
→ `Africa_S1_Silicon_Savannah_KINETIC_preview.mp4`

### 5. Fairlight
Cut ticks / whooshes ±2f on montage clusters; music energy curve from `docs/audio_design_map.yaml`.

---

## Do NOT
- Use Google Antigravity IDE for this project
- Add acting characters
- Use 1s black fades between chapters
- Fight $984M / 82% / 97% with dense B-roll

---

## Success check

- [ ] Kinetic preview mp4 exists and feels fast on mute
- [ ] Resolve Kinetic timeline track layout in place
- [ ] Yellow ball remains hero on V2
- [ ] ASL ≤ 1.0s in S01, S03, S04, S06, S09
