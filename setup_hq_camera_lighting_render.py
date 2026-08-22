"""
High-quality camera + lighting + EEVEE render config for Africa S1 master.
Targets crisp photoreal plates on Blender 5.1.2 / RTX 4060.
"""
from __future__ import annotations

import math
import bpy

# Per-scene lens / exposure intent (meters, full-frame)
SCENE_HQ = {
    "01_ColdOpen": {"lens": 35.0, "fstop": 5.6, "exposure": 0.15},
    "02_Context2007": {"lens": 40.0, "fstop": 5.6, "exposure": 0.05},
    "03_Beat1_Hubs": {"lens": 40.0, "fstop": 5.0, "exposure": 0.1},
    "04_Beat1_Phone": {"lens": 50.0, "fstop": 4.0, "exposure": 0.0},
    "05_Beat2_Money": {"lens": 35.0, "fstop": 8.0, "exposure": 0.35},
    "06_Beat2_Solar": {"lens": 35.0, "fstop": 8.0, "exposure": 0.2},
    "07_Beat3_Gap": {"lens": 40.0, "fstop": 8.0, "exposure": 0.25},
    "08_Beat3_SecondaryCity": {"lens": 40.0, "fstop": 5.6, "exposure": 0.05},
    "09_Closer": {"lens": 35.0, "fstop": 5.6, "exposure": 0.1},
    "10_EndCard": {"lens": 50.0, "fstop": 8.0, "exposure": 0.0},
}


def configure_eevee(sc: bpy.types.Scene):
    ee = sc.eevee
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.resolution_percentage = 100
    sc.render.fps = 24
    sc.render.use_motion_blur = False  # keep type crisp unless shot needs it
    sc.render.film_transparent = False

    # Sampling — crisp anti-alias
    if hasattr(ee, "taa_render_samples"):
        ee.taa_render_samples = 128
    if hasattr(ee, "taa_samples"):
        ee.taa_samples = 32

    # Film filter — slightly sharper than default
    if hasattr(sc.render, "filter_size"):
        sc.render.filter_size = 1.2

    # Ray tracing (photoreal EEVEE core)
    if hasattr(ee, "use_raytracing"):
        ee.use_raytracing = True
    if hasattr(ee, "ray_tracing_method"):
        ee.ray_tracing_method = "SCREEN"
    opts = getattr(ee, "ray_tracing_options", None)
    if opts:
        if hasattr(opts, "resolution_scale"):
            opts.resolution_scale = "1"  # 1:1 crisp reflections
        if hasattr(opts, "screen_trace_quality"):
            opts.screen_trace_quality = 0.5
        if hasattr(opts, "screen_trace_thickness"):
            opts.screen_trace_thickness = 1.0
        if hasattr(opts, "trace_max_roughness"):
            opts.trace_max_roughness = 0.75
        if hasattr(opts, "use_denoise"):
            opts.use_denoise = True
        for a in ("denoise_spatial", "denoise_temporal", "denoise_bilateral"):
            if hasattr(opts, a):
                setattr(opts, a, True)

    # Shadows
    if hasattr(ee, "use_shadows"):
        ee.use_shadows = True
    if hasattr(ee, "shadow_ray_count"):
        ee.shadow_ray_count = 4
    if hasattr(ee, "shadow_step_count"):
        ee.shadow_step_count = 12
    if hasattr(ee, "shadow_resolution_scale"):
        ee.shadow_resolution_scale = 1.0
    if hasattr(ee, "shadow_pool_size"):
        try:
            ee.shadow_pool_size = "1024"
        except Exception:
            pass

    # Fast GI quality
    if hasattr(ee, "use_fast_gi"):
        ee.use_fast_gi = True
    if hasattr(ee, "fast_gi_quality"):
        ee.fast_gi_quality = 0.5
    if hasattr(ee, "fast_gi_ray_count"):
        ee.fast_gi_ray_count = 4
    if hasattr(ee, "fast_gi_step_count"):
        ee.fast_gi_step_count = 16
    if hasattr(ee, "fast_gi_resolution"):
        try:
            ee.fast_gi_resolution = "1"
        except Exception:
            pass
    if hasattr(ee, "gi_cubemap_resolution"):
        try:
            ee.gi_cubemap_resolution = "1024"
        except Exception:
            pass

    # DOF quality (optical from camera; EEVEE bokeh quality)
    if hasattr(ee, "use_bokeh_jittered"):
        ee.use_bokeh_jittered = True
    if hasattr(ee, "bokeh_overblur"):
        ee.bokeh_overblur = 0.02  # keep bokeh crisp, less mush
    if hasattr(ee, "bokeh_max_size"):
        ee.bokeh_max_size = 64.0

    # Soft bloom — photoreal highlight roll-off without haze
    if hasattr(ee, "use_bloom"):
        ee.use_bloom = True
        if hasattr(ee, "bloom_threshold"):
            ee.bloom_threshold = 0.9
        if hasattr(ee, "bloom_intensity"):
            ee.bloom_intensity = 0.03
        if hasattr(ee, "bloom_radius"):
            ee.bloom_radius = 4.0

    # Color management — cinematic but clean
    sc.display_settings.display_device = "sRGB"
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        try:
            sc.view_settings.look = "Medium High Contrast"
        except TypeError:
            sc.view_settings.look = "None"
    sc.view_settings.gamma = 1.0
    sc.sequencer_colorspace_settings.name = "sRGB"


