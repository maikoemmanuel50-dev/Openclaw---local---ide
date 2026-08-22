# Episode 01 — Completion Breakdown  
## Roadmap · Setting · Resources · Deliverables · Execution

**Episode:** Silicon Savannah · ~7:00 @ 24fps · 10,080 frames  
**Master blend:** `blend/africa_s1_master_v01.blend` (Blender **5.1.2** only)  
**VO spine:** `assets/audio/vo/episode_01_vo.wav`  
**This pass overrides:** Yellow ball / V2 **OFF** · S01 matatu+HDRI+Africa@30s · dense Canva + generated + **stock** on V3/V4  
**Companion cut map:** `docs/SCENES_LIBRARY_CUTS_ROADMAP.md` (authoritative library + transitions + ETAs)  
**Legacy companions:** `docs/SCENE_RESOURCE_CUT_ROADMAP.md` · this file  
**Gate:** `docs/PRE_4K_GATE.md` — 4K HOLD until #2–7 clear  

### Global execution (after all 10 HQ plates)

1. `wait_hq_assemble.ps1` → `finish_after_hq.ps1`  
2. Normalize → `renders/built_clips/` · assemble 7min / MASTER / FINAL  
3. Resolve **Episode 01 - Assembly**: V1 relink · V3/V4 dense kinetic+stock · V5 TextStat · A1–A5 Fairlight (`AFRICA_NO_YELLOW_BALL=1`)  
4. Spot-check · PRE_4K #2–7 · then optional 4K via `render_scenes_4k.py` (full presets)

### Track layout

| Track | Content |
|-------|---------|
| V1 | Blender scene plates |
| V2 | Empty this pass (YB waived) |
| V3 | Kinetic stills + stock cuts (primary) |
| V4 | Alternate kinetic + stock |
| V5 | TextStat / labels |
| A1–A5 | VO · ducked music · SFX |

---

## S01 — Cold Open

| | |
|--|--|
| **Duration** | 50s · 1–1200 · timeline 0–1200 |
| **Setting** | Nairobi dawn. Full-bleed **matatu** plate only; HDRI plate switches (dusk↔sky); Africa title **whip-in at 30s (f720)** then settle. No YB. DOF/bloom off for sharpness. |
| **Roadmap** | 0–15s high-density dawn/street/matatu stock+stills → mid phone-pocket flashes → **clear V3/V4 at Africa whip** → close on Silicon Savannah → cut to S02 |
| **Resources — Blender** | `Background_Plane` + `S01_Africa_Slide` · HDRIs `aarfontein_dusk_2k` / `kloofendal_48d_*` · `setup_coldopen_matatu_africa.py` |
| **Resources — Canva / gen** | `k01_matatu_street_1080`, `k01_nairobi_dawn_1080`, `k01_phone_hands_1080`, `pr_s01_matatu_traffic_gen_1080`, `pr_s01_street_morning_1080`, `pr_s01_phone_commute_1080`, `pr_s01_nairobi_skyline_dawn_1080`, `s1_matatu_silhouettes.png` |
| **Resources — Stock** | Graded: `city_sunrise_aerial`, `city_walk_busy`, `phone_hands_type`, `skyline_clouds` · Cuts: `cut_000`–`cut_005`, `cut_001_pan_nairobi_dawn`, `cut_003_pan_street_texture` |
| **Resources — Audio** | VO · `matatu_horn` · city morning ambient · dawn pad |
| **Cut target** | **18–22** V3/V4 hits (10–14f) |
| **Deliverables** | `renders/video_clips/01_ColdOpen.mp4` · Resolve TextStat: Nairobi / Silicon Savannah · Africa readable after f720 |
| **Eventual execution** | HQ @ **128 / full RT** (`AFRICA_ONLY_SCENES=01_ColdOpen`) → then remaining batch · finish pace skips YB |

---

## S02 — Context 2007

| | |
|--|--|
| **Duration** | 45s · 1080f · timeline 1200–2280 |
| **Setting** | Warm retro dawn chapter. M-Pesa origin: kiosk, feature phones, cash→SMS money. Camera pan L→R. |
| **Roadmap** | Year slam → M-PESA card → Phone→Agent→Recipient flashes (still+stock) → blueprint beat → slide-wipe to S03 |
| **Resources — Blender** | Scene `02_Context2007` · kiosk plate · pan camera |
| **Resources — Canva / gen** | `s2_kiosk_2007.png`, `k02_feature_phone_1080`, `k02_market_kiosk_1080`, `pr_s02_feature_phone_1080`, `pr_s02_market_stall_1080`, `pr_s02_cash_hands_1080` |
| **Resources — Stock** | `phone_hands_type`, `pan_market` / `cut_007`, `pan_phone` / `cut_008–009`, light `city_walk_busy` |
| **Resources — Diagrams** | `s2_mpesa_flow.svg`, `icon_phone`, `icon_agent`, `icon_recipient` |
| **Cut target** | **14–16** hits |
| **Deliverables** | `02_Context2007.mp4` · TextStat: `2007`, `M-PESA`, flow labels |
| **Eventual execution** | HQ @ **64 / half RT**, no YB · V1 place · dense V3/V4 · Fairlight brand/keypad SFX |

