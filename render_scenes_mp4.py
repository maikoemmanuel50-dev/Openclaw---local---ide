"""Render all 10 scenes to MP4 clips (no audio).

Skip logic: skips complete clips unless AFRICA_FORCE_RERENDER=1 (full reformulation).

Quality path (post-batch, set before launch):
  AFRICA_RENDER_ENGINE=CYCLES   — honor arch-lock Cycles + OptiX/OIDN (GPU)
  AFRICA_MASTER_FRAMES=1        — PNG masters → scripts/ffmpeg_delivery_encode.py @ 10M
  AFRICA_EEVEE_SAMPLES=128      — legacy EEVEE only when AFRICA_RENDER_ENGINE=EEVEE

Default (legacy batch): EEVEE direct ~2 Mbps H.264 in Blender.
"""
from __future__ import annotations

import bpy
import os
import shutil
import subprocess
import sys

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
RENDER_DIR = os.path.join(PROJECT, "renders", "video_clips")
MASTER_DIR = os.path.join(RENDER_DIR, "masters")
ENCODE_SCRIPT = os.path.join(PROJECT, "scripts", "ffmpeg_delivery_encode.py")
FORCE = os.environ.get("AFRICA_FORCE_RERENDER", "").strip() in {"1", "true", "TRUE", "yes", "YES"}
ONLY_RAW = os.environ.get("AFRICA_ONLY_SCENES", "").strip()
ONLY = {s.strip() for s in ONLY_RAW.split(",") if s.strip()} if ONLY_RAW else set()
ENGINE = os.environ.get("AFRICA_RENDER_ENGINE", "EEVEE").strip().upper()
MASTER_FRAMES = os.environ.get("AFRICA_MASTER_FRAMES", "1").strip() in {"1", "true", "TRUE", "yes", "YES"}
DELIVERY_BITRATE = os.environ.get("AFRICA_DELIVERY_BITRATE", "10M").strip() or "10M"
SCENE_ORDER = [
    "01_ColdOpen", "02_Context2007", "03_Beat1_Hubs", "04_Beat1_Phone",
    "05_Beat2_Money", "06_Beat2_Solar", "07_Beat3_Gap", "08_Beat3_SecondaryCity",
    "09_Closer", "10_EndCard",
]
EXPECTED_SEC = {
    "01_ColdOpen": 50, "02_Context2007": 45, "03_Beat1_Hubs": 45,
    "04_Beat1_Phone": 25, "05_Beat2_Money": 45, "06_Beat2_Solar": 40,
    "07_Beat3_Gap": 50, "08_Beat3_SecondaryCity": 35, "09_Closer": 70,
    "10_EndCard": 15,
}


def find_ffprobe():
    ff = shutil.which("ffprobe")
    if ff:
        return ff
    winget_root = os.path.join(
        os.path.expandvars(r"%LOCALAPPDATA%"),
        "Microsoft", "WinGet", "Packages",
        "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe",
    )
    if os.path.isdir(winget_root):
        for root, _, files in os.walk(winget_root):
            if "ffprobe.exe" in files:
                return os.path.join(root, "ffprobe.exe")
    return None


def clip_complete(path, min_sec):
    if not os.path.isfile(path) or os.path.getsize(path) < 200_000:
        return False
    ffprobe = find_ffprobe()
    if not ffprobe:
        return os.path.getsize(path) > min_sec * 80_000
    try:
        r = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True, timeout=30,
        )
        dur = float(r.stdout.strip())
        return dur >= min_sec - 0.5
    except Exception:
        return False


