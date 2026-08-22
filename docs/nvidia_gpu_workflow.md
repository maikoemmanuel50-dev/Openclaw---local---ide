# NVIDIA RTX 4060 — Production Quality & Workflow Guide

**GPU:** NVIDIA GeForce RTX 4060 Laptop GPU (8 GB)  
**Driver:** 610.62 (CUDA 13.3)  
**NVIDIA App:** Running (v11.0.8)  
**Also present:** Intel UHD Graphics (hybrid laptop — force NVIDIA for creative apps)

---

## Current Live Status (captured)

| Metric | Value | Notes |
|--------|-------|-------|
| Perf state | P0 | Max clocks available |
| Temp | ~73–79°C | Warm but OK under load; keep vents clear |
| VRAM | ~2.4–2.5 / 8.2 GB | Headroom for Resolve + Blender |
| Util | ~60% | Resolve + Blender + Cursor sharing GPU |
| Power | ~40–48 W / 80 W cap | Laptop TGP — avoid dual heavy renders |

**Running on GPU now:** Resolve, Blender, Cursor, Brave, NVIDIA App

---

## Applied Automatically

1. **Windows High-performance GPU** pinned for:
   - `Resolve.exe`
   - `blender.exe` (5.1.2)
   - `Cursor.exe`
2. **Resolve project:** Optimized media ON, auto render cache ON
3. Script ready: `setup_nvidia_gpu.py` → OptiX/CUDA for Cycles when needed

---

## NVIDIA App — What You Should Verify (GUI)

Open **NVIDIA App** (already running) → **Graphics / Settings**:

### Driver branch
Prefer **Studio Driver** for Resolve + Blender stability over Game Ready when possible.  
Driver 610.x family already includes Studio creative-app support (Resolve 21 / Blender).

### Per-app settings (add if missing)
| App | Preferred GPU | Power management | Antialiasing |
|-----|---------------|------------------|--------------|
| DaVinci Resolve | High-performance NVIDIA | Prefer maximum performance | App-controlled |
| Blender | High-performance NVIDIA | Prefer maximum performance | App-controlled |
| Cavalry (if installed) | High-performance NVIDIA | Prefer maximum performance | App-controlled |

Path: NVIDIA App → Graphics → Program Settings → Add program → browse exe.

### Optional creator tools
- **NVIDIA Broadcast** — Studio Voice noise removal for VO recording (Fairlight still masters the mix)
- **FrameView** — optional FPS/GPU overlay while scrubbing Resolve

---

## DaVinci Resolve — GPU Checklist

**Preferences → System → Memory and GPU** (manual once):
1. GPU Processing Mode: **CUDA**
2. GPU selection: **NVIDIA GeForce RTX 4060 Laptop GPU** only (uncheck Intel if listed)
- Avoid dual-GPU processing on this laptop (wastes VRAM bandwidth)

**Preferences → System → Decode / Encode:**
- Enable **NVIDIA** hardware decode for H.264/H.265
- Deliver page: encoder **NVIDIA** / hardware when exporting FINAL

**Project (already tuned via MCP):**
- Optimized media: ON
- Auto render cache: ON
- Timeline: 1920×1080 @ 24fps
- Cache codec: ProRes Proxy-class (`apch`)

**Workflow management:**
- Edit with **proxies / optimized media** for yellow-ball overlays + Fusion
- Full-res only for final color + deliver
- Don’t run Blender full-scene render *and* Resolve Fusion playback at once (8 GB VRAM)

---

## Blender — GPU Checklist

Run when re-rendering scenes:

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b "C:\Users\HP\OneDrive\The Vault\Africa Season 1\blend\africa_s1_master_v01.blend" -P "C:\Users\HP\OneDrive\The Vault\Africa Season 1\setup_nvidia_gpu.py"
```

Then Preferences → System:
- Cycles Render Devices: **OptiX** (RTX) with the 4060 checked
- Pipeline default remains **Eevee Next** for 2.5D motion graphics (faster, fits VRAM)
- Use Cycles+OptiX only for glass / map glow quality passes

**VRAM hygiene:** Close Brave GPU tabs / idle Blender GUI before overnight `render_scenes_mp4.py`.

---

## Yellow Ball / Cavalry / Affinity on NVIDIA

| Stage | Device |
|-------|--------|
| Affinity `.af` masters | NVIDIA GPU (pin in Windows Graphics Settings) |
| Cavalry ball animation | NVIDIA GPU + real-time viewport |
| Resolve Fusion ball overlays | CUDA / NVIDIA |
| Blender scene plates | Eevee on NVIDIA; OptiX if Cycles |

---

## Thermal / Power Workflow Rules (Laptop)

1. Plug into AC power; set Windows power plan to **High performance** during renders  
2. One heavy job at a time: either Blender batch **or** Resolve deliver encode  
3. If GPU hits >85°C sustained, pause and cool — quality drops under thermal throttle  
4. Keep NVIDIA App open for driver/health; don’t force Game Ready mid-project  

---

## Quality Gate Before FINAL Export

- [ ] Resolve Preferences show CUDA + RTX 4060 only  
- [ ] NVIDIA App: Resolve + Blender = High performance + Prefer max performance  
- [ ] Optimized media generated for timeline  
- [ ] Deliver uses NVIDIA hardware encode (H.264/H.265)  
- [ ] `nvidia-smi` shows Resolve (and encode) on GPU 0 during export  
- [ ] No second full Blender render competing for VRAM  

---

## Quick Monitor Command

```powershell
nvidia-smi
nvidia-smi --query-gpu=utilization.gpu,memory.used,temperature.gpu,power.draw --format=csv -l 2
```
