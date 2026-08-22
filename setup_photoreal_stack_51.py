"""
Blender 5.1 Photoreal Production Stack — Africa S1
=================================================
Applies release-page + manual guidance for:
  - EEVEE ray tracing (full-res) + Light Path intensity (5.1 GI control)
  - Poly Haven–style PBR material hygiene (Principled, Smart filter)
  - Camera / DOF / AgX color
  - Animation: Easy Ease + Smooth (Gaussian) F-curve modifiers where available
  - Rigify enable (YB-Body ready); Geometry Nodes Bone Info note
  - Video encode: H.264 HIGH / GOOD (fidelity intermediate until PNG seq)

Run (Blender 5.1.2 ONLY):
  & "C:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe" `
    -b "blend\\africa_s1_master_v01.blend" -P "setup_photoreal_stack_51.py"

Sources:
  https://www.blender.org/download/releases/5-1/
  https://docs.blender.org/manual/en/5.1/render/eevee/render_settings/light_paths.html
  https://polyhaven.com/  (HDRI / textures already in assets/hdri)
"""
from __future__ import annotations

import math
import bpy
import addon_utils

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
HDRI_DIR = PROJECT + r"\assets\hdri"

SCENE_CAM = {
    "01_ColdOpen": {"lens": 35.0, "fstop": 5.6, "exposure": 0.15, "gi_indirect": 1.35},
    "02_Context2007": {"lens": 40.0, "fstop": 5.6, "exposure": 0.05, "gi_indirect": 1.2},
    "03_Beat1_Hubs": {"lens": 40.0, "fstop": 5.0, "exposure": 0.1, "gi_indirect": 1.25},
    "04_Beat1_Phone": {"lens": 50.0, "fstop": 4.0, "exposure": 0.0, "gi_indirect": 1.15},
    "05_Beat2_Money": {"lens": 35.0, "fstop": 8.0, "exposure": 0.35, "gi_indirect": 1.1},
    "06_Beat2_Solar": {"lens": 35.0, "fstop": 8.0, "exposure": 0.2, "gi_indirect": 1.4},
    "07_Beat3_Gap": {"lens": 40.0, "fstop": 8.0, "exposure": 0.25, "gi_indirect": 1.0},
    "08_Beat3_SecondaryCity": {"lens": 40.0, "fstop": 5.6, "exposure": 0.05, "gi_indirect": 1.2},
    "09_Closer": {"lens": 35.0, "fstop": 5.6, "exposure": 0.1, "gi_indirect": 1.3},
    "10_EndCard": {"lens": 50.0, "fstop": 8.0, "exposure": 0.0, "gi_indirect": 1.0},
}


def enable_addons():
    """Enable stock + useful extensions when present (5.1 Extensions platform).

    Note: GScatter currently fails on Blender 5.1 / Python 3.13 — skip quietly.
    Use Geometry Nodes scatter or update GScatter when a 3.13 build ships.
    """
    wanted = [
        "rigify",
        "io_scene_gltf2",
        "node_wrangler",
        "cycles",
        # Optional — may be missing or py-incompatible:
        "bl_ext.user_default.gscatter",
        "bl_ext.blender_org.polyhaven",
    ]
    out = []
    for mod in wanted:
        try:
            # Probe compatibility before enable
            if mod.startswith("bl_ext"):
                try:
                    addon_utils.check(mod)
                except Exception:
                    pass
            addon_utils.enable(mod, default_set=True, persistent=True)
            out.append({"module": mod, "ok": True})
        except Exception as e:
            out.append({"module": mod, "ok": False, "err": str(e)[:160]})
    return out


def configure_cycles_gpu():
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
    except Exception:
        return None
    backend = None
    for b in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = b
            prefs.get_devices()
            n = 0
            for d in prefs.devices:
                name = d.name.upper()
                if d.type in ("OPTIX", "CUDA") and any(k in name for k in ("NVIDIA", "GEFORCE", "RTX")):
                    d.use = True
                    n += 1
                elif d.type == "CPU":
                    d.use = True
            if n:
                backend = b
                break
        except Exception:
            continue
    return backend


