---
title: "Copyright Guardrail & YouTube Policy"
category: "Production Standards"
tags: ["copyright", "guardrail", "youtube", "content-id", "ai-disclosure", "clearance"]
date: 2026-08-15
version: 1.0
---

# Copyright Guardrail & YouTube Policy

Machine-readable guardrail spec for the Africa S1 IDE agent loop. Enforced
by `server.py` (`copyright_check` tool + `/api/copyright/check` endpoint).

## Policy summary (researched, 2026-08-15)

### YouTube / platform rules
- **Content ID** auto-scans uploads against a rights-holder database. Defensive
  credit does NOT clear a claim; claims hit monetization, strikes can terminate
  a channel (3 strikes / 90 days).
- **Fair use** is a legal defense, not a platform feature. Credit alone never
  establishes it; short-excerpt durations have no legal "safe" length.
- **AI content disclosure**: YouTube requires the "Altered or synthetic content"
  flag for realistic synthetic media. Fully AI-generated music is treated as
  high-risk; no Content ID guarantee, possible rejection, keep generation logs.
- **Reused content**: mass-produced / template / repetitive uploads risk
  demonetization under the inauthentic-content policy. Production must add
  original creative value (our graphics/spine do).

### Production clearance workflow
- Clearance is a **pre-production** step: every third-party element (music,
  footage, photos, logos, people) needs a recorded license or release.
- **Music** needs BOTH sync license (composition) AND master use license
  (recording). No random YouTube rips.
- **Talent**: name / voice / likeness are privacy (tort) rights, not copyright —
  obtain releases.
- **Logos / brand marks**: brand-guideline use; prefer generic silhouettes and
  text-only nominative mentions. No official logo packs in hero graphics.

## Machine gate logic (`copyright_check`)

Input: free text (prompt / asset name / clip filename).

1. **Assess** — scan for risky signals:
   - Brand marks: `M-Pesa`, `Safaricom`, `Microsoft`, `Visa`, `UN`, `Netflix`,
     `UNICEF`, `UN Women`, `UNFPA`, `Canva`, `Gabriel`, `Saske`, etc.
   - Words implying reproduction of third-party media: `grab`, `rip`, `scrape`,
     `borrow`, `download` (when paired with media), `clone`, `trace`, `copy`.
   - Music terms without clearance context: `soundtrack`, `song`, `beat`,
     `ripped`, `youtube rip`.
2. **Flag** — return a verdict:
   - `CLEAR` — text uses allowed sources (Mixkit / Unsplash / Poly Haven /
     Blender spine / project SVG).
   - `WARN` — risky signal found but text also names a cleared source or
     generic treatment; agent must use a replacement.
   - `BLOCK` — text requests direct reproduction of a brand mark / official
     logo / licensed track / copyrightable footage without clearance.
3. **Guide** — when BLOCK or WARN, the agent MUST:
   - Prefer generic silhouettes, text labels, or project-authored SVG.
   - Use allowlisted stock (see `COPYRIGHT_CLEARANCE.md` priorities).
   - Never paste official brand logo files into the timeline.
   - Report the violation in the reply: `COPYRIGHT_GUARD: use <replacement>`.

## Scored rules (substring, case-insensitive)

| Category | Signals | Verdict | Replacement guidance |
|----------|---------|---------|----------------------|
| Brand logo | `netflix`, `safaricom logo`, `microsoft logo`, `visa logo`, `un logo` | BLOCK | text-only / `s9_global_icons.svg` / generic glyph |
| Brand name (text) | `m-pesa`, `safaricom`, `microsoft`, `visa`, `unicef`, `unfpa`, `un women` | WARN | nominative text OK in VO/titles; no logo art |
| Media rip | `youtube rip`, `scrape google`, `grab from`, `download mp3`, `steal` | BLOCK | allowlisted stems only |
| Stock reuse | `mixkit`, `unsplash`, `poly haven`, `polhaven` | CLEAR | per `CLEARANCE_ALLOWLIST.json` |
| Generated asset | `generate`, `hyper3d`, `meshy`, `hun yuan`, `process_image` | WARN | keep generation logs; no real-name likenesses |

## Reference docs
- `docs/COPYRIGHT_CLEARANCE.md` (live project clearance policy)
- `docs/CLEARANCE_ALLOWLIST.json` (approved prefixes / tags)
- `docs/CLEARANCE_REPLACEMENTS.md` (trademark-safe replacements)
- YouTube Help: fair use, Content ID, altered/synthetic content disclosure