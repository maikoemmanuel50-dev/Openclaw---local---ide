"""
Generate extra native kinetic stills (soft-pop documentary) for Africa S1.
CPU-only — safe while Blender HQ renders. No faces / no competing heroes.

Output: assets/canva/kinetic/k*_native_*.jpg then graded via normalize_kinetic_stills.py
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1\assets\canva\kinetic")
W, H = 1920, 1080

# Soft-pop locked palette (hero gold reserved for ball — accents only)
CREAM = (241, 228, 200)
MUSTARD = (217, 164, 65)
INDIGO = (46, 58, 80)
TERRACOTTA = (193, 85, 46)
PLUM = (125, 46, 59)
CHARCOAL = (38, 32, 25)
GOLD = (255, 213, 79)  # tiny accent dots only — not a hero ball


def lerp(a, b, t):
    return int(a + (b - a) * t)


def grad(im, c0, c1, vertical=True):
    dr = ImageDraw.Draw(im)
    steps = H if vertical else W
    for i in range(steps):
        t = i / max(1, steps - 1)
        c = (lerp(c0[0], c1[0], t), lerp(c0[1], c1[1], t), lerp(c0[2], c1[2], t))
        if vertical:
            dr.line([(0, i), (W, i)], fill=c)
        else:
            dr.line([(i, 0), (i, H)], fill=c)


def vignette(im, strength=0.35):
    overlay = Image.new("RGB", (W, H), (0, 0, 0))
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse((-W * 0.1, -H * 0.2, W * 1.1, H * 1.2), fill=int(255 * strength))
    mask = mask.filter(ImageFilter.GaussianBlur(120))
    return Image.composite(overlay, im, mask)


def noise(im, amt=8):
    rnd = random.Random(42)
    px = im.load()
    for _ in range(W * H // 40):
        x, y = rnd.randrange(W), rnd.randrange(H)
        r, g, b = px[x, y]
        d = rnd.randint(-amt, amt)
        px[x, y] = (max(0, min(255, r + d)), max(0, min(255, g + d)), max(0, min(255, b + d)))
    return im


def skyline(seed=1):
    rnd = random.Random(seed)
    im = Image.new("RGB", (W, H))
    grad(im, INDIGO, CREAM)
    d = ImageDraw.Draw(im)
    y0 = int(H * 0.55)
    d.rectangle([0, y0, W, H], fill=CHARCOAL)
    x = 40
    while x < W - 40:
        bw = rnd.randint(40, 110)
        bh = rnd.randint(80, 420)
        d.rectangle(
            [x, y0 - bh, x + bw, y0],
            fill=(
                lerp(INDIGO[0], CHARCOAL[0], 0.4),
                lerp(INDIGO[1], CHARCOAL[1], 0.4),
                lerp(INDIGO[2], CHARCOAL[2], 0.4),
            ),
        )
        # window dots
        for wy in range(y0 - bh + 10, y0 - 10, 18):
            for wx in range(x + 8, x + bw - 8, 14):
                if rnd.random() > 0.45:
                    d.rectangle([wx, wy, wx + 6, wy + 8], fill=MUSTARD if rnd.random() > 0.7 else (90, 100, 120))
        x += bw + rnd.randint(8, 28)
    # sun disc (not yellow-ball hero — cream/mustard wash)
    d.ellipse([W - 280, 80, W - 120, 240], fill=MUSTARD)
    im = vignette(im, 0.25)
    return noise(im, 6)


def solar_field(seed=2):
    rnd = random.Random(seed)
    im = Image.new("RGB", (W, H))
    grad(im, (120, 160, 200), CREAM)
    d = ImageDraw.Draw(im)
    d.rectangle([0, int(H * 0.55), W, H], fill=(90, 110, 70))
    for row in range(6):
        for col in range(14):
            x = 80 + col * 120 + row * 8
            y = 520 + row * 70
            d.rectangle([x, y, x + 90, y + 45], fill=INDIGO, outline=MUSTARD)
            d.line([x, y + 22, x + 90, y + 22], fill=(70, 90, 120))
    d.ellipse([100, 60, 220, 180], fill=GOLD)
    return vignette(noise(im, 5), 0.2)


def data_grid(seed=3):
    rnd = random.Random(seed)
    im = Image.new("RGB", (W, H), CHARCOAL)
    d = ImageDraw.Draw(im)
    for x in range(0, W, 48):
        d.line([(x, 0), (x, H)], fill=(55, 48, 40), width=1)
    for y in range(0, H, 48):
        d.line([(0, y), (W, y)], fill=(55, 48, 40), width=1)
    for _ in range(40):
        x0, y0 = rnd.randint(40, W - 40), rnd.randint(40, H - 40)
        x1, y1 = x0 + rnd.randint(-200, 200), y0 + rnd.randint(-200, 200)
        d.line([(x0, y0), (x1, y1)], fill=MUSTARD if rnd.random() > 0.5 else TERRACOTTA, width=2)
        d.ellipse([x0 - 4, y0 - 4, x0 + 4, y0 + 4], fill=GOLD)
    return vignette(im, 0.4)


def road_dusk(seed=4):
    im = Image.new("RGB", (W, H))
    grad(im, PLUM, INDIGO)
    d = ImageDraw.Draw(im)
    # road trapezoid
    d.polygon([(W * 0.35, H), (W * 0.65, H), (W * 0.52, H * 0.45), (W * 0.48, H * 0.45)], fill=CHARCOAL)
    for i in range(8):
        y = int(H * 0.5 + i * 60)
        w = 8 + i * 4
        d.rectangle([W // 2 - w // 2, y, W // 2 + w // 2, y + 24], fill=MUSTARD)
    d.ellipse([W - 260, 40, W - 100, 200], fill=TERRACOTTA)
    return vignette(noise(im, 7), 0.3)


def market_awning(seed=5):
    rnd = random.Random(seed)
    im = Image.new("RGB", (W, H))
    grad(im, CREAM, MUSTARD, vertical=False)
    d = ImageDraw.Draw(im)
    d.rectangle([0, int(H * 0.6), W, H], fill=(70, 60, 50))
    colors = [TERRACOTTA, MUSTARD, INDIGO, PLUM, CREAM]
    x = 0
    for i in range(16):
        bw = W // 16
        d.rectangle([x, 200, x + bw, 520], fill=colors[i % len(colors)])
        d.polygon([(x, 200), (x + bw, 200), (x + bw // 2, 140)], fill=colors[(i + 2) % len(colors)])
        x += bw
    return vignette(noise(im, 5), 0.22)


def fiber_abstract(seed=6):
    rnd = random.Random(seed)
    im = Image.new("RGB", (W, H), INDIGO)
    d = ImageDraw.Draw(im)
    for i in range(30):
        y = 40 + i * 34
        amp = 40 + (i % 5) * 12
        pts = [(x, int(y + math.sin(x / 80 + i) * amp)) for x in range(0, W, 8)]
        d.line(pts, fill=MUSTARD if i % 3 else GOLD, width=2)
    return vignette(im, 0.35)


SPECS = [
    ("k11_native_skyline", skyline, 1),
    ("k12_native_solar", solar_field, 2),
    ("k13_native_datagrid", data_grid, 3),
    ("k14_native_road_dusk", road_dusk, 4),
    ("k15_native_market", market_awning, 5),
    ("k16_native_fiber", fiber_abstract, 6),
    ("k17_native_skyline_b", skyline, 11),
    ("k18_native_solar_b", solar_field, 12),
    ("k19_native_datagrid_b", data_grid, 13),
    ("k20_native_road_b", road_dusk, 14),
    ("k21_native_market_b", market_awning, 15),
    ("k22_native_fiber_b", fiber_abstract, 16),
]


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    out = []
    for name, fn, seed in SPECS:
        path = ROOT / f"{name}.jpg"
        im = fn(seed).convert("RGB")
        im = im.filter(ImageFilter.GaussianBlur(0.6))
        im.save(path, "JPEG", quality=92, optimize=True)
        out.append(str(path))
        print("OK", path.name)
    print(f"DONE {len(out)} stills -> {ROOT}")


if __name__ == "__main__":
    main()