def set_light_path_intensity(sc, direct=1.0, indirect=1.25):
    """Blender 5.1 EEVEE Light Paths intensity (GI juice without touching light energy)."""
    ee = sc.eevee
    # Prefer nested light_paths if present
    lp = getattr(ee, "light_paths", None) or getattr(ee, "light_path", None)
    targets = [ee]
    if lp is not None:
        targets.insert(0, lp)
    for obj in targets:
        for attr, val in (
            ("intensity_direct", direct),
            ("intensity_indirect", indirect),
            ("direct_light_intensity", direct),
            ("indirect_light_intensity", indirect),
            ("gi_intensity", indirect),
        ):
            if hasattr(obj, attr):
                try:
                    setattr(obj, attr, val)
                except Exception:
                    pass
        # Nested intensity block
        inten = getattr(obj, "intensity", None)
        if inten is not None:
            for attr, val in (("direct", direct), ("indirect", indirect)):
                if hasattr(inten, attr):
                    try:
                        setattr(inten, attr, val)
                    except Exception:
                        pass


def configure_eevee_photoreal(sc, gi_indirect=1.25):
    ee = sc.eevee
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.resolution_percentage = 100
    sc.render.fps = 24
    sc.render.use_motion_blur = False
    if hasattr(sc.render, "filter_size"):
        sc.render.filter_size = 1.15  # sharper than default ~1.5

    if hasattr(ee, "taa_render_samples"):
        ee.taa_render_samples = 128
    if hasattr(ee, "taa_samples"):
        ee.taa_samples = 32

    # Ray tracing — photoreal core (Blender 5.x EEVEE)
    if hasattr(ee, "use_raytracing"):
        ee.use_raytracing = True
    if hasattr(ee, "ray_tracing_method"):
        try:
            ee.ray_tracing_method = "SCREEN"
        except Exception:
            pass
    opts = getattr(ee, "ray_tracing_options", None)
    if opts:
        if hasattr(opts, "resolution_scale"):
            opts.resolution_scale = "1"  # full-res
        if hasattr(opts, "screen_trace_quality"):
            opts.screen_trace_quality = 0.55
        if hasattr(opts, "use_denoise"):
            opts.use_denoise = True
        for a in ("denoise_spatial", "denoise_temporal", "denoise_bilateral"):
            if hasattr(opts, a):
                setattr(opts, a, True)

    # Shadows
    if hasattr(ee, "shadow_ray_count"):
        ee.shadow_ray_count = 4
    if hasattr(ee, "shadow_step_count"):
        ee.shadow_step_count = 12
    if hasattr(ee, "shadow_resolution_scale"):
        ee.shadow_resolution_scale = 1.0

    # Fast GI
    if hasattr(ee, "use_fast_gi"):
        ee.use_fast_gi = True
    if hasattr(ee, "fast_gi_quality"):
        ee.fast_gi_quality = 0.55
    if hasattr(ee, "fast_gi_ray_count"):
        ee.fast_gi_ray_count = 4

    set_light_path_intensity(sc, direct=1.0, indirect=gi_indirect)

    # Mild bloom for highlight roll-off
    if hasattr(ee, "use_bloom"):
        ee.use_bloom = True
        if hasattr(ee, "bloom_threshold"):
            ee.bloom_threshold = 0.95
        if hasattr(ee, "bloom_intensity"):
            ee.bloom_intensity = 0.025

    # Color — AgX (OCIO 2.5 in 5.1)
    sc.display_settings.display_device = "sRGB"
    sc.view_settings.view_transform = "AgX"
    for look in ("AgX - Medium High Contrast", "Medium High Contrast", "None"):
        try:
            sc.view_settings.look = look
            break
        except TypeError:
            continue
    sc.view_settings.gamma = 1.0

    # Cycles fallback path when used
    if hasattr(sc, "cycles"):
        sc.cycles.device = "GPU"
        if hasattr(sc.cycles, "use_denoising"):
            sc.cycles.use_denoising = True
        try:
            sc.cycles.denoiser = "OPTIX"
        except Exception:
            pass


