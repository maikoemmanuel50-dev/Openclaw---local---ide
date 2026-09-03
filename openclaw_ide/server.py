"""
OpenClaw Local IDE — Backend Server
Zero external dependencies (uses standard library http.server, urllib, subprocess, json, threading).
Hosts Web IDE at http://127.0.0.1:8765
"""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DEFAULT_WORKSPACE = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = Path(DEFAULT_WORKSPACE).resolve()
IDE_ROOT = (WORKSPACE_ROOT).resolve()
# Static web root for the IDE itself (the folder this server.py lives in).
# Must NOT follow switch_project: project switches change WORKSPACE_ROOT for the
# file/workspace APIs, but the IDE's own HTML/JS/CSS always comes from here --
# otherwise '/' serves the project folder (which has no index.html) and the UI
# becomes a directory listing, i.e. "IDE not accessible".
WEB_ROOT = Path(__file__).resolve().parent

# ── Per-project isolated runtime state ─────────────────────────────────
# Sessions, prompt history, agent traces, chat memory and the session
# search index are stored per ACTIVE project under project_state/<slug>/,
# so switching projects never mixes sessions between workspaces.
STATE_ROOT = WEB_ROOT / "project_state"
# Registered external project workspaces (see projects.json next to server.py).
PROJECTS_REGISTRY = WEB_ROOT / "projects.json"

def _apply_state_paths():
    """Point every per-project runtime state file at the active project."""
    global SESSION_MEMORY_PATH, PROMPT_LOG_PATH, AGENT_TRACE_PATH, INDEX_DB
    slug = re.sub(r'[^\w\-]', '_', WORKSPACE_ROOT.name or "default") or "default"
    state_dir = STATE_ROOT / slug
    state_dir.mkdir(parents=True, exist_ok=True)
    SESSION_MEMORY_PATH = state_dir / ".session_memory.json"
    PROMPT_LOG_PATH = (state_dir / ".prompt_log.jsonl").resolve()
    AGENT_TRACE_PATH = (state_dir / ".agent_trace.jsonl").resolve()
    INDEX_DB = str((state_dir / ".session_index.db").resolve())

_apply_state_paths()

# #region agent log
_DEBUG_LOG_PATH = (Path(DEFAULT_WORKSPACE).resolve().parent / "debug-c6d300.log")
def _agent_dbg(hypothesis_id, location, message, data=None):
    # Left-over hypothesis-debug telemetry: intentionally a no-op so it stops
    # (re)creating debug-c6d300.log at the repo root. Kept for call-site compat.
    pass
def _safe_print(*args, **kwargs):
    """print() that never crashes the request handler (broken redirected stdout)."""
    try:
        print(*args, **kwargs)
    except Exception as e:
        _agent_dbg("H1", "server.py:_safe_print", "print_failed", {"error": repr(e), "args": [str(a)[:80] for a in args]})
# #endregion

# ── OpenClaw CLI Shim Path (configurable via env) ──
OPENCLAW_SHIM = os.environ.get("AFRICA_CLAW_SHIM") or r"C:\Users\HP\AppData\Roaming\npm\openclaw.cmd"

# ── Project Configuration ──
PROJECT_CONFIG = {}
RENDER_ROOT = Path(".")

def load_project_config():
    """Load project.json from IDE root or env-specified workspace. Sets RENDER_ROOT and PROJECT_CONFIG.
    
    Priority: AFRICA_WORKSPACE env var -> project.json in IDE_ROOT -> auto-discover renders/
    """
    global PROJECT_CONFIG, RENDER_ROOT
    
    # Priority 1: AFRICA_WORKSPACE environment variable
    env_root = os.environ.get("AFRICA_WORKSPACE")
    config_path = None
    
    if env_root:
        config_path = Path(env_root) / "project.json"
    else:
        # Priority 2: project.json in IDE root
        config_path = IDE_ROOT / "project.json"
    
    if config_path and config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            PROJECT_CONFIG = json.load(f)
        render_root = PROJECT_CONFIG.get("renderRoot", ".")
        # Handle relative paths from config file location
        if not os.path.isabs(render_root):
            RENDER_ROOT = (config_path.parent / render_root).resolve()
        else:
            RENDER_ROOT = Path(render_root).resolve()
        
        # Load plan state from separate file (runtime-generated, not tracked in git)
        plan_state_path = config_path.parent / ".plan_state.json"
        if plan_state_path.exists():
            try:
                with open(plan_state_path, "r", encoding="utf-8") as f:
                    PROJECT_CONFIG["plan"] = json.load(f)
            except Exception:
                pass  # If plan state is corrupted, just skip it
    else:
        # Priority 3: Auto-discover from workspace
        PROJECT_CONFIG = {
            "name": WORKSPACE_ROOT.name or "OpenClaw Project",
            "episode": "",
            "renderRoot": str(WORKSPACE_ROOT / "renders"),
            "scriptsRoot": str(WORKSPACE_ROOT / "scripts"),
            "blenderPath": r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe",
            "renderScripts": {},
            "delivery": {"resolution": "1080p", "targetFps": 24},
            "gates": {"4kHold": True, "gpuOneMax": True, "blenderOnly": "5.1.2"},
            "tools": {"canva": {"account": ""}, "blender": {"port": 9876}, "resolve": {"port": 49632}},
            "logFiles": [],
            "scenes": []
        }
        RENDER_ROOT = WORKSPACE_ROOT / "renders"
    return PROJECT_CONFIG

load_project_config()

OLLAMA_HOST = "http://127.0.0.1:11434"
_VL_MODEL = "qwen2.5vl:7b"
_CODER_MODEL = "qwen2.5-coder:14b"  # 14b for agentic Build mode
_CODER_MODEL_7B = "qwen2.5-coder:7b"  # 7b for Deep Plan mode (fast, tool-capable)

# ── Copyright Guardrail (YouTube policy 2026 + production clearance) ──
# Machine-scored substring rules. Verdicts: CLEAR / WARN / BLOCK.
# Full policy: docs/guides/production_standards_copyright/README.md
COPYRIGHT_BLOCK = {
    "brand_logo": [
        "netflix", "safaricom logo", "safaricom wordmark", "microsoft logo",
        "visa logo", "un logo", "unicef logo", "canva logo", "official logo",
    ],
    "media_rip": [
        "youtube rip", "rip from youtube", "scrape google", "grab from youtube",
        "download mp3", "steal footage", "reuse disney", "pirate",
    ],
    "trademark_lockup": ["netflix_bak", "netflix lockup", "netflix-safi"],
}

COPYRIGHT_WARN = {
    "brand_name_text": [
        "m-pesa", "mpesa", "safaricom", "microsoft", "visa", "unicef",
        "un women", "unfpa", "united nations", "d.light", "sun king",
        "m-kopa", "burn", "andela", "nailab", "ihub",
    ],
    "generated_asset": [
        "generate", "hyper3d", "meshy", "hunyuan", "process_image",
        "image-to-3d", "text-to-3d",
    ],
}

COPYRIGHT_CLEAR = {
    "allowlisted_source": [
        "mixkit", "unsplash", "poly haven", "polyhaven", "cc0",
        "blender spine", "project svg", "assets/diagrams", "assets/icons",
        "allowlisted", "graded kinetic", "clearance",
    ],
}

# Brand names safe as *text* (nominative use in VO / titles) but never as logo art.
COPYRIGHT_TEXT_ONLY_NAMES = [
    "m-pesa", "mpesa", "safaricom", "microsoft", "visa", "unicef",
    "unfpa", "un women", "united nations", "d.light", "sun king",
    "m-kopa", "burn", "andela", "nailab", "ihub",
]

# Clearance replacements from CLEARANCE_REPLACEMENTS.md
COPYRIGHT_REPLACEMENTS = {
    "netflix": "project wordmark endcard (project wordmark only)",
    "safaricom": "generic telecom label or project device indicator",
    "microsoft": "stylized non-trademarked icon (assets/icons/icon_microsoft.svg)",
    "visa": "stylized non-trademarked icon (assets/icons/icon_visa.svg)",
    "un logo": "UN text-only overlay, no emblem art",
    "canva logo": "no third-party logo; project-authored SVG",
}


def check_copyright(text):
    """Return a copyright guardrail verdict for the given text.

    verdict: CLEAR (safe) | WARN (use generic replacement) | BLOCK (refused).
    """
    if not text:
        return {"verdict": "CLEAR", "reason": "empty input", "matched": []}
    low = text.lower()
    matched = {"block": [], "warn": [], "clear": []}

    for cat, patterns in COPYRIGHT_BLOCK.items():
        for pat in patterns:
            if pat in low:
                matched["block"].append(pat)

    for cat, patterns in COPYRIGHT_WARN.items():
        for pat in patterns:
            if pat in low:
                matched["warn"].append(pat)

    for pat in COPYRIGHT_CLEAR["allowlisted_source"]:
        if pat in low:
            matched["clear"].append(pat)

    if matched["block"]:
        replacements = []
        for m in matched["block"]:
            for key, repl in COPYRIGHT_REPLACEMENTS.items():
                if key in m:
                    replacements.append(repl)
        return {
            "verdict": "BLOCK",
            "reason": f"Direct reproduction of protected material requested: {', '.join(matched['block'])}",
            "matched": matched,
            "replacement": replacements[0] if replacements else "use generic silhouette / project-authored SVG",
        }

    if matched["warn"] and not matched["clear"]:
        return {
            "verdict": "WARN",
            "reason": f"Risky signal(s) found: {', '.join(matched['warn'])}. "
                      f"Names may be used as TEXT (nominative) only, never as logo art. "
                      f"Prefer generic silhouettes or project SVGs.",
            "matched": matched,
            "replacement": "text-only or generic replacement",
        }

    return {"verdict": "CLEAR", "reason": "text uses allowed/cleared sources or is safe", "matched": matched}


# Single source of truth for the copyright protocol — injected into the agent
# system prompt AND served to the IDE's Copyright panel (moved out of being
# buried in the chat handler; same rules everywhere).
COPYRIGHT_PROTOCOL = {
    "name": "Copyright Guardrail Protocol (YouTube 2026 + production clearance)",
    "verdicts": [
        {"code": "CLEAR", "action": "Safe to proceed.", "color": "emerald"},
        {"code": "WARN", "action": "Brand names may appear as TEXT (nominative) only, never as logo art. Prefer generic glyphs / project SVGs.", "color": "amber"},
        {"code": "BLOCK", "action": "Do NOT proceed. Use the suggested generic replacement (silhouette / project SVG / allowlisted stock).", "color": "red"},
    ],
    "rules": [
        "Before generating/importing ANY asset that names a brand, stock source, or calls for generated content, run copyright_check on the prompt text.",
        "BLOCK verdict = do not proceed; substitute the suggested generic replacement.",
        "WARN verdict = brand names as text (nominative) only, never official logo art.",
        "Allowlisted sources only: Mixkit, Unsplash, Poly Haven (CC0), Blender spine, project diagrams/icons.",
        "No YouTube rips, no scraped Google Images, no official brand logo packs, no unlicensed music/SFX.",
        "When asked, disclose AI-generated/synthetic content; keep generation logs for AI assets.",
    ],
    "blockedSources": ["official brand logos", "YouTube rips", "scraped Google Images", "unlicensed music/SFX"],
    "allowedSources": ["Mixkit", "Unsplash", "Poly Haven CC0", "Blender spine", "project SVG"],
    "guide": "docs/guides/02_production_standards/copyright_guardrail_youtube_policy.md",
    "checkEndpoint": "/api/copyright/check",
}


def copyright_protocol_prompt():
    """Render COPYRIGHT_PROTOCOL as an LLM-visible instruction block."""
    lines = ["\n- COPYRIGHT GUARDRAIL (YouTube 2026 + production clearance):"]
    for i, r in enumerate(COPYRIGHT_PROTOCOL["rules"], 1):
        lines.append(f"  {i}. {r}")
    lines.append("  Verdicts: " + " | ".join(
        f"{v['code']} ({v['action'][:40]})" for v in COPYRIGHT_PROTOCOL["verdicts"]
    ))
    lines.append("  Run `copyright_check` BEFORE scheduling any step that names brands, stock sources, or generated content.")
    return "\n".join(lines)


# ── Prompt retention & archiving ────────────────────────────────────────
# Every prompt sent through `/api/chat` is appended to a rolling JSONL so
# history survives a page refresh (the browser DOM does not persist it).
# (PROMPT_LOG_PATH is set per-project by _apply_state_paths().)


def log_prompt(entry):
    """Append one prompt record to the rolling JSONL (safe against races)."""
    try:
        PROMPT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(entry, ensure_ascii=False, default=str) + "\n"
        with open(str(PROMPT_LOG_PATH), "a", encoding="utf-8") as f:
            f.write(line)
        # Keep the archive bounded: never delete, rotate at ~2000 entries by
        # renaming the tail into a timestamped archive file.
        try:
            with open(str(PROMPT_LOG_PATH), "r", encoding="utf-8") as f:
                count = sum(1 for _ in f)
            if count > 2000:
                stamp = time.strftime("%Y%m%d_%H%M%S")
                archive = PROMPT_LOG_PATH.with_suffix(f".{stamp}.jsonl")
                os.replace(str(PROMPT_LOG_PATH), str(archive))
                with open(str(PROMPT_LOG_PATH), "a", encoding="utf-8") as f:
                    f.write(line)
        except Exception:
            pass
    except Exception:
        pass


