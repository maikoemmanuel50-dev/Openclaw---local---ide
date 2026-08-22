"""
Replace opening with 4K landscape pan (30s), AFRICA series slide transition,
then rejoin remaining content and split into 30-second portions.
"""
from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
import urllib.request

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
SOURCE = os.path.join(PROJECT, "Africa_S1_Silicon_Savannah_7min_Resolve.mp4")
WORK = os.path.join(PROJECT, "rebuild_work")
PORTIONS = os.path.join(PROJECT, "portions_30s")
OUTPUT = os.path.join(PROJECT, "Africa_S1_Silicon_Savannah_7min_rebuilt.mp4")
FPS = 24

CANVA_4K_URL = (
    "https://export-download.canva.com/YrlsA/DAHSEUYrlsA/-1/0/"
    "0001-3359071884756531470.png?X-Amz-Algorithm=AWS4-HMAC-SHA256"
    "&X-Amz-Credential=AKIAQYCGKMUH5AO7UJ26%2F20260812%2Fus-east-1%2Fs3%2Faws4_request"
    "&X-Amz-Date=20260812T073416Z&X-Amz-Expires=26896"
    "&X-Amz-Signature=8b6719e16765bbb7ffbd95702052452c951c47bafc97598c627f1f0c998d60dc"
    "&X-Amz-SignedHeaders=host%3Bx-amz-expected-bucket-owner"
    "&response-expires=Wed%2C%2012%20Aug%202026%2015%3A02%3A32%20GMT"
)
LOGO_PNG = os.path.join(PROJECT, "assets", "canva", "s10_africa_logo.png")
OPENING_FALLBACK = os.path.join(PROJECT, "assets", "canva", "s1_dawn_skyline.png")


def find_ffmpeg() -> str:
    ff = shutil.which("ffmpeg")
    if ff:
        return ff
    winget = os.path.join(
        os.path.expandvars(r"%LOCALAPPDATA%"),
        "Microsoft", "WinGet", "Packages",
        "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe",
    )
    for root, _, files in os.walk(winget):
        if "ffmpeg.exe" in files:
            return os.path.join(root, "ffmpeg.exe")
    raise RuntimeError("ffmpeg not found")


