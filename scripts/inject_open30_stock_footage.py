"""
Inject clearance-safe stock B-roll under TED-Ed open30 beats (CPU/ffmpeg).

Per-beat stock underlays at ~22% opacity + graphic on top → richer open without
replacing VO timing. Uses local Mixkit cuts + graded stock where available.

Output:
  renders/paced_overlays/s01_teded_open_30s_enhanced.mp4
  renders/quality/open30_stock_inject_report.json

Run: python scripts/inject_open30_stock_footage.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import urllib.request
from pathlib import Path

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
MANIFEST = PROJECT / "renders" / "quality" / "s01_teded_open30_manifest.json"
STOCK_DIR = PROJECT / "assets" / "stock" / "license_free" / "open30"
CUTS = PROJECT / "renders" / "paced_overlays" / "open30_stock_cuts"
OUT = PROJECT / "renders" / "paced_overlays" / "s01_teded_open_30s_enhanced.mp4"
REPORT = PROJECT / "renders" / "quality" / "open30_stock_inject_report.json"

SOFTPOP = (
    "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
    "eq=contrast=1.06:saturation=0.88:brightness=0.015"
)

# beat_id -> (local cut glob hint, mixkit fallback url)
BEAT_STOCK = {
    "01": ("cut_000*", "https://assets.mixkit.co/videos/4497/4497-720.mp4"),  # dawn desk/city
    "02": ("cut_002*", "https://assets.mixkit.co/videos/4601/4601-720.mp4"),  # city walk
    "04": ("cut_004*", "https://assets.mixkit.co/videos/34506/34506-720.mp4"),  # phone
    "09": ("cut_029*", "https://assets.mixkit.co/videos/4870/4870-720.mp4"),  # skyline clouds
}

UA = {"User-Agent": "AfricaS1Open30/1.0"}


def ff() -> str:
    x = shutil.which("ffmpeg")
    if not x:
        raise RuntimeError("ffmpeg required")
    return x


def find_local_cut(glob_hint: str) -> Path | None:
    roots = [
        PROJECT / "renders" / "paced_overlays" / "stock_cinematic",
        PROJECT / "renders" / "paced_overlays" / "unique_replacements",
    ]
    for root in roots:
        if not root.is_dir():
            continue
        for p in sorted(root.glob(glob_hint)):
            if p.is_file() and p.stat().st_size > 30_000:
                return p
    return None


def ensure_stock(beat_id: str, glob_hint: str, url: str) -> Path:
    local = find_local_cut(glob_hint)
    if local:
        return local
    STOCK_DIR.mkdir(parents=True, exist_ok=True)
    raw = STOCK_DIR / f"mixkit_open30_b{beat_id}.mp4"
    if not (raw.is_file() and raw.stat().st_size > 80_000):
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=120) as resp, open(raw, "wb") as out:
            shutil.copyfileobj(resp, out)
    CUTS.mkdir(parents=True, exist_ok=True)
    cut = CUTS / f"open30_stock_b{beat_id}_12f.mp4"
    if cut.is_file() and cut.stat().st_size > 20_000:
        return cut
    dur = 0.5
    cmd = [
        ff(), "-y", "-ss", "0.5", "-i", str(raw), "-t", f"{dur:.2f}",
        "-vf", SOFTPOP, "-r", "24",
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-an", str(cut),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return cut


def graphic_only_cmd(graphic: Path, dur: float, out: Path) -> list[str]:
    return [
        ff(), "-y", "-i", str(graphic),
        "-t", f"{dur:.3f}", "-r", "24",
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-an", str(out),
    ]


def composite_beat(beat: dict, stock: Path | None, out: Path) -> bool:
    graphic = Path(beat["clip"])
    if not graphic.is_file():
        return False
    out.parent.mkdir(parents=True, exist_ok=True)
    frames = int(beat["frames"])
    dur = frames / 24.0
    if stock and stock.is_file():
        fc = (
            "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
            "eq=brightness=-0.04:saturation=0.9[bg];"
            "[1:v]scale=1920:1080,format=yuva420p,colorchannelmixer=aa=0.88[fg];"
            "[bg][fg]overlay=0:0:shortest=1[v]"
        )
        cmd = [
            ff(), "-y",
            "-stream_loop", "-1", "-i", str(stock),
            "-i", str(graphic),
            "-filter_complex", fc,
            "-map", "[v]",
            "-t", f"{dur:.3f}", "-r", "24",
            "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
            "-an", str(out),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0 and out.is_file():
            return True
    r = subprocess.run(graphic_only_cmd(graphic, dur, out), capture_output=True, text=True)
    return r.returncode == 0 and out.is_file()


def concat_beats(segments: list[Path], out: Path) -> None:
    lst = out.parent / "_open30_enhanced_concat.txt"
    with open(lst, "w", encoding="utf-8") as f:
        for p in segments:
            f.write(f"file '{p.as_posix()}'\n")
    cmd = [
        ff(), "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-r", "24", "-an", str(out),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    segments = []
    log = []
    work = CUTS / "_enhanced_segments"
    work.mkdir(parents=True, exist_ok=True)

    for beat in manifest["beats"]:
        bid = beat["id"]
        stock_path = None
        if bid in BEAT_STOCK:
            hint, url = BEAT_STOCK[bid]
            try:
                stock_path = ensure_stock(bid, hint, url)
            except Exception as e:
                log.append({"beat": bid, "stock_err": str(e)})
        seg = work / f"enhanced_b{bid}_{beat['frames']}f.mp4"
        ok = composite_beat(beat, stock_path, seg)
        if ok:
            segments.append(seg)
            log.append({"beat": bid, "stock": str(stock_path) if stock_path else None, "out": str(seg)})
        else:
            log.append({"beat": bid, "error": "composite failed"})

    if len(segments) != len(manifest["beats"]):
        raise RuntimeError(f"segment count {len(segments)} != {len(manifest['beats'])} beats")

    concat_beats(segments, OUT)
    probe = subprocess.run(
        [shutil.which("ffprobe") or "ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=nb_frames", "-of", "default=nw=1:nk=1", str(OUT)],
        capture_output=True, text=True,
    )
    nb = int((probe.stdout or "0").strip() or "0")
    if nb != manifest["frames"]:
        raise RuntimeError(f"enhanced open has {nb} frames, expected {manifest['frames']}")

    delivery = OUT.with_name("s01_teded_open_30s_enhanced_delivery.mp4")
    subprocess.run([
        ff(), "-y", "-i", str(OUT),
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-b:v", "10M", "-pass", "1", "-an", "-f", "null", "NUL",
    ], check=True, capture_output=True)
    subprocess.run([
        ff(), "-y", "-i", str(OUT),
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-b:v", "10M", "-pass", "2", "-an", str(delivery),
    ], check=True, capture_output=True)
    if delivery.is_file():
        shutil.copy2(delivery, OUT)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps({"output": str(OUT), "frames": nb, "beats": log}, indent=2),
        encoding="utf-8",
    )
    print("ENHANCED", OUT, flush=True)


if __name__ == "__main__":
    main()
