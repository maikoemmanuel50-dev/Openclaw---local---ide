"""
Overnight documentary mix — TED-Ed / Vox / Bloomberg / WSJ inspired.
Builds music + ambient beds + punctuation SFX + tension/release transitions.
Uses placeholder VO until real episode_01_vo.wav arrives.

Output: Africa_S1_Silicon_Savannah_FINAL.mp4
Also writes stems: renders/audio_stems/{music,ambient,sfx,mix}.wav

Run: python assemble_with_audio.py
"""
from __future__ import annotations

import os
import subprocess
import sys

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
SILENT_VIDEO = os.path.join(PROJECT, "Africa_S1_Silicon_Savannah_7min.mp4")
OUTPUT = os.path.join(PROJECT, "Africa_S1_Silicon_Savannah_FINAL.mp4")
AUDIO_DIR = os.path.join(PROJECT, "assets", "audio")
VO_REAL = os.path.join(AUDIO_DIR, "vo", "episode_01_vo.wav")
VO_PLACEHOLDER = os.path.join(AUDIO_DIR, "vo", "episode_01_vo_placeholder.wav")
MUSIC_DIR = os.path.join(AUDIO_DIR, "music")
SFX_DIR = os.path.join(AUDIO_DIR, "sfx")
STEMS = os.path.join(PROJECT, "renders", "audio_stems")

# Chapter music (start_sec, file, segment_sec) — tension arc: warm → drive → data → sparse → hope
CHAPTER_MUSIC = [
    (0, "ch01_dawn_pad.wav", 95),
    (95, "ch02_daylight_lofi.wav", 70),
    (165, "ch03_darkdata_electronic.wav", 85),
    (250, "ch04_cooltension_drone.wav", 85),
    (335, "ch05_hopeful_dusk.wav", 85),
]

# Ambient beds: (start_sec, duration_sec, file, volume)
AMBIENT_BEDS = [
    (0, 50, "city_morning_ambient.wav", 0.22),
    (50, 45, "street_bustle.wav", 0.20),
    (95, 45, "coworking_chatter.wav", 0.18),
    (140, 25, "coworking_chatter.wav", 0.12),  # phone beat — quieter
    (210, 40, "solar_hum.wav", 0.20),
    (250, 85, "drone_ambient.wav", 0.24),  # gap tension
    (335, 70, "city_morning_ambient.wav", 0.14),  # dusk lift (softer)
]

# Punctuation + tension/release (TED-Ed cut accents, Bloomberg stat hits, Vox whooshes)
# (time_sec, file, volume)
SFX_CUES = [
    # S01 cold open — establish + pulse
    (2.0, "chapter_inhale.wav", 0.45),
    (8.0, "matatu_horn.wav", 0.45),
    (12.0, "whoosh_soft.wav", 0.35),
    (22.0, "transaction_chime.wav", 0.5),
    (28.0, "whoosh_soft.wav", 0.3),
    # S01→S02 transition
    (49.5, "whoosh_hard.wav", 0.4),
    (50.0, "chapter_inhale.wav", 0.35),
    # S02 M-Pesa
    (58.0, "brand_sting.wav", 0.5),
    (72.0, "keypad_click.wav", 0.45),
    (88.0, "ui_swipe.wav", 0.4),
    # S02→S03
    (94.5, "whoosh_hard.wav", 0.42),
    # S03 hubs
    (100.0, "keyboard_clack.wav", 0.4),
    (112.0, "whoosh_soft.wav", 0.3),
    (125.0, "keyboard_clack.wav", 0.35),
    # S03→S04
    (139.5, "whoosh_soft.wav", 0.38),
    (145.0, "ui_swipe.wav", 0.45),
    # S04→S05 tension into money
    (164.0, "transition_riser.wav", 0.4),
    (163.0, "chart_riser.wav", 0.45),
    (170.0, "stat_ping.wav", 0.55),
    (171.0, "release_hit.wav", 0.5),
    (195.0, "stat_impact.wav", 0.55),
    (196.0, "release_hit.wav", 0.45),
    # S05→S06
    (209.5, "whoosh_hard.wav", 0.4),
    (215.0, "solar_hum.wav", 0.15),  # short bed poke if trimmed by amix
    # S06→S07 tension into gap
    (248.0, "tension_riser_long.wav", 0.42),
    (249.0, "gap_sub_pulse.wav", 0.45),
    (255.0, "stat_impact.wav", 0.55),
    (256.0, "release_hit.wav", 0.5),
    (270.0, "gap_sub_pulse.wav", 0.35),
    # S07→S08
    (299.5, "whoosh_soft.wav", 0.35),
    (310.0, "drone_ambient.wav", 0.12),
    # S08→S09 release / hope
    (334.0, "transition_riser.wav", 0.35),
    (335.0, "chapter_inhale.wav", 0.4),
    (340.0, "whoosh_soft.wav", 0.3),
    (360.0, "logo_fade.wav", 0.4),
    (375.0, "logo_fade.wav", 0.35),
    # End card resolve
    (400.0, "whoosh_soft.wav", 0.28),
    (405.0, "music_resolve.wav", 0.55),
    (410.0, "release_hit.wav", 0.35),
]


