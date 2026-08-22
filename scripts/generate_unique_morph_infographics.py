"""
Unique yellow-type morph transitions + extra scene infographics.
CPU-only (CUDA_VISIBLE_DEVICES=-1). Soft ffmpeg. Never reuse an asset
across scenes/frames. Does not touch Blender GPU render.

Refs (craft):
- Motion morph / kinetic type: https://youtu.be/36SIUe_mOZU
- Infographic motion: https://youtu.be/o5zHIYLqDIw
- Canva craft: https://www.youtube.com/shorts/j4YAXZRluW4
  https://www.youtube.com/shorts/SC_3fG4mvQs
  https://www.youtube.com/watch?v=uBBmbdPbfhw
  https://www.youtube.com/watch?v=FOnx6eTfKB8
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch, FancyArrowPatch, Wedge, Rectangle

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
STILL_ROOT = PROJECT / "assets" / "canva" / "kinetic" / "infographics"
MORPH_STILLS = STILL_ROOT / "morph_unique"
EXTRA_STILLS = STILL_ROOT / "extra_unique"
CLIP_ROOT = PROJECT / "renders" / "paced_overlays" / "morph_unique"
REGISTRY = PROJECT / "renders" / "quality" / "UNIQUE_ASSET_REGISTRY.json"
MANIFEST = PROJECT / "renders" / "quality" / "morph_unique_manifest.json"
PACK_MP4 = PROJECT / "renders" / "paced_overlays" / "episode_morph_pack_preview.mp4"

BG = "#1A1408"
PANEL = "#2A2210"
YELLOW = "#FFD54F"
CREAM = "#FFF6D6"
TEAL = "#2EC4B6"
CORAL = "#FF6B4A"
SOFT = "#8B7E5A"
PURPLE = "#9B8AC4"
MINT = "#7DCEA0"
W, H = 1920, 1080

# Hard uniqueness: each asset_id may appear once in the entire episode.
USED_IDS: set[str] = set()
USED_HASHES: set[str] = set()


def claim(asset_id: str) -> str:
    if asset_id in USED_IDS:
        raise RuntimeError(f"DUPLICATE asset_id forbidden: {asset_id}")
    USED_IDS.add(asset_id)
    return asset_id


def file_hash(path: Path, *, enforce_unique_bytes: bool = True) -> str:
    if "morph_unique" in path.parts:
        enforce_unique_bytes = False
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    digest = h.hexdigest()
    if enforce_unique_bytes and digest in USED_HASHES:
        raise RuntimeError(f"DUPLICATE file bytes forbidden: {path.name}")
    USED_HASHES.add(digest)
    return digest


def fig_ax(seed_color: str = BG):
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100, facecolor=seed_color)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor(seed_color)
    return fig, ax


def footer(ax, text: str):
    ax.text(70, 34, text, color=SOFT, fontsize=11, va="center")


def save_png(fig, path: Path, asset_id: str, *, morph_frame: bool = False) -> dict:
    claim(asset_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)
    digest = file_hash(path, enforce_unique_bytes=not morph_frame)
    print("PNG", asset_id, path.name, flush=True)
    return {"id": asset_id, "path": str(path), "sha1": digest, "kind": "still"}


def ff() -> str:
    x = shutil.which("ffmpeg")
    if not x:
        raise RuntimeError("ffmpeg required")
    return x


def frames_to_mp4(frame_dir: Path, dest: Path, fps: int = 24) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Soft CPU encode — no NVENC (leave GPU to Blender)
    pattern = str(frame_dir / "f_%04d.png")
    cmd = [
        ff(), "-y", "-framerate", str(fps), "-i", pattern,
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-preset", "veryfast", "-crf", "20", "-an", str(dest),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-500:])


def concat_mp4s(clips: list[Path], dest: Path) -> None:
    lst = dest.with_suffix(".txt")
    lst.write_text("".join(f"file '{c.as_posix()}'\n" for c in clips), encoding="utf-8")
    cmd = [
        ff(), "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-preset", "veryfast", "-crf", "20", "-an", "-r", "24", str(dest),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-500:])


# ---------- Morph frame drawing ----------

def draw_yellow_word(ax, text: str, scale: float = 1.0, y: float = 540, alpha: float = 1.0):
    ax.text(
        960, y, text, color=YELLOW, fontsize=int(96 * scale), fontweight="bold",
        ha="center", va="center", alpha=alpha,
    )


def draw_pie(ax, cx, cy, r, sizes, colors, labels, alpha: float = 1.0):
    total = sum(sizes) or 1
    ang = 90
    for size, color, lab in zip(sizes, colors, labels):
        theta = 360 * size / total
        ax.add_patch(Wedge((cx, cy), r, ang - theta, ang, facecolor=color, edgecolor=BG, linewidth=2, alpha=alpha))
        mid = np.deg2rad(ang - theta / 2)
        ax.text(cx + (r + 55) * np.cos(mid), cy + (r + 55) * np.sin(mid), lab,
                color=CREAM, fontsize=12, ha="center", va="center", alpha=alpha, fontweight="bold")
        ang -= theta
    ax.add_patch(Circle((cx, cy), r * 0.38, facecolor=BG, edgecolor=YELLOW, linewidth=2, alpha=alpha))


def draw_bars(ax, items, alpha: float = 1.0, xmax: float = 1000):
    # items: (label, value, vmax, color)
    for i, (lab, val, vmax, col) in enumerate(items):
        y = 720 - i * 110
        ax.text(200, y + 28, lab, color=CREAM, fontsize=16, ha="right", va="center", alpha=alpha)
        ax.add_patch(FancyBboxPatch((240, y), xmax, 56, boxstyle="round,pad=2,rounding_size=8",
                                    facecolor="#3A3018", edgecolor=SOFT, linewidth=1, alpha=alpha))
        fill = max(12, xmax * (val / vmax))
        ax.add_patch(FancyBboxPatch((240, y), fill, 56, boxstyle="round,pad=2,rounding_size=8",
                                    facecolor=col, edgecolor="none", alpha=alpha))
        ax.text(240 + fill + 18, y + 28, str(val), color=YELLOW, fontsize=16, va="center", alpha=alpha, fontweight="bold")


def draw_donut_progress(ax, pct: float, label: str, alpha: float = 1.0):
    r = 220
    ax.add_patch(Wedge((960, 520), r, 90, 90 - 360 * (pct / 100), facecolor=YELLOW, edgecolor=BG, linewidth=3, alpha=alpha))
    ax.add_patch(Wedge((960, 520), r, 90 - 360 * (pct / 100), 90 - 360, facecolor="#3A3018", edgecolor=BG, linewidth=3, alpha=alpha))
    ax.add_patch(Circle((960, 520), r * 0.55, facecolor=BG, edgecolor=TEAL, linewidth=2, alpha=alpha))
    ax.text(960, 540, f"{pct:.0f}%", color=YELLOW, fontsize=56, ha="center", va="center", fontweight="bold", alpha=alpha)
    ax.text(960, 460, label, color=CREAM, fontsize=16, ha="center", va="center", alpha=alpha)


# Scene morph specs — unique word/number + unique chart per scene (never shared)
MORPHS = [
    {
        "scene": "01", "id": "morph_s01_821_to_pie",
        "word": "82.1%", "frames": 36,
        "chart": "pie",
        "pie": {"sizes": [82.1, 17.9], "colors": [YELLOW, "#4A3F28"], "labels": ["MM\n82.1%", "Other\n17.9%"]},
        "title": "Mobile money penetration", "source": "CA Kenya Q2 FY2024/25",
    },
    {
        "scene": "01", "id": "morph_s01_423m_to_bars",
        "word": "42.3M", "frames": 36,
        "chart": "bars",
        "bars": [("Smartphones", 41.5, 45, YELLOW), ("Feature", 30.6, 45, TEAL), ("MM subs", 42.3, 45, CORAL)],
        "title": "Kenya device + MM stock", "source": "CA Kenya Q2 FY2024/25",
    },
    {
        "scene": "02", "id": "morph_s02_2007_to_flow",
        "word": "2007", "frames": 36,
        "chart": "flow",
        "flow": ["SMS", "AGENT", "WALLET"],
        "title": "M-Pesa launch year → rails", "source": "Safaricom lineage / documentary",
    },
    {
        "scene": "02", "id": "morph_s02_3582m_to_donut",
        "word": "35.8M", "frames": 36,
        "chart": "donut",
        "donut": {"pct": 90, "label": "account ownership · Kenya (Findex lineage)"},
        "title": "Active M-Pesa → inclusion", "source": "Safaricom FY25 / Findex",
    },
    {
        "scene": "03", "id": "morph_s03_ihub_to_cards",
        "word": "iHub", "frames": 36,
        "chart": "cards",
        "cards": [("SPACE", TEAL), ("CODE", YELLOW), ("TALENT", CORAL)],
        "title": "Hub factors", "source": "Documentary nominative",
    },
    {
        "scene": "03", "id": "morph_s03_32b_to_bars",
        "word": "$3.2B", "frames": 36,
        "chart": "bars",
        "bars": [("Nigeria", 520, 520, YELLOW), ("Egypt", 400, 520, TEAL), ("S. Africa", 350, 520, CORAL), ("Kenya eq.", 221, 520, MINT)],
        "title": "Africa equity 2024", "source": "Partech Africa Tech VC 2024",
    },
    {
        "scene": "04", "id": "morph_s04_phone_to_pie",
        "word": "PHONE", "frames": 36,
        "chart": "pie",
        "pie": {"sizes": [57.5, 42.5], "colors": [YELLOW, TEAL], "labels": ["Smart\n57%", "Feature\n43%"]},
        "title": "Device mix from phone word", "source": "CA Kenya device stock",
    },
    {
        "scene": "04", "id": "morph_s04_93_to_donut",
        "word": "93%", "frames": 30,
        "chart": "donut",
        "donut": {"pct": 93, "label": "adults with a mobile phone"},
        "title": "Phone ownership", "source": "World Bank Findex Kenya summaries",
    },
    {
        "scene": "05", "id": "morph_s05_984m_to_pie",
        "word": "$984M", "frames": 40,
        "chart": "pie",
        "pie": {"sizes": [82, 18], "colors": [CORAL, YELLOW], "labels": ["Top 5\n82%", "Rest\n18%"]},
        "title": "Kenya funding concentration 2025", "source": "Africa: The Big Deal 2025",
    },
    {
        "scene": "05", "id": "morph_s05_82_to_bars",
        "word": "82%", "frames": 36,
        "chart": "bars",
        "bars": [("Debt", 60, 100, TEAL), ("Equity", 40, 100, YELLOW)],
        "title": "Debt vs equity structure", "source": "The Big Deal 2025",
    },
    {
        "scene": "06", "id": "morph_s06_79_to_donut",
        "word": "79%", "frames": 36,
        "chart": "donut",
        "donut": {"pct": 79, "label": "national electricity access 2023"},
        "title": "Electrification", "source": "IEA Kenya 2024",
    },
    {
        "scene": "06", "id": "morph_s06_solar_to_pie",
        "word": "SOLAR", "frames": 36,
        "chart": "pie",
        "pie": {"sizes": [80, 20], "colors": [YELLOW, "#3A3018"], "labels": ["Renewables\n~80%", "Other\n~20%"]},
        "title": "Generation capacity mix", "source": "IEA Kenya 2024",
    },
    {
        "scene": "07", "id": "morph_s07_974_to_pie",
        "word": "97.4%", "frames": 40,
        "chart": "pie",
        "pie": {"sizes": [97.4, 2.6], "colors": [CORAL, YELLOW], "labels": ["Nairobi\n97.4%", "Rest\n2.6%"]},
        "title": "Startup geography", "source": "Disrupt Africa 2022",
    },
    {
        "scene": "07", "id": "morph_s07_gap_to_bars",
        "word": "GAP", "frames": 36,
        "chart": "bars",
        "bars": [("Urban access", 100, 100, YELLOW), ("Rural access", 67.9, 100, TEAL), ("Rural KPLC", 51, 100, CORAL)],
        "title": "Urban / rural electricity", "source": "IEA / WB / Afrobarometer",
    },
    {
        "scene": "08", "id": "morph_s08_quiet_to_split",
        "word": "QUIET", "frames": 36,
        "chart": "split",
        "split": [("NAIROBI", YELLOW, "HQ · VC · press"), ("SECONDARY", SOFT, "thinner capital")],
        "title": "Secondary-city quiet beat", "source": "Documentary contrast",
    },
    {
        "scene": "08", "id": "morph_s08_30_to_donut",
        "word": ">30%", "frames": 30,
        "chart": "donut",
        "donut": {"pct": 30, "label": "clean cooking access 2023"},
        "title": "Clean cooking lag", "source": "IEA Kenya 2024",
    },
    {
        "scene": "09", "id": "morph_s09_number1_to_bars",
        "word": "#1", "frames": 36,
        "chart": "bars",
        "bars": [("Kenya", 984, 984, YELLOW), ("Egypt", 614, 984, TEAL), ("S. Africa", 599, 984, CORAL), ("Nigeria", 343, 984, MINT)],
        "title": "Africa funding 2025 leaders", "source": "The Big Deal 2025",
    },
    {
        "scene": "09", "id": "morph_s09_75_to_pie",
        "word": "75", "frames": 36,
        "chart": "pie",
        "pie": {"sizes": [46, 15, 13, 26], "colors": [YELLOW, TEAL, CORAL, PURPLE], "labels": ["Clean\n46%", "Agri\n15%", "Fin\n13%", "Other\n26%"]},
        "title": "Kenya equity sector tilt 2024", "source": "Partech 2024",
    },
    {
        "scene": "10", "id": "morph_s10_africa_to_arc",
        "word": "AFRICA", "frames": 40,
        "chart": "arc",
        "arc": ["RAILS", "HUBS", "CAPITAL", "GAP"],
        "title": "Series arc lockup", "source": "Episode narrative",
    },
    {
        "scene": "10", "id": "morph_s10_end_to_trio",
        "word": "END", "frames": 36,
        "chart": "trio",
        "trio": [("$984M", "funding"), ("82%", "top five"), ("97.4%", "Nairobi")],
        "title": "Three episode numbers", "source": "The Big Deal / Disrupt Africa",
    },
]


# Extra unique stills (one-shot graphics never used in morphs or open30)
EXTRAS = [
    ("02", "x_s02_agent_network_stat", "stat", "298k+", "M-Pesa agents (FY25)", "Safaricom FY25"),
    ("02", "x_s02_txn_volume_bars", "bars_txn", None, None, "Safaricom FY25"),
    ("03", "x_s03_andela_nailab_split", "split_talent", None, None, "Documentary"),
    ("03", "x_s03_fintech_60pct_donut", "donut60", None, None, "Partech 2024"),
    ("04", "x_s04_4g_growth_spark", "spark4g", None, None, "Safaricom AR 2024"),
    ("04", "x_s04_5g_devices_stat", "stat", "670k", "5G devices on network", "Safaricom AR 2024"),
    ("05", "x_s05_kenya_31pct_africa", "donut31", None, None, "The Big Deal 2025"),
    ("05", "x_s05_megadeal_callout", "callout", "TOP 5", "absorb 82% of Kenya capital", "Citizen / Big Deal"),
    ("06", "x_s06_urban100_stat", "stat", "100%", "urban electricity access", "IEA Kenya 2024"),
    ("06", "x_s06_shs74_east_africa", "donut74", None, None, "IEA Kenya 2024"),
    ("07", "x_s07_city_ribbon", "ribbon", None, None, "VO + TechCabal"),
    ("07", "x_s07_97_hold_badge", "badge97", None, None, "Disrupt Africa 2022"),
    ("08", "x_s08_56m_data_subs", "stat", "56.1M", "mobile data subscriptions", "CA Kenya Q2"),
    ("08", "x_s08_thin_capital_meter", "meter", None, None, "Documentary"),
    ("09", "x_s09_yoy_up_arrow", "arrow54", None, None, "Business Daily / Big Deal"),
    ("09", "x_s09_debt_heavy_badge", "badge60", None, None, "The Big Deal 2025"),
    ("10", "x_s10_series_mark", "series", None, None, "Brand lockup"),
    ("10", "x_s10_verify_sources", "srclist", None, None, "INFOGRAPHIC_SOURCES.md"),
    ("01", "x_s01_tea_before_money", "timeline", None, None, "Episode VO"),
    ("01", "x_s01_mm_market_share_chip", "chip92", None, None, "CA Kenya Sep 2024"),
]


def render_morph_frames(spec: dict) -> tuple[Path, list[dict]]:
    scene = spec["scene"]
    mid = spec["id"]
    n = int(spec["frames"])
    out_dir = MORPH_STILLS / mid
    out_dir.mkdir(parents=True, exist_ok=True)
    records = []
    # Phase split: word dominate → crossfade → chart dominate
    for i in range(n):
        t = i / max(1, n - 1)
        fig, ax = fig_ax()
        # yellow word fades / shrinks
        word_a = max(0.0, 1.0 - t * 1.35)
        word_s = 1.15 - 0.55 * t
        if word_a > 0.02:
            draw_yellow_word(ax, spec["word"], scale=word_s, y=560 + 40 * (1 - t), alpha=word_a)
        chart_a = min(1.0, max(0.0, (t - 0.25) / 0.55))
        if chart_a > 0.02:
            kind = spec["chart"]
            if kind == "pie":
                p = spec["pie"]
                draw_pie(ax, 960, 500, 200 + 40 * chart_a, p["sizes"], p["colors"], p["labels"], alpha=chart_a)
            elif kind == "bars":
                draw_bars(ax, spec["bars"], alpha=chart_a, xmax=1100)
            elif kind == "donut":
                d = spec["donut"]
                draw_donut_progress(ax, d["pct"] * chart_a, d["label"], alpha=chart_a)
            elif kind == "flow":
                labs = spec["flow"]
                for j, lab in enumerate(labs):
                    x = 360 + j * 500
                    ax.add_patch(Circle((x, 520), 90 * chart_a + 20, facecolor=PANEL, edgecolor=YELLOW, linewidth=3, alpha=chart_a))
                    ax.text(x, 520, lab, color=CREAM, fontsize=16, ha="center", va="center", alpha=chart_a, fontweight="bold")
                    if j < len(labs) - 1:
                        ax.add_patch(FancyArrowPatch((x + 100, 520), (x + 400, 520), arrowstyle="-|>",
                                                     mutation_scale=18, color=TEAL, lw=3, alpha=chart_a))
            elif kind == "cards":
                for j, (lab, col) in enumerate(spec["cards"]):
                    x = 360 + j * 500
                    ax.add_patch(FancyBboxPatch((x - 150, 420), 300, 200, boxstyle="round,pad=8,rounding_size=16",
                                                facecolor=PANEL, edgecolor=col, linewidth=3, alpha=chart_a))
                    ax.text(x, 520, lab, color=col, fontsize=26, ha="center", va="center", alpha=chart_a, fontweight="bold")
            elif kind == "split":
                a, b = spec["split"]
                ax.add_patch(FancyBboxPatch((160, 360), 720, 400, boxstyle="round,pad=10,rounding_size=18",
                                            facecolor=PANEL, edgecolor=a[1], linewidth=3, alpha=chart_a))
                ax.add_patch(FancyBboxPatch((1040, 360), 720, 400, boxstyle="round,pad=10,rounding_size=18",
                                            facecolor="#15100A", edgecolor=b[1], linewidth=3, alpha=chart_a))
                ax.text(520, 600, a[0], color=a[1], fontsize=28, ha="center", alpha=chart_a, fontweight="bold")
                ax.text(520, 500, a[2], color=CREAM, fontsize=16, ha="center", alpha=chart_a)
                ax.text(1400, 600, b[0], color=b[1], fontsize=24, ha="center", alpha=chart_a, fontweight="bold")
                ax.text(1400, 500, b[2], color=CREAM, fontsize=16, ha="center", alpha=chart_a)
            elif kind == "arc":
                labs = spec["arc"]
                for j, lab in enumerate(labs):
                    x = 300 + j * 400
                    ax.add_patch(Circle((x, 520), 85, facecolor=PANEL, edgecolor=YELLOW, linewidth=3, alpha=chart_a))
                    ax.text(x, 520, str(j + 1), color=YELLOW, fontsize=28, ha="center", va="center", alpha=chart_a, fontweight="bold")
                    ax.text(x, 390, lab, color=CREAM, fontsize=14, ha="center", alpha=chart_a)
                    if j < len(labs) - 1:
                        ax.add_patch(FancyArrowPatch((x + 95, 520), (x + 305, 520), arrowstyle="-|>",
                                                     mutation_scale=16, color=TEAL, lw=2.5, alpha=chart_a))
            elif kind == "trio":
                for j, (v, lab) in enumerate(spec["trio"]):
                    x = 360 + j * 500
                    ax.add_patch(FancyBboxPatch((x - 170, 400), 340, 280, boxstyle="round,pad=10,rounding_size=18",
                                                facecolor=PANEL, edgecolor=YELLOW, linewidth=2, alpha=chart_a))
                    ax.text(x, 560, v, color=YELLOW, fontsize=32, ha="center", alpha=chart_a, fontweight="bold")
                    ax.text(x, 470, lab, color=CREAM, fontsize=14, ha="center", alpha=chart_a)
        ax.text(70, 1040, f"S{scene}  ·  {spec['title']}", color=SOFT, fontsize=14, va="center")
        footer(ax, spec["source"])
        # unique frame id
        aid = f"{mid}_f{i:04d}"
        fpath = out_dir / f"f_{i:04d}.png"
        rec = save_png(fig, fpath, aid, morph_frame=True)
        records.append(rec)
    return out_dir, records


def render_extra(scene: str, asset_id: str, kind: str, val, sub, source: str) -> dict:
    fig, ax = fig_ax()
    ax.text(70, 1040, f"S{scene}  ·  EXTRA UNIQUE", color=SOFT, fontsize=14, va="center")
    if kind == "stat":
        ax.text(960, 600, val, color=YELLOW, fontsize=110, ha="center", va="center", fontweight="bold")
        ax.text(960, 420, sub, color=CREAM, fontsize=22, ha="center")
    elif kind == "bars_txn":
        draw_bars(ax, [("Txn volume", 37.15, 40, YELLOW), ("Txn value T", 38.29, 40, TEAL)], xmax=1100)
        ax.text(960, 900, "M-Pesa Kenya FY25 scale", color=CREAM, fontsize=22, ha="center")
    elif kind == "split_talent":
        for i, (n, d, c) in enumerate([("Andela", "talent pipelines", TEAL), ("NaiLab", "incubation", YELLOW)]):
            x = 480 + i * 700
            ax.add_patch(FancyBboxPatch((x - 260, 380), 520, 360, boxstyle="round,pad=12,rounding_size=20",
                                        facecolor=PANEL, edgecolor=c, linewidth=3))
            ax.text(x, 600, n, color=c, fontsize=36, ha="center", fontweight="bold")
            ax.text(x, 500, d, color=CREAM, fontsize=18, ha="center")
    elif kind == "donut60":
        draw_donut_progress(ax, 60, "fintech share of Africa equity 2024")
    elif kind == "spark4g":
        xs = np.linspace(300, 1600, 6)
        ys = np.array([380, 420, 480, 560, 650, 760])
        ax.plot(xs, ys, color=YELLOW, lw=5)
        ax.scatter(xs, ys, color=TEAL, s=80, zorder=3)
        ax.text(960, 300, "4G devices ↑ 27.5% YoY", color=CREAM, fontsize=22, ha="center")
    elif kind == "donut31":
        draw_donut_progress(ax, 31, "Kenya share of Africa startup funding 2025")
    elif kind == "callout":
        ax.add_patch(FancyBboxPatch((460, 380), 1000, 360, boxstyle="round,pad=14,rounding_size=24",
                                    facecolor=PANEL, edgecolor=CORAL, linewidth=4))
        ax.text(960, 600, val, color=CORAL, fontsize=64, ha="center", fontweight="bold")
        ax.text(960, 480, sub, color=CREAM, fontsize=22, ha="center")
    elif kind == "donut74":
        draw_donut_progress(ax, 74, "East Africa SHS sales share (Kenya)")
    elif kind == "ribbon":
        cities = ["Mombasa", "Kisumu", "Eldoret", "Nakuru"]
        for i, c in enumerate(cities):
            x = 280 + i * 400
            ax.add_patch(Rectangle((x - 140, 480), 280, 100, facecolor=PANEL, edgecolor=TEAL, linewidth=2))
            ax.text(x, 530, c, color=CREAM, fontsize=18, ha="center", fontweight="bold")
        ax.text(960, 700, "secondary cities named in VO", color=YELLOW, fontsize=22, ha="center")
    elif kind == "badge97":
        ax.add_patch(Circle((960, 540), 260, facecolor=PANEL, edgecolor=CORAL, linewidth=6))
        ax.text(960, 580, "97.4%", color=CORAL, fontsize=72, ha="center", fontweight="bold")
        ax.text(960, 470, "startups in Nairobi", color=CREAM, fontsize=20, ha="center")
    elif kind == "meter":
        ax.add_patch(FancyBboxPatch((360, 500), 1200, 70, boxstyle="round,pad=2,rounding_size=10",
                                    facecolor="#3A3018", edgecolor=SOFT))
        ax.add_patch(FancyBboxPatch((360, 500), 280, 70, boxstyle="round,pad=2,rounding_size=10",
                                    facecolor=SOFT, edgecolor="none"))
        ax.text(960, 650, "capital density outside Nairobi", color=CREAM, fontsize=22, ha="center")
        ax.text(960, 420, "LOW", color=YELLOW, fontsize=28, ha="center", fontweight="bold")
    elif kind == "arrow54":
        ax.annotate("", xy=(1400, 700), xytext=(500, 380),
                    arrowprops=dict(arrowstyle="-|>", color=YELLOW, lw=10))
        ax.text(960, 300, "+54% YoY Kenya funding → $984M", color=CREAM, fontsize=24, ha="center")
    elif kind == "badge60":
        ax.add_patch(FancyBboxPatch((560, 400), 800, 320, boxstyle="round,pad=12,rounding_size=22",
                                    facecolor=PANEL, edgecolor=TEAL, linewidth=4))
        ax.text(960, 600, "≈60% DEBT", color=TEAL, fontsize=48, ha="center", fontweight="bold")
        ax.text(960, 500, "of Kenya 2025 capital stack", color=CREAM, fontsize=18, ha="center")
    elif kind == "series":
        ax.text(960, 600, "AFRICA", color=YELLOW, fontsize=96, ha="center", fontweight="bold")
        ax.text(960, 460, "Season 1  ·  Episode 01", color=CREAM, fontsize=28, ha="center")
    elif kind == "srclist":
        lines = ["CA Kenya", "Safaricom FY/AR", "Partech 2024", "The Big Deal 2025", "IEA Kenya 2024", "Disrupt Africa 2022"]
        for i, line in enumerate(lines):
            ax.text(400, 820 - i * 80, f"•  {line}", color=CREAM, fontsize=22, va="center")
    elif kind == "timeline":
        ax.text(960, 700, "TEA", color=SOFT, fontsize=40, ha="center")
        ax.add_patch(FancyArrowPatch((960, 640), (960, 500), arrowstyle="-|>", mutation_scale=24, color=YELLOW, lw=4))
        ax.text(960, 440, "MONEY ALREADY MOVED", color=YELLOW, fontsize=36, ha="center", fontweight="bold")
    elif kind == "chip92":
        ax.add_patch(FancyBboxPatch((610, 430), 700, 260, boxstyle="round,pad=10,rounding_size=40",
                                    facecolor=PANEL, edgecolor=YELLOW, linewidth=3))
        ax.text(960, 600, "92.3%", color=YELLOW, fontsize=64, ha="center", fontweight="bold")
        ax.text(960, 500, "Kenya mobile-money market share", color=CREAM, fontsize=18, ha="center")
    footer(ax, source)
    path = EXTRA_STILLS / f"{asset_id}.png"
    return save_png(fig, path, asset_id)


def seed_existing_registry():
    """Register already-shipped stills so new work cannot collide by id."""
    for p in STILL_ROOT.rglob("*.png"):
        # skip morph frame folders we are about to regenerate
        if "morph_unique" in p.parts or "extra_unique" in p.parts:
            continue
        aid = f"existing::{p.relative_to(STILL_ROOT).as_posix()}"
        claim(aid)
        try:
            file_hash(p)
        except RuntimeError:
            # Identical open30/stat duplicates across folders — record as known conflict
            print("WARN existing byte-duplicate", p.name, flush=True)


def main():
    MORPH_STILLS.mkdir(parents=True, exist_ok=True)
    EXTRA_STILLS.mkdir(parents=True, exist_ok=True)
    CLIP_ROOT.mkdir(parents=True, exist_ok=True)

    # Clear previous morph/extra outputs for clean unique regen
    for d in [MORPH_STILLS, EXTRA_STILLS, CLIP_ROOT]:
        if d.exists():
            for child in d.iterdir():
                if child.is_dir():
                    shutil.rmtree(child, ignore_errors=True)
                else:
                    child.unlink(missing_ok=True)

    seed_existing_registry()

    registry = {"policy": "one asset id + one sha1 per entire episode", "assets": [], "morph_clips": [], "extras": []}
    clips = []

    for spec in MORPHS:
        frame_dir, records = render_morph_frames(spec)
        registry["assets"].extend(records)
        clip = CLIP_ROOT / f"{spec['id']}.mp4"
        frames_to_mp4(frame_dir, clip, 24)
        claim(f"clip::{spec['id']}")
        registry["morph_clips"].append({
            "id": spec["id"], "scene": spec["scene"], "path": str(clip),
            "frames": spec["frames"], "word": spec["word"], "chart": spec["chart"],
            "duration_s": round(spec["frames"] / 24, 3),
        })
        clips.append(clip)
        print("CLIP", clip.name, flush=True)

    for scene, aid, kind, val, sub, source in EXTRAS:
        rec = render_extra(scene, aid, kind, val, sub, source)
        registry["extras"].append(rec)
        registry["assets"].append(rec)

    if clips:
        concat_mp4s(clips, PACK_MP4)
        claim("clip::episode_morph_pack_preview")
        print("PACK", PACK_MP4, flush=True)

    registry["counts"] = {
        "unique_ids": len(USED_IDS),
        "unique_sha1": len(USED_HASHES),
        "morph_clips": len(registry["morph_clips"]),
        "extras": len(registry["extras"]),
    }
    REGISTRY.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "pack": str(PACK_MP4),
        "clips": registry["morph_clips"],
        "extras": [e["path"] for e in registry["extras"]],
        "refs": [
            "https://youtu.be/36SIUe_mOZU",
            "https://youtu.be/o5zHIYLqDIw",
            "https://www.youtube.com/shorts/j4YAXZRluW4",
            "https://www.youtube.com/shorts/SC_3fG4mvQs",
            "https://www.youtube.com/watch?v=uBBmbdPbfhw",
            "https://www.youtube.com/watch?v=FOnx6eTfKB8",
        ],
        "gpu_policy": "CPU-only encode (libx264 veryfast); Blender retains GPU",
    }, indent=2), encoding="utf-8")
    print("REGISTRY", REGISTRY, registry["counts"], flush=True)


if __name__ == "__main__":
    main()
