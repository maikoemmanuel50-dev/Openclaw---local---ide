"""
Build a complete ~7-minute silent video for AFRICA S1 Episode 1.
Uses: hero PNGs (Ken Burns), bar-chart animation, Canva assets, free stock B-roll.
Output: Africa_S1_Silicon_Savannah_7min_silent.mp4
"""
from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
import urllib.request

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
RENDERS = os.path.join(PROJECT, "renders")
CLIPS_DIR = os.path.join(RENDERS, "video_clips")
BUILD_DIR = os.path.join(RENDERS, "built_clips")
STOCK_DIR = os.path.join(PROJECT, "assets", "stock")
OUTPUT = os.path.join(PROJECT, "Africa_S1_Silicon_Savannah_7min_silent.mp4")
OUTPUT_ALT = os.path.join(PROJECT, "Africa_S1_Silicon_Savannah_7min.mp4")
FPS = 24
XFADE = 1.0

# (scene_key, duration_sec, motion preset)
SCENES = [
    ("01_ColdOpen", 50, "push_in"),
    ("02_Context2007", 45, "pan_lr"),
    ("03_Beat1_Hubs", 45, "parallax"),
    ("04_Beat1_Phone", 25, "push_in_tight"),
    ("05_Beat2_Money", 45, "anim"),
    ("06_Beat2_Solar", 40, "parallax"),
    ("07_Beat3_Gap", 50, "zoom_out"),
    ("08_Beat3_SecondaryCity", 35, "parallax"),
    ("09_Closer", 70, "push_in"),
    ("10_EndCard", 15, "drift"),
]

# Free Mixkit stock (CC0) — Nairobi/tech/solar B-roll supplements
STOCK_URLS = {
    "city_dawn": "https://assets.mixkit.co/videos/preview/mixkit-city-traffic-at-night-with-blurred-lights-4445-large.mp4",
    "phone_hands": "https://assets.mixkit.co/videos/preview/mixkit-hands-of-a-person-typing-on-a-smartphone-34506-large.mp4",
    "solar_roof": "https://assets.mixkit.co/videos/preview/mixkit-solar-panels-on-a-roof-5045-large.mp4",
    "africa_landscape": "https://assets.mixkit.co/videos/preview/mixkit-aerial-view-of-a-city-at-sunrise-4439-large.mp4",
}

STOCK_SCENE_MAP = {
    "01_ColdOpen": "city_dawn",
    "04_Beat1_Phone": "phone_hands",
    "06_Beat2_Solar": "solar_roof",
    "09_Closer": "africa_landscape",
}


def find_ffmpeg() -> str:
    ff = shutil.which("ffmpeg")
    if ff:
        return ff
    winget = os.path.join(
        os.path.expandvars(r"%LOCALAPPDATA%"),
        "Microsoft", "WinGet", "Packages",
        "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe",
    )
    if os.path.isdir(winget):
        for root, _, files in os.walk(winget):
            if "ffmpeg.exe" in files:
                return os.path.join(root, "ffmpeg.exe")
    raise RuntimeError("ffmpeg not found")