def configure_world(world):
    if not world:
        return
    if hasattr(world, "use_sun_shadow"):
        world.use_sun_shadow = True
    if hasattr(world, "sun_threshold"):
        # Soft sun from HDRI (photoreal EEVEE tip: higher threshold = softer)
        world.sun_threshold = 5.0
    if hasattr(world, "sun_angle"):
        world.sun_angle = math.radians(1.5)
    if world.use_nodes:
        for n in world.node_tree.nodes:
            if n.type == "BACKGROUND":
                s = n.inputs["Strength"].default_value
                n.inputs["Strength"].default_value = max(0.4, min(1.4, s))


def configure_camera(cam, lens, fstop):
    if not cam or cam.type != "CAMERA":
        return
    d = cam.data
    d.type = "PERSP"
    d.sensor_fit = "HORIZONTAL"
    d.sensor_width = 36.0
    d.lens = lens
    d.clip_start = 0.05
    d.clip_end = 500.0
    d.show_passepartout = True
    d.passepartout_alpha = 0.8
    d.dof.use_dof = True
    d.dof.aperture_fstop = fstop
    d.dof.aperture_blades = 6


def pbr_material_hygiene():
    """Poly Haven–style Principled hygiene + Smart image filtering."""
    touched = {"mats": 0, "images": 0, "nodes": 0}
    for img in bpy.data.images:
        if img.source not in {"FILE", "SEQUENCE"}:
            continue
        path = (img.filepath or img.name).lower()
        if path.endswith((".hdr", ".exr")):
            continue
        try:
            img.colorspace_settings.name = "sRGB"
        except Exception:
            pass
        touched["images"] += 1

    for mat in bpy.data.materials:
        if not mat.use_nodes:
            continue
        touched["mats"] += 1
        for node in mat.node_tree.nodes:
            if node.type == "TEX_IMAGE":
                if hasattr(node, "interpolation"):
                    node.interpolation = "Smart"
                touched["nodes"] += 1
            if node.type == "BSDF_PRINCIPLED":
                # Ensure rough/metal sane for soft-pop photoreal
                if "Roughness" in node.inputs and node.inputs["Roughness"].default_value < 0.05:
                    # avoid mirror fireflies on non-hero
                    if "Sasa" not in mat.name and "Yellow" not in mat.name:
                        node.inputs["Roughness"].default_value = 0.35
    # Hero ball pop
    mat = bpy.data.materials.get("SasaYellow")
    if mat and mat.use_nodes:
        for n in mat.node_tree.nodes:
            if n.type == "BSDF_PRINCIPLED":
                n.inputs["Base Color"].default_value = (1.0, 0.835, 0.31, 1)
                n.inputs["Roughness"].default_value = 0.22
                if "Emission Color" in n.inputs:
                    n.inputs["Emission Color"].default_value = (1.0, 0.9, 0.25, 1)
                    n.inputs["Emission Strength"].default_value = 1.5
    return touched


def smooth_camera_fcurves():
    """Non-destructive Gaussian Smooth on camera F-curves (Blender 5.1)."""
    applied = []
    for sc in bpy.data.scenes:
        cam = sc.camera
        if not cam or not cam.animation_data or not cam.animation_data.action:
            continue
        action = cam.animation_data.action
        # Layered actions: iterate fcurves via slots if needed
        fcurves = getattr(action, "fcurves", None)
        if fcurves is None and hasattr(action, "layers"):
            # 5.x layered — try channelbags
            try:
                fcurves = []
                for layer in action.layers:
                    for strip in layer.strips:
                        for slot in getattr(strip, "channelbags", []) or []:
                            fcurves.extend(list(getattr(slot, "fcurves", []) or []))
            except Exception:
                fcurves = []
        if not fcurves:
            continue
        for fc in fcurves:
            # Skip if already has gaussian/smooth modifier
            has = False
            for m in fc.modifiers:
                t = getattr(m, "type", "")
                if t in {"SMOOTH", "GAUSSIAN_SMOOTH", "FGAUSSIAN"} or "SMOOTH" in t:
                    has = True
                    # ensure first in stack
                    try:
                        while fc.modifiers.find(m.name) > 0:
                            bpy.context.view_layer.objects.active = cam
                            break
                    except Exception:
                        pass
            if has:
                continue
            try:
                # Try new 5.1 type name variants
                mod = None
                for tname in ("GAUSSIAN_SMOOTH", "SMOOTH_GAUSSIAN", "SMOOTH"):
                    try:
                        mod = fc.modifiers.new(type=tname)
                        break
                    except TypeError:
                        continue
                if mod is None:
                    continue
                if hasattr(mod, "factor"):
                    mod.factor = 1.0
                if hasattr(mod, "steps"):
                    mod.steps = 2
                # Move to first position if API allows
                try:
                    while fc.modifiers[0] != mod:
                        bpy.ops.graph.fmodifier_move_up()  # may fail headless
                        break
                except Exception:
                    pass
                applied.append(f"{sc.name}:{fc.data_path}")
            except Exception:
                continue
    return applied


