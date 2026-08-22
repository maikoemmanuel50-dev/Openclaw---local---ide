# AFRICA S1 — Yellow Ball Concept Bible
**Theme:** Tech Growth × African Excellence  
**Motif:** A living yellow sphere that transforms, pops, and bursts through Episode 1  
**Episode:** Silicon Savannah  
**Runtime:** ~7:00 @ 24fps

---

## 1. Creative Thesis

The **Yellow Ball** is the episode’s emotional and narrative through-line — a single, memorable character that embodies:

| Meaning | Expression |
|---------|------------|
| **Potential** | A seed of energy at dawn |
| **Motion / money** | Rolling, bouncing, leaping with transactions |
| **Innovation** | Morphing into phone, chart bar, solar disc, map pin |
| **Excellence** | Bursting into gold constellations at the closer |

Inspired by TED-Ed’s minimalist “brave little character” approach ([Einstein TED-Ed](https://blog.ed.ted.com/2015/01/13/designing-einstein-2-animators-use-minimalist-style-to-illustrate-history/)) and particle morph / burst techniques from motion design practice ([path morphing & burst masterclass](https://designkkashi.com/en/after-effects-path-morphing-burst-liquid-motion-guide/), [particle morph tools](https://aescripts.com/reflow/)).

**Rule:** The ball is always on screen or just off-screen. Every major VO beat either *moves* it, *morphs* it, or *bursts* it.

---

## 2. Character Design — “Sasa” (the Yellow Ball)

**Name (internal):** Sasa (“now” in Swahili)  
**Base color:** `#FFD54F` (gold yellow)  
**Accent rim:** `#FFEB3B` highlight / `#F9A825` shadow  
**Glow:** Soft outer glow `#FFE082` at 40% opacity  
**Face (optional micro-expression):** Two dots + smile only in HopefulDusk chapter  
**Scale:** ~12–18% of frame height when hero; tiny when ambient

### Stage Sheet (morph forms)

| Stage | Form | Scene | Trigger word / beat |
|-------|------|-------|---------------------|
| **S0 Seed** | Solid yellow ball, soft bounce | Cold Open | “Six-thirty… Nairobi” |
| **S1 Pulse** | Ball with digital path trails | Cold Open | “money has already moved” |
| **S2 Coin** | Ball → flat M-Pesa disc / coin | Context 2007 | “M-Pesa” |
| **S3 Hub** | Ball splits into 3 satellite orbs | Beat 1 Hubs | “iHub / Andela / NaiLab” |
| **S4 Phone** | Ball compresses into phone screen glow | Beat 1 Phone | “phone” |
| **S5 Chart** | Ball elongates into rising neon bar | Beat 2 Money | “$984 million” → **POP** |
| **S6 Solar** | Ball flattens into solar disc + glare | Beat 2 Solar | “solar” → **BURST rays** |
| **S7 Pin** | Ball becomes map pin over Nairobi | Beat 3 Gap | “97%” → **impact slam** |
| **S8 Quiet** | Ball dimmed, desaturated, small | Secondary City | “underserved” |
| **S9 Constellation** | Ball bursts into gold star network | Closer | “Microsoft / Visa / UN” |
| **S10 Emblem** | Ball becomes AFRICA logo gold core | End Card | logo hold |

---

## 3. Color System (Vibrant Override)

Keep TED-Ed chapter structure but **raise saturation** and lock yellow as the constant:

| Chapter | BG / Environment | Ball | Burst / Pop accents |
|---------|------------------|------|---------------------|
| Dawn | `#E8845C` → `#7B6BA8` | `#FFD54F` | `#FF6B35` sparks |
| Daylight | `#E8F5E9` / white | `#FFD54F` | `#4CAF50` confetti |
| DarkData | `#0D0D1A` charcoal | `#FFD54F` + `#00E676` rim | Neon green shards |
| CoolTension | `#263238` slate | Dim `#C9A227` | `#FF6B35` slam ring |
| HopefulDusk | `#1A237E` deep blue | `#FFD54F` face + smile | Gold particle rain |

**Pop / Burst vocabulary**
- **POP:** Scale 1.0 → 1.35 → 1.0 in 6–8 frames + ring expand + 8–12 spark particles
- **BURST:** Ball dissolves into 24–64 particles that reform into next shape (morph)
- **IMPACT:** Scale punch + screen flash 2 frames + radial lines
- **SCATTER → REFORM:** Particles travel along bezier paths to next form (Resolve Fusion / Blender particles)

---

## 4. Scene-by-Scene Ball Storyboard

### S01 Cold Open (50s)
- Ball rises with dawn sun behind Nairobi skyline  
- Rolls L→R along matatu silhouettes  
- On “money… moved” → **PULSE** + digital path trails attach  
- Exit: ball flies into pocket silhouette → hard cut

### S02 Context 2007 (45s)
- Ball emerges from Nokia-era phone → **morph to coin**  
- Coin hops agent → recipient (M-Pesa flow)  
- Exit: coin spins into camera → wipe to hubs

### S03 Beat 1 Hubs (45s)
- Ball **splits into 3** satellite orbs (iHub / Andela / NaiLab)  
- Staggered **POP** as each hub named  
- Orbs recombine → roll into S04

### S04 Beat 1 Phone (25s)
- Ball compresses into phone UI glow  
- **POP** on screen as “Mobile-First” label  
- Exit: phone glow becomes chart seed

### S05 Beat 2 Money (45s) — HERO BURST
- Ball elongates into bar chart bars rising  
- At peak `$984M` → **MASSIVE POP** (confetti + neon shards)  
- Morph trail into solar disc for S06

### S06 Beat 2 Solar (40s)
- Ball = solar disc on rooftop  
- **BURST rays** outward on “Pay-As-You-Go”  
- Soft fade to map

### S07 Beat 3 Gap (50s)
- Ball becomes glowing map pin on Nairobi  
- On “97%” → **IMPACT slam** (screen shake 4 frames)  
- Pin shrinks as secondary cities labeled

### S08 Secondary City (35s)
- Quiet, desaturated ball rolls slowly on dusty street  
- Almost still — emotional contrast  
- Exit: ball brightens toward dusk

### S09 Closer (70s)
- Ball gains smile / face  
- On global hubs → **CONSTELLATION BURST** (gold stars connect Nairobi → world)  
- “Forecast” → ball leads line to Lagos / Kigali / Accra

### S10 End Card (15s)
- Ball settles into AFRICA logo gold core  
- Soft pulse loop  
- Hold

---

## 5. Tool Pipeline (MCP Reality)

| Tool | Role | Access in this workspace |
|------|------|--------------------------|
| **Canva** (Composio MCP) | Character sheets, burst frames, icons, stock-adjacent graphics, exports PNG/MP4 | ✅ Active |
| **Affinity** (sister to Canva) | Precision vector polish (macOS MCP only) | ❌ No Windows MCP — design in Canva / Blender SVG |
| **Blender MCP** | 3D ball morph, particles, scene integration | ✅ When Blender addon running |
| **DaVinci Resolve MCP** | Editorial assembly, Fusion pop/burst comps, titles, deliver | ✅ Connected |
| **Stock** | Pexels / Coverr / Mixkit B-roll under ball overlays | Manual / download scripts |

**Affinity note:** Affinity MCP servers (e.g. AffinityMCP) require macOS AppleScript. On Windows, use **Canva** for the same design family, or export SVG from Canva → refine in Affinity Desktop manually if installed.

---

## 6. Production Implementation Steps

### A. Visuals (Canva → assets)
1. Create character sheet + stage icons (1920×1080 + 1080×1080)  
2. Export transparent PNGs for each stage (S0–S10)  
3. Export burst / pop sprite sheets (spark ring, confetti, shards)  
4. Optional: short Canva MP4 loops for particle rain  

### B. Animation (Blender)
1. Build `YellowBall` empty + mesh sphere with emission material `#FFD54F`  
2. Geometry Nodes / shape keys for morph stages  
3. Particle systems for POP / BURST (emit on markers)  
4. Parent ball to camera or world empty per scene  

### C. Editorial (Resolve)
1. Timeline: video track V1 = scene plates; V2 = ball overlays; V3 = burst FX  
2. Fusion: radial burst, glow, impact flash templates  
3. Markers at each morph/pop beat (align to VO later)  
4. Deliver: YouTube 1080p + HQ master  

### D. Stock integration
1. Underlay aerial Nairobi / solar / tech B-roll (muted, desaturated 30%)  
2. Ball + illustrations sit on top at full saturation  

---

## 7. Reference Guides (researched)

| Guide | Why it matters |
|-------|----------------|
| [How to make TED-Ed style cartoons](https://graphicmama.com/blog/how-cartoon-animation-ted-ed/) | Style mix: 2D + motion graphics + infographic |
| [TED-Ed Einstein minimalism](https://blog.ed.ted.com/2015/01/13/designing-einstein-2-animators-use-minimalist-style-to-illustrate-history/) | Center-screen character, controlled palette |
| [TED-Ed BTS case study](https://www.behance.net/gallery/200233033/Behind-the-scenes-of-my-TED-Ed-film-Case-Study) | Color-coding chapters; leading character |
| [Path morphing & burst masterclass](https://designkkashi.com/en/after-effects-path-morphing-burst-liquid-motion-guide/) | Trim Paths + Repeater burst recipe |
| [Shape morphing](https://blog.nobledesktop.com/learn/after-effects/shape-morphing) | Path morph + Echo polish |
| [Canva official MCP](https://www.canva.dev/docs/mcp/) | Design generate / export via AI |
| [TED-Ed high-speed rail](https://youtu.be/2A1IEBFt6Xg) | Primary motion reference |

---

## 8. Success Criteria

- [ ] Yellow ball readable as character in first 5 seconds  
- [ ] At least **6 morphs** + **4 pops/bursts** across 7 minutes  
- [ ] Vibrant yellow never lost against chapter BGs (rim light / glow)  
- [ ] Stats `$984M` / `82%` / `97%` each get a POP or IMPACT  
- [ ] End card ball = series mascot (reusable for Lagos / Kigali / Accra)

---

*Living document — update when VO locked and Fusion templates built.*
