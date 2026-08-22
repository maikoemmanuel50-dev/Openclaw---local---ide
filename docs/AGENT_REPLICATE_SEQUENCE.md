# AGENT HANDOFF — Replicate full Africa S1 sequence

**Paste this entire message into the other open Cursor agent** working in:
`C:\Users\HP\OneDrive\The Vault\Africa Season 1`

You are Auto in Cursor. Execute this playbook end-to-end. Use Blender MCP (`user-blender-mcp`), DaVinci Resolve MCP (`user-davinci-resolve`), and Canva via Composio (`plugin-composio-composio`, account `canva_airway-sasin`, session as needed). Do not ask for confirmation between steps unless blocked.

---

## Creative locks (do not break)
- Hero ball `#FFD54F` only; soft-pop: mustard `#D9A441`, indigo `#2E3A50`, terracotta `#C1552E`, plum `#7D2E3B`, cream `#F1E4C8`, charcoal `#262019`
- YB-Body = faceless charcoal torso + yellow ball head; no faces; morph 12–18f
- Hybrid: photoreal HDRI worlds + graphic ball/YB-Body; LEMMiNO Ken Burns photoplates
- Kinetic ASL ~0.4–1.0s; protect stats 36–60f; **do not extend past 7:00**
- Blender **5.1.2** · master: `blend/africa_s1_master_v01.blend`
- Resolve project **Africa Season 1**, timeline **Episode 01 - Assembly**
- Tracks: V1 spine · V2 ball/YB · V3–V4 kinetic · V5 text

---

## Already done (verify, do not redo unless broken)
1. Camera framing pass — BG planes cover frame; S01 matatus; S05 bars; S06 solar; S08 layers; all-pass mid/start/end
2. HQ stills download → `assets/canva/kinetic/hq/` (~18 OK); Mixkit videos **403 failed**
3. Graded 1080p plates → `assets/canva/kinetic/graded_1080/` (~36 PNGs)
4. Generated gap fills: matatu + solar PAYG plates in hq/graded
5. **AFRICA end card v2** (word only, no Netflix) at `assets/canva/s10_africa_logo.png` (1920×1080); backup `s10_africa_logo_netflix_bak.png`; Blender S10 reloaded + reframed; hero check `renders/softpop_heroes/10_EndCard_logo_v2.png`
6. Canva blank templates created: `DAHSGodJcI0` (1920×1080), `DAHSGtdHqlM` (square), `DAHSGtmzQSI` (vertical)
7. Scripts present: `setup_frame_fidelity.py`, `setup_yb_body_humanoid.py`, `scripts/normalize_kinetic_stills.py`, `scripts/download_photoreal_cutaways.py`

---

## EXECUTE NOW — remaining finish sequence

### A. Blender fidelity + humanoid (MCP or CLI)
```
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b "blend\africa_s1_master_v01.blend" -P "setup_frame_fidelity.py"
```
Then run / fix `setup_yb_body_humanoid.py` (replace 8-vert cube YB_Body with ISO 7250 mannequin + armature + breath/sway). Studio base pack is at `assets/humanoid/human-base-meshes-bundle-v1.4.1/`. Enable humanity scenes: S01 crowd, S03 builder, S08 founder_dim, S09 crowd. Save master.

### B. HQ re-render all 10 scenes
Use `render_scenes_mp4.py` (or equivalent) with HQ samples (128–160), AgX Medium High Contrast, 1920×1080, H264 PERCEIVED_QUALITY. Output to `renders/video_clips/`. **Must include new AFRICA logo on S10.** Overnight GPU OK on RTX 4060.

Also re-render S10 alone first if full batch is too long:
- Confirm `10_EndCard.mp4` shows full AFRICA wordmark + ball, no Netflix line.

### C. Canva stylize cutaways (Composio)
For key stills (public Unsplash URLs from `assets/canva/kinetic/hq/manifest.json` or local graded plates after upload):
1. `CANVA_CREATE_URL_ASSET_UPLOAD_JOB` → poll `CANVA_GET_URL_ASSET_UPLOADS_JOBID`
2. `CANVA_POST_DESIGNS` custom 1920×1080 / 1080×1080 / 1080×1920 with `asset_id`, titles like `AFRICA S1 Cut S0X …`
3. `CANVA_POST_EXPORTS` PNG/JPG → poll → download into `assets/canva/kinetic/canva_exports/`
4. Drop AFRICA logo into the three existing end-card designs and export

Account: **`canva_airway-sasin`**

### D. Resolve integration
1. Import/relink V1 clips from fresh `renders/video_clips/*.mp4` (replace built_clips)
2. V3/V4: place graded_1080 stills as Ken Burns cutaways under VO (ASL 0.4–1.0s); do not exceed 7:00 — inserts only
3. V2: yellow ball / YB morphs at existing markers (`YB_S01_RISE`, `YB_S01_BODY_CROWD`, `YB_S03_BODY_BUILDER`, `YB_S08_FOUNDER_DIM`, `YB_S09_CROWD_REIGNITE`, etc.)
4. Keep V5 for TextStat; protect $984M / 82% / 97% holds 36–60f

### E. Audio
- Placeholder VO exists: `assets/audio/vo/episode_01_vo_placeholder.wav`
- If no real VO yet: assemble with placeholder; document that real VO still required
- Music 5 beds + 16 SFX already in `assets/audio/` — Fairlight duck under VO per `docs/audio_design_map.yaml`

### F. Assemble + verify
```
python assemble_final_video.py
python assemble_with_audio.py
```
Or Resolve deliverable export. Verify:
- Runtime ≤ 7:00 @ 24fps
- S10 AFRICA-only end card
- Ball never loses #FFD54F identity
- Graded cutaways appear as kinetic inserts

### G. Write status update
Update `PRODUCTION_STATUS.md` with what you completed and what remains (real VO if still placeholder).

---

## Animated sequences already in Blender (preserve)
Cameras all 10 · S05 GN bars · S06 solar · S07 map zoom · TED-Ed labels · planned ball morphs · YB-Body (upgrade mesh/rig)

## Docs to read first
- `docs/fern_imperial_lemmino_hybrid.md`
- `docs/yellow_ball_throughline.md`
- `docs/teded_scene_spec_ep01.md`
- `docs/s10_africa_logo_v2.md`
- `PRODUCTION_STATUS.md`

## Priority order if time-boxed
1. S10 re-render + Resolve relink  
2. Full HQ scene re-render batch  
3. V3/V4 graded stills Ken Burns  
4. YB-Body humanoid upgrade  
5. Canva multi-format exports  
6. FINAL assemble  

Start at step A now. Report progress after each major letter (A–G).
