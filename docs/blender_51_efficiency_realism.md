# Blender 5.1.2 — Efficiency + Realism Guide (Silicon Savannah)

**Master:** `blend/africa_s1_master_v01.blend`  
**Release notes:** [Blender 5.1 — Built for Speed](https://www.blender.org/download/releases/5-1/)  
**Applied scripts:** `setup_softpop_photoreal.py`, `setup_realism_camera_anthro.py`

---

## 1. What Blender 5.1 gives this project

| Feature (5.1) | How we use it |
|---------------|---------------|
| **Faster EEVEE compile / less VRAM** | Keep EEVEE for 10-scene overnight MP4; one GPU job at a time on RTX 4060 8GB |
| **Light Path intensity (EEVEE)** | Soften/boost indirect light without rebuilding HDRIs — Creative Shrimp GI control |
| **Light Path in World** | Optional: camera vs lighting path splits (use carefully — broke plates once) |
| **Faster Action / Shape Key playback** | Scrub long cameras (S09 1680f) without hitching |
| **Smooth (Gaussian) F-curve modifier** | Soften noisy camera/ball keys non-destructively |
| **Show Subframes** | Fine VO sync when slipping ball morphs |
| **Geometry Nodes Bone Info** | Future: rig-driven YB-Body crowd stagger |
| **String to Curves fields + Word output** | Future: TextStat motion in GN instead of only Resolve |
| **Sequencer Strip Info + Mask→SDF** | Optional in-Blender transitions; primary edit stays Resolve |
| **Official Lab MCP** | Cursor ↔ live Blender (null-byte protocol) — already wired |
| **Python 3.13 / VFX Platform 2026** | Note: GScatter (3.11) incompatible — scatter via GN or bake in 4.4 |

**Patch train:** 5.1.0 → 5.1.1 (71 fixes) → **5.1.2** (12 fixes) — stay on 5.1.2.

---

## 2. Realism locks (perspective + anthropometrics)

Sources: [EEVEE DOF 5.1 Manual](https://docs.blender.org/manual/en/5.1/render/eevee/render_settings/depth_of_field.html), photographic scale practice, ISO-style adult standing height.

| Parameter | Lock | Why |
|-----------|------|-----|
| Units | Metric, 1 BU = 1 m | DOF / lights / sensors behave like real cameras |
| Sensor | Full-frame **36 mm** horizontal | Standard cinema still |
| Eye height | **1.55–1.70 m** | Avoid accidental “drone” look |
| Establishing elevate | +0.85 m max (S01/S09 only) | Story overview without losing human scale |
| Normal lens | **35–50 mm** | Natural perspective |
| Chart / map | **35 mm + f/8** | Readable depth |
| Phone CU | **50 mm + f/4** | Mild compression |
| Adult YB-Body | **1.70 m** standing; head Ø **0.24 m** | Fern faceless humanoids, real proportions |
| Hero ball prop | Ø **0.42 m** | Readable graphic hero without giant-ball CGI lie |
| DOF | Real f-stops 4–8; focus object = ball/aim | Optical realism; enable EEVEE bokeh jitter when available |

**Camera hierarchy (deployed):**
```
CAM_RIG_<scene>   (Empty @ eye height, distance along -Y)
  └─ Main_Camera  (Track To → CAM_AIM_<scene>)
CAM_AIM_<scene>   (Empty on subject / ball)
```

**Overlays:** FONT objects get Track To camera, letter height ~0.18–0.35 m, light extrude for EEVEE presence.

---

## 3. How-to video / doc stack (efficiency)

1. [Blender 5.1 release overview — Jonathan Lampel / CGCookie](https://www.blender.org/download/releases/5-1/) (recap on release page)
2. [EEVEE Exterior Lighting (HDRI + world sun shadows)](https://www.youtube.com/watch?v=pp1N4XnBgHw)
3. [EEVEE high-quality DOF / jitter](https://www.youtube.com/watch?v=rO8xupUuN5U)
4. [Creative Shrimp — EEVEE GI intensity (5.1)](https://www.creativeshrimp.com/new-blender-5-1-eevee-feature-gi-intensity.html)
5. [Faceless scenes like Fern / Imperial — Blender](https://www.youtube.com/watch?v=Jmcg5ZSU8a8)
6. [Hoog / Fern / Imperial in Resolve USD](https://www.youtube.com/watch?v=BvIr_TJ-RE4)
7. Manual: [Depth of Field — Blender 5.1](https://docs.blender.org/manual/en/5.1/render/eevee/render_settings/depth_of_field.html)
8. Extensions: [extensions.blender.org](https://extensions.blender.org/) — Poly Haven asset browser recommended; GScatter wait for 3.13 build

---

## 4. Efficient Cursor IDE loop

1. **One heavy GPU job** — never Blender full re-render + Resolve denoise together.
2. MCP `execute_blender_code` for look-dev; overnight `render_scenes_mp4.py` for finals.
3. Hero stills first: `renders/softpop_heroes/*_hero.png` before multi-minute clips.
4. Prefer **constraints + empties** over baking camera locations (editable, VO-slippable).
5. Use **5.1 Smooth (Gaussian)** F-curve modifier on ball/camera after hand keys.
6. Keep Lab MCP server on port **9876**; don’t run Jagath + Lab together.

---

## 5. Character / scene truth table

| Asset | Realism rule |
|-------|----------------|
| Yellow ball | Graphic `#FFD54F` emission hero — **not** chrome PBR orb |
| YB-Body | Faceless charcoal torso + ball head @ adult scale; morph 12–18f |
| Photoplates | Camera-facing billboards; Ken Burns ≤6% scale; alpha hashed |
| HDRI | Lights scene (Poly Haven Africa dusk/day); plates carry story |
| Charts (S05) | Human eye height cam + area key/fill so EEVEE doesn’t go black |

---

## 6. Next efficiency wins (optional)

- GN **String to Curves** for onboard TextStat (5.1 Word output)
- GN **Bone Info** for crowd YB stagger driven by simple armature
- Compositor **Mask to SDF** for soft plate edges
- Install **Poly Haven** extension for 1-click 4K HDRI swaps
