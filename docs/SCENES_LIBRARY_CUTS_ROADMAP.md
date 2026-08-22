# Episode 01 — Per-Scene Asset Library · Cuts/Transitions · Roadmap to Completion

**Authoritative for this pass** (supersedes sparse lists in older pace notes).  
**Live state:** `PRODUCTION_STATUS.md` · **Clearance:** `docs/COPYRIGHT_CLEARANCE.md` · **Agent rules:** `.cursor/rules/africa-s1-agent-rules.mdc`  
**Stamp:** 2026-08-13 09:45 · S01 HQ ~f403/1200 (do not restart) · **library ≥15/scene met** via Mixkit + still variants  
**Hard edit rule:** every viewer-facing shot / B-roll cut **≤ 5.0 s** (≤120f @24). Preferred **0.4–2.0 s**. See `docs/DYNAMIC_EDIT_TRANSITIONS.md` + refs [TED-Ed rail](https://youtu.be/2A1IEBFt6Xg) · [xV82vkJ5Pjw](https://youtu.be/xV82vkJ5Pjw) · [CbUjuwhQPKs](https://youtu.be/CbUjuwhQPKs).

### Global cut grammar

| Type | Duration @24fps | Use |
|------|-----------------|-----|
| Kinetic still / stock insert | **10–48f** (0.4–2.0s); **hard max 120f / 5.0s** | V3/V4 Normal, opacity **85–92%**, full-frame 16:9 |
| Detail flash | **10–12f** | Phone/UI |
| Quiet insert (S08) | **24–48f** (still ≤5s) | Contrast |
| Stat protect | hold ≤ **5s** then cut | `$984M`, `82%`, `97%` |
| Scene transition | 0–15f whip/wipe/morph/fade | see `docs/DYNAMIC_EDIT_TRANSITIONS.md` |

**V2:** empty (YB waived). **Excluded:** `*netflix_bak*`, soft natives `k12–k15`, `k18–k21`.  
**Assets:** Mixkit downloads + graded cuts + `gen_sXX_*` still variants filled gaps (Coverr API 401 — skipped). Gemini credits depleted; Qwen CPU used for prompt pack only.

---

## S01 — Cold Open · timeline 0–1200 · 50s

**Spine (V1):** matatu plate + HDRI plate switches + Africa whip @ **f720**  
**OUT → S02:** hard **cut** on “Silicon Savannah”

### Asset library (15+ unique picture sources)

| # | Asset | Kind |
|---|--------|------|
| 1 | Blender `01_ColdOpen` plate | animation |
| 2 | `S01_Africa_Slide` / `pr_s10_africa_title` | animation/still @30s |
| 3 | HDRI aarfontein ↔ kloofendal beats | env transition |
| 4 | `k01_matatu_street_1080.png` | still |
| 5 | `k01_nairobi_dawn_1080.png` | still |
| 6 | `k01_phone_hands_1080.png` | still |
| 7 | `pr_s01_matatu_traffic_gen_1080.png` | still |
| 8 | `pr_s01_street_morning_1080.png` | still |
| 9 | `pr_s01_phone_commute_1080.png` | still |
| 10 | `pr_s01_nairobi_skyline_dawn_1080.png` | still |
| 11 | `cut_000_city_sunrise_aerial_16f` | stock |
| 12 | `cut_001_pan_nairobi_dawn_14f` | stock |
| 13 | `cut_002_city_walk_busy_14f` | stock |
| 14 | `cut_003_pan_street_texture_12f` | stock |
| 15 | `cut_004_phone_hands_type_12f` | stock |
| 16 | `cut_005_pan_phone_12f` | stock |
| 17 | `cut_029_skyline_clouds_12f` | stock |
| 18 | `k11_native_skyline_1080.png` | still (OK tier) |

### Cuts & transitions (highlight)

| Time | Action |
|------|--------|
| 0–15s | Dense V3/V4: dawn aerial → street → matatu stills (hard cuts) |
| 15–28s | Phone-pocket flashes (hard cut) |
| **28–30s** | **Clear V3/V4** → Africa **whip-in** (V1, ~10f linear) |
| 30–48s | Sparse skyline/clouds under Africa settle |
| 48–50s | TextStat Silicon Savannah → **CUT** to S02 |

**TED-Ed 30s overlay (V3):** `renders/paced_overlays/s01_teded_open_30s.mp4` — 10 infographic beats, 0–720f. Spec: `docs/S01_TEDED_30S_OPEN.md`. Clear at Africa whip.

**ETA:** HQ S01 still in progress · **do not restart**

---

## S02 — Context 2007 · 1200–2280 · 45s

**Spine:** kiosk plate + pan L→R · **OUT:** **slide_wipe** right (~8f) → S03

| # | Asset | Kind |
|---|--------|------|
| 1 | Blender `02_Context2007` | animation |
| 2 | `s2_kiosk_2007.png` | Canva hero |
| 3 | `k02_feature_phone_1080.png` | still |
| 4 | `k02_market_kiosk_1080.png` | still |
| 5 | `pr_s02_feature_phone_1080.png` | still |
| 6 | `pr_s02_market_stall_1080.png` | still |
| 7 | `pr_s02_cash_hands_1080.png` | still |
| 8 | `s2_mpesa_flow.svg` + icons | diagram |
| 9 | `cut_007_pan_market_14f` | stock |
| 10 | `cut_008_phone_hands_type_12f` | stock |
| 11 | `cut_009_pan_phone_12f` | stock |
| 12 | `cut_010_keyboard_work_14f` | stock |
| 13 | `cut_006_city_traffic_night_14f` | stock (sparse) |
| 14 | `phone_hands_type` graded MP4 | stock |
| 15 | TextStat `2007` / `M-PESA` | V5 |

**Cuts:** flash market/phone/cash on VO nouns · protect year/M-PESA TextStat · wipe out.  
**ETA:** after S01 · ~**1.4 h** @4.5s/f (1080f)

---

## S03 — Hubs · 2280–3360 · 45s

**Spine:** coworking parallax · **OUT:** **color_hold** cut → S04

| # | Asset |
|---|--------|
| 1–2 | Blender `03` · `s3_coworking.png` |
| 3–5 | `k03_coworking` · `k03_laptop_keys` · `pr_s03_coworking_desk` |
| 6–7 | `pr_s03_laptop_code` · `pr_s03_startup_whiteboard` |
| 8 | `s3_hub_cards.svg` |
| 9–15 | `cut_011` laptop · `cut_012` pan_laptop · `cut_013` keyboard · `cut_031` coding · `cut_032` network · `cut_038` office_glass · `network_nodes` |

**Cuts:** stagger hub cards on V5 · keyboard/laptop hard cuts under names.  
**ETA:** ~**1.4 h**

---

## S04 — Phone · 3360–3960 · 25s

**Spine:** phone push-in · **OUT:** **cut** → DarkData S05

| # | Asset |
|---|--------|
| 1–2 | Blender `04` · `s4_phone_hand.png` |
| 3–5 | `k04_phone_scroll` · `pr_s04_phone_ui` · `pr_s04_thumbs_scroll` |
| 6 | `k01_phone_hands_1080` (reuse OK across scenes) |
| 7–15 | `cut_015`–`017` phone/laptop · Mixkit `phone_hands_type` · `pan_phone` · coding accents · TextStat Mobile-First |

**Cuts:** highest ASL — new frame every ~1.5–2s · hard cuts.  
**ETA:** ~**0.8 h** (600f)

---

## S05 — Money · 3960–5040 · 45s

**Spine:** GN bars · **OUT:** **morph** (~15f) bar→solar → S06  
**Protect:** chart/`$984M`/`82%` cores — V3/V4 **bookends only**

| # | Asset |
|---|--------|
| 1 | Blender chart animation |
| 2–3 | `k05_data_city` · `pr_s05_chart_desk` |
| 4–5 | `k16` / `k22` fiber (HQ) |
| 6–15 | `cut_014` · `018` · `019` digital_city · `033` datacenter · `039` circuit · `digital_city_anim` · `data_center_lights` · `pan_data_city` · `pan_circuit` · TextStat `$984M`/`82%` |

**Cuts:** open texture → clear for stats → close abstract city → morph.  
**ETA:** ~**1.4 h**

---

## S06 — Solar · 5040–6000 · 40s

**Spine:** procedural roof · **OUT:** **cut** → S07

| # | Asset |
|---|--------|
| 1 | Blender solar |
| 2–5 | `k06_solar_roof` · `k06_solar_field` · `pr_s06_solar_roof_gen` · `pr_s06_rural_power` |
| 6 | `icon_solar.svg` |
| 7–15 | `cut_020`–`022` · `cut_034` turbines · Mixkit solar/wind · `pan_power` · company TextStat strip |

**Cuts:** hard cut per company beat.  
**ETA:** ~**1.2 h** (960f)

---

## S07 — Gap · 6000–7200 · 50s

**Spine:** map zoom · **OUT:** **fade** 8f → S08  
**Protect:** `97%` slam (~timeline 6360–6420)

| # | Asset |
|---|--------|
| 1–2 | Blender map · `s7_kenya_map.png` |
| 3–5 | `k07_kenya_landscape` · `pr_s07_dirt_road` · `pr_s07_kenya_savanna` |
| 6 | `icon_map_pin.svg` |
| 7–15 | `cut_023` savanna · `024` city_morning · `037` rural_road · Mixkit/Unsplash pans · TextStat `97%` · city labels |

**Cuts:** landscape around map · **clear** during slam · fade out.  
**ETA:** ~**1.5 h** (1200f)

---

## S08 — Secondary · 7200–8040 · 35s

**Spine:** desat street · **OUT:** **cut** → S09  
**ASL:** slower **16–24f**

| # | Asset |
|---|--------|
| 1 | Blender `08` |
| 2–4 | `k08_town_street` · `pr_s08_town_street` · `pr_s08_quiet_shop` |
| 5–15 | `cut_025` walk · street pans · soft market (HQ only) · Pre-seed TextStat · ambient holds |

**ETA:** ~**1.1 h** (840f)

---

## S09 — Closer · 8040–9720 · 70s

**Spine:** dusk skyline · **OUT:** **fade** 12f → S10  
**No official MS/Visa/UN logo files** — TextStat names only

| # | Asset |
|---|--------|
| 1–2 | Blender `09` · `s9_dusk_skyline.png` |
| 3–6 | `k09_nairobi_dusk` · `k09_skyline_modern` · `pr_s09_dusk_skyline` · `k11`/`k17` skyline |
| 7–8 | `k16`/`k22` fiber |
| 9–18 | `cut_026`–`029` · `035` fiber · `038` glass · sunset/skyline Mixkit · Forecast TextStat |

**ETA:** ~**2.1 h** (1680f) — longest remaining plate after S01

---

## S10 — End Card · 9720–10080 · 15s

**Spine:** AFRICA wordmark (v2 / title) · **OUT:** fade to black  
**Ban:** `s10_africa_logo_netflix_bak.png`

| # | Asset |
|---|--------|
| 1 | Blender `10_EndCard` |
| 2–3 | `s10_africa_logo.png` / `s10_africa_logo_v2.png` |
| 4 | `pr_s10_africa_title.png` (hq) |
| 5 | `Series_Logo_AFRICA_3840.png` (4K later only) |
| 6 | `k10_abstract_dark_1080.png` |
| 7–15 | Short accents only: `cut_028` if Unsplash pan existed — **skip if ok:false** · fiber abstracts · gold dust from project grade · Season 1 TextStat · otherwise **repeat Blender camera drift angles** as synthetic B-roll (project-owned) |

**Cuts:** max **2–3** flashes then logo hold.  
**ETA:** ~**0.5 h** (360f)

---

## Roadmap to completion (execute in order)

| Step | Action | Depends | Est. |
|------|--------|---------|------|
| 1 | **Let S01 finish** — verify ~50s playable MP4 | running | ~1.7h |
| 2 | Auto-continue **02–10** via `_hq_s01_full_then_remaining.cmd` second stage | S01 done | ~11h |
| 3 | Verify each clip duration vs `EXPECTED_SEC` in `render_scenes_mp4.py` | files | 15m |
| 4 | `finish_after_hq.ps1` (assemble + Fairlight; YB skip) | 10/10 | 30m |
| 5 | Resolve open: run densified `resolve_pace_kinetic_yb.py` (this library) | Resolve | 30–60m |
| 6 | Spot-check cuts/transitions vs table above | eyes | 30m |
| 7 | Close PRE_4K #2–7 or waive | creative | — |
| 8 | 4K only after gate | HOLD | — |

### Gaps (honest)

| Gap | Impact | Mitigate |
|-----|--------|----------|
| Some scenes &lt;15 *unique* HQ stills on disk | Pad with Mixkit/Unsplash cuts + Blender alt holds | Listed stock cuts above |
| Soft natives excluded | Fewer “native” fillers | Do not use |
| Gemini/Cursor gen credits | Cannot mint new stills/video now | Restore AI Studio billing, then fill |
| Dense pace script previously ~24 hits | Under-cut | Update script to this library (next execute step) |

---

*Update this file when clips verify complete; sync `PRODUCTION_STATUS.md` in the same pass.*
