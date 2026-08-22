"""Non-blocking pipeline integration tests for the OpenClaw Local IDE.

Exercises the prompt-to-generation API surface only (no Blender, no GPU,
no render commands). Safe to run while Scene 03 is actively rendering.

Run:  python test_pipeline.py
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8765"


def get(path):
    req = urllib.request.Request(BASE + path)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"error": body}


def post(path, payload):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def check(name, cond, detail=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {detail}" if detail else ""))
    return cond


results = []

# 1. Status / models
st, status = get("/api/status")
results.append(check("status 200 + models online",
                     st == 200 and status.get("ollama", {}).get("online") is True,
                     f"models={status.get('ollama', {}).get('models')}"))

# 2. Render progress
st, prog = get("/api/render/progress")
results.append(check("render/progress 200 + scene03 data",
                     st == 200 and any(s["name"] == "03_Beat1_Hubs" for s in prog.get("scenes", [])),
                     f"blenderRunning={prog.get('blenderRunning')} ready={prog.get('readyCount')}/10"))

# 3. Pipeline prompt (S01 and S03)
for sid in ("S01", "S03"):
    st, data = get(f"/api/pipeline/prompt?scene={sid}")
    results.append(check(f"pipeline/prompt {sid} returns Blender prompt",
                         st == 200 and "prompt" in data and len(data["prompt"]) > 100,
                         f"{len(data.get('prompt',''))} chars"))

# 4. Pipeline exec plan
st, plan = get("/api/pipeline/exec?scene=S03")
results.append(check("pipeline/exec S03 returns exec plan",
                     st == 200 and "steps" in plan and plan.get("frame_range"),
                     f"steps={len(plan.get('steps', []))} frame_range={plan.get('frame_range')}"))
st, _ = get("/api/pipeline/exec?scene=S99")
results.append(check("pipeline/exec unknown scene -> 404", st == 404))
# 5. Copyright policy
st, policy = get("/api/copyright/policy")
results.append(check("copyright/policy 200 + verdicts",
                     st == 200 and "CLEAR" in str(policy.get("verdicts", ""))
                     and "BLOCK" in str(policy.get("verdicts", "")),
                     f"rules={len(policy.get('rules', []))}"))

# 6. Copyright check live gate
st, block = post("/api/copyright/check", {"text": "generate the microsoft logo for the promo tile"})
results.append(check("copyright/check BLOCKs protected brand",
                     st == 200 and block.get("verdict") == "BLOCK",
                     f"verdict={block.get('verdict')}"))
st, clear = post("/api/copyright/check", {"text": "use a project-authored SVG silhouette of a phone"})
results.append(check("copyright/check CLEARs project SVG",
                     st == 200 and clear.get("verdict") == "CLEAR",
                     f"verdict={clear.get('verdict')}"))

# 7. Prompt history + trace + trajectory endpoints
st, hist = get("/api/chat/history?limit=3")
results.append(check("chat/history 200 returns list", st == 200 and isinstance(hist.get("history"), list)))
st, trace = get("/api/agent/trace?limit=3")
results.append(check("agent/trace 200 returns list", st == 200 and isinstance(trace.get("trace"), list)))
st, traj = get("/api/agent/trajectory?limit=3")
results.append(check("agent/trajectory 200 returns list", st == 200 and isinstance(traj.get("trajectory"), list)))

# 8. Power state endpoint
st, power = get("/api/power")
results.append(check("power 200 + active scheme",
                     st == 200 and power.get("activeScheme"),
                     f"scheme={power.get('activeScheme')} sleep_ac={power.get('sleep',{}).get('ac')}"))

# 9. Pipeline master map
st, pipe = get("/api/pipeline")
results.append(check("pipeline 200 + scenes", st == 200 and isinstance(pipe, (dict, list))))

passed = sum(1 for r in results if r)
print(f"\n=== {passed}/{len(results)} checks passed ===")
sys.exit(0 if passed == len(results) else 1)
