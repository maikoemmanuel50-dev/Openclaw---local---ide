"""
Africa S1 — Camera setup + per-scene MP4 render + ffmpeg assembly.
Run: blender -b africa_s1_master_v01.blend -P setup_cameras_and_render.py
Or with args: --render-only --assemble-only
"""
import bpy
import math
import os
import sys
import subprocess

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
BLEND = os.path.join(PROJECT, "blend", "africa_s1_master_v01.blend")
RENDER_DIR = os.path.join(PROJECT, "renders", "video_clips")
OUTPUT = os.path.join(PROJECT, "Africa_S1_Silicon_Savannah_7min.mp4")
FPS = 24
TOTAL_SECONDS = 420  # 7 minutes

# Scene durations (seconds) — weighted by narration/script sections
SCENE_DURATIONS = {
    "01_ColdOpen": 50,
    "02_Context2007": 45,
    "03_Beat1_Hubs": 45,
    "04_Beat1_Phone": 25,
    "05_Beat2_Money": 45,
    "06_Beat2_Solar": 40,
    "07_Beat3_Gap": 50,
    "08_Beat3_SecondaryCity": 35,
    "09_Closer": 55,
    "10_EndCard": 15,
}

# Pad to exactly 7 minutes
current = sum(SCENE_DURATIONS.values())
if current != TOTAL_SECONDS:
    diff = TOTAL_SECONDS - current
    SCENE_DURATIONS["09_Closer"] += diff  # add remainder to closer

SCENE_ORDER = list(SCENE_DURATIONS.keys())
XFADE_SECONDS = 1.0  # crossfade between clips


def get_cam(scene):
    for o in scene.objects:
        if o.type == "CAMERA":
            return o
    return None


def clear_cam_anim(cam):
    if cam.animation_data:
        cam.animation_data_clear()


def set_linear_interp(cam):
    if not cam.animation_data or not cam.animation_data.action:
        return
    for fc in cam.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
            kp.handle_left_type = "AUTO_CLAMPED"
            kp.handle_right_type = "AUTO_CLAMPED"


def setup_camera_push_in(cam, frames, dist_start=18, dist_end=11, z=5, y=-14):
    clear_cam_anim(cam)
    f0, f1 = 1, frames
    cam.location = (0, -dist_start, z)
    cam.rotation_euler = (math.radians(80), 0, 0)
    cam.keyframe_insert("location", frame=f0)
    cam.keyframe_insert("rotation_euler", frame=f0)
    cam.location = (0, -dist_end, z + 0.3)
    cam.keyframe_insert("location", frame=f1)
    set_linear_interp(cam)


def setup_camera_pan(cam, frames, x_start=-5, x_end=5, y=-14, z=5):
    clear_cam_anim(cam)
    f0, f1 = 1, frames
    cam.location = (x_start, y, z)
    cam.rotation_euler = (math.radians(80), 0, math.radians(6))
    cam.keyframe_insert("location", frame=f0)
    cam.keyframe_insert("rotation_euler", frame=f0)
    cam.location = (x_end, y, z)
    cam.rotation_euler = (math.radians(80), 0, math.radians(-6))
    cam.keyframe_insert("location", frame=f1)
    cam.keyframe_insert("rotation_euler", frame=f1)
    set_linear_interp(cam)


def setup_camera_parallax(cam, frames, y=-14, z=4.5):
    clear_cam_anim(cam)
    f0, f1 = 1, frames
    cam.location = (-2.5, y, z)
    cam.rotation_euler = (math.radians(82), 0, math.radians(8))
    cam.keyframe_insert("location", frame=f0)
    cam.keyframe_insert("rotation_euler", frame=f0)
    cam.location = (2.5, y, z + 0.2)
    cam.rotation_euler = (math.radians(82), 0, math.radians(-8))
    cam.keyframe_insert("location", frame=f1)
    cam.keyframe_insert("rotation_euler", frame=f1)
    set_linear_interp(cam)


