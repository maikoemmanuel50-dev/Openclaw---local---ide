# Resolve / Fairlight Finish Workflow — Episode 01

**Automated mix available:** Run `python assemble_with_audio.py` first for a working FINAL mp4.

## Manual Resolve Polish (Optional)

### Step 1: Import
1. Open DaVinci Resolve Studio
2. Create/open project: `Africa S1 - Silicon Savannah`
3. Import media:
   - `Africa_S1_Silicon_Savannah_FINAL.mp4` (or silent + separate audio)
   - `assets/audio/vo/episode_01_vo.wav` (when recorded)
   - `assets/audio/music/ch*.wav`
   - `assets/audio/sfx/*.wav`

### Step 2: VO-First Edit
1. Place VO on A1 as spine
2. Slip/trim video clips to VO sentence boundaries
3. Use markers from `resolve_spec.yaml` as guide
4. Cut on beats — no 1s black fades between chapters

### Step 3: Fusion Stat Callouts
Apply `templates/resolve/TextStat_README.md` at typography_markers frames:
- $984M (S05), 82% (S05), 97% (S07), Forecast (S09)

### Step 4: Fairlight Mix
Follow `templates/resolve/FairlightMix_README.md`:
- Music at -22dBFS, duck under VO
- SFX at -18dBFS (punctuation) / -14dBFS (stats)
- Chapter music crossfades at section_resets

### Step 5: Color Conform
Apply chapter LUTs per `resolve_spec.yaml` luts section.
Create LUTs in Resolve Color page or use PowerGrade presets matching `docs/teded_style_bible.md` palette chapters.

### Step 6: Deliver
Export: `Africa_S1_Silicon_Savannah_FINAL.mp4`
- H.264, 1920x1080, 24fps
- AAC 192kbps stereo

## VO Replacement
When final narration is recorded:
1. Replace `assets/audio/vo/episode_01_vo.wav`
2. Re-run `python assemble_with_audio.py`
3. Re-slip all visual keyframes in Blender/Resolve to new timestamps
4. Update `docs/audio_design_map.yaml` vo_cue_sheet with actual times
