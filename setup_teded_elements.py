"""
TED-Ed style element animations for AFRICA S1 Episode 01.
Run: blender -b blend/africa_s1_master_v01.blend -P setup_teded_elements.py

Priority scenes: S05, S07, S02, S03, S09, then remaining.
Imports SVG diagrams, adds animated text labels, keyframes overlay elements.
"""
import bpy
import math
import os
import sys

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
BLEND = os.path.join(PROJECT, "blend", "africa_s1_master_v01.blend")
DIAGRAMS = os.path.join(PROJECT, "assets", "diagrams")
ICONS = os.path.join(PROJECT, "assets", "icons")
FPS = 24

SCENE_DURATIONS = {
    "01_ColdOpen": 50, "02_Context2007": 45, "03_Beat1_Hubs": 45,
    "04_Beat1_Phone": 25, "05_Beat2_Money": 45, "06_Beat2_Solar": 40,
    "07_Beat3_Gap": 50, "08_Beat3_SecondaryCity": 35, "09_Closer": 70,
    "10_EndCard": 15,
}

FONT_PATH = None  # Use Blender default; swap to Inter if installed


def clear_collection(name, scene):
    coll = bpy.data.collections.get(name)
    if coll:
        for obj in list(coll.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        return coll
    coll = bpy.data.collections.new(name)
    scene.collection.children.link(coll)
    return coll


def import_svg(filepath, collection, location=(0, 0, 0), scale=0.01):
    if not os.path.isfile(filepath):
        print(f"  SKIP missing SVG: {filepath}")
        return []
    before = set(bpy.data.objects)
    try:
        bpy.ops.import_curve.svg(filepath=filepath)
    except Exception as e:
        print(f"  SVG import failed {filepath}: {e}")
        return []
    imported = [o for o in bpy.data.objects if o not in before]
    for obj in imported:
        for c in obj.users_collection:
            c.objects.unlink(obj)
        collection.objects.link(obj)
        obj.location = location
        obj.scale = (scale, scale, scale)
    return imported


def make_text(label, collection, location, size=0.5, color=(1, 1, 1, 1)):
    curve = bpy.data.curves.new(name=label, type="FONT")
    curve.body = label
    curve.size = size
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    obj = bpy.data.objects.new(f"Text_{label[:20]}", curve)
    collection.objects.link(obj)
    obj.location = location
    mat = bpy.data.materials.new(name=f"Mat_{label[:12]}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Emission Strength"].default_value = 1.0
        bsdf.inputs["Emission Color"].default_value = color
    obj.data.materials.append(mat)
    return obj


def fade_in_out(obj, frame_in, frame_hold, frame_out, prop="scale"):
    obj.scale = (0.001, 0.001, 0.001)
    obj.keyframe_insert(data_path="scale", frame=1)
    obj.scale = (1, 1, 1)
    obj.keyframe_insert(data_path="scale", frame=frame_in)
    obj.keyframe_insert(data_path="scale", frame=frame_hold)
    obj.scale = (0.001, 0.001, 0.001)
    obj.keyframe_insert(data_path="scale", frame=frame_out)


def setup_s01(scene):
    """Cold Open: transaction paths overlay + Nairobi label."""
    coll = clear_collection("TEDed_Overlay", scene)
    frames = SCENE_DURATIONS["01_ColdOpen"] * FPS
    import_svg(os.path.join(DIAGRAMS, "s1_digital_paths.svg"), coll,
               location=(0, 0, 2), scale=0.005)
    txt = make_text("Nairobi", coll, (0, -8, 3), size=0.8, color=(1, 0.53, 0.36, 1))
    fade_in_out(txt, frame_in=72, frame_hold=frames - 60, frame_out=frames)
    txt2 = make_text("Silicon Savannah", coll, (0, -10, 3), size=0.6, color=(0.48, 0.42, 0.66, 1))
    fade_in_out(txt2, frame_in=frames - 60, frame_hold=frames - 10, frame_out=frames)
    print("  S01: paths overlay + labels")


def setup_s02(scene):
    """Context 2007: M-Pesa flow diagram + year/title labels."""
    coll = clear_collection("TEDed_Overlay", scene)
    frames = SCENE_DURATIONS["02_Context2007"] * FPS
    import_svg(os.path.join(DIAGRAMS, "s2_mpesa_flow.svg"), coll,
               location=(0, 0, 1.5), scale=0.004)
    year = make_text("2007", coll, (-6, -6, 3), size=1.2, color=(0.91, 0.52, 0.36, 1))
    fade_in_out(year, frame_in=60, frame_hold=frames - 30, frame_out=frames)
    title = make_text("M-PESA", coll, (0, 4, 3), size=0.9, color=(0.1, 0.1, 0.18, 1))
    fade_in_out(title, frame_in=120, frame_hold=frames - 30, frame_out=frames)
    print("  S02: M-Pesa flow + labels")


def setup_s03(scene):
    """Beat 1 Hubs: hub enumeration cards."""
    coll = clear_collection("TEDed_Overlay", scene)
    frames = SCENE_DURATIONS["03_Beat1_Hubs"] * FPS
    import_svg(os.path.join(DIAGRAMS, "s3_hub_cards.svg"), coll,
               location=(0, 2, 1.5), scale=0.003)
    cards = [
        ("iHub 2010", (-4, 0, 2.5), 240),
        ("Andela", (0, 0, 2.5), 540),
        ("NaiLab", (4, 0, 2.5), 720),
    ]
    for label, loc, fin in cards:
        t = make_text(label, coll, loc, size=0.35, color=(0.3, 0.69, 0.31, 1))
        fade_in_out(t, frame_in=fin, frame_hold=frames - 30, frame_out=frames)
    print("  S03: hub cards stagger")


def setup_s04(scene):
    """Beat 1 Phone: Mobile-First label."""
    coll = clear_collection("TEDed_Overlay", scene)
    frames = SCENE_DURATIONS["04_Beat1_Phone"] * FPS
    txt = make_text("Mobile-First", coll, (0, -5, 2), size=0.6, color=(1, 1, 1, 1))
    fade_in_out(txt, frame_in=360, frame_hold=frames - 20, frame_out=frames)
    print("  S04: Mobile-First label")


def setup_s05(scene):
    """Beat 2 Money: $984M counter + 82% callout."""
    coll = clear_collection("TEDed_Overlay", scene)
    frames = SCENE_DURATIONS["05_Beat2_Money"] * FPS
    stat = make_text("$984M", coll, (0, 3, 4), size=1.0, color=(0, 0.9, 0.46, 1))
    fade_in_out(stat, frame_in=180, frame_hold=frames - 60, frame_out=frames)
    pct = make_text("82%", coll, (3, 1, 4), size=0.8, color=(1, 0.42, 0.21, 1))
    fade_in_out(pct, frame_in=780, frame_hold=frames - 30, frame_out=frames)
    for label, loc, fin in [("Fintech", (-3, -1, 3), 360), ("Climate/Energy", (3, -1, 3), 540)]:
        t = make_text(label, coll, loc, size=0.3, color=(0.8, 0.8, 0.8, 1))
        fade_in_out(t, frame_in=fin, frame_hold=frames - 30, frame_out=frames)
    print("  S05: chart stats + sector labels")


def setup_s06(scene):
    """Beat 2 Solar: Pay-As-You-Go label + company tags."""
    coll = clear_collection("TEDed_Overlay", scene)
    frames = SCENE_DURATIONS["06_Beat2_Solar"] * FPS
    import_svg(os.path.join(ICONS, "icon_solar.svg"), coll, location=(-4, 0, 2), scale=0.05)
    title = make_text("Pay-As-You-Go Solar", coll, (0, 4, 3), size=0.5, color=(1, 0.84, 0.31, 1))
    fade_in_out(title, frame_in=600, frame_hold=frames - 30, frame_out=frames)
    companies = [("d.light", -5, 120), ("Sun King", -2, 200), ("M-KOPA", 1, 280), ("BURN", 4, 360)]
    for name, x, fin in companies:
        t = make_text(name, coll, (x, -6, 2), size=0.25, color=(0.7, 0.7, 0.7, 1))
        fade_in_out(t, frame_in=fin, frame_hold=frames - 20, frame_out=frames)
    print("  S06: solar label + company tags")


def setup_s07(scene):
    """Beat 3 Gap: 97% stat slam + city markers."""
    coll = clear_collection("TEDed_Overlay", scene)
    frames = SCENE_DURATIONS["07_Beat3_Gap"] * FPS
    stat = make_text("97%", coll, (0, 0, 4), size=1.5, color=(1, 0.42, 0.21, 1))
    fade_in_out(stat, frame_in=360, frame_hold=420, frame_out=frames - 60)
    nairobi = make_text("Nairobi", coll, (0, 2, 3), size=0.4, color=(0, 0.9, 0.46, 1))
    fade_in_out(nairobi, frame_in=72, frame_hold=300, frame_out=360)
    cities = [("Mombasa", -4, -3, 660), ("Kisumu", 4, -2, 720),
              ("Eldoret", -2, 3, 780), ("Nakuru", 3, 2, 840)]
    for name, x, y, fin in cities:
        t = make_text(name, coll, (x, y, 2.5), size=0.2, color=(0.47, 0.56, 0.61, 1))
        fade_in_out(t, frame_in=fin, frame_hold=fin + 60, frame_out=fin + 120)
    print("  S07: 97% stat + city markers")


def setup_s08(scene):
    """Beat 3 Secondary: Pre-seed gap label."""
    coll = clear_collection("TEDed_Overlay", scene)
    frames = SCENE_DURATIONS["08_Beat3_SecondaryCity"] * FPS
    txt = make_text("Pre-seed gap", coll, (0, -5, 2), size=0.5, color=(0.47, 0.56, 0.61, 1))
    fade_in_out(txt, frame_in=300, frame_hold=frames - 30, frame_out=frames)
    print("  S08: pre-seed gap label")


def setup_s09(scene):
    """Closer: Forecast text + city tags."""
    coll = clear_collection("TEDed_Overlay", scene)
    frames = SCENE_DURATIONS["09_Closer"] * FPS
    logos = [("Microsoft ADC", -5, 4, 120), ("Visa Studio", 5, 4, 300), ("UN Agencies", 0, 5, 540)]
    for name, x, y, fin in logos:
        t = make_text(name, coll, (x, y, 3), size=0.35, color=(0.1, 0.14, 0.49, 1))
        fade_in_out(t, frame_in=fin, frame_hold=fin + 120, frame_out=fin + 180)
    forecast = make_text("Forecast", coll, (0, 0, 4), size=1.0, color=(1, 0.84, 0.31, 1))
    fade_in_out(forecast, frame_in=1200, frame_hold=frames - 60, frame_out=frames)
    cities = make_text("Lagos · Kigali · Accra", coll, (0, -6, 2.5), size=0.3, color=(0.7, 0.7, 0.7, 1))
    fade_in_out(cities, frame_in=1500, frame_hold=frames - 30, frame_out=frames)
    print("  S09: forecast + logo labels")


def setup_s10(scene):
    """End Card: Season 1 subtitle."""
    coll = clear_collection("TEDed_Overlay", scene)
    frames = SCENE_DURATIONS["10_EndCard"] * FPS
    txt = make_text("Season 1", coll, (0, -3, 2), size=0.5, color=(0.7, 0.7, 0.7, 1))
    fade_in_out(txt, frame_in=60, frame_hold=frames - 30, frame_out=frames)
    print("  S10: Season 1 subtitle")


SETUP_FUNCS = {
    "01_ColdOpen": setup_s01,
    "02_Context2007": setup_s02,
    "03_Beat1_Hubs": setup_s03,
    "04_Beat1_Phone": setup_s04,
    "05_Beat2_Money": setup_s05,
    "06_Beat2_Solar": setup_s06,
    "07_Beat3_Gap": setup_s07,
    "08_Beat3_SecondaryCity": setup_s08,
    "09_Closer": setup_s09,
    "10_EndCard": setup_s10,
}

PRIORITY = ["05_Beat2_Money", "07_Beat3_Gap", "02_Context2007",
            "03_Beat1_Hubs", "09_Closer", "01_ColdOpen",
            "04_Beat1_Phone", "06_Beat2_Solar", "08_Beat3_SecondaryCity", "10_EndCard"]


def main():
    print("=== TED-Ed Element Animation Setup ===")
    for sname in PRIORITY:
        if sname not in bpy.data.scenes:
            print(f"  SKIP missing scene: {sname}")
            continue
        sc = bpy.data.scenes[sname]
        bpy.context.window.scene = sc
        frames = SCENE_DURATIONS[sname] * FPS
        sc.frame_start = 1
        sc.frame_end = frames
        SETUP_FUNCS[sname](sc)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print(f"Saved: {BLEND}")
    print("=== DONE ===")


if __name__ == "__main__":
    main()