---

## S03 — Beat 1: Hubs

| | |
|--|--|
| **Duration** | 45s · 1080f · timeline 2280–3360 |
| **Setting** | Daylight co-working. iHub / Andela / NaiLab enumeration. Parallax drift. |
| **Roadmap** | Interior establish → stagger hub cards on VO nouns → keyboard/laptop/whiteboard stock storm → color-hold → S04 |
| **Resources — Blender** | `03_Beat1_Hubs` · `s3_coworking.png` |
| **Resources — Canva / gen** | `k03_coworking_1080`, `k03_laptop_keys_1080`, `pr_s03_coworking_desk_1080`, `pr_s03_laptop_code_1080`, `pr_s03_startup_whiteboard_1080` |
| **Resources — Stock** | `keyboard_work`, `laptop_office`, `coding_screen`, `pan_laptop`, `pan_office_glass`, `network_nodes` · cuts `cut_010`–`013`, `cut_031`, `cut_032`, `cut_038` |
| **Resources — Diagrams** | `s3_hub_cards.svg` |
| **Cut target** | **14–16** hits |
| **Deliverables** | `03_Beat1_Hubs.mp4` · TextStat: iHub 2010 / Andela / NaiLab |
| **Eventual execution** | Same HQ path · daylight lofi + coworking ambient on finish |

---

## S04 — Beat 1: Phone

| | |
|--|--|
| **Duration** | 25s · 600f · timeline 3360–3960 |
| **Setting** | Tight mobile-first close-up. Hand + phone UI energy. |
| **Roadmap** | Very high ASL: thumb/UI/stock phone every ~1.5–2s → Mobile-First hold → cut to DarkData |
| **Resources — Blender** | `04_Beat1_Phone` · `s4_phone_hand.png` push-in |
| **Resources — Canva / gen** | `k04_phone_scroll_1080`, `pr_s04_phone_ui_1080`, `pr_s04_thumbs_scroll_1080`, `k01_phone_hands_1080` |
| **Resources — Stock** | `phone_hands_type`, `pan_phone` · cuts `cut_015`–`017` |
| **Cut target** | **10–12** hits (short scene) |
| **Deliverables** | `04_Beat1_Phone.mp4` · TextStat: `Mobile-First` |
| **Eventual execution** | Fastest mid-episode plate · ui_swipe SFX |

---

## S05 — Beat 2: Money (priority)

| | |
|--|--|
| **Duration** | 45s · 1080f · timeline 3960–5040 |
| **Setting** | DarkData charcoal. Geometry Nodes bars · `$984M` · sector mix · `82%`. |
| **Roadmap** | Bookend B-roll only → chart readable core → `$984M` / bars / `82%` protected → morph setup to solar |
| **Resources — Blender** | GN bar chart in `05_Beat2_Money` |
| **Resources — Canva / gen** | `k05_data_city_1080`, `pr_s05_chart_desk_1080`, `k13`/`k19` native datagrid |
| **Resources — Stock** | `digital_city_anim`, `data_center_lights`, `pan_data_city`, `pan_circuit` · cuts `cut_014`, `018`, `019`, `033`, `039` |
| **Cut target** | **8–10** hits · **no** overlays on counter/82% windows |
| **Deliverables** | `05_Beat2_Money.mp4` · TextStat backup `$984M` / `82%` / sector labels |
| **Eventual execution** | Protect V5 · darkdata bed + chart SFX · morph into S06 |

---

## S06 — Beat 2: Solar

| | |
|--|--|
| **Duration** | 40s · 960f · timeline 5040–6000 |
| **Setting** | DarkData suburb rooftop. PAYG solar (d.light / Sun King / M-KOPA / BURN). |
| **Roadmap** | Panel reveal → company-tag VO matched to solar/rural stock → PAYG label → cut to Gap |
| **Resources — Blender** | Procedural panels `06_Beat2_Solar` |
| **Resources — Canva / gen** | `k06_solar_roof_1080`, `k06_solar_field_1080`, `pr_s06_solar_roof_gen_1080`, `pr_s06_rural_power_1080`, `k12`/`k18` native solar |
| **Resources — Stock** | `solar_roof_panels`, `wind_turbines`, `pan_solar`, `pan_power` · cuts `cut_020`–`022`, `cut_034` |
| **Resources — Icons** | `icon_solar.svg` |
| **Cut target** | **12–14** hits |
| **Deliverables** | `06_Beat2_Solar.mp4` · TextStat: Pay-As-You-Go Solar + company strip |
| **Eventual execution** | HQ remaining path · solar_hum ambient |

---

## S07 — Beat 3: Gap (priority)

