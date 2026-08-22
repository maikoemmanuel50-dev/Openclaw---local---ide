#!/usr/bin/env python3
"""
Africa S1 — Script-to-Visual Pipeline Generator
Parses episode_1_script.md + teded_scene_spec_ep01.md + audio_design_map.yaml
and generates per-scene visual prompts synced to VO timing.

Usage:
  python generate_visual_pipeline.py                    # generate for episode 1
  python generate_visual_pipeline.py --episode 2        # generate for episode N
  python generate_visual_pipeline.py --dry-run          # preview without writing
"""

import re
import sys
import json
from pathlib import Path
from datetime import datetime

# ── Config ───────────────────────────────────────────────────────────
VAULT = Path(r"C:\Users\HP\OneDrive\The Vault\Africa Season 1")
LOCAL_IDE = Path(r"C:\Users\HP\OneDrive\The Vault\Local ide")
CLEARANCE_FILE = VAULT / "docs" / "CLEARANCE_ALLOWLIST.json"
CLEARANCE_REPLACEMENTS = VAULT / "docs" / "CLEARANCE_REPLACEMENTS.md"
PIPELINE_OUTPUT = LOCAL_IDE / "pipeline"
PROMPTS_OUTPUT = PIPELINE_OUTPUT / "prompts"
SCENES_OUTPUT = PIPELINE_OUTPUT / "scenes"

