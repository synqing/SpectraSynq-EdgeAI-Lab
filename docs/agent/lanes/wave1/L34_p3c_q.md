---
abstract: "L34: HOST P3C_QUANT holdout Q1–Q3 MATCH C0-v2. Both PASS; silicon Δ stronger. Compare holdout not all/challenge. Docs-only."
---

# L34 — P3C_QUANT vs C0-v2 Q1–Q3 (10-line contract)

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** Same song/clip looped >15 min → agent dies.

1. **STATUS:** MATCH. Holdout Q1–Q3 **PASS** on both receipts. Binding `source_share × WaveformTempo × head_position`. Circular trap unchanged: raw r(pixels, share) is not a pass.
2. **CLAIM:** HOST P3-C extra-DoF and C0-v2 silicon answer the same three questions the same way; silicon is stronger, not a regression. Stamp on silicon: `ON_SILICON_PIXEL_VALIDATED`. `lag_corrected: false`.
3. **Q1 knob=head_position:** HOST holdout Spearman(pos, extra_gain)=**0.677** PASS vs C0-v2 native.holdout **0.832** PASS (floor ≥0.40). Top-level `C0V2_RESULT.json` Q1=PASS.
4. **Q2 share increment in pixels:** HOST holdout Δ partial r(head, share|mix)=**0.625** 9/9 (B 0.040 vs D 0.676) vs C0-v2 **0.690** 9/9 (B 0.160 vs D 0.844). Floor Δ≥0.15 and ≥70% clips Δ>0. Both PASS.
5. **Q3 source-abs after mix:** HOST holdout Δ pos_abs=**0.451** 9/9 vs C0-v2 **0.585** 9/9. Both PASS. Abs was not the driver.
6. **EVIDENCE:** `docs/mir/P3C_QUANT.json` `holdout`; `artifacts/gate_c0v2/C0V2_RESULT.json` `native.holdout` + top-level Q1/Q2/Q3. Denominator is holdout n=10, not HOST `all` n=20 and not C0-v2 `challenge` n=0.
7. **COMMAND:** none. Docs-only. No USB, no flash, no `/dev/cu.usbmodem*`, no 8 s loop, no cadence reopen.
8. **METHOD_RISK:** C0-v2 `native.challenge` n=0 prints Q1–Q3 FAIL vacuously — ignore. C0-v2 `native.all` n=10 is holdout-only. HOST firmware_sha `36466cd` ≠ probe `349d3cd4` chip `9087A500`. Q4 HOST FAIL / silicon PASS is **out of this lane**.
9. **NON-CLAIMS:** not Gate C perceptual; not C1 `LGP_PERCEPTUAL_VALIDATED`; not student freeze; previous two-clock C0 corpse still FAIL; Q5 FAIL on both.
10. **NEXT:** none for L34. Cadence silicon CLOSED. Student I/O unfrozen. C1 is the remaining human look.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L34 10-line: HOST P3C holdout Q1–Q3 MATCH C0-v2. |
