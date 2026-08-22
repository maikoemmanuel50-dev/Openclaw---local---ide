"""
Build partial integrated stem from available scene clips + open30 S01 merge.

Output: renders/quality/episode_stem_partial.mp4 (silent, available scenes only)

Run: python scripts/assemble_partial_stem.py
"""
from __future__ import annotations

import os
import subprocess
import sys

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
CLIPS = os.path.join(PROJECT, "renders", "video_clips")
OUT = os.path.join(PROJECT, "renders", "quality", "episode_stem_partial.mp4")
SCENES = [
    "01_ColdOpen", "02_Context2007", "03_Beat1_Hubs", "04_Beat1_Phone",
    "05_Beat2_Money", "06_Beat2_Solar", "07_Beat3_Gap", "08_Beat3_SecondaryCity",
    "09_Closer", "10_EndCard",
]


def main():
    merge = os.path.join(PROJECT, "scripts", "merge_open30_into_s01.py")
    if os.path.isfile(merge):
        subprocess.run([sys.executable, merge], cwd=PROJECT, check=False)

    paths = []
    s01 = os.path.join(CLIPS, "01_ColdOpen_with_open30.mp4")
    if os.path.isfile(s01) and os.path.getsize(s01) > 200_000:
        paths.append(s01)
    elif os.path.isfile(os.path.join(CLIPS, "01_ColdOpen.mp4")):
        paths.append(os.path.join(CLIPS, "01_ColdOpen.mp4"))

    for s in SCENES[1:]:
        p = os.path.join(CLIPS, f"{s}.mp4")
        if os.path.isfile(p) and os.path.getsize(p) > 200_000:
            paths.append(p)

    if len(paths) < 1:
        print("No clips available")
        return 1

    listf = os.path.join(PROJECT, "renders", "quality", "_partial_concat.txt")
    with open(listf, "w", encoding="utf-8") as f:
        for p in paths:
            f.write(f"file '{p.replace(chr(92), '/')}'\n")

    import shutil
    ff = shutil.which("ffmpeg")
    cmd = [
        ff, "-y", "-f", "concat", "-safe", "0", "-i", listf,
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-b:v", "10M", "-r", "24", "-an", OUT,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-500:])
        return r.returncode
    print("PARTIAL_STEM", OUT, "scenes=", len(paths))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