# ── Scene definitions (from teded_scene_spec_ep01.md) ────────────────
SCENES = {
    "S01": {
        "name": "Cold Open",
        "chapter": "Dawn",
        "camera": "Push-In",
        "duration_sec": 50,
        "frames": 1200,
        "style": "Hook + abstract overlay",
        "composition_bg": "Dawn gradient sky (warm orange-purple)",
        "composition_mid": "CBD tower silhouettes (UAP Tower, Times Tower)",
        "composition_fg": "Matatu + motorbike silhouettes",
        "composition_overlay": "Digital transaction paths",
        "composition_ui": "Nairobi location label + Silicon Savannah title",
        "animation_triggers": [
            {"word": "Nairobi", "element": "Location label", "anim": "Fade in + slide up", "frames": "72-80"},
            {"word": "matatus", "element": "Matatu silhouettes", "anim": "Subtle bounce 2px Y", "frames": "180-200"},
            {"word": "pockets", "element": "Transaction paths overlay", "anim": "Fade in 0->0.7 opacity, paths animate L->R", "frames": "360-480"},
            {"word": "money has already moved", "element": "Path pulse", "anim": "Glow pulse on path nodes", "frames": "540-600"},
            {"word": "phone", "element": "Path convergence", "anim": "Lines converge to phone icon", "frames": "720-780"},
            {"word": "Silicon Savannah", "element": "Subtitle label", "anim": "Fade in below Nairobi", "frames": "1140-1200"},
        ],
        "sfx": [
            {"word": "matatus", "sfx": "matatu_horn.wav", "db": -18},
            {"word": "money has already moved", "sfx": "transaction_chime.wav", "db": -18},
            {"word": "scene_start", "sfx": "city_morning_ambient.wav", "db": -24, "continuous": True},
        ],
        "music": "ch01_dawn_pad.wav",
        "text": [
            {"string": "Nairobi", "style": "Label 36px", "timing_sec": 3},
            {"string": "Silicon Savannah", "style": "Headline 72px", "timing_sec": 47},
        ],
        "transition_out": {"type": "cut", "on_word": "Silicon Savannah"},
        "assets": {
            "existing": ["assets/canva/s1_dawn_skyline.png", "assets/canva/s1_matatu_silhouettes.png"],
            "new": ["assets/diagrams/s1_digital_paths.svg"],
        },
    },
    "S02": {
        "name": "Context 2007",
        "chapter": "Dawn",
        "camera": "Pan L->R",
        "duration_sec": 45,
        "frames": 1080,
        "style": "Historical flashback + diagram",
        "composition_bg": "Warm retro yellow gradient",
        "composition_mid": "Phone kiosk illustration",
        "composition_fg": "Nokia handsets on display",
        "composition_overlay": "M-Pesa flow diagram",
        "composition_ui": "2007 year label + M-PESA title card",
        "animation_triggers": [
            {"word": "2007", "element": "Year label", "anim": "Slam in scale 1.2->1.0", "frames": "60-72"},
            {"word": "M-Pesa", "element": "Title card M-PESA", "anim": "Fade in center-top", "frames": "120-140"},
            {"word": "no bank account", "element": "Flow step 1 phone icon", "anim": "Slide in from left", "frames": "300-320"},
            {"word": "bank branches", "element": "Flow step 2 agent icon", "anim": "Slide in", "frames": "480-500"},
            {"word": "text message", "element": "Flow step 3 recipient icon", "anim": "Slide in", "frames": "660-680"},
            {"word": "blueprint", "element": "Connector arrows", "anim": "Draw-on animation", "frames": "960-1000"},
        ],
        "sfx": [
            {"word": "M-Pesa", "sfx": "brand_sting.wav"},
            {"word": "text message", "sfx": "keypad_click.wav"},
            {"word": "scene", "sfx": "street_bustle.wav", "db": -24, "continuous": True},
        ],
        "music": "ch01_dawn_pad.wav",
        "text": [
            {"string": "2007", "style": "Stat 96px", "timing_sec": 2.5},
            {"string": "M-PESA", "style": "Headline 72px", "timing_sec": 5},
            {"string": "Phone -> Agent -> Recipient", "style": "Label 36px staggered", "timing_sec": "12-22"},
        ],
        "transition_out": {"type": "slide_wipe", "on_word": "blueprint", "direction": "right", "frames": 8},
        "assets": {
            "existing": ["assets/canva/s2_kiosk_2007.png"],
            "new": ["assets/diagrams/s2_mpesa_flow.svg", "assets/icons/icon_phone.svg", "assets/icons/icon_agent.svg"],
        },
    },
    "S03": {
        "name": "Beat 1: The Hubs",
        "chapter": "Daylight",
        "camera": "Parallax Drift L->R",
        "duration_sec": 45,
        "frames": 1080,
        "style": "3-factor enumeration",
        "composition_bg": "Co-working interior",
        "composition_mid": "Desks, laptops, whiteboards",
        "composition_fg": "Plants, foreground desk edge",
        "composition_overlay": "Hub cards",
        "composition_ui": "Card labels (iHub, Andela, NaiLab)",
        "animation_triggers": [
            {"word": "iHub", "element": "Card 1 iHub 2010", "anim": "Stagger slide-in delay 0", "frames": "240-260"},
            {"word": "Andela", "element": "Card 2 Andela", "anim": "Stagger slide-in delay 12f", "frames": "540-560"},
            {"word": "NaiLab", "element": "Card 3 NaiLab", "anim": "Stagger slide-in delay 24f", "frames": "720-740"},
            {"word": "desks", "element": "Laptop screens", "anim": "Screen flicker loop", "frames": "continuous"},
            {"word": "whiteboards", "element": "Whiteboard lines", "anim": "Draw-on", "frames": "400-480"},
        ],
        "sfx": [
            {"word": "scene", "sfx": "coworking_chatter.wav", "db": -24, "continuous": True},
            {"word": "desks", "sfx": "keyboard_clack.wav", "db": -20},
        ],
        "music": "ch02_daylight_lofi.wav",
        "text": [
            {"string": "iHub 2010", "style": "Label 36px", "timing_sec": 10},
            {"string": "Andela", "style": "Label 36px", "timing_sec": 22},
            {"string": "NaiLab", "style": "Label 36px", "timing_sec": 30},
        ],
        "transition_out": {"type": "color_hold", "to_scene": "S04"},
        "assets": {
            "existing": ["assets/canva/s3_coworking.png"],
            "new": ["assets/diagrams/s3_hub_cards.svg"],
        },
    },
    "S04": {
        "name": "Beat 1: Phone Close-Up",
        "chapter": "Daylight",
        "camera": "Push-In tight",
        "duration_sec": 25,
        "frames": 600,
        "style": "Close-up detail + concept label",
        "composition_bg": "Soft blur",
        "composition_mid": "Hand + phone close-up",
        "composition_overlay": "UI highlight boxes",
        "composition_ui": "Mobile-First label",
        "animation_triggers": [
            {"word": "phone", "element": "Phone screen", "anim": "UI scroll micro-animation thumb drag", "frames": "60-300"},
            {"word": "small screen", "element": "UI highlight boxes", "anim": "Box draw-on around app elements", "frames": "180-240"},
            {"word": "Mobile-First", "element": "Label", "anim": "Fade in + slide up", "frames": "360-380"},
        ],
        "sfx": [
            {"word": "phone", "sfx": "ui_swipe.wav"},
        ],
        "music": "ch02_daylight_lofi.wav",
        "text": [
            {"string": "Mobile-First", "style": "Headline 72px", "timing_sec": 15},
        ],
        "transition_out": {"type": "cut", "to_scene": "S05"},
        "assets": {
            "existing": ["assets/canva/s4_phone_hand.png"],
            "new": [],
        },
    },
    "S05": {
        "name": "Beat 2: The Money",
        "chapter": "DarkData",
        "camera": "Push-In",
        "duration_sec": 45,
        "frames": 1080,
        "style": "Data viz + animated bars + stat counter",
        "composition_bg": "Dark charcoal #1A1A2E",
        "composition_mid": "Geometry Nodes bar chart (4 sectors)",
        "composition_overlay": "Sector labels, stat callouts",
        "composition_ui": "$984M counter + 82% glow",
        "animation_triggers": [
            {"word": "measurable", "element": "Chart frame", "anim": "Fade in chart outline", "frames": "60-80"},
            {"word": "a billion dollars", "element": "$984M counter", "anim": "Count up 0->984", "frames": "180-240"},
            {"word": "Fintech", "element": "Fintech bar + label", "anim": "Bar rises label fades in", "frames": "360-400"},
            {"word": "Climate/Energy", "element": "Climate bar + label", "anim": "Bar rises tallest neon glow", "frames": "540-600"},
            {"word": "eighty-two percent", "element": "82% callout", "anim": "Slam in center pulse glow", "frames": "780-840"},
            {"word": "E-commerce Logistics", "element": "Remaining bars", "anim": "Rise sequentially", "frames": "420-520"},
        ],
        "sfx": [
            {"word": "bar growth", "sfx": "chart_riser.wav"},
            {"word": "$984M", "sfx": "stat_ping.wav"},
            {"word": "eighty-two percent", "sfx": "stat_impact.wav"},
        ],
        "music": "ch03_darkdata_electronic.wav",
        "text": [
            {"string": "$984M", "style": "Stat 96px neon green", "timing_sec": 7.5},
            {"string": "Fintech", "style": "Label 36px", "timing_sec": 15},
            {"string": "Climate/Energy", "style": "Label 36px", "timing_sec": 22},
            {"string": "82%", "style": "Stat 96px accent", "timing_sec": 32},
        ],
        "transition_out": {"type": "morph", "on_trigger": "Climate bar morphs to solar panel silhouette", "frames": 15},
        "assets": {
            "existing": ["blend/africa_s1_master_v01.blend Scene 05"],
            "new": ["Blender text objects / Resolve overlay for sector labels"],
        },
    },
    "S06": {
        "name": "Beat 2: Solar",
        "chapter": "DarkData",
        "camera": "Parallax Drift",
        "duration_sec": 40,
        "frames": 960,
        "style": "Supporting example after data",
        "composition_bg": "Leafy suburb",
        "composition_mid": "Rooftop + solar panels procedural",
        "composition_fg": "Solar glare overlay",
        "composition_ui": "Company tags + Pay-As-You-Go Solar label",
        "animation_triggers": [
            {"word": "d.light Sun King", "element": "Company tags", "anim": "Stagger fade-in", "frames": "120-200"},
            {"word": "solar panels", "element": "Panel array", "anim": "Glare sweep L->R", "frames": "300-420"},
            {"word": "daily payment", "element": "Payment flow icon", "anim": "Coin stack build", "frames": "540-660"},
            {"word": "M-Pesa instinct", "element": "Callback connector", "anim": "Draw-on arrow from S02 flow", "frames": "780-840"},
        ],
        "sfx": [
            {"word": "scene", "sfx": "solar_hum.wav", "db": -24, "continuous": True},
            {"word": "solar panels", "sfx": "glare_sweep.wav", "db": -20},
        ],
        "music": "ch03_darkdata_electronic.wav",
        "text": [
            {"string": "Pay-As-You-Go Solar", "style": "Headline 72px", "timing_sec": 22},
        ],
        "transition_out": {"type": "fade_to_black", "frames": 24},
        "assets": {
            "existing": [],
            "new": ["assets/diagrams/s6_solar_flow.svg"],
        },
    },
    "S07": {
        "name": "Beat 3: The Gap",
        "chapter": "CoolTension",
        "camera": "Custom zoom-out",
        "duration_sec": 50,
        "frames": 1200,
        "style": "Map reveal + stat slam",
        "composition_bg": "High-contrast Kenya map dark muted",
        "composition_mid": "Nairobi glowing beacon pulsing",
        "composition_overlay": "Dim markers Mombasa Kisumu Eldoret Nakuru",
        "composition_ui": "97% stat callout",
        "animation_triggers": [
            {"word": "Nairobi", "element": "Beacon pulse", "anim": "Glow pulse intensity cycle", "frames": "60-300"},
            {"word": "Mombasa Kisumu", "element": "Dim city markers", "anim": "Sequential fade-in muted", "frames": "360-540"},
            {"word": "ninety-seven percent", "element": "97% callout", "anim": "Slam in + hold 36f", "frames": "720-780"},
            {"word": "funding", "element": "Funding trail lines", "anim": "Draw-on from Nairobi to cities", "frames": "900-1080"},
        ],
        "sfx": [
            {"word": "scene", "sfx": "drone_ambient.wav", "db": -26, "continuous": True},
            {"word": "ninety-seven percent", "sfx": "stat_impact.wav", "db": -14},
        ],
        "music": "ch04_cooltension_drone.wav",
        "text": [
            {"string": "97%", "style": "Stat 96px", "timing_sec": 30},
        ],
        "transition_out": {"type": "parallax_drift", "to_scene": "S08"},
        "assets": {
            "existing": [],
            "new": ["assets/maps/kenya_map_hi_contrast.svg"],
        },
    },
    "S08": {
        "name": "Beat 3: Secondary City",
        "chapter": "CoolTension",
        "camera": "Parallax Drift",
        "duration_sec": 35,
        "frames": 840,
        "style": "Contrast / quiet beat",
        "composition_bg": "Dusty regional town street (Mombasa/Kisumu style)",
        "composition_mid": "Small shop, cyclist passing by",
        "composition_fg": "Dust particles ambient",
        "composition_ui": "City name labels muted",
        "animation_triggers": [
            {"word": "founders", "element": "Shopkeeper figure", "anim": "Subtle idle motion", "frames": "120-300"},
            {"word": "infrastructure", "element": "Road/path overlay", "anim": "Draw-on dashed lines", "frames": "420-600"},
        ],
        "sfx": [
            {"word": "scene", "sfx": "drone_ambient.wav", "db": -26, "continuous": True},
            {"word": "founders", "sfx": "ambient_street.wav", "db": -28},
        ],
        "music": "ch04_cooltension_drone.wav",
        "text": [],
        "transition_out": {"type": "cut", "to_scene": "S09"},
        "assets": {
            "existing": [],
            "new": ["assets/canva/s8_regional_town.png"],
        },
    },
    "S09": {
        "name": "Closer",
        "chapter": "HopefulDusk",
        "camera": "Push-In ending wide hold",
        "duration_sec": 70,
        "frames": 1680,
        "style": "Optimistic turn + icons",
        "composition_bg": "Modern Nairobi dusk deep blue-gold sky",
        "composition_mid": "Glass facades reflecting sky",
        "composition_overlay": "Global logo icons Microsoft Visa stylized non-trademarked",
        "composition_ui": "UN agencies text overlay",
        "animation_triggers": [
            {"word": "Microsoft", "element": "Microsoft-style icon", "anim": "Fade in + settle", "frames": "180-240"},
            {"word": "Visa", "element": "Visa-style icon", "anim": "Fade in + settle", "frames": "360-420"},
            {"word": "United Nations", "element": "UN text overlay", "anim": "Typewriter reveal", "frames": "600-780"},
            {"word": "forecast", "element": "Series tagline", "anim": "Fade in wide hold", "frames": "1500-1680"},
        ],
        "sfx": [
            {"word": "scene", "sfx": "warm_swell.wav", "db": -20},
        ],
        "music": "ch05_hopeful_dusk.wav",
        "text": [
            {"string": "Lagos", "style": "Label 36px", "timing_sec": 55},
            {"string": "Kigali", "style": "Label 36px", "timing_sec": 58},
            {"string": "Accra", "style": "Label 36px", "timing_sec": 61},
        ],
        "transition_out": {"type": "fade_to_black", "frames": 30},
        "assets": {
            "existing": [],
            "new": ["assets/icons/icon_microsoft.svg", "assets/icons/icon_visa.svg", "assets/diagrams/s9_global_icons.svg"],
        },
    },
    "S10": {
        "name": "End Card",
        "chapter": "HopefulDusk",
        "camera": "Static wide",
        "duration_sec": 15,
        "frames": 360,
        "style": "Series card",
        "composition_bg": "Dark textured background",
        "composition_mid": "AFRICA series logo",
        "composition_overlay": "Subtle parallax drift",
        "composition_ui": "None",
        "animation_triggers": [
            {"word": "scene_start", "element": "AFRICA logo", "anim": "Fade in + subtle drift", "frames": "0-120"},
        ],
        "sfx": [
            {"word": "scene", "sfx": "music_resolve.wav", "db": -12},
        ],
        "music": "ch05_hopeful_dusk.wav",
        "text": [
            {"string": "AFRICA", "style": "Logo 120px", "timing_sec": 2},
        ],
        "transition_out": {"type": "fade_to_black", "frames": 60},
        "assets": {
            "existing": [],
            "new": [],
        },
    },
}

