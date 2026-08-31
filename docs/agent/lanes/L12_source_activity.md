---
abstract: "L12 HOST docs-only. SOURCE_ACTIVITY and GATE_C agree on PRE-PRODUCT FEASIBILITY PASS and Gate B HOST PASS. SOURCE_ACTIVITY is silent on the two-clock C0 corpse (FAIL) and never records C0-v2 ON_SILICON_PIXEL_VALIDATED. Gate C programme still OPEN (C1). No USB."
---

# L12 — SOURCE_ACTIVITY vs GATE_C

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** Cadence CLOSED. No USB. No flash. No audio. This file only.

| Field | Value |
| --- | --- |
| STATUS | **PASS (audit). Subject STALE on silicon close.** |
| CLAIM | They agree on HOST programme stamps. They do not both carry the silicon close. |
| CLAIM | **PRE-PRODUCT FEASIBILITY PASS — AGREE.** SOURCE_ACTIVITY L148, GATE_C L9, D17 Chosen. A PASS + B HOST PASS + recoverability HOST PASS + I/O unfrozen + C not closed from host pixels. |
| CLAIM | **C0 two-clock FAIL corpse — AGREE if read as “never a PASS.”** Receipt `c0=FAIL`, `execution=INVALID_TEMPORAL_EXECUTION`, `stamp=not ON_SILICON_PIXEL_VALIDATED`. SOURCE_ACTIVITY never names that run. It does not contradict the corpse. It also never says “leave the corpse FAIL.” |
| CLAIM | **C0-v2 `ON_SILICON_PIXEL_VALIDATED` — DISAGREE by omission.** GATE_C abstract + `C0V2_RESULT.json` stamp it. SOURCE_ACTIVITY last close is still “Gate C (physical show) is still OPEN” / “Next is Gate C.” It never records C0-v2. |
| EVIDENCE | `docs/mir/SOURCE_ACTIVITY.md`; `docs/mir/GATE_C.md`; `docs/mir/GATE_C0V2.md`; `docs/DECISIONS.md` D16–D17, D20; `docs/mir/P3C_QUANT.json` holdout; `artifacts/gate_c0/C0_RESULT.json`; `artifacts/gate_c0v2/C0V2_RESULT.json`; `artifacts/share_student/receipt.json`; `AGENTS.md` source-oracle / source-ownership rows. Receipts read, not re-run. |
| COMMAND | none. HOST read of markdown + frozen JSON. Did not run `p3c_quant`, `gate_c0_silicon.py`, `gate_c0v2_silicon.py`, MUSDB, or USB. |
| METHOD_RISK | GATE_C body L27 still leads with two-clock FAIL and “C1 blocked” while abstract + changelog stamp C0-v2 PASS and C1 OPEN. An agent who skips the abstract reads a live FAIL. L22 owns that split. GATE_C0V2 still says cadence OPEN / C1 blocked — receipt-time, superseded by D20. L18 owns cadence-doc drift. |
| NEXT | Later writer of SOURCE_ACTIVITY (not this lane): keep HOST B PASS; add C0 corpse FAIL frozen; add C0-v2 `ON_SILICON_PIXEL_VALIDATED`; cadence CLOSED; C1 OPEN; I/O still unfrozen. Do not treat HOST Δ 0.63 as silicon. Do not freeze student I/O. Do not rescore `artifacts/gate_c0/`. |

## Do they agree? (the three stamps)

Denominator = live programme (`AGENTS.md` source rows + D17 + D20 + silicon receipts), not SOURCE_ACTIVITY vs itself.

