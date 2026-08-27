import json
import os
from pathlib import Path

# Directory to store project JSON files
PROJECTS_DIR = Path(__file__).resolve().parent.parent / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

def _project_path(project_id: str) -> Path:
    """Return the file path for a given project ID (sanitized)."""
    safe_id = "".join(c if c.isalnum() or c in "_-" else "_" for c in project_id)
    return PROJECTS_DIR / f"{safe_id}.json"

def save_plan(project_id: str, plan: dict) -> None:
    """Write ``plan`` atomically to ``project_id.json``."""
    path = _project_path(project_id)
    temp = path.with_suffix('.tmp')
    with open(temp, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    os.replace(temp, path)

def load_plan(project_id: str) -> dict | None:
    """Load a saved plan, returning ``None`` on missing or malformed file."""
    path = _project_path(project_id)
    if not path.exists():
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def list_projects() -> list[str]:
    """Return a list of stored project IDs (filenames without extension)."""
    return [p.stem for p in PROJECTS_DIR.glob('*.json')]
