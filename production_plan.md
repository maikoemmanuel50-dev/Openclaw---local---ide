# Episode 1 Production Plan — "Silicon Savannah"
**Series:** AFRICA — Season 1  
**Topic:** The Kenyan startup scene  
**Target runtime:** ~7 minutes (Optimized from 9 minutes to eliminate excess visual holds and match narration word count)  
**Companion script:** [episode_1_script.md](file:///C:/Users/HP/OneDrive/The%20Vault/Africa%20Season%201/episode_1_script.md)

---

## 1. Episode Brief
*   **Angle:** Kenya's "Silicon Savannah" reputation has a solid origin point (M-Pesa, 2007) and substantial momentum (raising nearly $1B in 2025, global tech centers setting up locally). However, it faces critical, under-covered structural gaps: the concentration of ~97% of startups in Nairobi and a persistent early-stage pre-seed funding shortage. The episode builds an honest narrative by analyzing the complications before earning its optimistic, forward-looking conclusion.
*   **Throughline:** Explores Kenya's tech ecosystem as the pilot story of a broader series detailing localized innovation across the African continent.

---

## 2. Research Grounding & Data Accuracy
*   **M-Pesa Launch:** Introduced by Safaricom in 2007; bypasses physical banks by turning airtime agents into cash-in/cash-out points.
*   **Innovation Ecosystem:** iHub founded in 2010; followed by talent builders Andela and NaiLab.
*   **Mobile-First Market:** High mobile internet penetration (overwhelmingly phone-first traffic) dictates app design.
*   **2025 Funding Totals:** Kenyan startups raised **$984 million** in 2025 (representing roughly a third of all startup funding in Africa).
*   **Funding Concentration (Sectors):** While fintech remains active by volume of launches, **82% of total capital** in 2025 was concentrated in energy and climate-tech (mega debt/equity rounds led by d.light, Sun King, M-KOPA, BURN, and PowerGen).
*   **Funding Concentration (Geography):** Nairobi hosts **~97%** of registered/funded startups, leaving secondary hubs (Mombasa, Kisumu, Eldoret, Nakuru) heavily underserved.
*   **Global Presence:** Nairobi hosts Microsoft’s African Development Centre and Visa's Innovation Studio. By late 2026, three UN agencies (UNICEF, UN Women, UNFPA) will relocate global operational units to Nairobi.

---

## 3. Scene-by-Scene Visual & Camera Plan

| # | Script Section | Visual Composition | Camera Preset | Key Assets Needed | Color & Mood |
|---|---|---|---|---|---|
| **1** | Cold Open | Dawn Nairobi skyline; silhouette layers of motorbikes and matatus. | Push-In | Nairobi skyline vectors, matatu/bike layers | Warm orange, dust-purple dawn |
| **2** | Context (2007) | 2007 phone accessories kiosk, Nokia-era phone handsets. | Pan (Left to Right) | Kiosk illustration, handset assets | Warm retro yellow, high contrast |
| **3** | Beat 1 (Hubs) | Co-working space interior; rows of desks, laptops, whiteboards. | Parallax Drift | Desk layer, screen layer, plant layer | Crisp daylight, bright whites & greens |
| **4** | Beat 1 (cont.) | Extreme close-up of phone-in-hand showing custom UI. | Push-In | Hand + phone vector, app interface mock | Warm focus, shallow depth of field |
| **5** | Beat 2 (Money) | Dark-mode 3D bar chart growing dynamically (Fintech, Climate/Energy). | Push-In | Geometry nodes setup, sector data | Sleek dark mode, neon green highlights |
| **6** | Beat 2 (cont.) | Rooftop solar panel setup overlooking leafy suburbs. | Parallax Drift | Solar panel layer, house vector, suburb bg | Bright midday sun, golden hour glare |
| **7** | Beat 3 (Gap) | 2.5D map of Kenya; Nairobi pulsing with intense neon glow. | Custom Zoom-Out | Kenya map SVG, glow shader | Cool slate gray, sharp high-contrast neon |
| **8** | Beat 3 (cont.) | Quieter secondary city street (Mombasa/Kisumu style). | Parallax Drift | Secondary city vector, dusty street, shop | Natural, slightly desaturated tones |
| **9** | Closer | Modern skyline transition showing global tech/UN hubs. | Push-In | Skyline modern variant, stylized logo vectors | Corporate dark blue, gold dusk tones |
| **10**| End Card | "AFRICA" series logo on textured dark background. | Subtle Drift | High-res logo vector, noise texture | Deep charcoal, gold metallic logo |

---

## 4. Reusable Template Checklist
To ensure future episodes (Lagos, Kigali, Accra) are completed efficiently, the following assets must be built as flexible templates in Episode 1:
1.  **Blender Master Camera Rig:** Pre-configured camera files with keyframed switchable presets (`Push-In`, `Pan`, `Parallax Drift`).
2.  **Parallax Scene Template:** A 3D Blender file containing pre-spaced planes (Foreground, Midground, Background) linked to depth-of-field nodes.
3.  **Data Viz Engine:** A Geometry Nodes setup that automatically scales, labels, and animates bar charts based on input numbers.
4.  **Color LUTs:** Standardized LUTs for documentary grading (Dawn, Day, Dusk, Dark Mode Chart) to keep lighting styles consistent.
5.  **Typography & Captions:** Reusable DaVinci Resolve text style (font, size, shadow, animation) for auto-captions and title cards.

---

## 5. Production Steps

### Phase A: Blender Setup (Automated via Scripting)
1.  Create a template Blender scene with standard camera configurations and lighting rigs.
2.  Execute batch generation of 10 scenes, naming them sequentially (`Scene_01_ColdOpen` to `Scene_10_EndCard`).
3.  Import SVG vectors into individual Z-depth layers.
4.  Configure the Geometry Nodes bar chart in `Scene_05` with 2025 sector data ($984M total).

### Phase B: Creative Fine-Tuning (Manual)
1.  **Camera Customization:** Animate the custom zoom-out on `Scene_07` (Map) to start tightly on Nairobi's glow and pull back rapidly, pausing to highlight the contrast between the capital and regional areas.
2.  **Lighting & Flare:** Add a sun-glare pass to `Scene_06` (Solar) and a soft dusk-glow to `Scene_09` (Closer) to enhance visual premium quality.
3.  **Visual Asset Check:** Stylize all global brand references in `Scene_09` (Microsoft/Visa/UN) to avoid trademark issues while remaining recognizable.

### Phase C: Resolve & Fairlight Integration (Editing)
1.  **Audio Spine:** Lay down the voiceover track first. Cut the animation scenes to the voiceover, never the other way around.
2.  **Sound Design Layering:** Add ambient background sound effects (street bustle, keypad clicks, chart risers) at `-18dB` to `-24dB`.
3.  **Music Track Integration:** Keep the music bed ducked under the voiceover at `-20dB` to `-26dB`, rising up to `-10dB` during transitions.
4.  **Color Conform:** Apply the project-wide grading LUT across all 10 imported clips to tie the visual style together.

---

## 6. Phase D — TED-Ed Style Retrofit

**Reference:** [TED-Ed high-speed rail explainer](https://youtu.be/2A1IEBFt6Xg)  
**Style bible:** [docs/teded_style_bible.md](docs/teded_style_bible.md)  
**Scene spec:** [docs/teded_scene_spec_ep01.md](docs/teded_scene_spec_ep01.md)  
**Audio map:** [docs/audio_design_map.yaml](docs/audio_design_map.yaml)

### D1 — Documentation ✅
- TED-Ed style bible (palette chapters, typography, motion, transitions, audio rules)
- Full 10-scene revised spec with element animations and asset list
- Audio design map with 5 chapter beds, 16 SFX cues, Fairlight bus layout

### D2 — Asset Creation ✅
- SVG diagrams: M-Pesa flow, hub cards, transaction paths, split comparison template
- Icon set: phone, agent, recipient, solar, map pin
- 5 music beds + 16 SFX files in `assets/audio/`
- Placeholder VO (390s silence — replace with recorded narration)

### D3 — Blender Element Animation ✅
- `setup_teded_elements.py` adds animated text labels to all 10 scenes
- Priority scenes: S05 ($984M, 82%), S07 (97%), S02 (M-PESA), S03 (hub cards), S09 (Forecast)
- Saved to `blend/africa_s1_master_v01.blend`

### D4 — Assembly Pipeline ✅
- `assemble_final_video.py` updated: 0.3s chapter-aware transitions (cut/wipe/fade)
- `assemble_with_audio.py` mixes music + SFX + placeholder VO
- Output: `Africa_S1_Silicon_Savannah_FINAL.mp4`

### D5 — Series Templates ✅
- `templates/blender/`: DiagramEnumerate, DataVizBarChart, FlowDiagram, MapReveal
- `templates/resolve/`: TextStat, FairlightMix
- Documented for Episode 2 (Lagos) reuse

### D6 — Remaining (Manual)
1. **Blender re-render** in progress (`render_scenes_mp4.py` → `render_log_teded.txt`)
2. **Record final VO** from `episode_1_script.md` → replace `assets/audio/vo/episode_01_vo.wav`
3. **Re-slip keyframes** to final VO timestamps
4. **Resolve LUT polish** per `docs/resolve_finish_workflow.md`
5. **Re-run** `assemble_with_audio.py` after VO + new renders complete
