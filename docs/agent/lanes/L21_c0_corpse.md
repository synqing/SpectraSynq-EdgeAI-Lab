---
abstract: "L21: two-clock C0 corpse stays FAIL. Live C0 is C0-v2 ON_SILICON_PIXEL_VALIDATED 2026-08-31. GATE_C is the programme; GATE_C0V2 is the successor method. Do not treat corpse as current. HOST receipts only."
---

# L21 — C0 two-clock corpse vs C0-v2

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** Cadence CLOSED. No USB. No flash. This file only.

| Field | Value |
| --- | --- |
| **STATUS** | **PASS** (receipt split). Corpse FAIL is frozen history. Live C0 stamp is C0-v2. |
| **CLAIM** | Two-clock C0 stays **FAIL** (`INVALID_TEMPORAL_EXECUTION`). C0-v2 is the **PASS** (`ON_SILICON_PIXEL_VALIDATED`) on the same binding. Do not promote the corpse with +14 hops. Do not quote GATE_C’s FAIL paragraph as the live close. |
| **EVIDENCE** | `artifacts/gate_c0/C0_RESULT.json`; `artifacts/gate_c0/CORPSE_MANIFEST.json` (89 files; `C0_RESULT.json` SHA-256 `35075e7d244c20b5fd45e5969469d74d7e70fc04962ea593c58394e731265161`); `artifacts/gate_c0v2/C0V2_RESULT.json`; `docs/mir/GATE_C.md`; `docs/mir/GATE_C0V2.md`. |
| **COMMAND** | none. HOST JSON/docs read only. Did not run `scripts/gate_c0_silicon.py`, `scripts/gate_c0v2_silicon.py`, `p3c_quant`, or lag search on corpse dumps. |
| **METHOD_RISK** | HOST-ONLY restatement of frozen receipts. Chip both `9087A500`. C0 probe git `acaecaa8`; C0-v2 probe git `349d3cd4`. Cadence CLOSED is D20 / L18 — not this lane. L22 owns GATE_C prose rewrite. |
| **NEXT** | Leave `artifacts/gate_c0/` frozen. Authority for C0 pixels is C0-v2. Do not rescore. No USB. L22 rewrites GATE_C body. Later writers may tombstone SELECTION_GATE / GATE_C0_SILICON_PATH / D17 revisit so they do not read as “C0-v2 still next.” |

## GATE_C vs GATE_C0V2

These are not two live verdicts. Confusing them is how the corpse becomes “current.”

| Doc | What it is | What it is not |
| --- | --- | --- |
| `docs/mir/GATE_C.md` | Programme Gate C: C0 = silicon pixels, C1 = LGP look. Abstract + D20: C0-v2 PASS, cadence CLOSED, C1 OPEN. | Not the two-clock run. Body §C0 still *leads* with corpse FAIL (L22). |
| `docs/mir/GATE_C0V2.md` | Successor **method** after the retired two-clock harness. Device-epoch invariant. Receipt of the 2026-08-31 PASS. Labels previous C0 as corpse FAIL. | Not a second binding. Abstract still says cadence OPEN / C1 blocked — stale vs D20; L18/L12 own that. |
| `docs/mir/GATE_C0_SILICON_PATH.md` | Corpse-era inject/dump recon. Runner retired. | Not the live ship path. “Remaining: flash C0-v2” is already done. |

**Rule:** live C0 = GATE_C0V2 receipt. GATE_C is the programme wrapper. Corpse dumps stay FAIL forever.

## Receipts (re-derived)

Same binding both runs: `source_share × Waveform Tempo × head_position`. Same scorer floors (Q1 Spearman ≥ 0.40; Q2/Q3 Δ ≥ 0.15 and ≥70% wins). Thresholds not changed after silicon.

| | Two-clock C0 (corpse) | C0-v2 (live) |
| --- | --- | --- |
| File | `artifacts/gate_c0/C0_RESULT.json` | `artifacts/gate_c0v2/C0V2_RESULT.json` |
| Verdict | `c0=FAIL` `execution=INVALID_TEMPORAL_EXECUTION` | `c0v2=PASS` `lag_corrected=false` `retired_c0_untouched=true` |
| Stamp | `not ON_SILICON_PIXEL_VALIDATED` | `source_share × WaveformTempo × head_position = ON_SILICON_PIXEL_VALIDATED` |
| Q1 | 0.13 FAIL | 0.83 PASS |
| Q2 | 6/9 FAIL (Δ 0.17) | Δ 0.69 **9/9** PASS |
| Q3 | 6/9 FAIL (Δ 0.19) | Δ 0.58 **9/9** PASS |
| Timing | two host clocks; capture ≠ inject (~0.5 s). +14 hops (~448 ms) is **diagnosis only** | one device epoch; self-test PASS; best lag 0 hops |
| Runner | `scripts/gate_c0_silicon.py` **RETIRED** | `scripts/gate_c0v2_silicon.py` |
| Probe | `k1_main_rpl_rtrace_probe` @ `acaecaa8` | same env @ `349d3cd4` |
| Product restore (that run) | `acaecaa8` / `k1_main_rpl_im69d` | `acaecaa8` / `k1_main_rpl_im69d` (GATE_C0V2.md) |

Post-hoc lag on the corpse is **not** a PASS. `C0_RESULT.json` `authority`: do not score with a corrected offset.

## Docs must not treat the corpse as current

Keep corpse FAIL as labelled history. Do **not** use it as the live C0 close.

| Surface | Current read | Required read |
| --- | --- | --- |
| `GATE_C.md` L27 | Looks live: “silicon close: FAIL … C1 blocked.” | Historical two-clock **corpse**. Live C0 is C0-v2 PASS. C1 OPEN (D20). **L22.** |
| `SELECTION_GATE.md` abstract | “C0 FAIL … C0-v2 next. C1 blocked.” | C0-v2 already PASS. C1 OPEN. I/O still unfrozen. |
| `GATE_C0_SILICON_PATH.md` §4 | Remaining work = flash C0-v2 | C0-v2 already shipped. Path is recon of the corpse. |
| `DECISIONS.md` D17 **Revisit** | “Next is C0-v2 … C1 still blocked.” | True as D17 history. Live programme is D19–D20. Do not execute the Revisit as a task list. |
| `GATE_C0V2.md` L9 | Correct: previous C0 stays FAIL. | Keep. |
| `AGENTS.md` source-ownership | Correct: “Two-clock C0 corpse stays FAIL.” Live row: C0-v2 `ON_SILICON_PIXEL_VALIDATED`. | Keep. |
| `HANDOFF.md` | Correct: corpse FAIL / C0-v2 PASS split. | Keep. |

## Non-claims

Not C1 `LGP_PERCEPTUAL_VALIDATED`. Not a student I/O freeze. Not a Tempo edit. Not another net. Not Cadence reopen. Not USB. Corpse not overwritten. Product firmware not changed this lane.

USB: none. Audio: none. No `/dev/cu.usbmodem*`. No 8 s loop.

---
**Document Changelog**
| Date | Author | Change |
| --- | --- | --- |
| 2026-08-31 | agent:grok | Compact contract: corpse FAIL vs C0-v2 PASS. |
| 2026-08-31 | agent:grok | Re-derive receipts; GATE_C vs GATE_C0V2; list docs that still treat corpse as current. |
