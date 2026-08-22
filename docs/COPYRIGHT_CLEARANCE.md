# Copyright & License Clearance — Africa Season 1

**Purpose:** Keep Episode 01 picture/audio within rights we can defend.  
**Not legal advice** — confirm Canva plan tier and any brand-use questions with counsel before public release / monetization.

---

## Cleared for B-roll / plates (use these)

| Source | Where in project | License basis | Rules we follow |
|--------|------------------|---------------|-----------------|
| **Mixkit video** | `assets/stock/license_free/raw/*.mp4` · graded · `renders/paced_overlays/stock_cinematic/` | [Mixkit License](https://mixkit.co/license/) — free for commercial video | Do **not** redistribute files as a stock pack; OK inside finished episode; keep download URLs in `scripts/ingest_license_free_stock_cinematic.py` |
| **Unsplash stills** | `assets/stock/license_free/raw/pan_*.jpg` → pan cuts | [Unsplash License](https://unsplash.com/license) | Free commercial use; **do not** sell the photo itself as stock; credit photographers in `docs/ATTRIBUTIONS.md` (good practice / required by some partners) |
| **Poly Haven HDRI/PBR** | `assets/hdri/` · `assets/textures/polyhaven/` | CC0 | No attribution required; credit optional |
| **Blender originals** | `blend/africa_s1_master_v01.blend` animations, GN charts, procedural solar | Project-owned | Primary spine (V1) |
| **Project diagrams/icons** | `assets/diagrams/` · `assets/icons/` | Project-authored SVG | Prefer these over scraped brand art |
| **Canva exports you created** | `assets/canva/s*.png`, kinetic graded, logo v2 | Your Canva license (Free/Pro) + any Canva stock elements inside | Confirm account plan allows **commercial** use; do not use Canva assets whose license is “editorial only” |

---

## Use with care (not a free-for-all)

| Asset class | Risk | Policy |
|-------------|------|--------|
| **AI / generated stills** (`pr_s*_gen`, some `pr_s*`) | Model ToS + possible training-data disputes; may depict real-looking people/places | Prefer as **treated** B-roll under VO; no claim they are documentary photos of named people; keep generation prompts/logs if available |
| **Brand / product marks** (M-Pesa, Safaricom, Microsoft, Visa, UN, Netflix) | Trademark / brand guidelines — not “stock license” | Prefer **generic** labels / abstract silhouettes; do **not** paste official logo packs without permission; news/commentary may allow nominative use of **names in text** — still avoid fake endorsement lockups |
| **`s10_africa_logo_netflix_bak.png`** | Netflix trade dress / lookalike lockup | **Do not use in FINAL** — keep only as internal bak; end card = AFRICA wordmark only |
| **Telegram / third-party class videos** | Copyright of instructors / platforms | Reference learning only; do **not** cut into episode unless you have a written license |
| **Music / SFX** | Separate licenses | Use only stems you own or that are cleared in `assets/audio/`; no random YouTube rips |

---

## Banned from delivery timeline

1. Any media **not** listed under Cleared / Care with a known source.  
2. Soft/unprovenance “native” dumps if source unknown — prefer Mixkit, Unsplash, Canva-licensed, or Blender.  
3. Official third-party logos as hero graphics without written permission.  
4. Re-uploading Mixkit/Unsplash files to stock sites or asset marketplaces.  
5. Face-hero stock that implies a real person is “the founder” of a named company.

---

## Per-scene B-roll policy (copyright-safe)

For **≥15 unique cuts/scene**, fill from this order only:

1. Blender plate / in-scene animation (spine)  
2. Project Canva plates + **HQ** graded kinetics (`k01–k10`, `pr_s*` ≥~1.5MB)  
3. Mixkit graded / stock cinematic cuts (`manifest.json` → `"ok": true`)  
4. Unsplash-derived pan cuts (`pan_*` with Unsplash id in manifest)  
5. Poly Haven–lit Blender holds (not a substitute for illegal stills)

**Do not** pad to 15 with: Netflix bak, unknown Telegram stills, scraped Google Images, watermarked previews, or failed manifest rows (`"ok": false`).

---

## Attribution (ship with release)

Maintain `docs/ATTRIBUTIONS.md`:

- Mixkit clip list (titles/IDs from ingest URLs)  
- Unsplash photo IDs (already in `manifest.json` stills) + photographer names when fetched  
- Poly Haven asset names (optional)  
- “Additional motion graphics © [your production entity]”

YouTube/description: short “Stock: Mixkit & Unsplash (licensed); graphics original” is enough for most platforms; keep the full file for disputes.

---

## Agent / pipeline rules

1. `scripts/ingest_license_free_stock_cinematic.py` — **only** Mixkit + Unsplash (or other sources added with an explicit license URL in-script).  
2. `scripts/resolve_pace_kinetic_yb.py` — place only allowlisted stems (see `docs/CLEARANCE_ALLOWLIST.json`).  
3. Before FINAL: spot-check end card has **no** Netflix bak; S09 has **no** official MS/Visa/UN logo files.  
4. If a rightsholder objects: mute/remove that insert and re-export; do not argue from “everyone uses Mixkit.”

---

## Status (2026-08-13)

| Bucket | Clearance |
|--------|-----------|
| Mixkit videos in `license_free` | ✅ Intended under Mixkit License (verify each ID still free on mixkit.co before monetized release) |
| Unsplash pans with ids in manifest | ✅ Unsplash License + credit in ATTRIBUTIONS |
| Poly Haven | ✅ CC0 |
| Canva `s*` / kinetic HQ | ⚠️ User must confirm Canva commercial entitlement |
| `pr_s*` generated | ⚠️ Treat as original-derived; no photojournalism claims |
| Music / SFX beds | ✅ Project-generated procedural (`assets/audio/generate_*.py`) — not third-party rips |
| Netflix bak / Safaricom mark art | 🚫 Quarantined under `assets/_quarantine_copyright/` (2026-08-13) |
| Telegram class media | 🚫 Not for episode picture |

*Update this file when new stock is ingested.*
