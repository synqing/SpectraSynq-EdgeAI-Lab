---
abstract: "L11 HOST-ONLY: Essentia DEAM/Jamendo receipts vs DEAM human 2 Hz. Head is not a substitute. No USB."
---

# L11 — Essentia oracle vs DEAM

STATUS: CONSISTENT. Docs match on-disk receipts. Not a freeze. HOST-ONLY. No USB. Cadence CLOSED.
CLAIM: `deam-msd-musicnn-2` arousal ≠ DEAM human 2 Hz on 2030/2034 (r=−0.075 / −0.150). DSP RMS still tracks 2030 (r=0.811) and fails 2034 (r=0.102, R²_energy=0.022). Jamendo mood means differ (2030 energetic 0.223 vs 2034 0.022); 2034 energetic std=0.009 (clip-flat).
EVIDENCE: `docs/mir/ESSENTIA_ORACLE.md` ↔ `artifacts/essentia_oracle/receipt.json` + `jamendo_receipt.json`; `docs/mir/DEAM_AROUSAL_RECEIPT.md` ↔ `artifacts/deam_arousal/receipt.json` (2015_full n=58, mean r_rms=0.373).
COMMAND: none this lane — receipts already on disk. Re-run only if artefacts vanish: `uv run python scripts/essentia_deam_heads.py` then `uv run python scripts/essentia_jamendo_mood.py`. No `/dev/cu.usbmodem*`. No 8 s loop. No same-song room play >15 min.
METHOD_RISK: MusiCNN hop vs 2 Hz GT may be misaligned; n=2 songs; crude [1,9]→[0,1] map in `scripts/essentia_deam_heads.py`; CC BY-NC-SA weights; DEAM commercial UNKNOWN; teacher use ≠ student-weight clearance.
NEXT: do not substitute the Essentia head for human arousal. L07 owns Gate-A DEAM vs DSP. Windowing study only if lighting needs sub-clip mood. No Titan. No freeze.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L11 contract: ESSENTIA_ORACLE vs DEAM receipts. |
