---
abstract: "L11 HOST-ONLY: Essentia DEAM/Jamendo receipts vs DEAM human 2 Hz. Head is not a substitute. No USB."
---

# L11 — Essentia oracle vs DEAM

STATUS: CONSISTENT. Docs match on-disk receipts (docs round; receipts are source). Not a freeze. HOST-ONLY. No USB. Cadence CLOSED.

CLAIM: `deam-msd-musicnn-2` predicted arousal ≠ DEAM human 2 Hz on the two songs the oracle actually ran (2030/2034): receipt r=−0.075 / −0.150. Docs (`ESSENTIA_ORACLE.md`, `DEAM_AROUSAL_RECEIPT.md`) say r ≈ −0.08 / −0.15. Same fact.

CLAIM: That head is **not** a substitute for the human series, even on the energy-like song. DSP RMS still tracks 2030 (receipt r=0.811, R²_energy=0.760; doc 0.81 / 0.76) and fails 2034 (receipt r=0.102, R²_energy=0.022; doc “R²_energy < 0.04”). Head r is negative on both.

CLAIM: Jamendo mood means differ across those songs; 2034 energetic is clip-flat. Receipt 2030 energetic mean=0.223 std=0.072 vs 2034 mean=0.022 std=0.009. Watch table in `ESSENTIA_ORACLE.md` (energetic/relaxing/happy/dark) matches `jamendo_receipt.json` to 3 dp.

CLAIM: Cohort DSP residual is L07’s Gate-A evidence, not L11’s. DEAM 2015_full n=58 mean r_rms=0.373, R²_energy=0.296, R²_dsp_full=0.338 (docs 0.37 / 0.30 / 0.34). L11 only asks whether the Essentia teacher head recovers the human 2 Hz series. It does not, on n=2.

EVIDENCE:
- `docs/mir/ESSENTIA_ORACLE.md` ↔ `artifacts/essentia_oracle/receipt.json` (2030 n_frames=183 r=−0.07513; 2034 n_frames=74 r=−0.15027; VA means [5.858, 5.146] / [5.539, 4.369] on ~[1,9])
- `artifacts/essentia_oracle/jamendo_receipt.json` (2030 n=276 dur=275.1 s; 2034 n=111 dur=111.9 s)
- `docs/mir/DEAM_AROUSAL_RECEIPT.md` ↔ `artifacts/deam_arousal/receipt.json` (2015_full n=58; 2030 r_rms=0.81076 R²_energy=0.76005; 2034 r_rms=0.10213 R²_energy=0.02239)
- `docs/mir/SELECTION_GATE.md` teacher/oracle line: “Essentia DEAM head ≠ human 2 Hz on two songs. Jamendo mood means differ; often clip-flat.” Matches this lane.

COMMAND: none this lane — receipts already on disk. Do **not** re-run heads (that would decode DEAM mp3s). If artefacts vanish later: `uv run python scripts/essentia_deam_heads.py` then `uv run python scripts/essentia_jamendo_mood.py`. No `/dev/cu.usbmodem*`. No 8 s loop. No same-song room play >15 min. Cadence CLOSED.

METHOD_RISK: MusiCNN hop vs 2 Hz GT may be misaligned (`scripts/essentia_deam_heads.py` linspace + `np.interp` onto GT times; crude [1,9]→[0,1] map). n=2 songs (energy-like 2030 vs high-residual 2034). Weights CC BY-NC-SA; registry also flags CC BY-NC-ND conflict on essentia-models. Essentia library AGPL. DEAM commercial UNKNOWN. Teacher use ≠ student-weight clearance. HOST-ONLY; not Titan; not ON-SILICON.

NEXT: do not substitute the Essentia head for human arousal. Do not freeze student I/O on this head. L07 owns Gate-A DEAM vs DSP. Windowing study only if lighting needs sub-clip mood (2034 energetic std=0.009 argues against drop-scale). No Titan. No freeze.

HARD FAIL: `SAME_SONG_LOOP_MAX_15MIN` — same song/clip in the room >15 min → kill the player; agent dies.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L11 contract: ESSENTIA_ORACLE vs DEAM receipts. |
| 2026-08-31 | agent:grok | Re-derived from receipts; doc rounding vs JSON; L07 split. |