def configure_ffmpeg_hq(sc):
    """High-quality intermediate encode settings when FFMPEG still exists.

    Blender 5.1.2 image_settings.file_format no longer lists FFMPEG in some
    builds (PNG/EXR/AVIF preferred). Keep ffmpeg props if present; else leave
    image format alone (render_scenes_mp4.py owns output format).
    """
    # 5.1.2: RNA may list FFMPEG but assignment is rejected — never force it.
    try:
        sc.render.image_settings.file_format = "FFMPEG"
    except (TypeError, ValueError):
        pass
    ff = getattr(sc.render, "ffmpeg", None)
    if ff is None:
        return
    try:
        ff.format = "MPEG4"
        ff.codec = "H264"
    except Exception:
        return
    if hasattr(ff, "constant_rate_factor"):
        for v in ("PERCEIVED_QUALITY", "HIGH", "MEDIUM"):
            try:
                ff.constant_rate_factor = v
                break
            except TypeError:
                continue
    if hasattr(ff, "ffmpeg_preset"):
        try:
            ff.ffmpeg_preset = "GOOD"
        except TypeError:
            pass
    if hasattr(ff, "ffmpeg_crf"):
        try:
            ff.ffmpeg_crf = 18
        except Exception:
            pass
    try:
        ff.audio_codec = "NONE"
    except Exception:
        pass


def run():
    addons = enable_addons()
    gpu = configure_cycles_gpu()
    mats = pbr_material_hygiene()
    scenes = []
    for sname, cfg in SCENE_CAM.items():
        sc = bpy.data.scenes.get(sname)
        if not sc:
            scenes.append({"scene": sname, "status": "missing"})
            continue
        try:
            bpy.context.window.scene = sc
        except Exception:
            pass
        configure_eevee_photoreal(sc, gi_indirect=cfg["gi_indirect"])
        sc.view_settings.exposure = cfg["exposure"]
        configure_world(sc.world)
        if sc.camera:
            configure_camera(sc.camera, cfg["lens"], cfg["fstop"])
            # Focus ball if present
            ball = next((o for o in sc.objects if "Sasa_Ball" in o.name and not o.hide_render), None)
            if ball:
                sc.camera.data.dof.focus_object = ball
        configure_ffmpeg_hq(sc)
        scenes.append({
            "scene": sname,
            "status": "ok",
            "samples": getattr(sc.eevee, "taa_render_samples", None),
            "rt": getattr(sc.eevee, "use_raytracing", None),
            "lens": cfg["lens"],
            "gi_indirect": cfg["gi_indirect"],
            "view": sc.view_settings.view_transform,
        })
    smooth = smooth_camera_fcurves()
    bpy.ops.wm.save_mainfile()
    return {
        "version": bpy.app.version_string,
        "filepath": bpy.data.filepath,
        "gpu_backend": gpu,
        "addons": addons,
        "materials": mats,
        "camera_smooth": smooth[:20],
        "scenes": scenes,
    }


if __name__ == "__main__":
    import json
    print("=== setup_photoreal_stack_51 ===")
    print(json.dumps(run(), indent=2, default=str))