# ── Chapter frame ranges (from audio_design_map.yaml section_resets) ──
CHAPTER_FRAMES = [
    {"frame": 0, "name": "Cold Open", "music": "dawn"},
    {"frame": 1080, "name": "Context 2007", "music": "dawn"},
    {"frame": 2040, "name": "Beat 1 Hubs", "music": "daylight"},
    {"frame": 3720, "name": "Beat 2 Money", "music": "darkdata"},
    {"frame": 5400, "name": "Beat 3 Gap", "music": "cooltension"},
    {"frame": 6840, "name": "Closer", "music": "hopefuldusk"},
    {"frame": 8280, "name": "End Card", "music": "hopefuldusk"},
]


def load_clearance_allowlist():
    """Load the copyright clearance allowlist."""
    if CLEARANCE_FILE.exists():
        with open(CLEARANCE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"approved_sources": [], "blocked": []}


def scene_id_to_frame_range(scene_id):
    """Convert scene ID to (start_frame, end_frame) based on scene durations."""
    idx = int(scene_id.replace("S", ""))
    # Calculate from scene durations (more accurate than chapter resets)
    start = 0
    for i in range(1, idx):
        sid = f"S{i:02d}"
        if sid in SCENES:
            start += SCENES[sid]["duration_sec"] * 24
    duration = SCENES[scene_id]["duration_sec"] * 24
    return start, start + duration


