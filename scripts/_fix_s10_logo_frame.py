import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

sc = bpy.data.scenes["10_EndCard"]
bpy.context.window.scene = sc
cam = sc.camera
bg = next(o for o in sc.objects if "Background" in o.name and o.type == "MESH")
mid = (sc.frame_start + sc.frame_end) // 2
sc.frame_set(mid)

# Scale BG up until projected UV covers frame with margin and word likely centered
# Prefer overscan so letterforms aren't edge-clipped
for _ in range(10):
    bpy.context.view_layer.update()
    corners = [bg.matrix_world @ Vector(c) for c in bg.bound_box]
    uvs = [world_to_camera_view(sc, cam, c) for c in corners]
    xs = [u.x for u in uvs]; ys = [u.y for u in uvs]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    # Want ~15% overscan beyond frame so typography has breathing room
    # If coverage is huge already (tight crop on texture), DOLLIES BACK instead
    width = maxx - minx
    height = maxy - miny
    # Ideal: plane covers frame with overscan ~1.25-1.4 in UV space
    # Current tight crop means plane barely covers / camera too close to subject on texture
    # Pull CAM_RIG back along view axis
    break

rig = sc.objects.get("CAM_RIG_10_EndCard")
aim = sc.objects.get("CAM_AIM_10_EndCard")
# Dolly out: increase distance from aim
if rig and aim:
    direction = (rig.matrix_world.translation - aim.matrix_world.translation).normalized()
    for step in range(12):
        bpy.context.view_layer.update()
        corners = [bg.matrix_world @ Vector(c) for c in bg.bound_box]
        uvs = [world_to_camera_view(sc, cam, c) for c in corners]
        xs = [u.x for u in uvs]; ys = [u.y for u in uvs]
        # Also check how much of plane is in view - we want the plane to fill frame
        # but camera farther = more of the logo texture visible if UV mapped 1:1
        # Actually for image planes, dollying changes FOV coverage of the plane;
        # if plane is UV full-bleed logo, being closer crops the logo in frame...
        # Wait: if BG plane shows the full image and fills camera, logo fills frame.
        # Cropped letters mean either (a) plane too large / camera too close showing center crop of texture
        # or (b) DOF/framing. Looking at render - letters are large and edges cut = camera too close OR plane scale too big relative to cam.
        # Fix: scale plane DOWN so more of the image fits? No - if image is on plane and plane fills view, full image shows.
        # Unless the texture is cropped by camera being orthographic-ish close with plane larger than needed...
        # UV coverage of plane corners: if plane UV extends beyond 0-1 a lot (overscan), camera sees center of texture = cropped word.
        # So REDUCE plane scale OR move camera farther so less overscan / see more of plane edges... 
        # Farther camera = more of plane in view = more of logo visible. Dolly out.
        covers_ok = min(xs) <= -0.05 and max(xs) >= 1.05 and min(ys) <= -0.05 and max(ys) >= 1.05
        # We want milder overscan: corners near -0.08..1.08 not -0.4..1.4
        over_x = min(0 - min(xs), max(xs) - 1)
        if over_x > 0.18:
            rig.location += direction * 0.55
        elif over_x < 0.08:
            rig.location -= direction * 0.35
        else:
            break
else:
    # scale plane down toward milder overscan
    bg.scale *= 0.82

# Also widen FOV slightly for title readability
if cam.data.lens > 40:
    cam.data.lens = 40.0

bpy.context.view_layer.update()
corners = [bg.matrix_world @ Vector(c) for c in bg.bound_box]
uvs = [world_to_camera_view(sc, cam, c) for c in corners]
xs = [u.x for u in uvs]; ys = [u.y for u in uvs]
bpy.ops.wm.save_mainfile()
print({
    "lens": cam.data.lens,
    "rig": list(rig.location) if rig else None,
    "bg_scale": list(bg.scale),
    "uv": [min(xs), min(ys), max(xs), max(ys)],
})
