---
abstract: "L33 docs-only. HOST rehearsal is not C0. Silicon owns product clock (5 Hz / 50 ms / joint FAIL). Do not freeze student I/O from host 20 Hz or 50 ms FAIL. C1 on C0-v2 ~31.25 Hz 0 ms. Cadence CLOSED."
---

# L33 — HOST cadence vs silicon cadence

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** No USB. No flash. This file only. Cadence silicon **CLOSED**.

**STATUS:** PASS (audit). Host receipt and silicon `CADENCE_RESULT` agree internally. They are **not** the same clock. Host rehearsal is **not C0**. Silicon owns the product clock.

**CLAIM:** `GATE_C_CADENCE_HOST` is HOST-ONLY / `HOST_PIXEL_VALIDATED` design evidence (`not_c0: true`, `student_gate: OPEN`). Do not freeze student I/O from host 20 Hz or host 50 ms FAIL. Do not freeze 31.25 Hz because the host renderer used it (D17). Product clock is silicon: slowest 0-delay PASS **5 Hz**; largest added delay PASS **50 ms at 20 Hz**; joint **5 Hz+50 ms FAIL**. C1 plays the already-proven C0-v2 carrier (**~31.25 Hz, 0 ms extra delay**) on product firmware — not the host 20 Hz floor.

| Axis | HOST `artifacts/gate_c_cadence/receipt.json` | SILICON `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json` |
| --- | --- | --- |
| Stamp | HOST-ONLY / HOST_PIXEL_VALIDATED; `not_c0` / `not_silicon` / `not_lgp` | ON-SILICON; C0-v2 stays `ON_SILICON_PIXEL_VALIDATED`; cadence `PASS` / `CLOSED` |
| Oracle | median Δ partial r(head, share \| mix); ≥0.15 **and** ≥70% of this-run native Δ | C0-v2 Q1–Q3 (Spearman ≥0.40; Δ ≥0.15 and ≥70% clips Δ>0) |
| Native 31.25 Hz 0 ms | Δ 0.625 (P3-C dump reuse) | Q1 0.83; Q2 Δ 0.69 9/9; Q3 Δ 0.58 9/9 (`source=c0v2_receipt`) |
| Rate 20 Hz 0 ms | PASS Δ 0.501 (80% native) | PASS |
| Rate 10 Hz 0 ms | FAIL Δ 0.372 (60% native) | PASS |
| Rate 5 Hz 0 ms | FAIL Δ 0.305 | PASS (Q1 0.414) |
| Rate 2 Hz 0 ms | FAIL Δ 0.257 | not in the 1-D close |
| Delay 50 ms | FAIL **at 31.25 Hz** (req 50 → actual 64 ms; Δ 0.398 vs rel floor 0.438) | PASS **at 20 Hz** (req 50 → 64 ms; Q1 0.402) |
| Delay 100 ms | FAIL at 31.25 Hz | FAIL at 20 Hz (Q1) |
| Delay 200 ms | FAIL under 0.15 (Δ 0.104) at 31.25 Hz | FAIL at 20 Hz (Q1+Q2+Q3) |
| Joint 5 Hz+50 ms | not a host cell (host 5 Hz already FAIL) | FAIL Q1 (`r5_d50`) |
| 10 Hz+25 ms | not run | NOT_COMPLETED |
| Product clock | no — D17 rehearsal | yes — D20 5 Hz / 50 ms / joint FAIL |
| Student I/O | OPEN; do not freeze from these numbers | `student_freeze: false`; freeze only after C1 if the contract still holds |
| C1 carrier | not this | ~31.25 Hz, 0 ms extra delay, product firmware |

Do **not** average the two ladders. Host is stricter on rate (20 Hz vs silicon 5 Hz) and fails 50 ms on a **different delay axis** (31.25 Hz vs silicon 20 Hz). Host does not veto silicon cells.

**EVIDENCE:** `docs/mir/GATE_C_CADENCE_HOST.md`; `artifacts/gate_c_cadence/receipt.json` (`not_c0: true`, `lowest_passing_rate_hz: 20`, `delay_cliff_s: 0.05`); `docs/mir/GATE_C0_CADENCE.md`; `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json` (`plain.minimum_demonstrated_useful_rate_hz: 5`, `maximum_demonstrated_added_delay_s: 0.05`, `combined_5hz_50ms: FAIL`, `gate_c0_cadence: CLOSED`); `docs/mir/GATE_C.md` (HOST rehearsal **is not C0**; do not freeze 20 Hz as the student contract); `docs/DECISIONS.md` D17/D20; `docs/mir/GATE_C1.md`; `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md` (C1 playback C0-v2 ~31.25 Hz 0 ms).

**COMMAND:** none. Docs-only. Do not run `gate_c_cadence_host.py` or `gate_c0_cadence_silicon.py`. No pytest, no USB, no `/dev/cu.usbmodem*`, no 8 s loop, no ffplay.

**METHOD_RISK:** Quoting host 20 Hz as “the cadence” undoes D20 silicon 5 Hz. Treating host 50 ms FAIL as the delay cap undoes silicon 50 ms PASS at 20 Hz — those are not the same cell. Treating host native 31.25 Hz as a student freeze undoes D17. Treating either rehearsal as C0 confuses C0-v2 pixels with a later subtest. L18 owns silicon doc-vs-receipt cells. L03 owns JSON `PROPOSED` vs MD `FROZEN_FOR_C1`. L04 owns joint 5+50 must-not-assume.

**NEXT:** Leave host as HOST-ONLY. Consume silicon 5 Hz / 50 ms / joint FAIL. Do not freeze student I/O. C1 OPEN on the ~31.25 Hz 0 ms carrier. Do not re-run cadence.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Created. 10-line HOST vs silicon cadence contract. HOST is not C0. |
| 2026-08-31 | agent:grok | Re-derived from receipts. Split table: host delay axis is 31.25 Hz, silicon delay axis is 20 Hz. Silicon owns product clock. I/O unfrozen. C1 on ~31.25 Hz 0 ms. |
