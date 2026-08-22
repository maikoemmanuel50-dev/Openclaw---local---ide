# Scene Resource + Dense Cut Roadmap — Episode 01

**Why this exists:** Prior Resolve pace lists ~24 kinetic hits across 7 minutes (~ASL >15s on B-roll). That reads as a **low frame/cut count**. Fern / kinetic target is **0.4–1.0s inserts** on V3/V4 while V1 Blender plates hold the spine.

**Sources in play (all must be used):**
| Bucket | Path | Count (approx) |
|--------|------|----------------|
| Canva scene plates | `assets/canva/s*.png` | 9 hero plates |
| Graded kinetic stills | `assets/canva/kinetic/graded_1080/` | 48 PNG |
| Generated HQ (`pr_s*`) | same + `kinetic/hq/` | 20+ |
| License-free stock video | `assets/stock/license_free/graded_1080/` | 14 MP4 |
| Stock stills / pans | `assets/stock/license_free/raw/pan_*.jpg` | 18 |
| Pre-cut stock overlays | `renders/paced_overlays/stock_cinematic/` | 38 MP4 (10–16f) |
| Pre-cut kinetic overlays | `renders/paced_overlays/kinetic/` | 35 MP4 |
| HDRI / PBR | `assets/hdri/`, `assets/textures/polyhaven/` | lighting / realism |
| Diagrams / icons | `assets/diagrams/`, `assets/icons/` | UI accents |

**Track rule (this pass):** V2 yellow ball **OFF**. Stock + kinetic share **V3 / V4**. Protect TextStat windows on V5 (no dense overlays during `$984M`, `82%`, `97%`).

**Execution:** `scripts/resolve_pace_kinetic_yb.py` (dense `KINETIC` + `STOCK` tables) · imported by `finish_after_hq.ps1` with `AFRICA_NO_YELLOW_BALL=1`.

**ASL targets by scene type:** montage **10–14f** · detail **12–16f** · stock motion **12–16f** · quiet S08 **16–24f** · end card **minimal**.

Timeline offsets assume contiguous plates: S01 `0`, S02 `1200`, S03 `2280`, S04 `3360`, S05 `3960`, S06 `5040`, S07 `6000`, S08 `7200`, S09 `8040`, S10 `9720` (@24fps).

---

## S01 Cold Open · 0–1200 · **High density (~18–22 cuts)**

| Role | Resources |
|------|-----------|
| V1 spine | Matatu plate + HDRI beats + Africa whip @720 (`setup_coldopen_matatu_africa.py`) |
| Canva / gen stills | `k01_*`, `pr_s01_matatu_traffic_gen`, `pr_s01_street_morning`, `pr_s01_phone_commute`, `pr_s01_nairobi_skyline_dawn`, `s1_matatu_silhouettes` |
| Stock video | `city_sunrise_aerial`, `city_walk_busy`, `phone_hands_type`, `skyline_clouds` |
| Stock pans / cuts | `cut_000`–`cut_005`, `cut_001_pan_nairobi_dawn`, `cut_003_pan_street_texture` |
| Roadmap | 0–15s flood dawn/street/matatu · mid phone-pocket flashes · @30s clear for Africa whip · close Silicon Savannah still |

---

## S02 Context 2007 · 1200–2280 · **High (~14–16 cuts)**

| Role | Resources |
|------|-----------|
| V1 spine | Kiosk plate `s2_kiosk_2007.png` · pan L→R |
| Canva / gen | `k02_feature_phone`, `k02_market_kiosk`, `pr_s02_feature_phone`, `pr_s02_market_stall`, `pr_s02_cash_hands` |
| Stock | `phone_hands_type`, `pan_market`, `pan_phone`, `city_walk_busy` |
| Cuts | `cut_007_pan_market`, `cut_008`/`009` phone, `cut_006` traffic night sparingly |
| Diagrams | `s2_mpesa_flow.svg`, `icon_phone` / `icon_agent` / `icon_recipient` |
| Roadmap | Year/M-PESA holds on V5 · flash feature-phone + cash + market between VO clauses · wipe to S03 |

---

## S03 Hubs · 2280–3360 · **High (~14–16 cuts)**

| Role | Resources |
|------|-----------|
| V1 | `s3_coworking.png` parallax |
| Canva / gen | `k03_coworking`, `k03_laptop_keys`, `pr_s03_coworking_desk`, `pr_s03_laptop_code`, `pr_s03_startup_whiteboard` |
| Stock | `keyboard_work`, `laptop_office`, `coding_screen`, `pan_laptop`, `pan_office_glass`, `network_nodes` |
| Cuts | `cut_010`–`cut_013`, `cut_031_coding_screen`, `cut_032_network_nodes`, `cut_038` |
| Diagrams | `s3_hub_cards.svg` |
| Roadmap | Card staggers on V5 · keyboard/laptop/whiteboard inserts under “iHub / Andela / NaiLab” |

---

## S04 Phone · 3360–3960 · **Very high (~10–12 cuts in 25s)**

| Role | Resources |
|------|-----------|
| V1 | `s4_phone_hand.png` push-in |
| Canva / gen | `k04_phone_scroll`, `pr_s04_phone_ui`, `pr_s04_thumbs_scroll`, `k01_phone_hands` |
| Stock | `phone_hands_type`, `pan_phone`, short `coding_screen` accents |
| Cuts | `cut_015`–`cut_017` |
| Roadmap | Thumb/UI flash every ~1.5–2s · Mobile-First TextStat protected last 8s |