# Render contract constants shared by every generated scene script.
RENDER_CONTRACT = {
    "engine": "CYCLES",
    "resolution": [1920, 1080],
    "fps": 24,
    "samples": 64,
    "device": "GPU",
    "output_root": "C:/Users/HP/OneDrive/The Vault/Africa Season 1/renders/video_clips/masters",
    "naming": "frame_%04d.png",
}

# Scene ID -> canonical render folder name (matches the live creates dirs).
SCENE_FOLDERS = {
    "S01": "01_ColdOpen",
    "S02": "02_Context2007",
    "S03": "03_Beat1_Hubs",
    "S04": "04_Beat1_Phone",
    "S05": "05_Beat2_Money",
    "S06": "06_Beat2_Solar",
    "S07": "07_Beat3_Gap",
    "S08": "08_Beat3_SecondaryCity",
    "S09": "09_Closer",
    "S10": "10_EndCard",
}


def canonical_folder(scene_id):
    """Return the canonical render-folder name for a scene ID."""
    return SCENE_FOLDERS.get(scene_id, scene_id)


def parse_frames(frames):
    """Parse '72-80' / '360-480' / 'continuous' trigger frames into (start, end) or None."""
    if not frames or frames == "continuous":
        return None
    try:
        a, _, b = str(frames).partition("-")
        s, e = int(a), int(b)
        return (s, e)
    except Exception:
        return None


