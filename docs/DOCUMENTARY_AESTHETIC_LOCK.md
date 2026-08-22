# Faceless YT Documentary Aesthetic Lock — Africa S1

Sources folded into production (Blender **5.1.2** · Resolve grade · VO-first):

| Video | Channel | What we take |
|-------|---------|--------------|
| [Edit Faceless Videos (Fern, Neo & Imperial)](https://youtu.be/Jmcg5ZSU8a8) | TomsProject | Faceless subjects; cinematic DOF; atmospheric plates; hero motif clear in frame |
| [Science of Aesthetic YT 3D Documentaries](https://youtu.be/YJdGgpZoiAA) | Lucas Edits | Script-driven scenes; smooth cams; light that shapes with shadow; YT doc composition |
| [I animated this in 18 days… in Blender](https://youtu.be/tCTkkHGRpNk) | tinynocky | Plan→block→previz→rig→anim→env→light→**Resolve grade**; Graph Editor timing scale; Poly Haven; parent empties for speed |

Project cousins: `docs/CHANNEL_MERGE_TEMPLATE.md` · `docs/BLENDER_RIG_ANIM_RESOURCES.md` · `docs/YELLOW_BALL_TEDED_PHYSICS.md`

---

## Hard rules (creative lock preserved)

1. **Faceless only** — yellow ball `#FFD54F` / YB-Body charcoal torso + ball head (Fern/Imperial language).  
2. **VO / script drives picture** — no orphan motion (Lucas Edits).  
3. **DOF on hero** — camera Focus Object = `Sasa_Master` or `YB_Head_*` when present; f-stop from scene table (not razor-thin on charts).  
4. **Motion blur subtle** — EEVEE/Cycles shutter low (doc readability > action blur).  
5. **Parent empties** — camera + ball masters share speed scaling (tinynocky Graph Editor pivot trick).  
6. **Poly Haven** — HDRI + PBR in `assets/hdri` / `assets/textures/polyhaven`.  
7. **Final look in Resolve** — Blender AgX MHC plates; chapter soft-pop polish on Color page (tinynocky Day 18).  
8. **No 4K** until `docs/PRE_4K_GATE.md` clears.

---

## Per-scene DOF / doc intent

| Scene | Focus | f-stop | Note |
|-------|-------|--------|------|
| 01 ColdOpen | Ball / skyline | 4.0 | Soft dawn Fern atmosphere |
| 02 Context | Ball / kiosk | 5.0 | Coin bounce readable |
| 03 Hubs | Ball orbit | 4.5 | Parallax depth |
| 04 Phone | Ball | 3.5 | CU — shallower |
| 05 Money | Chart (protect) | 8.0 | Deep — stats sharp |
| 06 Solar | Panels / ball | 5.6 | Glare OK |
| 07 Gap | Map / ball | 8.0 | Deep — 97% hold |
| 08 Secondary | YB founder | 4.0 | Quiet Imperial mood |
| 09 Closer | Crowd / ball | 5.0 | Warm dusk |
| 10 EndCard | Logo / ball | 8.0 | Flat readable |

---

## Script

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" `
  -b "blend\africa_s1_master_v01.blend" -P setup_documentary_aesthetic_lock.py
```

Runs in `finish_after_hq.ps1` after camera/framing + ball + YB-Body + rig hygiene.  
Report: `renders/quality/documentary_aesthetic_report.json`