| | |
|--|--|
| **Duration** | 50s · 1200f · timeline 6000–7200 |
| **Setting** | CoolTension. Kenya map zoom-out · Nairobi concentration · secondary cities dim. |
| **Roadmap** | Nairobi glow → zoom → **clear for 97% slam** → landscape/road stock around edges → city blinks → fade S08 |
| **Resources — Blender** | Map zoom `07_Beat3_Gap` · `s7_kenya_map.png` |
| **Resources — Canva / gen** | `k07_kenya_landscape_1080`, `pr_s07_dirt_road_1080`, `pr_s07_kenya_savanna_1080`, `k14`/`k20` native road |
| **Resources — Stock** | `pan_savanna`, `pan_rural_road`, `pan_city_morning` · cuts `cut_023`, `024`, `037` |
| **Resources — Icons** | `icon_map_pin.svg` |
| **Cut target** | **8–10** hits · clear ~timeline 6360–6420 (97%) |
| **Deliverables** | `07_Beat3_Gap.mp4` · TextStat: `97%` · city names |
| **Eventual execution** | Music dip before slam · cooltension drone |

---

## S08 — Beat 3: Secondary City

| | |
|--|--|
| **Duration** | 35s · 840f · timeline 7200–8040 |
| **Setting** | CoolTension quiet contrast. Desaturated street / pre-seed gap. |
| **Roadmap** | Longer ASL · fewer inserts · Pre-seed gap label → cut to dusk |
| **Resources — Blender** | Secondary-city plate `08_Beat3_SecondaryCity` |
| **Resources — Canva / gen** | `k08_town_street_1080`, `pr_s08_town_street_1080`, `pr_s08_quiet_shop_1080`, `k15`/`k21` native market |
| **Resources — Stock** | Soft `city_walk_busy`, `pan_street_texture` · `cut_025` (longer holds 16–24f) |
| **Cut target** | **8–10** hits @ slower pace |
| **Deliverables** | `08_Beat3_SecondaryCity.mp4` · TextStat: `Pre-seed gap` |
| **Eventual execution** | Sparse ambient · contrast edit vs S07/S09 |

---

## S09 — Closer (priority)

| | |
|--|--|
| **Duration** | 70s · 1680f · timeline 8040–9720 |
| **Setting** | HopefulDusk skyline. Institutions as forecast (Microsoft / Visa / UN) · Lagos·Kigali·Accra strip. |
| **Roadmap** | Logo VO → skyline/glass/fiber stock flashes → Forecast slam → city strip → fade to end card |
| **Resources — Blender** | `09_Closer` · `s9_dusk_skyline.png` |
| **Resources — Canva / gen** | `k09_nairobi_dusk_1080`, `k09_skyline_modern_1080`, `pr_s09_dusk_skyline_1080`, `k11`/`k17` skyline, `k16`/`k22` fiber |
| **Resources — Stock** | `sunset_skyline`, `skyline_clouds`, `pan_dusk_towers`, `pan_fiber_cables`, `pan_office_glass` · cuts `cut_026`–`029`, `035`, `038` |
| **Cut target** | **16–18** hits |
| **Deliverables** | `09_Closer.mp4` · TextStat: `Forecast` · city strip |
| **Eventual execution** | Longest remaining GPU plate · hopeful dusk swell |

---

## S10 — End Card

| | |
|--|--|
| **Duration** | 15s · 360f · timeline 9720–10080 |
| **Setting** | HopefulDusk. **AFRICA** wordmark only · Season 1 · fade to black. |
| **Roadmap** | Logo drift → Season 1 fade-in → optional one gold abstract accent → black |
| **Resources — Blender** | `10_EndCard` |
| **Resources — Canva / gen** | `s10_africa_logo.png` / v2 · `pr_s10_africa_title.png` · `upscales/Series_Logo_AFRICA_3840.png` (4K later) · optional `k10_abstract_dark_1080` |
| **Resources — Stock** | Optional once: `cut_028_pan_gold_abstract` |
| **Cut target** | **2–3** max |
| **Deliverables** | `10_EndCard.mp4` · must refresh Resolve V1 end card |
| **Eventual execution** | Short last plate → assemble → Fairlight resolve → FINAL |

---

## Density scoreboard (completion target)

| Scene | V3/V4 hits | Notes |
|-------|------------|--------|
| S01 | 18–22 | Stock dawn/walk/phone + Africa clear |
| S02 | 14–16 | Market + phone stock |
| S03 | 14–16 | Keyboard/laptop stock |
| S04 | 10–12 | Highest ASL |
| S05 | 8–10 | Bookends; protect stats |
| S06 | 12–14 | Solar + turbines |
| S07 | 8–10 | Clear 97% |
| S08 | 8–10 | Longer ASL |
| S09 | 16–18 | Dusk stock heavy |
| S10 | 2–3 | Logo first |
| **Total** | **~110–130** | vs prior ~24 |

---

## Completion checklist (stamp when true)

- [ ] All 10 `renders/video_clips/*.mp4` duration-complete  
- [ ] `built_clips` mirrored · 7min / MASTER / FINAL assembled  
- [ ] Resolve V1 relinked · V3/V4 dense kinetic **+ stock** placed · V2 empty  
- [ ] Fairlight A1–A5 + grade spot-check  
- [ ] PRE_4K #2–7 cleared or waived before 4K  

*Document generated for post-batch handoff. Update checkboxes when `finish_after_hq.ps1` completes.*