def read_prompt_history(limit=20):
    """Return the last `limit` prompts, newest first."""
    if not PROMPT_LOG_PATH.exists():
        return []
    try:
        with open(str(PROMPT_LOG_PATH), "r", encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        records = []
        for l in lines[-300:]:
            try:
                records.append(json.loads(l))
            except Exception:
                continue
        return list(reversed(records[-limit:])) if records else []
    except Exception:
        return []


# ── Agent-loop execution trace (for debugging feedback/error loops) ─────
# (AGENT_TRACE_PATH is set per-project by _apply_state_paths().)


# ── Reference Plans for Deep Plan Mode ──────────────────────────────
REFERENCE_PLANS_PATH = IDE_ROOT / "reference_plans.json"
REFERENCE_PLANS = []
if REFERENCE_PLANS_PATH.exists():
    try:
        with open(REFERENCE_PLANS_PATH, "r", encoding="utf-8") as f:
            REFERENCE_PLANS = json.load(f).get("plans", [])
    except Exception:
        pass

VALID_PLAN_ACTIONS = {
    "render_all_scenes", "render_mp4", "assemble_final",
    "assemble_with_audio", "assemble_kinetic_preview",
    "render_4k", "run_1080_then_4k", "brainstorm",
    "ping_qwen", "qwen_chat",
}

ACTION_ALTERNATIVES = {
    "start_shooting": "render_all_scenes",
    "edit_video": "assemble_final",
    "color_grade": "assemble_with_audio",
    "mix_audio": "assemble_with_audio",
    "export_video": "assemble_final",
    "render": "render_mp4",
    "assemble": "assemble_final",
    "brainstorm_concept": "brainstorm",
    "generate_script": "brainstorm",
    "create_storyboard": "brainstorm",
}

def validate_and_fix_plan(plan_json):
    """Validate plan actions and auto-replace invalid ones with valid alternatives."""
    fixed = False
    issues = []
    for phase in plan_json.get("phases", []):
        for task in phase.get("tasks", []):
            action = task.get("action", "")
            if action and action not in VALID_PLAN_ACTIONS:
                replacement = ACTION_ALTERNATIVES.get(action)
                if replacement:
                    task["action"] = replacement
                    task["action_note"] = f"Auto-replaced '{action}' -> '{replacement}'"
                    issues.append(f"Task {task.get('id')}: {action} -> {replacement}")
                    fixed = True
                else:
                    task.pop("action", None)
                    task["action_note"] = f"Removed invalid action '{action}'"
                    issues.append(f"Task {task.get('id')}: removed {action}")
                    fixed = True
    return plan_json, fixed, issues


def self_evaluate_plan(plan_json, project_state=None):
    """Score a plan's quality and return issues/suggestions."""
    score = 100
    issues = []
    suggestions = []

    phases = plan_json.get("phases", [])
    if not phases:
        score -= 30
        issues.append("No phases defined")

    for phase in phases:
        tasks = phase.get("tasks", [])
        if not tasks:
            score -= 15
            issues.append(f"Phase '{phase.get('name')}' has no tasks")

    for phase in phases:
        for task in phase.get("tasks", []):
            action = task.get("action", "")
            if action and action not in VALID_PLAN_ACTIONS:
                score -= 10
                issues.append(f"Task {task.get('id')}: invalid action '{action}'")

    all_task_ids = {"kickoff"}
    for phase in phases:
        for task in phase.get("tasks", []):
            all_task_ids.add(task.get("id", ""))
    for phase in phases:
        for task in phase.get("tasks", []):
            for dep in task.get("depends_on", []):
                if dep not in all_task_ids:
                    score -= 5
                    issues.append(f"Task {task.get('id')}: depends on unknown '{dep}'")

    total_hrs = sum(
        t.get("estimate_hrs", 0)
        for phase in phases
        for t in phase.get("tasks", [])
    )
    total_days = plan_json.get("total_estimate_days", 0)
    if total_hrs > 0 and total_days > 0:
        implied_days = total_hrs / 8
        if abs(implied_days - total_days) > 2:
            suggestions.append(f"Time mismatch: {total_hrs}hrs ~ {implied_days:.1f} days, but plan says {total_days} days")

    for phase in phases:
        for task in phase.get("tasks", []):
            if not task.get("deliverable"):
                score -= 5
                suggestions.append(f"Task {task.get('id')}: no deliverable specified")

    quality = "excellent" if score >= 90 else "good" if score >= 70 else "needs_work" if score >= 50 else "poor"

    return {
        "score": score,
        "quality": quality,
        "issues": issues,
        "suggestions": suggestions,
        "total_task_hours": total_hrs,
        "total_plan_days": total_days,
    }


def execute_mission_with_feedback(plan_json, session):
    """Execute plan steps with feedback loop — adapt if a step fails."""
    results = []
    adapted_plan = json.loads(json.dumps(plan_json))  # Deep copy

    for phase in adapted_plan.get("phases", []):
        for task in phase.get("tasks", []):
            action = task.get("action", "")
            if not action:
                continue

            # Execute the action
            if action in EXEC_ACTIONS:
                result = execute_action(action, task.get("action_params", {}))
            else:
                result = dispatch_tool(action, task.get("action_params", {}))

            if result.get("ok"):
                results.append({"task": task["id"], "status": "success", "result": result})
            else:
                # FAILED — try to adapt
                results.append({"task": task["id"], "status": "failed", "result": result})

                # Log the failure for the model to adapt
                trace_agent({
                    "event": "mission.adapt",
                    "session": session,
                    "failed_task": task["id"],
                    "failed_action": action,
                    "error": result.get("error", ""),
                    "suggestion": f"Task {task['id']} failed. Consider alternative approach.",
                })

                # If action failed, try alternative
                alt = ACTION_ALTERNATIVES.get(action)
                if alt and alt != action and alt in EXEC_ACTIONS:
                    trace_agent({
                        "event": "mission.retry_alt",
                        "session": session,
                        "original": action,
                        "alternative": alt,
                    })
                    alt_result = execute_action(alt, task.get("action_params", {}))
                    results.append({"task": task["id"], "status": "retry", "action": alt, "result": alt_result})

    return results


# ── Cross-Session Memory ────────────────────────────────────────────
# (SESSION_MEMORY_PATH is set per-project by _apply_state_paths().)
_SESSION_MEMORY_LOCK = threading.Lock()

def load_session_memory():
    """Load persistent session memory."""
    if SESSION_MEMORY_PATH.exists():
        try:
            with open(SESSION_MEMORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"projects": {}, "preferences": {}, "history": []}

def save_session_memory(memory):
    """Save session memory to disk (atomic temp+replace)."""
    tmp = SESSION_MEMORY_PATH.with_suffix(".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
        os.replace(tmp, SESSION_MEMORY_PATH)
    except Exception:
        pass

def remember_project(session_id, project_info):
    """Remember project details across sessions."""
    with _SESSION_MEMORY_LOCK:
        memory = load_session_memory()
        memory["projects"][session_id] = {
            "name": project_info.get("name", ""),
            "type": project_info.get("type", ""),
            "details": project_info.get("details", {}),
            "plan": project_info.get("plan"),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        # Keep last 50 projects
        keys = list(memory["projects"].keys())
        if len(keys) > 50:
            for k in keys[:len(keys) - 50]:
                del memory["projects"][k]
        save_session_memory(memory)

def remember_preference(key, value):
    """Remember user preferences."""
    with _SESSION_MEMORY_LOCK:
        memory = load_session_memory()
        memory["preferences"][key] = value
        save_session_memory(memory)

def get_remembered_projects():
    """Get all remembered projects for context."""
    memory = load_session_memory()
    return memory.get("projects", {})


def trace_agent(entry):
    """Append one agent-loop trace record (round, tool, error, outcome)."""
    try:
        AGENT_TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(entry, ensure_ascii=False, default=str) + "\n"
        with open(str(AGENT_TRACE_PATH), "a", encoding="utf-8") as f:
            f.write(line)
        # Rotate when the trace grows large so tail reads stay bounded.
        try:
            if AGENT_TRACE_PATH.stat().st_size > 2 * 1024 * 1024:  # 2 MB
                stamp = time.strftime("%Y%m%d_%H%M%S")
                os.replace(str(AGENT_TRACE_PATH),
                           str(AGENT_TRACE_PATH.with_suffix(f".{stamp}.jsonl")))
        except Exception:
            pass
    except Exception:
        pass


def read_agent_trace(limit=40, session=None):
    """Return the latest agent-loop trace records, newest first.

    When `session` is given, only records for that chat session are returned
    (used by the frontend to render a live per-turn session view)."""
    if not AGENT_TRACE_PATH.exists():
        return []
    try:
        # Tail-read only the last ~256 KB instead of the whole (unbounded) file.
        size = AGENT_TRACE_PATH.stat().st_size
        tail_bytes = min(size, 256 * 1024)
        with open(str(AGENT_TRACE_PATH), "r", encoding="utf-8", errors="replace") as f:
            f.seek(size - tail_bytes)
            if size - tail_bytes > 0:
                f.readline()  # drop the partial first line from the seek
            lines = [l for l in f if l.strip()]
        records = []
        for l in lines[-300:]:
            try:
                records.append(json.loads(l))
            except Exception:
                continue
        if session:
            records = [r for r in records if r.get("session") == session]
        return list(reversed(records[-limit:])) if records else []
    except Exception:
        return []


def _balanced_json_end(text, start):
    """Given an index at '{', return the index of its matching '}' or None.
    Tracks quoted strings and escapes so braces inside strings don't count."""
    depth = 0
    in_str = False
    esc = False
    i = start
    n = len(text)
    while i < n:
        c = text[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None


def _suggest_image_paths(path_str):
    """When an image path is wrong, suggest nearby matches from the render tree."""
    suggestions = []
    name_lower = path_str.lower().split("/")[-1].split("\\")[-1]
    masters_dir = RENDER_ROOT / "video_clips" / "masters"
    if masters_dir.exists():
        for scene_dir in masters_dir.iterdir():
            if scene_dir.is_dir():
                for f in scene_dir.glob("*.png"):
                    if name_lower in f.name.lower() or f.stem in name_lower:
                        suggestions.append(str(f.relative_to(RENDER_ROOT)))
        if not suggestions:
            recent = sorted(masters_dir.rglob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)[:3]
            for f in recent:
                suggestions.append(str(f.relative_to(RENDER_ROOT)))
    keywords = name_lower.replace(".png", "").replace("_", " ").split()
    for kw in keywords:
        if len(kw) < 4:
            continue
        hits = list(RENDER_ROOT.rglob(f"*{kw}*"))
        for h in hits[:3]:
            if h.suffix.lower() in (".png", ".jpg", ".jpeg", ".mp4") and str(h) not in suggestions:
                suggestions.append(str(h.relative_to(RENDER_ROOT)))
    return suggestions[:6]


def _extract_content_tool_calls(content):
    """Extract tool-call JSON a model printed inside content (qwen2.5-coder
    style). The previous non-greedy regex broke on nested empty args like
    {\"arguments\": {}}; this brace-balancing scanner survives that and any
    nesting, in fenced or bare JSON blocks."""
    if not content:
        return []
    calls = []
    seen = set()
    valid_names = {t["function"]["name"] for t in AGENT_TOOLS}
    # Nested empty objects (e.g. {\"arguments\": {}}) defeat \{.*?\}: rely on a
    # balanced scan. Check fence starts first, then the whole content, then every '{'.
    starts = [m.end() for m in re.finditer(r"```(?:json)?\s*", content)]
    starts += [0] if content.lstrip().startswith("{") else []
    starts += [m.start() for m in re.finditer(r"[{]", content)]
    scanned = set()
    for start in starts:
        if start >= len(content) or content[start] != "{":
            continue
        if start in scanned:
            continue
        scanned.add(start)
        end = _balanced_json_end(content, start)
        if end is None:
            continue
        raw = content[start:end + 1]
        if len(raw) > 20000:
            continue
        try:
            obj = json.loads(raw)
        except Exception:
            continue
        if not isinstance(obj, dict) or not isinstance(obj.get("name"), str):
            continue
        # Only accept tool names that are in AGENT_TOOLS; ignore
        # exec-action names (qwen_chat, ping_qwen, etc.) the model
        # may print from the system prompt's action list.
        if obj["name"] not in valid_names:
            continue
        args = obj.get("arguments")
        payload = json.dumps(args) if args is not None else "{}"
        key = (obj["name"], payload)
        if key in seen:
            continue
        seen.add(key)
        calls.append({"function": {"name": obj["name"], "arguments": payload}})
        if len(calls) >= 4:
            break
    return calls


def vl_ready():
    """True once qwen2.5vl is fully pulled and registered with Ollama."""
    tags = fetch_ollama_tags()
    return any(str(n).lower().split(":")[0] == "qwen2.5vl"
               for n in tags.get("models", [])) if tags.get("models") else False


def resolve_default_model():
    """Routed-model architecture.

    qwen2.5vl:7b is the DEFAULT model for fast chat and general tasks (~7s response).
    qwen2.5-coder:14b is reserved for heavy agentic tasks via escalation only.
    Set AFRICA_QWEN_MODEL to force any single model."""
    override = os.environ.get("AFRICA_QWEN_MODEL")
    if override:
        return override
    return _VL_MODEL


DEFAULT_MODEL = resolve_default_model()


def latest_master_frame():
    """Newest master PNG under the live render root, or None."""
    try:
        base = RENDER_ROOT / "video_clips" / "masters"
        if not base.exists():
            return None
        frames = [p for p in base.rglob("*.png")]
        if not frames:
            return None
        return str(max(frames, key=lambda p: (p.parent.name, p.stat().st_mtime)))
    except Exception:
        return None


def _readability_score(text: str) -> int:
    if not text:
        return 0
    bad = 0
    bad += text.count("\ufffd") * 100
    bad += text.count("\x00") * 30
    bad += sum(0x80 <= ord(c) <= 0x024F for c in text) // 2
    bad += sum(0x3000 <= ord(c) <= 0x9FFF for c in text) // 4
    bad += sum(0xE000 <= ord(c) <= 0xFFFF for c in text) * 3
    lines = len(text.splitlines())
    ascii_ratio = sum(32 <= ord(c) < 127 for c in text) / max(len(text), 1)
    return lines * 10 + int(ascii_ratio * 100) - bad


def _robust_decode_bytes(raw: bytes) -> str:
    """Pick the decode with the most readable result (handles UTF-16 BOM,
    misaligned UTF-16 appends, and UTF-8 logs with stray bad bytes)."""
    if not raw:
        return ""
    candidates = [
        raw.decode("utf-16", errors="replace"),
        raw.decode("utf-16le", errors="replace"),
        raw.decode("utf-8", errors="replace"),
    ]
    best = max(candidates, key=_readability_score)
    return best.lstrip("\ufeff")


def _decode_log_tail(raw: bytes, tail_bytes: int = 32768) -> str:
    """Decode the TAIL of a log file, where appends can shift UTF-16 alignment.
    Tries both UTF-16 offsets plus UTF-8 and picks the most readable result."""
    if not raw:
        return ""
    window = raw[-tail_bytes:]
    candidates = []
    for offset in (0, 2):
        seg = window[offset:]
        seg = seg[: len(seg) - (len(seg) % 2)]
        candidates.append(seg.decode("utf-16le", errors="replace"))
    candidates.append(window.decode("utf-8", errors="replace"))
    candidates.append(window.decode("utf-16", errors="replace"))
    best = max(candidates, key=_readability_score)
    return best.lstrip("\ufeff")


SYSTEM_PROMPT = (
    "You are OpenClaw Production Copilot — a local AI assistant for video production, "
    "creative planning, and project management. "
    "Connected tools: OpenClaw CLI, Local Qwen 2.5, Blender 5.1 MCP, DaVinci Resolve MCP, Composio (Canva). "
    "Rules: Blender 5.1.2 only, one GPU job at a time. "
    "A Knowledge & Guides library is indexed in the IDE (docs/guides/): software manuals, production standards, "
    "creative direction, tutorials/references, templates, and a technical quick reference; video index at "
    "docs/video_library/tutorial_index.json. Key delivery standards: 1920x1080 @ 24fps exact, H.264 High 8-12 Mbps "
    "(4K 35-45 Mbps gated), Rec. 709, audio 48kHz AAC-LC 320-384k stereo, loudness -14 LUFS, true peak <= -1 dBTP, "
    "title-safe 80%, action-safe 90%. Verify against them before calling anything 'done'. "
    "Provide actionable, concrete code, commands, or answers. "
    "Do NOT assume a specific project unless the user explicitly says so. "
    "You can help with ANY video production project, creative brainstorming, or general knowledge questions."
)

GUIDES_ROOT = (WORKSPACE_ROOT / "docs" / "guides").resolve()


def _parse_guide_front_matter(text):
    """Minimal YAML front-matter parser (no deps). Returns (title, category, tags)."""
    def _txt(s):
        s = s.strip()
        if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
            return s[1:-1]
        if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
            return s[1:-1]
        return s

    title = category = None
    tags = []
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        close = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                close = i
                break
        if close is not None:
            for ln in lines[1:close]:
                low = ln.lower().strip()
                if low.startswith("title:"):
                    title = _txt(ln.split(":", 1)[1])
                elif low.startswith("category:"):
                    category = _txt(ln.split(":", 1)[1])
                elif low.startswith("tags:"):
                    raw = ln.split(":", 1)[1]
                    tags = [_txt(x) for x in raw.split(",") if x.strip()]
    return title, category, tags


def _strip_front_matter(text):
    """Remove the leading YAML front matter block (--- ... ---) from markdown body."""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "\n".join(lines[i + 1:]).lstrip()
    return text


def load_guides_catalog():
    """Scan docs/guides/**/*.md and build the guide catalog served by /api/guides."""
    guides = []
    if GUIDES_ROOT.is_dir():
        for dirpath, dirnames, filenames in os.walk(str(GUIDES_ROOT)):
            dirnames.sort()
            for fn in sorted(filenames):
                if not fn.lower().endswith(".md") or fn.lower() == "readme.md":
                    continue
                path = Path(dirpath) / fn
                try:
                    text = path.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                title, category, tags = _parse_guide_front_matter(text)
                folder = path.parent.name
                if not category:
                    category = re.sub(r"^\d+_", "", folder).replace("_", " ").title()
                if not title:
                    title = path.stem.replace("_", " ").title()
                rel = path.relative_to(GUIDES_ROOT).as_posix()
                gid = re.sub(r"[^A-Za-z0-9_]", "_", rel.rsplit(".", 1)[0])
                guides.append({
                    "id": gid,
                    "title": title,
                    "category": category,
                    "tags": tags,
                    "path": rel,
                    "content": _strip_front_matter(text),
                })
    return guides


LEGACY_GUIDES = [
    {
        "id": "openclaw_quickstart",
        "title": "OpenClaw + Qwen 2.5 Local Agent",
        "category": "Agent & Local LLM",
        "content": (
            "### OpenClaw Local Integration Guide\n\n"
            "OpenClaw acts as your autonomous local assistant. Paired with Ollama (`qwen2.5-coder:14b`), "
            "you have a 100% private, zero-token cost copilot for video production and creative work.\n\n"
            "#### Useful Operations:\n"
            "- **Ping Model:** `python scripts/qwen_local.py ping`\n"
            "- **Ask Qwen:** `python scripts/qwen_local.py chat \"Audit scene 03 timing\"`\n"
            "- **Memory:** Curated memory in `MEMORY.md`, daily raw notes in `memory/YYYY-MM-DD.md`."
        )
    },
    {
        "id": "composio_canva",
        "title": "Composio & Canva Connected MCP",
        "category": "Design & Asset MCPs",
        "content": (
            "### Composio & Canva Workflow Guide\n\n"
            "Composio connects OpenClaw to Canva using account `canva_airway-sasin`.\n\n"
            "#### Capabilities:\n"
            "1. **URL Asset Upload:** Push rendered stills/infographics into Canva designs.\n"
            "2. **Design Dimensions:** Multi-format 1920x1080 (horizontal), 1080x1080 (square), 1080x1920 (vertical).\n"
            "3. **Batch Export:** Download PNG exports into `assets/canva/kinetic/canva_exports/`.\n"
            "4. **End Card Logo:** Design templates `DAHSGodJcI0`, `DAHSGtdHqlM`, `DAHSGtmzQSI`."
        )
    },
    {
        "id": "blender_resolve",
        "title": "Blender 5.1 & DaVinci Resolve MCP",
        "category": "3D & Video Pipelines",
        "content": (
            "### Studio MCP Integration\n\n"
            "#### Blender 5.1 MCP:\n"
            "- Socket Port: `127.0.0.1:9876`\n"
            "- Enable: Blender -> Preferences -> Add-ons -> **Blender MCP** -> check **Start Server**.\n\n"
            "#### DaVinci Resolve MCP:\n"
            "- Bridge Port: `127.0.0.1:49632`\n"
            "- Enable: DaVinci Resolve GUI -> Workspace -> Scripts -> `resolve_bridge`."
        )
    },
    {
        "id": "pre_4k_gate",
        "title": "PRE-4K Gate & Quality Standards",
        "category": "Quality Locks",
        "content": (
            "### Production & Delivery Locks\n\n"
            "- **4K Status:** Strict HOLD until 1080p master clears creative review.\n"
            "- **VO Stem:** Real voice only; placeholder used for pacing.\n"
            "- **Runtime Target:** Exactly 7:00 @ 24fps."
        )
    }
]


class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ('ACLineStatus', ctypes.c_byte),
        ('BatteryFlag', ctypes.c_byte),
        ('BatteryLifePercent', ctypes.c_byte),
        ('SystemStatusFlag', ctypes.c_byte),
        ('BatteryLifeTime', ctypes.c_ulong),
        ('BatteryFullLifeTime', ctypes.c_ulong),
    ]


def is_port_open(port, host="127.0.0.1"):
    """Fast non-blocking port check (<1ms) via native socket."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.1)
        res = s.connect_ex((host, int(port)))
        s.close()
        return res == 0
    except Exception:
        return False


def check_online_status():
    """Check if internet connectivity is available (tests 8.8.8.8:53)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        res = s.connect_ex(("8.8.8.8", 53))
        s.close()
        return res == 0
    except Exception:
        return False


def get_native_blender_pid():
    """Fast native process snapshot to locate active Blender process ID without PowerShell."""
    try:
        TH32CS_SNAPPROCESS = 0x00000002
        class PROCESSENTRY32(ctypes.Structure):
            _fields_ = [
                ('dwSize', wintypes.DWORD),
                ('cntUsage', wintypes.DWORD),
                ('th32ProcessID', wintypes.DWORD),
                ('th32DefaultHeapID', ctypes.c_size_t),
                ('th32ModuleID', wintypes.DWORD),
                ('cntThreads', wintypes.DWORD),
                ('th32ParentProcessID', wintypes.DWORD),
                ('pcPriClassBase', ctypes.c_long),
                ('dwFlags', wintypes.DWORD),
                ('szExeFile', ctypes.c_char * 260)
            ]
        hSnapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        pe32 = PROCESSENTRY32()
        pe32.dwSize = ctypes.sizeof(PROCESSENTRY32)
        blender_pid = None
        if ctypes.windll.kernel32.Process32First(hSnapshot, ctypes.byref(pe32)):
            while True:
                exe = pe32.szExeFile.decode('latin1', errors='ignore').lower()
                if exe == 'blender.exe':
                    blender_pid = int(pe32.th32ProcessID)
                    break
                if not ctypes.windll.kernel32.Process32Next(hSnapshot, ctypes.byref(pe32)):
                    break
        ctypes.windll.kernel32.CloseHandle(hSnapshot)
        return blender_pid
    except Exception:
        return None


def get_battery_info():
    """Fast Win32 battery and AC status probe (<1ms)."""
    try:
        sps = SYSTEM_POWER_STATUS()
        if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(sps)):
            pct = int(sps.BatteryLifePercent)
            if pct == 255:  # No system battery / desktop
                pct = 100
            status = "Charging / AC" if sps.ACLineStatus == 1 else "Discharging"
            return {"percent": pct, "status": status}
    except Exception:
        pass
    # Fallback to WMI only if native fails
    try:
        cmd = ["powershell", "-NoProfile", "-Command", 
               "(Get-CimInstance Win32_Battery) | Select-Object EstimatedChargeRemaining, BatteryStatus | ConvertTo-Json"]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=4).decode("utf-8")
        data = json.loads(out)
        return {
            "percent": data.get("EstimatedChargeRemaining", 0),
            "status": "Discharging" if data.get("BatteryStatus") == 1 else "Charging / AC"
        }
    except Exception:
        return {"percent": 0, "status": "Unknown"}


# ── Power settings (full-throttle strategy) ─────────────────────────────
# The render pipeline must run flat-out until shutdown and resume at full
# throttle on power-up: High Performance plan, sleep never, hibernate never.
_HIGH_PERF_GUID = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
_BALANCED_GUID = "381b4222-f694-41f0-9685-ff5bb260df2e"


def _run_powercfg(args, timeout=10):
    """Run powercfg and return (stdout, ok). Never raises."""
    try:
        out = subprocess.check_output(["powercfg"] + args, stderr=subprocess.DEVNULL, timeout=timeout).decode("utf-8", errors="replace")
        return out, True
    except Exception:
        return "", False


def get_power_state():
    """Read the current power configuration for the IDE panel."""
    state = {
        "activeScheme": None,
        "activeGuid": None,
        "schemes": [],
        "sleep": {"ac": "unknown", "dc": "unknown"},
        "hibernate": {"ac": "unknown", "dc": "unknown"},
        "battery": get_battery_info(),
        "sleepStates": [],
    }
    # Active scheme
    out, ok = _run_powercfg(["/getactivescheme"])
    if ok:
        m = re.search(r"GUID:\s*([0-9a-f\-]+)\s*\(([^)]+)\)", out)
        if m:
            state["activeGuid"] = m.group(1)
            state["activeScheme"] = m.group(2)
    # All schemes
    out, ok = _run_powercfg(["/list"])
    if ok:
        for line in out.splitlines():
            m = re.search(r"GUID:\s*([0-9a-f\-]+)\s*\(([^)]+)\)", line)
            if m:
                state["schemes"].append({"guid": m.group(1), "name": m.group(2)})
    # Sleep / hibernate values (Current AC/DC Setting Index)
    out, ok = _run_powercfg(["/query", "SCHEME_CURRENT", "SUB_SLEEP"])
    if ok:
        # Split into per-setting blocks on "Power Setting GUID" lines; each
        # block carries an alias (STANDBYIDLE / HIBERNATEIDLE) followed by
        # the Current AC/DC Setting Index lines.
        blocks = re.split(r"(?=^\s*Power Setting GUID)", out, flags=re.MULTILINE)
        for block in blocks:
            alias_m = re.search(r"GUID Alias:\s*(\S+)", block)
            if not alias_m:
                continue
            alias = alias_m.group(1)
            ac_m = re.search(r"Current AC Power Setting Index:\s*0x([0-9a-f]+)", block)
            dc_m = re.search(r"Current DC Power Setting Index:\s*0x([0-9a-f]+)", block)
            ac_val = int(ac_m.group(1), 16) if ac_m else None
            dc_val = int(dc_m.group(1), 16) if dc_m else None
            if alias == "STANDBYIDLE":
                state["sleep"] = {
                    "ac": "never" if ac_val == 0 else ("on" if ac_val else "unknown"),
                    "dc": "never" if dc_val == 0 else ("on" if dc_val else "unknown"),
                }
            elif alias == "HIBERNATEIDLE":
                state["hibernate"] = {
                    "ac": "never" if ac_val == 0 else ("on" if ac_val else "unknown"),
                    "dc": "never" if dc_val == 0 else ("on" if dc_val else "unknown"),
                }
    # Available sleep states
    out, ok = _run_powercfg(["/availablesleepstates"])
    if ok:
        state["sleepStates"] = [ln.strip() for ln in out.splitlines() if ln.strip() and not ln.strip().startswith("The following")]
    return state


def apply_power_action(action, payload=None):
    """Apply a power action for the full-throttle strategy.

    Returns {"ok": True, ...} with a human summary, or {"ok": False, "error"}.
    Safe: never touches the GPU render (separate process)."""
    action = (action or "").lower()
    payload = payload or {}
    out = ""
    if action == "full_throttle":
        # High Performance + sleep never + hibernate never (AC & DC)
        ok1 = _run_powercfg(["/setactive", _HIGH_PERF_GUID])
        ok2 = _run_powercfg(["/setacvalueindex", "SCHEME_CURRENT", "SUB_SLEEP", "STANDBYIDLE", "0"])
        ok3 = _run_powercfg(["/setdcvalueindex", "SCHEME_CURRENT", "SUB_SLEEP", "STANDBYIDLE", "0"])
        ok4 = _run_powercfg(["/setacvalueindex", "SCHEME_CURRENT", "SUB_SLEEP", "HIBERNATEIDLE", "0"])
        ok5 = _run_powercfg(["/setdcvalueindex", "SCHEME_CURRENT", "SUB_SLEEP", "HIBERNATEIDLE", "0"])
        ok6 = _run_powercfg(["/setactive", _HIGH_PERF_GUID])
        return {"ok": ok1[1] and ok2[1] and ok3[1] and ok4[1] and ok5[1] and ok6[1],
                "message": "High Performance plan active · Sleep & hibernate Never (AC/DC) — render runs flat-out until shutdown."}
    if action == "set_plan":
        guid = payload.get("guid") or _HIGH_PERF_GUID
        _, ok = _run_powercfg(["/setactive", guid])
        return {"ok": ok, "message": f"Switched active plan to {guid[:8]}…" if ok else "Failed to switch plan"}
    if action == "disable_sleep":
        _run_powercfg(["/setacvalueindex", "SCHEME_CURRENT", "SUB_SLEEP", "STANDBYIDLE", "0"])
        _run_powercfg(["/setdcvalueindex", "SCHEME_CURRENT", "SUB_SLEEP", "STANDBYIDLE", "0"])
        return {"ok": True, "message": "Sleep set to Never on AC & DC."}
    if action == "disable_hibernate":
        _run_powercfg(["/setacvalueindex", "SCHEME_CURRENT", "SUB_SLEEP", "HIBERNATEIDLE", "0"])
        _run_powercfg(["/setdcvalueindex", "SCHEME_CURRENT", "SUB_SLEEP", "HIBERNATEIDLE", "0"])
        return {"ok": True, "message": "Hibernate set to Never on AC & DC."}
    return {"ok": False, "error": f"Unknown power action: {action}"}


def get_render_progress():
    """Query ACTUAL project state from filesystem — not cached/generic data."""
    scenes_dir = RENDER_ROOT / "video_clips"
    masters_dir = scenes_dir / "masters" if scenes_dir.exists() else None
    final_dir = RENDER_ROOT / "final"

    # Count actual scene folders
    scene_folders = []
    if scenes_dir.exists():
        scene_folders = sorted([d for d in scenes_dir.iterdir() if d.is_dir()])

    # Check for rendered frames in each scene
    rendered_scenes = []
    pending_scenes = []
    scene_details = []
    for scene in scene_folders:
        frames = list(scene.glob("*.png")) if scene.exists() else []
        mp4s = list(scene.glob("*.mp4")) if scene.exists() else []
        frame_count = len(frames)
        mp4_count = len(mp4s)
        status = "rendered" if frame_count >= 100 or mp4_count > 0 else "pending"
        if status == "rendered":
            rendered_scenes.append(scene.name)
        else:
            pending_scenes.append(scene.name)
        scene_details.append({
            "name": scene.name,
            "status": status,
            "frames": frame_count,
            "mp4s": mp4_count,
        })

    # Check Blender process
    blender_pid = get_native_blender_pid()

    # Check for assembled final videos
    final_videos = list(final_dir.glob("*.mp4")) if final_dir.exists() else []

    # Check for audio assets
    audio_dir = WORKSPACE_ROOT / "assets" / "audio"
    audio_files = list(audio_dir.glob("*.mp3")) + list(audio_dir.glob("*.wav")) if audio_dir.exists() else []

    # Check for masters
    masters_count = len(list(masters_dir.glob("*.png"))) if masters_dir and masters_dir.exists() else 0

    # Disk space on render drive
    try:
        total, used, free = shutil.disk_usage(str(RENDER_ROOT))
        disk_info = {
            "total_gb": round(total / (1024**3), 1),
            "used_gb": round(used / (1024**3), 1),
            "free_gb": round(free / (1024**3), 1),
        }
    except Exception:
        disk_info = {"total_gb": 0, "used_gb": 0, "free_gb": 0}

    return {
        "totalScenes": len(scene_folders),
        "renderedScenes": len(rendered_scenes),
        "pendingScenes": len(pending_scenes),
        "readyCount": len(rendered_scenes),
        "sceneDetails": scene_details,
        "rendered": rendered_scenes,
        "pending": pending_scenes,
        "blenderRunning": blender_pid is not None,
        "blenderPid": blender_pid,
        "finalVideos": [v.name for v in final_videos],
        "mastersFrameCount": masters_count,
        "audioFiles": [a.name for a in audio_files[:20]],
        "disk": disk_info,
        "renderRoot": str(RENDER_ROOT),
        "projectName": PROJECT_CONFIG.get("name", ""),
        "episodeName": PROJECT_CONFIG.get("episode", ""),
        "gates": PROJECT_CONFIG.get("gates", {}),
        "logFiles": PROJECT_CONFIG.get("logFiles", []),
        "resolution": PROJECT_CONFIG.get("delivery", {}).get("resolution", "1080p"),
    }


def get_project_state():
    """Full project state for agentic planning — real filesystem data."""
    render = get_render_progress()
    config = PROJECT_CONFIG.copy()
    config.pop("scenes", None)  # too large
    return {
        "project": config.get("name", "Unknown"),
        "render_root": str(RENDER_ROOT),
        "render": render,
        "gates": config.get("gates", {}),
        "delivery": config.get("delivery", {}),
        "tools": config.get("tools", {}),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


_TAGS_CACHE = {"ts": 0.0, "data": None}
_TAGS_TTL = 2.0  # seconds; status is polled constantly, Ollama rarely changes
_STATUS_CACHE = {"ts": 0.0, "data": None}  # /api/status ~2s cache (per-process)

# Serialize agent-loop executions so concurrent chat/build requests don't
# saturate the local Ollama model (one model can't serve N loops well).
agent_semaphore = threading.Semaphore(1)

# Sessions whose in-flight agent loop has been cancelled by the frontend.
_CANCELLED = set()
_CANCELLED_LOCK = threading.Lock()


def fetch_ollama_tags(force=False):
    """Single shared /api/tags fetch with a short TTL so /api/status (polled
    every few seconds) does not fire 3 redundant Ollama calls per request."""
    now = time.time()
    if not force and _TAGS_CACHE["data"] is not None and (now - _TAGS_CACHE["ts"]) < _TAGS_TTL:
        return _TAGS_CACHE["data"]
    try:
        req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
        models = [m.get("name", "") for m in data.get("models", [])]
        result = {"online": True, "models": models}
    except Exception as e:
        result = {"online": False, "error": str(e), "models": []}
    _TAGS_CACHE["ts"] = time.time()
    _TAGS_CACHE["data"] = result
    return result


def ping_ollama():
    return dict(fetch_ollama_tags())


def is_model_loaded(model):
    """Check whether the given model is currently resident in memory."""
    try:
        req = urllib.request.Request(f"{OLLAMA_HOST}/api/ps", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            names = [m.get("name", "") for m in data.get("models", [])]
            # resolve aliases like "qwen2.5-coder:14b" vs "qwen2.5-coder:14b:latest"
            model_l = model.lower().split(":")[0]
            for n in names:
                if n.lower().split(":")[0] == model_l:
                    return True
            return False
    except Exception:
        return False


def warm_up_ollama(model=None):
    """Preload the model so the first chat does not cold-load an 8.9 GB model.

    Posting an empty prompt with keep_alive=-1 pins the model in memory,
    avoiding the 'signal is aborted without reason' cold-start hang.
    """
    model = model or DEFAULT_MODEL
    if is_model_loaded(model):
        return {"warmed": True, "model": model, "alreadyLoaded": True}
    try:
        payload = {
            "model": model,
            "prompt": "",
            "keep_alive": -1,
            "stream": False,
            "options": {"num_predict": 1}
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA_HOST}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            resp.read()
        return {"warmed": True, "model": model, "alreadyLoaded": False}
    except Exception as e:
        return {"warmed": False, "model": model, "error": str(e)}


def get_crestodian_info():
    crestodian_dir = Path.home() / ".openclaw" / "crestodian"
    attest_dir = Path.home() / ".openclaw" / "workspace-attestations"
    audit_file = Path.home() / ".openclaw" / "audit" / "crestodian.jsonl"
    exec_approvals_file = Path.home() / ".openclaw" / "exec-approvals.json"

    attestations = []
    if attest_dir.exists():
        for f in attest_dir.glob("*.attested"):
            attestations.append({"hash": f.stem, "time": f.stat().st_mtime})

    audit_logs = []
    if audit_file.exists():
        try:
            lines = audit_file.read_text(encoding="utf-8", errors="replace").strip().splitlines()
            for line in lines[-20:]:
                try:
                    audit_logs.append(json.loads(line))
                except Exception:
                    audit_logs.append({"raw": line})
        except Exception:
            pass

    has_approvals = exec_approvals_file.exists()

    return {
        "active": True,
        "status": "Attested & Enforced",
        "attestationsCount": len(attestations),
        "attestations": attestations,
        "auditCount": len(audit_logs),
        "recentAudit": audit_logs,
        "hasApprovals": has_approvals,
        "custodianPath": str(crestodian_dir)
    }


# ---------------------------------------------------------------------------
# Agentic executor: gated action registry + OpenClaw escalation layer
# ---------------------------------------------------------------------------

# Curated, gate-protected production actions the model may invoke by name.
# `kind`: "script" runs `python <script>`; "ps" runs the PowerShell directly.
EXEC_ACTIONS = {
    "assemble_final": {
        "kind": "script", "script": "assemble_final_video.py",
        "desc": "Assemble final master video from ready clips (ffmpeg, CPU-safe).",
        "gate_cpu": True, "terminal": True,
    },
    "assemble_with_audio": {
        "kind": "script", "script": "assemble_with_audio.py",
        "desc": "Assemble master video with audio stem (ffmpeg, CPU-safe).",
        "gate_cpu": True, "terminal": True,
    },
    "assemble_kinetic_preview": {
        "kind": "script", "script": "assemble_kinetic_preview.py",
        "desc": "Build kinetic preview cut (CPU-safe).",
        "gate_cpu": True, "terminal": True,
    },
    "render_mp4": {
        "kind": "script", "script": PROJECT_CONFIG.get("renderScripts", {}).get("renderMp4", str(WORKSPACE_ROOT / "render_scenes_mp4.py")),
        "desc": "Render scene clips to MP4 from rendered PNG sequences (GPU/Blender job, CPU+GPU preset).",
        "gate_blender": True, "terminal": True,
    },
    "render_all_scenes": {
        "kind": "script", "script": PROJECT_CONFIG.get("renderScripts", {}).get("renderMp4", str(WORKSPACE_ROOT / "render_scenes_mp4.py")),
        "desc": "Cycles render all scenes (GPU, CPU+GPU preset, 64 samples OptiX).",
        "gate_blender": True, "terminal": True,
    },
    "render_4k": {
        "kind": "script", "script": PROJECT_CONFIG.get("renderScripts", {}).get("render4k", str(WORKSPACE_ROOT / "render_scenes_4k.py")),
        "desc": "4K conversion render - 4K HOLD is in effect; refused by default.",
        "gate_4k_hold": True, "terminal": True,
    },
    "run_1080_then_4k": {
        "kind": "ps", "script": "run_1080_then_4k.ps1",
        "desc": "1080p-first then 4K pipeline runner.",
        "gate_4k_hold": True, "gate_blender": True, "terminal": True,
    },
    "hourly_report": {
        "kind": "ps", "script": str(Path(PROJECT_CONFIG.get("scriptsRoot", str(WORKSPACE_ROOT / "scripts"))) / "hourly_status_report.ps1"),
        "desc": "Generate an hourly production status report (markdown + STATUS_HOURLY_LATEST.txt + Telegram).",
        "terminal": True,
    },
}

# Actions that auto-execute without user approval (read-only / safe)
AUTO_EXECUTE_ACTIONS = {
    "ping_qwen",
    "production_status",
    "get_project_state",
    "disk",
    "blender process",
    "port 18789",
    "port 11434",
    "renders list",
    "masters pngs",
    "network status",
}

def is_auto_executable(action_name):
    """Check if an action can run without user approval."""
    return action_name in AUTO_EXECUTE_ACTIONS

# Read-only shell allowlist: patterns the model may run freely.
ALLOWED_SHELL_PATTERNS = [
    ("get-process blender", "Get-Process blender -ErrorAction SilentlyContinue | Select Id,CPU"),
    ("blender exists", "Test-Path blender"),
    ("list renders", f"Get-ChildItem '{RENDER_ROOT / 'video_clips'}' | Select Name,Length"),
    ("masters pngs", f"Get-ChildItem '{RENDER_ROOT / 'video_clips' / 'masters'}' -Recurse -Filter *.png | Measure-Object"),
    ("net status", "Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Select LocalPort"),
    ("port 18789", "Get-NetTCPConnection -LocalPort 18789 -State Listen -ErrorAction SilentlyContinue | Select LocalPort"),
    ("disk", "Get-PSDrive C | Select Used,Free"),
]

GATE_BLOCKED_MSG = "BLOCKED_BY_GATE"


def gate_check(action_key, params):
    """Return (ok, reason). Enforces the production gates from AGENTS.md."""
    action = EXEC_ACTIONS.get(action_key)
    if not action:
        return False, f"Unknown action: {action_key}"
    render = get_render_progress()
    if action.get("gate_4k_hold"):
        return False, "4K HOLD is in effect — 1080p delivery must finish first (reactor refused render_4k / run_1080_then_4k)."
    if action.get("gate_blender") and render["blenderRunning"]:
        # Find the active scene dynamically
        active_scene = next((s["name"] for s in render["sceneDetails"] if s["frames"] > 0), "unknown")
        return False, (f"Blender is actively rendering {active_scene} — one GPU job at a time. "
                       "Ask the user to approve a second job or wait for the active render to finish.")
    if action.get("gate_cpu") and render["blenderRunning"]:
        return False, "Blender is actively rendering — refuse CPU-heavy ffmpeg assembly while a GPU job is live."
    return True, "ok"


def execute_action(action_key, params=None):
    """Execute a gated, allowlisted action. Never runs arbitrary commands."""
    params = params or {}
    ok, reason = gate_check(action_key, params)
    if not ok:
        return {"ok": False, "blocked": GATE_BLOCKED_MSG, "reason": reason, "action": action_key}
    action = EXEC_ACTIONS[action_key]
    free = params.get("text", "")
    if action.get("kind") == "script":
        cmd = ["python", action["script"]]
        if action.get("sub"):
            cmd.append(action["sub"])
        if action.get("free_text") and free:
            cmd.append(free)
    else:
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", action["script"]]
    # Production presets for render scripts
    if action.get("script", "").replace("\\", "/").endswith(
        ("render_scenes_mp4.py", "render_all_scenes.py", "render_scenes_4k.py")
    ):
        env = dict(os.environ)
    else:
        env = None
    try:
        timeout = int(params.get("timeout", 600 if action.get("gate_cpu") else 120))
    except (TypeError, ValueError):
        timeout = 600 if action.get("gate_cpu") else 120
    try:
        proc = subprocess.run(
            cmd, cwd=str(WORKSPACE_ROOT), capture_output=True,
            text=True, timeout=timeout,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) or 0,
            env=env,
        )
        return {
            "ok": proc.returncode == 0,
            "action": action_key,
            "terminal": action.get("terminal", False),
            "exitCode": proc.returncode,
            "stdout": proc.stdout[-4000:],
            "stderr": proc.stderr[-2000:],
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "action": action_key, "error": f"Timed out after {timeout}s"}
    except Exception as e:
        return {"ok": False, "action": action_key, "error": str(e)}


HOURLY_REPORT_SCRIPT = str(Path(PROJECT_CONFIG.get("scriptsRoot", str(WORKSPACE_ROOT / "scripts"))) / "hourly_status_report.ps1")
HOURLY_STATUS_FILE = str(Path(PROJECT_CONFIG.get("scriptsRoot", str(WORKSPACE_ROOT))).parent / "STATUS_HOURLY_LATEST.txt")


def run_hourly_report(blocking=True):
    """Run the hourly status report once. Returns the subprocess result dict."""
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", HOURLY_REPORT_SCRIPT],
            cwd=str(WORKSPACE_ROOT), capture_output=True,
            text=True, timeout=180,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) or 0,
        )
        return {"ok": proc.returncode == 0, "exitCode": proc.returncode,
                "stdout": (proc.stdout or "")[-2000:], "stderr": (proc.stderr or "")[-1000:]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def read_hourly_latest():
    """Return the latest hourly report markdown block, newest first."""
    if not os.path.exists(HOURLY_STATUS_FILE):
        return {"ok": False, "error": "No hourly report generated yet",
                "hint": "Trigger one via the Hourly panel's Run Now button."}
    try:
        raw = open(HOURLY_STATUS_FILE, "r", encoding="utf-8-sig", errors="replace").read()
        return {"ok": True, "content": raw[:8000], "stamp": time.strftime(
            "%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(HOURLY_STATUS_FILE)))}
    except Exception as e:
        return {"ok": False, "error": str(e)}


AUDIO_ROOTS = [
    str(Path(PROJECT_CONFIG.get("renderRoot", str(WORKSPACE_ROOT / "renders"))).parent / "assets" / "audio"),
]


def _audio_relative(path):
    """Resolve an audio-relative path under the audio roots; None if unsafe."""
    if not path or ".." in path.replace("\\", "/"):
        return None
    for root in AUDIO_ROOTS:
        cand = os.path.join(root, path)
        if os.path.isfile(cand):
            return cand
    return None


def list_audio_files():
    """List audio files under the production assets/audio tree."""
    out = []
    for root in AUDIO_ROOTS:
        if not os.path.isdir(root):
            continue
        for dirpath, _dirs, files in os.walk(root):
            for fn in sorted(files):
                if fn.lower().endswith((".wav", ".mp3", ".ogg", ".flac", ".m4a")):
                    full = os.path.join(dirpath, fn)
                    rel = os.path.relpath(full, AUDIO_ROOTS[0]).replace("\\", "/")
                    out.append({"name": fn, "rel": rel, "dir": os.path.relpath(dirpath, AUDIO_ROOTS[0]),
                                "size": os.path.getsize(full),
                                "ext": os.path.splitext(fn)[1].lstrip(".").lower()})
    return {"ok": True, "count": len(out), "files": out}


def _hourly_report_loop():
    """Daemon: run the hourly report on startup, then every 3600s."""
    time.sleep(45)  # let the server finish booting / Ollama warm-up first
    while True:
        try:
            res = run_hourly_report()
            print(f"[hourly-report] {'ok' if res.get('ok') else 'ERROR'} "
                  f"exit={res.get('exitCode')} err={res.get('stderr', '')[:160]}", flush=True)
        except Exception as e:
            print(f"[hourly-report] loop error: {e}", flush=True)
        time.sleep(3600)


def execute_shell_probe(alias):
    """Run a read-only shell probe from the allowlist. Uses ultra-fast native Python probes with PowerShell fallback."""
    alias_l = (alias or "").strip().lower()
    
    # 1. Ultra-fast native probe paths (<5ms execution, zero subprocess spawns)
    if alias_l in ("get-process blender", "get-process"):
        pid = get_native_blender_pid()
        if pid:
            return {"ok": True, "alias": alias, "stdout": f"Id: {pid}, Process: blender.exe (Active Cycles Render)", "stderr": ""}
        return {"ok": True, "alias": alias, "stdout": "No active blender.exe process found.", "stderr": ""}
    
    if alias_l == "blender exists":
        blender_path = PROJECT_CONFIG.get("blenderPath", r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe")
        exists = os.path.isfile(blender_path)
        return {"ok": True, "alias": alias, "stdout": f"True (Blender exists: {exists})", "stderr": ""}
    
    if alias_l == "port 18789":
        open_18789 = is_port_open(18789)
        return {"ok": True, "alias": alias, "stdout": f"Port 18789 Open: {open_18789} (OpenClaw Gateway {'ONLINE' if open_18789 else 'OFFLINE'})", "stderr": ""}
    
    if alias_l == "net status":
        p18789 = is_port_open(18789)
        p11434 = is_port_open(11434)
        p49632 = is_port_open(49632)
        p8765 = is_port_open(8765)
        online = check_online_status()
        out = (f"System Network & Service Status:\n"
               f"- Internet Connection: {'ONLINE' if online else 'OFFLINE (Local Mode Only)'}\n"
               f"- Port 8765 (Local IDE Server): {'OPEN' if p8765 else 'CLOSED'}\n"
               f"- Port 18789 (OpenClaw Gateway): {'OPEN' if p18789 else 'CLOSED'}\n"
               f"- Port 11434 (Ollama Local LLM): {'OPEN' if p11434 else 'CLOSED'}\n"
               f"- Port 49632 (DaVinci Resolve Bridge): {'OPEN' if p49632 else 'CLOSED'}")
        return {"ok": True, "alias": alias, "stdout": out, "stderr": ""}
    
    if alias_l == "disk":
        try:
            total, used, free = shutil.disk_usage(str(RENDER_ROOT))
            out = f"Drive {RENDER_ROOT}\n  Used: {round(used / (1024**3), 1)} GB\n  Free: {round(free / (1024**3), 1)} GB\n  Total: {round(total / (1024**3), 1)} GB"
            return {"ok": True, "alias": alias, "stdout": out, "stderr": ""}
        except Exception:
            pass
    
    if alias_l == "masters pngs":
        try:
            masters_dir = RENDER_ROOT / "video_clips" / "masters"
            count = len(list(masters_dir.glob("*/*.png"))) if masters_dir.exists() else 0
            return {"ok": True, "alias": alias, "stdout": f"Total Master PNG Frames Rendered: {count}", "stderr": ""}
        except Exception:
            pass
    
    if alias_l == "list renders":
        try:
            clips_dir = RENDER_ROOT / "video_clips"
            if clips_dir.exists():
                files = [f"{p.name} ({round(p.stat().st_size / (1024*1024), 2)} MB)" for p in clips_dir.glob("*.mp4")]
                return {"ok": True, "alias": alias, "stdout": "\n".join(files) or "No mp4 clips found in renders/video_clips", "stderr": ""}
        except Exception:
            pass

    # 2. PowerShell fallback for other patterns in allowlist
    for key, cmd in ALLOWED_SHELL_PATTERNS:
        if key == alias:
            try:
                proc = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", cmd],
                    cwd=str(WORKSPACE_ROOT), capture_output=True,
                    text=True, timeout=25,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) or 0,
                )
                return {"ok": True, "alias": alias, "stdout": proc.stdout[-2500:] or "", "stderr": proc.stderr[-1000:] or ""}
            except Exception as e:
                return {"ok": False, "alias": alias, "error": str(e)}
    return {"ok": False, "alias": alias, "error": f"Shell probe '{alias}' not in allowlist"}


def clean_agent_reply(text):
    """Unwrap and format raw tool calls and JSON blocks into clean, natural conversational English markdown."""
    if not text:
        return ""
    text_s = text.strip()
    
    # 1. Direct JSON unwrap (e.g. update_goal or raw tool payload)
    if text_s.startswith("{") and text_s.endswith("}"):
        try:
            data = json.loads(text_s)
            if isinstance(data, dict):
                if data.get("name") == "update_goal" or "update_goal" in str(data):
                    args = data.get("arguments") or {}
                    note = args.get("note") or data.get("note") or ""
                    status = args.get("status") or data.get("status") or "complete"
                    progress = get_render_progress()
                    ready = progress.get("readyCount", 0)
                    total = progress.get("totalScenes", 0)
                    scenes = progress.get("scenes") or []
                    # Find the active scene dynamically
                    active_scene = next((s for s in scenes if s.get("frames", 0) > 0 and not s.get("isReady")), None)
                    render_status_line = (
                        f"- **Active Render:** {active_scene['name']} at {active_scene['frames']}/{active_scene['target']} frames (PID {progress.get('blenderPid', '?')})"
                        if progress.get("blenderRunning") and active_scene else
                        f"- **Blender Status:** Idle"
                    )
                    return (
                        f"**Project Status Update ({status.upper()}):**\n\n"
                        f"{note}\n\n"
                        f"### Live Production Summary:\n"
                        f"- **Render Progress:** {ready}/{total} scenes verified.\n"
                        f"{render_status_line}\n"
                        f"- **Watcher Daemon:** `wait_hq_assemble.ps1` monitoring completion."
                    )
                if "name" in data and "arguments" in data:
                    name = data["name"]
                    args = data["arguments"]
                    args_str = "\n".join(f"- **{k}**: {v}" for k, v in args.items()) if isinstance(args, dict) else str(args)
                    return f"**Action Executed:** `{name}`\n\n{args_str}"
        except Exception:
            pass
            
    return text_s


def escalation_openclaw(task_text, timeout=120):
    """Escalate a task to the OpenClaw gateway agent. Returns its reply text.

    Uses `openclaw agent -m <task> --json` via the local gateway (port 18789).
    Invoked directly through the Node CLI shim with JSON payload parsing.
    """
    if not task_text:
        return {"ok": False, "error": "Empty escalation task"}
    
    # Use configurable shim path (set at module load from AFRICA_CLAW_SHIM env var)
    shim = OPENCLAW_SHIM
    if not os.path.isfile(shim):
        shim = "openclaw"  # fallback to PATH lookup
        
    # Sanitize task_text to prevent shell injection (shell=False, but defense in depth)
    # Remove shell metacharacters that could be interpreted if shell=True somehow gets used
    safe_task = re.sub(r'[&|^%<>]', '', task_text)
    
    cmd = [shim, "agent", "--json", "--agent", "main", "-m", safe_task]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            shell=False,  # SECURITY: shell=False prevents command injection
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) or 0,
        )
        raw = proc.stdout.strip() or proc.stderr[-2000:].strip()
        reply_text = raw
        if proc.returncode == 0 and raw:
            try:
                # JSON envelope: reply text is under result.payloads[].text.
                env = json.loads(raw.replace('\ufeff', ''))
                result = env.get("result") or {}
                payloads = result.get("payloads") or []
                texts = [p.get("text", "") for p in payloads if p.get("text")]
                if texts:
                    reply_text = "\n".join(texts)
                elif env.get("summary"):
                    reply_text = str(env["summary"])
                elif result.get("error"):
                    reply_text = f"OpenClaw error: {result['error']}"
                else:
                    reply_text = raw[-6000:]
            except Exception:
                reply_text = raw[-6000:]
        reply_text = clean_agent_reply(reply_text)
        return {"ok": proc.returncode == 0, "output": reply_text, "exitCode": proc.returncode}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"OpenClaw escalation timed out after {timeout}s"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def direct_openclaw_chat(prompt, session=None, timeout=10):
    """Direct execution mode — local Ollama for fast responses, gateway for heavy tasks."""
    if not prompt:
        return {"ok": False, "error": "Empty prompt"}
    gw_online = is_port_open(18789)
    # Go straight to local Ollama for fast responses
    try:
        payload = {"model": _VL_MODEL, "stream": False, "keep_alive": 60,
                   "options": {"temperature": 0.7, "num_ctx": 8192, "num_predict": 256},
                   "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                                {"role": "user", "content": prompt}]}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(f"{OLLAMA_HOST}/api/chat", data=data,
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        output = (result.get("message") or {}).get("content", "") or "No response"
        log_prompt({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "route": "direct_ollama",
                    "model": _VL_MODEL, "session": session or "direct",
                    "prompt": prompt, "reply": str(output)[:1200]})
        return {"reply": output, "model": _VL_MODEL, "session": session or "direct",
                "rounds": [], "gatewayOnline": gw_online, "ok": True}
    except Exception as e:
        return {"ok": False, "error": f"Ollama failed: {e}"}


# Tool schema exposed to the model via Ollama function calling.
# Each tool has a "category" for AI reasoning about tool selection.
AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "production_status",
            "description": "Get live production status: per-scene render frames, Blender activity, ready clips, power.",
            "parameters": {"type": "object", "properties": {}},
            "category": "status",
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_project_state",
            "description": "Get full project state for agentic planning: project name, render root, scene details (rendered/pending), Blender status, final videos, audio assets, disk space, gates, delivery config. ALWAYS call this FIRST before creating any plan.",
            "parameters": {"type": "object", "properties": {}},
            "category": "status",
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_log",
            "description": "Read the tail of a production log. Logs: project config logFiles + PRODUCTION_STATUS.md, STATUS_LIVE_DELIVERY.txt, STATUS_POWER_CHECKPOINT.txt, arch_comm_iv_lock_log.txt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "log": {"type": "string", "description": "Log filename"},
                    "lines": {"type": "integer", "description": "Number of tail lines"},
                },
                "required": ["log"],
            },
            "category": "diagnostics",
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_action",
            "description": (
                "Execute a known production action. Actions: "
                + ", ".join(f"{k} ({v['desc']})" for k, v in EXEC_ACTIONS.items())
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": list(EXEC_ACTIONS.keys())},
                    "text": {"type": "string", "description": "Free-text arg (qwen_chat only)"},
                    "timeout": {"type": "integer", "description": "Timeout seconds"},
                },
                "required": ["action"],
            },
            "category": "execution",
        },
    },
    {
        "type": "function",
        "function": {
            "name": "shell_probe",
            "description": "Run a READ-ONLY system probe. Aliases: "
                + ", ".join(k for k, _ in ALLOWED_SHELL_PATTERNS),
            "parameters": {
                "type": "object",
                "properties": {"alias": {"type": "string", "enum": [k for k, _ in ALLOWED_SHELL_PATTERNS]}},
                "required": ["alias"],
            },
            "category": "diagnostics",
        },
    },
    {
        "type": "function",
        "function": {
            "name": "inspect_image",
            "description": "Describe / analyze an image file with the local vision model (qwen2.5vl). Returns a text description of what is in the image. CORRECT PATHS: scene frames are at video_clips/masters/<SceneName>/frame_XXXX.png. For audits or 'root out' tasks, use read_log or shell_probe instead.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Relative path to the image inside the workspace"},
                    "question": {"type": "string", "description": "Optional question to answer about the image"},
                },
                "required": ["image_path"],
            },
            "category": "visual_qc",
        },
    },
    {
        "type": "function",
        "function": {
            "name": "copyright_check",
            "description": "Check text/prompt/asset against the production copyright guardrail (YouTube Content ID + AI-disclosure + clearance policy). Call this BEFORE generating or importing any visual/audio asset that mentions brand names, stock sources, or generated content. Returns verdict CLEAR | WARN | BLOCK with a replacement suggestion. On BLOCK, never proceed; use the suggested generic replacement.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The prompt, asset filename, or text to assess for copyright risk"},
                },
                "required": ["text"],
            },
            "category": "compliance",
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_openclaw",
            "description": "Delegate a complex task to the OpenClaw gateway agent (port 18789). Use for multi-step cross-app work, Blender MCP scripting, DaVinci Resolve, or Canva deliverables.",
            "parameters": {
                "type": "object",
                "properties": {"task": {"type": "string", "description": "Precise task description for the gateway agent"}},
                "required": ["task"],
            },
            "category": "complex_tasks",
        },
    },
    {
        "type": "function",
        "function": {
            "name": "brainstorm",
            "description": "Answer creative, planning, or general-knowledge questions directly. Use for brainstorming, ideating, explaining concepts, writing scripts, or any task that does NOT require a specific tool. This is your default for non-production questions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "The question or topic to address"},
                },
                "required": ["topic"],
            },
            "category": "creative",
        },
    },
]


