---
abstract: "L07 HOST-ONLY: DEAM receipt.json vs SELECTION_GATE. 2015 n=58 r_rms=0.373 R²_energy=0.296. Arousal is criterion-3 evidence, not Gate A PASS. No playback."
---

# L07 — DEAM arousal receipt vs SELECTION_GATE

HARD_FAIL: `SAME_SONG_LOOP_MAX_15MIN`. Same song/clip in the room >15 min → kill the player; agent dies. Cadence CLOSED. No USB. No `/dev/cu.usbmodem*`. **No audio playback.** No 8 s loop.

STATUS: **CONSISTENT** (artifact ↔ `DEAM_AROUSAL_RECEIPT.md` ↔ `SELECTION_GATE.md` rounding). Arousal is **not** Gate A/B/C PASS. HOST-ONLY. I/O unfrozen.

CLAIM: Measured P1 (`artifacts/deam_arousal/receipt.json`, label HOST-ONLY, n_songs=82): **2015_full n=58** mean r(arousal, RMS)=**0.373323** → docs **0.37**; mean R² energy (RMS+bands)=**0.295949** → docs **0.30**; mean R² DSP-full (energy+flux/onset/novelty)=**0.338212** → `DEAM_AROUSAL_RECEIPT.md` **0.34**. `SELECTION_GATE.md` Evidence cites only r=0.37 and R²=0.30 (energy). Same run, not a second experiment. 2013_clip n=24 mean r_rms=**−0.035957** → **−0.04**; R² energy **0.112** / DSP-full **0.153**. No 2014_clip in `by_cohort` (24+58=82).

CLAIM: Residual vs this DSP set is real and is **SELECTION_GATE criterion 3** only (“real-audio incremental vs DSP — DEAM human arousal vs energy (P1)”). It is **not** a Gate A stamp. Gate A PASS in `SELECTION_GATE.md` is **`source_share` (P3-B)** only. Do not read line-70 DEAM numbers as `arousal` PASS.

CLAIM: Per-song controls match the P5 page. 2030 r_rms=**0.810761**, R²_energy=**0.760049** (page 0.81 / 0.76). 2028 r_rms=**0.805332**, R²_energy=**0.696652** (page 0.80 / 0.70). Residuals: 2034 r=**0.102125** R²=**0.022387**; 2041 r=**0.065796** R²=**0.027650**; 2056 r=**−0.068989** R²=**0.035534**. `DEAM_AROUSAL_RECEIPT.md` also lists **2049** (R²=**0.038039**, r=**0.153644**) as R²_energy < 0.04; P5 five-song set dropped 2049. Not a number conflict.

CLAIM: Gate B table has **no** `arousal × mode × lever`. P5 A/B/C (`w=0.65`, A=onset, B=RMS extra DoF, C=human-arousal extra DoF) is a HOST control plot, not firmware, not LGP, not Captain LED judgement, not a student freeze. Gate C remains OPEN (host pixels ≠ silicon pixels ≠ LGP look). Working shortlist still lists dynamic arousal as unfrozen.

CLAIM: Essentia `deam-msd-musicnn-2` vs human 2 Hz on two songs (r≈−0.08 / −0.15) is criterion-4 teacher quality, not a Gate A oracle. L11 owns that head. Semantic-v0 synthetic r=0.99 is the falsifier that **does not** repeat here.

EVIDENCE: `artifacts/deam_arousal/receipt.json` (`by_cohort.2015_full`, `high_residual_vs_energy`, songs 2028/2030/2034/2041/2049/2056); `docs/mir/DEAM_AROUSAL_RECEIPT.md`; `docs/mir/SELECTION_GATE.md` (Gate A question, criterion 3, Evidence so far line-70, Gate B table, shortlist); `docs/mir/visual_replay/index.html`; `src/edgeai/mir/arousal_vs_dsp.py`; `mir/registry.yaml` id `deam` (executed; commercial UNKNOWN).

COMMAND: none. Receipts already on disk. Do **not** re-run `uv run python scripts/deam_arousal_vs_dsp.py` this lane (loads local DEAM mp3; not playback, not needed). No ffplay. No USB.

METHOD_RISK: HOST-ONLY. Human GT is 2 Hz from ~15 s. OLS R² is this librosa set (rms, bands, flux, onset_env, novelty), not “all DSP.” 2015 preferred per DEAM manual; 2013 clips are near-zero r. Dataset research-yes / commercial UNKNOWN (registry). Traces gitignored (`artifacts/deam_arousal/traces/`). P5 is isolated HTML, not a binding. Mean r=0.37 is **not** “arousal ≈ energy on every song.” No silicon numbers.

NEXT: do not train an arousal student until a product lighting evaluator says C beats B on a named `arousal × mode × lever`. Keep Gate A PASS on `source_share` only. Optional later: add R² DSP-full 0.34 to SELECTION_GATE Evidence so far (completeness, not a stamp change). No Titan. No Cadence reopen.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L07 contract: DEAM vs Gate A; HOST-ONLY; no playback. |
| 2026-08-31 | agent:grok | Re-derived vs receipt.json; criterion-3 ≠ Gate A PASS; P5/2049 completeness. |
