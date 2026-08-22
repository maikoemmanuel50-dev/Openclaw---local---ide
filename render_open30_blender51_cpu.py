"""CPU Cycles render of polished open30 sidecar (720f). Does not touch master."""
from __future__ import annotations

import os
from pathlib import Path

import bpy

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
OUT_MP4 = PROJECT / "renders" / "paced_overlays" / "s01_teded_open30_blender51.mp4"
LOG = PROJECT / "renders" / "quality" / "teded_open30_render_log.txt"


def main():
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 64
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.fps = 24
    scene.frame_start = 1
    scene.frame_end = 720
    scene.render.filepath = str(OUT_MP4.with_suffix(""))
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    OUT_MP4.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write("RENDER_START CPU Cycles 1-720\n")
    bpy.ops.render.render(animation=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"RENDER_DONE {OUT_MP4}\n")
    print("DONE", OUT_MP4)


if __name__ == "__main__":
    main()