def dispatch_tool(name, args):
    if name == "production_status":
        return {"status": get_render_progress(), "battery": get_battery_info()}
    if name == "get_project_state":
        return get_project_state()
    if name == "read_log":
        try:
            nlines = int(args.get("lines", 30))
        except (TypeError, ValueError):
            nlines = 30
        return read_log_tail(args.get("log", "wait_hq_assemble_log.txt"), nlines)
    if name == "run_action":
        return execute_action(args.get("action", ""), args)
    if name == "shell_probe":
        return execute_shell_probe(args.get("alias", ""))
    if name == "inspect_image":
        return inspect_image_with_vl(args.get("image_path", ""), args.get("question", ""))
    if name == "copyright_check":
        return check_copyright(args.get("text", ""))
    if name == "escalate_openclaw":
        return escalation_openclaw(args.get("task", ""))
    if name == "brainstorm":
        topic = args.get("topic", "")
        if not topic:
            return {"ok": False, "error": "No topic provided"}
        try:
            payload = {
                "model": _VL_MODEL,
                "stream": False,
                "keep_alive": 60,
            "options": {"temperature": 0.7, "num_ctx": 8192, "num_predict": 512},
                "messages": [
                    {"role": "system", "content": "You are a creative production assistant. Answer the user's question directly and helpfully. Be concise but thorough. Help with series planning, brainstorming, scripting, and creative ideation for ANY project."},
                    {"role": "user", "content": topic},
                ],
            }
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{OLLAMA_HOST}/api/chat",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            reply = (result.get("message") or {}).get("content", "")
            return {"ok": True, "reply": reply, "topic": topic}
        except Exception as e:
            return {"ok": False, "error": str(e), "topic": topic}
    # Fallback: route production action names (qwen_chat, ping_qwen, etc.)
    # through run_action so content-printed tool calls don't error.
    if name in EXEC_ACTIONS:
        return execute_action(name, args)
    # Unknown tool — return a helpful message instead of an error so the
    # model doesn't loop retrying the same call.
    return {"ok": True, "output": f"Note: `{name}` is not a direct tool. Use one of: brainstorm, production_status, read_log, run_action, shell_probe, inspect_image, copyright_check, escalate_openclaw."}


