# AFRICA S1 — Full Production Workflow (execute to completion)
# Path: C:\Users\HP\OneDrive\The Vault\Africa Season 1

## Current Pipeline (as documented)

```
Phase A: Blender Setup          [COMPLETE]
Phase B: Creative Fine-Tuning   [COMPLETE]
    ↓
Full Video Render               [IN PROGRESS — S09 rendering, S10 queued]
    render_scenes_mp4.py → renders/video_clips/*.mp4
    ↓
FFmpeg Assembly                 [AUTO on render complete]
    assemble_final_video.py → Africa_S1_Silicon_Savannah_7min.mp4
    ↓
Resolve Assembly                [RUN on new master]
    resolve_spec.yaml → Episode 01 - Assembly → HQ deliver export
    ↓
Phase C: Audio (Fairlight)      [PARTIAL — placeholder assets generated]
    VO spine → SFX → music beds → LUT conform
```

## Run to completion

```powershell
powershell -File run_workflow_to_completion.ps1
```

## Manual steps (require human)

- Replace `assets/audio/vo/episode_01_vo.wav` with recorded narration from `episode_1_script.md`
- Optional: LUT color conform in Resolve Color page

## Key outputs

| File | When |
|------|------|
| `renders/video_clips/*.mp4` | Per-scene Blender renders |
| `Africa_S1_Silicon_Savannah_7min.mp4` | FFmpeg crossfade assembly |
| `Africa_S1_Silicon_Savannah_7min_Resolve.mp4` | Resolve H.264 deliver |
| `Africa_S1_Silicon_Savannah_7min_HQ.mp4` | Resolve high-bitrate export |
