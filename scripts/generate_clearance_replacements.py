"""
Generate trademark-safe replacements for quarantined Netflix/Safaricom-named assets.

Outputs (no brand marks in filenames or hero copy):
  assets/canva/kinetic/infographics/inf_s04_kenya_4g_device_bars.png
  assets/canva/kinetic/infographics/extra_unique/x_s01_mm_market_share_chip.png
  assets/canva/s10_africa_wordmark_endcard.png  (AFRICA only — not Netflix lookalike)

Facts may cite public reports in small footer text; hero titles stay generic.
"""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
OUT_INF = PROJECT / "assets" / "canva" / "kinetic" / "infographics"
OUT_X = OUT_INF / "extra_unique"
OUT_CANVA = PROJECT / "assets" / "canva"

BG = "#1A1410"
PANEL = "#2A221C"
YELLOW = "#F5C518"
TEAL = "#3DB8A8"
CORAL = "#E07A5F"
CREAM = "#F4EFE6"
SOFT = "#B8A99A"
W, H = 1920, 1080


def fig_ax():
    fig, ax = plt.subplots(figsize=(W / 100, H / 100), dpi=100)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    return fig, ax


def save(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=100, facecolor=BG, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    # force exact 1920x1080
    try:
        from PIL import Image

        im = Image.open(path).convert("RGB")
        if im.size != (W, H):
            im = im.resize((W, H), Image.Resampling.LANCZOS)
            im.save(path, "PNG")
    except Exception:
        pass
    print("OK", path.name, path.stat().st_size)


def bar_h(ax, x, y, max_w, h, val, vmax, color, label, value_txt):
    ax.add_patch(FancyBboxPatch((x - 40, y - 20), max_w + 280, h + 40,
                                boxstyle="round,pad=0.02,rounding_size=12",
                                facecolor=PANEL, edgecolor=YELLOW, linewidth=1.2, alpha=0.95))
    ax.text(x, y + h / 2, label, color=CREAM, fontsize=18, va="center", ha="left")
    bw = max(8, (val / vmax) * max_w)
    ax.add_patch(FancyBboxPatch((x + 320, y), bw, h,
                                boxstyle="round,pad=0.02,rounding_size=8",
                                facecolor=color, edgecolor="none"))
    ax.text(x + 320 + bw + 16, y + h / 2, value_txt, color=color, fontsize=16, va="center", fontweight="bold")


def gen_4g_bars():
    fig, ax = fig_ax()
    ax.add_patch(FancyBboxPatch((80, 820), 900, 180, boxstyle="round,pad=0.02,rounding_size=16",
                                facecolor="none", edgecolor=YELLOW, linewidth=2))
    ax.text(110, 960, "S04 · SILICON SAVANNAH", color=YELLOW, fontsize=14, fontweight="bold")
    ax.text(110, 900, "Kenya 4G device growth", color=CREAM, fontsize=36, fontweight="bold")
    ax.text(110, 850, "National mobile network · device stock signals (FY24)", color=SOFT, fontsize=16)
    bar_h(ax, 200, 680, 1100, 70, 16.85, 23, YELLOW, "4G devices", "16.85M (+27.5%)")
    bar_h(ax, 200, 520, 1100, 70, 22.93, 23, TEAL, "Smartphones on network", "22.93M (+12.9%)")
    bar_h(ax, 200, 360, 1100, 70, 0.67, 23, CORAL, "5G devices", "0.67M (+79.3%)")
    ax.text(80, 60, "Source: Kenya operator public annual filings 2024 (device counts).", color=SOFT, fontsize=11)
    ax.text(1400, 60, "Africa S1 · motion-graphics still", color=SOFT, fontsize=11)
    save(fig, OUT_INF / "inf_s04_kenya_4g_device_bars.png")


def gen_mm_chip():
    fig, ax = fig_ax()
    ax.text(80, 1000, "S01 · EXTRA UNIQUE", color=YELLOW, fontsize=14, fontweight="bold")
    ax.add_patch(FancyBboxPatch((560, 360), 800, 360, boxstyle="round,pad=0.02,rounding_size=28",
                                facecolor=PANEL, edgecolor=YELLOW, linewidth=3))
    ax.text(960, 580, "92.3%", color=YELLOW, fontsize=96, ha="center", va="center", fontweight="bold")
    ax.text(960, 440, "Kenya mobile-money market share", color=CREAM, fontsize=22, ha="center")
    ax.text(80, 60, "CA Kenya Sep 2024", color=YELLOW, fontsize=12)
    ax.text(1400, 60, "Africa S1 · illustrative still", color=SOFT, fontsize=11)
    save(fig, OUT_X / "x_s01_mm_market_share_chip.png")


def gen_africa_endcard():
    """Soft-but-vivid AFRICA wordmark on dusk panel — original lockup, not streamer trade dress."""
    fig, ax = fig_ax()
    # subtle gradient bands
    for i in range(12):
        c = plt.matplotlib.colors.to_hex(
            [0.10 + i * 0.01, 0.08 + i * 0.008, 0.06 + i * 0.006]
        )
        ax.add_patch(Rectangle((0, i * 90), W, 90, facecolor=c, edgecolor="none"))
    ax.add_patch(FancyBboxPatch((460, 380), 1000, 320, boxstyle="round,pad=0.02,rounding_size=24",
                                facecolor=PANEL, edgecolor=YELLOW, linewidth=2.5, alpha=0.92))
    ax.text(960, 580, "AFRICA", color=YELLOW, fontsize=110, ha="center", va="center",
            fontweight="bold", fontfamily="sans-serif")
    ax.text(960, 450, "SEASON 1  ·  SILICON SAVANNAH", color=CREAM, fontsize=22, ha="center")
    ax.text(960, 160, "Original series mark · project-owned", color=SOFT, fontsize=12, ha="center")
    save(fig, OUT_CANVA / "s10_africa_wordmark_endcard.png")
    # Also refresh 1080 delivery copy next to existing v2 (do not overwrite v2 if preferred)
    save(fig_ax()[0], OUT_CANVA / "_tmp_skip.png")  # noop guard removed below


def main():
    gen_4g_bars()
    gen_mm_chip()
    # endcard: reopen clean
    fig, ax = fig_ax()
    for i in range(12):
        shade = 0.08 + i * 0.012
        ax.add_patch(Rectangle((0, i * 90), W, 90, facecolor=(shade, shade * 0.85, shade * 0.7), edgecolor="none"))
    ax.add_patch(FancyBboxPatch((460, 380), 1000, 320, boxstyle="round,pad=0.02,rounding_size=24",
                                facecolor=PANEL, edgecolor=YELLOW, linewidth=2.5, alpha=0.92))
    ax.text(960, 580, "AFRICA", color=YELLOW, fontsize=110, ha="center", va="center", fontweight="bold")
    ax.text(960, 450, "SEASON 1  ·  SILICON SAVANNAH", color=CREAM, fontsize=22, ha="center")
    ax.text(960, 160, "Original series mark · project-owned", color=SOFT, fontsize=12, ha="center")
    save(fig, OUT_CANVA / "s10_africa_wordmark_endcard.png")
    # Keep primary logo pointer: copy wordmark over s10 if netflix bak was the only option — prefer leave v2; write sibling
    print("DONE replacements")


if __name__ == "__main__":
    main()
