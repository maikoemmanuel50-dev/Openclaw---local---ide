"""
Render short kinetic B-roll takes from each Blender scene (fast-paced edit pack).
Run:
  blender -b blend/africa_s1_master_v01.blend -P render_kinetic_broll.py

Outputs to renders/kinetic_broll/{scene}_broll_{tight|whip|detail}.mp4
Uses Eevee; keep Resolve deliver idle while this runs (RTX 4060 VRAM).
"""
import bpy
import math
import os

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
OUT_DIR = os.path.join(PROJECT, "renders", "kinetic_broll")
FPS = 24

SCENES = [
    "01_ColdOpen", "02_Context2007", "03_Beat1_Hubs", "04_Beat1_Phone",
    "05_Beat2_Money", "06_Beat2_Solar", "07_Beat3_Gap", "08_Beat3_SecondaryCity",
    "09_Closer", "10_EndCard",
]

# (suffix, frames, camera mutation)
TAKES = [
    ("tight", 60, "tight"),
    ("whip", 30, "whip"),
    ("detail", 42, "detail"),
]


def get_cam(scene):
    for o in scene.objects:
        if o.type == "CAMERA":
            return o
    return None


def mutate_camera(cam, kind, frames):
    if not cam:
        return
    if cam.animation_data:
        cam.animation_data_clear()
    base = cam.location.copy()
    if kind == "tight":
        cam.location = (base.x, base.y * 0.75, base.z)
        cam.keyframe_insert("location", frame=1)
        cam.location = (base.x, base.y * 0.55, base.z + 0.2)
        cam.keyframe_insert("location", frame=frames)
    elif kind == "whip":
        cam.location = (base.x - 3, base.y, base.z)
        cam.keyframe_insert("location", frame=1)
        cam.location = (base.x + 3, base.y, base.z)
        cam.keyframe_insert("location", frame=frames)
    elif kind == "detail":
        cam.location = (base.x, base.y * 0.5, base.z - 0.5)
        cam.data.lens = min(getattr(cam.data, "lens", 35) + 15, 85)
        cam.keyframe_insert("location", frame=1)
        cam.keyframe_insert("location", frame=frames)


def configure(sc, frames, path):
    sc.frame_start = 1
    sc.frame_end = frames
    sc.render.fps = FPS
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.image_settings.file_format = "FFMPEG"
    sc.render.ffmpeg.format = "MPEG4"
    sc.render.ffmpeg.codec = "H264"
    sc.render.ffmpeg.constant_rate_factor = "MEDIUM"
    sc.render.ffmpeg.audio_codec = "NONE"
    if hasattr(sc.eevee, "taa_render_samples"):
        sc.eevee.taa_render_samples = 16  # faster kinetic takes
    sc.render.filepath = path


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("=== KINETIC B-ROLL RENDER ===")
    for sname in SCENES:
        if sname not in bpy.data.scenes:
            print(f"SKIP missing {sname}")
            continue
        sc = bpy.data.scenes[sname]
        bpy.context.window.scene = sc
        cam = get_cam(sc)
        for suffix, frames, kind in TAKES:
            out = os.path.join(OUT_DIR, f"{sname}_broll_{suffix}.mp4")
            if os.path.isfile(out) and os.path.getsize(out) > 200_000:
                print(f"SKIP {out}")
                continue
            mutate_camera(cam, kind, frames)
            configure(sc, frames, out)
            print(f"RENDER {sname} {suffix} ({frames}f) → {out}", flush=True)
            try:
                bpy.ops.render.render(animation=True)
            except Exception as e:
                print(f"FAIL {sname} {suffix}: {e}")
    print("=== DONE ===")


if __name__ == "__main__":
    main()
