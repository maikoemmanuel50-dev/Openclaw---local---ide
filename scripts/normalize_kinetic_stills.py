"""
Normalize kinetic stills to broadcast 1920x1080 with soft-pop documentary grade.
Preserves fidelity: center-crop 16:9, mild unsharp, chapter-aware color grade.
"""
from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1\assets\canva\kinetic")
OUT = ROOT / "graded_1080"
TARGET = (1920, 1080)

# Soft-pop grade bias per chapter prefix (subtle multiply overlays)
CHAPTER_BIAS = {
    "k01": (1.05, 0.98, 0.92),   # dawn warm
    "k02": (1.02, 0.99, 0.95),
    "k03": (0.98, 1.00, 1.04),   # daylight cool-ish
    "k04": (0.98, 1.00, 1.05),
    "k05": (0.92, 0.95, 1.08),   # dark data cool
    "k06": (1.04, 1.02, 0.94),   # solar warm
    "k07": (0.95, 0.97, 1.02),   # tension slate
    "k08": (0.96, 0.96, 0.98),
    "k09": (1.02, 0.96, 1.06),   # dusk indigo/gold
    "k10": (0.90, 0.92, 0.98),
}


def center_crop_16x9(im: Image.Image) -> Image.Image:
    w, h = im.size
    target_ratio = 16 / 9
    ratio = w / h
    if abs(ratio - target_ratio) < 0.01:
        return im
    if ratio > target_ratio:
        # too wide
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return im.crop((left, 0, left + new_w, h))
    # too tall
    new_h = int(w / target_ratio)
    top = (h - new_h) // 2
    return im.crop((0, top, w, top + new_h))


def apply_bias(im: Image.Image, rgb_mul) -> Image.Image:
    r, g, b = im.split()
    r = r.point(lambda x: min(255, int(x * rgb_mul[0])))
    g = g.point(lambda x: min(255, int(x * rgb_mul[1])))
    b = b.point(lambda x: min(255, int(x * rgb_mul[2])))
    return Image.merge("RGB", (r, g, b))


def process(path: Path) -> Path:
    im = Image.open(path).convert("RGB")
    im = center_crop_16x9(im)
    # High-quality downsample/upscale with LANCZOS
    im = im.resize(TARGET, Image.Resampling.LANCZOS)
    # Mild sharpen for crisp documentary stills
    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=2))
    # Contrast / color fidelity
    im = ImageEnhance.Contrast(im).enhance(1.06)
    im = ImageEnhance.Color(im).enhance(0.92)  # slight desat → documentary
    im = ImageEnhance.Sharpness(im).enhance(1.08)
    prefix = path.stem[:3]
    bias = CHAPTER_BIAS.get(prefix, (1.0, 1.0, 1.0))
    im = apply_bias(im, bias)
    # Soft vignette-free; keep edges clean for Ken Burns
    out = OUT / f"{path.stem}_1080.png"
    im.save(out, "PNG", optimize=True)
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for p in sorted(ROOT.glob("k*.jpg")):
        out = process(p)
        results.append({"src": p.name, "out": out.name, "size": Image.open(out).size})
    # Also normalize any loose pngs named k*
    for p in sorted(ROOT.glob("k*.png")):
        if p.parent == OUT:
            continue
        out = process(p)
        results.append({"src": p.name, "out": out.name, "size": Image.open(out).size})
    print({"count": len(results), "results": results})


if __name__ == "__main__":
    main()
