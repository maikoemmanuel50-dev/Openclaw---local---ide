"""
Soft-Pop Photoreal Hybrid setup for africa_s1_master_v01.blend
Inspired by Fern / Imperial (faceless 3D cinematic) + LEMMiNO (photo Ken Burns).

Run inside Blender 5.1.2 (MCP execute_blender_code or -P).
"""
from __future__ import annotations

import os
import math
import bpy
from mathutils import Color

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
HDRI_DIR = os.path.join(PROJECT, "assets", "hdri")

# Locked palette
HERO = (1.0, 0.835, 0.310)          # #FFD54F
MUSTARD = (0.851, 0.643, 0.255)     # #D9A441 bg wash
INDIGO = (0.180, 0.227, 0.314)      # #2E3A50
TERRACOTTA = (0.757, 0.333, 0.180)  # #C1552E
PLUM = (0.490, 0.180, 0.231)        # #7D2E3B
CREAM = (0.945, 0.894, 0.784)       # #F1E4C8
CHARCOAL = (0.149, 0.125, 0.098)    # #262019

CHAPTER = {
    "01_ColdOpen": {"field": CREAM, "accent": MUSTARD, "hdri": "aarfontein_dusk_2k.hdr", "strength": 0.85},
    "02_Context2007": {"field": CREAM, "accent": TERRACOTTA, "hdri": "aarfontein_dusk_2k.hdr", "strength": 0.75},
    "03_Beat1_Hubs": {"field": INDIGO, "accent": CREAM, "hdri": "kloofendal_48d_partly_cloudy_puresky_2k.hdr", "strength": 1.0},
    "04_Beat1_Phone": {"field": INDIGO, "accent": CREAM, "hdri": "kloofendal_48d_partly_cloudy_puresky_2k.hdr", "strength": 0.95},
    "05_Beat2_Money": {"field": CHARCOAL, "accent": (0.0, 0.902, 0.463), "hdri": "kloofendal_48d_partly_cloudy_puresky_2k.hdr", "strength": 0.45},
    "06_Beat2_Solar": {"field": CHARCOAL, "accent": MUSTARD, "hdri": "kloofendal_48d_partly_cloudy_puresky_2k.hdr", "strength": 1.15},
    "07_Beat3_Gap": {"field": INDIGO, "accent": PLUM, "hdri": "kloofendal_48d_partly_cloudy_puresky_2k.hdr", "strength": 0.55},
    "08_Beat3_SecondaryCity": {"field": INDIGO, "accent": TERRACOTTA, "hdri": "aarfontein_dusk_2k.hdr", "strength": 0.7},
    "09_Closer": {"field": INDIGO, "accent": HERO, "hdri": "venice_sunset_2k.hdr", "strength": 0.9},
    "10_EndCard": {"field": CHARCOAL, "accent": HERO, "hdri": "venice_sunset_2k.hdr", "strength": 0.65},
}


def hex_ok(rgb):
    return (max(0.0, min(1.0, rgb[0])), max(0.0, min(1.0, rgb[1])), max(0.0, min(1.0, rgb[2])))


def ensure_mat(name: str) -> bpy.types.Material:
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat


def set_principled(mat: bpy.types.Material, *, base, roughness, metallic=0.0, emission=None, emission_strength=0.0, alpha=1.0):
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (300, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)
    bsdf.inputs["Base Color"].default_value = (*hex_ok(base), 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*hex_ok(emission), 1.0)
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission_strength
    elif emission is not None and "Emission" in bsdf.inputs:
        bsdf.inputs["Emission"].default_value = (*hex_ok(emission), 1.0)
    if alpha < 1.0 and "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = alpha
        mat.blend_method = "BLEND"
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def upgrade_image_mat(mat: bpy.types.Material, tint=None, mix=0.18):
    """Keep image texture (LEMMiNO photo plate) but soft-tint toward soft-pop field."""
    if not mat or not mat.use_nodes:
        return
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    tex = next((n for n in nodes if n.type == "TEX_IMAGE" and n.image), None)
    bsdf = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
    out = next((n for n in nodes if n.type == "OUTPUT_MATERIAL"), None)
    if not tex or not bsdf or not out:
        return
    # Soften: higher roughness, slight emission-off
    bsdf.inputs["Roughness"].default_value = min(0.92, max(0.55, bsdf.inputs["Roughness"].default_value))
    if tint is None:
        return
    mixn = nodes.get("SoftPop_Mix") or nodes.new("ShaderNodeMix")
    mixn.name = "SoftPop_Mix"
    mixn.data_type = "RGBA"
    mixn.location = (-200, 0)
    mixn.inputs["Factor"].default_value = mix
    mixn.inputs[7].default_value = (*hex_ok(tint), 1.0)  # B color in Mix RGBA
    # reconnect: tex -> mix A, tint B, mix -> base
    for link in list(bsdf.inputs["Base Color"].links):
        links.remove(link)
    links.new(tex.outputs["Color"], mixn.inputs[6])
    links.new(mixn.outputs[2], bsdf.inputs["Base Color"])


