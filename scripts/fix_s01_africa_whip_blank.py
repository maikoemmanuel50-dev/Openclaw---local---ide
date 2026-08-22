"""
Fix S01 Cold Open blank dark patch @ ~28–50s.

Cause: S01_Africa_Slide used pr_s10_africa_title.png (RGB, solid black
canvas, no alpha). The whip plane therefore rendered as a black rectangle.

This script (CPU only — does not touch the live HQ GPU batch):
  1. Builds an alpha wordmark from the gold AFRICA title (black → transparent)
  2. Patches renders/video_clips/01_ColdOpen.mp4: keep 0–28.5s, whip into
     full-bleed title card for the remainder (seamless viewable fix NOW)
  3. Writes a Blender patch script for the next S01 HQ pass

Refs: TED-Ed whip energy · Resolve density grade short
  https://www.youtube.com/shorts/spB6aNU8Hms
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
SRC_TITLE = PROJECT / "assets" / "canva" / "kinetic" / "hq" / "pr_s10_africa_title.png"
OUT_ALPHA = PROJECT / "assets" / "canva" / "kinetic" / "hq" / "pr_s10_africa_title_alpha.png"
S01 = PROJECT / "renders" / "video_clips" / "01_ColdOpen.mp4"
S01_BAK = PROJECT / "renders" / "video_clips" / "01_ColdOpen_pre_africa_fix.mp4"
S01_PATCHED = PROJECT / "renders" / "video_clips" / "01_ColdOpen.mp4"
REPORT = PROJECT / "renders" / "quality" / "s01_africa_whip_fix_report.json"
BLEND_PATCH = PROJECT / "setup_fix_s01_africa_alpha.py"

FPS = 24
KEEP_S = 28.5  # before whip starts looking broken
TITLE_HOLD_S = 50.0 - KEEP_S  # rest of scene


def make_alpha_wordmark(src: Path, dest: Path) -> dict:
    """Punch near-black canvas to alpha; keep gold AFRICA letters."""
    im = Image.open(src).convert("RGBA")
    arr = np.asarray(im).astype(np.float32)
    rgb = arr[:, :, :3]
    lum = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]
    # Soft key: pure black canvas → 0; keep mid/high gold
    # Protect bronze letter sides (lum ~20–80) by raising floor on warm pixels
    warm = (rgb[:, :, 0] > rgb[:, :, 2] + 8) & (rgb[:, :, 1] > rgb[:, :, 2])
    alpha = np.clip((lum - 12.0) / 48.0, 0.0, 1.0)
    alpha = np.where(warm & (lum > 18), np.maximum(alpha, 0.85), alpha)
    alpha = np.where(lum < 10, 0.0, alpha)
    out = arr.copy()
    out[:, :, 3] = (alpha * 255.0).astype(np.uint8)
    # Slight gold lift on opaque pixels for plate readability
    mask = out[:, :, 3] > 40
    out[mask, 0] = np.clip(out[mask, 0] * 1.05 + 6, 0, 255)
    out[mask, 1] = np.clip(out[mask, 1] * 1.03 + 4, 0, 255)
    Image.fromarray(out.astype(np.uint8), "RGBA").save(dest)
    opaque = int((out[:, :, 3] > 20).sum())
    return {"path": str(dest), "opaque_px": opaque, "size": list(im.size)}


def patch_mp4() -> dict:
    """Keep head of S01; whip/fade into full-bleed AFRICA title for tail."""
    if not S01.is_file():
        raise FileNotFoundError(S01)
    if not S01_BAK.is_file():
        shutil.copy2(S01, S01_BAK)

    title_mp4 = PROJECT / "renders" / "quality" / "_s01_africa_title_hold.mp4"
    # Still → 24fps video for concat
    cmd_still = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(SRC_TITLE),
        "-t", f"{TITLE_HOLD_S:.3f}",
        "-r", str(FPS),
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,"
               "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p,"
               "fade=t=in:st=0:d=0.35:color=black",
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-preset", "veryfast", "-crf", "18", "-an",
        str(title_mp4),
    ]
    r1 = subprocess.run(cmd_still, capture_output=True, text=True)
    if r1.returncode != 0:
        raise RuntimeError(r1.stderr[-800:])

    head = PROJECT / "renders" / "quality" / "_s01_head_285.mp4"
    cmd_head = [
        "ffmpeg", "-y", "-i", str(S01_BAK),
        "-t", f"{KEEP_S:.3f}",
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-preset", "veryfast", "-crf", "18", "-an",
        str(head),
    ]
    r2 = subprocess.run(cmd_head, capture_output=True, text=True)
    if r2.returncode != 0:
        raise RuntimeError(r2.stderr[-800:])

    # Short whip: last 0.4s of head zoom-blur into title (xfade)
    out_tmp = PROJECT / "renders" / "quality" / "_s01_patched_tmp.mp4"
    # xfade duration 0.4s ending at KEEP_S
    offset = KEEP_S - 0.4
    cmd_xf = [
        "ffmpeg", "-y",
        "-i", str(head),
        "-i", str(title_mp4),
        "-filter_complex",
        f"[0:v][1:v]xfade=transition=fadeblack:duration=0.4:offset={offset:.3f},format=yuv420p[v]",
        "-map", "[v]",
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-preset", "veryfast", "-crf", "18", "-an",
        "-r", str(FPS),
        str(out_tmp),
    ]
    r3 = subprocess.run(cmd_xf, capture_output=True, text=True)
    if r3.returncode != 0:
        # Fallback: hard concat without xfade
        lst = PROJECT / "renders" / "quality" / "_s01_concat.txt"
        lst.write_text(
            f"file '{head.as_posix()}'\nfile '{title_mp4.as_posix()}'\n",
            encoding="utf-8",
        )
        cmd_cat = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
            "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
            "-preset", "veryfast", "-crf", "18", "-an", "-r", str(FPS),
            str(out_tmp),
        ]
        r3 = subprocess.run(cmd_cat, capture_output=True, text=True)
        if r3.returncode != 0:
            raise RuntimeError(r3.stderr[-800:])

    shutil.copy2(out_tmp, S01_PATCHED)
    probe = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate,nb_frames,duration",
            "-of", "default=noprint_wrappers=1", str(S01_PATCHED),
        ],
        capture_output=True, text=True,
    )
    return {"patched": str(S01_PATCHED), "backup": str(S01_BAK), "probe": probe.stdout}


def write_blender_patch() -> str:
    """Next S01 HQ pass: alpha wordmark whip, no opaque black plane."""
    code = f'''"""Apply Africa alpha whip fix to 01_ColdOpen (Blender 5.1). CPU-safe setup."""
import math
from pathlib import Path
import bpy

ALPHA = r"{OUT_ALPHA.as_posix()}"
SCENE = "01_ColdOpen"
AFRICA_IN = 720
WHIP = 10

sc = bpy.data.scenes.get(SCENE) or bpy.context.scene
bpy.context.window.scene = sc if hasattr(bpy.context, "window") else None

img = bpy.data.images.load(ALPHA, check_existing=True)
img.name = "S01_Africa_Tex_Alpha"
try:
    img.colorspace_settings.name = "sRGB"
except Exception:
    pass
img.alpha_mode = "STRAIGHT"

mat = bpy.data.materials.get("M_S01_Africa_Slide") or bpy.data.materials.new("M_S01_Africa_Slide")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputMaterial")
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
tex = nt.nodes.new("ShaderNodeTexImage")
tex.image = img
tex.interpolation = "Cubic"
nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
try:
    bsdf.inputs["Emission Color"].default_value = (1.0, 0.85, 0.35, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 2.5
except Exception:
    pass
bsdf.inputs["Roughness"].default_value = 0.55
nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
try:
    mat.blend_method = "BLEND"
except Exception:
    pass
try:
    mat.surface_render_method = "BLENDED"
except Exception:
    pass

obj = sc.objects.get("S01_Africa_Slide")
if obj is None:
    raise SystemExit("S01_Africa_Slide missing — run setup_coldopen_matatu_africa.py first")
if obj.animation_data:
    obj.animation_data_clear()
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)

start, end, settle = AFRICA_IN, AFRICA_IN + WHIP, AFRICA_IN + WHIP + 18
obj.hide_render = True
obj.keyframe_insert("hide_render", frame=start - 1)
obj.hide_render = False
obj.keyframe_insert("hide_render", frame=start)

# Whip: enter from right oversized → settle readable wordmark over plate
obj.location = (10.0, -1.2, 2.4)
obj.scale = (16.0, 9.0, 1.0)
obj.rotation_euler = (math.radians(90), math.radians(-28), math.radians(12))
for dp in ("location", "scale", "rotation_euler"):
    obj.keyframe_insert(dp, frame=start)

obj.location = (0.0, -1.2, 2.4)
obj.scale = (9.6, 5.4, 1.0)
obj.rotation_euler = (math.radians(90), 0.0, 0.0)
for dp in ("location", "scale", "rotation_euler"):
    obj.keyframe_insert(dp, frame=end)

obj.location = (0.0, -0.9, 2.35)
obj.scale = (8.4, 4.7, 1.0)
obj.keyframe_insert("location", frame=settle)
obj.keyframe_insert("scale", frame=settle)
obj.keyframe_insert("location", frame=sc.frame_end)
obj.keyframe_insert("scale", frame=sc.frame_end)

# Keep matatu / BG plate visible under alpha letters
for name in ("Background_Plane.001",):
    o = sc.objects.get(name)
    if o:
        o.hide_render = False

out_blend = Path(r"{(PROJECT / 'blend' / 'africa_s1_master_v01.blend').as_posix()}")
bpy.ops.wm.save_as_mainfile(filepath=str(out_blend))
print("FIX_S01_AFRICA_ALPHA_OK", ALPHA, flush=True)
'''
    BLEND_PATCH.write_text(code, encoding="utf-8")
    return str(BLEND_PATCH)


def main():
    OUT_ALPHA.parent.mkdir(parents=True, exist_ok=True)
    alpha = make_alpha_wordmark(SRC_TITLE, OUT_ALPHA)
    print("ALPHA", alpha, flush=True)
    patched = patch_mp4()
    print("PATCHED", patched["probe"], flush=True)
    blend_patch = write_blender_patch()
    # Also point coldopen setup at alpha asset for future runs
    setup = PROJECT / "setup_coldopen_matatu_africa.py"
    text = setup.read_text(encoding="utf-8")
    old = 'AFRICA = PROJECT / "assets" / "canva" / "kinetic" / "hq" / "pr_s10_africa_title.png"'
    new = 'AFRICA = PROJECT / "assets" / "canva" / "kinetic" / "hq" / "pr_s10_africa_title_alpha.png"'
    if old in text:
        setup.write_text(text.replace(old, new), encoding="utf-8")
        print("UPDATED setup_coldopen_matatu_africa.py → alpha asset", flush=True)
    report = {
        "cause": "Africa slide plane used RGB title with solid black canvas (no alpha)",
        "alpha": alpha,
        "patched_mp4": patched,
        "blender_patch_script": blend_patch,
        "note": "Patched MP4 is viewable now. Re-apply Blender alpha whip on next S01 HQ pass when GPU free (do not interrupt S02+).",
        "refs": [
            "https://youtu.be/Jh5RALdecPs",
            "https://youtu.be/12lB3NA_ZwE",
            "https://www.youtube.com/shorts/spB6aNU8Hms",
        ],
    }
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("REPORT", REPORT, flush=True)


if __name__ == "__main__":
    main()