---

## S05 Money · 3960–5040 · **Medium (protect chart) · ~8–10 cuts**

| Role | Resources |
|------|-----------|
| V1 | GN bar chart (priority readable) |
| Canva / gen | `k05_data_city`, `pr_s05_chart_desk`, `k13`/`k19` native datagrid |
| Stock | `digital_city_anim`, `data_center_lights`, `pan_data_city`, `pan_circuit` |
| Cuts | `cut_014`, `cut_018`, `cut_019`, `cut_033`, `cut_039` — **avoid** f180–840 chart/stat cores |
| Roadmap | Bookend only: open texture · mid abstract city · close morph setup · no overlays on `$984M` / `82%` |

---

## S06 Solar · 5040–6000 · **High (~12–14 cuts)**

| Role | Resources |
|------|-----------|
| V1 | Procedural rooftop solar |
| Canva / gen | `k06_solar_roof`, `k06_solar_field`, `pr_s06_solar_roof_gen`, `pr_s06_rural_power`, `k12`/`k18` native solar |
| Stock | `solar_roof_panels`, `wind_turbines`, `pan_solar`, `pan_power` |
| Cuts | `cut_020`–`cut_022`, `cut_034_wind_turbines` |
| Icons | `icon_solar.svg` |
| Roadmap | Company-tag VO → matching solar/rural stock flash · PAYG label hold |

---

## S07 Gap · 6000–7200 · **Medium-low (protect 97%) · ~8–10 cuts**

| Role | Resources |
|------|-----------|
| V1 | `s7_kenya_map.png` zoom-out |
| Canva / gen | `k07_kenya_landscape`, `pr_s07_dirt_road`, `pr_s07_kenya_savanna`, `k14`/`k20` native road |
| Stock | `pan_savanna`, `pan_rural_road`, `pan_city_morning` (Nairobi contrast) |
| Cuts | `cut_023`, `cut_024`, `cut_037` — **clear** during 97% slam (~f360–420 scene-local ≈ timeline 6360–6420) |
| Roadmap | Landscape/road texture around map · city markers on V5 · sparse during slam |

---

## S08 Secondary · 7200–8040 · **Medium-slow (~8–10 cuts @ 16–24f)**

| Role | Resources |
|------|-----------|
| V1 | Desaturated secondary-city plate |
| Canva / gen | `k08_town_street`, `pr_s08_town_street`, `pr_s08_quiet_shop`, `k15`/`k21` native market |
| Stock | `city_walk_busy` (desat grade in Resolve), `pan_street_texture`, quieter pans |
| Cuts | `cut_025`, longer holds |
| Roadmap | Contrast pace — fewer, longer inserts · Pre-seed gap TextStat |

---

## S09 Closer · 8040–9720 · **High (~16–18 cuts)**

| Role | Resources |
|------|-----------|
| V1 | `s9_dusk_skyline.png` |
| Canva / gen | `k09_nairobi_dusk`, `k09_skyline_modern`, `pr_s09_dusk_skyline`, `k11`/`k17` native skyline, `k16`/`k22` fiber |
| Stock | `sunset_skyline`, `skyline_clouds`, `pan_dusk_towers`, `pan_fiber_cables`, `pan_office_glass` |
| Cuts | `cut_026`–`cut_029`, `cut_035`, `cut_038` |
| Roadmap | Logo VO → matching skyline/glass/fiber flashes · Forecast TextStat · city strip |

---

## S10 End Card · 9720–10080 · **Minimal (2–3 accents max)**

| Role | Resources |
|------|-----------|
| V1 | `s10_africa_logo` / `pr_s10_africa_title` · `Series_Logo_AFRICA_3840` for 4K later |
| Canva / gen | `k10_abstract_dark` only if needed |
| Stock | Optional `cut_028_pan_gold_abstract` once under logo settle |
| Roadmap | Logo readable — almost no B-roll |

---

## Density scoreboard (target vs old)

| Scene | Old pace hits | Target kinetic+stock hits | Notes |
|-------|---------------|---------------------------|--------|
| S01 | ~4 | **18–22** | Includes stock dawn/walk/phone |
| S02 | ~3 | **14–16** | Market + phone stock |
| S03 | ~3 | **14–16** | Keyboard/laptop stock |
| S04 | ~2 | **10–12** | Very high ASL |
| S05 | ~1 | **8–10** | Bookends only |
| S06 | ~3 | **12–14** | Solar + turbines |
| S07 | ~2 | **8–10** | Clear 97% |
| S08 | ~2 | **8–10** | Longer ASL |
| S09 | ~3 | **16–18** | Dusk stock heavy |
| S10 | 0 | **2–3** | Logo first |
| **Total** | **~24** | **~110–130** | ~5× cut density |

---

## Agent checklist

1. Keep HQ Blender batch running (one GPU).  
2. When Resolve is free after plates: re-import Media Pool folders `Kinetic Graded` + stock overlays if missing.  
3. Run `python scripts/resolve_pace_kinetic_yb.py` with `AFRICA_NO_YELLOW_BALL=1`.  
4. Spot-check ASL on V3/V4 — flashes should feel Fern-dense, not TED-Ed sparse.  
5. Do **not** start 4K until `docs/PRE_4K_GATE.md` clears.
