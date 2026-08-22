# Pre-sleep Resolve spot-check — Episode 01

**Time budget:** ~15–25 minutes  
**Timeline:** `Episode 01 - Assembly` · project **Africa Season 1**  
**Fairlight page is open** (MCP already switched you there).

## What you can / cannot sign off tonight

| Can spot-check now | Must re-check after HQ (morning) |
|--------------------|----------------------------------|
| A1 VO + **A2 ducked music** balance | V1 scene plates (new HQ still rendering) |
| V2 yellow ball / V3–V4 kinetic presence | Relinked end card + any V1 frame hits |
| Rough picture: overlays, track layout | Final grade / FINAL export |

Tonight = **audio + editorial layers**. Picture plates refresh after HQ 10/10.

---

## Part A — Fairlight: A2 duck (~10 min)

### A1. Confirm tracks
1. Fairlight page → timeline **Episode 01 - Assembly**.
2. Audio tracks should read roughly:
   - **A1 VO** → `A1_vo_eq.wav` (full episode length)
   - **A2 Music** → `A2_music_eq_ducked.wav` (starts with VO at `01:00:00:00`)
   - A3 Ambient · A4 Punctuation · A5 Stats

### A2. Solo audition (duck proof)
1. Solo **A1 + A2** only (mute A3–A5).
2. Jump to a **dense VO** section (any mid-episode talky stretch).
3. Play 20–30 seconds.
4. **Pass if:** speech is clear; music dips under phrases and comes back between lines (baked sidechain ~−12 dB intent).
5. **Fail if:** music buries VO, or duck pumps harshly — note timecode; morning can re-bake with softer ratio.

### A3. Full bed check (optional 2 min)
1. Unsolo; leave all A1–A5 audible at mix levels.
2. Play same VO section once.
3. **Pass if:** VO still leads; whooshes/SFX don’t drown speech.

### A4. Known gap (don’t block sleep)
- A2 ducked file is **~5:00**; A1 VO is **longer**. Music will go silent near the end of A2’s clip.
- That’s expected with current stem length. Morning: extend/loop music stem or re-render longer bed — **not required tonight**.

### A5. Sign-off box
- [ ] A1+A2 solo: VO readable, music ducks under speech  
- [ ] No obvious clicks/pops at A2 in/out  
- [ ] Noted any ugly timecodes: _______________

---

## Part B — Edit page: picture / layers (~10 min)

1. Switch to **Edit** page (bottom icons).
2. Confirm track layout:
   - **V1** scene plates (current/older — will refresh after HQ)
   - **V2** Ball / yellow ball overlays  
   - **V3 / V4** Kinetic  
   - **V5** TextStat (if used)
3. Scrub these **smoke tests** only (don’t grade):

| Check | Where | Pass |
|-------|--------|------|
| Cold open has picture + overlays | Start `01:00:00:00` | Image + some V2/V3 motion |
| Ball still yellow `#FFD54F` hero | Mid V2 hits | No face / competing mascot |
| Kinetic stills flash briefly | V3/V4 | Short cuts, not 5s stills stuck |
| End card exists | Near end | Plate present (may be old until HQ) |
| No offline media red | Timeline | Clips linked |

4. **Do not** Deliver / export FINAL tonight.  
5. **Do not** start another GPU render.

### Sign-off box
- [ ] V2/V3/V4 look present and intentional  
- [ ] No offline clips  
- [ ] Yellow ball still only hero  

---

## Part C — Before you walk away (2 min)

1. **Save project** (Ctrl+S).
2. Optional: quit Resolve so HQ Blender keeps full GPU (recommended).
3. Confirm PC will **stay awake** overnight.
4. Leave Blender HQ + watcher alone (don’t open master `.blend`).

---

## Morning (after HQ)

1. Confirm `STATUS_HOURLY_LATEST.txt` or 10/10 clips in `renders/video_clips/`.
2. Confirm `finish_after_hq.ps1` ran (new MASTER / Resolve V1 refresh).
3. Re-spot-check **V1** picture quality + end card.
4. Quick re-listen A1+A2 (ducked stem should still be there unless Fairlight script overwrote A2).
5. Then FINAL export / gate toward 4K only when ready.

---

## If duck fails tonight

Re-bake softer (morning OK):

```powershell
cd "C:\Users\HP\OneDrive\The Vault\Africa Season 1"
# restore bak then re-run bake script, or tweak ffmpeg threshold/ratio
python scripts\bake_a2_sidechain_duck.py
```

Guide: `docs/FAIRLIGHT_A2_SIDECHAIN.md`
