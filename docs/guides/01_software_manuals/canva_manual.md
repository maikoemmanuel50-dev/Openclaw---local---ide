---
title: Canva Manual
category: Software Manuals
tags: canva, design, export, infographic, end-card, mcp, composio
source: Composio airw-sasin connection, docs/canva_yellow_ball_brief.md, templates
---

# Canva Manual (graphic design + postcards)

Canva produces the flat/graphic design assets: infographic callouts, stat
cards, end card, and the project's Canva exports for social. Connected through
Composio (`airway-sasin` account).

## Design dimensions

- **Horizontal** 1920x1080 (16:9 video frame).
- Square 1080x1080, vertical 1080x1920 for social/Shorts.

## Export contract (delivery standard)

- **1920x1080 exact at export** — no upscale on Resolve ingest.
- Match the project's fps/format; the master must stay separate and
  uncompressed/high-bitrate; only the final YouTube-spec export is compressed.

## Known templates (Composio / Canva)

- End card logo templates: `DAHSGodJcI0`, `DAHSGtdHqlM`, `DAHSGtmzQSI`.
- Batch PNG exports land in `assets/canva/kinetic/canva_exports/`.

## Workflow via MCP/Composio (in IDE)

1. Render/produce the still or stat visual (Blender or SVG asset).
2. Push rendered stills/infographics into a Canva design (URL asset upload).
3. Edit layout in Canva; apply brand (yellow #FFD54F base, Inter type system).
4. Export 1920x1080 PNG at 100% — then ingest into Resolve for kinetic use.

## Style rules (align with creative bible)

- Soft-but-vivid yellow base; statistic-heavy layouts = readable, one focal idea.
- Typography: Inter heavy for numbers/headlines, Nunito Sans for captions.
- Keep critical content inside title-safe center 80%; content clear of the
  watermark zone top-right.

## Learning resources

- Canva on Miracamp / Motion Array cover lower-thirds and animated graphics;
  see `online_tutorial_library.md` under motion graphics for placement.
- In-app: use the Canva MCP export workflow guide in this IDE (chips: Canva MCP
  Guide) for the `open30` deliverable.