def configure_engine(sc):
    """Honor AFRICA_RENDER_ENGINE; Cycles uses arch-lock settings already in .blend."""
    if ENGINE == "CYCLES":
        sc.render.engine = "CYCLES"
        cy = sc.cycles
        try:
            cy.device = "GPU"
        except Exception:
            pass
        if hasattr(cy, "use_denoising"):
            cy.use_denoising = True
        for dn in ("OPTIX", "OPENIMAGEDENOISE"):
            try:
                cy.denoiser = dn
                break
            except Exception:
                continue
        if hasattr(cy, "samples"):
            env_samples = os.environ.get("AFRICA_CYCLES_SAMPLES", "").strip()
            if env_samples.isdigit():
                cy.samples = max(64, int(env_samples))
            else:
                # Cap runaway blend-locked 4096 for overnight/outage viability
                cy.samples = min(max(int(getattr(cy, "samples", 128) or 128), 256), 512)
        print(f"  engine=CYCLES samples={getattr(cy, 'samples', '?')} denoiser={getattr(cy, 'denoiser', '?')}", flush=True)
        return
    # Legacy EEVEE path
    sc.render.engine = "BLENDER_EEVEE"
    samples = int(os.environ.get("AFRICA_EEVEE_SAMPLES", "128"))
    rt_scale = os.environ.get("AFRICA_RT_SCALE", "1")
    if hasattr(sc.eevee, "taa_render_samples"):
        sc.eevee.taa_render_samples = samples
    if hasattr(sc.eevee, "use_raytracing"):
        sc.eevee.use_raytracing = True
    if hasattr(sc.eevee, "shadow_ray_count"):
        sc.eevee.shadow_ray_count = 4
    if hasattr(sc.eevee, "shadow_step_count"):
        sc.eevee.shadow_step_count = 12
    opts = getattr(sc.eevee, "ray_tracing_options", None)
    if opts and hasattr(opts, "resolution_scale"):
        opts.resolution_scale = str(rt_scale)
    print(f"  engine=EEVEE samples={samples}", flush=True)


def next_missing_frame(frame_dir: str, frame_start: int, frame_end: int) -> int | None:
    """Return first frame with no PNG on disk, or None if the range is complete."""
    if not frame_dir or not os.path.isdir(frame_dir):
        return frame_start
    missing = None
    for f in range(int(frame_start), int(frame_end) + 1):
        # Blender writes frame_0001.png style from filepath prefix frame_
        cand = os.path.join(frame_dir, f"frame_{f:04d}.png")
        if not os.path.isfile(cand) or os.path.getsize(cand) < 10_000:
            missing = f
            break
    return missing


def configure_output(sc, out_path: str, sname: str, use_frames: bool):
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.resolution_percentage = 100
    img = sc.render.image_settings
    if use_frames:
        img.media_type = "IMAGE" if hasattr(img, "media_type") else None
        try:
            img.file_format = "PNG"
        except TypeError:
            pass
        img.color_mode = "RGB"
        frame_root = os.path.join(MASTER_DIR, sname)
        os.makedirs(frame_root, exist_ok=True)
        if FORCE:
            for fn in os.listdir(frame_root):
                try:
                    os.remove(os.path.join(frame_root, fn))
                except OSError:
                    pass
        sc.render.filepath = os.path.join(frame_root, "frame_")
        return frame_root
    img.media_type = "VIDEO" if hasattr(img, "media_type") else None
    try:
        img.file_format = "FFMPEG"
    except TypeError:
        img.file_format = "PNG"
    ff = sc.render.ffmpeg
    ff.format = "MPEG4"
    ff.codec = "H264"
    try:
        ff.constant_rate_factor = "HIGH"
    except TypeError:
        pass
    try:
        ff.ffmpeg_preset = "GOOD"
    except TypeError:
        pass
    try:
        ff.audio_codec = "NONE"
    except TypeError:
        pass
    sc.render.filepath = out_path
    return None


def encode_delivery(frame_dir: str, out_path: str) -> int:
    py = sys.executable
    cmd = [py, ENCODE_SCRIPT, frame_dir, out_path, "--bitrate", DELIVERY_BITRATE]
    print(f"  ENCODE_START {frame_dir} -> {out_path} @ {DELIVERY_BITRATE}", flush=True)
    r = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout, flush=True)
        print(r.stderr, flush=True)
    return r.returncode


def hide_yellow_ball(sc):
    if os.environ.get("AFRICA_NO_YELLOW_BALL", "").strip() not in ("1", "true", "TRUE", "yes"):
        return
    for obj in sc.objects:
        n = obj.name
        if (
            n.startswith(("Sasa_", "YB_", "YellowBall", "CTRL_Root", "CTRL_Squash", "MCH_Stretch"))
            or "Sasa_Ball" in n
            or "Sasa_Master" in n
        ):
            obj.hide_render = True


os.makedirs(RENDER_DIR, exist_ok=True)
print(f"RENDER_CONFIG engine={ENGINE} master_frames={MASTER_FRAMES and ENGINE=='CYCLES'} force={FORCE}", flush=True)