def configure_world_sun(world: bpy.types.World | None):
    if not world:
        return
    if hasattr(world, "use_sun_shadow"):
        world.use_sun_shadow = True
    if hasattr(world, "sun_threshold"):
        world.sun_threshold = 0.8
    if hasattr(world, "sun_angle"):
        world.sun_angle = math.radians(1.2)  # softer photoreal sun disc
    if hasattr(world, "sun_shadow_filter_radius"):
        world.sun_shadow_filter_radius = 1.0
    if hasattr(world, "sun_shadow_maximum_resolution"):
        world.sun_shadow_maximum_resolution = 0.001
    # Soften / ensure HDRI strength not crushed
    if world.use_nodes:
        for n in world.node_tree.nodes:
            if n.type == "BACKGROUND":
                # Don't override artistic strengths wildly; floor for visibility
                n.inputs["Strength"].default_value = max(0.35, min(1.35, n.inputs["Strength"].default_value))


def configure_camera(cam: bpy.types.Object, lens: float, fstop: float):
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
    d.passepartout_alpha = 0.75
    d.dof.use_dof = True
    d.dof.aperture_fstop = fstop
    d.dof.aperture_blades = 6
    d.dof.aperture_rotation = 0.0
    d.dof.aperture_ratio = 1.0
    # Slightly tighter focus for crisp subject
    if hasattr(d.dof, "focus_distance") and not d.dof.focus_object:
        d.dof.focus_distance = max(1.0, d.dof.focus_distance)


def configure_lights(sc: bpy.types.Scene):
    for ob in sc.objects:
        if ob.type != "LIGHT":
            continue
        L = ob.data
        # Soft area defaults
        if L.type == "AREA":
            if L.size < 1.0:
                L.size = max(L.size, 2.0)
            if hasattr(L, "spread"):
                L.spread = math.radians(180)
        if L.type == "SUN":
            L.angle = math.radians(1.5)
            if L.energy > 8:
                L.energy = 5.0
        # Shadow quality on light
        if hasattr(L, "use_shadow"):
            L.use_shadow = True
        if hasattr(L, "use_contact_shadow"):
            L.use_contact_shadow = True
            if hasattr(L, "contact_shadow_distance"):
                L.contact_shadow_distance = 0.2
            if hasattr(L, "contact_shadow_thickness"):
                L.contact_shadow_thickness = 0.02
        if hasattr(L, "shadow_soft_size") and L.type == "POINT":
            L.shadow_soft_size = 0.15


