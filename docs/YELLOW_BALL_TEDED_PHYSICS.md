# Yellow Ball — TED-Ed Physics & Photoreal Rig Lock

**Script:** `setup_yellow_ball_teded_physics.py` (Blender **5.1.2** only)  
**When:** After HQ batch frees `africa_s1_master_v01.blend` (wired into `finish_after_hq.ps1`)  
**Hero:** `#FFD54F` only · faceless · no competing mascots  
**Tutorial pack:** [`docs/BLENDER_RIG_ANIM_RESOURCES.md`](BLENDER_RIG_ANIM_RESOURCES.md)

## Standards applied

| Source | What we take |
|--------|----------------|
| [TED-Ed timing & spacing](https://ed.ted.com/lessons/animation-basics-the-art-of-timing-and-spacing-ted-ed) | Same timing, different spacing = weight; accelerate into impact; decelerate to apex |
| [Bouncing ball / squash-stretch](https://drawntoanimation.com/bouncing-ball-animation-guide/) | Volume-preserving squash on contact, stretch on rebound, energy decay |
| [Blender 5.1 Stretch-To rig](https://oldetinkererstudio.com/how-do-you-make-a-squash-and-stretch-rig-in-blender-5-1/) | CTRL_Root + CTRL_Squash + MCH_Stretch |
| Principled plastic / coat | Coat weight ~0.85, roughness ~0.28, soft SSS + micro bump + rim emission |

## Node graph (must stay fully linked)

`TexCoord → Mapping → Noise → Bump → Principled.Normal`  
`Principled + Emission → Mix Shader (LayerWeight/Facing) → Material Output`

Audit written to `renders/quality/yellow_ball_teded_report.json`.

## Per-scene motion kinds

Matches `docs/yellow_ball_throughline.md`: rise · coin_bounce · orbit · push · inflate · shimmer · concentrate · roll · reignite · settle.

## Uptake

1. Post-HQ auto-run upgrades the blend.  
2. Ball-heavy beats also live on Resolve **V2** (keep overlays).  
3. Optional selective re-render of S02/S05/S08/S10 if V1 bake must show new physics.  
4. **Do not** start 4K until PRE_4K_GATE clears.