for i, sname in enumerate(SCENE_ORDER, 1):
    if ONLY and sname not in ONLY:
        print(f"[{i}/10] SKIP {sname} (AFRICA_ONLY_SCENES)", flush=True)
        continue
    out = os.path.join(RENDER_DIR, f"{sname}.mp4")
    need = EXPECTED_SEC[sname]
    use_frames = MASTER_FRAMES and ENGINE == "CYCLES"
    if (not FORCE) and clip_complete(out, need):
        if use_frames:
            meta = os.path.join(MASTER_DIR, sname, ".delivery_ok")
            if os.path.isfile(meta):
                print(f"[{i}/10] SKIP {sname} (cycles delivery ok)", flush=True)
                continue
        else:
            print(f"[{i}/10] SKIP {sname} (already rendered)", flush=True)
            continue
    if FORCE and os.path.isfile(out):
        try:
            os.remove(out)
            print(f"[{i}/10] FORCE remove stale {sname}.mp4", flush=True)
        except OSError as e:
            print(f"[{i}/10] FORCE warn could not remove {out}: {e}", flush=True)
    if FORCE:
        parent = os.path.dirname(out)
        for fn in os.listdir(parent):
            if fn.startswith(sname) and fn.lower().endswith(".mp4"):
                p = os.path.join(parent, fn)
                try:
                    os.remove(p)
                    print(f"[{i}/10] FORCE remove variant {fn}", flush=True)
                except OSError:
                    pass
    if FORCE:
        print(f"[{i}/10] FORCE render {sname}", flush=True)

    sc = bpy.data.scenes[sname]
    bpy.context.window.scene = sc
    configure_engine(sc)
    hide_yellow_ball(sc)
    frame_dir = configure_output(sc, out, sname, use_frames)
    if use_frames and frame_dir:
        miss = next_missing_frame(frame_dir, sc.frame_start, sc.frame_end)
        if miss is None:
            print(f"[{i}/10] PNG_COMPLETE {sname} — encode only", flush=True)
            if encode_delivery(frame_dir, out) != 0:
                print(f"[{i}/10] ENCODE_FAIL {sname}", flush=True)
                sys.exit(1)
            with open(os.path.join(frame_dir, ".delivery_ok"), "w", encoding="utf-8") as f:
                f.write(DELIVERY_BITRATE)
            print(f"[{i}/10] RENDER_DONE {sname}", flush=True)
            continue
        if miss > sc.frame_start:
            print(f"[{i}/10] RESUME {sname} from frame {miss} (kept prior PNGs)", flush=True)
            sc.frame_start = miss
    print(f"[{i}/10] RENDER_START {sname} frames={sc.frame_start}-{sc.frame_end} engine={ENGINE} -> {out}", flush=True)
    try:
        bpy.ops.render.render(animation=True)
    except Exception as exc:
        print(f"[{i}/10] RENDER_FAIL {sname}: {exc}", flush=True)
        sys.exit(1)

    if use_frames and frame_dir:
        if encode_delivery(frame_dir, out) != 0:
            print(f"[{i}/10] ENCODE_FAIL {sname}", flush=True)
            sys.exit(1)
        with open(os.path.join(frame_dir, ".delivery_ok"), "w", encoding="utf-8") as f:
            f.write(DELIVERY_BITRATE)
    elif not os.path.isfile(out) or os.path.getsize(out) < 100_000:
        base = os.path.splitext(out)[0]
        parent = os.path.dirname(out)
        candidates = []
        for fn in os.listdir(parent):
            if not fn.lower().endswith(".mp4"):
                continue
            if fn.startswith(sname) or fn.startswith(os.path.basename(base)):
                p = os.path.join(parent, fn)
                if os.path.getsize(p) > 100_000:
                    candidates.append(p)
        if candidates:
            best = max(candidates, key=os.path.getsize)
            if best != out:
                if os.path.isfile(out):
                    os.remove(out)
                os.replace(best, out)
                print(f"[{i}/10] RENAMED {os.path.basename(best)} -> {os.path.basename(out)}", flush=True)
    print(f"[{i}/10] RENDER_DONE {sname}", flush=True)

print("ALL_SCENES_RENDERED", flush=True)
