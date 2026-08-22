# Blender Rig & Animation Resource Lock — Africa S1

**Binary:** Blender **5.1.2** only  
**Apply scripts:** `setup_yellow_ball_teded_physics.py` · `setup_yb_body_humanoid.py` · `setup_blender_rig_animation_lock.py` · `setup_documentary_aesthetic_lock.py` · `setup_arch_comm_iv_lock.py`  
**When:** Prelocks before force HQ (`run_full_reformulation.ps1`) — do not dual-open the master `.blend` during render.

Creative locks stay: yellow ball `#FFD54F` only · YB-Body = faceless torso + ball head · no faces.

---

## Faceless documentary pack (added)

| Video | Takeaway |
|-------|----------|
| [Edit Faceless (Fern, Neo & Imperial)](https://youtu.be/Jmcg5ZSU8a8) | Faceless hero language; cinematic DOF; atmospheric plates |
| [Science of Aesthetic YT 3D Documentaries](https://youtu.be/YJdGgpZoiAA) | Script-driven scenes; smooth cams; shaping light |
| [I animated this in 18 days (tinynocky)](https://youtu.be/tCTkkHGRpNk) | Plan→previz→rig→anim→env→light→Resolve grade; Graph Editor timing; Poly Haven |

Full lock: `docs/DOCUMENTARY_AESTHETIC_LOCK.md`

---

## Curated tutorials (user pack) → what we enforce

| Video | Takeaway we bake into scripts |
|-------|-------------------------------|
| [Animation for Beginners (Ryan King Art)](https://youtu.be/CBJp82tlR3M) | Keyframes on Loc/Rot/Scale; Timeline + **Graph Editor**; BEZIER handles; FPS lock **24**; render path hygiene |
| [Watch This BEFORE You Start Animating (Crashsune)](https://www.youtube.com/watch?v=UtLku74CvXQ&list=PLcaQc6eQjXCxFhrsFWWemTkxAWwAmbxzi) | Plan extremes first; timing before polish; arcs & spacing before detail |
| [Rig and Animate in Under a Minute](https://www.youtube.com/shorts/IeV6xLGIp94) | Fast path: armature → **Automatic Weights** → Pose Mode keys |
| [How to Animate 3D Characters in 1 Minute (CG Geek)](https://youtu.be/TjJLIuFKA20) | Pose Mode only for character motion; broad poses then refine |
| [First Steps in Blender Animation (ProductionCrate)](https://youtu.be/PGvyBlgXHi8) | Object vs bone animation; interpolation types; camera as separate action |
| [Rig Any 3D Character in 60 Seconds](https://www.youtube.com/shorts/W9WOi9SxG7w) | Apply transforms → parent **With Automatic Weights** |
| [3D Animated Character Creation (CrossMind)](https://www.youtube.com/watch?v=0cbMH30xs54&list=PLgO2ChD7acqFl3vtixa673FwCf2OfcCqK) | Clean mesh → proportioned armature → skin → animate |
| [Animate inside Edit Mode (QuickTips)](https://youtu.be/EK3PgoZ9rqo) | Prefer **shape keys / bones** over raw Edit-Mode vertex anim for production; Edit-Mode anim only for special cases |
| [Beginner Blender Tutorial 2026 (Blender Guru)](https://youtu.be/z-Xl9tGqH14) | Fundamentals: transforms, collections, shading before animation |
| [Animate like a PRO (CBaileyFilm)](https://youtu.be/AEAc_lLjOMc) | Blocking → splining → polish; ease-in/out; hold on readables |
| [Become a PRO at Animation (CG Geek)](https://youtu.be/_C2ClFO3FAY) | Graph Editor curves drive weight; avoid LINEAR pops |
| [How to Animate ANYTHING (SharpWind)](https://youtu.be/JQT9sT1YuAI) | Anything keyable (materials, shape keys, constraints) — keep drivers clean |

Also: TED-Ed [timing & spacing](https://ed.ted.com/lessons/animation-basics-the-art-of-timing-and-spacing-ted-ed) · [Stretch-To ball rig (Blender 5.1)](https://oldetinkererstudio.com/how-do-you-make-a-squash-and-stretch-rig-in-blender-5-1/) · [Rigify character path](https://www.strayspark.studio/blog/how-to-rig-a-character-in-blender-2026)

---

## Telegram — Arch Comm IV pack (JKUAT Blender Class 01–16)

Source: [private group post](https://t.me/c/1923786175/233) · media on disk: `Telegram/`  
Raw paste: `docs/telegram_imports/post_233_arch_comm_iv.txt`  
Stills: `docs/telegram_imports/arch_comm_iv_frames/`  
**Lock script:** `setup_arch_comm_iv_lock.py` · full notes: `docs/ARCH_COMM_IV_LOCK.md`

| File | ~Duration |
|------|-----------|
| Blender_Class 01.mp4 | 5.3 min |
| Blender_Class 02.m4v | 1.9 min |
| Blender_Class 03.m4v | 6.7 min |
| Blender_Class 04.m4v | 8.4 min |
| Blender_Class 05.m4v | 1.9 min |
| Blender_Class 06.m4v | 2.4 min |
| Blender_Class 07.m4v | 3.5 min |
| Blender_Class 08.m4v | 4.4 min |
| Blender_Class 09 (1).m4v | 3.6 min |
| Blender_Class 10.m4v | 13.1 min |
| Blender_Class 11.m4v | 5.5 min |
| Blender_Class 12.m4v | 6.8 min |
| Blender_Class 13.m4v | 13.8 min |
| Blender_Class 14.m4v | 20.5 min |
| Blender_Class 15.m4v | 14.4 min |
| Blender_Class 16.m4v | 13.7 min |

| Theme from classes | Bake into |
|--------------------|-----------|
| Cycles GPU + Denoise + noise thresholds | `setup_arch_comm_iv_lock.py` |
| Metric real-world scale / ortho plan | same + scale audit |
| Principled PBR (albedo/normal/height) | same material wiring |
| Texture libraries + Poly Haven / Sketchfab | remap → `assets/textures` · HDRIs in `assets/hdri` |
| Area lights + multi-camera interiors | soft Area fill; camera lens floor 24→35 |
| Naming / collections | `HERO` · `ENV` · `LIGHTS` · `CAMERAS` · `MODEL_ADDITIONS` |
| Still: yellow ball remains only hero — no competing arch mascots | creative gate |

---

## Hard rules for this project

1. **FPS = 24** on every scene.  
2. **Apply Location/Rotation/Scale** on meshes before armature bind.  
3. **Skin with Automatic Weights** (`ARMATURE_AUTO`); Armature modifier before Subsurf when possible.  
4. **Pose Mode** for bone keys — never animate deform bones in Edit Mode.  
5. **Graph Editor:** BEZIER + AUTO_CLAMPED (or FREE with ease) — no LINEAR on hero ball / body.  
6. **Shape keys** for ball squash/stretch (volume intent) — not Edit-Mode vertex animation.  
7. **Actions named** `YB_*` / `Sasa_*` so Replace Action works (Blender 5.1 slots).  
8. **Idle loops** use F-curve Cycles modifier (bob / breath), not duplicated keys forever.  
9. Enable **Rigify** addon (available for future meta-rig upgrades); current YB-Body uses a lightweight anthropometric armature with the same skinning rules.

---

## Run order (post-HQ)

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" `
  -b "blend\africa_s1_master_v01.blend" -P setup_yellow_ball_teded_physics.py
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" `
  -b "blend\africa_s1_master_v01.blend" -P setup_yb_body_humanoid.py
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" `
  -b "blend\africa_s1_master_v01.blend" -P setup_blender_rig_animation_lock.py
```

Report: `renders/quality/rig_animation_lock_report.json`
