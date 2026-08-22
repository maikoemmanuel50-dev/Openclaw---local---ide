"""
Merge verified TED-Ed 30s open onto S01 V1 plate (frames 0–720 / 0–30s).

Per docs/S01_TEDED_30S_OPEN.md: Normal composite @ ~88% on V1; clears after 30s
so Africa whip @ ~28–30s reads on bare plate tail of S01.

Outputs:
  renders/video_clips/01_ColdOpen_with_open30.mp4  (integrated S01 stem)
  renders/built_clips/01_ColdOpen.mp4               (mirror for Resolve V1)

Run:
  python scripts/merge_open30_into_s01.py
  python scripts/merge_open30_into_s01.py --open path/to/open.mp4 --opacity 0.88
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
DEFAULT_OPEN_ENH = os.path.join(PROJECT, "renders", "paced_overlays", "s01_teded_open_30s_enhanced.mp4")
DEFAULT_OPEN = DEFAULT_OPEN_ENH if os.path.isfile(DEFAULT_OPEN_ENH) else os.path.join(
    PROJECT, "renders", "paced_overlays", "s01_teded_open_30s.mp4"
)
DEFAULT_PLATE = os.path.join(PROJECT, "renders", "video_clips", "01_ColdOpen.mp4")
OUT = os.path.join(PROJECT, "renders", "video_clips", "01_ColdOpen_with_open30.mp4")
BUILT = os.path.join(PROJECT, "renders", "built_clips", "01_ColdOpen.mp4")
REPORT = os.path.join(PROJECT, "renders", "quality", "open30_s01_merge_report.json")
OPEN_SEC = 30.0
FPS = 24


def ff() -> str:
    x = shutil.which("ffmpeg")
    if not x:
        raise RuntimeError("ffmpeg required")
    return x


def probe(path: str) -> dict:
    fp = shutil.which("ffprobe") or "ffprobe"
    r = subprocess.run(
        [fp, "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,r_frame_rate",
         "-show_entries", "format=duration", "-of", "json", path],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return {}
    import json as _json
    return _json.loads(r.stdout or "{}")


def merge(plate: str, open_mp4: str, out: str, opacity: float, bitrate: str) -> dict:
    if not os.path.isfile(plate):
        raise FileNotFoundError(plate)
    if not os.path.isfile(open_mp4):
        raise FileNotFoundError(open_mp4)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    # Normal-style overlay: open graphic over plate for first 30s only
    fc = (
        f"[1:v]format=rgba,colorchannelmixer=aa={opacity:.3f}[fg];"
        f"[0:v][fg]overlay=0:0:enable='lte(t,{OPEN_SEC})'[vout]"
    )
    passlog = out + ".2pass"
    common = [
        ff(), "-y",
        "-i", plate, "-i", open_mp4,
        "-filter_complex", fc,
        "-map", "[vout]",
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-b:v", bitrate, "-maxrate", bitrate, "-bufsize", "20M",
        "-r", str(FPS), "-an",
    ]
    r1 = subprocess.run(common + ["-pass", "1", "-passlogfile", passlog, "-f", "null", "NUL"], capture_output=True, text=True)
    if r1.returncode != 0:
        raise RuntimeError(r1.stderr[-600:])
    r2 = subprocess.run(common + ["-pass", "2", "-passlogfile", passlog, out], capture_output=True, text=True)
    for suf in (".log", "-0.log", "-1.log"):
        try:
            os.remove(passlog + suf)
        except OSError:
            pass
    if r2.returncode != 0:
        raise RuntimeError(r2.stderr[-600:])
    return {"out": out, "size": os.path.getsize(out), "opacity": opacity}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plate", default=DEFAULT_PLATE)
    ap.add_argument("--open", dest="open_mp4", default=DEFAULT_OPEN)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--opacity", type=float, default=0.88)
    ap.add_argument("--bitrate", default="10M")
    ap.add_argument("--mirror-built", action="store_true", default=True)
    args = ap.parse_args()

    meta = merge(args.plate, args.open_mp4, args.out, args.opacity, args.bitrate)
    if args.mirror_built:
        os.makedirs(os.path.dirname(BUILT), exist_ok=True)
        shutil.copy2(args.out, BUILT)
        meta["built_clips"] = BUILT

    meta.update({
        "plate": args.plate,
        "open": args.open_mp4,
        "open_sec": OPEN_SEC,
        "integration": "S01 frames 0-720 V3 equivalent; VO timeline unchanged",
    })
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print("MERGED", args.out, flush=True)
    print("REPORT", REPORT, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