def setup_camera_zoom_out(cam, frames):
    clear_cam_anim(cam)
    cam.data.lens = 55
    cam.location = (0, -5, 2.5)
    cam.rotation_euler = (math.radians(88), 0, 0)
    cam.keyframe_insert("location", frame=1)
    cam.keyframe_insert("rotation_euler", frame=1)
    cam.data.keyframe_insert("lens", frame=1)
    mid = int(frames * 0.35)
    cam.location = (0, -10, 4)
    cam.rotation_euler = (math.radians(78), 0, 0)
    cam.data.lens = 35
    cam.keyframe_insert("location", frame=mid)
    cam.keyframe_insert("rotation_euler", frame=mid)
    cam.data.keyframe_insert("lens", frame=mid)
    cam.location = (0, -20, 6.5)
    cam.rotation_euler = (math.radians(72), 0, 0)
    cam.data.lens = 28
    cam.keyframe_insert("location", frame=frames)
    cam.keyframe_insert("rotation_euler", frame=frames)
    cam.data.keyframe_insert("lens", frame=frames)
    set_linear_interp(cam)


def setup_camera_subtle_drift(cam, frames):
    clear_cam_anim(cam)
    cam.location = (0, -12, 4)
    cam.rotation_euler = (math.radians(82), 0, 0)
    cam.keyframe_insert("location", frame=1)
    cam.location = (0.4, -12, 4.15)
    cam.rotation_euler = (math.radians(81), 0, math.radians(-2))
    cam.keyframe_insert("location", frame=frames)
    cam.keyframe_insert("rotation_euler", frame=frames)
    set_linear_interp(cam)


def setup_camera_chart(cam, frames):
    clear_cam_anim(cam)
    cam.location = (0, -16, 5.5)
    cam.rotation_euler = (math.radians(72), 0, 0)
    cam.data.lens = 32
    cam.keyframe_insert("location", frame=1)
    cam.keyframe_insert("rotation_euler", frame=1)
    cam.location = (0, -11, 4.8)
    cam.rotation_euler = (math.radians(76), 0, 0)
    cam.keyframe_insert("location", frame=frames)
    cam.keyframe_insert("rotation_euler", frame=frames)
    set_linear_interp(cam)


CAMERA_PRESETS = {
    "01_ColdOpen": setup_camera_push_in,
    "02_Context2007": setup_camera_pan,
    "03_Beat1_Hubs": setup_camera_parallax,
    "04_Beat1_Phone": lambda c, f: setup_camera_push_in(c, f, 14, 9, 4.5, -12),
    "05_Beat2_Money": setup_camera_chart,
    "06_Beat2_Solar": setup_camera_parallax,
    "07_Beat3_Gap": setup_camera_zoom_out,
    "08_Beat3_SecondaryCity": setup_camera_parallax,
    "09_Closer": setup_camera_push_in,
    "10_EndCard": setup_camera_subtle_drift,
}


def setup_all_cameras():
    print("=== SETUP CAMERAS ===")
    for sname in SCENE_ORDER:
        sc = bpy.data.scenes[sname]
        frames = SCENE_DURATIONS[sname] * FPS
        sc.frame_start = 1
        sc.frame_end = frames
        sc.render.fps = FPS
        cam = get_cam(sc)
        if cam:
            cam.data.dof.use_dof = sname in {
                "01_ColdOpen", "03_Beat1_Hubs", "04_Beat1_Phone",
                "06_Beat2_Solar", "08_Beat3_SecondaryCity", "09_Closer",
            }
            if cam.data.dof.use_dof:
                cam.data.dof.aperture_fstop = 2.8
                cam.data.dof.focus_distance = 14
            CAMERA_PRESETS[sname](cam, frames)
            print(f"  {sname}: {frames} frames ({SCENE_DURATIONS[sname]}s) — {CAMERA_PRESETS[sname].__name__}")
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("Saved blend.")


