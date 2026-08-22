---
title: Audio Mix Standards
category: Production Standards
tags: audio, fairlight, lufs, ducking, vo, music, sfx, mix
source: docs/AUDIO_MIX_STANDARDS.md, docs/AUDIO_EXCELLENCE_PACK.md, docs/audio_design_map.yaml, docs/FAIRLIGHT_A2_SIDECHAIN.md
---

# Audio Mix Standards

VO-first documentary mix. Narration is the loudest continuous element; music is
felt, not heard. These numbers unify every episode.

## Delivery targets

- 48 kHz / 24-bit project · AAC-LC 320–384 kbps stereo.
- Loudness **−14 LUFS** integrated · true peak ≤ −1 dBTP.

## Track map (Fairlight)

| Track | Content | Level |
|---|---|---|
| A1 | VO (real voice only) | 0 dB reference |
| A2 | Music | ~ −24 dB under VO; swell −12 dB in transitions |
| A3 | Ambient SFX | ~ −28 dB |
| A4 | Punctuation SFX | ~ −18 dB |
| A5 | Stat impact SFX | ~ −14 dB |

## Mix dynamics

- Music sits ~18–24 dB below VO. Scoop the speech band ~1–3 kHz out of music.
- Duck: A2 sidechain from A1 — amount ~ −12 dB, attack 15–30 ms, release 120–250 ms
  (smooth, no pumping). (Baked chain: ratio 4:1, threshold for ~12 dB duck,
  attack 100 ms, release 400 ms.)
- Pre-reveal dip: −6 dB for 0.5 s before big stat reveals; gap swell attack
  and release 0.4–0.8 s.

## Processing chain (Fairlight, baked in template)

- VO: HPF 80–100 Hz · cut boxiness 250–400 Hz · presence +2.5 dB @ ~3 kHz ·
  air +1 dB @ 7.5 kHz · gentle compression · loudnorm toward −16 LUFS.
- Music: HPF 80 Hz · cut 250 Hz · gentle −1.5 dB @ 4 kHz · loudnorm ~ −22 LUFS.
- Ambient: HPF 120, LPF 6 kHz, soft mid dip · music bed ducked under VO.
- Mix bus: master limiter TP ≤ −1.0 dB. Render template: `FairlightMix_README.md`.

## Rules

- VO is the user's own recorded voice — never substitute AI voice.
- Leveling reference: VO 0 dBFS; never let any stem clip.
- Fairlight A2 sidechain: see `docs/FAIRLIGHT_A2_SIDECHAIN.md` step-by-step.