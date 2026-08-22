"""
Generate ≥3 cited infographic stills per scene (1920×1080) for Africa S1.
Yellow-base soft-pop documentary style. Real sources in footer + SOURCES.md.
Does not touch Blender GPU. CPU matplotlib only.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Wedge, Circle
import numpy as np

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
OUT = PROJECT / "assets" / "canva" / "kinetic" / "infographics"
OUT.mkdir(parents=True, exist_ok=True)
MANIFEST = PROJECT / "renders" / "quality" / "infographics_manifest.json"
SOURCES = PROJECT / "docs" / "INFOGRAPHIC_SOURCES.md"

# Palette — yellow base soft-pop
BG = "#1A1408"
PANEL = "#2A2210"
YELLOW = "#FFD54F"
CREAM = "#FFF6D6"
TEAL = "#2EC4B6"
CORAL = "#FF6B4A"
SOFT = "#8B7E5A"
WHITE = "#FFF8E7"

W, H = 1920, 1080


def fig_ax():
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100, facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor(BG)
    return fig, ax


def title_block(ax, scene: str, title: str, subtitle: str = ""):
    ax.add_patch(FancyBboxPatch((60, 920), 1800, 120, boxstyle="round,pad=8,rounding_size=18",
                                facecolor=PANEL, edgecolor=YELLOW, linewidth=2))
    ax.text(90, 990, f"S{scene}  ·  SILICON SAVANNAH", color=YELLOW, fontsize=18, fontweight="bold", va="center")
    ax.text(90, 955, title, color=CREAM, fontsize=32, fontweight="bold", va="center")
    if subtitle:
        ax.text(90, 935, subtitle, color=SOFT, fontsize=14, va="center")


def footer(ax, source: str):
    ax.text(90, 40, source, color=SOFT, fontsize=11, va="center", wrap=True)
    ax.text(1830, 40, "Africa S1 · illustrative motion-graphics still", color=SOFT, fontsize=10, ha="right", va="center")


def save(fig, path: Path):
    fig.savefig(path, dpi=100, facecolor=BG)
    plt.close(fig)
    print("OK", path.name, flush=True)


def pie_chart(ax, cx, cy, r, sizes, colors, labels):
    total = sum(sizes)
    ang = 90
    for size, color, lab in zip(sizes, colors, labels):
        theta = 360 * size / total
        wedge = Wedge((cx, cy), r, ang - theta, ang, facecolor=color, edgecolor=BG, linewidth=3)
        ax.add_patch(wedge)
        mid = np.deg2rad(ang - theta / 2)
        lx, ly = cx + (r + 70) * np.cos(mid), cy + (r + 70) * np.sin(mid)
        ax.text(lx, ly, lab, color=CREAM, fontsize=14, ha="center", va="center", fontweight="bold")
        ang -= theta
    ax.add_patch(Circle((cx, cy), r * 0.42, facecolor=BG, edgecolor=YELLOW, linewidth=2))


def bar_h(ax, x, y, width, height, value, vmax, color, label, val_txt):
    ax.add_patch(FancyBboxPatch((x, y), width, height, boxstyle="round,pad=2,rounding_size=8",
                                facecolor="#3A3018", edgecolor=SOFT, linewidth=1))
    fill_w = max(8, width * (value / vmax))
    ax.add_patch(FancyBboxPatch((x, y), fill_w, height, boxstyle="round,pad=2,rounding_size=8",
                                facecolor=color, edgecolor="none"))
    ax.text(x - 10, y + height / 2, label, color=CREAM, fontsize=16, ha="right", va="center")
    ax.text(x + fill_w + 16, y + height / 2, val_txt, color=YELLOW, fontsize=16, va="center", fontweight="bold")


def big_stat(ax, x, y, value, label):
    ax.text(x, y + 40, value, color=YELLOW, fontsize=72, fontweight="bold", ha="center", va="center")
    ax.text(x, y - 40, label, color=CREAM, fontsize=18, ha="center", va="center")


# --- Specs: 3+ per scene with cited figures ---
SPECS: list[dict] = []


def add(scene, stem, kind, title, render_fn, source, notes=""):
    SPECS.append({
        "scene": scene, "stem": stem, "kind": kind, "title": title,
        "source": source, "notes": notes, "render": render_fn,
    })


# S01 Cold Open
def r_s01_a():
    fig, ax = fig_ax()
    title_block(ax, "01", "Morning money already moved", "Mobile money penetration · Kenya")
    big_stat(ax, 480, 580, "82.1%", "mobile-money penetration\n(CA Q2 FY2024/25)")
    big_stat(ax, 1200, 580, "42.3M", "mobile-money subscriptions")
    footer(ax, "Source: Communications Authority of Kenya, Sector Statistics Report Q2 FY2024/25 (Oct–Dec 2024).")
    save(fig, OUT / "inf_s01_mm_penetration_stat.png")


def r_s01_b():
    fig, ax = fig_ax()
    title_block(ax, "01", "Who moves the money?", "Mobile money market share · Kenya")
    pie_chart(ax, 960, 520, 260, [92.3, 7.6, 0.1], [YELLOW, TEAL, CORAL],
              ["Safaricom\n92.3%", "Airtel Money\n7.6%", "Other\n<1%"])
    footer(ax, "Source: CA Kenya — Increased Smartphone Adoption & Mobile Money (Sep 2024 sector note). Brand names nominative.")
    save(fig, OUT / "inf_s01_mm_share_pie.png")


def r_s01_c():
    fig, ax = fig_ax()
    title_block(ax, "01", "Devices in pockets", "Feature phones vs smartphones · Kenya (Dec 2024)")
    bar_h(ax, 520, 680, 1100, 70, 41.48, 45, YELLOW, "Smartphones", "41.5M")
    bar_h(ax, 520, 520, 1100, 70, 30.58, 45, TEAL, "Feature phones", "30.6M")
    bar_h(ax, 520, 360, 1100, 70, 71.4, 80, CORAL, "Active SIMs", "71.4M · 138.5% pen.")
    footer(ax, "Source: CA Kenya Sector Statistics Report Q2 FY2024/25.")
    save(fig, OUT / "inf_s01_devices_bars.png")


add("01", "inf_s01_mm_penetration_stat", "stat", "82.1% MM penetration", r_s01_a,
    "CA Kenya Q2 FY2024/25")
add("01", "inf_s01_mm_share_pie", "pie", "MM market share pie", r_s01_b, "CA Kenya Sep 2024")
add("01", "inf_s01_devices_bars", "bars", "Devices bars", r_s01_c, "CA Kenya Q2 FY2024/25")


# S02 M-Pesa 2007
def r_s02_a():
    fig, ax = fig_ax()
    title_block(ax, "02", "M-Pesa at scale (FY25)", "One-month active customers · Kenya")
    big_stat(ax, 960, 620, "35.82M", "one-month active M-Pesa customers (+10.5% YoY)")
    ax.text(960, 420, "Agents >298,000  ·  Txn value KSh 38.29T  ·  Volume 37.15B", color=CREAM, fontsize=18, ha="center")
    footer(ax, "Source: Safaricom / M-PESA Africa FY25 results summary (Apr 2024–Mar 2025). Nominative brand reference.")
    save(fig, OUT / "inf_s02_mpesa_active_stat.png")


def r_s02_b():
    fig, ax = fig_ax()
    title_block(ax, "02", "From cash to text rails", "Conceptual flow (documentary diagram)")
    steps = [("1", "Sender\nphone"), ("2", "Agent\nnetwork"), ("3", "SMS\ntransfer"), ("4", "Recipient")]
    for i, (n, lab) in enumerate(steps):
        x = 280 + i * 400
        ax.add_patch(Circle((x, 560), 90, facecolor=PANEL, edgecolor=YELLOW, linewidth=3))
        ax.text(x, 560, n, color=YELLOW, fontsize=36, ha="center", va="center", fontweight="bold")
        ax.text(x, 420, lab, color=CREAM, fontsize=16, ha="center")
        if i < 3:
            ax.annotate("", xy=(x + 160, 560), xytext=(x + 100, 560),
                        arrowprops=dict(arrowstyle="->", color=TEAL, lw=3))
    footer(ax, "Diagrammatic (not proprietary UI). Context: M-Pesa launch 2007 — Safaricom annual reporting lineage.")
    save(fig, OUT / "inf_s02_mpesa_flow_steps.png")


def r_s02_c():
    fig, ax = fig_ax()
    title_block(ax, "02", "Account ownership · Kenya", "World Bank Global Findex lineage")
    bar_h(ax, 560, 680, 1000, 70, 90, 100, YELLOW, "Any account (2025 Findex*", "≈90%")
    bar_h(ax, 560, 520, 1000, 70, 79, 100, TEAL, "Account ownership (Findex 2021)", "79%")
    bar_h(ax, 560, 360, 1000, 70, 58, 100, CORAL, "Mobile money (Findex 2014)", "58%")
    ax.text(960, 250, "*Kenya row in 2025 Global Findex regional summaries / secondary reporting", color=SOFT, fontsize=12, ha="center")
    footer(ax, "Sources: World Bank Global Findex 2021 SSA note; 2025 Findex Kenya connectivity summaries.")
    save(fig, OUT / "inf_s02_findex_bars.png")


add("02", "inf_s02_mpesa_active_stat", "stat", "35.82M active", r_s02_a, "Safaricom FY25")
add("02", "inf_s02_mpesa_flow_steps", "flow", "Flow steps", r_s02_b, "Documentary diagram")
add("02", "inf_s02_findex_bars", "bars", "Findex bars", r_s02_c, "World Bank Findex")


# S03 Hubs
def r_s03_a():
    fig, ax = fig_ax()
    title_block(ax, "03", "Hub stack · Silicon Savannah", "Talent · space · capital (concept map)")
    hubs = [("iHub", "Community\n& founders"), ("Andela", "Talent\npipelines"), ("NaiLab", "Incubation\n& startups")]
    for i, (name, desc) in enumerate(hubs):
        x = 360 + i * 500
        ax.add_patch(FancyBboxPatch((x - 160, 420), 320, 280, boxstyle="round,pad=10,rounding_size=20",
                                    facecolor=PANEL, edgecolor=YELLOW, linewidth=2))
        ax.text(x, 620, name, color=YELLOW, fontsize=28, ha="center", fontweight="bold")
        ax.text(x, 520, desc, color=CREAM, fontsize=16, ha="center")
    footer(ax, "Nominative hub names for documentary context. Style: TED-Ed factor cards.")
    save(fig, OUT / "inf_s03_hub_factor_cards.png")


def r_s03_b():
    fig, ax = fig_ax()
    title_block(ax, "03", "Africa tech capital 2024", "Equity + debt combined · Partech")
    big_stat(ax, 960, 600, "$3.2B", "Africa tech VC (equity+debt) 2024 · −7% YoY")
    ax.text(960, 400, "Fintech ≈60% of equity funding · 131 deals", color=CREAM, fontsize=20, ha="center")
    footer(ax, "Source: Partech Africa Tech Venture Capital Report 2024.")
    save(fig, OUT / "inf_s03_partech_32b_stat.png")


def r_s03_c():
    fig, ax = fig_ax()
    title_block(ax, "03", "Big Four equity 2024", "Country equity funding · Partech")
    countries = [("Nigeria", 520, YELLOW), ("Egypt", 400, TEAL), ("South Africa", 350, CORAL), ("Kenya", 221, SOFT)]
    for i, (name, val, col) in enumerate(countries):
        bar_h(ax, 560, 720 - i * 120, 1100, 70, val, 520, col, name, f"${val}M")
    footer(ax, "Source: Partech Africa Tech VC 2024 (equity amounts). Kenya led debt share (~38%).")
    save(fig, OUT / "inf_s03_big4_equity_bars.png")


add("03", "inf_s03_hub_factor_cards", "cards", "Hub cards", r_s03_a, "Documentary")
add("03", "inf_s03_partech_32b_stat", "stat", "$3.2B", r_s03_b, "Partech 2024")
add("03", "inf_s03_big4_equity_bars", "bars", "Big4 bars", r_s03_c, "Partech 2024")


# S04 Phone
def r_s04_a():
    fig, ax = fig_ax()
    title_block(ax, "04", "Smartphone surge", "Kenya device stock · CA")
    pie_chart(ax, 960, 520, 250, [41.48, 30.58], [YELLOW, TEAL], ["Smartphones\n41.5M", "Feature\n30.6M"])
    footer(ax, "Source: CA Kenya Sector Statistics Report Q2 FY2024/25.")
    save(fig, OUT / "inf_s04_phone_mix_pie.png")


def r_s04_b():
    fig, ax = fig_ax()
    title_block(ax, "04", "Kenya 4G device growth", "National mobile network · device stock (FY24)")
    bar_h(ax, 560, 680, 1100, 70, 16.85, 23, YELLOW, "4G devices", "16.85M (+27.5%)")
    bar_h(ax, 560, 520, 1100, 70, 22.93, 23, TEAL, "Smartphones on network", "22.93M (+12.9%)")
    bar_h(ax, 560, 360, 1100, 70, 0.67, 23, CORAL, "5G devices", "0.67M (+79.3%)")
    footer(ax, "Source: Kenya operator public annual filings 2024 (device counts).")
    save(fig, OUT / "inf_s04_kenya_4g_device_bars.png")


def r_s04_c():
    fig, ax = fig_ax()
    title_block(ax, "04", "Phone ownership · Kenya", "Global Findex connectivity")
    big_stat(ax, 960, 580, "93%", "adults with a mobile phone (Findex Kenya 2025 summaries)")
    footer(ax, "Source: World Bank Global Findex 2025 Kenya / regional connectivity tables (secondary).")
    save(fig, OUT / "inf_s04_phone_ownership_stat.png")


add("04", "inf_s04_phone_mix_pie", "pie", "Phone mix", r_s04_a, "CA Kenya")
add("04", "inf_s04_kenya_4g_device_bars", "bars", "4G bars", r_s04_b, "Operator AR 2024")
add("04", "inf_s04_phone_ownership_stat", "stat", "93% phones", r_s04_c, "Findex 2025")


# S05 Money $984M / 82%
def r_s05_a():
    fig, ax = fig_ax()
    title_block(ax, "05", "Kenya startup funding 2025", "Episode hero figure · Africa: The Big Deal")
    big_stat(ax, 960, 620, "$984M", "raised by Kenyan startups in 2025")
    ax.text(960, 420, "≈ KSh 126.9B  ·  ~31% of Africa startup funding", color=CREAM, fontsize=20, ha="center")
    footer(ax, "Source: Africa: The Big Deal via Business Daily / Citizen Digital (2025 funding trackers).")
    save(fig, OUT / "inf_s05_984m_stat.png")


def r_s05_b():
    fig, ax = fig_ax()
    title_block(ax, "05", "82% → top five", "Capital concentration · Kenya 2025")
    pie_chart(ax, 960, 520, 260, [82, 18], [CORAL, YELLOW], ["Top 5 firms\n82%", "Rest of\necosystem\n18%"])
    ax.text(960, 200, "Top recipients cited in coverage: d.light, Sun King, M-KOPA, BURN, PowerGen", color=SOFT, fontsize=13, ha="center")
    footer(ax, "Source: Citizen Digital / TechPoint Africa summarizing Africa: The Big Deal 2025.")
    save(fig, OUT / "inf_s05_82pct_pie.png")


def r_s05_c():
    fig, ax = fig_ax()
    title_block(ax, "05", "Debt vs equity · Kenya 2025", "Structure of the $984M year")
    pie_chart(ax, 960, 520, 250, [60, 40], [TEAL, YELLOW], ["Debt\n≈60%\n($582M)", "Equity\n≈40%\n($383M)"])
    footer(ax, "Source: Africa: The Big Deal / Eastleigh Voice / Tech In Africa summaries of 2025 Kenya totals.")
    save(fig, OUT / "inf_s05_debt_equity_pie.png")


def r_s05_d():
    fig, ax = fig_ax()
    title_block(ax, "05", "Africa Big Four 2025 funding", "Country haul comparison")
    for i, (name, val, col) in enumerate([
        ("Kenya", 984, YELLOW), ("Egypt", 614, TEAL), ("South Africa", 599, CORAL), ("Nigeria", 343, SOFT)
    ]):
        bar_h(ax, 560, 720 - i * 120, 1100, 70, val, 984, col, name, f"${val}M")
    footer(ax, "Source: Africa: The Big Deal 2025 country rankings (Business Daily / Citizen Digital).")
    save(fig, OUT / "inf_s05_africa_big4_2025_bars.png")


add("05", "inf_s05_984m_stat", "stat", "$984M", r_s05_a, "The Big Deal 2025")
add("05", "inf_s05_82pct_pie", "pie", "82% pie", r_s05_b, "The Big Deal 2025")
add("05", "inf_s05_debt_equity_pie", "pie", "Debt/equity", r_s05_c, "The Big Deal 2025")
add("05", "inf_s05_africa_big4_2025_bars", "bars", "Big4 2025", r_s05_d, "The Big Deal 2025")


# S06 Solar
def r_s06_a():
    fig, ax = fig_ax()
    title_block(ax, "06", "Electricity access · Kenya", "IEA Energy Policy Review Kenya 2024")
    big_stat(ax, 520, 580, "79%", "national access (2023)")
    big_stat(ax, 1200, 580, "100%", "urban access")
    ax.text(960, 360, "Access rose from 37% (2013) → 79% (2023)", color=CREAM, fontsize=18, ha="center")
    footer(ax, "Source: IEA, Kenya 2024 Energy Policy Review / Executive Summary.")
    save(fig, OUT / "inf_s06_iea_access_stat.png")


def r_s06_b():
    fig, ax = fig_ax()
    title_block(ax, "06", "Generation mix · renewables lead", "Kenya power system (IEA)")
    pie_chart(ax, 960, 520, 250, [80, 20], [YELLOW, SOFT], ["Renewables\n≈80% of\ncapacity", "Other\n≈20%"])
    ax.text(960, 200, "Geothermal · hydro · wind · solar PV dominate the mix", color=CREAM, fontsize=16, ha="center")
    footer(ax, "Source: IEA Kenya 2024 — renewables ~80% of capacity; nearly 90% of generation from RE resources.")
    save(fig, OUT / "inf_s06_renewables_pie.png")


def r_s06_c():
    fig, ax = fig_ax()
    title_block(ax, "06", "Off-grid solar leadership", "East Africa SHS market")
    big_stat(ax, 960, 600, "~74%", "of East Africa solar home system sales (2023)")
    ax.text(960, 400, "Kenya = largest / most mature off-grid solar market globally (IEA)", color=CREAM, fontsize=16, ha="center")
    footer(ax, "Source: IEA Kenya 2024 Executive Summary (SHS sales share East Africa 2023).")
    save(fig, OUT / "inf_s06_shs_share_stat.png")


add("06", "inf_s06_iea_access_stat", "stat", "79% access", r_s06_a, "IEA Kenya 2024")
add("06", "inf_s06_renewables_pie", "pie", "RE pie", r_s06_b, "IEA Kenya 2024")
add("06", "inf_s06_shs_share_stat", "stat", "74% SHS", r_s06_c, "IEA Kenya 2024")


# S07 Gap 97%
def r_s07_a():
    fig, ax = fig_ax()
    title_block(ax, "07", "97.4% in Nairobi", "Geographic concentration of tracked Kenyan tech startups")
    pie_chart(ax, 960, 520, 260, [97.4, 2.6], [CORAL, YELLOW], ["Nairobi\n97.4%", "Rest of\nKenya\n2.6%"])
    footer(ax, "Source: Disrupt Africa — The Kenyan Startup Ecosystem Report 2022 (97.4% of tracked tech startups).")
    save(fig, OUT / "inf_s07_nairobi_97_pie.png")


def r_s07_b():
    fig, ax = fig_ax()
    title_block(ax, "07", "Secondary cities named in VO", "Mombasa · Kisumu · Eldoret · Nakuru")
    cities = ["Mombasa", "Kisumu", "Eldoret", "Nakuru"]
    for i, c in enumerate(cities):
        x = 280 + i * 400
        ax.add_patch(FancyBboxPatch((x - 140, 480), 280, 160, boxstyle="round,pad=8,rounding_size=16",
                                    facecolor=PANEL, edgecolor=TEAL, linewidth=2))
        ax.text(x, 560, c, color=CREAM, fontsize=22, ha="center", fontweight="bold")
    ax.text(960, 360, "Emerging hubs — still thin on VC vs Nairobi (TechCabal 2026 analysis)", color=SOFT, fontsize=14, ha="center")
    footer(ax, "Sources: Episode VO; TechCabal ‘Kenya’s tech future is no longer a Nairobi monopoly’ (Jan 2026).")
    save(fig, OUT / "inf_s07_secondary_cities_cards.png")


def r_s07_c():
    fig, ax = fig_ax()
    title_block(ax, "07", "Rural electricity still gaps", "Access is not evenly distributed")
    bar_h(ax, 560, 680, 1100, 70, 100, 100, YELLOW, "Urban access (IEA)", "≈100%")
    bar_h(ax, 560, 520, 1100, 70, 67.9, 100, TEAL, "Rural access (WB 2023)", "67.9%")
    bar_h(ax, 560, 360, 1100, 70, 51, 100, CORAL, "Rural KPLC connection (Afrobarometer)", "≈51%")
    footer(ax, "Sources: IEA Kenya 2024; World Bank rural electricity access; Afrobarometer AD892 (2024).")
    save(fig, OUT / "inf_s07_rural_urban_bars.png")


add("07", "inf_s07_nairobi_97_pie", "pie", "97.4% pie", r_s07_a, "Disrupt Africa 2022")
add("07", "inf_s07_secondary_cities_cards", "cards", "Cities", r_s07_b, "TechCabal / VO")
add("07", "inf_s07_rural_urban_bars", "bars", "Rural gap", r_s07_c, "IEA / WB / Afrobarometer")


# S08 Secondary city quiet
def r_s08_a():
    fig, ax = fig_ax()
    title_block(ax, "08", "Quiet beat · funding thins out", "Conceptual contrast card")
    ax.add_patch(FancyBboxPatch((200, 360), 700, 420, boxstyle="round,pad=12,rounding_size=20",
                                facecolor=PANEL, edgecolor=YELLOW, linewidth=2))
    ax.add_patch(FancyBboxPatch((1020, 360), 700, 420, boxstyle="round,pad=12,rounding_size=20",
                                facecolor="#15100A", edgecolor=SOFT, linewidth=2))
    ax.text(550, 620, "NAIROBI", color=YELLOW, fontsize=28, ha="center", fontweight="bold")
    ax.text(550, 520, "HQ · VC · press\ninvestor meetings", color=CREAM, fontsize=18, ha="center")
    ax.text(1370, 620, "SECONDARY CITY", color=SOFT, fontsize=24, ha="center", fontweight="bold")
    ax.text(1370, 520, "Thinner capital\nthinner coverage", color=CREAM, fontsize=18, ha="center")
    footer(ax, "Illustrative contrast for S08. Grounded by Disrupt Africa 97.4% Nairobi concentration.")
    save(fig, OUT / "inf_s08_nairobi_vs_secondary.png")


def r_s08_b():
    fig, ax = fig_ax()
    title_block(ax, "08", "Clean cooking lag", "Energy access is multi-dimensional")
    big_stat(ax, 520, 580, ">30%", "clean cooking access 2023")
    big_stat(ax, 1200, 580, "10%", "clean cooking in 2013")
    ax.text(960, 360, "69% of households still rely on traditional cooking fuels (IEA)", color=CREAM, fontsize=16, ha="center")
    footer(ax, "Source: IEA Kenya 2024 Executive Summary.")
    save(fig, OUT / "inf_s08_clean_cooking_stat.png")


def r_s08_c():
    fig, ax = fig_ax()
    title_block(ax, "08", "Mobile data subscriptions", "Connectivity outside the capital story")
    big_stat(ax, 960, 600, "56.1M", "mobile data subscriptions (Dec 2024)")
    ax.text(960, 420, "Broadband subs 44.8M (+12.3% QoQ)", color=CREAM, fontsize=18, ha="center")
    footer(ax, "Source: CA Kenya Sector Statistics Report Q2 FY2024/25.")
    save(fig, OUT / "inf_s08_data_subs_stat.png")


add("08", "inf_s08_nairobi_vs_secondary", "cards", "Contrast", r_s08_a, "Documentary")
add("08", "inf_s08_clean_cooking_stat", "stat", "Cooking", r_s08_b, "IEA Kenya 2024")
add("08", "inf_s08_data_subs_stat", "stat", "Data subs", r_s08_c, "CA Kenya")


# S09 Closer
def r_s09_a():
    fig, ax = fig_ax()
    title_block(ax, "09", "Kenya led Africa funding 2025", "Optimism with caveats")
    big_stat(ax, 960, 600, "#1", "African market by startup capital raised (2025)")
    ax.text(960, 400, "$984M · almost hitting the $1B mark (The Big Deal)", color=CREAM, fontsize=18, ha="center")
    footer(ax, "Source: Africa: The Big Deal via Business Daily (Jan 2026 coverage of 2025 totals).")
    save(fig, OUT / "inf_s09_kenya_rank1_stat.png")


def r_s09_b():
    fig, ax = fig_ax()
    title_block(ax, "09", "75 startups funded ≥$100k", "Breadth beyond megadeals")
    big_stat(ax, 960, 580, "75", "Kenyan startups raised ≥ $100k in 2025")
    footer(ax, "Source: Africa: The Big Deal / Business Daily 2025 Kenya funding summary.")
    save(fig, OUT / "inf_s09_75_startups_stat.png")


def r_s09_c():
    fig, ax = fig_ax()
    title_block(ax, "09", "Climate / energy tilt", "Why the story shifts from pure fintech")
    pie_chart(ax, 960, 520, 250, [46, 15, 13, 26], [YELLOW, TEAL, CORAL, SOFT],
              ["Cleantech\n46%*", "Agritech\n15%*", "Fintech\n13%*", "Other\n26%*"])
    ax.text(960, 180, "*Kenya equity sector mix 2024 (Partech) — cleantech-led year", color=SOFT, fontsize=12, ha="center")
    footer(ax, "Source: Partech Africa Tech VC 2024 — Kenya equity sector shares.")
    save(fig, OUT / "inf_s09_kenya_sector_pie.png")


add("09", "inf_s09_kenya_rank1_stat", "stat", "#1 market", r_s09_a, "The Big Deal")
add("09", "inf_s09_75_startups_stat", "stat", "75 startups", r_s09_b, "The Big Deal")
add("09", "inf_s09_kenya_sector_pie", "pie", "Sectors", r_s09_c, "Partech 2024")


# S10 End card
def r_s10_a():
    fig, ax = fig_ax()
    title_block(ax, "10", "Series lockup · key figures", "Three numbers from the episode")
    for i, (v, lab) in enumerate([("$984M", "Kenya funding 2025"), ("82%", "to top five"), ("97.4%", "startups in Nairobi")]):
        x = 360 + i * 500
        ax.add_patch(FancyBboxPatch((x - 180, 420), 360, 300, boxstyle="round,pad=10,rounding_size=20",
                                    facecolor=PANEL, edgecolor=YELLOW, linewidth=2))
        ax.text(x, 600, v, color=YELLOW, fontsize=36, ha="center", fontweight="bold")
        ax.text(x, 500, lab, color=CREAM, fontsize=14, ha="center")
    footer(ax, "Sources: The Big Deal 2025; Disrupt Africa 2022 (97.4%).")
    save(fig, OUT / "inf_s10_three_numbers.png")


def r_s10_b():
    fig, ax = fig_ax()
    title_block(ax, "10", "Silicon Savannah · takeaway", "Rails → hubs → capital → gap")
    labels = ["Mobile\nrails", "Talent\nhubs", "Climate\ncapital", "Geographic\ngap"]
    for i, lab in enumerate(labels):
        x = 280 + i * 400
        ax.add_patch(Circle((x, 560), 100, facecolor=PANEL, edgecolor=YELLOW, linewidth=3))
        ax.text(x, 560, str(i + 1), color=YELLOW, fontsize=32, ha="center", va="center", fontweight="bold")
        ax.text(x, 400, lab, color=CREAM, fontsize=16, ha="center")
        if i < 3:
            ax.annotate("", xy=(x + 170, 560), xytext=(x + 110, 560),
                        arrowprops=dict(arrowstyle="->", color=TEAL, lw=3))
    footer(ax, "Narrative arc diagram for end card. Data-backed in prior scene graphics.")
    save(fig, OUT / "inf_s10_narrative_arc.png")


def r_s10_c():
    fig, ax = fig_ax()
    title_block(ax, "10", "Primary sources used", "For verification & Canva polish")
    lines = [
        "CA Kenya Sector Statistics Q2 FY2024/25",
        "Safaricom Annual Report 2024 / FY25 M-Pesa results",
        "Partech Africa Tech VC 2024",
        "Africa: The Big Deal 2025 (Business Daily / Citizen)",
        "IEA Kenya 2024 Energy Policy Review",
        "Disrupt Africa Kenyan Startup Ecosystem Report 2022",
        "World Bank Global Findex (2021/2025 Kenya)",
    ]
    for i, line in enumerate(lines):
        ax.text(200, 780 - i * 70, f"•  {line}", color=CREAM, fontsize=18, va="center")
    footer(ax, "Full URLs in docs/INFOGRAPHIC_SOURCES.md")
    save(fig, OUT / "inf_s10_sources_card.png")


add("10", "inf_s10_three_numbers", "cards", "Three numbers", r_s10_a, "Episode + sources")
add("10", "inf_s10_narrative_arc", "flow", "Arc", r_s10_b, "Documentary")
add("10", "inf_s10_sources_card", "list", "Sources", r_s10_c, "Meta")


def main():
    report = {"count": 0, "by_scene": {}, "files": []}
    for spec in SPECS:
        spec["render"]()
        sc = spec["scene"]
        report["by_scene"].setdefault(sc, []).append(spec["stem"] + ".png")
        report["files"].append({
            "scene": sc, "file": spec["stem"] + ".png", "kind": spec["kind"],
            "title": spec["title"], "source": spec["source"],
        })
        report["count"] += 1
    MANIFEST.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("MANIFEST", MANIFEST, "count=", report["count"], flush=True)
    for sc, files in sorted(report["by_scene"].items()):
        print(f"S{sc}: {len(files)}", flush=True)


if __name__ == "__main__":
    main()
