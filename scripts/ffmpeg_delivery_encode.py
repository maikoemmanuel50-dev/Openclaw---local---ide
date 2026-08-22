"""
2-pass H.264 delivery encode — docs/DELIVERY_STANDARDS.md (1080p, 8–12 Mbps VBR).

Usage:
  python scripts/ffmpeg_delivery_encode.py <input> <output.mp4> [--bitrate 10M]
  python scripts/ffmpeg_delivery_encode.py frames_dir/ output.mp4

Input: PNG sequence (frame_*.png / ####.png) or any video file.
"""
from __future__ import annotations

import argparse
import glob
import os
import shutil
import subprocess
import sys


def ff() -> str:
    x = shutil.which("ffmpeg")
    if not x:
        raise RuntimeError("ffmpeg required on PATH")
    return x


def detect_input(path: str) -> tuple[str, list[str]]:
    if os.path.isdir(path):
        patterns = [
            os.path.join(path, "frame_*.png"),
            os.path.join(path, "*.png"),
        ]
        frames = []
        for pat in patterns:
            frames = sorted(glob.glob(pat))
            if frames:
                break
        if not frames:
            raise FileNotFoundError(f"No PNG frames in {path}")
        # ffmpeg glob — zero-padded names
        if "frame_" in os.path.basename(frames[0]):
            inp = os.path.join(path, "frame_%04d.png")
        else:
            inp = os.path.join(path, "%04d.png")
        return inp, ["-framerate", "24"]
    return path, []


def encode(inp: str, out: str, bitrate: str = "10M", extra_in: list[str] | None = None) -> int:
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    passlog = out + ".ffmpeg2pass"
    base = [
        ff(), "-y",
        *(extra_in or []),
        "-i", inp,
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-b:v", bitrate, "-maxrate", bitrate, "-bufsize", "20M",
        "-g", "12", "-keyint_min", "12",
        "-movflags", "+faststart",
        "-an",
    ]
    r1 = subprocess.run(base + ["-pass", "1", "-passlogfile", passlog, "-f", "null"],
                        capture_output=True, text=True)
    if r1.returncode != 0:
        print(r1.stderr, file=sys.stderr)
        return r1.returncode
    r2 = subprocess.run(base + ["-pass", "2", "-passlogfile", passlog, out],
                        capture_output=True, text=True)
    for suf in (".log", "-0.log", "-1.log"):
        try:
            os.remove(passlog + suf)
        except OSError:
            pass
    if r2.returncode != 0:
        print(r2.stderr, file=sys.stderr)
    else:
        print("ENCODED", out, flush=True)
    return r2.returncode


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--bitrate", default="10M")
    args = ap.parse_args()
    inp, extra = detect_input(args.input)
    return encode(inp, args.output, args.bitrate, extra)


if __name__ == "__main__":
    raise SystemExit(main())