def sharpen_textures():
    """Crisp image sampling for photoplates / Canva assets."""
    n = 0
    for img in bpy.data.images:
        if img.source not in {"FILE", "SEQUENCE"}:
            continue
        # Keep HDRIs as-is for lighting; sharpen LDR plates
        name = (img.filepath or img.name).lower()
        if name.endswith((".hdr", ".exr")):
            if hasattr(img, "colorspace_settings"):
                # HDR usually Non-Color or Linear — don't force sRGB
                pass
            continue
        if hasattr(img, "use_interpolation"):
            pass
        # Texture nodes use image settings
        if hasattr(img, "colorspace_settings"):
            # Most PNG plates are sRGB
            try:
                img.colorspace_settings.name = "sRGB"
            except TypeError:
                pass
        n += 1
    # Material texture nodes: Smart interpolation where available
    for mat in bpy.data.materials:
        if not mat.use_nodes:
            continue
        for node in mat.node_tree.nodes:
            if node.type == "TEX_IMAGE" and node.image:
                if hasattr(node, "interpolation"):
                    node.interpolation = "Smart"
                if hasattr(node, "projection"):
                    node.projection = "FLAT"
    return n


def ensure_chart_lights(sc: bpy.types.Scene):
    if sc.name != "05_Beat2_Money":
        return
    if "Chart_KeyLight" not in sc.objects:
        ld = bpy.data.lights.new("Chart_KeyLight_data", "AREA")
        ld.energy = 400.0
        ld.size = 5.0
        ld.color = (1.0, 0.97, 0.92)
        ob = bpy.data.objects.new("Chart_KeyLight", ld)
        sc.collection.objects.link(ob)
        ob.location = (2.5, -6.5, 4.5)
        ob.rotation_euler = (math.radians(55), 0, math.radians(25))
    else:
        sc.objects["Chart_KeyLight"].data.energy = max(300.0, sc.objects["Chart_KeyLight"].data.energy)
    if "Chart_FillLight" not in sc.objects:
        ld = bpy.data.lights.new("Chart_FillLight_data", "AREA")
        ld.energy = 120.0
        ld.size = 7.0
        ob = bpy.data.objects.new("Chart_FillLight", ld)
        sc.collection.objects.link(ob)
        ob.location = (-3.5, -5.0, 3.2)
    # Rim
    if "Chart_RimLight" not in sc.objects:
        ld = bpy.data.lights.new("Chart_RimLight_data", "AREA")
        ld.energy = 180.0
        ld.size = 3.0
        ld.color = (0.85, 0.92, 1.0)
        ob = bpy.data.objects.new("Chart_RimLight", ld)
        sc.collection.objects.link(ob)
        ob.location = (0.0, 4.0, 3.5)


def run():
    tex_n = sharpen_textures()
    report = []
    for sname, cfg in SCENE_HQ.items():
        sc = bpy.data.scenes.get(sname)
        if not sc:
            report.append({"scene": sname, "status": "missing"})
            continue
        bpy.context.window.scene = sc
        configure_eevee(sc)
        sc.view_settings.exposure = cfg["exposure"]
        configure_world_sun(sc.world)
        if sc.camera:
            configure_camera(sc.camera, cfg["lens"], cfg["fstop"])
        configure_lights(sc)
        ensure_chart_lights(sc)
        report.append({
            "scene": sname,
            "status": "ok",
            "samples": sc.eevee.taa_render_samples,
            "shadow_rays": getattr(sc.eevee, "shadow_ray_count", None),
            "rt_res": getattr(sc.eevee.ray_tracing_options, "resolution_scale", None),
            "lens": cfg["lens"],
            "fstop": cfg["fstop"],
            "exposure": cfg["exposure"],
            "view": sc.view_settings.view_transform,
            "look": sc.view_settings.look,
        })
    bpy.ops.wm.save_mainfile()
    return {"textures_touched": tex_n, "scenes": report, "saved": bpy.data.filepath}


if __name__ == "__main__":
    print(run())
