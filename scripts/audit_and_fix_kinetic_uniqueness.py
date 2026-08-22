"""
Audit KINETIC list in resolve_pace_kinetic_yb.py for duplicate media names.
Generate unique replacement stills/cuts (CPU ffmpeg) and patch KINETIC in-place.

Run: python scripts/audit_and_fix_kinetic_uniqueness.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
PACE = PROJECT / "scripts" / "resolve_pace_kinetic_yb.py"
STILLS = PROJECT / "assets" / "canva" / "kinetic" / "graded_1080"
CUTS = PROJECT / "renders" / "paced_overlays" / "stock_cinematic"
UNIQ_STILLS = PROJECT / "assets" / "canva" / "kinetic" / "unique_replacements"
UNIQ_CUTS = PROJECT / "renders" / "paced_overlays" / "unique_replacements"
REGISTRY = PROJECT / "renders" / "quality" / "UNIQUE_ASSET_REGISTRY.json"
REPORT = PROJECT / "renders" / "quality" / "kinetic_uniqueness_report.json"

SOFTPOP = (
    "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
    "eq=contrast=1.06:saturation=0.88:brightness=0.015"
)

SCENE_AT_FRAME = [
    (1200, "01"),
    (2280, "02"),
    (3360, "03"),
    (3960, "04"),
    (5040, "05"),
    (6000, "06"),
    (7200, "07"),
    (8040, "08"),
    (9720, "09"),
    (10080, "10"),
]


def ff() -> str:
    x = shutil.which("ffmpeg")
    if not x:
        raise RuntimeError("ffmpeg required")
    return x


def scene_for_frame(f: int) -> str:
    for limit, sc in SCENE_AT_FRAME:
        if f < limit:
            return sc
    return "10"


def load_kinetic() -> list[tuple[str, int, int, int]]:
    spec = importlib.util.spec_from_file_location("pace", PACE)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return list(mod.KINETIC)


def find_source(name: str) -> Path | None:
    stem = Path(name).stem
    for root in (STILLS, PROJECT / "assets" / "canva" / "kinetic" / "hq", UNIQ_STILLS):
        if not root.is_dir():
            continue
        for p in root.glob(f"{stem}*"):
            if p.is_file():
                return p
        for p in root.glob("*.png"):
            if stem.lower() in p.stem.lower():
                return p
    cut_root = CUTS
    for p in (cut_root, UNIQ_CUTS):
        if not p.is_dir():
            continue
        for c in p.glob(name):
            if c.is_file():
                return c
        for c in p.glob(f"{stem}*"):
            if c.is_file():
                return c
    return None


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_registry() -> dict:
    if REGISTRY.is_file():
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {"policy": "one asset id + one sha1 per entire episode", "assets": []}


def register_asset(reg: dict, asset_id: str, path: Path, kind: str) -> None:
    digest = sha1_file(path)
    for a in reg.get("assets", []):
        if a.get("id") == asset_id:
            return
        if a.get("sha1") == digest:
            raise RuntimeError(f"byte collision {path.name} vs {a.get('id')}")
    reg.setdefault("assets", []).append(
        {"id": asset_id, "path": str(path), "sha1": digest, "kind": kind}
    )


def make_still_variant(src: Path, dest: Path, vf: str) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 80_000:
        return True
    cmd = [ff(), "-y", "-i", str(src), "-vf", vf, "-frames:v", "1", str(dest)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0 and dest.is_file() and dest.stat().st_size > 50_000


def make_cut_from_still(src: Path, dest: Path, frames: int, pan: str) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 30_000:
        return True
    if pan == "left":
        zp = "zoompan=z='min(zoom+0.0018,1.14)':x='0':y='ih/2-(ih/zoom/2)':d={d}:s=1920x1080:fps=24"
    elif pan == "right":
        zp = "zoompan=z='min(zoom+0.0018,1.14)':x='iw-iw/zoom':y='ih/2-(ih/zoom/2)':d={d}:s=1920x1080:fps=24"
    else:
        zp = "zoompan=z='min(zoom+0.002,1.16)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d}:s=1920x1080:fps=24"
    zp = zp.format(d=frames)
    cmd = [
        ff(), "-y", "-loop", "1", "-i", str(src), "-vf", zp,
        "-frames:v", str(frames), "-c:v", "libx264", "-profile:v", "high",
        "-pix_fmt", "yuv420p", "-an", str(dest),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0 and dest.is_file() and dest.stat().st_size > 20_000


def make_cut_from_video(src: Path, dest: Path, frames: int, ss: float) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 30_000:
        return True
    dur = frames / 24.0
    # Short stock cuts may be <1s — stay in-bounds
    ss = max(0.0, min(ss, 0.15))
    cmd = [
        ff(), "-y", "-i", str(src), "-ss", f"{ss:.3f}", "-t", f"{dur:.3f}",
        "-vf", SOFTPOP, "-r", "24",
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-an", str(dest),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0 and dest.is_file() and dest.stat().st_size > 20_000:
        return True
    # Fallback: still zoompan from first frame
    still = dest.parent / f"_tmp_{dest.stem}.png"
    subprocess.run([ff(), "-y", "-i", str(src), "-frames:v", "1", str(still)], capture_output=True)
    if still.is_file():
        ok = make_cut_from_still(still, dest, frames, "center")
        still.unlink(missing_ok=True)
        return ok
    return False


VARIANTS = [
    ("warm", SOFTPOP + ",eq=saturation=1.08"),
    ("cool", SOFTPOP + ",eq=saturation=0.82:contrast=1.1"),
    ("left", "scale=2200:1238:force_original_aspect_ratio=increase,crop=1920:1080:0:(ih-1080)/2," + SOFTPOP),
    ("right", "scale=2200:1238:force_original_aspect_ratio=increase,crop=1920:1080:(iw-1920):(ih-1080)/2," + SOFTPOP),
    ("tight", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080:(iw-1920)/2:(ih-1080)/3," + SOFTPOP),
]


def generate_replacement(original: str, scene: str, idx: int) -> str:
    """Return new unique media filename."""
    src = find_source(original)
    ext = Path(original).suffix.lower()
    stem = Path(original).stem
    tag, vf = VARIANTS[idx % len(VARIANTS)]
    uniq_idx = 800 + idx

    if ext in (".png", ".jpg", ".jpeg"):
        new_name = f"uniq_s{scene}_{stem[:28]}_{tag}_1080.png"
        dest = UNIQ_STILLS / new_name
        if not src:
            # fallback: any scene still
            seeds = list(STILLS.glob(f"k{scene}_*.png")) or list(STILLS.glob("k*.png"))
            src = seeds[0] if seeds else None
        if not src:
            raise FileNotFoundError(f"No source for still {original}")
        if not make_still_variant(src, dest, vf):
            raise RuntimeError(f"Failed still {dest.name}")
        return new_name

    m = re.search(r"_(\d+)f", original)
    frames = int(m.group(1)) if m else 12
    new_name = f"cut_u{uniq_idx:03d}_s{scene}_{tag}_{frames}f.mp4"
    dest = UNIQ_CUTS / new_name
    if src and src.suffix.lower() == ".mp4":
        ss = (idx % 3) * 0.05
        frames = 12
        m = re.search(r"_(\d+)f", original)
        if m:
            frames = int(m.group(1))
        if not make_cut_from_video(src, dest, frames, ss):
            raise RuntimeError(f"Failed cut from video {dest.name}")
    else:
        still = src or (list(STILLS.glob(f"k{scene}_*.png")) or list(STILLS.glob("k*.png")))[0]
        frames = 12
        m = re.search(r"_(\d+)f", original)
        if m:
            frames = int(m.group(1))
        pan = ("left", "right", "center")[idx % 3]
        if not make_cut_from_still(still, dest, frames, pan):
            raise RuntimeError(f"Failed cut from still {dest.name}")
    return dest.name


def patch_kinetic_file(replacements: dict[str, str]) -> int:
  """Replace duplicate occurrence lines (2nd+ only) in resolve_pace_kinetic_yb.py."""
  text = PACE.read_text(encoding="utf-8")
  seen: dict[str, int] = {}
  lines = text.splitlines()
  changed = 0
  out = []
  in_kinetic = False
  for line in lines:
    if line.strip().startswith("KINETIC = ["):
      in_kinetic = True
    if in_kinetic and line.strip() == "]":
      in_kinetic = False
    if in_kinetic and '("' in line.replace("'", '"'):
      m = re.search(r'\("([^"]+)"', line)
      if m:
        name = m.group(1)
        n = seen.get(name, 0) + 1
        seen[name] = n
        if n > 1 and name in replacements:
          new_name = replacements[name][n - 2]  # 0-based for dup index
          line = line.replace(f'("{name}"', f'("{new_name}"', 1)
          changed += 1
    out.append(line)
  if changed:
    PACE.write_text("\n".join(out) + "\n", encoding="utf-8")
  return changed


def main():
    UNIQ_STILLS.mkdir(parents=True, exist_ok=True)
    UNIQ_CUTS.mkdir(parents=True, exist_ok=True)
    kinetic = load_kinetic()
    seen: dict[str, list[int]] = {}
    for i, (name, rel, dur, tr) in enumerate(kinetic):
        seen.setdefault(name, []).append(i)

    duplicates = {k: v for k, v in seen.items() if len(v) > 1}
    reg = load_registry()
    replacements: dict[str, list[str]] = {}
    created: list[dict] = []
    gen_idx = 0

    for name, indices in sorted(duplicates.items()):
        replacements[name] = []
        for occ_i, kin_idx in enumerate(indices[1:], start=1):
            rel = kinetic[kin_idx][1]
            scene = scene_for_frame(rel)
            new_name = generate_replacement(name, scene, gen_idx)
            gen_idx += 1
            replacements[name].append(new_name)
            path = UNIQ_STILLS / new_name if new_name.endswith(".png") else UNIQ_CUTS / new_name
            kind = "still" if new_name.endswith(".png") else "cut"
            asset_id = Path(new_name).stem
            register_asset(reg, asset_id, path, kind)
            created.append(
                {
                    "original": name,
                    "replacement": new_name,
                    "occurrence": occ_i + 1,
                    "frame": rel,
                    "scene": scene,
                }
            )

    changed = patch_kinetic_file(replacements)
    REGISTRY.write_text(json.dumps(reg, indent=2), encoding="utf-8")
    report = {
        "kinetic_total": len(kinetic),
        "duplicate_names": len(duplicates),
        "replacements_created": len(created),
        "pace_lines_patched": changed,
        "duplicates": {k: len(v) for k, v in duplicates.items()},
        "created": created,
    }
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Duplicates: {len(duplicates)} names, {len(created)} replacements, {changed} lines patched")
    print("REPORT", REPORT)


if __name__ == "__main__":
    main()
