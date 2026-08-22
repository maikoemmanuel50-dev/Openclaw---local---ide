# MCP + resource connectivity — Africa S1

**Updated:** 2026-08-13 ~22:00 EAT

## MCP status

| Server | Status | How to go live |
|--------|--------|----------------|
| **Composio** | ✅ Ready + authenticated | — |
| **Canva** (via Composio) | ✅ Active (`canva_airway-sasin`) | OPEN designs listed (e.g. `DAHSJwY5FQc`, `DAHSJzAbXzM`) |
| **Blender MCP** | ⚠️ Server ready; **live port 9876 closed** | In Blender GUI: enable **Blender MCP** addon → **Start Server** (127.0.0.1:9876). CLI tools (`*_for_cli`) work without the port. |
| **DaVinci Resolve MCP** | ⚠️ Process can run; **bridge 49632 closed** | Open project → **Workspace → Scripts → `resolve_bridge`** (once/session). Free edition needs bridge. |
| **Qwen / Ollama** | ✅ `qwen2.5-coder:14b` @ 11434 | `python scripts/qwen_local.py ping` |

## User actions (required for full MCP)

1. **Blender** (preview or open30 blend already open): Edit → Preferences → Add-ons → **Blender MCP** → check **Start Server**.
2. **Resolve**: open **Africa S1 - Silicon Savannah** → **Workspace → Scripts → `resolve_bridge`**.
3. Reply **“bridge is up”** / **“blender mcp up”** so Cursor can drive timelines / scene edits.

## Provided resources already in use

| Resource | Path / ID | Used for |
|----------|-----------|----------|
| Mixkit + Unsplash stock | `renders/paced_overlays/stock_cinematic/` (**56** cuts) · `docs/ATTRIBUTIONS.md` | Open30 underlays + kinetic V3/V4 |
| Canva OPEN shells | 10 PNGs in `assets/canva/kinetic/infographics/open30/` · designs `DAHSJzAbXzM` / `DAHSJ2Y1PC0` / `DAHSJzxs1ls` / `DAHSJwY5FQc` | TED-Ed 30s open |
| Enhanced open | `s01_teded_open_30s_enhanced.mp4` | S01 0–720f |
| Fairlight stems | `renders/audio_stems/fairlight/` | A1–A5 |
| Telegram Arch Comm IV | `docs/telegram_imports/post_233_arch_comm_iv.txt` | Rig / GN lock refs |
| TED-Ed + CA Kenya stats | `docs/S01_TEDED_30S_OPEN.md` | Locked beat sheet |
| Local Qwen | Ollama | Resume plans / JSON drafts |

## Online sources (catalogued — obey clearance)

- Mixkit license · Unsplash license — `docs/ATTRIBUTIONS.md` / `COPYRIGHT_CLEARANCE.md`
- TED-Ed craft links · CA Kenya Q2 FY2024/25 PDF — open30 stats
- Poly Haven HDRIs · Blender 5.1 docs — photoreal stack
- Cavalry / Affinity / Resolve Affinity — `docs/yellow_ball_throughline.md` (YB waived this pass)

## Do not

- Start second GPU HQ while another Blender `-b` render runs  
- 4K until `docs/PRE_4K_GATE.md` clears  
- Replace VO with AI voice  
