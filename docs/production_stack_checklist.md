# Production Stack Checklist — Yellow Ball Episode

## Cursor IDE (command center)
Keep this workspace open: `Africa Season 1`  
Key docs already in project:
- `docs/yellow_ball_throughline.md` ← opened in editor
- `docs/teded_style_bible.md`
- `docs/teded_scene_spec_ep01.md`
- `docs/audio_design_map.yaml`
- `docs/nvidia_gpu_workflow.md` ← RTX 4060 / NVIDIA App production guide

Agent drives: scripts, Resolve MCP, Canva MCP, NVIDIA GPU prefs, file assets.

---

## NVIDIA GPU (RTX 4060 Laptop — 8 GB)

**Status:** NVIDIA App open; driver 610.62; GPU pinned High-performance for Resolve, Blender, Cursor.

| Use NVIDIA for | Leave Intel UHD for |
|----------------|---------------------|
| Resolve edit / Fusion / encode | Desktop chrome / light UI |
| Blender Eevee + OptiX Cycles | — |
| Cavalry ball animation | — |
| Affinity when painting large boards | — |

**Rule:** One heavy GPU job at a time (Blender batch **or** Resolve deliver). See `docs/nvidia_gpu_workflow.md`.

---

## Creative lock — Yellow ball is the hero

Episode 1: **yellow ball is the only hero identity.**  
**Humanity:** ball transforms into a **faceless torso with yellow ball as head**; crowds = same format (many ball-heads). No faces, no acting cast. See `docs/yellow_ball_throughline.md`.

---

## Do you need Blender open?

**Not for the yellow ball throughline itself.**

| Task | App | Open now? |
|------|-----|-----------|
| Yellow ball transforms / timing | **Cavalry** (Canva) or Resolve Fusion | Yes — preferred for the ball |
| Scene backgrounds / parallax / chart / map | **Blender** | Only when re-rendering scenes |
| Layered ball masters / typography | **Affinity** | Yes for polish |
| Still boards / stock plates / brand | **Canva** | Yes (MCP already connected) |
| Edit, markers, VO, Fairlight, grade | **DaVinci Resolve** | Yes — project `Africa Season 1` is open |

### When to open Blender
- Re-render scenes after `setup_teded_elements.py` (labels/overlays)
- Fix Scene 05 chart / Scene 07 map camera
- Overnight batch: `render_scenes_mp4.py`

### When to leave Blender closed
- Designing/animating the **yellow ball** (use Cavalry or Fusion)
- Editorial cuts, markers, audio (Resolve)
- Illustration stills (Canva / Affinity)

---

## Resources you need

### Already in place
- [x] Resolve project `Africa Season 1` + timeline `Episode 01 - Assembly`
- [x] Canva MCP connected (designs created for ball master + storyboard)
- [x] Yellow ball SVGs + PNGs in `assets/yellow_ball/`
- [x] Style bible + scene spec + audio map
- [x] Silent / FINAL mp4 drafts

### You should have installed / logged in
1. **DaVinci Resolve** (Studio preferred for scripting; free + bridge also works) — open
2. **Canva account** — connected via Composio
3. **Affinity** (Canva sister app) — for `.af` layered ball masters → Resolve 21 native import
4. **Cavalry** (free with Canva) — yellow ball procedural animation  
   https://www.canva.com/help/free-cavalry-access/
5. **Blender 5.1.2** — master scenes + MCP; open only for scene re-renders / soft-pop work
6. **FFmpeg** — assembly scripts
7. **Inter / Nunito Sans** fonts (optional, for Resolve Text+)

### Still needed from you
| Resource | Why |
|----------|-----|
| **Recorded VO** (`assets/audio/vo/episode_01_vo.wav`) | Locks all ball transforms to words |
| Affinity layered `.af` ball masters | Live refresh into Resolve |
| Cavalry ball motion export (PNG seq / ProRes) | Smooth TED-Ed timing/spacing |
| Optional: better stock plates in Canva | Texture under illustrations only |

### No Affinity MCP
Affinity has **no MCP in Cursor**. Workflow:
Affinity design → save `.af` → import in Resolve Media Pool → Split Layers into Place.

---

## Recommended open-now layout

1. **Cursor** — this chat + `docs/yellow_ball_throughline.md`
2. **Resolve** — Edit page, timeline markers
3. **Canva** — fill the two blank designs (links below)
4. **Cavalry** — animate ball states
5. **Blender** — closed until re-render time

### Canva designs (edit in browser)
- SunSeed Master: design ID `DAHSF7ASb_s`
- Transform Storyboard: design ID `DAHSFzkCgoM`