def generate_blender_exec_spec(scene_id, scene):
    """Build a machine-executable Blender plan for the scene.

    Returns a structured plan (list of ordered steps) that an agent feeding
    the Blender MCP can execute top-to-bottom: import each asset as a plane at
    its Z layer, place a camera with the scene's motion, keyframe the VO-synced
    triggers on their frame ranges, then configure Cyclest rendering to the
    contract output path."""
    start_f, end_f = scene_id_to_frame_range(scene_id)
    duration_f = end_f - start_f

    # Map composition layers -> Z positions on the camera-facing stack.
    # Plane spans ~ (x: -1.6..1.6, y: -0.9..0.9) at z given; camera looks down -Z.
    z_depth = {"bg": -2, "mid": -1, "fg": 0, "overlay": 1, "ui": 2}
    steps = []
    ordered = ["bg", "mid", "fg", "overlay", "ui"]
    for key in ordered:
        content = (scene.get(f"composition_{key}") or "").strip()
        if not content:
            continue
        z = z_depth.get(key, 0)
        steps.append({
            "op": "import_plane",
            "layer": key,
            "z": z,
            "content": content,
            "notes": f"Layer {key.upper()} at Z={z:+d}: {content}",
        })

    # Existing/new assets attach to the first layer they describe; new SVG
    # assets require a Blender Grease Pencil / curve trace, so flag as create.
    assets = scene.get("assets", {})
    for a in assets.get("existing", []):
        steps.append({
            "op": "texture_plane",
            "asset": a,
            "mode": "existing_image",
            "path": f"C:/Users/HP/OneDrive/The Vault/Africa Season 1/{a}",
            "exists": True,
        })
    for a in assets.get("new", []):
        steps.append({
            "op": "texture_plane",
            "asset": a,
            "mode": "new_generate",
            "path": f"C:/Users/HP/OneDrive/The Vault/Africa Season 1/{a}",
            "exists": False,
        })

    # Camera: place at (0, -7, 2.2) looking at origin; scene camera motion maps
    # to a keyframe-able path (push-in / pan / parallax).
    motion = scene.get("camera", "Static")
    steps.append({
        "op": "camera",
        "motion": motion,
        "frame_range": [start_f, end_f],
        "duration_sec": scene.get("duration_sec", 45),
        "fov": 45,
    })

    # VO-synced element animations -> keyframe steps with absolute target frames.
    for trig in scene.get("animation_triggers", []):
        fr = parse_frames(trig.get("frames"))
        steps.append({
            "op": "animate",
            "element": trig.get("element", ""),
            "anim": trig.get("anim", ""),
            "trigger_word": trig.get("word", ""),
            "frames": {"absolute": fr, "raw": trig.get("frames")},
            "keyframe": {"start": fr[0] if fr else start_f, "end": fr[1] if fr else end_f},
        })

    # On-screen text -> Text objects (kept generic; Fusion overlays handle the final)
    for t in scene.get("text", []):
        steps.append({
            "op": "text_object",
            "string": t.get("string", ""),
            "style": t.get("style", ""),
            "timing_sec": t.get("timing_sec"),
            "timing_frame": (t["timing_sec"] * 24) if isinstance(t.get("timing_sec"), (int, float)) else None,
        })

    # Render step.
    steps.append({
        "op": "render",
        "contract": RENDER_CONTRACT,
        "output": f"{RENDER_CONTRACT['output_root']}/{canonical_folder(scene_id)}/frame_%04d.png",
        "frame_start": start_f,
        "frame_end": end_f,
    })

    return {
        "scene": scene_id,
        "name": scene["name"],
        "frame_range": [start_f, end_f],
        "fps": 24,
        "steps": steps,
    }