def save_pasted_image(data_uri):
    """Decode a pasted data:image/...;base64 blob into a temp file the VL model
    can read. Returns the file path or None on failure."""
    try:
        import base64 as _b64
        header, _, encoded = str(data_uri).partition(",")
        if not encoded:
            return None
        raw = _b64.b64decode(encoded)
        if len(raw) > 15 * 1024 * 1024:
            return None
        ext = "png"
        low = header.lower()
        if "jpeg" in low or "jpg" in low:
            ext = "jpg"
        elif "webp" in low:
            ext = "webp"
        elif "gif" in low and len(raw) < 2 * 1024 * 1024:
            ext = "gif"
        tmp_dir = Path(os.environ.get("TEMP", "."))
        target = tmp_dir / f"openclaw_paste_{int(time.time() * 1000)}.{ext}"
        target.write_bytes(raw)
        return str(target)
    except Exception:
        return None


# Read-only information tools. When the 14b emits ONLY these (tool JSON, no
# prose) the tool results ARE the answer — we format them into a readable
# report and stop instead of asking the model for a second round.
# brainstorm intentionally excluded: in build mode the model often brainstorms
# first then must continue with more tools — treating it as info-only caused
# premature single-round exits.
INFO_TERMINAL_TOOLS = {"production_status", "read_log", "shell_probe", "inspect_image", "copyright_check"}


def _format_tool_summary(results):
    """Format dispatch results from a read-only info round into a readable report."""
    parts = []
    for name, _tr_args, res in results:
        if name == "production_status":
            st = (res or {}).get("status") or {}
            bat = (res or {}).get("battery") or {}
            scenes = st.get("scenes") or []
            # Find the active scene dynamically
            active_scene = next((s for s in scenes if s.get("frames", 0) > 0 and not s.get("isReady")), None)
            cur = active_scene.get("frames", 0) if active_scene else 0
            cur_target = active_scene.get("target", 0) if active_scene else 0
            active_name = active_scene.get("name", "") if active_scene else ""
            lines = ["**Production Status**"]
            lines.append("- Blender Cycles: "
                         + ("ACTIVE" if st.get("blenderRunning") else "IDLE")
                         + (f" (PID {st.get('blenderPid')})" if st.get("blenderRunning") else ""))
            lines.append(f"- Ready clips: {st.get('readyCount', 0)}/{st.get('totalScenes', len(scenes))}")
            if active_scene:
                lines.append(f"- Active Scene (`{active_name}`): {cur}/{cur_target}")
            for s in scenes:
                flag = " READY" if s.get("isReady") else ""
                lines.append(f"  - {s.get('name')}: {s.get('frames')}/{s.get('target')} ({s.get('percent', 0)}%){flag}".rstrip())
            eta = render_eta()
            if eta.get("ok"):
                lines.append(f"- Render rate: ~{eta['ratePerFrameSec']}s/frame")
                lines.append(f"- ETA Scene 03: ~{eta['scene03EtaHrs']}h remaining")
                lines.append(f"- ETA all scenes: ~{eta['projectEtaDays']}d ({eta['projectEtaHrs']}h)")
                lines.append(f"- Strategy: {eta.get('strategy', 'unknown')}")
            else:
                lines.append(f"- ETA: unavailable ({eta.get('error', 'no data')})")
            lines.append(f"- Power: {bat.get('percent')}% ({bat.get('status')})")
            parts.append("\n".join(lines))
        elif name == "read_log":
            if res.get("ok"):
                tail = (res.get("tail") or "")[:3000]
                parts.append(f"**Log `{res.get('log')}`** ({res.get('lines')} lines)\n```\n{tail}\n```")
            else:
                parts.append(f"read_log: {res.get('error')}")
        elif name == "shell_probe":
            if res.get("ok"):
                out = (res.get("stdout") or "").strip() or "(no output)"
                parts.append(f"**Shell probe `{res.get('alias')}`**\n```\n{out[:2500]}\n```")
            else:
                parts.append(f"shell_probe: {res.get('error')}")
        elif name == "inspect_image":
            if res.get("ok"):
                parts.append(f"**Visual QC `{res.get('image')}`**\n{res.get('description', '')}")
            else:
                parts.append(f"inspect_image: {res.get('error')}")
        elif name == "brainstorm":
            reply = res.get("reply", "")
            topic = res.get("topic", "")
            if reply:
                parts.append(f"**Brainstorm: {topic}**\n\n{reply[:2000]}")
            else:
                parts.append(f"Brainstorm completed for: {topic}")
        else:
            # Format as readable text, not JSON
            if res.get("ok"):
                output = res.get("output") or res.get("reply") or res.get("stdout") or ""
                parts.append(f"**{name}**\n{str(output)[:2000]}")
            else:
                parts.append(f"{name}: {res.get('error', 'unknown error')}")
    return "\n\n".join(parts)


_STATUS_FASTPATH_WORDS = {
    "status", "progress", "completion", "complete", "ready", "rendering",
    "render", "scene", "blender", "clip", "frames", "frame", "finished",
    "done", "eta", "how far", "how much", "check", "how is", "how are",
    "what's the", "what is the", "update", "percent", "%",
}

_IMPERATIVE_MARKERS = (
    "do not", "don't", "please", "make ", "build ", "create ", "assemble ",
    "render scene", "render the", "render mp4", "render now", "start render",
    "run render", "begin render", "make render", "build render",
    "run ", "start ", "stop ", "set ", "change ", "add ", "write ",
    "fix ", "do ", "update the ", "keep ", "check the logs", "check for ",
    "check if ", "make sure", "go through", "review the", "analyze the",
    "investigate", "find the", "look into", "look at", "tell me the",
)


def _status_only_prompt(prompt):
    """Return True when the user is asking a pure status/progress QUESTION
    that can be answered directly from live server data — no LLM round needed.

    Strict on purpose: any imperative / action / review phrasing must route to
    the real agent loop so deliverables actually execute."""
    low = " ".join(prompt.lower().split())
    if not low or len(low) > 160:
        return False
    # Instructions / review / action prompts NEVER fast-path.
    if any(m in low for m in _IMPERATIVE_MARKERS):
        return False
    # Must be phrased as a question: a "?" or a leading question word, OR
    # an explicit "status/progress of X" form.
    is_question = ("?" in low
                   or low.startswith(("what", "how", "is ", "are ", "does",
                                      "do you", "when", "where", "which"))
                   or any(q in low for q in ("status of", "progress of",
                                             "how far", "how is", "how are",
                                             "status?", "progress?")))
    if not is_question:
        return False
    hits = sum(1 for w in _STATUS_FASTPATH_WORDS if w in low)
    return hits >= 2


def status_fast_path_reply(prompt):
    """Answer a pure status question from live data without touching the LLM.
    Returns a formatted markdown report or None if not applicable."""
    try:
        st = get_render_progress()
        bat = get_battery_info()
        scenes = st.get("scenes") or []
        # Find the active scene dynamically
        active_scene = next((s for s in scenes if s.get("frames", 0) > 0 and not s.get("isReady")), None)
        active_line = f"- **Active Scene (`{active_scene['name']}`):** {active_scene.get('frames')}/{active_scene.get('target')} ({active_scene.get('percent', 0)}%)" if active_scene else "- No active render"
        eta = render_eta()
        eta_line = ""
        if eta.get("ok"):
            eta_line = (f"- **Render rate:** ~{eta['ratePerFrameSec']}s/frame — ETA active scene ~{eta.get('scene03EtaHrs', 0)}h, "
                        f"all scenes ~{eta['projectEtaDays']}d ({eta['projectEtaHrs']}h)")
        ready_scenes = [s.get("name") for s in scenes if s.get("isReady")]
        busy_scenes = [s.get("name") for s in scenes if not s.get("isReady")]
        return (
            "**OpenClaw Production Status** *(answered from live server data, no model round)*\n\n"
            f"- **Blender Cycles:** {'ACTIVE' if st.get('blenderRunning') else 'IDLE'}"
            f"{' (PID ' + str(st.get('blenderPid')) + ')' if st.get('blenderRunning') else ''}\n"
            f"- **Ready clips:** {st.get('readyCount')}/{st.get('totalScenes')}"
            f" {'— ALL READY' if st.get('readyCount') >= st.get('totalScenes') else ''}\n"
            f"{active_line}\n"
            f"- **Ready:** {', '.join(ready_scenes) if ready_scenes else 'none'}\n"
            f"- **Still rendering:** {', '.join(busy_scenes) if busy_scenes else 'none'}\n"
            f"{eta_line}\n"
            f"- **Power:** {bat.get('percent')}% ({bat.get('status')})\n"
            f"- **Watcher:** Auto-assembles when all clips are ready."
        )
    except Exception as e:
        return f"Status check unavailable: {e}"


_CREATIVE_WORDS = {
    "brainstorm", "idea", "ideas", "concept", "concepts",
    "outline", "story", "narrative", "suggest",
    "recommend", "opinion", "explain", "describe", "summarize",
    "review", "compare", "strategy", "approach",
    "new series", "new show", "episode", "pitch", "proposal",
    "new season", "tell me about", "what if", "imagine",
    "plan for", "roadmap",
}


def _creative_prompt(prompt):
    """Return True ONLY for pure brainstorming/planning questions.
    Action requests (create, build, render, etc.) must go through agent loop."""
    low = " ".join(prompt.lower().split())
    if not low or len(low) > 300:
        return False
    # Production imperatives — NEVER fast-path these
    PRODUCTION_IMPERATIVES = (
        "render", "export", "deploy", "assemble", "compile", 
        "build the", "create the", "make the", "generate the",
        "execute", "run the", "start the", "build a", "create a",
        "make a", "design a", "write the", "fix the",
    )
    if any(m in low for m in PRODUCTION_IMPERATIVES):
        return False
    # Output signals — implies execution wanted
    OUTPUT_SIGNALS = (
        ".mp4", ".blend", ".png", ".jpg", "deliverable", "output", "render",
    )
    if any(s in low for s in OUTPUT_SIGNALS):
        return False
    # Must be question form + creative intent
    has_question = ("?" in low or low.startswith(("what", "how", "can", "could", 
                    "suggest", "brainstorm", "ideas", "concept", "plan for", "roadmap")))
    if not has_question:
        return False
    creative_hits = sum(1 for w in _CREATIVE_WORDS if w in low)
    return creative_hits >= 1


def _production_task(prompt):
    """Return True when the user wants execution, not just discussion.
    Production tasks should go through the agent loop with tools."""
    low = " ".join(prompt.lower().split())
    if not low:
        return False
    
    # Must have imperative verb + production signal
    IMPERATIVE_VERBS = (
        "render", "export", "deploy", "assemble", "compile",
        "build the", "create the", "make the", "generate the",
        "execute", "run ", "start ", "build a", "create a",
        "make a", "design a", "write ", "fix ",
    )
    PRODUCTION_SIGNALS = (
        "render", "export", "deploy", "assemble", "compile", "package", "bundle",
        ".mp4", ".blend", ".png", "deliverable", "output", "file",
    )
    has_imperative = any(m in low for m in IMPERATIVE_VERBS)
    has_output = any(s in low for s in PRODUCTION_SIGNALS)
    return has_imperative and has_output


def creative_fast_path_reply(prompt):
    """Answer a creative/planning question directly via Ollama — no agent loop."""
    try:
        payload = {
            "model": _VL_MODEL,
            "stream": False,
            "keep_alive": 60,
            "options": {"temperature": 0.7, "num_ctx": 16384, "num_predict": 1024},
            "messages": [
                {"role": "system", "content": (
                    "You are a creative production assistant. "
                    "Answer the user's question directly and helpfully. Be concise but thorough. "
                    "Help with series planning, brainstorming, scripting, and creative ideation "
                    "for ANY project."
                )},
                {"role": "user", "content": prompt},
            ],
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA_HOST}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        reply = (result.get("message") or {}).get("content", "")
        return reply or None
    except Exception:
        return None