def setup_world(world: bpy.types.World, hdri_name: str, strength: float):
    path = os.path.join(HDRI_DIR, hdri_name)
    world.use_nodes = True
    nt = world.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputWorld")
    out.location = (400, 0)
    bg = nodes.new("ShaderNodeBackground")
    bg.location = (200, 0)
    bg.inputs["Strength"].default_value = strength
    env = nodes.new("ShaderNodeTexEnvironment")
    env.location = (0, 0)
    if os.path.isfile(path):
        img = bpy.data.images.load(path, check_existing=True)
        env.image = img
    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-200, 0)
    texcoord = nodes.new("ShaderNodeTexCoord")
    texcoord.location = (-400, 0)
    links.new(texcoord.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], env.inputs["Vector"])
    links.new(env.outputs["Color"], bg.inputs["Color"])
    links.new(bg.outputs["Background"], out.inputs["Surface"])

    # World sun shadows (EEVEE exterior Fern light trick)
    if hasattr(world, "use_sun_shadow"):
        world.use_sun_shadow = True
    if hasattr(world, "sun_threshold"):
        world.sun_threshold = 0.6
    if hasattr(world, "sun_angle"):
        world.sun_angle = math.radians(0.8)


def setup_eevee(sc: bpy.types.Scene):
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.fps = 24
    sc.render.film_transparent = False
    ee = sc.eevee
    if hasattr(ee, "use_raytracing"):
        ee.use_raytracing = True
    if hasattr(ee, "ray_tracing_options"):
        opts = ee.ray_tracing_options
        if hasattr(opts, "use_denoise"):
            opts.use_denoise = True
    if hasattr(ee, "taa_render_samples"):
        ee.taa_render_samples = 64
    if hasattr(ee, "use_bloom"):
        ee.use_bloom = True
        if hasattr(ee, "bloom_intensity"):
            ee.bloom_intensity = 0.04
        if hasattr(ee, "bloom_threshold"):
            ee.bloom_threshold = 0.85
    # Soft volumetric atmosphere hint via mist
    if hasattr(sc.view_layers[0], "use_pass_mist"):
        sc.view_layers[0].use_pass_mist = True
    if hasattr(sc.world, "mist_settings") if sc.world else False:
        pass
    if sc.world and hasattr(sc.world, "mist_settings"):
        sc.world.mist_settings.use_mist = True
        sc.world.mist_settings.start = 8.0
        sc.world.mist_settings.depth = 40.0


def setup_camera_dof(cam_obj: bpy.types.Object, focus_obj: bpy.types.Object | None):
    if not cam_obj or cam_obj.type != "CAMERA":
        return
    cam = cam_obj.data
    cam.dof.use_dof = True
    cam.dof.aperture_fstop = 2.8
    cam.lens = max(cam.lens, 35.0)
    if focus_obj:
        cam.dof.focus_object = focus_obj
    else:
        cam.dof.focus_distance = 6.0


