"""
Master fidelity lock for all 10 scenes — crisp photoreal EEVEE + texture + encode.
Run via Blender MCP or: blender -b master.blend -P setup_frame_fidelity.py
"""
from __future__ import annotations

import math
import bpy

SAMPLES = 160  # fidelity over speed (RTX 4060 overnight OK)


def lock_eevee(sc: bpy.types.Scene):
    ee = sc.eevee
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.resolution_percentage = 100
    sc.render.fps = 24
    sc.render.use_motion_blur = False
    sc.render.filter_size = 1.0  # sharper than default 1.5
    sc.render.use_border = False

    ee.taa_render_samples = SAMPLES
    if hasattr(ee, "taa_samples"):
        ee.taa_samples = 64
    ee.use_raytracing = True
    ee.use_shadows = True
    ee.shadow_ray_count = 4
    ee.shadow_step_count = 16
    if hasattr(ee, "shadow_resolution_scale"):
        ee.shadow_resolution_scale = 1.0
    try:
        ee.shadow_pool_size = "1024"
    except Exception:
        pass

    opts = ee.ray_tracing_options
    opts.resolution_scale = "1"
    opts.screen_trace_quality = 0.65
    opts.screen_trace_thickness = 1.0
    opts.trace_max_roughness = 0.8
    opts.use_denoise = True
    opts.denoise_spatial = True
    opts.denoise_temporal = True
    opts.denoise_bilateral = True

    if hasattr(ee, "use_fast_gi"):
        ee.use_fast_gi = True
        ee.fast_gi_quality = 0.6
        ee.fast_gi_ray_count = 4
        ee.fast_gi_step_count = 16
        try:
            ee.fast_gi_resolution = "1"
        except Exception:
            pass

    if hasattr(ee, "use_bokeh_jittered"):
        ee.use_bokeh_jittered = True
    if hasattr(ee, "bokeh_overblur"):
        ee.bokeh_overblur = 0.015

    if hasattr(ee, "use_bloom"):
        ee.use_bloom = True
        ee.bloom_threshold = 0.92
        ee.bloom_intensity = 0.025

    # Color fidelity — AgX consistent across episode
    sc.display_settings.display_device = "sRGB"
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        sc.view_settings.look = "None"
    sc.view_settings.gamma = 1.0

    # High-quality FFMPEG for animation encodes
    sc.render.image_settings.file_format = "FFMPEG"
    sc.render.ffmpeg.format = "MPEG4"
    sc.render.ffmpeg.codec = "H264"
    sc.render.ffmpeg.constant_rate_factor = "PERCEIVED_QUALITY"
    try:
        # Prefer visually lossless if available
        sc.render.ffmpeg.constant_rate_factor = "PERCEIVED_QUALITY"
    except Exception:
        sc.render.ffmpeg.constant_rate_factor = "HIGH"
    sc.render.ffmpeg.ffmpeg_preset = "BEST"
    sc.render.ffmpeg.gopsize = 12
    sc.render.ffmpeg.audio_codec = "NONE"
    if hasattr(sc.render.ffmpeg, "use_max_b_frames"):
        sc.render.ffmpeg.use_max_b_frames = True


def lock_camera(cam: bpy.types.Object | None):
    if not cam or cam.type != "CAMERA":
        return
    d = cam.data
    d.sensor_fit = "HORIZONTAL"
    d.sensor_width = 36.0
    d.clip_start = 0.05
    d.clip_end = 500.0
    d.show_passepartout = True
    d.dof.use_dof = True
    # Prefer deeper DOF for plate fidelity unless already set shallow for CU
    if d.dof.aperture_fstop < 4.0:
        d.dof.aperture_fstop = 4.0
    d.dof.aperture_blades = 6


def lock_textures():
    n = 0
    for img in bpy.data.images:
        if img.source != "FILE":
            continue
        fp = (img.filepath or "").lower()
        if fp.endswith((".hdr", ".exr")):
            continue
        try:
            img.colorspace_settings.name = "sRGB"
        except TypeError:
            pass
        # Reload to ensure full resolution packed/unpacked consistency
        try:
            img.reload()
        except Exception:
            pass
        n += 1
    for mat in bpy.data.materials:
        if not mat.use_nodes:
            continue
        for node in mat.node_tree.nodes:
            if node.type == "TEX_IMAGE" and node.image:
                node.interpolation = "Cubic"  # smoother than Linear for plates
                if hasattr(node, "extension"):
                    node.extension = "CLIP"
    return n


def lock_world_sun(world):
    if not world:
        return
    if hasattr(world, "use_sun_shadow"):
        world.use_sun_shadow = True
    if hasattr(world, "sun_angle"):
        world.sun_angle = math.radians(1.0)
    if hasattr(world, "sun_threshold"):
        world.sun_threshold = 0.75


def run():
    tex = lock_textures()
    report = []
    for sc in bpy.data.scenes:
        bpy.context.window.scene = sc
        lock_eevee(sc)
        lock_camera(sc.camera)
        lock_world_sun(sc.world)
        report.append({
            "scene": sc.name,
            "samples": sc.eevee.taa_render_samples,
            "filter": sc.render.filter_size,
            "rt_res": sc.eevee.ray_tracing_options.resolution_scale,
            "crf": sc.render.ffmpeg.constant_rate_factor,
            "preset": sc.render.ffmpeg.ffmpeg_preset,
            "view": sc.view_settings.view_transform,
            "look": sc.view_settings.look,
        })
    bpy.ops.wm.save_mainfile()
    return {"textures": tex, "scenes": report, "saved": bpy.data.filepath}


if __name__ == "__main__":
    print(run())
