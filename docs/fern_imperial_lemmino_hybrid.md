# Fern × Imperial × LEMMiNO Hybrid — Silicon Savannah

**Command center:** Cursor IDE · Blender 5.1.2 MCP · DaVinci Resolve  
**Episode:** AFRICA S1 Ep01 · ~7 min · 24fps · 10 scenes  
**Hero:** Yellow ball `#FFD54F` · humanity = YB-Body (faceless torso + ball head)

This is how those channels integrate **animation + photo/stock**, and how we execute the same language without copying their niche content.

---

## 1. What each channel actually does

### Fern / Imperial (Hoog lineage)
- **Primary surface:** cinematic **3D** scenes (Blender / USD), not talking-head.
- **People:** **faceless** mannequin-like figures — anonymity forces attention onto story/space.
- **Camera:** slow push / orbit / dolly; one clear subject per shot.
- **Light:** soft ambient + directional sun; matte materials; desaturated environments so accents read.
- **Stock role:** secondary. Environments feel *built*; photo is texture under 3D, not the main act.

**Tutorials that map to our stack:**
- [Edit Faceless Videos like Fern, Neo & Imperial — Blender](https://www.youtube.com/watch?v=Jmcg5ZSU8a8)
- [3D Scene Animations like Hoog, Fern, Imperial — Resolve USD](https://www.youtube.com/watch?v=BvIr_TJ-RE4)
- EEVEE exterior HDRI + world sun shadows: [EEVEE Exterior Lighting](https://www.youtube.com/watch?v=pp1N4XnBgHw)
- Blender 5.1 GI intensity: [Creative Shrimp — EEVEE GI](https://www.creativeshrimp.com/new-blender-5-1-eevee-feature-gi-intensity.html)

### LEMMiNO
- **Primary surface:** researched VO + **abstract motion graphics** + **archival / photo treated as cinema**.
- **Still photos:** Ken Burns (scale/pan), grain, grade match, posterize-time when matching old film — never “dump a JPEG full-frame static.”
- **Stock people walking:** avoided as literal illustration; prefer atmosphere, maps, particles, diagrams, carefully chosen archival.
- **Tool truth (his FAQ):** Photoshop → After Effects → Cinema 4D/Blender/Unreal → Premiere **or Resolve**.

**References:**
- [LEMMiNO FAQ — tools](https://www.lemmi.no/faq)
- Archival still treatment: Ken Burns / Basic 3D tilt workflows in NLE

### Shared DNA (what we steal)
| Rule | Practice |
|------|----------|
| Faceless humanity | YB-Body only — no faces |
| One idea per frame | Ball or diagram or photo-plane, not all fighting |
| Photo ≠ raw dump | Always move + grade + soft edge into CG |
| Atmosphere > literal B-roll | HDRI dusk/dawn plates, soft indigo fields |
| Narration owns timing | VO drives cuts; protect stats 36–60f |

---

## 2. Our hybrid stack (locked)

```
V1  Photoreal-lit Blender spine (HDRI + EEVEE ray tracing + soft DOF)
V2  Graphic hero — yellow ball / YB-Body (Fern faceless layer)
V3  Photo/archival Ken Burns + kinetic texture (LEMMiNO still treatment)
V4  Detail inserts / flash cuts
V5  TextStat / labels
```

**Look name:** Soft-Pop Photoreal Hybrid  
- **Worlds:** photoreal African HDRIs (Poly Haven South Africa dusk family already on disk; optional Bambanani / Dikhololo / Magalies).  
- **Hero:** graphic gold ball — never replaced by photoreal sphere chrome.  
- **Humans:** YB-Body = Fern mannequin rule in our soft-pop charcoal + ball head.  
- **Fields:** matte soft-pop indigo/cream/charcoal under photoreal light.

### Soft-pop field palette (Claude lock)
| Role | Hex |
|------|-----|
| Hero ball | `#FFD54F` |
| Mustard (bg wash only) | `#D9A441` |
| Dusty indigo | `#2E3A50` |
| Terracotta | `#C1552E` |
| Plum | `#7D2E3B` |
| Cream | `#F1E4C8` |
| Soft charcoal | `#262019` |

---

## 3. Scene integration map

| Scene | Fern/Imperial 3D beat | LEMMiNO photo beat | Ball / YB |
|-------|----------------------|--------------------|-----------|
| S01 Cold Open | Dawn skyline plate + DOF push | Matatu silhouette Ken Burns | Sun-seed → YB crowd morph |
| S02 2007 | Kiosk parallax | Retro phone / keypad stills flash | M-Pesa coin |
| S03 Hubs | Coworking depth | Keyboard / whiteboard inserts | Hub orbit |
| S04 Phone | Hand+phone plate | UI glow inserts | Data orb |
| S05 Money | Chart room (graphic) | Sparse — protect chart | Dim orb rim |
| S06 Solar | Panel + HDRI sun | Rooftop texture inserts | Beacon flash |
| S07 Gap | Kenya map graphic | Sparse archival map stills | Dim gap |
| S08 Secondary | Desat kiosk dusk | Street still Ken Burns | Founder dim |
| S09 Closer | Dusk skyline photoreal | Global skyline flashes | Forecast beacon |
| S10 End | Logo hold | Minimal | Ball settle |

---

## 4. Addons & resources (Blender 5.1.2)

| Resource | Role | Status |
|----------|------|--------|
| **Official Lab MCP** | Cursor ↔ Blender | ✅ Connected |
| **Blendkit** | Asset browse | ✅ Enabled |
| **GScatter** | Ground scatter | ❌ Python 3.13 incompatible on 5.1 — use 4.4 scatter bake *or* Geometry Nodes scatter proxy |
| **Poly Haven HDRIs** | Photoreal worlds | ✅ 3 on disk; optional more Africa dusk |
| **Poly Haven Blender addon** | Drag HDRI/mats | Recommended install |
| EEVEE ray tracing + **World → Sun → Shadows** | Fern exterior light | Applied via `setup_softpop_photoreal.py` |

---

## 5. Resolve execution (LEMMiNO photo layer)

1. Import Canva / still packs into Media Pool folder `Photoplates_LEMMiNO`.
2. On **V3**, place stills **over** V1 for 12–36f with:
   - Dynamic Zoom / Transform keyframes (1.00 → 1.08 scale)
   - Soft Gaussian blur 0.3–0.8 on edges via Fusion if needed
   - Slight desat + warm or cool match to chapter LUT
   - Optional Film Grain 8–15% so CG and photo share grain
3. Never leave a still static >18f unless it is a protected archival “evidence” beat.
4. V2 ball always wins contrast — photoplates stay ≤60% luminance vs ball.

---

## 6. Cursor IDE command loop

1. Blender MCP: run soft-pop photoreal setup → save master.  
2. Render spine clips (`render_scenes_mp4.py`) one GPU job at a time.  
3. Resolve MCP: markers + V2/V3 notes.  
4. Assemble: `assemble_final_video.py` → `assemble_with_audio.py`.  
5. Guard: no second mascot, no faces, hero hex `#FFD54F` only.
