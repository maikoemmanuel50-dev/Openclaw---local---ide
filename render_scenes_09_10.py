"""Render only scenes 09 and 10 (resume after crash)."""
import bpy
import os
import sys

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
RENDER_DIR = os.path.join(PROJECT, "renders", "video_clips")
SCENE_ORDER = ["09_Closer", "10_EndCard"]

os.makedirs(RENDER_DIR, exist_ok=True)

for i, sname in enumerate(SCENE_ORDER, 9):
    sc = bpy.data.scenes[sname]
    bpy.context.window.scene = sc
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "FFMPEG"
    sc.render.ffmpeg.format = "MPEG4"
    sc.render.ffmpeg.codec = "H264"
    sc.render.ffmpeg.constant_rate_factor = "HIGH"
    sc.render.ffmpeg.ffmpeg_preset = "GOOD"
    sc.render.ffmpeg.audio_codec = "NONE"
    if hasattr(sc.eevee, "taa_render_samples"):
        sc.eevee.taa_render_samples = 8
    out = os.path.join(RENDER_DIR, f"{sname}.mp4")
    if os.path.isfile(out):
        os.remove(out)
    sc.render.filepath = out
    print(f"[{i}/10] RENDER_START {sname} frames={sc.frame_end} -> {out}", flush=True)
    bpy.ops.render.render(animation=True)
    print(f"[{i}/10] RENDER_DONE {sname}", flush=True)

print("ALL_SCENES_RENDERED", flush=True)
