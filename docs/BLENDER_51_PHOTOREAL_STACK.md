# Blender 5.1 Photoreal Stack — Africa S1

**Binary:** Blender **5.1.2** only (`C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`)  
**Apply script:** `setup_photoreal_stack_51.py`  
**Sources:** [Blender 5.1 release](https://www.blender.org/download/releases/5-1/) · [EEVEE Light Paths](https://docs.blender.org/manual/en/5.1/render/eevee/render_settings/light_paths.html) · [Poly Haven](https://polyhaven.com/) · [Actions / slots](https://docs.blender.org/manual/en/5.1/animation/actions.html)

---

## Plugin / material stack

| Need | Tool | Status / how we use it |
|------|------|-------------------------|
| **Raytracing / GI** | EEVEE Ray Tracing + **Light Path intensity** (5.1) | Script sets RT on, resolution `1`, bump **indirect** ~1.1–1.4 |
| **GPU** | Cycles OptiX/CUDA (RTX 4060) | `setup_nvidia_gpu.py` + stack script |
| **HDRI lighting** | Poly Haven HDRIs in `assets/hdri/` | Soft sun threshold ↑ for softer discs |
| **Textures** | Principled + Smart filter; Poly Haven PBR when imported | Hygiene pass on all plate mats |
| **Scatter / ground** | **GScatter** (Extensions) | ⚠️ Incompatible with Blender 5.1 / Python 3.13 — use GN scatter until updated |
| **Character / YB-Body** | **Rigify** + optional Bone Info GN (5.1) | Enable Rigify; faceless torso + ball head |
| **Motion polish** | F-Curve **Smooth (Gaussian)** (5.1) | Cameras get non-destructive smooth |
| **Text motion** | GN **String to Curves** (5.1 Word output) | Use for future TextStat in-Blender |
| **Encode** | H.264 HIGH / CRF~18 | Intermediate plates; Prefer PNG/EXR for FINAL fidelity |

---

## Apply (one command)

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" `
  -b "C:\Users\HP\OneDrive\The Vault\Africa Season 1\blend\africa_s1_master_v01.blend" `
  -P "C:\Users\HP\OneDrive\The Vault\Africa Season 1\setup_photoreal_stack_51.py"
```

Then HQ re-render (PRE-4K gate step 2 — **not** 4K yet):

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" `
  -b "blend\africa_s1_master_v01.blend" -P "render_scenes_mp4.py"
```

---

## Animation practice (from 5.1 release)

1. **Actions + slots** — keep ball + material emission in one action with separate slots.  
2. **Replace Action** — swap morph packs across YB instances in one go.  
3. **Gaussian Smooth** — first modifier on noisy cam/ball curves.  
4. **Dope Sheet colors** — verify BEZIER vs LINEAR on kinetic beats.  
5. **Shape keys** — ball squash/stretch; use “Apply to Basis” only when locking a look.  
6. **Bone Info (GN)** — drive props from YB-Body armature (one-way: bone → geometry).

---

## Install if missing (Blender → Edit → Preferences → Get Extensions)

- GScatter  
- Any Poly Haven browser addon you prefer  
- Keep **Rigify** (built-in) enabled  

VRAM rule (RTX 4060 8GB): one heavy job at a time; Simplify texture cap if OOM.
