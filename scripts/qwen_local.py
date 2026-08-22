"""
Local Qwen (Ollama) client for Africa S1 production assists.

Default model: qwen2.5-coder:14b @ http://127.0.0.1:11434
Tuned for long JSON/script drafts with 32k context.

Usage:
  python scripts/qwen_local.py ping
  python scripts/qwen_local.py chat "Summarize PRE_4K_GATE open items"
  python scripts/qwen_local.py json "Return beat sheet JSON for TED-Ed open" --out renders/quality/qwen_out.json

Env overrides:
  AFRICA_QWEN_MODEL   (default qwen2.5-coder:14b)
  AFRICA_QWEN_HOST    (default http://127.0.0.1:11434)
  AFRICA_QWEN_TEMP    (default 0.2)
  AFRICA_QWEN_NUM_CTX (default 16384)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

HOST = os.environ.get("AFRICA_QWEN_HOST", "http://127.0.0.1:11434").rstrip("/")
MODEL = os.environ.get("AFRICA_QWEN_MODEL", "qwen2.5-coder:14b")
TEMP = float(os.environ.get("AFRICA_QWEN_TEMP", "0.2"))
NUM_CTX = int(os.environ.get("AFRICA_QWEN_NUM_CTX", "16384"))
NUM_PREDICT = int(os.environ.get("AFRICA_QWEN_NUM_PREDICT", "4096"))

SYSTEM_PROD = (
    "You are a production assistant for Africa Season 1 (Silicon Savannah). "
    "Obey: Blender 5.1.2 only, 4K HOLD, one GPU job at a time, never restart "
    "in-progress HQ from frame 0, VO is user voice only, yellow-base TED-Ed style. "
    "Prefer concrete file paths and JSON when asked. Do not invent completed renders."
)


def _post(path: str, payload: dict, timeout: int = 600) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{HOST}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get(path: str, timeout: int = 15) -> dict:
    req = urllib.request.Request(f"{HOST}{path}", method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def ping() -> int:
    try:
        tags = _get("/api/tags")
        names = [m.get("name") for m in tags.get("models") or []]
        print("OLLAMA_OK", HOST)
        print("MODELS", ", ".join(names) or "(none)")
        if MODEL not in names:
            print("WARN missing model:", MODEL)
            return 2
        r = _post(
            "/api/generate",
            {
                "model": MODEL,
                "prompt": "Reply with exactly: QWEN_OK",
                "stream": False,
                "options": {"num_predict": 16, "temperature": 0},
            },
            timeout=180,
        )
        text = (r.get("response") or "").strip()
        print("GENERATE", text)
        return 0 if "QWEN_OK" in text else 1
    except urllib.error.URLError as e:
        print("OLLAMA_DOWN", e)
        return 1


def chat(prompt: str, system: str | None = None) -> str:
    payload = {
        "model": MODEL,
        "stream": False,
        "options": {
            "temperature": TEMP,
            "num_ctx": NUM_CTX,
            "num_predict": NUM_PREDICT,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
        },
        "messages": [
            {"role": "system", "content": system or SYSTEM_PROD},
            {"role": "user", "content": prompt},
        ],
    }
    r = _post("/api/chat", payload, timeout=900)
    msg = r.get("message") or {}
    return (msg.get("content") or "").strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="Local Qwen via Ollama")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("ping", help="Health-check Ollama + model")

    p_chat = sub.add_parser("chat", help="One-shot chat")
    p_chat.add_argument("prompt")
    p_chat.add_argument("--system", default=None)

    p_json = sub.add_parser("json", help="Chat and write raw reply to file")
    p_json.add_argument("prompt", nargs="?", default=None)
    p_json.add_argument("--prompt-file", dest="prompt_file", default=None)
    p_json.add_argument("--out", required=True)
    p_json.add_argument("--system", default=None)

    args = ap.parse_args()
    if args.cmd == "ping":
        return ping()
    if args.cmd == "chat":
        print(chat(args.prompt, args.system))
        return 0
    if args.cmd == "json":
        prompt = args.prompt
        if args.prompt_file:
            prompt = Path(args.prompt_file).read_text(encoding="utf-8")
        if not prompt:
            print("Need prompt or --prompt-file", file=sys.stderr)
            return 2
        text = chat(prompt, args.system)
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print("WROTE", out, "chars=", len(text))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