def generate_blender_prompt(scene_id, scene):
    """Generate a Blender-ready visual prompt for a scene."""
    start_f, end_f = scene_id_to_frame_range(scene_id)
    duration_f = end_f - start_f

    layers = []
    for z, layer_key in enumerate(["composition_bg", "composition_mid", "composition_fg", "composition_overlay", "composition_ui"]):
        content = scene.get(layer_key, "")
        if content:
            label = layer_key.replace("composition_", "").upper()
            layers.append(f"  Z={z-2:+d} [{label}]: {content}")

    animation_notes = []
    for trig in scene.get("animation_triggers", []):
        animation_notes.append(
            f'  VO word "{trig["word"]}" -> {trig["element"]}: {trig["anim"]} (frames {trig["frames"]})'
        )

    text_notes = []
    for t in scene.get("text", []):
        text_notes.append(f'  "{t["string"]}" [{t["style"]}] at {t["timing_sec"]}s')

    asset_notes = []
    for a in scene.get("assets", {}).get("existing", []):
        asset_notes.append(f"  [EXISTS] {a}")
    for a in scene.get("assets", {}).get("new", []):
        asset_notes.append(f"  [CREATE] {a}")

    prompt = f"""# Blender Visual Prompt — {scene_id}: {scene['name']}
# Chapter: {scene['chapter']} | Camera: {scene['camera']}
# Duration: {scene['duration_sec']}s ({duration_f} frames @ 24fps)
# Frame range: {start_f}–{end_f}
# Style: {scene['style']}

## COMPOSITION (Layer Stack)
{chr(10).join(layers) if layers else '  (none defined)'}

## CAMERA MOTION
- Type: {scene['camera']}
- Duration: {scene['duration_sec']}s
- Frame range: {start_f}–{end_f}

## ELEMENT ANIMATIONS (VO-synced triggers)
{chr(10).join(animation_notes) if animation_notes else '  (none defined)'}

## ON-SCREEN TEXT
{chr(10).join(text_notes) if text_notes else '  (none defined)'}

## ASSETS REQUIRED
{chr(10).join(asset_notes) if asset_notes else '  (none defined)'}

## SFX TRIGGERS
{chr(10).join(f'  "{s.get("word", "?")}" -> {s["sfx"]} ({s.get("db", "?")} dB)' for s in scene.get("sfx", [])) if scene.get("sfx") else '  (none)'}

## MUSIC
- Bed: {scene.get('music', 'TBD')}

## TRANSITION OUT
- Type: {scene.get('transition_out', {}).get('type', 'cut')}
"""
    return prompt


