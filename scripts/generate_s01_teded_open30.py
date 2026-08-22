"""
TED-Ed-style 30s infographic cold-open stills + silent 1080p24 MP4.
Reference: https://youtu.be/2A1IEBFt6Xg
CPU only — does not touch Blender GPU render.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, FancyArrowPatch, Wedge

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
STILLS = PROJECT / "assets" / "canva" / "kinetic" / "infographics" / "open30"
CUTS = PROJECT / "renders" / "paced_overlays"
OUT_MP4 = CUTS / "s01_teded_open_30s.mp4"
MANIFEST = PROJECT / "renders" / "quality" / "s01_teded_open30_manifest.json"

BG = "#1A1408"
PANEL = "#2A2210"
YELLOW = "#FFD54F"
CREAM = "#FFF6D6"
TEAL = "#2EC4B6"
CORAL = "#FF6B4A"
SOFT = "#8B7E5A"
W, H = 1920, 1080

# 10 beats = 720f @24 = 30.0s. All ≤5s (edit law).
BEATS = [
    {"id": "01", "t0": 0.0, "dur": 2.0, "frames": 48, "trans": "hard cut",
     "title": "06:30", "sub": "NAIROBI", "kind": "stat"},
    {"id": "02", "t0": 2.0, "dur": 2.5, "frames": 60, "trans": "hard cut",
     "title": "MATATUS", "sub": "the city is already awake", "kind": "label"},
    {"id": "03", "t0": 4.5, "dur": 2.5, "frames": 60, "trans": "whip",
     "title": "NOT THE ROAD", "sub": "the real motion is in pockets", "kind": "label"},
    {"id": "04", "t0": 7.0, "dur": 3.0, "frames": 72, "trans": "zoom blur",
     "title": "A PHONE", "sub": "a network · a system built here", "kind": "flow"},
    {"id": "05", "t0": 10.0, "dur": 3.5, "frames": 84, "trans": "hard cut",
     "title": "82.1%", "sub": "mobile-money penetration · Kenya", "kind": "stat"},
    {"id": "06", "t0": 13.5, "dur": 3.0, "frames": 72, "trans": "hard cut",
     "title": "42.3M", "sub": "mobile-money subscriptions", "kind": "stat"},
    {"id": "07", "t0": 16.5, "dur": 3.5, "frames": 84, "trans": "hard cut",
     "title": "MONEY HAS\nALREADY MOVED", "sub": "before the first cup of tea", "kind": "paths"},
    {"id": "08", "t0": 20.0, "dur": 3.0, "frames": 72, "trans": "hard cut",
     "title": "NO BRANCH", "sub": "no queue · just a phone", "kind": "compare"},
    {"id": "09", "t0": 23.0, "dur": 4.0, "frames": 96, "trans": "whip",
     "title": "SILICON\nSAVANNAH", "sub": "This is Nairobi.", "kind": "title"},
    {"id": "10", "t0": 27.0, "dur": 3.0, "frames": 72, "trans": "cut to S02",
     "title": "2007", "sub": "the nickname has a start date →", "kind": "bridge"},
]


def fig_ax():
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100, facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor(BG)
    return fig, ax


def footer(ax, src: str):
    ax.text(80, 36, src, color=SOFT, fontsize=12, va="center")
    ax.text(1840, 36, "TED-Ed grammar  ·  24fps  ·  ≤5s cuts", color=SOFT, fontsize=11, ha="right", va="center")


def save(fig, path: Path):
    fig.savefig(path, dpi=100, facecolor=BG)
    plt.close(fig)
    print("OK", path.name, flush=True)


def draw_01(ax):
    ax.text(960, 640, "06:30", color=YELLOW, fontsize=140, fontweight="bold", ha="center", va="center")
    ax.add_patch(FancyBboxPatch((720, 430), 480, 70, boxstyle="round,pad=4,rounding_size=12",
                                facecolor=PANEL, edgecolor=YELLOW, linewidth=2))
    ax.text(960, 465, "NAIROBI", color=CREAM, fontsize=28, ha="center", va="center", fontweight="bold")
    footer(ax, "Cold open  ·  episode VO lock")


def draw_02(ax):
    ax.text(960, 700, "MATATUS", color=YELLOW, fontsize=72, fontweight="bold", ha="center")
    for i, lab in enumerate(["on foot", "on motorbikes", "packed in color"]):
        x = 360 + i * 400
        ax.add_patch(FancyBboxPatch((x - 150, 420), 300, 140, boxstyle="round,pad=8,rounding_size=16",
                                    facecolor=PANEL, edgecolor=TEAL, linewidth=2))
        ax.text(x, 490, lab, color=CREAM, fontsize=18, ha="center")
    footer(ax, "TED-Ed factor cards  ·  one idea per frame")


def draw_03(ax):
    ax.text(960, 720, "THE REAL MOTION", color=CREAM, fontsize=36, ha="center")
    ax.text(960, 560, "ISN'T ON THE ROAD", color=YELLOW, fontsize=48, fontweight="bold", ha="center")
    ax.text(960, 420, "it's in people's pockets", color=TEAL, fontsize=28, ha="center")
    footer(ax, "VO: look closer")


def draw_04(ax):
    steps = [("PHONE", YELLOW), ("NETWORK", TEAL), ("SYSTEM", CORAL)]
    for i, (lab, col) in enumerate(steps):
        x = 360 + i * 500
        ax.add_patch(Circle((x, 560), 110, facecolor=PANEL, edgecolor=col, linewidth=4))
        ax.text(x, 560, lab, color=CREAM, fontsize=18, ha="center", va="center", fontweight="bold")
        if i < 2:
            ax.add_patch(FancyArrowPatch((x + 120, 560), (x + 380, 560),
                                         arrowstyle="-|>", mutation_scale=22, color=col, lw=3))
    ax.text(960, 320, "built here  ·  solving a problem that started here", color=SOFT, fontsize=18, ha="center")
    footer(ax, "TED-Ed labeled sequence")


def draw_05(ax):
    ax.text(960, 640, "82.1%", color=YELLOW, fontsize=130, fontweight="bold", ha="center", va="center")
    ax.text(960, 430, "mobile-money penetration  ·  Kenya", color=CREAM, fontsize=22, ha="center")
    footer(ax, "Source: CA Kenya Sector Statistics Q2 FY2024/25")


def draw_06(ax):
    ax.text(960, 640, "42.3M", color=YELLOW, fontsize=120, fontweight="bold", ha="center", va="center")
    ax.text(960, 430, "mobile-money subscriptions", color=CREAM, fontsize=24, ha="center")
    ax.text(960, 360, "Safaricom 92.3% share of MM  ·  CA Kenya Sep 2024", color=SOFT, fontsize=16, ha="center")
    footer(ax, "Source: Communications Authority of Kenya")


def draw_07(ax):
    ax.text(960, 780, "MONEY HAS ALREADY MOVED", color=YELLOW, fontsize=36, fontweight="bold", ha="center")
    for i, lab in enumerate(["RENT", "STOCK", "LOAN"]):
        x = 360 + i * 500
        ax.add_patch(FancyBboxPatch((x - 140, 460), 280, 160, boxstyle="round,pad=8,rounding_size=16",
                                    facecolor=PANEL, edgecolor=YELLOW, linewidth=2))
        ax.text(x, 540, lab, color=CREAM, fontsize=22, ha="center", fontweight="bold")
        ax.plot([x - 80, x + 80], [500, 500], color=TEAL, lw=2)
    ax.text(960, 340, "before the first cup of tea", color=SOFT, fontsize=20, ha="center")
    footer(ax, "Episode VO  ·  transaction nodes")


def draw_08(ax):
    ax.add_patch(FancyBboxPatch((180, 380), 700, 420, boxstyle="round,pad=12,rounding_size=20",
                                facecolor="#15100A", edgecolor=SOFT, linewidth=2))
    ax.add_patch(FancyBboxPatch((1040, 380), 700, 420, boxstyle="round,pad=12,rounding_size=20",
                                facecolor=PANEL, edgecolor=YELLOW, linewidth=3))
    ax.text(530, 640, "BANK BRANCH", color=SOFT, fontsize=22, ha="center")
    ax.text(530, 520, "queues  ·  excluded", color=CREAM, fontsize=18, ha="center")
    ax.text(1390, 640, "JUST A PHONE", color=YELLOW, fontsize=26, ha="center", fontweight="bold")
    ax.text(1390, 520, "no branch  ·  no queue", color=CREAM, fontsize=18, ha="center")
    footer(ax, "TED-Ed before / after split")


def draw_09(ax):
    ax.text(960, 680, "SILICON", color=CREAM, fontsize=64, ha="center", fontweight="bold")
    ax.text(960, 540, "SAVANNAH", color=YELLOW, fontsize=88, ha="center", fontweight="bold")
    ax.text(960, 380, "This is Nairobi.", color=TEAL, fontsize=28, ha="center")
    footer(ax, "Title lockup  ·  VO last line of cold-open hook")


def draw_10(ax):
    ax.text(960, 680, "2007", color=YELLOW, fontsize=120, fontweight="bold", ha="center")
    ax.text(960, 480, "the nickname has a start date", color=CREAM, fontsize=26, ha="center")
    ax.text(960, 380, "→  M-Pesa", color=TEAL, fontsize=28, ha="center")
    footer(ax, "Bridge into S02  ·  whip / hard cut")


DRAW = {
    "01": draw_01, "02": draw_02, "03": draw_03, "04": draw_04, "05": draw_05,
    "06": draw_06, "07": draw_07, "08": draw_08, "09": draw_09, "10": draw_10,
}


def still_to_clip(src: Path, dest: Path, frames: int) -> None:
    ff = shutil.which("ffmpeg")
    if not ff:
        raise RuntimeError("ffmpeg required")
    zp = (
        "zoompan=z='min(zoom+0.0012,1.08)':x='iw/2-(iw/zoom/2)':"
        f"y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080:fps=24"
    )
    cmd = [
        ff, "-y", "-loop", "1", "-i", str(src), "-vf", zp,
        "-frames:v", str(frames),
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-r", "24", "-an", "-preset", "fast", "-crf", "18", str(dest),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-400:])


def concat(clips: list[Path], dest: Path) -> None:
    ff = shutil.which("ffmpeg")
    lst = dest.with_suffix(".txt")
    lst.write_text("".join(f"file '{c.as_posix()}'\n" for c in clips), encoding="utf-8")
    cmd = [
        ff, "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-r", "24", "-an", "-preset", "fast", "-crf", "18", str(dest),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-400:])


def main():
    STILLS.mkdir(parents=True, exist_ok=True)
    CUTS.mkdir(parents=True, exist_ok=True)
    clips = []
    files = []
    for b in BEATS:
        png = STILLS / f"open30_{b['id']}_{b['kind']}.png"
        canva_bak = png.with_suffix(png.suffix + ".matplotlib.bak")
        if canva_bak.is_file() and png.is_file():
            print(f"KEEP Canva {png.name}", flush=True)
        else:
            fig, ax = fig_ax()
            DRAW[b["id"]](ax)
            save(fig, png)
            print(f"DRAW {png.name}", flush=True)
        clip = CUTS / f"open30_{b['id']}_{b['frames']}f.mp4"
        still_to_clip(png, clip, b["frames"])
        clips.append(clip)
        files.append({**b, "png": str(png), "clip": str(clip)})
        print(f"CLIP {clip.name}", flush=True)
    concat(clips, OUT_MP4)
    print("MP4", OUT_MP4, "size", OUT_MP4.stat().st_size, flush=True)
    MANIFEST.write_text(json.dumps({
        "duration_s": 30.0, "fps": 24, "frames": 720, "file": str(OUT_MP4),
        "ref": "https://youtu.be/2A1IEBFt6Xg",
        "beats": files,
    }, indent=2), encoding="utf-8")
    print("MANIFEST", MANIFEST, flush=True)


if __name__ == "__main__":
    main()
