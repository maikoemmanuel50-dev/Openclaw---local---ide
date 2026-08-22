"""Render all 10 scenes at 4K (3840x2160). Needs more VRAM/time than 1080p.
Run only when ready for true 4K master.
Output: renders/video_clips_4k/*.mp4
"""
import bpy
import os
import subprocess
import sys

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
RENDER_DIR = os.path.join(PROJECT, "renders", "video_clips_4k")
SCENE_ORDER = [
    "01_ColdOpen", "02_Context2007", "03_Beat1_Hubs", "04_Beat1_Phone",
    "05_Beat2_Money", "06_Beat2_Solar", "07_Beat3_Gap", "08_Beat3_SecondaryCity",
    "09_Closer", "10_EndCard",
]
EXPECTED_SEC = {
    "01_ColdOpen": 50, "02_Context2007": 45, "03_Beat1_Hubs": 45,
    "04_Beat1_Phone": 25, "05_Beat2_Money": 45, "06_Beat2_Solar": 40,
    "07_Beat3_Gap": 50, "08_Beat3_SecondaryCity": 35, "09_Closer": 70,
    "10_EndCard": 15,
}


def find_ffprobe():
    import shutil
    ff = shutil.which("ffprobe")
    if ff:
        return ff
    winget_root = os.path.join(
        os.path.expandvars(r"%LOCALAPPDATA%"),
        "Microsoft", "WinGet", "Packages",
        "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe",
    )
    if os.path.isdir(winget_root):
        for root, _, files in os.walk(winget_root):
            if "ffprobe.exe" in files:
                return os.path.join(root, "ffprobe.exe")
    return None


def clip_complete(path, min_sec):
    if not os.path.isfile(path) or os.path.getsize(path) < 400_000:
        return False
    ffprobe = find_ffprobe()
    if not ffprobe:
        return os.path.getsize(path) > min_sec * 200_000
    try:
        r = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True, timeout=30,
        )
        return float(r.stdout.strip()) >= min_sec - 0.5
    except Exception:
        return False


os.makedirs(RENDER_DIR, exist_ok=True)

for i, sname in enumerate(SCENE_ORDER, 1):
    out = os.path.join(RENDER_DIR, f"{sname}.mp4")
    if clip_complete(out, EXPECTED_SEC[sname]):
        print(f"[{i}/10] SKIP {sname}", flush=True)
        continue
    sc = bpy.data.scenes[sname]
    bpy.context.window.scene = sc
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = 3840
    sc.render.resolution_y = 2160
    sc.render.resolution_percentage = 100
    img = sc.render.image_settings
    if hasattr(img, "media_type"):
        img.media_type = "VIDEO"
    else:
        try:
            img.file_format = "FFMPEG"
        except TypeError:
            img.file_format = "PNG"
    sc.render.ffmpeg.format = "MPEG4"
    sc.render.ffmpeg.codec = "H264"
    try:
        sc.render.ffmpeg.constant_rate_factor = "HIGH"
    except TypeError:
        pass
    try:
        sc.render.ffmpeg.ffmpeg_preset = "GOOD"
    except TypeError:
        pass
    sc.render.ffmpeg.audio_codec = "NONE"
    # Full quality presets (restore for gated 4K): match HQ photoreal stack
    if hasattr(sc.eevee, "taa_render_samples"):
        sc.eevee.taa_render_samples = 128
    if hasattr(sc.eevee, "use_raytracing"):
        sc.eevee.use_raytracing = True
    if hasattr(sc.eevee, "shadow_ray_count"):
        sc.eevee.shadow_ray_count = 4
    if hasattr(sc.eevee, "shadow_step_count"):
        sc.eevee.shadow_step_count = 12
    opts = getattr(sc.eevee, "ray_tracing_options", None)
    if opts and hasattr(opts, "resolution_scale"):
        opts.resolution_scale = "1"
    if os.path.isfile(out):
        os.remove(out)
    sc.render.filepath = out
    print(f"[{i}/10] RENDER_START_4K {sname} frames={sc.frame_end} -> {out}", flush=True)
    try:
        bpy.ops.render.render(animation=True)
    except Exception as exc:
        print(f"[{i}/10] RENDER_FAIL {sname}: {exc}", flush=True)
        sys.exit(1)
    print(f"[{i}/10] RENDER_DONE_4K {sname}", flush=True)

print("ALL_SCENES_RENDERED_4K", flush=True)
