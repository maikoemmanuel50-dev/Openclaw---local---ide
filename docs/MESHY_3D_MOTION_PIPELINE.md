# Meshy 3D motion pipeline — Africa S1

Replace **camera pan-into-still** with **textured 3D dioramas** (trees sway, animals walk, lights pulse). Illustrated-documentary style — not full character animation.

**Default for Africa S1:** Option **D** — see `docs/OBJECT_MOTION_LOCK.md` (`setup_object_motion_all_scenes.py`).  
Meshy Free browser is **optional** (S07 giraffe only). API/MCP stay unused without Pro.

---

## Prerequisites / access reality

**API + MCP require a paid Meshy plan** (Pro+). Free accounts get **web-app credits only** — no API keys. There is no supported “free API” path; do not share keys or scrape the site.

### Legitimate options (pick one)

| Path | Cost | How it works for Africa S1 |
|------|------|----------------------------|
| **A. Meshy Free web UI** | $0 (~100 credits/mo + daily login bonuses) | Generate in browser → download GLB → drop into `assets/meshy/scenes/SXX/` → run `setup_meshy_scene_motion.py`. CC BY 4.0 — credit Meshy if commercial. |
| **B. Meshy Pro** | Paid | Unlocks API/MCP so Cursor can batch all 10 scenes. |
| **C. Local / free AI (no Meshy)** | $0 compute | TripoSR / InstantMesh / Hunyuan3D / Blender add-ons on your GPU (after HQ free). Same folder layout. |
| **D. No image-to-3D** | $0 | Keep plates; animate **objects** in Blender (GN sway, simple animal walk cycles, emission pulse) — matches illustrated-doc style without full diorama rebuild. |

3. **Do not modify `africa_s1_master_v01.blend` while HQ GPU batch is running.**  
   Blender motion script saves a **preview blend** until `AFRICA_MESHY_APPLY_MASTER=1`.

### If using Free web UI (Option A)

1. Image-to-3D each hero still from `scripts/meshy_scene_manifest.json` (prioritize S07 savanna, S01 dawn, S06 solar).  
2. Export **GLB** (OBJ/FBX/STL optional).  
3. Save as `assets/meshy/scenes/S07/s07_meshy.glb` (etc.).  
4. Run Blender motion setup (CPU) when HQ GPU is free.

## Scene map (all 10)

| Scene | Hero still | Motion |
|-------|------------|--------|
| S01 | `k01_nairobi_dawn_1080.png` | tree sway, cloud drift |
| S02 | `k02_market_kiosk_1080.png` | sign sway, fabric |
| S03 | `k03_coworking_1080.png` | screen glow, plants |
| S04 | `k04_phone_scroll_1080.png` | thumb scroll, UI pulse |
| S05 | `k05_data_city_1080.png` | light pulse, data flow |
| S06 | `k06_solar_field_1080.png` | panel shimmer, grass |
| S07 | `k07_kenya_landscape_1080.png` | **tree sway + giraffe walk** |
| S08 | `k08_town_street_1080.png` | lamp flicker, trees |
| S09 | `k09_nairobi_dusk_1080.png` | window twinkle, clouds |
| S10 | `pr_s10_africa_title.png` | subtle title glow |

Manifest: `scripts/meshy_scene_manifest.json`

## Step 1 — Generate meshes (API or MCP)

### Option A: Python batch (REST)

```powershell
setx MESHY_API_KEY msy_YOUR_KEY
# New terminal:
python scripts/meshy_generate_all_scenes.py
python scripts/meshy_generate_all_scenes.py --scene S07
```

Outputs: `assets/meshy/scenes/SXX/` → **GLB, OBJ, FBX, STL**  
Registry: `renders/quality/meshy_scene_registry.json`

### Option B: Cursor chat (MCP tools)

After MCP green dot:

> Convert `assets/canva/kinetic/graded_1080/k07_kenya_landscape_1080.png` to a textured 3D model with PBR, smart topology ~8000 faces, export GLB/OBJ/FBX/STL to `assets/meshy/scenes/S07/`.

Repeat per scene using the table above.

## Step 2 — Blender 5.1 import + motion (CPU)

```powershell
$env:CUDA_VISIBLE_DEVICES = "-1"
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b blend/africa_s1_master_v01.blend -P setup_meshy_scene_motion.py
```

- Locks camera (removes pan/push)
- Hides flat `Background_Plane` / parallax cards
- Imports GLB, applies sway / walk drivers
- Saves `blend/africa_s1_meshy_motion_preview.blend` (master safe)

After HQ **10/10** finishes:

```powershell
$env:AFRICA_MESHY_APPLY_MASTER = "1"
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b blend/africa_s1_master_v01.blend -P setup_meshy_scene_motion.py
```

Then re-render affected scenes only (S01 already done — patch list in registry).

## Step 3 — Resolve

- **V1** = new Blender plates (mesh dioramas)
- **V3/V4** kinetic overlays unchanged; fewer pan-style stock inserts where 3D carries motion
- Grade: Rec.709 · density tweak per [Resolve density short](https://www.youtube.com/shorts/spB6aNU8Hms)

## Craft refs (user links)

- [Jh5RALdecPs](https://youtu.be/Jh5RALdecPs) · [12lB3NA_ZwE](https://youtu.be/12lB3NA_ZwE) · [BExK2Xj6ypU](https://youtu.be/BExK2Xj6ypU)  
- [kmnYxvGxLVE](https://youtu.be/kmnYxvGxLVE) · [ley0hp5__tY](https://youtu.be/ley0hp5__tY) · [EF_Wysanmn0](https://youtu.be/EF_Wysanmn0)  
- [EhuzWg7XsF0](https://youtu.be/EhuzWg7XsF0) · [aOvNcfzi4D0](https://youtu.be/aOvNcfzi4D0) · [8WKs9HdwTY8](https://youtu.be/8WKs9HdwTY8) · [04zgrIohnXE](https://youtu.be/04zgrIohnXE)

## QC locks (unchanged)

Blender **5.1.2 only** · **4K HOLD** · user VO · yellow-base · shots **≤5s** · one GPU job at a time.
