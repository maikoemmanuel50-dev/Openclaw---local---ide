"""Assemble scene MP4s. Usage:
  python assemble_final_video.py
  python assemble_final_video.py --dir renders/video_clips_4k --output Africa_S1_Silicon_Savannah_7min_4K.mp4
"""
import argparse
import shutil
import subprocess
import os
import sys

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
XFADE = 0.8

SCENES = [
    ("01_ColdOpen", 50), ("02_Context2007", 45), ("03_Beat1_Hubs", 45),
    ("04_Beat1_Phone", 25), ("05_Beat2_Money", 45), ("06_Beat2_Solar", 40),
    ("07_Beat3_Gap", 50), ("08_Beat3_SecondaryCity", 35), ("09_Closer", 70),
    ("10_EndCard", 15),
]


def find_ffmpeg():
    ff = shutil.which("ffmpeg")
    if ff:
        return ff
    winget_glob = os.path.join(
        os.path.expandvars(r"%LOCALAPPDATA%"),
        "Microsoft", "WinGet", "Packages",
        "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe",
    )
    if os.path.isdir(winget_glob):
        for root, _, files in os.walk(winget_glob):
            if "ffmpeg.exe" in files:
                return os.path.join(root, "ffmpeg.exe")
    return None


def assemble(render_dir: str, output: str, master_copy: str | None = None) -> None:
    ff = find_ffmpeg()
    if not ff:
        print("ERROR: ffmpeg not found")
        sys.exit(1)

    clips = []
    for name, _ in SCENES:
        if name == "01_ColdOpen":
            integrated = os.path.join(render_dir, "01_ColdOpen_with_open30.mp4")
            path = integrated if os.path.isfile(integrated) else os.path.join(render_dir, f"{name}.mp4")
        else:
            path = os.path.join(render_dir, f"{name}.mp4")
        if not os.path.isfile(path):
            print(f"MISSING: {path}")
            sys.exit(1)
        clips.append(path)
        print(f"OK {name} ({os.path.getsize(path) // 1024} KB)")

    durations = [d for _, d in SCENES]
    parts = []
    prev = "[0:v]"
    offset = durations[0] - XFADE
    for i in range(1, len(clips)):
        out_label = f"[v{i}]" if i < len(clips) - 1 else "[vout]"
        parts.append(
            f"{prev}[{i}:v]xfade=transition=fadeblack:duration={XFADE}:offset={offset:.3f}{out_label}"
        )
        prev = out_label
        if i < len(clips) - 1:
            offset += durations[i] - XFADE

    fc = ";".join(parts)
    # Archive master: high quality (not YouTube delivery bitrate)
    cmd_master = [ff, "-y"] + sum([["-i", c] for c in clips], []) + [
        "-filter_complex", fc, "-map", "[vout]",
        "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
        "-crf", "14", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-g", "12", "-keyint_min", "12", "-sc_threshold", "0",
        "-an", output,
    ]
    print(f"Assembling archive master -> {output}")
    r = subprocess.run(cmd_master, capture_output=True, text=True)
    if r.returncode != 0:
        print("xfade failed:", r.stderr[-800:])
        sys.exit(1)

    size_mb = os.path.getsize(output) / (1024 * 1024)
    print(f"DONE master: {output} ({size_mb:.1f} MB)")
    if master_copy:
        shutil.copy2(output, master_copy)
        print(f"MASTER: {master_copy}")

    # YouTube-spec delivery sibling (docs/DELIVERY_STANDARDS.md): 1080p ~10 Mbps 2-pass VBR
    delivery = os.path.splitext(output)[0] + "_YT1080.mp4"
    passlog = os.path.join(os.path.dirname(output) or ".", "ffmpeg2pass_africa_s1")
    common = [
        "-i", output, "-an",
        "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
        "-b:v", "10M", "-maxrate", "12M", "-bufsize", "20M",
        "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-g", "12", "-keyint_min", "12", "-sc_threshold", "0",
        "-preset", "medium",
    ]
    print(f"Delivery 2-pass -> {delivery}")
    r1 = subprocess.run(
        [ff, "-y"] + common + ["-pass", "1", "-f", "null", "NUL" if os.name == "nt" else "/dev/null"],
        capture_output=True, text=True, cwd=os.path.dirname(output) or ".",
    )
    if r1.returncode != 0:
        print("2-pass1 warn:", r1.stderr[-400:])
    r2 = subprocess.run(
        [ff, "-y"] + common + ["-pass", "2", delivery],
        capture_output=True, text=True, cwd=os.path.dirname(output) or ".",
    )
    if r2.returncode != 0:
        print("2-pass2 failed:", r2.stderr[-800:])
    else:
        print(f"DELIVERY: {delivery} ({os.path.getsize(delivery)/(1024*1024):.1f} MB)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dir", default=os.path.join(PROJECT, "renders", "video_clips"))
    p.add_argument("--output", default=os.path.join(PROJECT, "Africa_S1_Silicon_Savannah_7min.mp4"))
    p.add_argument("--master", default=os.path.join(PROJECT, "Africa_S1_Silicon_Savannah_7min_MASTER.mp4"))
    args = p.parse_args()
    master = args.master if args.master else None
    assemble(args.dir, args.output, master)


if __name__ == "__main__":
    main()