| Stamp | SOURCE_ACTIVITY | GATE_C | Receipt / decision | Verdict |
| --- | --- | --- | --- | --- |
| PRE-PRODUCT FEASIBILITY PASS | L148 yes. Changelog “Feasibility PASS stamp; Gate C next.” | L9 programme stamp. D17 Chosen. | `share_student/receipt.json` `verdict=PASS`, `student_io_frozen=false`, four-source including `other`. | **AGREE.** [FACT] |
| Gate A share incremental-info | P3-B PASS; abs DEMOTE. | “Gate A PASS.” | P3-B within-track r(share, mix) vocals 0.17 / drums 0.10 / bass 0.16 vs abs 0.44 / 0.62 / 0.64. | **AGREE.** [FACT] |
| Gate B `source_share × WaveformTempo × head_position` HOST PASS | HOST PASS. Q2 holdout Δ **0.63** 9/9. | “Gate B HOST PASS.” Binding exact. | `P3C_QUANT.json` holdout: Q1 Spearman 0.68 PASS; Q2 Δ 0.625 9/9 PASS; Q3 Δ 0.45 9/9 PASS. Label `HOST-ONLY`. | **AGREE.** [FACT] Host Δ is not silicon. |
| `composition_change × Comet × impact-launch` FAIL | FAIL this comparator. | Parked: composition_change ML head. | `P3C_QUANT.json` Q5 FAIL (F1 Δ 0.02). | **AGREE.** [FACT] |
| Recoverability HOST PASS | L148 21k CNN, four-source `other`. | Recoverability HOST PASS. | `share_student/receipt.json` HOST-ONLY PASS. | **AGREE.** [FACT] |
| I/O unfrozen; Demucs NO; no hop-level student until C | Student OPEN; Demucs NO. | I/O unfrozen. Parked: hop-level student, Demucs. | D17; D20 still unfrozen. | **AGREE.** [FACT] |
| C0 two-clock corpse FAIL | Silent. Still “Gate C OPEN.” | Body L27: FAIL INVALID_TEMPORAL_EXECUTION; dumps frozen; runner retired. | `C0_RESULT.json`: `c0=FAIL`, Q1 0.13, Q2/Q3 6/9, `+14 hops` diagnosis only, `stamp=not ON_SILICON_PIXEL_VALIDATED`, runner RETIRED. | **AGREE on FAIL if asked. SILENT in SOURCE_ACTIVITY.** [FACT] Not a claim that SOURCE_ACTIVITY promotes the corpse. |
| C0-v2 `ON_SILICON_PIXEL_VALIDATED` | **Absent.** Last sentence: next is Gate C. | Abstract yes. Body L27 still the corpse. Changelog “C0-v2 PASS.” | `C0V2_RESULT.json`: `c0v2=PASS`, Q1 Spearman **0.83**, Q2 Δ **0.69** 9/9, Q3 Δ **0.58** 9/9, `lag_corrected=false`, `retired_c0_untouched=true`, stamp `source_share × WaveformTempo × head_position = ON_SILICON_PIXEL_VALIDATED`. | **DISAGREE by omission.** [FACT] GATE_C abstract matches the receipt. SOURCE_ACTIVITY does not. GATE_C body can still be read as C0 FAIL (L22). |
| Gate C programme | “still OPEN” / “next is Gate C.” | L10 “Gate C OPEN”; L53 C1 OPEN; cadence CLOSED (D20). | C0-v2 is pixels, not C1. `C0V2_RESULT.json` `non_claims` includes “no Gate C perceptual verdict.” | **AGREE that C is not closed.** [FACT] Drift: SOURCE_ACTIVITY treats all of Gate C as not-yet-run. Live: C0-v2 done; C1 is the remaining human look. [INFERENCE] |
| Cadence | Not stated. | Abstract: CLOSED Captain 2026-08-31. GATE_C0V2 still “OPEN.” | D20: 5 Hz / 50 ms; joint 5+50 FAIL; do not reopen. | **Out of SOURCE_ACTIVITY scope.** GATE_C vs GATE_C0V2 cadence/C1 wording is L18/L22, not this lane. |

## Numbers (re-derived, not recited)

HOST Gate B (`P3C_QUANT.json` `holdout`, n=10): Q1 0.677 PASS (≥0.40); Q2 Δ 0.625 9/9 PASS; Q3 Δ 0.451 9/9 PASS.

Two-clock C0 (`C0_RESULT.json` `native`, n=10): Q1 0.133 FAIL; Q2 Δ 0.167 wins 6/9 FAIL; Q3 Δ 0.186 wins 6/9 FAIL. Chip `9087A500`. Probe git `acaecaa8`.

C0-v2 (`C0V2_RESULT.json` `holdout`, n=10): Q1 0.832 PASS; Q2 Δ 0.690 9/9 PASS; Q3 Δ 0.585 9/9 PASS. Probe git `349d3cd4` (GATE_C0V2.md). Same binding. Not a lagged rescore of the corpse.

HOST Δ 0.63 ≠ silicon Δ 0.69. Do not substitute.

## Aligned (keep)

abs DEMOTE; share incremental-info PASS; exact binding `source_share × WaveformTempo × head_position`; composition-change Comet FAIL this comparator; recoverability HOST PASS; PRE-PRODUCT FEASIBILITY PASS; student I/O unfrozen; Demucs NO; Waveform Tempo is a continuity carrier; Captain is not the LED validator; two-clock corpse stays FAIL if mentioned at all.

## Drift (do not execute here)

1. SOURCE_ACTIVITY “next is Gate C” vs live “C0-v2 pixels done; C1 is the remaining Gate C look.”
2. GATE_C L27 live-voice FAIL vs abstract C0-v2 PASS (L22).
3. GATE_C0V2 cadence OPEN / C1 blocked vs D20 cadence CLOSED / C1 OPEN.

## Ship path (this lane)

1. Already on disk: HOST A/B receipts; C0 corpse FAIL; C0-v2 PASS; D17 feasibility; D20 cadence close.
2. Remaining: C1 LGP look (Captain, one full song, no 8 s loop). SOURCE_ACTIVITY silicon-close paragraph is optional later prose, not C1.
3. Who: C1 is Captain. This SSA does not flash, dump, or play audio.
4. Shipped for L12: this audit file. Shipped for Gate C: `LGP_PERCEPTUAL_VALIDATED` after C1, not this file.

USB: none. No `/dev/cu.usbmodem*`. No 8 s loop. No sibling worktree.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Created. Stamp diff SOURCE_ACTIVITY vs GATE_C / GATE_C0V2. |
| 2026-08-31 | agent:grok | Re-derived three-stamp agree/omit table from P3C_QUANT + C0_RESULT + C0V2_RESULT. |
