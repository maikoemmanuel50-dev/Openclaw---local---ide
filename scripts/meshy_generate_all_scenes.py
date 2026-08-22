"""
Meshy image-to-3D batch for all 10 Africa S1 scenes.

CPU/API only — does NOT touch Blender GPU HQ batch.

Requires MESHY_API_KEY (User env or https://www.meshy.ai/settings/api).

Usage:
  set MESHY_API_KEY=msy_...
  python scripts/meshy_generate_all_scenes.py
  python scripts/meshy_generate_all_scenes.py --scene S07
  python scripts/meshy_generate_all_scenes.py --dry-run

Outputs:
  assets/meshy/scenes/<SXX>/*.glb|obj|fbx|stl
  renders/quality/meshy_scene_registry.json

MCP alternative: once @meshy-ai/meshy-mcp-server is toggled on in Cursor,
call meshy_image_to_3d per scene from chat (see docs/MESHY_3D_MOTION_PIPELINE.md).
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

PROJECT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
MANIFEST = PROJECT / "scripts" / "meshy_scene_manifest.json"
OUT_ROOT = PROJECT / "assets" / "meshy" / "scenes"
REGISTRY = PROJECT / "renders" / "quality" / "meshy_scene_registry.json"
API = "https://api.meshy.ai/openapi/v1/image-to-3d"
POLL_SEC = 15
MAX_WAIT = 60 * 45  # 45 min per scene


def api_key() -> str:
    k = os.environ.get("MESHY_API_KEY") or os.environ.get("MESHY_API_KEY", "")
    if not k:
        # Windows User env
        try:
            import winreg  # noqa
        except ImportError:
            pass
    k = os.environ.get("MESHY_API_KEY", "")
    if not k:
        # read from User environment via subprocess-friendly check
        k = os.getenv("MESHY_API_KEY", "")
    if not k:
        raise SystemExit(
            "MESHY_API_KEY not set. Get key at https://www.meshy.ai/settings/api\n"
            "  setx MESHY_API_KEY msy_YOUR_KEY\n"
            "Or enable Meshy MCP in .cursor/mcp.json and generate from Cursor chat."
        )
    return k


def image_data_uri(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    if not mime:
        mime = "image/png"
    raw = path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{b64}"


def meshy_request(method: str, url: str, key: str, body: dict | None = None) -> dict:
    data = None
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Meshy HTTP {e.code}: {err[:600]}") from e


def create_task(key: str, scene: dict, defaults: dict) -> str:
    img_path = PROJECT / scene["source_image"]
    if not img_path.is_file():
        raise FileNotFoundError(img_path)
    payload = {
        **defaults,
        "image_url": image_data_uri(img_path),
        "texture_prompt": scene.get("texture_prompt", ""),
        "target_formats": scene.get("exports", defaults.get("target_formats", ["glb", "obj", "fbx", "stl"])),
    }
    resp = meshy_request("POST", API, key, payload)
    task_id = resp.get("result") or resp.get("id")
    if not task_id:
        raise RuntimeError(f"No task id in response: {resp}")
    return str(task_id)


def poll_task(key: str, task_id: str) -> dict:
    url = f"{API}/{task_id}"
    deadline = time.time() + MAX_WAIT
    while time.time() < deadline:
        data = meshy_request("GET", url, key)
        status = (data.get("status") or data.get("result", {}).get("status") or "").upper()
        progress = data.get("progress", data.get("result", {}).get("progress"))
        print(f"  poll {task_id} status={status} progress={progress}", flush=True)
        if status in ("SUCCEEDED", "SUCCESS", "COMPLETED"):
            return data
        if status in ("FAILED", "CANCELED", "CANCELLED"):
            raise RuntimeError(f"Meshy task failed: {data}")
        time.sleep(POLL_SEC)
    raise TimeoutError(f"Meshy task {task_id} timed out after {MAX_WAIT}s")


def download_url(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "AfricaS1-Meshy/1.0"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        dest.write_bytes(resp.read())


def extract_model_urls(task: dict) -> dict[str, str]:
    """Pull format URLs from Meshy task response."""
    urls: dict[str, str] = {}
    result = task.get("model_urls") or task.get("result", {}).get("model_urls") or {}
    if isinstance(result, dict):
        for fmt, url in result.items():
            if url and isinstance(url, str):
                urls[fmt.lower()] = url
    # alternate shapes
    for key in ("glb_url", "obj_url", "fbx_url", "stl_url"):
        if task.get(key):
            urls[key.replace("_url", "")] = task[key]
    arts = task.get("artifacts") or task.get("result", {}).get("artifacts") or []
    if isinstance(arts, list):
        for a in arts:
            if isinstance(a, dict):
                fmt = (a.get("format") or a.get("type") or "").lower()
                url = a.get("url")
                if fmt and url:
                    urls[fmt] = url
    return urls


def process_scene(key: str, scene: dict, defaults: dict, dry_run: bool = False) -> dict:
    sid = scene["id"]
    out_dir = OUT_ROOT / sid
    print(f"\n=== {sid} {scene['blender_scene']} ===", flush=True)
    img = PROJECT / scene["source_image"]
    print(f"  source: {img}", flush=True)
    if dry_run:
        return {"id": sid, "dry_run": True, "source": str(img)}

    task_id = create_task(key, scene, defaults)
    print(f"  task_id={task_id}", flush=True)
    task = poll_task(key, task_id)
    urls = extract_model_urls(task)
    if not urls:
        print(f"  WARN no model_urls; dumping keys: {list(task.keys())}", flush=True)
        (out_dir / "task_response.json").write_text(json.dumps(task, indent=2), encoding="utf-8")

    saved = {}
    for fmt, url in urls.items():
        ext = fmt if fmt.startswith(".") else f".{fmt}"
        dest = out_dir / f"{sid.lower()}_meshy{ext}"
        try:
            download_url(url, dest)
            saved[fmt] = str(dest)
            print(f"  saved {dest.name} ({dest.stat().st_size} bytes)", flush=True)
        except Exception as e:
            print(f"  FAIL download {fmt}: {e}", flush=True)

    if scene.get("animal_prompt"):
        note = out_dir / "animal_prompt.txt"
        note.write_text(scene["animal_prompt"], encoding="utf-8")

    return {
        "id": sid,
        "blender_scene": scene["blender_scene"],
        "task_id": task_id,
        "source_image": str(img),
        "files": saved,
        "motion": scene.get("motion", []),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", help="Only S01..S10 id")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    defaults = dict(manifest.get("meshy_defaults", {}))
    defaults["target_formats"] = manifest.get("exports", ["glb", "obj", "fbx", "stl"])

    key = "" if args.dry_run else api_key()
    registry = {"generated": [], "errors": []}
    if REGISTRY.is_file():
        try:
            registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        except Exception:
            pass

    scenes = manifest["scenes"]
    if args.scene:
        scenes = [s for s in scenes if s["id"].upper() == args.scene.upper()]

    for scene in scenes:
        try:
            rec = process_scene(key, scene, defaults, dry_run=args.dry_run)
            registry.setdefault("generated", []).append(rec)
        except Exception as e:
            print(f"ERROR {scene['id']}: {e}", flush=True)
            registry.setdefault("errors", []).append({"id": scene["id"], "error": str(e)})

    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    print(f"\nREGISTRY {REGISTRY}", flush=True)


if __name__ == "__main__":
    main()
