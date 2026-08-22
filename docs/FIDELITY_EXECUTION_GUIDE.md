# Fidelity & Sharpness Execution Guide (Africa S1)

**Purpose:** Online-backed settings so PRE-4K gate steps stay sharp — no soft Ken Burns / multi-reencode masters.  
**Constraint:** Blender **5.1.2** only · one heavy GPU job at a time · 4K still HOLD until gate clears.

---

## Why current masters can look soft

| Risk | What happens | Fix |
|------|----------------|-----|
| Blender → H.264 MP4 plates | Delivery codec used as intermediate | Prefer PNG/EXR sequences or DNxHR intermediates |
| Low Eevee TAA / over-denoise | Shimmer or plastic blur | Raise samples; check 100% crop |
| Wide Film filter | Softens edges | Narrow pixel filter width |
| Ken Burns from stills + ffmpeg reencodes | Generational mush | Use graded stills as Resolve stills with Dynamic Zoom, not double-encoded MP4 |
| YouTube-bitrate final as “master” | Too thin for archive/re-edit | Master = DNxHR HQX; upload = separate H.264 |

Current scripts (`render_scenes_mp4.py`) write **1080p H.264 HIGH** with **Eevee TAA 128**. Fine for preview; **not** the fidelity path for FINAL.

---

## Gate step → how to execute for fidelity

### 2) HQ Blender re-render (Blender 5.1)

**Command pattern (do not use 4.4):**
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" `
  -b "blend\africa_s1_master_v01.blend" -P render_scenes_mp4.py