def generate_resolve_overlay_prompt(scene_id, scene):
    """Generate Resolve/Fusion overlay specs for text and stat callouts."""
    overlays = []
    for t in scene.get("text", []):
        timing_f = t["timing_sec"] * 24 if isinstance(t["timing_sec"], (int, float)) else "TBD"
        overlays.append({
            "scene": scene_id,
            "text": t["string"],
            "style": t["style"],
            "timing_sec": t["timing_sec"],
            "timing_frame": timing_f,
            "template": "TextStat" if "$" in t["string"] or "%" in t["string"] else "TextBasic",
        })
    return overlays


def generate_copyright_gate(scene_id, scene):
    """Check assets against clearance allowlist and flag new needs.

    The CLEARANCE_ALLOWLIST.json uses:
      - allow_graded_hq_prefixes: filename prefixes cleared for reuse
      - allow_mixkit_tags: Mixkit stock tags (CC0)
      - allow_unsplash_pan_tags: Unsplash pan tags (CC0)
      - exclude_substrings: blocked filename substrings
      - forbid_exact: exact filenames blocked
      - replacement_map: blocked -> replacement mappings
    """
    clearance = load_clearance_allowlist()

    prefixes = [p.lower() for p in clearance.get("allow_graded_hq_prefixes", [])]
    mixkit_tags = [t.lower() for t in clearance.get("allow_mixkit_tags", [])]
    unsplash_tags = [t.lower() for t in clearance.get("allow_unsplash_pan_tags", [])]
    exclude = [e.lower() for e in clearance.get("exclude_substrings", [])]
    forbid_exact = [f.lower() for f in clearance.get("forbid_exact", [])]

    needs = []
    for asset_type in ["existing", "new"]:
        for asset in scene.get("assets", {}).get(asset_type, []):
            filename = asset.split("/")[-1].lower()
            basename = filename.rsplit(".", 1)[0] if "." in filename else filename

            # Check exact forbid
            if filename in forbid_exact:
                replacement = clearance.get("replacement_map", {}).get(asset.split("/")[-1], "UNKNOWN")
                needs.append({"asset": asset, "type": asset_type, "status": "BLOCKED", "replacement": replacement})
                continue

            # Check exclude substrings
            if any(ex in filename for ex in exclude):
                needs.append({"asset": asset, "type": asset_type, "status": "BLOCKED"})
                continue

            # Check prefix match
            if any(basename.startswith(p) or filename.startswith(p) for p in prefixes):
                needs.append({"asset": asset, "type": asset_type, "status": "APPROVED"})
                continue

            # Check Mixkit/Unsplash tag matches
            if any(t in basename for t in mixkit_tags + unsplash_tags):
                needs.append({"asset": asset, "type": asset_type, "status": "APPROVED"})
                continue

            # Default: needs clearance or is a new creation
            needs.append({"asset": asset, "type": asset_type, "status": "NEEDS_CLEARANCE"})

    return {
        "scene": scene_id,
        "assets": needs,
        "has_new_creations": any(n["type"] == "new" for n in needs),
    }


