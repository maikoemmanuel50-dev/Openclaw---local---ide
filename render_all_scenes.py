"""Batch-render all 10 Africa S1 scenes as PNG sequences via Blender CLI."""
import subprocess, sys

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
BLEND = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1\blend\africa_s1_master_v01.blend"
RENDER_ROOT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1\renders"

SCENES = [
    "01_ColdOpen", "02_Context2007", "03_Beat1_Hubs", "04_Beat1_Phone",
    "05_Beat2_Money", "06_Beat2_Solar", "07_Beat3_Gap", "08_Beat3_SecondaryCity",
    "09_Closer", "10_EndCard",
]

PY = f"""
import bpy, os
RENDER_ROOT = r"{RENDER_ROOT}"
sname = "{{SCENE}}"
sc = bpy.data.scenes[sname]
bpy.context.window.scene = sc
out_dir = os.path.join(RENDER_ROOT, sname, "anim")
os.makedirs(out_dir, exist_ok=True)
sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
sc.render.image_settings.file_format = 'PNG'
sc.frame_start = 1
sc.frame_end = 200
sc.render.filepath = os.path.join(out_dir, "frame_")
bpy.ops.render.render(animation=True)
print("DONE", sname)
"""

def main():
    scenes = sys.argv[1:] if len(sys.argv) > 1 else SCENES
    for sname in scenes:
        print(f"Rendering {sname}...")
        code = PY.replace("{{SCENE}}", sname)
        cmd = [BLENDER, "-b", BLEND, "--python-expr", code]
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(r.stdout[-500:] if r.stdout else "")
        if r.returncode != 0:
            print(f"ERROR {sname}:", r.stderr[-300:])
        else:
            print(f"OK {sname}")

if __name__ == "__main__":
    main()