def run(cmd: list[str], label: str = "") -> None:
    print(f"  >> {label or 'ffmpeg'}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:])
        raise RuntimeError(label or "ffmpeg failed")


def download_opening_asset(dest: str) -> str:
    os.makedirs(WORK, exist_ok=True)
    try:
        req = urllib.request.Request(CANVA_4K_URL, headers={"User-Agent": "AfricaS1/1.0"})
        with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as f:
            f.write(resp.read())
        if os.path.getsize(dest) > 100_000:
            print(f"  Downloaded 4K Canva skyline ({os.path.getsize(dest)//1024} KB)")
            return dest
    except Exception as e:
        print(f"  Canva 4K download failed: {e}")
    shutil.copy2(OPENING_FALLBACK, dest)
    print(f"  Using fallback dawn skyline PNG")
    return dest


def build_opening_4k_pan(ff: str, img: str, out: str) -> None:
    """30s 4K slow push-in pan from landscape still."""
    frames = 30 * FPS
    vf = (
        "scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,"
        f"zoompan=z='min(1.0+0.0005*on,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s=3840x2160:fps={FPS},"
        "scale=1920:1080:flags=lanczos"
    )
    run([
        ff, "-y", "-loop", "1", "-i", img,
        "-vf", vf, "-t", "30",
        "-c:v", "libx264", "-crf", "16", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-an", out,
    ], "4K opening pan 30s")


def build_logo_slide(ff: str, logo: str, out: str, duration: float = 8.0) -> None:
    """AFRICA series logo slides up with fade on dark background."""
    slide_frames = int(1.5 * FPS)
    vf = (
        f"[0:v]scale=1200:-1,format=rgba,"
        f"fade=t=in:st=0:d=1.5:alpha=1[logo];"
        f"color=c=0x1a1a1a:s=1920x1080:d={duration},fps={FPS}[bg];"
        f"[bg][logo]overlay=x=(W-w)/2:"
        f"y='if(lt(n\\,{slide_frames}),H-(H-h)*n/{slide_frames},(H-h)/2)'"
        f"[vout]"
    )
    run([
        ff, "-y", "-loop", "1", "-i", logo,
        "-filter_complex", vf, "-map", "[vout]", "-t", str(duration),
        "-c:v", "libx264", "-crf", "16", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-an", out,
    ], "AFRICA series slide transition")


def trim_body(ff: str, src: str, out: str, start: float = 30.0) -> None:
    """Skip original cold-open; keep rest of episode."""
    run([
        ff, "-y", "-ss", str(start), "-i", src,
        "-vf", f"fps={FPS},scale=1920:1080:force_original_aspect_ratio=decrease,"
               "pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264", "-crf", "17", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-an", out,
    ], f"body from {start}s")


def crossfade_join(ff: str, a: str, b: str, out: str, xfade_d: float = 1.0) -> None:
    """Crossfade two clips."""
    run([
        ff, "-y", "-i", a, "-i", b,
        "-filter_complex",
        f"[0:v][1:v]xfade=transition=slideleft:duration={xfade_d}:offset=29[vout]",
        "-map", "[vout]", "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "-an", out,
    ], "crossfade opening->logo")


def concat_clips(ff: str, clips: list[str], out: str) -> None:
    inputs = sum([["-i", c] for c in clips], [])
    n = len(clips)
    chains = "".join(f"[{i}:v]" for i in range(n))
    fc = f"{chains}concat=n={n}:v=1:a=0[vout]"
    run([
        ff, "-y", *inputs,
        "-filter_complex", fc, "-map", "[vout]",
        "-c:v", "libx264", "-crf", "17", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-an", out,
    ], "concat final (filter)")


def split_30s(ff: str, src: str, out_dir: str) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    for old in glob.glob(os.path.join(out_dir, "portion_*.mp4")):
        os.remove(old)

    # Get total duration
    r = subprocess.run(
        [ff, "-i", src, "-f", "null", "-"], capture_output=True, text=True
    )
    import re
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    if not m:
        raise RuntimeError("Could not read source duration")
    h, mi, s = m.groups()
    total = int(h) * 3600 + int(mi) * 60 + float(s)

    paths = []
    idx = 0
    start = 0.0
    while start < total - 0.5:
        dur = min(30.0, total - start)
        out = os.path.join(out_dir, f"portion_{idx:02d}.mp4")
        run([
            ff, "-y", "-ss", str(start), "-i", src, "-t", str(dur),
            "-c:v", "libx264", "-crf", "18", "-preset", "medium",
            "-pix_fmt", "yuv420p", "-an", out,
        ], f"portion {idx:02d} ({start:.0f}s)")
        paths.append(out)
        idx += 1
        start += 30.0
    return paths


def main() -> int:
    print("=== Rebuild opening + split 30s portions ===")
    ff = find_ffmpeg()
    os.makedirs(WORK, exist_ok=True)

    opening_img = os.path.join(WORK, "opening_4k.png")
    opening_clip = os.path.join(WORK, "01_opening_4k_pan.mp4")
    logo_clip = os.path.join(WORK, "02_africa_slide.mp4")
    opening_logo = os.path.join(WORK, "intro_combined.mp4")
    body_clip = os.path.join(WORK, "03_body.mp4")

    print("\n--- 4K opening landscape ---")
    if not os.path.isfile(opening_clip):
        download_opening_asset(opening_img)
        build_opening_4k_pan(ff, opening_img, opening_clip)
    else:
        print("  (cached)")

    print("\n--- AFRICA series slide ---")
    if not os.path.isfile(logo_clip):
        build_logo_slide(ff, LOGO_PNG, logo_clip, duration=8.0)
    else:
        print("  (cached)")

    print("\n--- Transition opening -> logo ---")
    if not os.path.isfile(opening_logo):
        crossfade_join(ff, opening_clip, logo_clip, opening_logo, xfade_d=1.0)
    else:
        print("  (cached)")

    print("\n--- Body (skip original 30s cold open) ---")
    if not os.path.isfile(body_clip):
        trim_body(ff, SOURCE, body_clip, start=30.0)
    else:
        print("  (cached)")

    print("\n--- Assemble final ---")
    concat_clips(ff, [opening_logo, body_clip], OUTPUT)

    print("\n--- Split into 30s portions ---")
    portions = split_30s(ff, OUTPUT, PORTIONS)
    print(f"  Created {len(portions)} portions in {PORTIONS}")

    # Copy portion 01 as standalone intro pack
    manifest = os.path.join(PROJECT, "portions_manifest.txt")
    with open(manifest, "w") as f:
        f.write(f"rebuilt_master={OUTPUT}\n")
        f.write("intro=portion_00: 4K pan 30s + AFRICA slide transition\n")
        for i, p in enumerate(portions):
            f.write(f"portion_{i:02d}={p}\n")

    dur_r = subprocess.run(
        [ff, "-i", OUTPUT, "-f", "null", "-"], capture_output=True, text=True
    )
    import re
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", dur_r.stderr)
    if m:
        h, mi, s = m.groups()
        total = int(h) * 3600 + int(mi) * 60 + float(s)
        print(f"\nDONE: {OUTPUT} ({total/60:.2f} min, {len(portions)} x 30s portions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