def ken_burns_plane(obj: bpy.types.Object, frames: int):
    """LEMMiNO still treatment: subtle scale breathe on photo planes."""
    if not obj or obj.type != "MESH":
        return
    if "Background" not in obj.name and "Foreground" not in obj.name and "Midground" not in obj.name:
        return
    # Clear prior SoftPop KB keys on scale only if tagged
    obj["softpop_kb"] = 1
    base = obj.scale.copy()
    obj.scale = base
    obj.keyframe_insert(data_path="scale", frame=1)
    obj.scale = (base.x * 1.06, base.y * 1.06, base.z)
    obj.keyframe_insert(data_path="scale", frame=max(frames, 24))
    # Ease (Blender 5.x actions use layered strips; fall back safely)
    ad = obj.animation_data
    if not ad or not ad.action:
        return
    action = ad.action
    fcurves = getattr(action, "fcurves", None)
    if fcurves is None and hasattr(action, "layers"):
        # Blender 5 layered action — iterate channelbags if present
        try:
            for layer in action.layers:
                for strip in layer.strips:
                    bag = getattr(strip, "channelbag", None)
                    if bag and hasattr(bag, "fcurves"):
                        fcurves = bag.fcurves
                        break
                if fcurves:
                    break
        except Exception:
            fcurves = None
    if not fcurves:
        return
    for fc in fcurves:
        if fc.data_path == "scale":
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.easing = "EASE_IN_OUT"


def find_ball(sc: bpy.types.Scene):
    for o in sc.objects:
        if "Sasa_Ball" in o.name or "Yellow" in o.name:
            return o
    return None


def run():
    # Hero ball material — graphic Fern accent, not chrome photoreal
    ball_mat = ensure_mat("SasaYellow")
    set_principled(
        ball_mat,
        base=HERO,
        roughness=0.35,
        metallic=0.05,
        emission=HERO,
        emission_strength=0.35,
    )

    # Soft field mats
    set_principled(ensure_mat("SoftPop_Field_Indigo"), base=INDIGO, roughness=0.95)
    set_principled(ensure_mat("SoftPop_Field_Cream"), base=CREAM, roughness=0.92)
    set_principled(ensure_mat("SoftPop_Field_Charcoal"), base=CHARCOAL, roughness=0.96)
    set_principled(ensure_mat("SoftPop_YB_Body"), base=CHARCOAL, roughness=0.88)

    report = []
    for sname, cfg in CHAPTER.items():
        sc = bpy.data.scenes.get(sname)
        if not sc:
            report.append({"scene": sname, "status": "missing"})
            continue
        bpy.context.window.scene = sc
        setup_eevee(sc)

        # World / HDRI
        wname = sc.world.name if sc.world else f"W_{sname[:2]}"
        world = sc.world or bpy.data.worlds.new(wname)
        sc.world = world
        setup_world(world, cfg["hdri"], cfg["strength"])

        ball = find_ball(sc)
        if sc.camera:
            setup_camera_dof(sc.camera, ball)

        # Materials on planes
        for obj in sc.objects:
            if obj.type != "MESH":
                continue
            if "Sasa_Ball" in obj.name:
                if obj.data.materials:
                    obj.data.materials[0] = ball_mat
                else:
                    obj.data.materials.append(ball_mat)
                continue
            if not obj.data.materials:
                continue
            mat = obj.data.materials[0]
            if mat and mat.name.startswith("M_") and any(
                k in obj.name for k in ("Background", "Foreground", "Midground")
            ):
                # Photo plate soft tint (LEMMiNO)
                upgrade_image_mat(mat, tint=cfg["field"], mix=0.14)
            elif mat and mat.name.startswith("Base_"):
                set_principled(mat, base=cfg["field"], roughness=0.94)

            ken_burns_plane(obj, sc.frame_end)

        # Chart floor soft charcoal in S05
        if sname == "05_Beat2_Money":
            floor = sc.objects.get("Chart_Floor")
            if floor and floor.data.materials:
                set_principled(floor.data.materials[0], base=CHARCOAL, roughness=0.9)

        report.append({
            "scene": sname,
            "status": "ok",
            "hdri": cfg["hdri"],
            "strength": cfg["strength"],
            "ball": ball.name if ball else None,
            "dof": bool(sc.camera.data.dof.use_dof) if sc.camera else False,
            "raytracing": getattr(sc.eevee, "use_raytracing", None),
        })

    bpy.ops.wm.save_mainfile()
    return {"saved": bpy.data.filepath, "scenes": report}


if __name__ == "__main__":
    print(run())