def generate_pipeline(episode=1, dry_run=False):
    """Generate the full visual pipeline for an episode."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_frames = sum(s["duration_sec"] * 24 for s in SCENES.values())
    pipeline = {
        "episode": episode,
        "title": "Silicon Savannah" if episode == 1 else f"Episode {episode}",
        "generated_at": timestamp,
        "fps": 24,
        "total_frames": total_frames,
        "total_duration_sec": total_frames // 24,
        "scenes": [],
    }

    all_overlays = []

    for scene_id, scene in SCENES.items():
        start_f, end_f = scene_id_to_frame_range(scene_id)
        scene_data = {
            "id": scene_id,
            "name": scene["name"],
            "chapter": scene["chapter"],
            "camera": scene["camera"],
            "frame_range": [start_f, end_f],
            "duration_sec": scene["duration_sec"],
            "frames": end_f - start_f,
            "blender_prompt": f"pipeline/prompts/{scene_id}_blender.py",
            "blender_exec": f"pipeline/exec/{scene_id}_exec.json",
            "render_folder": canonical_folder(scene_id),
            "resolve_overlays": f"pipeline/scenes/{scene_id}_resolve_overlays.json",
            "copyright_gate": generate_copyright_gate(scene_id, scene),
        }
        pipeline["scenes"].append(scene_data)
        all_overlays.extend(generate_resolve_overlay_prompt(scene_id, scene))

    if dry_run:
        print(json.dumps(pipeline, indent=2))
        print(f"\n--- Would generate {len(SCENES)} scene prompts + {len(all_overlays)} Resolve overlays ---")
        return pipeline

    # Write outputs
    PIPELINE_OUTPUT.mkdir(parents=True, exist_ok=True)
    PROMPTS_OUTPUT.mkdir(parents=True, exist_ok=True)
    SCENES_OUTPUT.mkdir(parents=True, exist_ok=True)
    EXEC_OUTPUT = PIPELINE_OUTPUT / "exec"
    EXEC_OUTPUT.mkdir(parents=True, exist_ok=True)

    # Master pipeline JSON
    pipeline_path = PIPELINE_OUTPUT / f"episode_{episode}_pipeline.json"
    with open(pipeline_path, "w", encoding="utf-8") as f:
        json.dump(pipeline, f, indent=2)
    print(f"[OK] Pipeline map: {pipeline_path}")

    # Per-scene Blender prompts
    for scene_id, scene in SCENES.items():
        prompt = generate_blender_prompt(scene_id, scene)
        prompt_path = PROMPTS_OUTPUT / f"{scene_id}_blender.py"
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"[OK] Blender prompt: {prompt_path}")

        # Machine-executable Blender plan (for the Blender MCP agent)
        exec_spec = generate_blender_exec_spec(scene_id, scene)
        exec_path = EXEC_OUTPUT / f"{scene_id}_exec.json"
        with open(exec_path, "w", encoding="utf-8") as f:
            json.dump(exec_spec, f, indent=2)
        print(f"[OK] Blender exec plan: {exec_path}")

    # Resolve overlays
    overlays_path = SCENES_OUTPUT / "resolve_overlays_all.json"
    with open(overlays_path, "w", encoding="utf-8") as f:
        json.dump(all_overlays, f, indent=2)
    print(f"[OK] Resolve overlays: {overlays_path}")

    # Copyright gate summary
    gate_summary = {"scenes": [], "total_new_assets": 0, "needs_clearance": 0}
    for scene_data in pipeline["scenes"]:
        gate = scene_data["copyright_gate"]
        gate_summary["scenes"].append({
            "id": scene_data["id"],
            "name": scene_data["name"],
            "assets": gate["assets"],
        })
        gate_summary["total_new_assets"] += sum(1 for a in gate["assets"] if a["type"] == "new")
        gate_summary["needs_clearance"] += sum(1 for a in gate["assets"] if a["status"] == "NEEDS_CLEARANCE")

    gate_path = PIPELINE_OUTPUT / "copyright_gate_summary.json"
    with open(gate_path, "w", encoding="utf-8") as f:
        json.dump(gate_summary, f, indent=2)
    print(f"[OK] Copyright gate: {gate_path}")

    print(f"\n{'='*60}")
    print(f"PIPELINE GENERATED — Episode {episode}: {pipeline['title']}")
    print(f"  {len(SCENES)} scenes mapped")
    print(f"  {len(all_overlays)} Resolve text overlays defined")
    print(f"  {len(SCENES)} machine-executable Blender plans (pipeline/exec/)")
    print(f"  {gate_summary['total_new_assets']} new assets to create")
    print(f"  {gate_summary['needs_clearance']} assets needing copyright clearance")
    print(f"{'='*60}")

    return pipeline


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Africa S1 Visual Pipeline Generator")
    parser.add_argument("--episode", type=int, default=1, help="Episode number")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    args = parser.parse_args()
    generate_pipeline(episode=args.episode, dry_run=args.dry_run)