```

**Sharpness checklist (apply in script or scene before batch):**
1. Resolution **1920×1080 @ 100%** (or native stills at full pixel size).
2. Engine: if staying on **Eevee** — raise `taa_render_samples` (≥128; hero scenes test 256).
3. If moving to **Cycles** — max samples **256–512**, adaptive noise threshold **~0.01**, OIDN/OptiX with **Albedo+Normal**; test a short frame range for flicker before full batch ([RenderJuice samples guide](https://www.renderjuice.com/learn/rendering-fundamentals/how-many-samples-should-i-use-in-blender), [SuperRenders settings](https://superrendersfarm.com/article/blender-render-settings-optimization-guide), [Blender Studio fundamentals](https://studio.blender.org/training/blender-fundamentals-45-lts/blender_4-5_lts_render-settings/)).
4. **Film → Pixel Filter Width:** lower for crisper CGI; Blackman-Harris default balanced ([Blender Film docs](https://docs.blender.org/manual/en/latest/render/cycles/render_settings/film.html)).
5. Prefer **PNG/EXR image sequence** into Resolve over H.264 for plates ([Motion Forge HQ CG video](https://www.motionforgepictures.com/high-quality-video-renders-from-your-cg-work/), [Blender Artists EXR workflow](https://blenderartists.org/t/vfx-workflow-blender-resolve/1227558)).
6. Yellow-ball / YB-Body overlays: Film **Transparent** + RGBA PNG/EXR; composite on Resolve **V2**.

### 3–5) Resolve V1 / kinetic V3–V4 / YB V2

| Track | Media | Fidelity rule |
|-------|--------|----------------|
| V1 | New scene plates | Relink; do not scale below native; match 24fps |
| V2 | YB PNGs / alpha MOV | Use PNG with alpha or **DNxHR 444 / ProRes 4444**; empty underlay only if exporting alpha alone ([Cutsio alpha export](https://cutsio.com/blog/best-way-to-export-transparent-video-in-davinci-resolve), [Moshion infographics](https://moshion.app/resources/animated-infographics-davinci-resolve)) |
| V3/V4 | Graded stills | Dynamic Zoom / Transform in Resolve — **not** pre-baked soft Ken Burns MP4 |
| V5 | TextStat | Vector/Fusion text preferred over raster blur |

**Windows master export:** QuickTime **DNxHR HQX** (Studio) — ProRes export is Mac-oriented; free Windows often needs DNxHR ([Hollyland export guide](https://store.hollyland.com/blogs/creator-hub/davinci-resolve-export-settings), [Cutsio HQ export](https://cutsio.com/blog/best-way-to-export-high-quality-video-in-davinci-resolve)).

### 6–7) Fairlight + grade + FINAL

1. Grade on Color page **after** picture lock / real VO.
2. Export **archive master** (DNxHR HQX) once.
3. Make **upload** H.264 from that master (never re-render timeline for every platform tweak) ([Compresto: master vs delivery](https://compresto.app/blog/davinci-resolve-export-settings)).

### 8) 4K (only after gate clear)

- Same Blender **5.1** path + `render_scenes_4k.py`.
- Do **not** upscale soft 1080p H.264 and call it 4K.
- Upload bitrate when delivering 4K SDR 24fps: **≥35–45 Mbps** H.264 High Profile ([YouTube encoding settings](https://support.google.com/youtube/answer/1722171)).

---

## Delivery encode (from master)

| Target | Settings |
|--------|----------|
| YouTube 1080p24 | H.264 High, progressive, yuv420p, **≥8 Mbps** (prefer **12–15** headroom) |
| YouTube 4K24 | H.264 High, **35–45 Mbps** |
| ffmpeg CRF path | `libx264 -crf 18 -preset slow -pix_fmt yuv420p` as visually near-lossless delivery from a clean master ([gist / YT params](https://gist.github.com/mikoim/27e4e0dc64e384adbcb91ff10a2d3678)) |

Audio: AAC-LC **192–320 kbps**, 48 kHz.

---

## Curated resource list

### Blender render quality
- https://superrendersfarm.com/article/blender-render-settings-optimization-guide  
- https://www.renderjuice.com/learn/rendering-fundamentals/how-many-samples-should-i-use-in-blender  
- https://studio.blender.org/training/blender-fundamentals-45-lts/blender_4-5_lts_render-settings/  
- https://docs.blender.org/manual/en/latest/render/cycles/render_settings/film.html  
- https://cgaxis.com/complete-blender-render-setup-guide-for-photorealistic-results-2026/

### Blender → Resolve fidelity
- https://www.motionforgepictures.com/high-quality-video-renders-from-your-cg-work/  
- https://blenderartists.org/t/vfx-workflow-blender-resolve/1227558  
- https://cookwithrome.com/blender/can-you-import-blender-into-davinci-resolve/  
- https://www.ab-arts.be/building-a-2d-and-3d-video-production-pipeline-with-free-software/

### Resolve export / overlays
- https://cutsio.com/blog/best-way-to-export-high-quality-video-in-davinci-resolve  
- https://store.hollyland.com/blogs/creator-hub/davinci-resolve-export-settings  
- https://compresto.app/blog/davinci-resolve-export-settings  
- https://cutsio.com/blog/best-way-to-export-transparent-video-in-davinci-resolve  
- https://moshion.app/resources/animated-infographics-davinci-resolve

### Stylized / educational reference
- https://blog.chaos.com/should-we-studio-ada (TED-Ed *Ada* handmade-3D pipeline lessons)

### Platform delivery
- https://support.google.com/youtube/answer/1722171  

---

## Africa S1 recommended “sharp path” (order)

1. Soft-pop / framing / AFRICA v2 in Blender **5.1** → render **PNG sequences** (or high-bitrate intermediates) to `renders/hq_plates/`.  
2. Relink Resolve **V1**; place YB/kinetic on **V2–V4** as native stills/alpha.  
3. Real VO → slip → Fairlight/grade.  
4. Deliver **DNxHR HQX master** + separate H.264 upload.  
5. Only then clear `STATUS_PRE4K_GATE_CLEARED.txt` and run 4K native.

**Anti-pattern to avoid:** Blender H.264 → ffmpeg Ken Burns → Resolve H.264 → YouTube H.264 (triple loss).
