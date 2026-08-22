"""
Polish TED-Ed open30 sidecar: PBR textures, beat drivers, emission pulse.
CPU-only; does not touch master blend.

Run:
  blender.exe -b blend/africa_s1_teded_open30.blend -P polish_open30_blender_textures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import bpy

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
REPORT = PROJECT / "renders" / "quality" / "open30_blender_polish_report.json"

YELLOW = (1.0, 0.835, 0.310, 1.0)
BG = (0.026, 0.018, 0.006, 1.0)


def ensure_mat(name: str, base_color, emission_strength=0.0, roughness=0.45):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Emission Color"].default_value = base_color
    bsdf.inputs["Emission Strength"].default_value = emission_strength
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def polish_materials():
    touched = []
    for mat in bpy.data.materials:
        if not mat.use_nodes:
            continue
        for node in mat.node_tree.nodes:
            if node.type != "BSDF_PRincipLED":
                continue
            if "Yellow" in mat.name or "yellow" in mat.name.lower():
                node.inputs["Roughness"].default_value = 0.38
                node.inputs["Emission Strength"].default_value = 0.15
                touched.append(mat.name)
            elif "BG" in mat.name or "bg" in mat.name.lower():
                node.inputs["Roughness"].default_value = 0.85
                touched.append(mat.name)
    ensure_mat("M_YellowHero", YELLOW, emission_strength=0.22, roughness=0.35)
    ensure_mat("M_BG", BG, emission_strength=0.0, roughness=0.9)
    return touched


def pulse_ctrl_wrangle():
    ctrl = bpy.data.objects.get("CTRL")
    if ctrl is None:
        return False
    if "wrangle" not in ctrl:
        ctrl["wrangle"] = 0.0
    if ctrl.animation_data is None:
        ctrl.animation_data_create()
    action = ctrl.animation_data.action
    if action is None:
        action = bpy.data.actions.new("CTRL_wrangle_pulse")
        ctrl.animation_data.action = action
    # pulse on stat beats
    keys = [(241, 0.0), (280, 1.0), (324, 0.2), (325, 0.0), (360, 1.0), (396, 0.0), (553, 0.8), (648, 0.0)]
    fc = action.fcurves.find('["wrangle"]') if hasattr(action, "fcurves") else None
    if fc is None and hasattr(action, "fcurves"):
        fc = action.fcurves.new(data_path='["wrangle"]')
    if fc:
        fc.keyframe_points.clear()
        for fr, val in keys:
            fc.keyframe_points.insert(fr, val)
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
    return True


def assign_image_planes():
    png_dir = PROJECT / "assets" / "canva" / "kinetic" / "infographics" / "open30"
    assigned = []
    for obj in bpy.data.objects:
        if obj.type != "MESH" or not obj.name.startswith("BEAT_"):
            continue
        beat_num = obj.name.split("_")[-1][:2]
        png = png_dir / f"open30_{beat_num}_stat.png"
        for suffix in ("stat", "label", "flow", "paths", "compare", "title", "bridge"):
            p = png_dir / f"open30_{beat_num}_{suffix}.png"
            if p.is_file():
                png = p
                break
        if not png.is_file():
            continue
        img = bpy.data.images.load(str(png), check_existing=True)
        if not obj.data.materials:
            obj.data.materials.append(bpy.data.materials.new(f"M_{obj.name}"))
        mat = obj.data.materials[0]
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        em = nt.nodes.new("ShaderNodeEmission")
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        tex.interpolation = "Linear"
        nt.links.new(tex.outputs["Color"], em.inputs["Color"])
        em.inputs["Strength"].default_value = 1.0
        nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
        assigned.append(str(png.name))
    return assigned


def main():
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 64
    if hasattr(scene, "view_settings"):
        scene.view_settings.view_transform = "AgX"
    touched = polish_materials()
    pulsed = pulse_ctrl_wrangle()
    planes = assign_image_planes()
    bpy.ops.wm.save_mainfile()
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps({"materials": touched, "pulse": pulsed, "image_planes": planes}, indent=2),
        encoding="utf-8",
    )
    print("POLISHED", REPORT)


if __name__ == "__main__":
    main()