def configure_render(sc):
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.resolution_percentage = 100
    sc.render.fps = FPS
    sc.render.image_settings.file_format = "FFMPEG"
    sc.render.ffmpeg.format = "MPEG4"
    sc.render.ffmpeg.codec = "H264"
    sc.render.ffmpeg.constant_rate_factor = "HIGH"
    sc.render.ffmpeg.ffmpeg_preset = "GOOD"
    sc.render.ffmpeg.audio_codec = "NONE"
    if hasattr(sc.eevee, "taa_render_samples"):
        sc.eevee.taa_render_samples = 64


def render_all_scenes():
    os.makedirs(RENDER_DIR, exist_ok=True)
    print("=== RENDER SCENES ===")
    for sname in SCENE_ORDER:
        sc = bpy.data.scenes[sname]
        bpy.context.window.scene = sc
        configure_render(sc)
        out = os.path.join(RENDER_DIR, f"{sname}.mp4")
        sc.render.filepath = out
        print(f"Rendering {sname} -> {out} ({sc.frame_end} frames)...")
        bpy.ops.render.render(animation=True)
        print(f"  DONE {sname}")
    print("All scene renders complete.")


def find_ffmpeg():
    import shutil
    ff = shutil.which("ffmpeg")
    if ff:
        return ff
    candidates = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


def assemble_with_ffmpeg():
    ff = find_ffmpeg()
    if not ff:
        print("ERROR: ffmpeg not found. Install with: winget install Gyan.FFmpeg")
        return False

    clips = [os.path.join(RENDER_DIR, f"{s}.mp4") for s in SCENE_ORDER]
    for c in clips:
        if not os.path.isfile(c):
            print(f"MISSING: {c}")
            return False

    # Build xfade filter chain
    # offset for each xfade = cumulative duration - (n * xfade)
    xfade_f = int(XFADE_SECONDS * FPS)
    filter_parts = []
    cumul = SCENE_DURATIONS[SCENE_ORDER[0]]
    inputs = "".join(f"-i \"{c}\" " for c in clips)

    if len(clips) == 1:
        cmd = f'"{ff}" -y -i "{clips[0]}" -c copy "{OUTPUT}"'
        subprocess.run(cmd, shell=True, check=True)
        return True

    # Use concat demuxer with crossfade via complex filter
    prev = "[0:v]"
    offset = SCENE_DURATIONS[SCENE_ORDER[0]] - XFADE_SECONDS
    for i in range(1, len(clips)):
        nxt = f"[v{i}]" if i < len(clips) - 1 else "[vout]"
        filter_parts.append(
            f"{prev}[{i}:v]xfade=transition=fade:duration={XFADE_SECONDS}:offset={offset}{nxt}"
        )
        prev = nxt
        if i < len(clips) - 1:
            offset += SCENE_DURATIONS[SCENE_ORDER[i]] - XFADE_SECONDS

    filter_complex = ";".join(filter_parts)
    input_args = " ".join(f'-i "{c}"' for c in clips)
    cmd = f'"{ff}" -y {input_args} -filter_complex "{filter_complex}" -map "[vout]" -c:v libx264 -crf 18 -preset medium -an "{OUTPUT}"'

    print(f"=== ASSEMBLE ===\n{cmd[:200]}...")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print("ffmpeg stderr:", r.stderr[-2000:])
        # Fallback: simple concat without xfade
        print("Fallback: concat without crossfade...")
        list_file = os.path.join(RENDER_DIR, "concat_list.txt")
        with open(list_file, "w") as f:
            for c in clips:
                f.write(f"file '{c.replace(chr(92), '/')}'\n")
        cmd2 = f'"{ff}" -y -f concat -safe 0 -i "{list_file}" -c copy "{OUTPUT}"'
        subprocess.run(cmd2, shell=True, check=True)
    print(f"OUTPUT: {OUTPUT}")
    return os.path.isfile(OUTPUT)


def main():
    args = sys.argv
    if "--assemble-only" in args:
        assemble_with_ffmpeg()
        return
    if "--render-only" in args:
        render_all_scenes()
        return
    setup_all_cameras()
    render_all_scenes()
    assemble_with_ffmpeg()


if __name__ == "__main__":
    main()
