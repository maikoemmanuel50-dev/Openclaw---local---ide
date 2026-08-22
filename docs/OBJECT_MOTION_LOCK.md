# Object motion lock — Option D (Blender-native)

**Policy:** Prefer Blender Geometry Nodes + Graph Editor motion over Meshy.  
**Meshy Free (browser only):** optional S07 giraffe GLB if credits allow — see `renders/quality/meshy_free_optional_queue.json`.  
**Binary:** Blender **5.1.2** only · **never** save into master while HQ `-b` is running.

## Apply (HQ-safe)

```powershell
Copy-Item blend\africa_s1_master_v01.blend blend\africa_s1_object_motion_preview.blend -Force
$env:CUDA_VISIBLE_DEVICES = "-1"
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" `
  -b blend\africa_s1_object_motion_preview.blend -P setup_object_motion_all_scenes.py
```

Output: `blend/africa_s1_object_motion_preview.blend`  
Report: `renders/quality/object_motion_lock_report.json`

After HQ **10/10**, automated via `merge_motion_after_hq.ps1` (called from `wait_hq_assemble.ps1`):

1. Wait for HQ `-b` batch to exit (never overlap GPU jobs).
2. Backup master → `blend/africa_s1_master_v01_pre_motion_*.blend`
3. Re-run this script with `AFRICA_OUT_BLEND=blend/africa_s1_master_v01.blend`
4. Re-render all 10 scenes (`render_scenes_mp4.py`) — motion baked into plates
5. `finish_after_hq.ps1` — assemble, import unique kinetic assets, Resolve V3/V4, Fairlight

Manual merge (if needed):

```powershell
$env:AFRICA_OUT_BLEND = "C:\Users\HP\OneDrive\The Vault\Africa Season 1\blend\africa_s1_master_v01.blend"
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b blend\africa_s1_master_v01.blend -P setup_object_motion_all_scenes.py
```

## What the script wires

| System | Implementation |
|--------|----------------|
| **GN_WindSway** | Scene Time → Noise W · Position → Noise · Map Range → Offset → **Set Position** (17 links verified) |
| **Rotation sway** | Mid/FG Z rotation keys, **BEZIER** auto-clamped (Ryan King / CG Geek) |
| **Emission pulse** | Principled Emission Strength keys (Arch Comm IV PBR) — S05 bars, S06 solar |
| **Walker** | `MOTION_Walker_S07` soft-gold faceless block walk L→R mid-scene |
| **Camera** | Existing push/pan **dampened** (objects carry life) |
| **Add-ons** | `node_wrangler`, `io_scene_gltf2`, Cycles |
| **Collections** | `ENV` · `MODEL_ADDITIONS` (Arch Comm IV) |

## Tutorials / class materials baked in

- Telegram Arch Comm IV Class 01–16 → `docs/ARCH_COMM_IV_LOCK.md` · `docs/BLENDER_RIG_ANIM_RESOURCES.md`
- [Ryan King — Animation for Beginners](https://youtu.be/CBJp82tlR3M) · [CG Geek Graph Editor](https://youtu.be/_C2ClFO3FAY) · [CBaileyFilm polish](https://youtu.be/AEAc_lLjOMc)
- [ProductionCrate object vs bone](https://youtu.be/PGvyBlgXHi8) · Blender Manual Geometry Nodes Set Position + Noise
- TED-Ed [timing & spacing](https://ed.ted.com/lessons/animation-basics-the-art-of-timing-and-spacing-ted-ed)

## Meshy Free (only if needed)

1. Open meshy.ai (Free credits)  
2. Image-to-3D optional giraffe / tree hero for S07  
3. Drop GLB → `assets/meshy/scenes/S07/`  
4. Import into `MODEL_ADDITIONS` and hide `MOTION_Walker_S07`

Do **not** burn credits on S01–S06 / S08–S10 — GN sway already covers plate life.
