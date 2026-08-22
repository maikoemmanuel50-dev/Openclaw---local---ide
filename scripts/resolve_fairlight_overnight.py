"""
Build Fairlight-ready stems with documentary EQ then place on Resolve Episode 01:

  Refs: docs/AUDIO_MIX_STANDARDS.md
        Bloomberg Originals https://youtu.be/d2dgJGkw5p0
        Search Party        https://youtu.be/5xm_luvYoc8
        (+ TED-Ed / Vox clarity)

  A1 VO          0 dB reference (episode_01_vo.wav — locked stem; may still be placeholder bytes)
  A2 Music      -24 dB clip trim (then bake duck + gap swell via bake_a2_tension_release.py)
  A3 Ambient    -28 dB
  A4 Punctuation / whoosh / riser  -18 dB
  A5 Stat impact -14 dB

EQ is baked into stems because Resolve scripting cannot set Fairlight plugin graphs.
After this script: python scripts/bake_a2_tension_release.py

Run: python scripts/resolve_fairlight_overnight.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

PROJECT = r"C:\Users\HP\OneDrive\The Vault\Africa Season 1"
STEMS = os.path.join(PROJECT, "renders", "audio_stems", "fairlight")
AUDIO = os.path.join(PROJECT, "assets", "audio")
VO_REAL = os.path.join(AUDIO, "vo", "episode_01_vo.wav")
VO_PH = os.path.join(AUDIO, "vo", "episode_01_vo_placeholder.wav")
MUSIC = os.path.join(AUDIO, "music")
SFX = os.path.join(AUDIO, "sfx")
SILENT = os.path.join(PROJECT, "Africa_S1_Silicon_Savannah_7min.mp4")
DURATION = 420.0  # fallback

# Resolve track layout (1-based audio track index)
TRACK = {"vo": 1, "music": 2, "ambient": 3, "punct": 4, "stats": 5}

# Volume property in Resolve is typically linear gain or dB string depending on version.
# We use approximate linear: 10**(dB/20)
VOL = {
    "vo": 1.0,          # 0 dB
    "music": 0.063,     # ~-24 dB (felt under VO; swell baked in gaps)
    "ambient": 0.040,   # ~-28 dB
    "punct": 0.126,     # ~-18 dB
    "stats": 0.200,     # ~-14 dB
}

CHAPTER_MUSIC = [
    (0, "ch01_dawn_pad.wav", 95),
    (95, "ch02_daylight_lofi.wav", 70),
    (165, "ch03_darkdata_electronic.wav", 85),
    (250, "ch04_cooltension_drone.wav", 85),
    (335, "ch05_hopeful_dusk.wav", 85),
]

AMBIENT = [
    (0, 50, "city_morning_ambient.wav"),
    (50, 45, "street_bustle.wav"),
    (95, 70, "coworking_chatter.wav"),
    (210, 40, "solar_hum.wav"),
    (250, 85, "drone_ambient.wav"),
    (335, 70, "city_morning_ambient.wav"),
]

PUNCT = [
    (2.0, "chapter_inhale.wav"),
    (8.0, "matatu_horn.wav"),
    (12.0, "whoosh_soft.wav"),
    (22.0, "transaction_chime.wav"),
    (49.5, "whoosh_hard.wav"),
    (58.0, "brand_sting.wav"),
    (72.0, "keypad_click.wav"),
    (88.0, "ui_swipe.wav"),
    (94.5, "whoosh_hard.wav"),
    (100.0, "keyboard_clack.wav"),
    (112.0, "whoosh_soft.wav"),
    (139.5, "whoosh_soft.wav"),
    (145.0, "ui_swipe.wav"),
    (163.0, "chart_riser.wav"),
    (164.0, "transition_riser.wav"),
    (209.5, "whoosh_hard.wav"),
    (248.0, "tension_riser_long.wav"),
    (249.0, "gap_sub_pulse.wav"),
    (270.0, "gap_sub_pulse.wav"),
    (299.5, "whoosh_soft.wav"),
    (334.0, "transition_riser.wav"),
    (335.0, "chapter_inhale.wav"),
    (360.0, "logo_fade.wav"),
    (400.0, "whoosh_soft.wav"),
    (405.0, "music_resolve.wav"),
]

STATS = [
    (170.0, "stat_ping.wav"),
    (171.0, "release_hit.wav"),
    (195.0, "stat_impact.wav"),
    (196.0, "release_hit.wav"),
    (255.0, "stat_impact.wav"),
    (256.0, "release_hit.wav"),
    (410.0, "release_hit.wav"),
]


def ff() -> str:
    import shutil
    x = shutil.which("ffmpeg")
    if not x:
        raise RuntimeError("ffmpeg required")
    return x


def ffp() -> str:
    import shutil
    x = shutil.which("ffprobe")
    if not x:
        raise RuntimeError("ffprobe required")
    return x


def duration_of(path: str) -> float:
    r = subprocess.run(
        [ffp(), "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return DURATION


def run(cmd: list[str], label: str) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FAIL {label}:", r.stderr[-400:])
        raise RuntimeError(label)


def silence(path: str, dur: float) -> None:
    run([ff(), "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
         "-t", str(dur), path], "silence")


def build_music(dur: float, out: str) -> None:
    """Music stem + documentary EQ: gentle HPF, slight presence cut, soft limiter feel."""
    inputs, parts = [], []
    for i, (_, name, seg) in enumerate(CHAPTER_MUSIC):
        p = os.path.join(MUSIC, name)
        if not os.path.isfile(p):
            continue
        inputs += ["-i", p]
        parts.append(
            f"[{i}:a]atrim=0:{seg},asetpts=PTS-STARTPTS,"
            f"afade=t=in:d=1.2,afade=t=out:st={seg-1.5}:d=1.5[a{i}]"
        )
    if not parts:
        silence(out, dur)
        return
    n = len(parts)
    cin = "".join(f"[a{i}]" for i in range(n))
    # EQ: HPF, mud cut, deep 1.8k scoop (VO pocket), soft highs — quieter bed (Bloomberg/Search Party)
    eq = (
        "highpass=f=90,"
        "equalizer=f=250:t=q:w=1.2:g=-3,"
        "equalizer=f=1800:t=q:w=1.3:g=-4.5,"
        "equalizer=f=4500:t=q:w=1.0:g=-2,"
        "loudnorm=I=-26:TP=-2.5:LRA=10"
    )
    fc = ";".join(parts) + f";{cin}concat=n={n}:v=0:a=1,{eq},aformat=sample_rates=48000:channel_layouts=stereo[out]"
    run([ff(), "-y", *inputs, "-filter_complex", fc, "-map", "[out]", "-t", str(dur), out], "music")


def build_vo(dur: float, out: str) -> None:
    src = VO_REAL if os.path.isfile(VO_REAL) else VO_PH
    if not os.path.isfile(src):
        silence(out, dur)
        return
    # VO EQ: HPF 100, presence boost ~3k, de-mud, light loudnorm for Fairlight reference
    af = (
        "highpass=f=100,equalizer=f=200:t=q:w=1.0:g=-2,"
        "equalizer=f=3000:t=q:w=1.2:g=2.5,equalizer=f=7500:t=q:w=1.0:g=1,"
        "loudnorm=I=-16:TP=-1.5:LRA=9,aformat=sample_rates=48000:channel_layouts=stereo"
    )
    run([ff(), "-y", "-i", src, "-af", af, "-t", str(dur), out], "vo")


def mix_cues(cues: list[tuple], dur: float, out: str, eq: str) -> None:
    valid = [(t, os.path.join(SFX, f)) for t, f in cues if os.path.isfile(os.path.join(SFX, f))]
    if not valid:
        silence(out, dur)
        return
    # chunk to avoid filter graph limits
    chunks = []
    for c in range(0, len(valid), 10):
        part = valid[c:c+10]
        stem = out.replace(".wav", f"_{c}.wav")
        inputs, filters = [], []
        for i, (t, path) in enumerate(part):
            inputs += ["-i", path]
            ms = int(t * 1000)
            filters.append(
                f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                f"adelay={ms}|{ms}[s{i}]"
            )
        mix = "".join(f"[s{i}]" for i in range(len(part)))
        fc = ";".join(filters) + f";{mix}amix=inputs={len(part)}:duration=longest:normalize=0[out]"
        run([ff(), "-y", *inputs, "-filter_complex", fc, "-map", "[out]", "-t", str(dur), stem], f"cues{c}")
        chunks.append(stem)
    if len(chunks) == 1:
        run([ff(), "-y", "-i", chunks[0], "-af", eq, out], "eq")
        os.remove(chunks[0])
        return
    inputs, parts = [], []
    for i, ch in enumerate(chunks):
        inputs += ["-i", ch]
        parts.append(f"[{i}:a]anull[s{i}]")
    mix = "".join(f"[s{i}]" for i in range(len(chunks)))
    fc = ";".join(parts) + f";{mix}amix=inputs={len(chunks)}:duration=longest:normalize=0,{eq}[out]"
    run([ff(), "-y", *inputs, "-filter_complex", fc, "-map", "[out]", "-t", str(dur), out], "merge")
    for ch in chunks:
        if os.path.isfile(ch):
            os.remove(ch)


def build_ambient(dur: float, out: str) -> None:
    temps = []
    valid = []
    for i, (start, length, name) in enumerate(AMBIENT):
        src = os.path.join(SFX, name)
        if not os.path.isfile(src):
            continue
        tmp = os.path.join(STEMS, f"_a{i}.wav")
        run([ff(), "-y", "-stream_loop", "-1", "-i", src, "-t", str(length),
             "-af", f"afade=t=in:d=1.5,afade=t=out:st={max(0,length-2)}:d=2", tmp], f"amb{i}")
        temps.append(tmp)
        valid.append((start, tmp))
    if not valid:
        silence(out, dur)
        return
    inputs, filters = [], []
    for i, (t, path) in enumerate(valid):
        inputs += ["-i", path]
        ms = int(t * 1000)
        filters.append(f"[{i}:a]adelay={ms}|{ms}[s{i}]")
    mix = "".join(f"[s{i}]" for i in range(len(valid)))
    # Ambient EQ: band-pass-ish — cut low rumble + harsh highs (Vox bed under VO)
    eq = "highpass=f=120,lowpass=f=6000,equalizer=f=400:t=q:w=1:g=-1.5,volume=0.9"
    fc = ";".join(filters) + f";{mix}amix=inputs={len(valid)}:duration=longest:normalize=0,{eq}[out]"
    run([ff(), "-y", *inputs, "-filter_complex", fc, "-map", "[out]", "-t", str(dur), out], "ambient")
    for t in temps:
        if os.path.isfile(t):
            os.remove(t)


def build_stems(dur: float) -> dict[str, str]:
    os.makedirs(STEMS, exist_ok=True)
    paths = {
        "vo": os.path.join(STEMS, "A1_vo_eq.wav"),
        "music": os.path.join(STEMS, "A2_music_eq.wav"),
        "ambient": os.path.join(STEMS, "A3_ambient_eq.wav"),
        "punct": os.path.join(STEMS, "A4_punctuation_eq.wav"),
        "stats": os.path.join(STEMS, "A5_stats_eq.wav"),
    }
    print("Building A1 VO (EQ)...")
    build_vo(dur, paths["vo"])
    print("Building A2 Music (EQ)...")
    build_music(dur, paths["music"])
    # Snapshot unducked A2 before any sidechain bake overwrites it
    bak = os.path.join(STEMS, "A2_music_eq_pre_sidechain.bak.wav")
    shutil.copy2(paths["music"], bak)
    print("Building A3 Ambient (EQ)...")
    build_ambient(dur, paths["ambient"])
    print("Building A4 Punctuation...")
    mix_cues(PUNCT, dur, paths["punct"], "highpass=f=150,equalizer=f=5000:t=q:w=1:g=1.5")
    print("Building A5 Stats...")
    mix_cues(STATS, dur, paths["stats"], "highpass=f=80,equalizer=f=120:t=q:w=1:g=2,equalizer=f=2000:t=q:w=1:g=1")
    meta = {"duration": dur, "paths": paths, "vol_linear": VOL, "tracks": TRACK}
    with open(os.path.join(STEMS, "fairlight_stem_map.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    return paths


def place_in_resolve(paths: dict[str, str]) -> None:
    sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
    try:
        import DaVinciResolveScript as dvr
    except ImportError as e:
        print("Resolve scripting unavailable:", e)
        return
    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        print("Resolve not running")
        return
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    tl = project.GetCurrentTimeline()
    if not tl or tl.GetName() != "Episode 01 - Assembly":
        for i in range(1, int(project.GetTimelineCount() or 0) + 1):
            t = project.GetTimelineByIndex(i)
            if t and t.GetName() == "Episode 01 - Assembly":
                tl = t
                break
    project.SetCurrentTimeline(tl)
    resolve.OpenPage("fairlight")

    # Ensure 5 stereo audio tracks
    while tl.GetTrackCount("audio") < 5:
        tl.AddTrack("audio", "stereo")
    names = {1: "VO", 2: "Music", 3: "Ambient", 4: "Punctuation", 5: "Stats"}
    for i, n in names.items():
        try:
            tl.SetTrackName("audio", i, n)
        except Exception:
            pass

    mp = project.GetMediaPool()
    root = mp.GetRootFolder()
    folder = None
    for sf in root.GetSubFolderList() or []:
        if sf.GetName() == "Fairlight Stems":
            folder = sf
            break
    if folder is None:
        folder = mp.AddSubFolder(root, "Fairlight Stems")
    mp.SetCurrentFolder(folder)

    # Clear existing items on A1-A5 (lift)
    for ti in range(1, 6):
        items = tl.GetItemListInTrack("audio", ti) or []
        if items:
            try:
                tl.DeleteClips([it.GetUniqueId() for it in items], False)
            except Exception:
                # older API
                for it in items:
                    try:
                        tl.DeleteClips([it], False)
                    except Exception:
                        pass

    start = int(tl.GetStartFrame())
    imported = mp.ImportMedia(list(paths.values())) or []
    by_name = {c.GetName(): c for c in imported}
    # also scan folder
    for c in folder.GetClipList() or []:
        by_name[c.GetName()] = c

    order = [
        ("vo", "A1_vo_eq.wav", 1),
        ("music", "A2_music_eq.wav", 2),
        ("ambient", "A3_ambient_eq.wav", 3),
        ("punct", "A4_punctuation_eq.wav", 4),
        ("stats", "A5_stats_eq.wav", 5),
    ]
    infos = []
    for key, fname, track in order:
        clip = by_name.get(fname)
        if not clip:
            # try without path basename match
            for n, c in by_name.items():
                if fname in n or key in n.lower():
                    clip = c
                    break
        if not clip:
            print(f"  miss stem {fname}")
            continue
        infos.append({
            "mediaPoolItem": clip,
            "startFrame": 0,
            "endFrame": int(DURATION * 24),
            "recordFrame": start,  # absolute often required for scripting API
            "trackIndex": track,
            "mediaType": 2,  # audio
        })

    if infos:
        # Try relative first for MCP parity — scripting often wants absolute
        ok = mp.AppendToTimeline(infos)
        print(f"Appended audio stems: {bool(ok)} count={len(ok) if ok else 0}")

    # Set clip volumes (documentary levels)
    for ti, key in [(1, "vo"), (2, "music"), (3, "ambient"), (4, "punct"), (5, "stats")]:
        items = tl.GetItemListInTrack("audio", ti) or []
        for it in items:
            try:
                it.SetProperty("Volume", VOL[key])
            except Exception:
                try:
                    it.SetProperty("Volume", f"{VOL[key]}")
                except Exception as e:
                    print(f"  volume set fail A{ti}: {e}")

    try:
        project.SaveProject()
    except Exception:
        pass
    print("Fairlight page open; stems on A1-A5 with target gains.")
    print("Next: python scripts/bake_a2_tension_release.py  # duck ~18dB + VO-gap release swells")
    print("Manual EQ polish: Track EQ on A1 (VO) presence; A2 cut 2-4k under VO")


def main() -> None:
    global DURATION
    # ensure whoosh pack
    pack = os.path.join(AUDIO, "generate_tension_release_sfx.py")
    if os.path.isfile(pack) and not os.path.isfile(os.path.join(SFX, "whoosh_soft.wav")):
        subprocess.run([sys.executable, pack], check=False)

    dur = duration_of(SILENT) if os.path.isfile(SILENT) else DURATION
    DURATION = dur
    print(f"Duration {dur:.1f}s")
    paths = build_stems(dur)
    place_in_resolve(paths)
    # Bake duck + tension/release swells onto A2 (replaces unducked clip)
    bake = os.path.join(PROJECT, "scripts", "bake_a2_tension_release.py")
    if os.path.isfile(bake):
        print("Baking A2 tension/release...")
        subprocess.run([sys.executable, bake], check=False)
    print("DONE Fairlight overnight layout")
    print(f"Stems: {STEMS}")


if __name__ == "__main__":
    main()
