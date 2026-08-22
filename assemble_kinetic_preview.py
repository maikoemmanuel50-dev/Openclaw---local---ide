"""
Build a FAST-PACED kinetic B-roll preview from hero PNGs + yellow ball.
No external stock required — uses local renders/heroes and assets/yellow_ball.

Output: Africa_S1_Silicon_Savannah_KINETIC_preview.mp4
Run: python assemble_kinetic_preview.py
"""
from __future__ import annotations

import glob
import os
import shutil
import subprocess

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
RENDERS = os.path.join(PROJECT, "renders")
BALL = os.path.join(PROJECT, "assets", "yellow_ball")
BUILD = os.path.join(RENDERS, "kinetic_build")
OUTPUT = os.path.join(PROJECT, "Africa_S1_Silicon_Savannah_KINETIC_preview.mp4")
FPS = 24

# (scene, hero_duration_sec for spine flash, kinetic_cut_frames)
# Kinetic mode: many short pulses from same hero with different Ken Burns
SCENES = [
    ("01_ColdOpen", 8, [12, 10, 14, 8, 16, 10, 12]),
    ("02_Context2007", 6, [14, 10, 12, 16]),
    ("03_Beat1_Hubs", 6, [10, 8, 12, 10, 14, 8]),
    ("04_Beat1_Phone", 4, [8, 10, 8, 12, 8]),
    ("05_Beat2_Money", 10, [16, 12]),  # protect chart — fewer cuts
    ("06_Beat2_Solar", 6, [10, 12, 8, 14, 10]),
    ("07_Beat3_Gap", 8, [20]),  # hold for 97%
    ("08_Beat3_SecondaryCity", 5, [14, 18, 12]),
    ("09_Closer", 8, [10, 8, 12, 10, 8, 14]),
    ("10_EndCard", 4, [48]),
]

MOTIONS = [
    "z='min(1.0+0.002*on,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
    "z='1.3':x='(iw-iw/zoom)*on/{d}':y='(ih-ih/zoom)/2'",
    "z='1.25':x='(iw-iw/zoom)*(1-on/{d})':y='(ih-ih/zoom)/2'",
    "z='max(1.4-0.002*on,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
    "z='1.2':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)*on/{d}'",
]


def find_ffmpeg() -> str:
    ff = shutil.which("ffmpeg")
    if ff:
        return ff
    raise RuntimeError("ffmpeg not found")


def hero(scene: str) -> str:
    p = os.path.join(RENDERS, scene, f"{scene}_hero.png")
    if not os.path.isfile(p):
        matches = glob.glob(os.path.join(RENDERS, scene, "*hero*.png"))
        if matches:
            return matches[0]
        raise FileNotFoundError(p)
    return p


def run(cmd: list[str], label: str) -> None:
    print(f"  >> {label}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-800:])
        raise RuntimeError(label)


def make_cut(ff: str, img: str, frames: int, motion_i: int, out: str) -> None:
    d = frames
    m = MOTIONS[motion_i % len(MOTIONS)].format(d=d)
    vf = (
        f"scale=2560:1440:force_original_aspect_ratio=increase,crop=2560:1440,"
        f"zoompan={m}:d={d}:s=1920x1080:fps={FPS}"
    )
    run([
        ff, "-y", "-loop", "1", "-i", img,
        "-vf", vf, "-frames:v", str(frames),
        "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-an", out,
    ], os.path.basename(out))


def main():
    ff = find_ffmpeg()
    os.makedirs(BUILD, exist_ok=True)
    parts = []
    idx = 0
    for scene, _spine, cuts in SCENES:
        img = hero(scene)
        for j, frames in enumerate(cuts):
            out = os.path.join(BUILD, f"cut_{idx:04d}_{scene}.mp4")
            make_cut(ff, img, frames, idx + j, out)
            parts.append(out)
            idx += 1

    listf = os.path.join(BUILD, "concat.txt")
    with open(listf, "w", encoding="utf-8") as f:
        for p in parts:
            f.write(f"file '{p.replace(chr(92), '/')}'\n")

    # Concat silent kinetic picture
    silent = os.path.join(BUILD, "kinetic_silent.mp4")
    run([
        ff, "-y", "-f", "concat", "-safe", "0", "-i", listf,
        "-c", "copy", silent,
    ], "concat")

    # Optional: overlay yellow ball pulse from PNG (top-right)
    ball = os.path.join(BALL, "yb_sun_seed.png")
    music = os.path.join(PROJECT, "assets", "audio", "music", "ch02_daylight_lofi.wav")
    cmd = [ff, "-y", "-i", silent]
    fc_parts = []
    maps = ["-map", "0:v"]
    if os.path.isfile(ball):
        cmd += ["-loop", "1", "-i", ball]
        fc_parts.append(
            "[1:v]scale=120:120,format=rgba,colorchannelmixer=aa=0.9[ball];"
            "[0:v][ball]overlay=W-w-40:40:shortest=1[vout]"
        )
        maps = ["-map", "[vout]"]
    if os.path.isfile(music):
        cmd += ["-stream_loop", "-1", "-i", music]
        a_idx = 2 if os.path.isfile(ball) else 1
        if fc_parts:
            fc_parts.append(f"[{a_idx}:a]volume=0.2[a]")
            maps += ["-map", "[a]"]
        else:
            maps += ["-map", f"{a_idx}:a"]

    if fc_parts:
        cmd += ["-filter_complex", ";".join(fc_parts)]
    cmd += maps + [
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-shortest", OUTPUT,
    ]
    run(cmd, "final kinetic preview")
    print(f"DONE: {OUTPUT} ({os.path.getsize(OUTPUT)/1024/1024:.1f} MB)")
    print(f"Cuts: {len(parts)} — kinetic ASL ~0.5s")


if __name__ == "__main__":
    main()
