---
title: OBS, FFmpeg & Encoding Manual
category: Software Manuals
tags: obs, ffmpeg, encoding, h264, delivery, screen-capture
source: docs/ffmpeg_delivery_encode.py, docs/DELIVERY_STANDARDS.md, docs/FIDELITY_EXECUTION_GUIDE.md
---

# OBS, FFmpeg & Encoding Manual

FFmpeg does assembly/transcode; OBS handles any screen-capture/camera work.
Together they are the delivery encode layer of the pipeline.

## FFmpeg — where it fits

Blender renders PNG sequences / MP4 plates → FFmpeg assembles scenes and final
masters → Resolve finishes → FFmpeg produces the delivery encode. Scripts:
`Africa Season 1\scripts\ffmpeg_delivery_encode.py` and the root assemble
scripts in this workspace.

## Delivery encode (H.264, verify with ffprobe)

- Container MP4 · H.264 **High profile** · yuv420p · closed GOP at half framerate.
- 1080p24 VBR 2-pass **8–12 Mbps** (top of range for high-motion kinetic).
- `libx264 -crf 18 -preset slow -pix_fmt yuv420p` = near-lossless reference.
- 4K24 upload (only after gate): 35–45 Mbps H.264 High.
- Archive master: **DNxHR HQX** (QuickTime, Windows/Studio).
- Audio: AAC-LC 320–384 kbps, 48 kHz stereo.

## Fidelity rule (avoid generational loss)

Anti-pattern: Blender H.264 → ffmpeg Ken Burns → Resolve H.264 → YouTube H.264
(triple loss). Correct: PNG/EXR sequences → relink in Resolve (V1) →
deliver DNxHR HQX master + separate H.264 upload copy. Keep uncompressed/high
bitrate masters before the YouTube-spec export.

## OBS (screen/camera + capture)

Use OBS for: on-screen demos, capture of IDE/render windows, live preview
streams, and webcam plates. For clean frames:

- Canvas 1920x1080, 24/30 fps, hardware (NVENC) H.264 encoder.
- Keep the same color space (Rec. 709) end-to-end; avoid re-encoding OBS output
  more than once.
- Capture in raw/CRF mode when frames will be edited later.

## Verify before "done"

Launching a job ≠ done. Run ffprobe: resolution, fps=24, yuv420p, H.264 High,
AAC-LC 48k, duration matches target, file plays. Stamp results into
`PRODUCTION_STATUS.md` when verified.