---
abstract: "L17 HOST: SERIAL_STUDIO.md matches D19. SS observe/record. Shuttle FAIL parked. Cadence refuses SS USB. Do not repair SS. No :7777."
---

# L17 — SERIAL_STUDIO vs D19

HOST-ONLY. Cadence CLOSED. No USB. No Serial Studio. Do not talk `:7777`.

STATUS: PASS

CLAIM: `docs/mir/SERIAL_STUDIO.md` matches D19. Serial Studio is the K1 observe/record instrument (Historian, snapshots, raw bytes, offline Python). It is not transport authority. The `k1_gate` `:7777` shuttle is demoted. Cadence refuses Serial-Studio-owned USB (`SERIAL_STUDIO_NOT_TRANSPORT`) and uses pyserial only after SS releases the port. Exclusive USB for command/reply is permanent. Do not multiplex two owners on one CDC. Do not repair the shuttle.

EVIDENCE:
- D19 Chosen/Rejected/Revisit: `docs/DECISIONS.md` (D18 Revisit line: superseded by D19; Chosen body of D18 is historical only).
- Instrument contract: `docs/mir/SERIAL_STUDIO.md` stamp OBSERVE/RECORD; Authority table; Exclusive port; Cadence refuse + pyserial; shuttle demoted as architectural fact.
- Source refuse: `src/edgeai/serial_studio.py` module docstring; `refuse_if_serial_studio_owns_usb` (`SERIAL_STUDIO_NOT_TRANSPORT`); `shuttle_roundtrip_proven` “Cadence does not wait… shuttle is demoted (D19)”; `open_k1_serial` labelled “Legacy :7777 shuttle opener. Cadence must not call this (D19).”
- Cadence path: `scripts/gate_c0_cadence_silicon.py` imports refuse only, calls it before flash and before `open_ser`; prints `I/O: pyserial`. Zero `open_k1_serial` / `SerialStudioPort` callers outside `serial_studio.py` and HOST tests.
- Parked FAIL (do not retest): `artifacts/serial_studio/MAIN_RPL_SHUTTLE_ROUNDTRIP.json` `MAIN_RPL_SHUTTLE_ROUNDTRIP=FAIL` `bytesRead=0`; `MAIN_BENCH_RX_RECOVERY.json` `cadence=SHUTTLE_UNPROVEN` `next_authorised_experiment=K1-MAIN-RPL-USB-RESET-RX-GO`.
- Roster: `AGENTS.md` Serial Studio = observe/record only; exclusive-port rule; Cadence silicon CLOSED.
- Handoff: `docs/agent/HANDOFF.md` shuttle DEAD/DEMOTED; C1 does not need it (`docs/mir/GATE_C1.md` Not this run: Serial Studio shuttle).
- Cadence USB sentence: `docs/mir/GATE_C0_CADENCE.md` “Serial Studio must release the K1 port first.”

COMMAND: none. Docs/source compare only. Do not open Serial Studio. Do not connect to `127.0.0.1:7777`. Do not `lsof` live `usbmodem`. Do not DTR/RTS/1200-baud. Do not `K1-MAIN-RPL-USB-RESET-RX-GO`. Do not pytest this lane (L29/L38/L39). Do not run `gate_c0_cadence_silicon.py`.

METHOD_RISK: HOST-ONLY file compare. D18 **Chosen** still says “UART owner” and “Cadence silicon talks :7777” — live only if an agent skips the Revisit supersession. `open_k1_serial` still talks `:7777` when `api_up()`; that is parked residue, not the cadence path. `SERIAL_STUDIO.md` programme-order line is D19-era (cadence still ahead); D20 already closed cadence — not a D19 mismatch. Raise-on-owned-USB is untested here (L38). `RX_RECOVERY=FAIL` left parked (logging, not cadence). This lane did not bind 7777, did not touch CDC, did not play audio.

NEXT: Leave SS parked. Do not repair the shuttle. C1 does not need it. Tests vs D19 belong to L39. Exclusive-port unit gap belongs to L38. Optional later physical Main-only USB reset is Captain GO only — not this lane.

MATRIX (D19 Chosen → SERIAL_STUDIO.md):
| D19 | SERIAL_STUDIO.md | Verdict |
| --- | --- | --- |
| SS = Historian/observe, not transport | stamp OBSERVE/RECORD; Not exclusive USB owner for silicon commands | MATCH |
| Demote exclusive-USB command shuttle | `k1_gate` :7777 shuttle demoted | MATCH |
| Refuse SS-owned USB; pyserial after release | `SERIAL_STUDIO_NOT_TRANSPORT`; close SS then cadence pyserial | MATCH |
| Exclusive port permanent; no multiplex | Exclusive port (permanent) | MATCH |
| `QSerialPort::write()` enqueue ≠ device delivery | same sentence | MATCH |
| Session 3/4 RX-dead; recovery off cadence path | `RX_RECOVERY=FAIL`; optional `K1-MAIN-RPL-USB-RESET-RX-GO` | MATCH |
| Failed shuttle is not Gate-C / firmware / C0-v2 | What this is not | MATCH |
| `SHUTTLE_UNPROVEN` ≠ one more PASS | architectural fact, not one more PASS | MATCH |

HARD FAIL: `SAME_SONG_LOOP_MAX_15MIN`. Cadence CLOSED. No USB multiplex.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L17 re-derived: SERIAL_STUDIO.md vs D19 PASS; shuttle FAIL parked; no :7777. |
| 2026-08-31 | agent:grok | L17: SERIAL_STUDIO vs D19 PASS; shuttle demoted; do not repair SS. |