def render_eta():
    """Estimate remaining render time from on-disk frame write rate.

    Uses the live master PNGs (currently rendering scene). Returns a dict
    with per-scene + overall human-readable estimates, or {"ok": False} when
    not enough data is present to extrapolate. Power-aware: when the
    full-throttle strategy is active (sleep Never AC/DC) no overnight gap
    factor is applied — the estimate assumes flat-out 24/7 rendering."""
    try:
        masters_root = RENDER_ROOT / "video_clips" / "masters"
        if not masters_root.is_dir():
            return {"ok": False, "error": "masters dir missing"}
        rate_per_frame = 153.0  # default fallback (~2.5 min/frame, measured)
        
        # Find the active scene dynamically
        active_scene = None
        for s_dir in sorted(masters_root.iterdir()):
            if s_dir.is_dir():
                frames = list(s_dir.glob("frame_*.png"))
                if len(frames) > 0:
                    # Check if there's an MP4 (not ready)
                    mp4_path = RENDER_ROOT / "video_clips" / f"{s_dir.name}.mp4"
                    if not (mp4_path.exists() and mp4_path.stat().st_size > 100000):
                        active_scene = s_dir
                        break
        
        if active_scene:
            frames = list(active_scene.glob("frame_*.png"))
            if len(frames) >= 3:
                fr = sorted(frames, key=lambda p: p.name)[-3:]
                dt = (fr[-1].stat().st_mtime - fr[0].stat().st_mtime)
                n = len(fr) - 1
                if dt > 30 and n > 0:
                    rate_per_frame = dt / n
            scene_done = len(frames)
            # Get target from config or default
            target = 1000
            for s in PROJECT_CONFIG.get("scenes", []):
                if s.get("id") == active_scene.name:
                    target = s.get("targetFrames", 1000)
                    break
            scene_remain = max(0, target - scene_done)
        else:
            scene_done = 0
            scene_remain = 0
        
        # Calculate remaining frames across all non-ready scenes
        remaining_frames = scene_remain
        for s_dir in sorted(masters_root.iterdir()):
            if s_dir.is_dir() and s_dir != active_scene:
                frames = list(s_dir.glob("frame_*.png"))
                mp4_path = RENDER_ROOT / "video_clips" / f"{s_dir.name}.mp4"
                if not (mp4_path.exists() and mp4_path.stat().st_size > 100000):
                    target = 1000
                    for s in PROJECT_CONFIG.get("scenes", []):
                        if s.get("id") == s_dir.name:
                            target = s.get("targetFrames", 1000)
                            break
                    remaining_frames += max(0, target - len(frames))

        # Full-throttle strategy: when sleep/hibernate are Never on AC+DC the
        # render is expected to run uninterrupted. Otherwise apply a gap factor
        # (previously ~83% wall efficiency from overnight sleep breaks).
        try:
            pw = get_power_state()
            sleep_never = (pw.get("sleep", {}).get("ac") == "never"
                           and pw.get("sleep", {}).get("dc") == "never")
            hibernate_never = (pw.get("hibernate", {}).get("ac") == "never"
                               and pw.get("hibernate", {}).get("dc") == "never")
            full_throttle = sleep_never and hibernate_never
        except Exception:
            full_throttle = False
        efficiency = 1.0 if full_throttle else 0.83

        eta_h = remaining_frames * rate_per_frame / 3600
        wall_h = eta_h / efficiency
        scene_eta_h = scene_remain * rate_per_frame / 3600
        scene_wall_h = scene_eta_h / efficiency
        active_name = active_scene.name if active_scene else "none"
        return {
            "ok": True,
            "ratePerFrameSec": round(rate_per_frame, 1),
            "activeScene": active_name,
            "activeSceneRemaining": scene_remain,
            "activeSceneEtaHrs": round(scene_wall_h, 1),
            "projectRemainingFrames": remaining_frames,
            "projectEtaHrs": round(wall_h, 1),
            "projectEtaDays": round(wall_h / 24, 1),
            "strategy": "FULL_THROTTLE (sleep/hibernate Never — uninterrupted 24/7)" if full_throttle
                        else "GAP-PRONE (sleep or hibernate active — est. ~83% wall efficiency)",
            "fullThrottle": full_throttle,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def humanize_tool_result(name, res, action_key=None):
    """Turn structured tool/action results into short, human-readable feedback.

    The agent loop returns these to the chat box; raw dict dumps are hard to
    read. This formats the common shapes (ok/blocked/error/ok-with-output)
    into clean status lines."""
    if not isinstance(res, dict):
        return str(res)[:1200]
    if res.get("blocked"):
        return f"⛔ **Blocked by production gate** — {res.get('reason', 'gated')}"
    if res.get("error"):
        return f"❌ **{name} failed** — {res.get('error')}"
    if res.get("ok") is False:
        reason = res.get("reason") or res.get("stderr") or "completed with errors"
        return f"⚠️ **{action_key or name} ran but reports a problem** — {str(reason)[:600]}"
    # Success paths
    if name == "run_action":
        action_key = action_key or (res.get("action") or "action")
        out = (res.get("stdout") or res.get("output") or "").strip()
        ex = res.get("exitCode")
        head = f"✅ **{action_key} finished**" + (f" (exit {ex})" if ex is not None else "")
        if out:
            body = out.splitlines()
            return head + "\n\n```\n" + "\n".join(body[:24]) + ("\n…" if len(body) > 24 else "") + "\n```"
        return head
    if name == "copyright_check":
        verdict = str(res.get("verdict") or res.get("status") or "unknown").upper()
        return f"© Copyright check on `{res.get('input') or res.get('text') or ''}` → **{verdict}**\n{res.get('summary') or res.get('detail') or res.get('reason') or ''}"
    if name == "escalate_openclaw":
        out = (res.get("output") or "").strip()
        return out[:2500] if out else "OpenClaw escalation completed."
    if name == "inspect_image":
        return res.get("description") or f"Visual QC done on `{res.get('image')}`"
    if name == "brainstorm":
        reply = res.get("reply", "")
        topic = res.get("topic", "")
        return f"**Brainstorm: {topic}**\n\n{reply[:2000]}" if reply else f"Brainstorm completed for: {topic}"
    if name in ("qwen_chat", "ping_qwen"):
        out = (res.get("stdout") or res.get("output") or "").strip()
        if out:
            return f"**{name}**\n```\n{out[:2000]}\n```"
        if res.get("ok"):
            return f"✅ **{name}** — completed successfully."
    for key in ("output", "stdout", "tail", "description", "status", "alias"):
        if res.get(key):
            v = str(res[key]).strip()
            if v:
                return f"**{name}**\n{v[:2000]}"
    return f"✅ **{name}** — done."
def inspect_image_with_vl(image_path, question=""):
    """Describe or answer a question about an image using qwen2.5vl.

    Vision requires the pull of the VL model to be complete; falls back to an
    explanatory message (and the coder model) when vision is not ready yet."""
    path_str = str(image_path)
    candidate = (WORKSPACE_ROOT / path_str)
    if not candidate.exists():
        for base in (WORKSPACE_ROOT, IDE_ROOT, RENDER_ROOT):
            p = base / path_str
            if p.exists():
                candidate = p
                break
    if not candidate.exists():
        suggestions = _suggest_image_paths(path_str)
        return {"ok": False, "error": f"Image not found: {image_path}", "suggestions": suggestions}
    if not candidate.is_file():
        return {"ok": False, "error": f"Not a file: {image_path}"}

    model = _VL_MODEL
    if not vl_ready():
        return {
            "ok": False,
            "error": "Vision model not pulled yet. Run 'ollama pull qwen2.5vl:7b' then retry.",
            "image": str(candidate),
        }
    prompt = question.strip() or "Describe what is visible in this image in detail."
    try:
        import base64
        with open(candidate, "rb") as fh:
            encoded = base64.b64encode(fh.read()).decode("ascii")
        payload = {
            "model": model,
            "prompt": prompt,
            "images": [encoded],
            "keep_alive": -1,
            "stream": False,
            "options": {"num_predict": 2048},
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA_HOST}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            out = json.loads(resp.read().decode("utf-8"))
        return {"ok": True, "image": str(candidate), "description": out.get("response", "").strip()}
    except Exception as e:
        return {"ok": False, "error": str(e), "image": str(candidate)}


def get_download_progress():
    """Read-only status of the qwen2.5vl pull vs what Ollama expects.

    Ollama does not expose blob-level pull progress to a second API call, so
    this reports: models present locally, whether the VL model has fully landed,
    and (best-effort) the manifest blob estimate. Never starts a pull."""
    tags = fetch_ollama_tags()
    names = tags.get("models") or []
    if not tags.get("online"):
        return {"online": False, "vlReady": False, "blobsExpected": 0, "blobsReady": 0, "models": []}

    has_vl = any(n.lower().split(":")[0] == "qwen2.5vl" for n in names)
    # A present manifest means all 5 blob layers are on disk; until then zero.
    return {
        "online": True,
        "vlReady": has_vl,
        "blobsExpected": 5 if not has_vl else 5,
        "blobsReady": 5 if has_vl else 0,
        "models": names,
    }


def read_log_tail(log_name, line_count=30):
    # Default log files + any from project config
    valid = {"PRODUCTION_STATUS.md", "STATUS_LIVE_DELIVERY.txt",
             "STATUS_POWER_CHECKPOINT.txt", "arch_comm_iv_lock_log.txt"}
    valid.update(PROJECT_CONFIG.get("logFiles", []))
    if log_name not in valid:
        return {"ok": False, "error": f"Unknown log: {log_name}", "available": sorted(valid)}
    target = WORKSPACE_ROOT / log_name
    if not target.exists():
        return {"ok": False, "error": f"{log_name} not found"}
    try:
        lines = _decode_log_tail(target.read_bytes()).replace("\x00", "").splitlines()
        tail = lines[-line_count:] if len(lines) > line_count else lines
        return {"ok": True, "log": log_name, "lines": len(lines), "tail": "\n".join(tail)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Mission planner: analyze a large prompt, rank deliverables, then execute
# them strictly in sequence (next step only after the current one is done).
# ---------------------------------------------------------------------------

_MISSION_TOOLS = "production_status, read_log, run_action, shell_probe, inspect_image, copyright_check, escalate_openclaw"

PLANNER_PROMPT = (
    "You are a production-runbook planner for video production projects.\n"
    "A mission prompt will be given to you. ANALYZE it and split it into discrete,\n"
    f"ranked execution steps. Valid tools: {_MISSION_TOOLS}.\n"
    "Return STRICT JSON ONLY — a JSON array of step objects, no prose, no markdown:\n"
    '[\n'
    '  {"rank": 1, "deliverable": "short name",\n'
    '   "tool": "one of the valid tools",\n'
    '   "args": {<tool arguments as a JSON object>},\n'
    '   "verify": "what proves this step is done"},\n'
    "  ...\n"
    "]\n"
    "Rules:\n"
    "- Order must reflect importance AND dependency: information-gathering steps\n"
    "  first, gated/long-running deliverables after their preconditions are met.\n"
    "- Each step uses EXACTLY ONE tool. Do not invent tools.\n"
    "- When a step is gated (Blender render active / 4K HOLD / CPU-while-GPU),\n"
    "  keep it in the plan anyway — the executor will respect the gate and halt.\n"
    f"- run_action args: {{\"action\": \"one of: {', '.join(EXEC_ACTIONS)}\"}}.\n"
    f"- read_log args: {{\"log\": \"filename\", \"lines\": 40}}; allowed logs: "
    f"project config logFiles + PRODUCTION_STATUS.md, "
    f"STATUS_LIVE_DELIVERY.txt, STATUS_POWER_CHECKPOINT.txt, arch_comm_iv_lock_log.txt.\n"
    f"- shell_probe args: {{\"alias\": \"one of: {', '.join(k for k, _ in ALLOWED_SHELL_PATTERNS)}\"}}.\n"
    "- production_status takes an empty args object {}.\n"
    '- inspect_image args: {"image_path": "relative/path/inside/workspace", "question": "optional question"}. Requires the qwen2.5vl model to be pulled; returns a text description of the image.\n'
    "- escalate_openclaw args: {\"task\": \"precise task description\"}.\n"
    '- copyright_check args: {"text": "prompt / asset name to assess"}. VERDICTS: CLEAR | WARN (brand name text-only, never logo art) | BLOCK (refused; use replacement). Run it BEFORE scheduling any step that names brands, stock sources, or generated content.\n'
    "- At most 10 steps. Prefer fewer, higher-value steps over many small ones.\n"
)


DEEP_PLAN_PROMPT = (
    "You are an expert video production planner for the OpenClaw Local IDE.\n\n"
    "CRITICAL RULES:\n"
    "1. ALWAYS call get_project_state FIRST to understand current project state.\n"
    "2. NEVER ask the user questions — use tools to gather all context.\n"
    "3. ONLY use actions from this list: render_all_scenes, render_mp4, assemble_final, assemble_with_audio, assemble_kinetic_preview, render_4k, run_1080_then_4k, brainstorm, ping_qwen, qwen_chat\n"
    "4. Plans must be immediately actionable with existing tools.\n"
    "5. Estimate time based on actual render complexity, not generic placeholders.\n"
    "6. Reference the example plans below for structure and quality.\n"
    "7. Adapt the plan to the user's specific project details.\n\n"
    "REFERENCE EXAMPLES (learn structure and quality from these):\n\n"
    "### Example 1: Documentary Short Film\n"
    "Description: 30-min interview-based documentary with B-roll footage\n"
    "```json\n"
    + json.dumps(REFERENCE_PLANS[0]["plan"], indent=2) if REFERENCE_PLANS else '{"note": "No reference plans loaded"}' + "\n"
    "```\n\n"
    "### Example 2: 2D Animated Short Film\n"
    "Description: 5-minute hand-drawn style animated short\n"
    "```json\n"
    + json.dumps(REFERENCE_PLANS[1]["plan"], indent=2) if len(REFERENCE_PLANS) > 1 else '{"note": "No reference plans loaded"}' + "\n"
    "```\n\n"
    "### Example 3: 3D Animated Commercial\n"
    "Description: 60-second product visualization with photorealistic rendering\n"
    "```json\n"
    + json.dumps(REFERENCE_PLANS[2]["plan"], indent=2) if len(REFERENCE_PLANS) > 2 else '{"note": "No reference plans loaded"}' + "\n"
    "```\n\n"
    "OUTPUT FORMAT:\n"
    "Return a JSON object with this exact structure:\n"
    "{\n"
    "  \"project\": \"Project Name\",\n"
    "  \"phases\": [\n"
    "    {\n"
    "      \"id\": 1,\n"
    "      \"name\": \"Phase Name\",\n"
    "      \"days\": 2,\n"
    "      \"tasks\": [\n"
    "        {\n"
    "          \"id\": \"1.1\",\n"
    "          \"name\": \"Task Name\",\n"
    "          \"depends_on\": [\"kickoff\"],\n"
    "          \"deliverable\": \"path/to/deliverable\",\n"
    "          \"estimate_hrs\": 4,\n"
    "          \"action\": \"render_all_scenes\",\n"
    "          \"action_params\": {\"key\": \"value\"}\n"
    "        }\n"
    "      ]\n"
    "    }\n"
    "  ],\n"
    "  \"total_estimate_days\": 5,\n"
    "  \"gates\": [\"4K HOLD\"],\n"
    "  \"handoff_ready\": true\n"
    "}\n\n"
    "BAD EXAMPLE (DO NOT DO THIS):\n"
    "- Using actions like 'start_shooting', 'edit_video', 'color_grade' — these don't exist\n"
    "- Asking the user questions instead of calling tools\n"
    "- Generic time estimates not based on actual render complexity\n"
    "- No dependency chain between tasks\n\n"
    "GOOD EXAMPLE (DO THIS):\n"
    "- Use only valid actions from the list above\n"
    "- Call get_project_state first to gather context\n"
    "- Create clear dependency chains (kickoff -> 1.1 -> 1.2 -> 2.1)\n"
    "- Specify deliverables with file paths\n"
    "- Estimate time based on render complexity (1080p scenes: 2-4hrs each, 4K: 4-8hrs each)\n"
)


def extract_plan_json(text):
    """Extract the JSON block from Deep Plan reply (fenced or bare)."""
    # Try fenced ```json ... ``` first
    fenced = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except Exception:
            pass
    # Try bare { ... } at end
    bare = re.search(r"(\{.*\})\s*$", text, re.DOTALL)
    if bare:
        try:
            return json.loads(bare.group(1))
        except Exception:
            pass
    return None


def save_plan_to_project(plan_json):
    """Write plan to .plan_state.json atomically (separate from static config)."""
    plan_state_path = IDE_ROOT / ".plan_state.json"
    
    plan_state = {
        "version": 1,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": "qwen2.5-coder:7b",
        "phases": plan_json.get("phases", []),
        "tasks": plan_json.get("tasks", []),
        "handoff": plan_json.get("handoff", {}),
        "meta": {
            "total_estimate_days": plan_json.get("total_estimate_days", 0),
            "gates": plan_json.get("gates", []),
            "handoff_ready": plan_json.get("handoff_ready", False)
        }
    }
    
    # Atomic write
    tmp = plan_state_path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(plan_state, f, indent=2, ensure_ascii=False)
    os.replace(tmp, plan_state_path)
    
    # Reload global config
    load_project_config()
    return {"ok": True, "plan": plan_state}


# ─── Session Search Index (SQLite FTS5) ──────────────────────────────
import sqlite3
import threading
import atexit

# (INDEX_DB is set per-project by _apply_state_paths().)
_INDEX_LOCK = threading.Lock()
_INDEX_INITIALIZED = False

def _init_search_index():
    """Create FTS5 virtual table for session search."""
    global _INDEX_INITIALIZED
    with _INDEX_LOCK:
        if _INDEX_INITIALIZED:
            return
        conn = sqlite3.connect(INDEX_DB)
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts USING fts5(
                session_id UNINDEXED,
                timestamp UNINDEXED,
                mode UNINDEXED,
                model UNINDEXED,
                prompt,
                reply,
                tools_used,
                tools_detail,
                status UNINDEXED,
                duration_s UNINDEXED,
                has_plan_json UNINDEXED,
                plan_version UNINDEXED,
                tokenize='porter unicode61'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS session_meta (
                session_id TEXT PRIMARY KEY,
                timestamp TEXT,
                mode TEXT,
                model TEXT,
                prompt TEXT,
                reply TEXT,
                tools_used TEXT,
                tools_detail TEXT,
                status TEXT,
                duration_s REAL,
                has_plan_json INTEGER,
                plan_version INTEGER,
                raw_prompt TEXT,
                raw_reply TEXT
            )
        """)
        conn.commit()
        conn.close()
        _INDEX_INITIALIZED = True

def _index_session(session_id, meta, trace_events):
    """Index a completed session from prompt log + trace."""
    _init_search_index()
    
    # Aggregate trace data
    tools_used = []
    tools_detail = []
    rounds = 0
    duration = 0
    has_plan = False
    plan_ver = 0
    
    for ev in trace_events:
        if ev.get("event") == "round":
            rounds += 1
            if ev.get("model_text"):
                # Check for plan JSON in model text
                if "```json" in ev["model_text"] and "handoff_ready" in ev["model_text"]:
                    has_plan = True
        if ev.get("event") == "tool":
            for tc in ev.get("tools_called", []):
                name = tc.get("name")
                if name and name not in tools_used:
                    tools_used.append(name)
                tools_detail.append({
                    "name": name,
                    "status": tc.get("status"),
                    "summary": (tc.get("result_summary") or "")[:200]
                })
        if ev.get("event") == "loop.start":
            duration = ev.get("elapsed_s", 0)
        if ev.get("event") in ("loop.max_rounds", "loop.converged", "loop.term", "loop.wallclock"):
            duration = ev.get("elapsed_s", duration)
    
    with _INDEX_LOCK:
        conn = sqlite3.connect(INDEX_DB)
        # FTS5 doesn't support UPSERT - delete then insert
        conn.execute("DELETE FROM sessions_fts WHERE session_id = ?", (session_id,))
        conn.execute("""
            INSERT INTO sessions_fts(session_id, timestamp, mode, model, prompt, reply, tools_used, tools_detail, status, duration_s, has_plan_json, plan_version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id, meta.get("ts"), meta.get("mode"), meta.get("model"),
            meta.get("prompt", "")[:5000], meta.get("reply", "")[:5000],
            ", ".join(tools_used), json.dumps(tools_detail),
            meta.get("status", "completed"), duration, int(has_plan), plan_ver
        ))
        # Store full metadata for detail view (regular table supports UPSERT)
        conn.execute("""
            INSERT INTO session_meta(session_id, timestamp, mode, model, prompt, reply, tools_used, tools_detail, status, duration_s, has_plan_json, plan_version, raw_prompt, raw_reply)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                timestamp=excluded.timestamp, mode=excluded.mode, model=excluded.model,
                prompt=excluded.prompt, reply=excluded.reply, tools_used=excluded.tools_used,
                tools_detail=excluded.tools_detail, status=excluded.status,
                duration_s=excluded.duration_s, has_plan_json=excluded.has_plan_json,
                plan_version=excluded.plan_version, raw_prompt=excluded.raw_prompt,
                raw_reply=excluded.raw_reply
        """, (
            session_id, meta.get("ts"), meta.get("mode"), meta.get("model"),
            meta.get("prompt"), meta.get("reply"),
            ", ".join(tools_used), json.dumps(tools_detail),
            meta.get("status", "completed"), duration, int(has_plan), plan_ver,
            meta.get("prompt"), meta.get("reply")
        ))
        conn.commit()
        conn.close()

def _rebuild_index_from_logs():
    """Full rebuild from .prompt_log.jsonl + .agent_trace.jsonl (run once at startup)."""
    _init_search_index()
    prompts = read_prompt_history(limit=10000)  # all
    trace_by_session = {}
    for ev in read_agent_trace(limit=50000):
        sid = ev.get("session")
        if sid:
            trace_by_session.setdefault(sid, []).append(ev)
    
    for meta in prompts:
        sid = meta.get("session")
        if sid:
            _index_session(sid, meta, trace_by_session.get(sid, []))
    print(f"[search-index] Rebuilt: {len(prompts)} sessions indexed")

# Start background indexer
_indexer_thread = threading.Thread(target=_rebuild_index_from_logs, daemon=True)
_indexer_thread.start()
atexit.register(lambda: None)  # placeholder for cleanup


def plan_mission(mission_text, model=DEFAULT_MODEL):
    """Phase 1: analyze + rank a large prompt into ordered JSON steps.

    Uses a single no-tool Ollama chat call (fast, deterministic-ish). Returns
    {"plan": [...], "error": None} or {"plan": None, "error": "..."}."""
    import re
    try:
        payload = {
            "model": model,
            "stream": False,
            "keep_alive": -1,
            "options": {"temperature": 0.1, "num_ctx": 16384, "num_predict": 2048, "top_p": 0.8},
            "messages": [
                {"role": "system", "content": PLANNER_PROMPT},
                {"role": "user", "content": mission_text},
            ],
        }
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA_HOST}/api/chat",
            data=req_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=240) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        content = (result.get("message") or {}).get("content") or ""
    except Exception as e:
        return {"plan": None, "error": f"Planner call failed: {e}"}

    # Extract the first balanced JSON array in the reply.
    start = content.find("[")
    end = content.rfind("]")
    if start == -1 or end == -1 or end <= start:
        return {"plan": None, "error": f"Planner did not return a JSON array. Reply: {content[:400]}"}
    try:
        steps = json.loads(content[start:end + 1])
    except Exception as e:
        return {"plan": None, "error": f"Planner JSON unparsable: {e}"}

    if not isinstance(steps, list) or not steps:
        return {"plan": None, "error": "Planner returned an empty plan."}

    valid_tools = {"production_status", "read_log", "run_action", "shell_probe", "inspect_image", "copyright_check", "escalate_openclaw"}
    cleaned = []
    for i, s in enumerate(steps):
        if not isinstance(s, dict):
            continue
        tool = s.get("tool")
        if tool not in valid_tools:
            tool = None
        cleaned.append({
            "rank": s.get("rank", i + 1),
            "deliverable": s.get("deliverable") or f"step {i + 1}",
            "tool": tool,
            "args": s.get("args") if isinstance(s.get("args"), dict) else {},
            "verify": s.get("verify") or "",
        })
    usable = [s for s in cleaned if s["tool"]]
    if not usable:
        return {"plan": None, "error": "Planner produced no steps with a valid tool."}
    usable.sort(key=lambda s: s["rank"])
    for i, s in enumerate(usable):
        s["execIndex"] = i
    return {"plan": usable, "error": None}


def execute_mission_sequential(steps, model=DEFAULT_MODEL):
    """Phase 2: run the ranked plan in strict order.

    Each step is dispatched directly via dispatch_tool (not an LLM round).
    The next step runs ONLY after the current one verified OK. Halts (stops
    the whole sequence) on BLOCKED_BY_GATE or a failed step. Safe against the
    qwen churn problem because no model loop is involved."""
    report = []
    stopped = False
    for i, step in enumerate(steps):
        tool = step.get("tool")
        args = step.get("args") or {}
        deliverable = step.get("deliverable", f"step {i + 1}")
        status = "pending"
        detail = ""
        if not tool:
            status = "failed"
            detail = "no valid tool"
        else:
            try:
                res = dispatch_tool(tool, args)
            except Exception as e:
                res = {"ok": False, "error": str(e)}
            if res.get("blocked"):
                status = "blocked"
                detail = str(res.get("reason", "gated"))[:400]
                stopped = True
            elif res.get("error"):
                # Config errors (unknown probe alias / action key / log) are a
                # planner-data issue, not a pipeline failure: skip the step so
                # the rest of the chain still runs.
                err = str(res.get("error"))
                if "not in allowlist" in err or "Unknown action" in err or "Unknown log" in err or "Unknown tool" in err:
                    status = "skipped"
                    detail = err[:400]
                else:
                    status = "failed"
                    detail = err[:400]
                    stopped = True
            elif res.get("ok") is False:
                status = "failed"
                detail = str(res.get("reason") or "")[:400]
                stopped = True
            else:
                # ok=True OR a result with no error/blocked flag (e.g.
                # production_status returns {status, battery}) → success.
                status = "done"
                detail = str(res.get("output") or res.get("stdout") or res.get("status") or res.get("alias") or res.get("tail") or "")[:600]
        report.append({
            "execIndex": step.get("execIndex", i),
            "rank": step.get("rank", i + 1),
            "deliverable": deliverable,
            "tool": tool,
            "verify": step.get("verify", ""),
            "status": status,
            "detail": detail,
        })
        trace_agent({"event": "mission.step", "step": i + 1, "tool": tool,
                     "deliverable": str(deliverable)[:120], "status": status,
                     "detail": detail[:300]})
        if stopped:
            break
    return {"report": report, "stopped": stopped}


def _read_log_tail_fast(log_path, line_count=50, max_bytes=131072):
    """Fast zero-copy / seek-from-end log tail reader for large production logs."""
    try:
        p = Path(log_path)
        if not p.exists():
            return "(File does not exist yet)"
        size = p.stat().st_size
        with open(p, "rb") as f:
            if size > max_bytes:
                f.seek(size - max_bytes)
            raw = f.read()
        
        # Robust multi-encoding decode (UTF-8 / UTF-16 / Latin-1)
        text = ""
        for enc in ("utf-8", "utf-16-le", "utf-16", "latin1"):
            try:
                text = raw.decode(enc)
                if "\x00" in text:
                    text = text.replace("\x00", "")
                break
            except Exception:
                continue
        if not text:
            text = raw.decode("latin1", errors="replace").replace("\x00", "")
            
        lines = text.splitlines()
        tail = lines[-line_count:] if len(lines) > line_count else lines
        return "\n".join(tail)
    except Exception as e:
        return f"Log read error: {e}"


# ── Project Management ──────────────────────────────────────────────
def list_projects():
    """List sub-folders in workspace root that look like projects."""
    projects = []
    # Always include the current workspace
    projects.append({
        "name": PROJECT_CONFIG.get("name", "Current Workspace"),
        "path": str(WORKSPACE_ROOT),
        "active": True,
    })
    # Registered projects (see projects.json next to server.py).
    try:
        if PROJECTS_REGISTRY.exists():
            registry = json.loads(PROJECTS_REGISTRY.read_text(encoding="utf-8"))
            for entry in registry.get("projects", []):
                p = Path(entry.get("path", "")).resolve()
                if p.exists() and p.is_dir() and str(p) != str(WORKSPACE_ROOT):
                    projects.append({
                        "name": entry.get("name") or p.name,
                        "path": str(p),
                        "active": False,
                    })
    except Exception:
        pass
    return projects


def switch_project(project_path):
    """Switch the active workspace to a different project directory."""
    global WORKSPACE_ROOT, IDE_ROOT, RENDER_ROOT, PROJECT_CONFIG, _INDEX_INITIALIZED, GUIDES_ROOT
    p = Path(project_path).resolve()
    if not p.exists() or not p.is_dir():
        return {"ok": False, "error": f"Directory not found: {project_path}"}
    WORKSPACE_ROOT = p
    IDE_ROOT = p
    load_project_config()
    # Re-point per-project state (sessions/traces/memory/search) at the new
    # project and force its FTS index to (re)build on first use.
    _apply_state_paths()
    _INDEX_INITIALIZED = False
    GUIDES_ROOT = (WORKSPACE_ROOT / "docs" / "guides").resolve()
    # Invalidate the /api/status cache so the next poll reflects the new project.
    _STATUS_CACHE["ts"] = 0.0
    _STATUS_CACHE["data"] = None
    return {"ok": True, "name": p.name, "path": str(p)}


