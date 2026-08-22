"""Apply Africa alpha whip fix to 01_ColdOpen (Blender 5.1). CPU-safe setup."""
import math
from pathlib import Path
import bpy

ALPHA = r"C:/Users/HP/OneDrive/The Vault/Africa Season 1/assets/canva/kinetic/hq/pr_s10_africa_title_alpha.png"
SCENE = "01_ColdOpen"
AFRICA_IN = 720
WHIP = 10

sc = bpy.data.scenes.get(SCENE) or bpy.context.scene
bpy.context.window.scene = sc if hasattr(bpy.context, "window") else None

img = bpy.data.images.load(ALPHA, check_existing=True)
img.name = "S01_Africa_Tex_Alpha"
try:
    img.colorspace_settings.name = "sRGB"
except Exception:
    pass
img.alpha_mode = "STRAIGHT"

mat = bpy.data.materials.get("M_S01_Africa_Slide") or bpy.data.materials.new("M_S01_Africa_Slide")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputMaterial")
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
tex = nt.nodes.new("ShaderNodeTexImage")
tex.image = img
tex.interpolation = "Cubic"
nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
try:
    bsdf.inputs["Emission Color"].default_value = (1.0, 0.85, 0.35, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 2.5
except Exception:
    pass
bsdf.inputs["Roughness"].default_value = 0.55
nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
try:
    mat.blend_method = "BLEND"
except Exception:
    pass
try:
    mat.surface_render_method = "BLENDED"
except Exception:
    pass

obj = sc.objects.get("S01_Africa_Slide")
if obj is None:
    raise SystemExit("S01_Africa_Slide missing — run setup_coldopen_matatu_africa.py first")
if obj.animation_data:
    obj.animation_data_clear()
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)

start, end, settle = AFRICA_IN, AFRICA_IN + WHIP, AFRICA_IN + WHIP + 18
obj.hide_render = True
obj.keyframe_insert("hide_render", frame=start - 1)
obj.hide_render = False
obj.keyframe_insert("hide_render", frame=start)

# Whip: enter from right oversized → settle readable wordmark over plate
obj.location = (10.0, -1.2, 2.4)
obj.scale = (16.0, 9.0, 1.0)
obj.rotation_euler = (math.radians(90), math.radians(-28), math.radians(12))
for dp in ("location", "scale", "rotation_euler"):
    obj.keyframe_insert(dp, frame=start)

obj.location = (0.0, -1.2, 2.4)
obj.scale = (9.6, 5.4, 1.0)
obj.rotation_euler = (math.radians(90), 0.0, 0.0)
for dp in ("location", "scale", "rotation_euler"):
    obj.keyframe_insert(dp, frame=end)

obj.location = (0.0, -0.9, 2.35)
obj.scale = (8.4, 4.7, 1.0)
obj.keyframe_insert("location", frame=settle)
obj.keyframe_insert("scale", frame=settle)
obj.keyframe_insert("location", frame=sc.frame_end)
obj.keyframe_insert("scale", frame=sc.frame_end)

# Keep matatu / BG plate visible under alpha letters
for name in ("Background_Plane.001",):
    o = sc.objects.get(name)
    if o:
        o.hide_render = False

out_blend = Path(r"C:/Users/HP/OneDrive/The Vault/Africa Season 1/blend/africa_s1_master_v01.blend")
bpy.ops.wm.save_as_mainfile(filepath=str(out_blend))
print("FIX_S01_AFRICA_ALPHA_OK", ALPHA, flush=True)
