# Audio Mix Standards — Africa S1

**Picture refs (mix / storytelling feel, not stem sources):**

- [Bloomberg Originals — The $10 Billion Hunt for the Rocks That Power the World](https://youtu.be/d2dgJGkw5p0)
- [Search Party — Europe's cocaine habit is devastating South America](https://youtu.be/5xm_luvYoc8)

Also keep TED-Ed / Vox clarity from `docs/audio_design_map.yaml`. Delivery loudness: `docs/DELIVERY_STANDARDS.md` (−14 LUFS / ≤ −1 dBTP).

---

## What those docs sound like (targets we bake)

| Device | Rule |
|--------|------|
| **VO first** | Narration is the loudest continuous element. Never fight it with melody or midrange bed. |
| **Felt, not heard beds** | Under speech, music sits ~**18–24 dB** below VO (≈ −24…−30 dBFS bed). Listener should feel pulse/mood, not hum along. |
| **Tension / release** | Build through chapter beds + sparse risers; **release** in VO gaps and after stat hits (music +3…+8 dB for 1–3 s). Flat constant beds = amateur. |
| **Bass discipline** | Soften sub/low-mid under dense VO so speech stays intelligible (documentary “drop the bass under talk”). |
| **Speech-band pocket** | Scoop music ~**1–3 kHz**; leave VO presence intact. |
| **Punctuation** | Short whooshes / risers / stings at section resets only — no wall of SFX. |
| **Stat release** | Impact + soft release hit; music may swell briefly after. |
| **Ambient** | Quiet room/city beds (−26…−30 under VO). Never louder than music bed. |
| **Dynamics** | Duck attack ~15–30 ms, release ~150–250 ms (smooth, no pumping). Gap swell attack/release ~0.4–0.8 s. |

---

## Resolve track map

| Track | Role | Clip volume (start) |
|-------|------|---------------------|
| A1 | VO | 0 dB |
| A2 | Music (ducked + gap swell baked) | ~−24 dB |
| A3 | Ambient | ~−28 dB |
| A4 | Punctuation | ~−18 dB |
| A5 | Stats / release hits | ~−14 dB |

Bake offline (API cannot set Fairlight sidechain graphs):

```powershell
python scripts/bake_a2_tension_release.py
```

Legacy duck-only: `scripts/bake_a2_sidechain_duck.py`  
Stem rebuild: `scripts/resolve_fairlight_overnight.py`

---

## Done when

- VO phrases read clearly on phone speakers.
- Music dips under speech and **breathes up** in pauses / chapter air.
- Chapter beds track mood (dawn → daylight → darkdata → cooltension → hopefuldusk).
- Integrated program ~**−14 LUFS**, true peak ≤ **−1 dBTP** on FINAL export.