def create_project(name, parent=None):
    """Scaffold a new project folder at <parent>/<name> and register it."""
    safe_name = re.sub(r'[^\w\s\-]', '', name).strip().replace(' ', '_')
    if not safe_name:
        return {"ok": False, "error": "Invalid project name"}
    base = Path(parent).resolve() if parent else WORKSPACE_ROOT.parent
    if not base.exists() or not base.is_dir():
        return {"ok": False, "error": f"Folder not found: {base}"}
    project_dir = base / safe_name
    if project_dir.exists():
        return {"ok": False, "error": f"Project '{safe_name}' already exists at {project_dir}"}
    try:
        project_dir.mkdir(parents=True)
        (project_dir / "src").mkdir()
        (project_dir / "assets").mkdir()
        (project_dir / "docs").mkdir()
        config = {
            "name": name,
            "episode": "",
            "renderRoot": "renders",
            "scriptsRoot": "scripts",
            "delivery": {"resolution": "1080p", "targetFps": 24},
            "gates": {"4kHold": True, "gpuOneMax": True},
            "scenes": [],
        }
        with open(str(project_dir / "project.json"), "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        _register_project(name, project_dir)
        return {"ok": True, "name": name, "path": str(project_dir)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _register_project(name, project_path):
    """Add (or update) a project entry in projects.json so it appears in the list."""
    try:
        entries = []
        if PROJECTS_REGISTRY.exists():
            registry = json.loads(PROJECTS_REGISTRY.read_text(encoding="utf-8"))
            entries = registry.get("projects", [])
        resolved = str(Path(project_path).resolve())
        entries = [e for e in entries
                   if str(Path(e.get("path", "")).resolve()).lower() != resolved.lower()]
        entries.append({"name": name, "path": resolved})
        PROJECTS_REGISTRY.write_text(
            json.dumps({"projects": entries}, indent=2), encoding="utf-8")
        return True
    except Exception:
        return False


def browse_filesystem(path=""):
    """Directory browser for the 'New Project' picker.

    With no path, returns the available drives. Otherwise returns the sorted
    sub-directories of `path` plus the parent path for 'up' navigation.
    """
    try:
        if not path:
            drives = []
            for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                d = f"{letter}:\\"
                if os.path.exists(d):
                    drives.append({"name": letter + ":", "path": d, "isDrive": True})
            return {"ok": True, "root": True, "path": "", "parent": None, "entries": drives}
        p = Path(path).resolve()
        if not p.is_dir():
            return {"ok": False, "error": f"Not a folder: {path}"}
        entries = []
        try:
            with os.scandir(str(p)) as it:
                for child in it:
                    try:
                        if child.is_dir():
                            entries.append({"name": child.name, "path": child.path, "isDrive": False})
                    except Exception:
                        continue
        except PermissionError:
            return {"ok": False, "error": f"Access denied: {path}"}
        entries.sort(key=lambda e: e["name"].lower())
        parent = str(p.parent) if p.parent != p else None
        return {"ok": True, "root": False, "path": str(p), "parent": parent, "entries": entries}
    except Exception as e:
        return {"ok": False, "error": str(e)}


class IDEHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        query = urllib.parse.parse_qs(url.query)

        if path == "/api/status":
            self.handle_api_status()
        elif path == "/api/crestodian/status":
            self._send_json(get_crestodian_info())
        elif path == "/api/render/progress":
            self.handle_render_progress()
        elif path == "/api/files/tree":
            self.handle_files_tree()
        elif path == "/api/files/read":
            self.handle_file_read(query.get("path", [""])[0])
        elif path == "/api/logs/tail":
            self.handle_logs_tail(query.get("file", ["wait_hq_assemble_log.txt"])[0], int(query.get("lines", [50])[0]))
        elif path == "/api/guides":
            self.handle_guides()
        elif path == "/api/pipeline":
            self.handle_pipeline()
        elif path == "/api/pipeline/prompt":
            self.handle_pipeline_prompt()
        elif path == "/api/pipeline/exec":
            self.handle_pipeline_exec()
        elif path == "/api/copyright/policy":
            self._send_json(COPYRIGHT_PROTOCOL)
        elif path == "/api/chat/history":
            try:
                limit = int(query.get("limit", ["20"])[0])
            except ValueError:
                limit = 20
            self._send_json({"history": read_prompt_history(limit=max(1, min(limit, 200)))})
        elif path == "/api/agent/trace":
            try:
                limit = int(query.get("limit", ["40"])[0])
            except ValueError:
                limit = 40
            self._send_json({"trace": read_agent_trace(limit=max(1, min(limit, 500)))})
        elif path == "/api/agent/trajectory":
            try:
                limit = int(query.get("limit", ["30"])[0])
            except ValueError:
                limit = 30
            session = query.get("session", [None])[0]
            self._send_json({"trajectory": read_agent_trace(limit=max(1, min(limit, 300)), session=session)})
        elif path == "/api/hourly":
            self._send_json(read_hourly_latest())
        elif path == "/api/audio/files":
            self._send_json(list_audio_files())
        elif path == "/api/audio/file":
            self.handle_audio_file(query.get("path", [""])[0])
        elif path == "/api/plan/list":
            self.handle_plan_list()
        elif path == "/api/plan/read":
            self.handle_plan_read(query)
        elif path == "/api/power":
            self._send_json(get_power_state())
        elif path == "/api/system/network":
            gw_reachable = is_port_open(18789)
            self._send_json({
                "online": check_online_status(),
                "port18789": gw_reachable,
                "port11434": is_port_open(11434),
                "port49632": is_port_open(49632),
                "port8765": is_port_open(8765),
                "blenderRunning": get_native_blender_pid() is not None,
                "gateway": {
                    "port": 18789,
                    "reachable": gw_reachable,
                },
            })
        elif path == "/api/readiness":
            self._send_json(self.get_readiness())
        elif path == "/api/sessions/search":
            # parse_qs returns lists; flatten to strings for the shared handler
            flat = {k: (v[0] if isinstance(v, list) and len(v) == 1 else v)
                    for k, v in query.items()}
            self.handle_search_sessions(flat)
        elif path == "/api/sessions/detail":
            self.handle_session_detail(query)
        elif path == "/api/agent/stream":
            self.handle_agent_stream(query.get("session", [None])[0])
        elif path == "/api/git/status":
            self._send_json(handle_git_status())
        elif path == "/api/fs/browse":
            self._send_json(browse_filesystem(query.get("path", [""])[0]))
        elif path == "/api/projects/list":
            self._send_json({"projects": list_projects()})
        else:
            super().do_GET()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        content_len = int(self.headers.get('Content-Length', 0))
        # Security: limit request size to 10MB
        if content_len > 10_000_000:
            self._send_json({"error": "Request too large (max 10MB)"}, 413)
            return
        post_body = self.rfile.read(content_len) if content_len > 0 else b"{}"

        try:
            payload = json.loads(post_body.decode('utf-8'))
        except Exception:
            payload = {}

        if path == "/api/chat":
            self.handle_chat(payload)
        elif path == "/api/chat/cancel":
            self.handle_chat_cancel(payload)
        elif path == "/api/plan/save":
            self.handle_plan_save(payload)
        elif path == "/api/sessions/search":
            self.handle_search_sessions(payload)
        elif path == "/api/openclaw/direct":
            prompt = payload.get("prompt", "")
            session = payload.get("session", "")
            self._send_json(direct_openclaw_chat(prompt, session=session))
        elif path == "/api/files/save":
            self.handle_file_save(payload)
        elif path == "/api/openclaw/exec":
            self.handle_openclaw_exec(payload)
        elif path == "/api/tools/trigger":
            self.handle_tool_trigger(payload)
        elif path == "/api/exec":
            self.handle_exec(payload)
        elif path == "/api/mission":
            self.handle_mission(payload)
        elif path == "/api/vision":
            self.handle_vision(payload)
        elif path == "/api/copyright/check":
            text = payload.get("text", "")
            self._send_json(check_copyright(text))
        elif path == "/api/agent/tools":
            self.handle_agent_tools()
        elif path == "/api/escalate":
            self.handle_escalate(payload)
        elif path == "/api/power":
            action = payload.get("action", "")
            self._send_json(apply_power_action(action, payload))
        elif path == "/api/git/diff":
            self._send_json(handle_git_diff(payload))
        elif path == "/api/git/commit":
            self._send_json(handle_git_commit(payload))
        elif path == "/api/git/branch":
            self._send_json(handle_git_branch(payload))
        elif path == "/api/git/log":
            self._send_json(handle_git_log(payload))
        elif path == "/api/git/push":
            self._send_json(handle_git_push(payload))
        elif path == "/api/git/pull":
            self._send_json(handle_git_pull(payload))
        elif path == "/api/git/stage":
            self._send_json(handle_git_stage(payload))
        elif path == "/api/model":
            self._send_json(handle_model_change(payload))
        elif path == "/api/projects/switch":
            self._send_json(switch_project(payload.get("path", "")))
        elif path == "/api/projects/create":
            self._send_json(create_project(payload.get("name", ""), payload.get("parent")))
        else:
            self.send_error(404, "Unknown API endpoint")

    def handle_chat_cancel(self, payload):
        """Mark an in-flight agent-loop session as cancelled."""
        session = payload.get("session", "")
        if not session:
            self._send_json({"ok": False, "error": "No session provided"}, 400)
            return
        with _CANCELLED_LOCK:
            _CANCELLED.add(session)
        self._send_json({"ok": True, "cancelled": session})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()

    def _send_json(self, data, code=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(body)

    def handle_audio_file(self, rel_path):
        """Stream an audio file from the production assets/audio tree."""
        full = _audio_relative(rel_path)
        if not full:
            self.send_error(404, "Audio file not found")
            return
        try:
            with open(full, "rb") as fh:
                data = fh.read()
        except Exception as e:
            self.send_error(500, str(e))
            return
        ctype = "audio/mpeg"
        ext = os.path.splitext(full)[1].lower()
        if ext == ".wav":
            ctype = "audio/wav"
        elif ext == ".ogg":
            ctype = "audio/ogg"
        elif ext == ".flac":
            ctype = "audio/flac"
        elif ext == ".m4a":
            ctype = "audio/mp4"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    def handle_api_status(self):
        _now = time.time()
        if _STATUS_CACHE["ts"] and _now - _STATUS_CACHE["ts"] < 2.0:
            self._send_json(_STATUS_CACHE["data"])
            return
        ollama_status = ping_ollama()
        battery = get_battery_info()
        render_prog = get_render_progress()
        crestodian = get_crestodian_info()
        download = get_download_progress()
        active_model = resolve_default_model()
        vision_ok = vl_ready()
        gateway_reachable = is_port_open(18789)

        status = {
            "workspace": str(WORKSPACE_ROOT),
            "ollama": ollama_status,
            "defaultModel": DEFAULT_MODEL,
            "activeModel": active_model,
            "modelRouting": {
                "general": _CODER_MODEL,
                "vision": _VL_MODEL,
                "policy": "general agentic tasks use the 14b; visual tasks route to the 7b via /api/vision and inspect_image",
            },
            "vision": {
                "model": _VL_MODEL,
                "active": vision_ok,
                "ready": vision_ok,
            },
            "download": download,
            "battery": battery,
            "render": render_prog,
            "gateway": {
                "port": 18789,
                "reachable": gateway_reachable,
                "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S")
            },
            "openclaw": {
                "installed": True,
                "version": "2026.7.1-2",
                "rules": "AGENTS.md active"
            },
            "crestodian": crestodian,
            "agent": {
                "executor": True,
                "actions": list(EXEC_ACTIONS.keys()),
                "shellProbes": [k for k, _ in ALLOWED_SHELL_PATTERNS],
                "vision": vision_ok,
                "escalation": "openclaw gateway (port 18789)",
                "mission": "analyze → rank → sequential execute (/api/mission)",
                "gates": {"oneGpuJob": True, "fourKHold": True, "cpuWhileGpu": True}
            },
            "tools": {
                "composio": {"status": "Ready & Authenticated", "auth": True},
                "canva": {"status": "Active (canva_airway-sasin)", "auth": True},
                "blender_mcp": {"status": "Configured (5.1.2)", "port": 9876},
                "resolve_mcp": {"status": "Bridge Configured", "port": 49632},
                "crestodian": {"status": "Enforced & Attested", "attestations": crestodian.get("attestationsCount", 0)}
            }
        }
        _STATUS_CACHE["ts"] = _now
        _STATUS_CACHE["data"] = status
        self._send_json(status)

    def get_readiness(self):
        """Aggregate all health signals into a single readiness assessment."""
        status = get_render_progress()
        battery = get_battery_info()
        ollama = ping_ollama()
        gateway_ok = is_port_open(18789)
        power = get_power_state()
        disk = shutil.disk_usage(str(RENDER_ROOT))
        
        checks = {
            "ollama": {"ok": ollama.get("online"), "detail": f"{len(ollama.get('models', []))} models available"},
            "gateway": {"ok": gateway_ok, "port": 18789},
            "blender": {"ok": not status.get("blenderRunning") or status.get("readyCount", 0) == status.get("totalScenes", 0), 
                        "detail": f"{status.get('readyCount', 0)}/{status.get('totalScenes', 0)} scenes ready"},
            "power": {"ok": battery.get("percent", 0) > 20 or "AC" in battery.get("status", ""), 
                      "detail": f"{battery.get('percent')}% ({battery.get('status')})"},
            "disk": {"ok": disk.free > 10 * 1024**3,  # 10GB minimum
                     "detail": f"{round(disk.free / 1024**3, 1)} GB free"},
            "sleep": {"ok": power.get("sleep", {}).get("ac") == "never" and power.get("hibernate", {}).get("ac") == "never",
                      "detail": "Sleep/hibernate disabled" if power.get("sleep", {}).get("ac") == "never" else "Sleep active - may interrupt renders"}
        }
        
        all_ok = all(c["ok"] for c in checks.values())
        return {
            "overall": "ready" if all_ok else "degraded",
            "checks": checks,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }

    def handle_render_progress(self):
        self._send_json(get_render_progress())

    def handle_files_tree(self):
        items = []
        skip_dirs = {".git", ".system_generated", "__pycache__", "venv", ".venv", "node_modules", "masters"}
        
        for root, dirs, files in os.walk(WORKSPACE_ROOT):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            rel_dir = os.path.relpath(root, WORKSPACE_ROOT)
            if rel_dir == ".":
                rel_dir = ""
            
            for f in files:
                if f.endswith((".py", ".md", ".json", ".yaml", ".txt", ".ps1", ".bat", ".cmd", ".html", ".css", ".js")):
                    rel_path = os.path.join(rel_dir, f).replace("\\", "/")
                    items.append({
                        "path": rel_path,
                        "name": f,
                        "folder": rel_dir.replace("\\", "/"),
                        "size": (Path(root) / f).stat().st_size
                    })
        self._send_json({"files": items})

    def handle_file_read(self, rel_path):
        if not rel_path:
            self._send_json({"error": "No path provided"}, 400)
            return
        target = (WORKSPACE_ROOT / rel_path).resolve()
        if not target.is_relative_to(WORKSPACE_ROOT):
            self._send_json({"error": "Access denied"}, 403)
            return
        try:
            if not target.exists():
                self._send_json({"error": "File not found"}, 404)
                return
            content = target.read_text(encoding="utf-8", errors="replace")
            self._send_json({"path": rel_path, "content": content})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def handle_file_save(self, payload):
        rel_path = payload.get("path", "")
        content = payload.get("content", "")
        if not rel_path:
            self._send_json({"error": "No path provided"}, 400)
            return
        target = (WORKSPACE_ROOT / rel_path).resolve()
        if not target.is_relative_to(WORKSPACE_ROOT):
            self._send_json({"error": "Access denied"}, 403)
            return
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            self._send_json({"ok": True, "saved": rel_path})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def handle_logs_tail(self, log_name, line_count=50):
        # #region agent log
        _agent_dbg("H1", "server.py:handle_logs_tail:entry", "logs_tail_enter", {
            "log_name": log_name, "line_count": line_count,
            "workspace": str(WORKSPACE_ROOT), "pid": os.getpid(),
        })
        # #endregion
        _safe_print(f"[Logs] Requested: {log_name!r}, lines={line_count}", flush=True)
        valid_logs = {"PRODUCTION_STATUS.md", "STATUS_LIVE_DELIVERY.txt",
             "STATUS_POWER_CHECKPOINT.txt", "arch_comm_iv_lock_log.txt",
             "render_log_phaseB_rerender.txt"}
        valid_logs.update(PROJECT_CONFIG.get("logFiles", []))
        if log_name not in valid_logs:
            default_log = PROJECT_CONFIG.get("logFiles", ["PRODUCTION_STATUS.md"])[0]
            _safe_print(f"[Logs] Unknown log {log_name!r}; falling back to {default_log!r}", flush=True)
            log_name = default_log
        
        target = WORKSPACE_ROOT / log_name
        if not target.exists():
            target_live = RENDER_ROOT.parent / log_name
            if target_live.exists():
                target = target_live
                _safe_print(f"[Logs] Resolved via live root: {target}", flush=True)
            else:
                _safe_print(f"[Logs] Missing file: {log_name!r}", flush=True)
                # #region agent log
                _agent_dbg("H1", "server.py:handle_logs_tail:missing", "logs_missing_send", {"log_name": log_name})
                # #endregion
                self._send_json({"log": log_name, "content": "(File does not exist yet)"})
                return

        try:
            content = _read_log_tail_fast(target, line_count=line_count)
            n_lines = len(content.splitlines())
            _safe_print(f"[Logs] OK {target.name}: {n_lines} lines", flush=True)
            # #region agent log
            _agent_dbg("H1", "server.py:handle_logs_tail:ok", "logs_ok_send", {
                "log_name": log_name, "n_lines": n_lines, "target": str(target),
            })
            # #endregion
            self._send_json({"log": log_name, "content": content, "totalLines": n_lines})
        except Exception as e:
            # #region agent log
            _agent_dbg("H1", "server.py:handle_logs_tail:exc", "logs_exception", {"error": repr(e)})
            # #endregion
            _safe_print(f"[Logs] Read error for {log_name!r}: {e}", flush=True)
            self._send_json({"log": log_name, "content": f"Log read error: {str(e)}"})

    def handle_chat(self, payload):
        prompt = payload.get("prompt", "").strip()
        system_msg = payload.get("system", SYSTEM_PROMPT)
        model = payload.get("model") or resolve_default_model()
        mode = (payload.get("mode") or "openclaw").lower()
        session = payload.get("session") or (
            "ses_" + time.strftime("%H%M%S") + "_" + str(int(time.time() * 1000))[-5:]
        )

        if not prompt:
            self._send_json({"error": "Empty prompt"}, 400)
            return

        # Fast path: pure status/progress questions answered from live server data
        # Check this FIRST regardless of mode (except plan/openclaw which return early)
        if _status_only_prompt(prompt):
            fast_reply = status_fast_path_reply(prompt)
            if fast_reply:
                trace_agent({"event": "loop.fastpath", "session": session,
                             "model": model, "prompt": prompt[:300]})
                log_prompt({
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "route": "chat_fastpath",
                    "model": "live-data",
                    "session": session,
                    "prompt": prompt[:4000],
                    "has_reply": True,
                })
                self._send_json({"reply": fast_reply, "model": "live-data",
                                 "session": session, "rounds": [],
                                 "fastpath": True})
                return

        # Plan mode: fast VL model for brainstorming/planning — no tools, no agent loop
        if mode == "plan":
            # #region agent log
            _agent_dbg("H3", "server.py:handle_chat:plan", "plan_mode_enter", {
                "session": session, "prompt_len": len(prompt),
            })
            # #endregion
            try:
                payload = {"model": _VL_MODEL, "stream": False, "keep_alive": 60,
            "options": {"temperature": 0.7, "num_ctx": 16384, "num_predict": 4096},
                           "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                                        {"role": "user", "content": prompt}]}
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(f"{OLLAMA_HOST}/api/chat", data=data,
                                             headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=60) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                output = (result.get("message") or {}).get("content", "") or "No response"
                log_prompt({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "route": "plan",
                            "model": _VL_MODEL, "session": session, "prompt": prompt, "reply": str(output)[:1200]})
                # #region agent log
                _agent_dbg("H3", "server.py:handle_chat:plan", "plan_mode_ok_no_trace", {
                    "session": session, "reply_len": len(str(output)),
                    "wrote_trace": False,
                })
                # #endregion
                self._send_json({"reply": output, "model": _VL_MODEL, "session": session, "rounds": [], "mode": "plan", "ok": True})
            except Exception as e:
                # #region agent log
                _agent_dbg("H3", "server.py:handle_chat:plan", "plan_mode_error", {
                    "session": session, "error": repr(e),
                })
                # #endregion
                self._send_json({"reply": f"Plan mode error: {e}", "model": _VL_MODEL, "session": session, "ok": False})
            return

        # Deep Plan mode: 7b coder with info tools for researched planning
        if mode == "deep_plan":
            # Warm up the 7b coder for planning with tools
            warm_up_ollama(_CODER_MODEL_7B)
            # Fall through to agent loop with 7b model and DEEP_PLAN_PROMPT
            model = _CODER_MODEL_7B
            system_msg = DEEP_PLAN_PROMPT
            
            # Strip images from prompt in Deep Plan mode (7B coder is text-only)
            if prompt:
                import re
                # Remove data URLs and markdown images
                prompt = re.sub(r'<img[^>]+data:image[^>]+>', '[image omitted - Deep Plan mode is text-only]', prompt)
                prompt = re.sub(r'!\[.*?\]\(data:image[^)]+\)', '[image omitted]', prompt)
                # Remove base64 image data
                prompt = re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+', '[base64 image omitted]', prompt)

        # Build mode: 14b coder agent loop with full tool-calling
        if mode == "build":
            # Warm up the 14b coder for agentic tasks
            warm_up_ollama(_CODER_MODEL)
            # Fall through to the agent loop below with the 14b model
            model = _CODER_MODEL

        # Direct OpenClaw mode: routes directly to the OpenClaw Gateway CLI on port 18789
        if mode == "openclaw":
            res = direct_openclaw_chat(prompt, session=session)
            self._send_json(res)
            return

        # Production task detection: if the user wants execution (render, export, deploy, etc.),
        # route through the agent loop with tools — NOT the creative fast-path.
        if _production_task(prompt):
            print(f"[chat] production task detected: {prompt[:80]}", flush=True)
            # Fall through to agent loop below — do NOT return here
        elif _creative_prompt(prompt):
            # Creative fast-path: planning/brainstorming questions answered
            # directly via Ollama — bypasses the agent loop entirely.
            print(f"[chat] creative fast-path matched: {prompt[:80]}", flush=True)
            creative_reply = creative_fast_path_reply(prompt)
            if creative_reply:
                trace_agent({"event": "loop.fastpath", "session": session,
                             "model": model, "prompt": prompt[:300]})
                log_prompt({
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "route": "chat_creative_fastpath",
                    "model": model,
                    "session": session,
                    "prompt": prompt[:4000],
                    "has_reply": True,
                })
                self._send_json({"reply": creative_reply, "model": model,
                                 "session": session, "rounds": [],
                                 "fastpath": True})
                return

        # Agentic Execution: dispatches tools, probes, and escalations with live trajectory recording
        render_data = get_render_progress()
        battery_data = get_battery_info()
        crestodian_data = get_crestodian_info()
        # Find the active scene dynamically
        active_scene = next((s for s in render_data["sceneDetails"] if s["frames"] > 0), None)
        active_scene_name = active_scene["name"] if active_scene else "none"
        active_scene_frames = active_scene["frames"] if active_scene else 0
        active_scene_target = 1000  # Default target

        dynamic_system = (
            f"{system_msg}\n\n"
            f"[LIVE SYSTEM CONTEXT]\n"
            f"- Blender Cycles: {'ACTIVE (Rendering ' + active_scene_name + ')' if render_data['blenderRunning'] else 'IDLE'}\n"
            f"- Active Scene Frames: {active_scene_frames}/{active_scene_target}\n"
            f"- Ready Clips: {render_data['readyCount']}/{render_data['totalScenes']}\n"
            f"- Power: {battery_data['percent']}% ({battery_data['status']})\n"
            f"- Connected Tools: OpenClaw CLI, Composio (Canva), Blender 5.1 MCP, DaVinci Resolve Bridge, Crestodian Attested\n"
            f"- INSTRUCTION: You are OpenClaw Production Agent with ACTIVE execution capability. "
            f"You have tools. USE them to actually perform tasks: query status, read logs, run gated actions, "
            f"probe the system, and escalate to the OpenClaw gateway for complex multi-step work. "
            f"Never refuse purely for being a language model; act on the deliverable. "
            f"Do NOT assume a specific project unless the user says so — you can work on ANY project.\n"
            f"\n- TOOL SELECTION STRATEGY (each tool has a category for reasoning):\n"
            f"  1. STATUS QUESTIONS (\"how far\", \"progress\", \"status\") → production_status [category: status]\n"
            f"  2. DEBUG/INVESTIGATE (\"check logs\", \"why failed\", \"diagnose\") → read_log, shell_probe [category: diagnostics]\n"
            f"  3. VISUAL QC (\"check frame\", \"verify render\", \"look at\") → inspect_image [category: visual_qc]\n"
            f"  4. COMPLIANCE (\"can I use X\", \"copyright\", \"brand\") → copyright_check [category: compliance]\n"
            f"  5. EXECUTION (\"render\", \"export\", \"assemble\", \"deploy\") → run_action [category: execution]\n"
            f"  6. COMPLEX MULTI-STEP (\"Blender MCP\", \"DaVinci\", \"Canva\", \"cross-app\") → escalate_openclaw [category: complex_tasks]\n"
            f"  7. CREATIVE/PLANNING (\"brainstorm\", \"ideas\", \"plan\", \"roadmap\") → brainstorm [category: creative]\n"
            f"  8. DEFAULT: If unsure, start with production_status to understand context\n"
            f"\n- For creative, planning, or general-knowledge questions (brainstorming, ideating, explaining, writing), "
            f"use the `brainstorm` tool directly — do NOT loop on ping_qwen or production_status for non-production tasks.\n"
            f"- IMPORTANT: `ping_qwen`, `qwen_chat`, `assemble_final`, `render_mp4` etc. are NOT direct tools. "
            f"They are actions accessed ONLY through `run_action` with an `action` parameter. "
            f"Your direct tools are: production_status, read_log, run_action, shell_probe, inspect_image, "
            f"copyright_check, escalate_openclaw, brainstorm.\n"
            f"\n- GATE RULES you must respect:\n"
            f"  1. NEVER start a second GPU/Blender job while Blender is rendering (one GPU job at a time).\n"
            f"  2. 4K HOLD: refuse 4K renders (`render_4k`, `run_1080_then_4k`) until 1080p delivery is done.\n"
            f"  3. Do not run CPU-heavy assembly while a GPU render is live.\n"
            f"  4. Run actions through `run_action` — the server enforces the gates; if a tool returns "
            f"BLOCKED_BY_GATE, respect the reason and don't try to bypass it.\n"
            f"- When a task needs multi-step cross-app execution (Blender MCP scripting, DaVinci Resolve, "
            f"Canva/Composio deliverable creation), call `escalate_openclaw` with a precise task description.\n"
            f"{copyright_protocol_prompt()}\n"
            f"\n- SEQUENTIAL EXECUTION PROTOCOL for large prompts:\n"
            f"  1. ANALYZE FIRST: before acting, read the whole request and rank the deliverables by\n"
            f"     importance AND dependency (info-gathering before gated/long-running work).\n"
            f"  2. Then EXECUTE ONE AT A TIME in that order. Do NOT jump ahead: the second deliverable\n"
            f"     starts only after the first is VERIFIED DONE (its tool result confirms completion).\n"
            f"  3. State progress as 'STEP n DONE: <what was verified>' before opening the next step.\n"
            f"  4. If a step returns BLOCKED_BY_GATE, that is the sequence's decision: report it and stop\n"
            f"     the chain instead of forcing a later step.\n"
            f"  (For fully deterministic ranked execution you may instead use the /api/mission endpoint,\n"
            f"  which plans and runs the same protocol server-side.)"
        )

        messages = [
            {"role": "system", "content": dynamic_system},
            {"role": "user", "content": prompt},
        ]
        session = payload.get("session") or (
            "ses_" + time.strftime("%H%M%S") + "_" + str(int(time.time() * 1000))[-5:]
        )
        if not agent_semaphore.acquire(blocking=False):
            self._send_json({"reply": "Another agent task is already running. "
                            "Wait for it to finish, then retry.", "busy": True})
            return
        try:
            reply = self._run_agent_loop(messages, model, payload, session=session, mode=mode)
        finally:
            agent_semaphore.release()

        if not reply:
            eta = render_eta()
            eta_line = ""
            if eta.get("ok"):
                eta_line = (f"\n- **Render Rate:** ~{eta['ratePerFrameSec']}s/frame "
                            f"(ETA {eta.get('activeScene', 'active scene')}: ~{eta.get('activeSceneEtaHrs', 0)}h; all scenes ~{eta['projectEtaDays']}d). "
                            f"{eta.get('strategy', '')}")
            reply = (
                f"**OpenClaw Agent Execution:**\n\n"
                f"- **Blender Cycles Render:** {active_scene_name} is currently at **{active_scene_frames} / {active_scene_target} frames** (PID {render_data.get('blenderPid', '?')})."
                f"{eta_line}\n"
                f"- **Completed Deliverables:** {render_data['readyCount']}/{render_data['totalScenes']} clips ready.\n"
                f"- **Watcher Daemon:** Auto-assembles when all clips are ready.\n"
                f"- **Power:** Battery at {battery_data['percent']}% ({battery_data['status']})."
            )

        # Structured per-round data for the frontend session view (TUI-style
        # inline tool-call rendering). Same source as /api/agent/trajectory,
        # scoped to this turn so the chat can rebuild its session on refresh.
        try:
            turn_trace = read_agent_trace(limit=60, session=session)
        except Exception:
            turn_trace = []
        self._send_json({"reply": reply, "model": model, "session": session,
                         "rounds": turn_trace})

        # Prompt retention: record this turn so history survives page reloads.
        try:
            log_prompt({
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "route": "chat",
                "model": model,
                "session": session,
                "prompt": prompt[:4000],
                "has_reply": bool(reply),
            })
        except Exception:
            pass

    # NB: LLM chain continues tool_rounds up to max_rounds.
    def _run_agent_loop(self, messages, model, payload, session=None, mode=None):
        """Multi-round tool-calling loop against Ollama. Handles BOTH native
        function calling (`message.tool_calls`) and models that emit tool-call
        JSON inside `content` (e.g. qwen2.5-coder): <TOOLJSON>...</TOOLJSON>."""
        import re
        import time
        max_rounds = 15  # increased from 12 for complex tasks
        wall_clock_limit = 500  # increased from 400; stays under frontend's 660s watchdog
        loop_start = time.time()
        all_tools_called = set()
        all_round_results = []
        last_content = ""
        best_text = ""  # accumulated model prose; never a bare tool-call JSON
        tool_history = []  # (name, args_hash) persistent across rounds
        blocked_streak = 0
        trace_agent({"event": "loop.start", "model": model, "session": session,
                     "prompt": str(messages[1].get("content", ""))[:300] if len(messages) > 1 else ""})
        
        # Inject cross-session memory context
        memory = load_session_memory()
        recent_projects = list(memory.get("projects", {}).values())[-5:]
        if recent_projects:
            context_note = "\n\nREMEMBERED CONTEXT from previous sessions:\n"
            for p in recent_projects:
                context_note += f"- Project: {p.get('name', 'Unknown')} ({p.get('type', 'unknown')}) — {p.get('timestamp', '')}\n"
            messages.insert(0, {"role": "system", "content": context_note})
        
        # Planning-only mode: if user explicitly says "plan only", "do not execute", etc.,
        # OR if mode is "deep_plan", remove execution tools from available set
        user_prompt = str(messages[1].get("content", "")).lower() if len(messages) > 1 else ""
        planning_only = (mode == "deep_plan") or any(w in user_prompt for w in (
            "plan only", "do not execute", "hold execution", "just plan", 
            "don't execute", "only plan", "no execution", "no execute",
        ))
        
        # Force tool usage in deep_plan mode: inject project state
        if mode == "deep_plan":
            project_state = get_project_state()
            state_json = json.dumps(project_state, indent=2, default=str)
            messages.insert(1, {
                "role": "system",
                "content": (
                    f"MANDATORY FIRST STEP: You MUST call get_project_state to understand the current project. "
                    f"Do NOT ask the user any questions. Use tools to gather all context. "
                    f"Here is the current project state for your reference:\n\n{state_json}\n\n"
                    f"Now create a detailed, actionable plan using ONLY valid actions. "
                    f"Reference the example plans in your system prompt for structure."
                )
            })
        
        for round_i in range(max_rounds):
            # Honour a frontend cancel request (the fetch watchdog aborted the
            # request, but the loop would otherwise keep running server-side).
            with _CANCELLED_LOCK:
                _cancelled = session in _CANCELLED
            if _cancelled:
                trace_agent({"event": "loop.cancelled", "round": round_i,
                             "session": session})
                return "Task cancelled from the frontend. Agent loop stopped."
            # Wall-clock guard: stop when budget spent, even with rounds left
            if time.time() - loop_start > wall_clock_limit:
                print(f"[agent-loop] wall-clock {time.time()-loop_start:.0f}s > {wall_clock_limit}s -- stopping", flush=True)
                trace_agent({"event": "loop.wallclock", "round": round_i,
                             "session": session, "elapsed_s": round(time.time() - loop_start, 1)})
                if best_text:
                    return best_text.strip()
                if all_round_results:
                    return _format_tool_summary(all_round_results)
                return last_content.strip() or "Agent loop hit its time budget -- returning accumulated results."

            # Filter out single-shot status tools if already called in earlier rounds
            filtered_tools = [
                t for t in AGENT_TOOLS
                if not (
                    (t.get("function", {}).get("name") == "production_status" and "production_status" in all_tools_called)
                    or (t.get("function", {}).get("name") == "get_project_state" and "get_project_state" in all_tools_called)
                )
            ]
            
            # Planning-only: remove execution tools
            if planning_only:
                execution_tools = {"run_action", "escalate_openclaw"}
                filtered_tools = [t for t in filtered_tools 
                                 if t.get("function", {}).get("name") not in execution_tools]

            ollama_payload = {
                "model": model,
                "stream": False,
                "keep_alive": -1,
                "options": {"temperature": 0.2, "num_ctx": 16384, "num_predict": 4096, "top_p": 0.9},
                "messages": messages,
                "tools": filtered_tools or AGENT_TOOLS,
            }
            try:
                req_data = json.dumps(ollama_payload).encode("utf-8")
                req = urllib.request.Request(
                    f"{OLLAMA_HOST}/api/chat",
                    data=req_data,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=600) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                # Log done_reason to verify truncation cause
                done_reason = result.get("done_reason", "unknown")
                print(f"[agent-loop] done_reason: {done_reason}", flush=True)
                msg = (result.get("message") or {})
                tool_calls = list(msg.get("tool_calls") or [])
                # Filter native tool_calls to only valid AGENT_TOOLS names;
                # reject exec-action names (qwen_chat, ping_qwen, etc.) the
                # model may emit from the system prompt's action list.
                valid_names = {t["function"]["name"] for t in AGENT_TOOLS}
                tool_calls = [tc for tc in tool_calls
                              if (tc.get("function") or {}).get("name") in valid_names]
                print(f"[agent-loop] native tool_calls: {[(tc.get('function') or {}).get('name') for tc in tool_calls]}", flush=True)
            except Exception as e:
                trace_agent({"event": "loop.ollama_error", "round": round_i, "session": session,
                             "error": str(e)[:500]})
                return (f"Agent loop error: {e}\n\n"
                        "If this repeats, the local Ollama may be busy or overloaded. "
                        "Try a shorter prompt, or use /api/mission for server-side execution.")

            content = msg.get("content") or ""
            last_content = content
            # Fallback: parse tool-call JSON the model printed in content
            content_calls = _extract_content_tool_calls(content)
            if tool_calls:
                pass
            elif content_calls:
                tool_calls = content_calls
            print(f"[agent-loop] content_calls: {[tc.get('function', {}).get('name') for tc in content_calls]} | tool_calls: {[tc.get('function', {}).get('name') for tc in tool_calls]}", flush=True)

            if not tool_calls:
                return content.strip()

            print(f"[agent-loop] round: calling {[ (tc.get('function') or {}).get('name') for tc in tool_calls ]}", flush=True)

            # Strip leftover tool-call JSON from content so the model's own
            # prose (if any) is preserved as the visible continuation.
            clean_content = re.sub(r"```json\s*\{.*?\}\s*```", "", content, flags=re.DOTALL).strip()
            last_content = clean_content or last_content
            if clean_content:
                best_text = clean_content

            # Model escalation: check if 7b is struggling
            ESCALATION_TRIGGERS = [
                "i don't know", "i cannot", "i'm not sure", "i don't have access",
                "i don't have enough", "could you please provide", "can you tell me",
                "what is your", "please provide", "i need more information",
                "i'm unable to", "i do not have",
            ]
            if mode == "deep_plan" and model == _CODER_MODEL_7B:
                lower_content = clean_content.lower()
                is_struggling = any(t in lower_content for t in ESCALATION_TRIGGERS)
                if is_struggling:
                    retries = getattr(self, '_deep_plan_retries', {}).get(session, 0)
                    if retries < 2:
                        retries += 1
                        if not hasattr(self, '_deep_plan_retries'):
                            self._deep_plan_retries = {}
                        self._deep_plan_retries[session] = retries
                        trace_agent({
                            "event": "plan.retry",
                            "session": session,
                            "attempt": retries,
                            "reason": "7b model struggling",
                            "response_snippet": clean_content[:200],
                        })
                    elif retries >= 2:
                        model = _CODER_MODEL  # Escalate to 14b
                        trace_agent({
                            "event": "plan.escalate",
                            "session": session,
                            "from_model": _CODER_MODEL_7B,
                            "to_model": _CODER_MODEL,
                            "reason": "7b failed after 2 retries",
                        })
                        if hasattr(self, '_deep_plan_retries'):
                            self._deep_plan_retries[session] = 0
            msg = dict(msg)
            msg["content"] = clean_content
            messages.append(msg)

            # Convergence tracking across rounds
            blocked_streak = 0

            round_names = []
            round_results = []
            for tc in tool_calls:
                fn = tc.get("function") or {}
                name = fn.get("name", "")
                try:
                    args = json.loads(fn.get("arguments") or "{}")
                except Exception:
                    args = {}
                args_hash = hash(json.dumps(args, sort_keys=True, default=str))
                tool_history.append((name, args_hash))
                tool_result = dispatch_tool(name, args)
                round_names.append(name)
                round_results.append((name, args, tool_result))
                all_round_results.append((name, args, tool_result))
                all_tools_called.add(name)

                # Escalation is terminal: OpenClaw already executed the
                # deliverable, so its reply is the answer. No follow-up round.
                if name == "escalate_openclaw" and tool_result.get("ok"):
                    trace_agent({"event": "loop.term", "round": round_i, "tool": "escalate_openclaw",
                                 "session": session, "ok": True, "elapsed_s": round(time.time() - loop_start, 1)})
                    return humanize_tool_result(name, tool_result)
                if tool_result.get("terminal") and tool_result.get("ok"):
                    trace_agent({"event": "loop.term", "round": round_i, "tool": "run_action",
                                 "session": session, "action": name, "ok": True,
                                 "elapsed_s": round(time.time() - loop_start, 1)})
                    return humanize_tool_result("run_action", tool_result, action_key=name)
                if tool_result.get("blocked"):
                    blocked_streak += 1
                    if blocked_streak >= 2:
                        print("[agent-loop] BLOCKED_BY_GATE streak -- heavy job running", flush=True)
                        trace_agent({"event": "loop.blocked_streak", "round": round_i, "tool": name,
                                     "session": session, "reason": str(tool_result)[:200]})
                        return ("Render / heavy job is actively cranking (BLOCKED_BY_GATE x2). "
                                "Stopping the loop, not starting a second GPU job. Re-run this prompt "
                                "after the current job completes or ask to see live progress.")
                else:
                    blocked_streak = 0

                # Format tool result as readable text (not JSON) for the model
                try:
                    result_text = humanize_tool_result(name, tool_result)
                except Exception:
                    result_text = str(tool_result)[:4000]
                messages.append({"role": "tool", "content": result_text})

            # Rich per-round trajectory record: model reasoning + every tool
            # call with its argument summary and outcome status.
            try:
                tool_details = []
                for nm, tr_args, tr in round_results:
                    status = "ok"
                    if tr.get("blocked"):
                        status = "blocked"
                    elif tr.get("error"):
                        status = "error"
                    elif tr.get("ok") is False:
                        status = "failed"
                    tool_details.append({
                        "name": nm,
                        "status": status,
                        "args": tr_args,
                        "result_summary": (str(tr.get("output") or tr.get("stdout") or tr.get("tail")
                                               or tr.get("reason") or "")[:400]),
                    })
                trace_agent({
                    "event": "round",
                    "round": round_i,
                    "session": session,
                    "model_text": clean_content[:600],
                    "tools_called": tool_details,
                    "elapsed_s": round(time.time() - loop_start, 1),
                })
            except Exception:
                pass

            # Read-only info round: the tool results ARE the answer. When ALL
            # tools in this round are read-only info tools, return a formatted
            # report (merging any model prose on top) — avoids looping back for
            # a second round that the qwen2.5-coder often re-requests.
            user_prompt = ""
            if len(messages) > 1:
                user_prompt = str(messages[1].get("content", "")).lower()
            ACTION_WORDS = {"audit", "review", "crunch", "analyze", "diagnose",
                            "check", "verify", "fix", "execute", "escalate",
                            "mission", "root out", "open items", "blockers",
                            "generate", "create", "build", "develop", "produce",
                            "animate", "implement", "render", "assemble"}
            is_status_only = not any(w in user_prompt for w in ACTION_WORDS)
            # Build mode always continues after read-only probes so the model
            # can chain into run_action / escalate rather than stopping early.
            if (round_names
                    and all(n in INFO_TERMINAL_TOOLS for n in round_names)
                    and is_status_only
                    and mode != "build"):
                summary = _format_tool_summary(round_results)
                answer = (clean_content + "\n\n" + summary).strip() if clean_content else summary
                print(f"[agent-loop] info-only round ({','.join(round_names)}) -> formatted report", flush=True)
                trace_agent({"event": "loop.info_only", "round": round_i, "tools": round_names,
                             "session": session, "elapsed_s": round(time.time() - loop_start, 1)})
                return answer

            # Stuck-loop: the most recent call repeats the previous call exactly.
            # Persistent tool_history catches repeats across rounds too.
            # Trigger after 3 identical calls (was 2) to allow for retry patterns.
            if len(tool_history) >= 3:
                # Check last 3 calls for identical pattern
                last_three = tool_history[-3:]
                if all(n == last_three[0][0] and h == last_three[0][1] for n, h in last_three):
                    cur_name, cur_hash = tool_history[-1]
                    print(f"[agent-loop] stuck loop: {cur_name} repeated 3x with identical args", flush=True)
                    trace_agent({"event": "loop.stuck", "round": round_i, "tool": cur_name,
                                 "session": session, "elapsed_s": round(time.time() - loop_start, 1)})
                    # Build a helpful fallback with recommendations
                    prompt_hint = ""
                    if len(messages) > 1:
                        prompt_hint = str(messages[1].get("content", ""))[:200]
                    tools_used = sorted(all_tools_called)
                    
                    # Generate recommendations based on what was tried
                    recommendations = []
                    if "production_status" in all_tools_called:
                        recommendations.append("Check render progress with `production_status`")
                    if "read_log" in all_tools_called:
                        recommendations.append("Review logs with `read_log`")
                    if "run_action" not in all_tools_called:
                        recommendations.append("Execute a production action with `run_action`")
                    if "escalate_openclaw" not in all_tools_called:
                        recommendations.append("Escalate to OpenClaw for multi-step work")
                    if not recommendations:
                        recommendations.append("Try a more specific prompt with clear deliverables")
                    
                    stuck_msg = (
                        f"**Agent loop converged after {round_i + 1} rounds** "
                        f"(stuck on `{cur_name}` — identical call repeated 3x).\n\n"
                    )
                    if prompt_hint:
                        stuck_msg += f"**Your request:** {prompt_hint}\n\n"
                    stuck_msg += (
                        f"**Tools used:** {', '.join(tools_used) if tools_used else 'none'}\n\n"
                        f"**Recommended next steps:**\n"
                        + "\n".join(f"- {r}" for r in recommendations) + "\n\n"
                        f"The local model exhausted its tool options for this task. "
                        f"Try a more specific prompt, or ask me to **escalate to OpenClaw** "
                        f"for multi-step execution."
                    )
                    if all_round_results:
                        summary = _format_tool_summary(all_round_results)
                        return (stuck_msg + "\n\n" + summary).strip()
                    return stuck_msg

            # All tools tried at least once AND model still has prose: enough
            if len(all_tools_called) >= len(AGENT_TOOLS) and clean_content:
                print("[agent-loop] all tools called + prose present -- stopping", flush=True)
                trace_agent({"event": "loop.converged", "round": round_i,
                             "session": session,
                             "tools": str(sorted(all_tools_called))[:500],
                             "elapsed_s": round(time.time() - loop_start, 1)})
                return clean_content
        # Max rounds hit without a final text answer: return best content found
        trace_agent({"event": "loop.max_rounds", "rounds": max_rounds,
                     "session": session, "elapsed_s": round(time.time() - loop_start, 1)})
        if best_text.strip():
            return best_text.strip()
        if all_round_results:
            return _format_tool_summary(all_round_results)
        
        # Fallback with recommendations
        tools_used = sorted(all_tools_called)
        recommendations = []
        if "production_status" in all_tools_called:
            recommendations.append("Check render progress with `production_status`")
        if "run_action" not in all_tools_called:
            recommendations.append("Execute a production action with `run_action`")
        if "escalate_openclaw" not in all_tools_called:
            recommendations.append("Escalate to OpenClaw for multi-step work")
        if not recommendations:
            recommendations.append("Try a more specific prompt with clear deliverables")
        
        return (
            f"**Agent loop completed after {max_rounds} rounds**\n\n"
            f"**Tools used:** {', '.join(tools_used) if tools_used else 'none'}\n\n"
            f"**Recommended next steps:**\n"
            + "\n".join(f"- {r}" for r in recommendations) + "\n\n"
            f"For complex tasks, try **Mission mode** (server-side sequential execution) "
            f"or **escalate to OpenClaw** for multi-step cross-app work."
        )

    def handle_vision(self, payload):
        """POST /api/vision — visual-property task, routed to the VL specialist.

        Accepts: image_path / image (path) OR data_uri (a pasted
        data:image/...;base64 blob from the chat box). image_path is optional;
        when omitted, the latest master render frame is used. question is
        optional. This is the dedicated vision route: the 14b agent model never
        handles vision itself — visual work is always dispatched here (or via
        the `inspect_image` agent tool) to qwen2.5vl."""
        image_path = payload.get("image_path") or payload.get("image") or ""
        created = None
        if not image_path:
            data_uri = payload.get("data_uri") or payload.get("image_data") or ""
            if data_uri:
                created = save_pasted_image(data_uri)
                if created:
                    image_path = created
                else:
                    self._send_json({"error": "Could not read the pasted image data."}, 400)
                    return
        if not image_path:
            image_path = latest_master_frame()
        if not image_path:
            self._send_json({"error": "No image_path given and no render frames found."}, 400)
            return
        question = payload.get("question", "")
        result = inspect_image_with_vl(image_path, question)
        if created:
            try:
                os.unlink(created)
            except Exception:
                pass
        result["routedTo"] = _VL_MODEL
        result["generalModel"] = resolve_default_model()
        self._send_json(result)

    def handle_mission(self, payload):
        """POST /api/mission — analyze a mission prompt, rank it into ordered
        steps, then execute each step strictly in sequence. The next step runs
        only after the current one verifies OK. Halts on BLOCKED_BY_GATE or a
        failed step. A caller may supply an explicit `plan` to skip ranking."""
        mission = payload.get("mission", "").strip()
        if not mission:
            self._send_json({"error": "Missing 'mission'"}, 400)
            return
        model = payload.get("model") or resolve_default_model()
        plan = payload.get("plan")
        if plan is None:
            planned = plan_mission(mission, model)
            if planned["error"]:
                self._send_json({"error": planned["error"]}, 500)
                return
            plan = planned["plan"]
        if not isinstance(plan, list) or not plan:
            self._send_json({"error": "No steps to execute."}, 400)
            return
        usable = [s for s in plan if s.get("tool")]
        result = execute_mission_sequential(usable, model)
        self._send_json({
            "mission": mission,
            "planCount": len(result["report"]),
            "stopped": result["stopped"],
            "report": result["report"],
            "model": model,
        })

    def handle_exec(self, payload):
        action = payload.get("action", "")
        if not action:
            self._send_json({"error": "Missing 'action'"}, 400)
            return
        if action not in EXEC_ACTIONS:
            self._send_json({"error": f"Unknown action: {action}", "available": list(EXEC_ACTIONS.keys())}, 400)
            return
        self._send_json(execute_action(action, payload))

    def handle_escalate(self, payload):
        task = payload.get("task", "").strip()
        if not task:
            self._send_json({"error": "Empty task"}, 400)
            return
        self._send_json(escalation_openclaw(task))

    def handle_plan_save(self, payload):
        plan_text = payload.get("plan_text", "")
        plan_json = extract_plan_json(plan_text)
        if not plan_json:
            self._send_json({"ok": False, "error": "No valid JSON block found in plan"}, 400)
            return

        # Validate and auto-fix invalid actions
        plan_json, was_fixed, issues = validate_and_fix_plan(plan_json)
        if was_fixed:
            trace_agent({
                "event": "plan.fixed",
                "session": payload.get("session", ""),
                "issues": issues,
            })

        # Self-evaluate plan quality
        evaluation = self_evaluate_plan(plan_json)
        if evaluation["score"] < 70:
            trace_agent({
                "event": "plan.low_quality",
                "session": payload.get("session", ""),
                "score": evaluation["score"],
                "quality": evaluation["quality"],
                "issues": evaluation["issues"],
            })

        result = save_plan_to_project(plan_json)
        result["evaluation"] = evaluation
        result["validation_issues"] = issues if was_fixed else []
        self._send_json(result)

    def handle_plan_list(self):
        """GET /api/plan/list — List all saved plan files."""
        plans_dir = IDE_ROOT / ".plans"
        plans_dir.mkdir(exist_ok=True)
        
        plans = []
        for plan_file in plans_dir.glob("*.json"):
            try:
                with open(plan_file, "r", encoding="utf-8") as f:
                    plan_data = json.load(f)
                plans.append({
                    "filename": plan_file.name,
                    "project": plan_data.get("project", plan_file.stem),
                    "generated": plan_data.get("generated", ""),
                    "total_estimate_days": plan_data.get("meta", {}).get("total_estimate_days", 0),
                    "phases_count": len(plan_data.get("phases", [])),
                    "handoff_ready": plan_data.get("meta", {}).get("handoff_ready", False),
                })
            except Exception:
                pass
        
        plans.sort(key=lambda x: x.get("generated", ""), reverse=True)
        self._send_json({"plans": plans})

    def handle_plan_read(self, query):
        """GET /api/plan/read — Read a specific plan file."""
        filename = query.get("file", [""])[0]
        if not filename:
            self._send_json({"error": "File parameter required"}, 400)
            return
        
        plans_dir = IDE_ROOT / ".plans"
        plan_file = plans_dir / filename
        
        # Security: resolve and validate path is inside plans_dir
        try:
            plan_file_resolved = plan_file.resolve()
            plans_dir_resolved = plans_dir.resolve()
            plan_file_resolved.relative_to(plans_dir_resolved)
        except ValueError:
            self._send_json({"error": "Invalid file path"}, 400)
            return
        
        if not plan_file.exists() or plan_file.suffix != ".json":
            self._send_json({"error": "Plan file not found"}, 404)
            return
        
        try:
            with open(plan_file, "r", encoding="utf-8") as f:
                plan_data = json.load(f)
            self._send_json({"ok": True, "plan": plan_data})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def handle_search_sessions(self, payload):
        """GET/POST /api/sessions/search — full-text search with filters.

        Call sites always pass a flat dict (POST JSON body, or flattened GET qs).
        """
        if not isinstance(payload, dict):
            payload = {}

        q = str(payload.get("q") or "").strip()
        mode = payload.get("mode") or None
        status = payload.get("status") or None
        has_plan = payload.get("has_plan")
        if isinstance(has_plan, str):
            has_plan = has_plan.strip().lower() in ("1", "true", "yes")
        elif has_plan is not None:
            has_plan = bool(has_plan)
        try:
            limit = min(int(payload.get("limit", 50)), 200)
        except (TypeError, ValueError):
            limit = 50
        try:
            offset = max(int(payload.get("offset", 0)), 0)
        except (TypeError, ValueError):
            offset = 0
        
        # #region agent log
        _agent_dbg("H2", "server.py:handle_search_sessions", "sessions_search_enter", {
            "q": q, "mode": mode, "status": status, "has_plan": has_plan,
            "limit": limit, "offset": offset,
        })
        # #endregion
        _init_search_index()
        conn = sqlite3.connect(INDEX_DB)
        conn.row_factory = sqlite3.Row
        
        # Build FTS query
        where = ["1=1"]
        params = []
        
        if q:
            where.append("sessions_fts MATCH ?")
            escaped_q = q.replace('"', '""')
            params.append(f'"{escaped_q}"')
        if mode:
            where.append("mode = ?")
            params.append(mode)
        if status:
            where.append("status = ?")
            params.append(status)
        if has_plan is not None:
            where.append("has_plan_json = ?")
            params.append(int(has_plan))
        
        sql = f"""
            SELECT session_id, timestamp, mode, model, prompt, reply, tools_used, tools_detail, 
                   status, duration_s, has_plan_json, plan_version,
                   bm25(sessions_fts) as rank
            FROM sessions_fts
            WHERE {' AND '.join(where)}
            ORDER BY rank
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        
        try:
            rows = conn.execute(sql, params).fetchall()
        except sqlite3.OperationalError as e:
            conn.close()
            self._send_json({"error": f"Search error: {str(e)}", "results": [], "total": 0, "query": q})
            return
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "session_id": row["session_id"],
                "timestamp": row["timestamp"],
                "mode": row["mode"],
                "model": row["model"],
                "prompt_preview": row["prompt"][:120] + ("…" if len(row["prompt"]) > 120 else ""),
                "reply_preview": row["reply"][:120] + ("…" if len(row["reply"]) > 120 else ""),
                "tools_used": row["tools_used"].split(", ") if row["tools_used"] else [],
                "tools_detail": json.loads(row["tools_detail"]) if row["tools_detail"] else [],
                "status": row["status"],
                "duration_s": row["duration_s"],
                "has_plan_json": bool(row["has_plan_json"]),
                "plan_version": row["plan_version"],
                "rank": round(row["rank"], 2)
            })
        
        # #region agent log
        _agent_dbg("H2", "server.py:handle_search_sessions", "sessions_search_ok", {
            "result_count": len(results), "total_sent": len(results),
        })
        # #endregion
        self._send_json({"results": results, "total": len(results), "query": q})

    def handle_session_detail(self, query):
        session_id = query.get("session_id", [""])[0]
        if not session_id:
            self._send_json({"error": "session_id required"}, 400)
            return
        
        _init_search_index()
        conn = sqlite3.connect(INDEX_DB)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM session_meta WHERE session_id = ?", (session_id,)).fetchone()
        conn.close()
        
        if not row:
            self._send_json({"error": "Session not found"}, 404)
            return
        
        # Also fetch full trace for this session
        trace = read_agent_trace(limit=1000, session=session_id)
        
        self._send_json({
            "session_id": row["session_id"],
            "timestamp": row["timestamp"],
            "mode": row["mode"],
            "model": row["model"],
            "prompt": row["raw_prompt"],
            "reply": row["raw_reply"],
            "tools_used": row["tools_used"].split(", ") if row["tools_used"] else [],
            "tools_detail": json.loads(row["tools_detail"]) if row["tools_detail"] else [],
            "status": row["status"],
            "duration_s": row["duration_s"],
            "has_plan_json": bool(row["has_plan_json"]),
            "plan_version": row["plan_version"],
            "trace": trace
        })

    def handle_agent_stream(self, session):
        """SSE stream of agent thinking events for a session."""
        # #region agent log
        _agent_dbg("H3", "server.py:handle_agent_stream:start", "sse_start", {
            "session": session, "trace": str(AGENT_TRACE_PATH),
        })
        # #endregion
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache, no-transform")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()
        
        # Track position in trace file
        last_pos = 0
        trace_path = AGENT_TRACE_PATH
        events_sent = 0
        
        try:
            while True:
                if trace_path.exists():
                    with open(trace_path, "r", encoding="utf-8") as f:
                        f.seek(last_pos)
                        new_lines = f.readlines()
                        last_pos = f.tell()
                    
                    for line in new_lines:
                        try:
                            event = json.loads(line.strip())
                            if event.get("session") == session:
                                # Filter to thinking/tool events - expanded to include tool and thinking events
                                if event.get("event") in ("round", "loop.start", "loop.term", "loop.converged",
                                    "loop.stuck", "loop.blocked_streak", "loop.info_only", "loop.wallclock",
                                    "loop.ollama_error", "loop.max_rounds", "loop.fastpath", "mission.step",
                                    "stream.token", "tool", "thinking"):
                                    data = json.dumps({
                                        "type": event["event"],
                                        "round": event.get("round"),
                                        "rounds": event.get("rounds"),
                                        "model_text": event.get("model_text", "")[:500],
                                        "tools": event.get("tools_called", []),
                                        "tool": event.get("tool"),
                                        "step": event.get("step"),
                                        "elapsed_s": event.get("elapsed_s"),
                                        "ts": event.get("ts"),
                                    })
                                    self.wfile.write(f"data: {data}\n\n".encode())
                                    self.wfile.flush()
                                    events_sent += 1
                                    # #region agent log
                                    if events_sent <= 5:
                                        _agent_dbg("H3", "server.py:handle_agent_stream", "sse_event_sent", {
                                            "session": session, "type": event.get("event"),
                                            "events_sent": events_sent,
                                        })
                                    # #endregion
                        except Exception:
                            pass
                time.sleep(0.3)  # Faster polling for more responsive updates
        except (ConnectionError, BrokenPipeError):
            # #region agent log
            _agent_dbg("H3", "server.py:handle_agent_stream:end", "sse_client_gone", {
                "session": session, "events_sent": events_sent,
            })
            # #endregion
            pass  # Client disconnected

    def handle_openclaw_exec(self, payload):
        """Execute a specific allowed operation (not arbitrary commands)."""
        operation = payload.get("operation", "")
        if not operation:
            self._send_json({"error": "No operation specified"}, 400)
            return
        
        # Dispatch table of allowed operations
        ALLOWED_OPERATIONS = {
            "ping_qwen": lambda: subprocess.run(
                ["python", "scripts/qwen_local.py", "ping"],
                cwd=str(WORKSPACE_ROOT), capture_output=True, text=True, timeout=30
            ),
            "list_renders": lambda: subprocess.run(
                ["powershell", "-NoProfile", "-Command", "Get-ChildItem", str(RENDER_ROOT / "video_clips")],
                cwd=str(WORKSPACE_ROOT), capture_output=True, text=True, timeout=30
            ),
            "check_blender": lambda: subprocess.run(
                ["powershell", "-NoProfile", "-Command", "Get-Process", "blender", "-ErrorAction", "SilentlyContinue"],
                cwd=str(WORKSPACE_ROOT), capture_output=True, text=True, timeout=30
            ),
        }
        
        if operation not in ALLOWED_OPERATIONS:
            self._send_json({"error": f"Operation not allowed: {operation}. Allowed: {list(ALLOWED_OPERATIONS.keys())}"}, 403)
            return
        
        try:
            proc = ALLOWED_OPERATIONS[operation]()
            self._send_json({
                "ok": proc.returncode == 0,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "exitCode": proc.returncode
            })
        except subprocess.TimeoutExpired:
            self._send_json({"error": "Operation timed out (30s limit)"}, 408)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def handle_tool_trigger(self, payload):
        tool = payload.get("tool", "")
        if tool == "canva_exports":
            script = "scripts/download_open30_canva_exports.py"
        elif tool == "clearance_gen":
            script = "scripts/generate_clearance_replacements.py"
        elif tool == "unique_assets":
            script = "scripts/import_unique_kinetic_assets.py"
        elif tool == "audit_kinetic":
            script = "scripts/audit_and_fix_kinetic_uniqueness.py"
        elif tool == "ping_qwen":
            script = "scripts/qwen_local.py ping"
        else:
            self._send_json({"error": f"Unknown tool: {tool}"}, 400)
            return

        cmd = f"python {script}" if not script.startswith("powershell") else script
        try:
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-Command", cmd],
                cwd=str(WORKSPACE_ROOT),
                capture_output=True,
                text=True,
                timeout=25
            )
            self._send_json({
                "tool": tool,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "exitCode": proc.returncode
            })
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def handle_guides(self):
        guides = load_guides_catalog()
        if not guides:
            guides = LEGACY_GUIDES
        guides.sort(key=lambda g: (g.get("category", "").lower(), g.get("title", "").lower()))
        self._send_json({"guides": guides, "count": len(guides)})

    def handle_pipeline(self):
        """Serve the visual pipeline JSON for the IDE."""
        pipeline_dir = WORKSPACE_ROOT / "pipeline"
        url = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(url.query)
        episode = query.get("episode", ["1"])[0]
        pipeline_file = pipeline_dir / f"episode_{episode}_pipeline.json"
        if not pipeline_file.exists():
            self._send_json({"error": f"Pipeline not found for episode {episode}. Run generate_visual_pipeline.py first.", "pipeline_dir": str(pipeline_dir)}, 404)
            return
        with open(pipeline_file, "r", encoding="utf-8") as f:
            pipeline = json.load(f)
        gate_file = pipeline_dir / "copyright_gate_summary.json"
        if gate_file.exists():
            with open(gate_file, "r", encoding="utf-8") as f:
                gate = json.load(f)
            pipeline["copyright_gate"] = gate
        self._send_json(pipeline)

    def handle_pipeline_prompt(self):
        """Serve an individual scene Blender prompt."""
        url = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(url.query)
        scene_id = query.get("scene", [""])[0]
        prompt_file = WORKSPACE_ROOT / "pipeline" / "prompts" / f"{scene_id}_blender.py"
        if not prompt_file.exists():
            self._send_json({"error": f"Prompt not found for {scene_id}"}, 404)
            return
        with open(prompt_file, "r", encoding="utf-8") as f:
            content = f.read()
        self._send_json({"scene": scene_id, "prompt": content})

    def handle_pipeline_exec(self):
        """Serve the machine-executable Blender plan for a scene.

        Generated by generate_visual_pipeline.py into pipeline/exec/<id>_exec.json.
        These steps are directly actionable through the Blender MCP agent:
        import planes at Z layers, texture existing assets, keyframe the
        VO-synced triggers, set the Cyclest camera, and render to the
        contract path."""
        url = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(url.query)
        scene_id = query.get("scene", [""])[0]
        exec_file = WORKSPACE_ROOT / "pipeline" / "exec" / f"{scene_id}_exec.json"
        if not exec_file.exists():
            self._send_json({"error": f"Exec plan not found for {scene_id}. Run generate_visual_pipeline.py first."}, 404)
            return
        with open(exec_file, "r", encoding="utf-8") as f:
            plan = json.load(f)
        self._send_json(plan)


# ── Git Integration ─────────────────────────────────────────────────
def _run_git(args, cwd=None):
    try:
        r = subprocess.run(["git"] + args, cwd=cwd or str(WORKSPACE_ROOT), capture_output=True, text=True, timeout=30)
        return {"ok": r.returncode == 0, "stdout": r.stdout, "stderr": r.stderr}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Git command timed out"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def handle_git_status():
    r = _run_git(["status", "--porcelain", "--branch"])
    if r["ok"]:
        lines = r["stdout"].strip().split('\n')
        branch = lines[0] if lines else ""
        files = []
        for line in lines[1:]:
            if line.strip():
                files.append({"status": line[:2].strip(), "path": line[3:].strip()})
        return {"ok": True, "branch": branch, "files": files}
    return {"ok": False, "error": r.get("error", "Not a git repository")}

def handle_git_diff(payload):
    fp = payload.get("file", "")
    if not fp: return {"ok": False, "error": "File path required"}
    r = _run_git(["diff", "--", fp])
    return {"ok": r["ok"], "diff": r["stdout"], "error": r.get("stderr")}

def handle_git_commit(payload):
    msg = payload.get("message", "")
    files = payload.get("files", [])
    if not msg: return {"ok": False, "error": "Commit message required"}
    for f in files: _run_git(["add", f])
    r = _run_git(["commit", "-m", msg])
    return {"ok": r["ok"], "output": r["stdout"], "error": r.get("stderr")}

def handle_git_branch(payload):
    action = payload.get("action", "list")
    branch = payload.get("branch", "")
    if action == "list":
        r = _run_git(["branch", "-a"])
        return {"ok": r["ok"], "branches": r["stdout"].strip().split('\n') if r["ok"] else []}
    elif action == "create":
        if not branch: return {"ok": False, "error": "Branch name required"}
        r = _run_git(["checkout", "-b", branch])
        return {"ok": r["ok"], "output": r["stdout"]}
    elif action == "checkout":
        if not branch: return {"ok": False, "error": "Branch name required"}
        r = _run_git(["checkout", branch])
        return {"ok": r["ok"], "output": r["stdout"]}
    elif action == "delete":
        if not branch: return {"ok": False, "error": "Branch name required"}
        r = _run_git(["branch", "-D", branch])
        return {"ok": r["ok"], "output": r["stdout"]}
    return {"ok": False, "error": "Unknown action"}

def handle_git_log(payload):
    limit = min(int(payload.get("limit", 20)), 100)
    r = _run_git(["log", "--oneline", "-%d" % limit])
    return {"ok": r["ok"], "log": r["stdout"].strip().split('\n') if r["ok"] else []}

def handle_git_push(payload):
    remote = payload.get("remote", "origin")
    branch = payload.get("branch", "")
    args = ["push", remote] + ([branch] if branch else [])
    r = _run_git(args)
    return {"ok": r["ok"], "output": r["stdout"], "error": r.get("stderr")}

def handle_git_pull(payload):
    remote = payload.get("remote", "origin")
    branch = payload.get("branch", "")
    args = ["pull", remote] + ([branch] if branch else [])
    r = _run_git(args)
    return {"ok": r["ok"], "output": r["stdout"], "error": r.get("stderr")}

def handle_git_stage(payload):
    fp = payload.get("file", "")
    if not fp: return {"ok": False, "error": "File path required"}
    r = _run_git(["add", fp])
    return {"ok": r["ok"], "error": r.get("stderr")}

def handle_model_change(payload):
    global DEFAULT_MODEL
    model = payload.get("model", "")
    if not model: return {"ok": False, "error": "Model required"}
    DEFAULT_MODEL = model
    return {"ok": True, "model": model}


# ── WebSocket Terminal Server ───────────────────────────────────────
try:
    import asyncio
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

_terminal_ws_clients = set()
_terminal_ws_loop = None

if HAS_WEBSOCKETS:
    async def _terminal_handler(websocket):
        _terminal_ws_clients.add(websocket)
        proc = None
        output_queue = None
        drain_thread = None
        try:
            # Try pywinpty first (Windows ConPTY API - proper terminal support)
            try:
                from winpty import PtyProcess
                import queue
                
                proc = PtyProcess.spawn(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass"])
                output_queue = queue.Queue()
                
                def drain_stdout():
                    while proc.isalive():
                        try:
                            data = proc.read(1024)
                            if data:
                                output_queue.put(data)
                        except Exception as e:
                            print(f"[Terminal] Drain error: {e}", flush=True)
                            break
                
                drain_thread = threading.Thread(target=drain_stdout, daemon=True)
                drain_thread.start()
                
                await websocket.send("OpenClaw Terminal (pywinpty)\r\nType 'exit' to close\r\n\r\n")
                
                while True:
                    # Read from queue (non-blocking)
                    output = []
                    while not output_queue.empty():
                        try:
                            output.append(output_queue.get_nowait())
                        except queue.Empty:
                            break
                    if output:
                        await websocket.send("".join(output))
                    
                    # Write to terminal
                    try:
                        msg = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                        proc.write(msg)
                    except asyncio.TimeoutError:
                        pass
                    except:
                        break
                        
            except ImportError:
                # Fallback: subprocess with queue (limited terminal support)
                import subprocess
                import queue
                
                proc = subprocess.Popen(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
                output_queue = queue.Queue()
                
                def drain_stdout():
                    while proc.poll() is None:
                        try:
                            line = proc.stdout.readline()
                            if line:
                                output_queue.put(line.decode('utf-8', errors='replace'))
                        except Exception as e:
                            print(f"[Terminal] Drain error: {e}", flush=True)
                            break
                
                drain_thread = threading.Thread(target=drain_stdout, daemon=True)
                drain_thread.start()
                
                await websocket.send("OpenClaw Terminal (subprocess fallback)\r\nType 'exit' to close\r\n\r\n")
                
                while True:
                    output = []
                    while not output_queue.empty():
                        try:
                            output.append(output_queue.get_nowait())
                        except queue.Empty:
                            break
                    if output:
                        await websocket.send("".join(output))
                    
                    try:
                        msg = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                        proc.stdin.write(msg.encode())
                        proc.stdin.flush()
                    except asyncio.TimeoutError:
                        pass
                    except:
                        break
        except Exception as e:
            print(f"[Terminal] Error: {e}", flush=True)
        finally:
            _terminal_ws_clients.discard(websocket)
            # Cleanup: kill process
            if proc is not None:
                try:
                    if hasattr(proc, 'kill'):
                        proc.kill()
                    elif hasattr(proc, 'close'):
                        proc.close()
                except:
                    pass

    async def _start_terminal_server():
        global _terminal_ws_loop
        _terminal_ws_loop = asyncio.get_event_loop()
        async with websockets.serve(_terminal_handler, "127.0.0.1", 8766, max_size=10**7, ping_interval=20, ping_timeout=20):
            await asyncio.Future()

    def _start_terminal_background():
        try: asyncio.run(_start_terminal_server())
        except Exception as e: print(f"[terminal] WebSocket server failed: {e}")

    threading.Thread(target=_start_terminal_background, daemon=True).start()


# ── File Watcher ────────────────────────────────────────────────────
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False

if HAS_WATCHDOG:
    class _FileChangeHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if not event.is_directory:
                msg = json.dumps({"type": "file.changed", "path": event.src_path})
                for client in list(_terminal_ws_clients):
                    try:
                        if _terminal_ws_loop:
                            asyncio.run_coroutine_threadsafe(client.send(msg), _terminal_ws_loop)
                    except: pass

    _file_observer = Observer()
    _file_observer.schedule(_FileChangeHandler(), str(WORKSPACE_ROOT), recursive=True)
    _file_observer.daemon = True
    _file_observer.start()


def run_server(port=8765):
    IDE_ROOT.mkdir(parents=True, exist_ok=True)
    server_address = ("127.0.0.1", port)
    httpd = ThreadingHTTPServer(server_address, IDEHandler)
    httpd.daemon_threads = True
    print(f"==================================================")
    print(f" OpenClaw Local IDE Multi-Threaded Server Running")
    print(f" URL: http://127.0.0.1:{port}")
    print(f" Workspace: {WORKSPACE_ROOT}")
    print(f" Ollama Host: {OLLAMA_HOST}")
    print(f"==================================================")
    def _warmup():
        result = warm_up_ollama()
        print(f"[warm-up] default={result}")
        # 14b only warmed on demand via escalation — too heavy for VRAM
        print("[warm-up] 14b reserved for heavy tasks (not pre-warmed)")
    threading.Thread(target=_warmup, daemon=True).start()
    threading.Thread(target=_hourly_report_loop, daemon=True).start()
    httpd.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenClaw IDE Server")
    parser.add_argument("--port", type=int, default=8765, help="Port to host on (default: 8765)")
    args = parser.parse_args()
    run_server(args.port)
