"""Generate 10 high-quality reference plans for diverse video projects."""
import json
from pathlib import Path

REFERENCE_PLANS = [
    {
        "scenario": "Documentary Short Film",
        "description": "30-min interview-based documentary with B-roll footage",
        "plan": {
            "project": "Documentary Title",
            "phases": [
                {"id": 1, "name": "Pre-Production", "days": 3, "tasks": [
                    {"id": "1.1", "name": "Research & Topic Validation", "depends_on": ["kickoff"],
                     "deliverable": "docs/research.md", "estimate_hrs": 8,
                     "action": "brainstorm", "action_params": {"topic": "documentary subject research"}},
                    {"id": "1.2", "name": "Interview Subject Outreach", "depends_on": ["1.1"],
                     "deliverable": "docs/contacts.md", "estimate_hrs": 4,
                     "action": "brainstorm", "action_params": {"topic": "interview subject identification"}},
                ]},
                {"id": 2, "name": "Production", "days": 5, "tasks": [
                    {"id": "2.1", "name": "Render Interview Scenes", "depends_on": ["1.2"],
                     "deliverable": "renders/video_clips/scene_interview/*.mp4", "estimate_hrs": 12,
                     "action": "render_all_scenes"},
                    {"id": "2.2", "name": "Render B-Roll Scenes", "depends_on": ["2.1"],
                     "deliverable": "renders/video_clips/scene_broll/*.mp4", "estimate_hrs": 8,
                     "action": "render_mp4"},
                ]},
                {"id": 3, "name": "Post-Production", "days": 4, "tasks": [
                    {"id": "3.1", "name": "Assemble Final Cut with Audio", "depends_on": ["2.2"],
                     "deliverable": "renders/final/documentary_final.mp4", "estimate_hrs": 6,
                     "action": "assemble_with_audio"},
                ]},
            ],
            "total_estimate_days": 12,
            "gates": ["4K HOLD"],
            "handoff_ready": True,
        }
    },
    {
        "scenario": "2D Animated Short Film",
        "description": "5-minute hand-drawn style animated short",
        "plan": {
            "project": "Animated Short",
            "phases": [
                {"id": 1, "name": "Animation Production", "days": 7, "tasks": [
                    {"id": "1.1", "name": "Render Character Animation Scenes", "depends_on": ["kickoff"],
                     "deliverable": "renders/video_clips/animation/*.mp4", "estimate_hrs": 24,
                     "action": "render_all_scenes"},
                    {"id": "1.2", "name": "Render Background Plates", "depends_on": ["1.1"],
                     "deliverable": "renders/video_clips/backgrounds/*.mp4", "estimate_hrs": 12,
                     "action": "render_mp4"},
                ]},
                {"id": 2, "name": "Compositing", "days": 3, "tasks": [
                    {"id": "2.1", "name": "Assemble Final Animation", "depends_on": ["1.2"],
                     "deliverable": "renders/final/animation_final.mp4", "estimate_hrs": 8,
                     "action": "assemble_final"},
                ]},
            ],
            "total_estimate_days": 10,
            "gates": ["4K HOLD"],
            "handoff_ready": True,
        }
    },
    {
        "scenario": "3D Animated Commercial",
        "description": "60-second product visualization with photorealistic rendering",
        "plan": {
            "project": "Product Commercial",
            "phases": [
                {"id": 1, "name": "3D Rendering", "days": 5, "tasks": [
                    {"id": "1.1", "name": "Render Product Shots at 1080p", "depends_on": ["kickoff"],
                     "deliverable": "renders/video_clips/product/*.mp4", "estimate_hrs": 18,
                     "action": "render_all_scenes"},
                    {"id": "1.2", "name": "Upscale to 4K", "depends_on": ["1.1"],
                     "deliverable": "renders/video_clips/product_4k/*.mp4", "estimate_hrs": 12,
                     "action": "run_1080_then_4k"},
                ]},
                {"id": 2, "name": "Final Delivery", "days": 2, "tasks": [
                    {"id": "2.1", "name": "Assemble Commercial with Music", "depends_on": ["1.2"],
                     "deliverable": "renders/final/commercial_4k.mp4", "estimate_hrs": 4,
                     "action": "assemble_with_audio"},
                ]},
            ],
            "total_estimate_days": 7,
            "gates": [],
            "handoff_ready": True,
        }
    },
    {
        "scenario": "Music Video with VFX",
        "description": "3-minute music video with visual effects and color grading",
        "plan": {
            "project": "Music Video",
            "phases": [
                {"id": 1, "name": "VFX Production", "days": 6, "tasks": [
                    {"id": "1.1", "name": "Render VFX Scenes", "depends_on": ["kickoff"],
                     "deliverable": "renders/video_clips/vfx/*.mp4", "estimate_hrs": 20,
                     "action": "render_all_scenes"},
                    {"id": "1.2", "name": "Create Kinetic Typography Preview", "depends_on": ["1.1"],
                     "deliverable": "renders/preview/kinetic.mp4", "estimate_hrs": 4,
                     "action": "assemble_kinetic_preview"},
                ]},
                {"id": 2, "name": "Final Assembly", "days": 3, "tasks": [
                    {"id": "2.1", "name": "Assemble Music Video with Audio Track", "depends_on": ["1.2"],
                     "deliverable": "renders/final/music_video.mp4", "estimate_hrs": 6,
                     "action": "assemble_with_audio"},
                ]},
            ],
            "total_estimate_days": 9,
            "gates": ["4K HOLD"],
            "handoff_ready": True,
        }
    },
    {
        "scenario": "Educational Explainer Video",
        "description": "10-minute animated explainer with motion graphics",
        "plan": {
            "project": "Explainer Video",
            "phases": [
                {"id": 1, "name": "Motion Graphics Production", "days": 4, "tasks": [
                    {"id": "1.1", "name": "Render Explainer Scenes", "depends_on": ["kickoff"],
                     "deliverable": "renders/video_clips/explainer/*.mp4", "estimate_hrs": 14,
                     "action": "render_all_scenes"},
                    {"id": "1.2", "name": "Create Kinetic Preview", "depends_on": ["1.1"],
                     "deliverable": "renders/preview/kinetic.mp4", "estimate_hrs": 3,
                     "action": "assemble_kinetic_preview"},
                ]},
                {"id": 2, "name": "Final Delivery", "days": 2, "tasks": [
                    {"id": "2.1", "name": "Assemble Final Explainer", "depends_on": ["1.2"],
                     "deliverable": "renders/final/explainer_final.mp4", "estimate_hrs": 4,
                     "action": "assemble_final"},
                ]},
            ],
            "total_estimate_days": 6,
            "gates": [],
            "handoff_ready": True,
        }
    },
    {
        "scenario": "Kinetic Typography Motion Graphics",
        "description": "2-minute text-based motion graphics piece",
        "plan": {
            "project": "Kinetic Typography",
            "phases": [
                {"id": 1, "name": "Typography Animation", "days": 3, "tasks": [
                    {"id": "1.1", "name": "Render Typography Scenes", "depends_on": ["kickoff"],
                     "deliverable": "renders/video_clips/typography/*.mp4", "estimate_hrs": 10,
                     "action": "render_all_scenes"},
                    {"id": "1.2", "name": "Assemble Kinetic Preview", "depends_on": ["1.1"],
                     "deliverable": "renders/preview/kinetic.mp4", "estimate_hrs": 2,
                     "action": "assemble_kinetic_preview"},
                ]},
                {"id": 2, "name": "Final Output", "days": 1, "tasks": [
                    {"id": "2.1", "name": "Assemble Final with Audio", "depends_on": ["1.2"],
                     "deliverable": "renders/final/kinetic_final.mp4", "estimate_hrs": 3,
                     "action": "assemble_with_audio"},
                ]},
            ],
            "total_estimate_days": 4,
            "gates": [],
            "handoff_ready": True,
        }
    },
    {
        "scenario": "Live-Action Short with Color Grading",
        "description": "15-minute narrative short film with cinematic color grading",
        "plan": {
            "project": "Narrative Short",
            "phases": [
                {"id": 1, "name": "Scene Rendering", "days": 5, "tasks": [
                    {"id": "1.1", "name": "Render All Scenes at 1080p", "depends_on": ["kickoff"],
                     "deliverable": "renders/video_clips/scenes/*.mp4", "estimate_hrs": 16,
                     "action": "render_all_scenes"},
                    {"id": "1.2", "name": "Render 4K Masters", "depends_on": ["1.1"],
                     "deliverable": "renders/video_clips/masters/*.mp4", "estimate_hrs": 12,
                     "action": "render_4k"},
                ]},
                {"id": 2, "name": "Post-Production", "days": 4, "tasks": [
                    {"id": "2.1", "name": "Assemble Final Cut", "depends_on": ["1.2"],
                     "deliverable": "renders/final/short_final.mp4", "estimate_hrs": 8,
                     "action": "assemble_final"},
                ]},
            ],
            "total_estimate_days": 9,
            "gates": ["4K HOLD"],
            "handoff_ready": True,
        }
    },
    {
        "scenario": "VFX-Heavy Sci-Fi Sequence",
        "description": "5-minute sci-fi sequence with complex visual effects",
        "plan": {
            "project": "Sci-Fi Sequence",
            "phases": [
                {"id": 1, "name": "VFX Rendering", "days": 8, "tasks": [
                    {"id": "1.1", "name": "Render VFX Elements", "depends_on": ["kickoff"],
                     "deliverable": "renders/video_clips/vfx/*.mp4", "estimate_hrs": 28,
                     "action": "render_all_scenes"},
                    {"id": "1.2", "name": "Render 4K VFX Masters", "depends_on": ["1.1"],
                     "deliverable": "renders/video_clips/vfx_4k/*.mp4", "estimate_hrs": 20,
                     "action": "run_1080_then_4k"},
                ]},
                {"id": 2, "name": "Compositing & Assembly", "days": 4, "tasks": [
                    {"id": "2.1", "name": "Assemble Final VFX Sequence", "depends_on": ["1.2"],
                     "deliverable": "renders/final/scifi_final.mp4", "estimate_hrs": 10,
                     "action": "assemble_final"},
                ]},
            ],
            "total_estimate_days": 12,
            "gates": [],
            "handoff_ready": True,
        }
    },
    {
        "scenario": "Series Pilot Episode",
        "description": "22-minute pilot episode for animated series",
        "plan": {
            "project": "Series Pilot",
            "phases": [
                {"id": 1, "name": "Episode Production", "days": 10, "tasks": [
                    {"id": "1.1", "name": "Render All Episode Scenes", "depends_on": ["kickoff"],
                     "deliverable": "renders/video_clips/episode/*.mp4", "estimate_hrs": 36,
                     "action": "render_all_scenes"},
                    {"id": "1.2", "name": "Render 4K Masters for Key Scenes", "depends_on": ["1.1"],
                     "deliverable": "renders/video_clips/masters/*.mp4", "estimate_hrs": 24,
                     "action": "render_4k"},
                ]},
                {"id": 2, "name": "Final Assembly", "days": 3, "tasks": [
                    {"id": "2.1", "name": "Assemble Pilot with Audio & Music", "depends_on": ["1.2"],
                     "deliverable": "renders/final/pilot_final.mp4", "estimate_hrs": 8,
                     "action": "assemble_with_audio"},
                ]},
            ],
            "total_estimate_days": 13,
            "gates": ["4K HOLD"],
            "handoff_ready": True,
        }
    },
    {
        "scenario": "Experimental Abstract Video",
        "description": "8-minute abstract visual art piece with generative elements",
        "plan": {
            "project": "Abstract Video",
            "phases": [
                {"id": 1, "name": "Generative Rendering", "days": 5, "tasks": [
                    {"id": "1.1", "name": "Render Abstract Scenes", "depends_on": ["kickoff"],
                     "deliverable": "renders/video_clips/abstract/*.mp4", "estimate_hrs": 18,
                     "action": "render_all_scenes"},
                    {"id": "1.2", "name": "Create Kinetic Preview", "depends_on": ["1.1"],
                     "deliverable": "renders/preview/kinetic.mp4", "estimate_hrs": 3,
                     "action": "assemble_kinetic_preview"},
                ]},
                {"id": 2, "name": "Final Output", "days": 2, "tasks": [
                    {"id": "2.1", "name": "Assemble Final Abstract Piece", "depends_on": ["1.2"],
                     "deliverable": "renders/final/abstract_final.mp4", "estimate_hrs": 4,
                     "action": "assemble_final"},
                ]},
            ],
            "total_estimate_days": 7,
            "gates": [],
            "handoff_ready": True,
        }
    },
]

if __name__ == "__main__":
    out = Path(__file__).parent.parent / "openclaw_ide" / "reference_plans.json"
    with open(out, "w") as f:
        json.dump({"plans": REFERENCE_PLANS}, f, indent=2)
    print(f"Generated {len(REFERENCE_PLANS)} reference plans to {out}")
