# Fairlight — A2 Sidechain Duck from A1 (Africa S1)

**Goal:** Music / bed on **A2** ducks ~**−18 dB** whenever VO on **A1** speaks, then **swells in VO gaps** (tension/release). Standards: `docs/AUDIO_MIX_STANDARDS.md` · refs [Bloomberg](https://youtu.be/d2dgJGkw5p0) / [Search Party](https://youtu.be/5xm_luvYoc8).

**Project:** Africa Season 1 · timeline **Episode 01 - Assembly**  
**Tracks:** A1 = VO · A2 = music/bed (or next bed stem) · A3–A5 = SFX / ambience as laid by Fairlight overnight script.

---

## MCP / scripting limit (important)

DaVinci Resolve’s public API **cannot** add or configure Fairlight Dynamics/Compressor sidechain graphs, or edit full mix automation curves. The Resolve MCP reports this as unsupported (`plugin_parameter_graphs`, `mix_automation_curves`).

What MCP *can* do: open Fairlight, confirm project/timeline/tracks, list/apply Fairlight presets (none installed here), set some clip volumes when the property is writable.

**Sidechain duck ~−12 dB must be done in the Fairlight UI** (steps above), **or** bake offline:

```powershell
python scripts/bake_a2_tension_release.py
# (legacy duck-only) python scripts/bake_a2_sidechain_duck.py
```

Active bake: `renders/audio_stems/fairlight/A2_music_eq_ducked.wav` → copied to `A2_music_eq.wav` on **A2**. Backup unducked: `A2_music_eq_pre_sidechain.bak.wav`.

---

## Quick path (Resolve Fairlight)

1. Open **DaVinci Resolve** → project **Africa Season 1** → timeline **Episode 01 - Assembly**.
2. Switch to the **Fairlight** page (bottom page icons).
3. Confirm track labels:
   - **A1** = VO (`episode_01_vo.wav` or active stem)
   - **A2** = music / underscore you want to duck
4. Select **A2** (click the track header so A2 is active).
5. Open the **Effects Library** (top-left Effects) → search **Sidechain** or **Compressor**.
6. Prefer one of:
   - **Dynamics** (Fairlight stock) with sidechain enabled, or
   - **Compressor** that exposes an **external / sidechain** key input  
   Drop it onto **A2** (Dynamics strip or clip FX — track FX is cleaner for the whole bed).
7. In the Dynamics / Compressor inspector:
   - Enable **Sidechain** / **External Key** / **SC**.
   - Set the **sidechain source** to **A1** (VO track).
   - **Threshold:** start around **−24 dB** to **−18 dB** (adjust to VO peaks).
   - **Ratio:** **4:1** to **6:1**.
   - **Attack:** **10–30 ms** (fast enough to catch consonants).
   - **Release:** **120–250 ms** (smooth recovery between phrases).
   - **Makeup / Output:** leave near unity; you’re ducking, not boosting.
8. Dial **Range** or makeup so the audible duck is about **−12 dB** when VO is present:
   - Solo A1+A2, play a dense VO section.
   - Watch A2 meter: when VO hits, A2 should drop roughly a stop (~12 dB).
   - If duck is too deep → raise threshold or lower ratio.
   - If music still fights VO → lower threshold or raise ratio slightly.
9. Bypass the plugin once to A/B; leave it on when music sits under VO without mud.

---

## Target numbers (starting preset)

| Parameter | Start here |
|-----------|------------|
| Duck amount | **≈ −12 dB** under VO |
| Threshold | −24 … −18 dB |
| Ratio | 4:1 … 6:1 |
| Attack | 10–30 ms |
| Release | 120–250 ms |
| Knee | Soft (if available) |
| Sidechain source | **A1 only** |

---

## If you don’t see Sidechain

- Use Fairlight **Dynamics** on A2 → enable **Compressor** + look for **Side Chain** / **Key** in the module options.
- Studio builds expose this more reliably than free Resolve; if sidechain is missing:
  1. Keep A2  **−12 to −18 dB** under A1 as a static trim, **or**
  2. Draw a simple **automation** ride on A2: dip ~12 dB under each VO phrase (tedious but works).

---

## After any VO swap

When you replace the stem with `python scripts/swap_vo_stem.py`:

1. Re-check A1 peaks.
2. Re-listen A2 duck depth (new VO loudness may need threshold tweak).
3. Re-export Fairlight mix / FINAL after picture is locked.

---

## Do not

- Sidechain A3–A5 from A1 unless those beds also fight VO (usually leave SFX alone).
- Put the compressor on **A1** (that ducks the VO).
- Start **4K Deliver** while tweaking Fairlight (one heavy GPU job at a time).

---

## Done when

Playing a VO-heavy section: speech is clear, music dips ~12 dB under phrases and recovers between lines without pumping.
