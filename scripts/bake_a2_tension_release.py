"""
Bake A2 music for Bloomberg / Search Party documentary feel:

  1) VO speech-band pocket EQ + soft bass roll under dialogue space
  2) Sidechain duck from A1 (~18 dB) — bed felt, not heard under VO
  3) Tension/release: swell music in VO silences (gaps ≥ 0.9 s)

Refs: docs/AUDIO_MIX_STANDARDS.md
  https://youtu.be/d2dgJGkw5p0  https://youtu.be/5xm_luvYoc8

Run: python scripts/bake_a2_tension_release.py
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
STEMS = PROJECT / "renders" / "audio_stems" / "fairlight"
VO = STEMS / "A1_vo_eq.wav"
MUSIC_SRC = STEMS / "A2_music_eq_pre_sidechain.bak.wav"
MUSIC_ACTIVE = STEMS / "A2_music_eq.wav"
MUSIC_FALLBACK = STEMS / "A2_music_eq.wav"
OUT = STEMS / "A2_music_eq_ducked.wav"
POCKET = STEMS / "A2_music_pocket.wav"
REPORT = STEMS / "a2_tension_release_report.json"

# Unducked source preference: bak → current A2 (if bak missing, copy A2 to bak first)
# Sidechain: deeper duck than earlier -12 dB preset (~18 dB under VO energy)
SC = (
    "sidechaincompress="
    "threshold=0.07:ratio=7:attack=18:release=200:makeup=1:knee=3:link=average"
)
# Pocket: HPF, mud cut, deep 1.5–2.5k scoop for VO, soft 5k shelf
POCKET_EQ = (
    "highpass=f=90,"
    "equalizer=f=220:t=q:w=1.1:g=-3,"
    "equalizer=f=1800:t=q:w=1.4:g=-5,"
    "equalizer=f=5000:t=q:w=1.0:g=-2,"
    "loudnorm=I=-26:TP=-2.5:LRA=10"
)
SWELL_DB = 6.0  # release lift in VO gaps (relative to ducked bed)
MIN_GAP_SEC = 0.9
MAX_SWELL_SEC = 4.5


def ff() -> str:
    x = shutil.which("ffmpeg")
    if not x:
        raise RuntimeError("ffmpeg required")
    return x


def ffp() -> str:
    x = shutil.which("ffprobe")
    if not x:
        raise RuntimeError("ffprobe required")
    return x


def duration(path: Path) -> float:
    r = subprocess.run(
        [ffp(), "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 420.0


def ensure_source() -> Path:
    """Use unducked bak when present; otherwise snapshot current A2 as bak."""
    if MUSIC_SRC.is_file() and MUSIC_ACTIVE.is_file():
        # Prefer bak only if it is at least as new as active (overnight refreshes bak)
        if MUSIC_SRC.stat().st_mtime >= MUSIC_ACTIVE.stat().st_mtime - 2:
            return MUSIC_SRC
    if MUSIC_ACTIVE.is_file():
        shutil.copy2(MUSIC_ACTIVE, MUSIC_SRC)
        return MUSIC_SRC
    if MUSIC_SRC.is_file():
        return MUSIC_SRC
    raise FileNotFoundError("No A2 music stem to bake")


def detect_silence_gaps(vo: Path) -> list[tuple[float, float]]:
    """Return (start, end) silence regions from VO (release windows)."""
    cmd = [
        ff(), "-i", str(vo),
        "-af", "silencedetect=noise=-32dB:d=0.35",
        "-f", "null", "-",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    text = (r.stderr or "") + (r.stdout or "")
    starts = [float(x) for x in re.findall(r"silence_start:\s*([\d.]+)", text)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([\d.]+)", text)]
    gaps: list[tuple[float, float]] = []
    # Pair starts with ends; silencedetect may omit trailing end
    ei = 0
    for s in starts:
        while ei < len(ends) and ends[ei] <= s:
            ei += 1
        if ei < len(ends):
            e = ends[ei]
            ei += 1
            if e - s >= MIN_GAP_SEC:
                gaps.append((s, min(e, s + MAX_SWELL_SEC)))
    return gaps


def swell_enable_expr(gaps: list[tuple[float, float]]) -> str:
    if not gaps:
        return "0"
    parts = [f"between(t\\,{a:.3f}\\,{b:.3f})" for a, b in gaps]
    return "+".join(parts)


def bake() -> dict:
    if not VO.is_file():
        raise FileNotFoundError(f"missing VO {VO}")
    src = ensure_source()
    gaps = detect_silence_gaps(VO)
    # Cap gap count for filter size
    if len(gaps) > 80:
        # keep longest gaps (strongest release moments)
        gaps = sorted(gaps, key=lambda g: g[1] - g[0], reverse=True)[:80]
        gaps = sorted(gaps, key=lambda g: g[0])

    # Stage 1: pocket EQ on unducked music
    cmd1 = [
        ff(), "-y", "-i", str(src),
        "-af", POCKET_EQ + ",aformat=sample_rates=48000:channel_layouts=stereo",
        str(POCKET),
    ]
    r1 = subprocess.run(cmd1, capture_output=True, text=True)
    if r1.returncode != 0 or not POCKET.is_file():
        raise RuntimeError((r1.stderr or "")[-900:])

    # Stage 2: sidechain duck + optional gap swell
    # volume: base 1.0 when speaking (already ducked by SC); * gain in gaps
    lin = 10 ** (SWELL_DB / 20.0)
    enable = swell_enable_expr(gaps)
    # When enable>0, multiply by swell; else 1. volume expression:
    # volume='if(enable, swell, 1)' via two volumes is cleaner:
    # volume=1, then volume=lin:enable='...'
    fc = (
        f"[0:a][1:a]{SC}[ducked];"
        f"[ducked]volume={lin}:eval=frame:enable='{enable}'[out]"
        if gaps else
        f"[0:a][1:a]{SC}[out]"
    )
    # enable expr uses escaped commas for filtergraph — ffmpeg wants single quotes around enable
    # Rebuild without over-escaping for filter_complex
    if gaps:
        enable_raw = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in gaps)
        fc = (
            f"[0:a][1:a]{SC}[ducked];"
            f"[ducked]volume={lin}:eval=frame:enable='{enable_raw}'[out]"
        )

    cmd2 = [
        ff(), "-y",
        "-i", str(POCKET),
        "-i", str(VO),
        "-filter_complex", fc,
        "-map", "[out]",
        "-ac", "2", "-ar", "48000",
        str(OUT),
    ]
    r2 = subprocess.run(cmd2, capture_output=True, text=True)
    if r2.returncode != 0 or not OUT.is_file():
        raise RuntimeError((r2.stderr or "")[-1200:])

    shutil.copy2(OUT, MUSIC_ACTIVE)
    return {
        "ok": True,
        "source": str(src),
        "vo": str(VO),
        "pocket": str(POCKET),
        "ducked": str(OUT),
        "active_a2": str(MUSIC_ACTIVE),
        "sidechain": SC,
        "pocket_eq": POCKET_EQ,
        "swell_db": SWELL_DB,
        "gap_count": len(gaps),
        "gaps_sample": gaps[:12],
        "bytes": OUT.stat().st_size,
        "duration_sec": duration(OUT),
    }


def place_in_resolve(path: Path) -> dict:
    try:
        import DaVinciResolveScript as dvr
    except ImportError:
        for p in (
            r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules",
        ):
            if os.path.isdir(p) and p not in sys.path:
                sys.path.append(p)
        import DaVinciResolveScript as dvr  # type: ignore

    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        return {"placed": False, "err": "Resolve not connected"}
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if not project:
        return {"placed": False, "err": "no project"}
    tl = project.GetCurrentTimeline()
    if not tl or tl.GetName() != "Episode 01 - Assembly":
        for i in range(1, int(project.GetTimelineCount() or 0) + 1):
            t = project.GetTimelineByIndex(i)
            if t and t.GetName() == "Episode 01 - Assembly":
                project.SetCurrentTimeline(t)
                tl = t
                break
    if not tl:
        return {"placed": False, "err": "timeline missing"}
    try:
        resolve.OpenPage("fairlight")
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

    # Clear A2
    items = tl.GetItemListInTrack("audio", 2) or []
    if items:
        try:
            tl.DeleteClips([it.GetUniqueId() for it in items], False)
        except Exception:
            try:
                tl.DeleteClips(items, False)
            except Exception:
                pass

    imported = mp.ImportMedia([str(path)]) or []
    if not imported:
        return {"placed": False, "err": "ImportMedia failed"}
    clip = imported[0]
    start = tl.GetStartFrame()
    ok = False
    try:
        ok = bool(mp.AppendToTimeline([{
            "mediaPoolItem": clip,
            "startFrame": 0,
            "trackIndex": 2,
            "recordFrame": start,
            "mediaType": 2,
        }]))
    except Exception as e:
        return {"placed": False, "err": str(e)}

    # Documentary bed trim (~-24 dB linear)
    vol = 0.063
    for it in (tl.GetItemListInTrack("audio", 2) or []):
        try:
            it.SetProperty("Volume", vol)
        except Exception:
            try:
                it.SetProperty("Volume", f"{vol}")
            except Exception:
                pass
    try:
        project.SaveProject()
    except Exception:
        pass
    names = []
    for it in (tl.GetItemListInTrack("audio", 2) or []):
        try:
            names.append(it.GetName())
        except Exception:
            names.append("?")
    return {"placed": ok, "a2_items": names, "volume_linear": vol}


def main() -> None:
    print("=== A2 tension/release bake (Bloomberg / Search Party standards) ===")
    meta = bake()
    print(f"gaps={meta['gap_count']} bytes={meta['bytes']} -> {MUSIC_ACTIVE}")
    print("=== place A2 on Resolve ===")
    place = place_in_resolve(MUSIC_ACTIVE)
    print(place)
    meta["resolve"] = place
    REPORT.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"report {REPORT}")
    if not place.get("placed"):
        sys.exit(2)


if __name__ == "__main__":
    main()