def find_ffmpeg() -> str:
    import shutil

    ff = shutil.which("ffmpeg")
    if ff:
        return ff
    winget = os.path.join(
        os.path.expandvars(r"%LOCALAPPDATA%"),
        "Microsoft",
        "WinGet",
        "Packages",
        "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe",
    )
    if os.path.isdir(winget):
        for root, _, files in os.walk(winget):
            if "ffmpeg.exe" in files:
                return os.path.join(root, "ffmpeg.exe")
    raise RuntimeError("ffmpeg not found")


def find_ffprobe() -> str:
    import shutil

    fp = shutil.which("ffprobe")
    if fp:
        return fp
    ff = find_ffmpeg()
    cand = ff.replace("ffmpeg.exe", "ffprobe.exe").replace("ffmpeg", "ffprobe")
    if os.path.isfile(cand):
        return cand
    raise RuntimeError("ffprobe not found")


def get_duration(path: str) -> float:
    fp = find_ffprobe()
    r = subprocess.run(
        [fp, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 420.0


def silence(ff: str, duration: float, out: str) -> None:
    subprocess.run(
        [ff, "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
         "-t", str(duration), out],
        check=True, capture_output=True,
    )


def build_music_track(ff: str, duration: float, out: str) -> None:
    inputs: list[str] = []
    parts: list[str] = []
    for i, (start, fname, seg_dur) in enumerate(CHAPTER_MUSIC):
        path = os.path.join(MUSIC_DIR, fname)
        if not os.path.isfile(path):
            print(f"  SKIP music: {fname}")
            continue
        inputs.extend(["-i", path])
        # soft chapter edges — documentary crossfade feel
        parts.append(
            f"[{i}:a]atrim=0:{seg_dur},asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d=1.2,afade=t=out:st={seg_dur-1.5}:d=1.5,"
            f"volume=0.28[a{i}]"
        )
    if not parts:
        silence(ff, duration, out)
        return
    n = len(parts)
    concat_in = "".join(f"[a{i}]" for i in range(n))
    fc = ";".join(parts) + f";{concat_in}concat=n={n}:v=0:a=1,aformat=sample_rates=48000:channel_layouts=stereo[music]"
    cmd = [ff, "-y", *inputs, "-filter_complex", fc, "-map", "[music]", "-t", str(duration), out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("Music build failed:", r.stderr[-400:])
        bed = os.path.join(MUSIC_DIR, "ch01_dawn_pad.wav")
        subprocess.run(
            [ff, "-y", "-stream_loop", "-1", "-i", bed, "-t", str(duration),
             "-af", "volume=0.25", out],
            check=True, capture_output=True,
        )


def build_layered_cues(
    ff: str,
    duration: float,
    cues: list[tuple],
    out: str,
    base_dir: str,
) -> None:
    """Place timed WAV cues with adelay + amix (stereo)."""
    valid = []
    for row in cues:
        t, fname, vol = row[0], row[1], row[2]
        path = os.path.join(base_dir, fname)
        if os.path.isfile(path):
            valid.append((t, path, vol))
    if not valid:
        silence(ff, duration, out)
        return

    # ffmpeg adelay/amix input count limits — chunk then mix stems
    chunk_size = 12
    stems = []
    for c in range(0, len(valid), chunk_size):
        chunk = valid[c : c + chunk_size]
        stem = out.replace(".wav", f"_chunk{c}.wav")
        inputs: list[str] = []
        filters: list[str] = []
        for i, (t, path, vol) in enumerate(chunk):
            inputs.extend(["-i", path])
            ms = int(t * 1000)
            filters.append(
                f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                f"adelay={ms}|{ms},volume={vol}[s{i}]"
            )
        mix_in = "".join(f"[s{i}]" for i in range(len(chunk)))
        fc = (
            ";".join(filters)
            + f";{mix_in}amix=inputs={len(chunk)}:duration=longest:normalize=0,"
            f"aformat=sample_rates=48000:channel_layouts=stereo[out]"
        )
        cmd = [ff, "-y", *inputs, "-filter_complex", fc, "-map", "[out]", "-t", str(duration), stem]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"Cue chunk {c} failed:", r.stderr[-300:])
            continue
        stems.append(stem)

    if not stems:
        silence(ff, duration, out)
        return
    if len(stems) == 1:
        os.replace(stems[0], out)
        return

    inputs = []
    parts = []
    for i, stem in enumerate(stems):
        inputs.extend(["-i", stem])
        parts.append(f"[{i}:a]anull[s{i}]")
    mix_in = "".join(f"[s{i}]" for i in range(len(stems)))
    fc = ";".join(parts) + f";{mix_in}amix=inputs={len(stems)}:duration=longest:normalize=0[out]"
    cmd = [ff, "-y", *inputs, "-filter_complex", fc, "-map", "[out]", "-t", str(duration), out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("Stem merge failed:", r.stderr[-300:])
        silence(ff, duration, out)
    for stem in stems:
        if os.path.isfile(stem):
            os.remove(stem)


def build_ambient_track(ff: str, duration: float, out: str) -> None:
    cues = []
    for start, dur, fname, vol in AMBIENT_BEDS:
        path = os.path.join(SFX_DIR, fname)
        if not os.path.isfile(path):
            continue
        # Use trimmed ambient as delayed cue — pre-trim to segment length via ffmpeg later
        # Represent as: generate temp trimmed then delay
        cues.append((start, fname, vol, dur))

    if not cues:
        silence(ff, duration, out)
        return

    # Build trimmed segments then delay
    temps = []
    valid = []
    for i, (start, fname, vol, dur) in enumerate(cues):
        src = os.path.join(SFX_DIR, fname)
        tmp = os.path.join(STEMS, f"_amb_{i}.wav")
        os.makedirs(STEMS, exist_ok=True)
        subprocess.run(
            [ff, "-y", "-stream_loop", "-1", "-i", src, "-t", str(dur),
             "-af", f"volume={vol},afade=t=in:d=1.5,afade=t=out:st={max(0,dur-2)}:d=2",
             tmp],
            check=True, capture_output=True,
        )
        temps.append(tmp)
        valid.append((start, tmp, 1.0))

    # reuse layered builder with absolute paths — patch by writing into SFX-less mode
    inputs = []
    filters = []
    for i, (t, path, vol) in enumerate(valid):
        inputs.extend(["-i", path])
        ms = int(t * 1000)
        filters.append(
            f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
            f"adelay={ms}|{ms},volume={vol}[s{i}]"
        )
    mix_in = "".join(f"[s{i}]" for i in range(len(valid)))
    fc = (
        ";".join(filters)
        + f";{mix_in}amix=inputs={len(valid)}:duration=longest:normalize=0[out]"
    )
    cmd = [ff, "-y", *inputs, "-filter_complex", fc, "-map", "[out]", "-t", str(duration), out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    for tmp in temps:
        if os.path.isfile(tmp):
            os.remove(tmp)
    if r.returncode != 0:
        print("Ambient failed:", r.stderr[-300:])
        silence(ff, duration, out)


def main() -> None:
    # Ensure tension SFX pack exists
    gen = os.path.join(AUDIO_DIR, "generate_tension_release_sfx.py")
    if os.path.isfile(gen) and not os.path.isfile(os.path.join(SFX_DIR, "whoosh_soft.wav")):
        subprocess.run([sys.executable, gen], check=False)

    ff = find_ffmpeg()
    if not os.path.isfile(SILENT_VIDEO):
        print(f"ERROR: Silent video not found: {SILENT_VIDEO}")
        sys.exit(1)

    os.makedirs(STEMS, exist_ok=True)
    duration = get_duration(SILENT_VIDEO)
    print(f"Video duration: {duration:.1f}s")

    tmp_music = os.path.join(STEMS, "music.wav")
    tmp_amb = os.path.join(STEMS, "ambient.wav")
    tmp_sfx = os.path.join(STEMS, "sfx.wav")
    tmp_mix = os.path.join(STEMS, "mix_pre_vo.wav")

    print("Building music (chapter beds + fades)...")
    build_music_track(ff, duration, tmp_music)

    print("Building ambient beds...")
    build_ambient_track(ff, duration, tmp_amb)

    print("Building SFX / tension-release...")
    build_layered_cues(ff, duration, SFX_CUES, tmp_sfx, SFX_DIR)

    vo = VO_REAL if os.path.isfile(VO_REAL) else (
        VO_PLACEHOLDER if os.path.isfile(VO_PLACEHOLDER) else None
    )
    print(f"VO: {vo or 'none'} ({'REAL' if vo == VO_REAL else 'placeholder'})")

    # Mix stems: music -22-ish, ambient quieter, sfx punctuation, VO on top
    print("Mixing stems...")
    inputs = ["-i", tmp_music, "-i", tmp_amb, "-i", tmp_sfx]
    if vo:
        inputs.extend(["-i", vo])
        # sidechain-ish duck: lower music when VO present via volume weights
        fc = (
            "[0:a]volume=0.55[m];"
            "[1:a]volume=0.7[amb];"
            "[2:a]volume=0.85[sfx];"
            "[3:a]volume=1.0[vo];"
            "[m][amb][sfx][vo]amix=inputs=4:duration=first:dropout_transition=2:normalize=0[aout]"
        )
    else:
        fc = (
            "[0:a]volume=0.7[m];"
            "[1:a]volume=0.8[amb];"
            "[2:a]volume=0.9[sfx];"
            "[m][amb][sfx]amix=inputs=3:duration=first:normalize=0[aout]"
        )
    r = subprocess.run(
        [ff, "-y", *inputs, "-filter_complex", fc, "-map", "[aout]", tmp_mix],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print("Stem mix failed:", r.stderr[-500:])
        sys.exit(1)

    print("Muxing FINAL mp4...")
    r = subprocess.run(
        [ff, "-y", "-i", SILENT_VIDEO, "-i", tmp_mix,
         "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-ac", "2",
         "-shortest", OUTPUT],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print("Mux failed:", r.stderr[-500:])
        sys.exit(1)

    size_mb = os.path.getsize(OUTPUT) / (1024 * 1024)
    print(f"DONE: {OUTPUT} ({size_mb:.1f} MB)")
    print(f"Stems: {STEMS}")
    print("Tomorrow: drop assets/audio/vo/episode_01_vo.wav then re-run this script.")


if __name__ == "__main__":
    main()
