# Arch Comm IV — Blender Setup Lock (Africa S1)

**Source:** `Telegram/Blender_Class 01.mp4` … `16.m4v` (JKUAT Arch Comm iv / B.Arch pack)  
**Frames:** `docs/telegram_imports/arch_comm_iv_frames/`  
**Apply:** `setup_arch_comm_iv_lock.py` (Blender **5.1.2** only)  
**Report:** `renders/quality/arch_comm_iv_lock_report.json`

Creative locks unchanged: yellow ball `#FFD54F` only · faceless YB-Body · no 4K until gate clear.

## Class → enforce

| Class themes (from video stills) | Project enforcement |
|----------------------------------|---------------------|
| Cycles + GPU Compute + Denoise | Cycles GPU OptiX/OIDN; adaptive threshold **0.01**; denoise on |
| Metric / cm–m real scale | Scene units **METRIC / METERS**; scale outlier audit |
| Top Ortho + Perspective layout | Documented workflow; cameras kept for render |
| Named meshes (`B_Barista …`) | Collections: `HERO` · `ENV` · `LIGHTS` · `CAMERAS` · `MODEL_ADDITIONS` |
| Principled + Image Texture (albedo/normal/height) | Auto-wire PBR links; Non-Color on data maps |
| Texture library folders + Poly Haven / Sketchfab | Remap missing images → `assets/textures` / Poly Haven |
| Area lights + multi-camera cafe/bar | Soft Area fill if scene has no Area lights |
| Low sample demos (20) | **Not** copied — production samples ≥256 |

## Run

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" `
  -b "blend\africa_s1_master_v01.blend" -P "setup_arch_comm_iv_lock.py"
```

Wired as lock `08_arch_comm` in `run_full_reformulation.ps1` (before force HQ).