def run(cmd: list[str], label: str = "") -> None:
    print(f"  >> {label or cmd[0]}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1500:])
        raise RuntimeError(f"Command failed: {label or 'ffmpeg'}")


def download_stock() -> dict[str, str]:
    os.makedirs(STOCK_DIR, exist_ok=True)
    paths = {}
    for key, url in STOCK_URLS.items():
        dest = os.path.join(STOCK_DIR, f"{key}.mp4")
        if os.path.isfile(dest) and os.path.getsize(dest) > 100_000:
            paths[key] = dest
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AfricaS1/1.0"})
            with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as f:
                f.write(resp.read())
            if os.path.getsize(dest) > 100_000:
                paths[key] = dest
                print(f"  OK stock: {key}")
            else:
                os.remove(dest)
        except Exception as e:
            print(f"  SKIP stock {key}: {e}")
    return paths


def hero_path(scene: str) -> str:
    folder = os.path.join(RENDERS, scene)
    matches = glob.glob(os.path.join(folder, f"{scene}_hero.png"))
    if matches:
        return matches[0]
    raise FileNotFoundError(f"No hero PNG for {scene}")


def motion_filter(preset: str, frames: int) -> str:
    d = frames
    if preset == "push_in":
        return (
            f"scale=2560:1440:force_original_aspect_ratio=increase,crop=2560:1440,"
            f"zoompan=z='min(1.0+0.0006*on,1.35)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={d}:s=1920x1080:fps={FPS}"
        )
    if preset == "push_in_tight":
        return (
            f"scale=2560:1440:force_original_aspect_ratio=increase,crop=2560:1440,"
            f"zoompan=z='min(1.1+0.001*on,1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={d}:s=1920x1080:fps={FPS}"
        )
    if preset == "pan_lr":
        return (
            f"scale=2560:1440:force_original_aspect_ratio=increase,crop=2560:1440,"
            f"zoompan=z='1.25':x='(iw-iw/zoom)*on/{d}':y='(ih-ih/zoom)/2':"
            f"d={d}:s=1920x1080:fps={FPS}"
        )
    if preset == "parallax":
        return (
            f"scale=2560:1440:force_original_aspect_ratio=increase,crop=2560:1440,"
            f"zoompan=z='1.2':x='(iw-iw/zoom)*(0.5+0.5*sin(2*PI*on/{d}))':y='(ih-ih/zoom)/2':"
            f"d={d}:s=1920x1080:fps={FPS}"
        )
    if preset == "zoom_out":
        return (
            f"scale=2560:1440:force_original_aspect_ratio=increase,crop=2560:1440,"
            f"zoompan=z='max(1.4-0.0008*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={d}:s=1920x1080:fps={FPS}"
        )
    if preset == "drift":
        return (
            f"scale=2560:1440:force_original_aspect_ratio=increase,crop=2560:1440,"
            f"zoompan=z='1.08':x='(iw-iw/zoom)*(0.48+0.04*sin(2*PI*on/{d}))':"
            f"y='(ih-ih/zoom)*(0.48+0.04*cos(2*PI*on/{d}))':"
            f"d={d}:s=1920x1080:fps={FPS}"
        )
    raise ValueError(preset)


def build_from_hero(ff: str, scene: str, duration: int, motion: str, out: str) -> None:
    img = hero_path(scene)
    frames = duration * FPS
    vf = motion_filter(motion, frames)
    run([
        ff, "-y", "-loop", "1", "-i", img,
        "-vf", vf, "-t", str(duration),
        "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-an", out,
    ], f"hero {scene}")


def build_from_anim(ff: str, scene: str, duration: int, out: str) -> None:
    anim_dir = os.path.join(RENDERS, scene, "anim")
    pattern = os.path.join(anim_dir, "frame_*.png")
    frames_list = sorted(glob.glob(pattern))
    if not frames_list:
        build_from_hero(ff, scene, duration, "push_in", out)
        return
    # Loop animation to fill duration
    list_file = os.path.join(BUILD_DIR, f"{scene}_frames.txt")
    target_frames = duration * FPS
    with open(list_file, "w") as f:
        idx = 0
        for i in range(target_frames):
            f.write(f"file '{frames_list[idx % len(frames_list)].replace(chr(92), '/')}'\n")
            f.write(f"duration {1/FPS}\n")
            idx += 1
        f.write(f"file '{frames_list[-1].replace(chr(92), '/')}'\n")
    run([
        ff, "-y", "-f", "concat", "-safe", "0", "-i", list_file,
        "-vf", f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-an", out,
    ], f"anim {scene}")


def blend_stock(ff: str, hero_clip: str, stock: str, duration: int, out: str) -> None:
    """Blend stock B-roll (first 30%) with hero clip using crossfade."""
    stock_d = min(8, int(duration * 0.3))
    hero_d = duration - stock_d + 1  # overlap 1s
    tmp_stock = out + ".stock.mp4"
    tmp_hero = out + ".hero.mp4"
    run([
        ff, "-y", "-i", stock, "-t", str(stock_d + 1),
        "-vf", f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps={FPS}",
        "-c:v", "libx264", "-crf", "20", "-an", tmp_stock,
    ], "trim stock")
    run([
        ff, "-y", "-i", hero_clip, "-t", str(hero_d),
        "-c:v", "libx264", "-crf", "18", "-an", tmp_hero,
    ], "trim hero")
    run([
        ff, "-y", "-i", tmp_stock, "-i", tmp_hero,
        "-filter_complex",
        f"[0:v][1:v]xfade=transition=fade:duration=1:offset={stock_d}[vout]",
        "-map", "[vout]", "-t", str(duration),
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-an", out,
    ], "blend stock+hero")
    for t in (tmp_stock, tmp_hero):
        if os.path.isfile(t):
            os.remove(t)


def prefer_blender_clip(scene: str) -> str | None:
    path = os.path.join(CLIPS_DIR, f"{scene}.mp4")
    if not os.path.isfile(path):
        return None
    size = os.path.getsize(path)
    # Require plausible size (>500KB per scene minimum)
    if size < 500_000:
        return None
    return path


def build_scene_clips(ff: str, stock_paths: dict[str, str]) -> list[str]:
    os.makedirs(BUILD_DIR, exist_ok=True)
    clips = []
    for scene, duration, motion in SCENES:
        out = os.path.join(BUILD_DIR, f"{scene}.mp4")
        blender = prefer_blender_clip(scene)
        if blender:
            print(f"[{scene}] Using Blender render")
            run([
                ff, "-y", "-i", blender, "-t", str(duration),
                "-vf", f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps={FPS}",
                "-c:v", "libx264", "-crf", "18", "-an", out,
            ], f"trim blender {scene}")
        elif motion == "anim":
            print(f"[{scene}] Building from bar-chart animation")
            build_from_anim(ff, scene, duration, out)
        else:
            print(f"[{scene}] Building Ken Burns from hero PNG")
            build_from_hero(ff, scene, duration, motion, out)

        stock_key = STOCK_SCENE_MAP.get(scene)
        if stock_key and stock_key in stock_paths and not blender:
            blended = os.path.join(BUILD_DIR, f"{scene}_blended.mp4")
            print(f"[{scene}] Blending stock B-roll")
            blend_stock(ff, out, stock_paths[stock_key], duration, blended)
            os.replace(blended, out)

        clips.append(out)
        mb = os.path.getsize(out) / (1024 * 1024)
        print(f"  -> {out} ({mb:.1f} MB)")
    return clips


def assemble_clips(ff: str, clips: list[str], output: str) -> None:
    durations = [d for _, d, _ in SCENES]
    if len(clips) == 1:
        shutil.copy2(clips[0], output)
        return

    parts = []
    prev = "[0:v]"
    offset = durations[0] - XFADE
    for i in range(1, len(clips)):
        label = f"[v{i}]" if i < len(clips) - 1 else "[vout]"
        parts.append(
            f"{prev}[{i}:v]xfade=transition=fadeblack:duration={XFADE}:offset={offset:.3f}{label}"
        )
        prev = label
        if i < len(clips) - 1:
            offset += durations[i] - XFADE

    fc = ";".join(parts)
    cmd = [ff, "-y"] + sum([["-i", c] for c in clips], []) + [
        "-filter_complex", fc, "-map", "[vout]",
        "-c:v", "libx264", "-crf", "17", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-an", output,
    ]
    print("Assembling final 7-min video with crossfades...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("xfade failed, concat fallback:", r.stderr[-800:])
        listf = os.path.join(BUILD_DIR, "concat.txt")
        with open(listf, "w") as f:
            for c in clips:
                f.write(f"file '{c.replace(chr(92), '/')}'\n")
        run([ff, "-y", "-f", "concat", "-safe", "0", "-i", listf,
             "-c", "copy", output], "concat")


def verify_duration(ff: str, path: str) -> float:
    r = subprocess.run(
        [ff, "-i", path, "-f", "null", "-"],
        capture_output=True, text=True,
    )
    import re
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    if m:
        h, mi, s = m.groups()
        return int(h) * 3600 + int(mi) * 60 + float(s)
    return 0.0


def main():
    print("=== AFRICA S1 — Build Complete Silent Video ===")
    ff = find_ffmpeg()
    print(f"ffmpeg: {ff}")

    print("\n--- Downloading free stock B-roll ---")
    stock_paths = download_stock()

    print("\n--- Building scene clips ---")
    clips = build_scene_clips(ff, stock_paths)

    print("\n--- Assembling final output ---")
    assemble_clips(ff, clips, OUTPUT)

    dur = verify_duration(ff, OUTPUT)
    size_mb = os.path.getsize(OUTPUT) / (1024 * 1024)
    print(f"\nDONE: {OUTPUT}")
    print(f"  Duration: {dur:.1f}s ({dur/60:.2f} min)")
    print(f"  Size: {size_mb:.1f} MB")

    # Also write canonical name if blender version doesn't exist yet
    if not os.path.isfile(OUTPUT_ALT):
        shutil.copy2(OUTPUT, OUTPUT_ALT)
        print(f"  Copied to: {OUTPUT_ALT}")

    # Write manifest for Resolve assembly
    manifest = os.path.join(PROJECT, "assembly_manifest.txt")
    with open(manifest, "w") as f:
        f.write(f"output={OUTPUT}\n")
        f.write(f"duration_sec={dur:.2f}\n")
        for c in clips:
            f.write(f"clip={c}\n")
    print(f"  Manifest: {manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
