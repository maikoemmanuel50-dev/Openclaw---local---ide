"""
Cold Open redesign (user 2026-08-13):
  - Only matatu plate + background / HDRI frame-to-frame transitions
  - Hide skyline FG clutter / YB / midground
  - At 30s (frame 720 @ 24fps): Africa slide whip-in + settle into frame
  - Sharpen: disable DOF/bloom, Closest/Cubic texture filter, film filter 1.0

Run:
  blender -b blend/africa_s1_master_v01.blend -P setup_coldopen_matatu_africa.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
SCENE = "01_ColdOpen"
MATATU = PROJECT / "assets" / "canva" / "kinetic" / "graded_1080" / "k01_matatu_street_1080.png"
MATATU_FALLBACK = PROJECT / "assets" / "canva" / "s1_matatu_silhouettes.png"
AFRICA = PROJECT / "assets" / "canva" / "kinetic" / "hq" / "pr_s10_africa_title_alpha.png"
AFRICA_FALLBACK = PROJECT / "assets" / "canva" / "s10_africa_logo.png"
HDRI_A = PROJECT / "assets" / "hdri" / "aarfontein_dusk_2k.hdr"
HDRI_B = PROJECT / "assets" / "hdri" / "kloofendal_48d_partly_cloudy_puresky_2k.hdr"
REPORT = PROJECT / "renders" / "quality" / "coldopen_matatu_africa_report.json"

FPS = 24
AFRICA_IN = 30 * FPS  # frame 720
WHIP = 10  # high-speed transition frames


def clear_object_animation(obj: bpy.types.Object):
    if obj.animation_data:
        obj.animation_data_clear()


def load_image(path: Path, name: str) -> bpy.types.Image:
    img = bpy.data.images.get(name)
    if img is None:
        img = bpy.data.images.load(str(path), check_existing=True)
        img.name = name
    else:
        img.filepath = str(path)
        try:
            img.reload()
        except Exception:
            pass
    try:
        img.colorspace_settings.name = "sRGB"
    except Exception:
        pass
    return img


def ensure_image_mat(name: str, img: bpy.types.Image, alpha_blend: bool = True) -> bpy.types.Material:
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (400, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (150, 0)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.location = (-200, 0)
    tex.image = img
    try:
        tex.interpolation = "Cubic"
    except Exception:
        pass
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if "Alpha" in tex.outputs and "Alpha" in bsdf.inputs:
        nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    try:
        bsdf.inputs["Roughness"].default_value = 1.0
        bsdf.inputs["Specular IOR Level"].default_value = 0.0
    except Exception:
        pass
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if alpha_blend:
        mat.blend_method = "HASHED" if hasattr(mat, "blend_method") else getattr(mat, "blend_method", "OPAQUE")
        try:
            mat.blend_method = "BLEND"
        except Exception:
            pass
        try:
            mat.surface_render_method = "BLENDED"
        except Exception:
            pass
        try:
            mat.use_backface_culling = False
        except Exception:
            pass
    return mat


def hide_non_essential(sc: bpy.types.Scene) -> list[str]:
    keep = {
        "Main_Camera.001",
        "CAM_RIG_01_ColdOpen",
        "CAM_AIM_01_ColdOpen",
        "Background_Plane.001",
        "Foreground_Plane.001",
        "S01_Africa_Slide",
        "S01_Matatu_Plate",
    }
    hidden = []
    for o in sc.objects:
        if o.name in keep or o.type == "CAMERA":
            continue
        # Keep world lights off for clean plate â€” documentary key softens image
        o.hide_render = True
        try:
            o.hide_viewport = True
        except Exception:
            pass
        hidden.append(o.name)
    return hidden


def setup_world_hdri_transitions(sc: bpy.types.Scene) -> dict:
    """Hard plate switches between HDRI A/B at beat frames + slow env rotation."""
    world = sc.world or bpy.data.worlds.new("World_01_ColdOpen")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    if world.animation_data:
        world.animation_data_clear()
    if nt.animation_data:
        nt.animation_data_clear()
    nt.nodes.clear()
    nt.links.clear()

    out = nt.nodes.new("ShaderNodeOutputWorld")
    out.location = (500, 0)
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.location = (280, 0)
    bg.inputs["Strength"].default_value = 0.95
    mix_rgb = nt.nodes.new("ShaderNodeMix")
    mix_rgb.data_type = "RGBA"
    mix_rgb.location = (60, 0)
    tex_a = nt.nodes.new("ShaderNodeTexEnvironment")
    tex_a.location = (-280, 120)
    tex_b = nt.nodes.new("ShaderNodeTexEnvironment")
    tex_b.location = (-280, -120)
    map_n = nt.nodes.new("ShaderNodeMapping")
    map_n.location = (-520, 0)
    coord = nt.nodes.new("ShaderNodeTexCoord")
    coord.location = (-720, 0)

    img_a = load_image(HDRI_A, "HDRI_S01_A")
    img_b = load_image(HDRI_B, "HDRI_S01_B")
    for im in (img_a, img_b):
        try:
            im.colorspace_settings.name = "Linear Rec.709"
        except Exception:
            pass
    tex_a.image = img_a
    tex_b.image = img_b

    nt.links.new(coord.outputs["Generated"], map_n.inputs["Vector"])
    nt.links.new(map_n.outputs["Vector"], tex_a.inputs["Vector"])
    nt.links.new(map_n.outputs["Vector"], tex_b.inputs["Vector"])
    # Blender 4+/5 Mix RGBA sockets
    a_in = mix_rgb.inputs.get("A") or mix_rgb.inputs[6]
    b_in = mix_rgb.inputs.get("B") or mix_rgb.inputs[7]
    res = mix_rgb.outputs.get("Result") or mix_rgb.outputs[2]
    nt.links.new(tex_a.outputs["Color"], a_in)
    nt.links.new(tex_b.outputs["Color"], b_in)
    nt.links.new(res, bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    beats = [(1, 0.0), (240, 1.0), (480, 0.0), (720, 1.0), (960, 0.35), (1200, 0.6)]
    fac = mix_rgb.inputs["Factor"]
    for fr, val in beats:
        fac.default_value = val
        fac.keyframe_insert("default_value", frame=fr)

    map_n.inputs["Rotation"].default_value[2] = 0.0
    map_n.inputs["Rotation"].keyframe_insert("default_value", frame=1, index=2)
    map_n.inputs["Rotation"].default_value[2] = math.radians(25)
    map_n.inputs["Rotation"].keyframe_insert("default_value", frame=1200, index=2)

    # Snappy HDRI plate changes (Blender 5 layered actions may lack .fcurves)
    try:
        act = nt.animation_data.action if nt.animation_data else None
        fcurves = list(getattr(act, "fcurves", []) or [])
        for fc in fcurves:
            is_fac = "Factor" in (fc.data_path or "")
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT" if is_fac else "LINEAR"
    except Exception:
        pass

    return {"hdri_a": str(HDRI_A), "hdri_b": str(HDRI_B), "beats": beats}


def setup_matatu_plate(sc: bpy.types.Scene) -> str:
    path = MATATU if MATATU.is_file() else MATATU_FALLBACK
    img = load_image(path, "S01_Matatu_Tex")
    mat = ensure_image_mat("M_S01_Matatu_Plate", img, alpha_blend=False)
    try:
        mat.blend_method = "OPAQUE"
    except Exception:
        pass

    bg = sc.objects.get("Background_Plane.001")
    if bg is None:
        mesh = bpy.data.meshes.new("S01_Matatu_Mesh")
        bg = bpy.data.objects.new("Background_Plane.001", mesh)
        sc.collection.objects.link(bg)
        # simple plane via ops needs context â€” use primitive verts
        import bmesh
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0)
        bm.to_mesh(mesh)
        bm.free()

    clear_object_animation(bg)
    bg.hide_render = False
    bg.hide_viewport = False
    bg.location = (0.0, 2.5, 2.4)
    bg.scale = (19.2, 10.8, 1.0)  # ~16:9 wall in front of cam
    bg.rotation_euler = (math.radians(90), 0.0, 0.0)
    if bg.data.materials:
        bg.data.materials[0] = mat
    else:
        bg.data.materials.append(mat)

    # Soft push: scale in slightly over first 30s then hold for Africa
    bg.scale = (20.4, 11.5, 1.0)
    bg.keyframe_insert("scale", frame=1)
    bg.scale = (19.2, 10.8, 1.0)
    bg.keyframe_insert("scale", frame=AFRICA_IN)

    # Hide old FG silhouette plane (user: matatu texture only)
    fg = sc.objects.get("Foreground_Plane.001")
    if fg:
        fg.hide_render = True
        fg.hide_viewport = True

    return str(path)


def setup_africa_slide(sc: bpy.types.Scene) -> str:
    path = AFRICA if AFRICA.is_file() else AFRICA_FALLBACK
    img = load_image(path, "S01_Africa_Tex")
    mat = ensure_image_mat("M_S01_Africa_Slide", img, alpha_blend=True)

    obj = sc.objects.get("S01_Africa_Slide")
    if obj is None:
        mesh = bpy.data.meshes.new("S01_Africa_Mesh")
        import bmesh
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0)
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new("S01_Africa_Slide", mesh)
        sc.collection.objects.link(obj)
    clear_object_animation(obj)
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    obj.hide_render = False
    obj.hide_viewport = False
    obj.rotation_euler = (math.radians(90), 0.0, 0.0)

    # Start off-frame: large, skewed, right side â€” whip into center
    start = AFRICA_IN
    end = AFRICA_IN + WHIP
    settle = AFRICA_IN + WHIP + 18

    # Hidden before 30s
    obj.hide_render = True
    obj.keyframe_insert("hide_render", frame=start - 1)
    obj.hide_render = False
    obj.keyframe_insert("hide_render", frame=start)

    obj.location = (14.0, -1.0, 2.4)
    obj.scale = (28.0, 16.0, 1.0)
    obj.rotation_euler = (math.radians(90), math.radians(-35), math.radians(18))
    obj.keyframe_insert("location", frame=start)
    obj.keyframe_insert("scale", frame=start)
    obj.keyframe_insert("rotation_euler", frame=start)

    # High-speed transit into frame
    obj.location = (0.0, -1.5, 2.4)
    obj.scale = (12.0, 6.75, 1.0)
    obj.rotation_euler = (math.radians(90), 0.0, 0.0)
    obj.keyframe_insert("location", frame=end)
    obj.keyframe_insert("scale", frame=end)
    obj.keyframe_insert("rotation_euler", frame=end)

    # Settle / entry into composition (slight push back)
    obj.location = (0.0, -0.8, 2.35)
    obj.scale = (10.5, 5.9, 1.0)
    obj.keyframe_insert("location", frame=settle)
    obj.keyframe_insert("scale", frame=settle)

    # Hold through end
    obj.keyframe_insert("location", frame=sc.frame_end)
    obj.keyframe_insert("scale", frame=sc.frame_end)

    if obj.animation_data and obj.animation_data.action:
        try:
            fcurves = list(obj.animation_data.action.fcurves)
        except Exception:
            fcurves = []
        for fc in fcurves:
            for kp in fc.keyframe_points:
                if start <= kp.co.x <= end:
                    kp.interpolation = "LINEAR"
                else:
                    kp.interpolation = "BEZIER"
                    try:
                        kp.handle_left_type = "AUTO_CLAMPED"
                        kp.handle_right_type = "AUTO_CLAMPED"
                    except Exception:
                        pass

    return str(path)


def sharpen_camera_and_eevee(sc: bpy.types.Scene) -> dict:
    """Main soft-image fixes for flat plates."""
    notes = {}
    if sc.camera and sc.camera.data:
        sc.camera.data.dof.use_dof = False
        notes["dof"] = False
        sc.camera.data.lens = 35.0
    ee = sc.eevee
    if hasattr(ee, "use_bloom"):
        ee.use_bloom = False
        notes["bloom"] = False
    if hasattr(ee, "use_motion_blur"):
        ee.use_motion_blur = False
        notes["motion_blur"] = False
    if hasattr(sc.render, "use_motion_blur"):
        sc.render.use_motion_blur = False
    if hasattr(sc.render, "filter_size"):
        sc.render.filter_size = 1.0
        notes["filter_size"] = 1.0
    if hasattr(ee, "taa_render_samples"):
        ee.taa_render_samples = 128
    if hasattr(ee, "use_raytracing"):
        ee.use_raytracing = True
    opts = getattr(ee, "ray_tracing_options", None)
    if opts and hasattr(opts, "resolution_scale"):
        opts.resolution_scale = "1"
        notes["rt_scale"] = "1"
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.resolution_percentage = 100
    sc.render.engine = "BLENDER_EEVEE"
    notes["engine"] = "BLENDER_EEVEE"
    return notes


def main():
    sc = bpy.data.scenes.get(SCENE)
    if not sc:
        raise RuntimeError(f"Missing scene {SCENE}")
    bpy.context.window.scene = sc if bpy.context.window else sc

    matatu = setup_matatu_plate(sc)
    hdri = setup_world_hdri_transitions(sc)
    africa = setup_africa_slide(sc)
    hidden = hide_non_essential(sc)
    sharp = sharpen_camera_and_eevee(sc)

    # Ensure Africa + matatu visible flags after hide pass
    for name in ("Background_Plane.001", "S01_Africa_Slide"):
        o = sc.objects.get(name)
        if o:
            if name == "S01_Africa_Slide":
                # visibility driven by keyframes; ensure object exists
                pass
            else:
                o.hide_render = False
                o.hide_viewport = False

    blend = Path(bpy.data.filepath) if bpy.data.filepath else PROJECT / "blend" / "africa_s1_master_v01.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))

    report = {
        "scene": SCENE,
        "matatu": matatu,
        "africa": africa,
        "africa_in_frame": AFRICA_IN,
        "whip_frames": WHIP,
        "hdri": hdri,
        "hidden": hidden,
        "sharpen": sharp,
        "soft_quality_causes": [
            "Camera DOF was ON (f/4) â€” blurs flat matatu/skyline plates",
            "EEVEE bloom from soft-pop / documentary lock",
            "HDRIs are 2K (aarfontein/kloofendal *_2k.hdr) â€” soft environment detail",
            "Canva plates are 1920x1080; upscale/filtering can look mushy under DOF",
            "Remaining-scene speed path (64 samples + half RT) is for 02â€“10 only â€” re-render S01 at 128/full",
        ],
        "saved": str(blend),
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("COLDOPEN_MATATU_AFRICA_OK", json.dumps({"africa_in": AFRICA_IN, "matatu": Path(matatu).name}), flush=True)


if __name__ == "__main__":
    main()

