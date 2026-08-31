---
abstract: "L03: CADENCE_RESULT.json plain vs SEMANTIC_TRANSPORT_CONTRACT.md. Edges match; 50 ms is requested not 64 ms hop; JSON still PROPOSED; extra_gain not in plain."
---
STATUS: CONFLICT
CLAIM: Plain-block cadence edges agree with the MD table; freeze status, delay units, extra_gain, hold grid, and omitted 10 Hz+25 ms do not.
EVIDENCE: artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json#plain ; docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md
COMMAND: python3 -c 'import json;p=json.load(open("artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json"));print(p["plain"]);print([(c["requested_delay_ms"],c["actual_delay_ms"],c["verdict"]) for c in p["delay"]["cells"]])'
METHOD_RISK: Student treating 50 ms as hop-true delay is false (actual 64 ms). 5 Hz PASS is Q1–Q3 only (cell Q4 FAIL). Cadence stays CLOSED.
NEXT: Do not reopen cadence or USB. Do not freeze student I/O. Do not assume 5 Hz+50 ms. Stamp MD delay as requested-ms; reconcile JSON contract.status PROPOSED vs MD FROZEN_FOR_C1.
MATCH: slowest 0-delay 5 Hz PASS; largest passing requested delay 50 ms at 20 Hz (Q1–Q3 PASS); combined_5hz_50ms FAIL; 100 ms at 20 Hz FAIL (Q1 FAIL).
CONTRADICTION-1: MD FROZEN_FOR_C1 vs JSON contract.status PROPOSED and c1 OPEN (plain.captain_close PASS; gate_c0_cadence CLOSED).
CONTRADICTION-2: MD extra_gain [0.62,1.0] and channels vocals/drums/bass/other absent from plain; MD hold omits 32 ms hop ZOH, first-sample freeze, extra_gain field.
CONTRADICTION-3: plain combined_10hz_25ms NOT_COMPLETED omitted from MD; MD C1 playback C0-v2 ~31.25 Hz 0 ms extra is not in plain (rate cell 31.25 Hz PASS exists).
