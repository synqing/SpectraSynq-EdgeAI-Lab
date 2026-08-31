---
abstract: "L17: SERIAL_STUDIO.md matches D19. Shuttle demoted. Do not repair SS. Observe/record only."
---

# L17 — SERIAL_STUDIO vs D19

STATUS: PASS
CLAIM: `docs/mir/SERIAL_STUDIO.md` matches D19. Serial Studio is observe/record (Historian, snapshots, offline Python). It is not transport. The `k1_gate` :7777 shuttle is demoted. Cadence refuses SS-owned USB (`SERIAL_STUDIO_NOT_TRANSPORT`) and uses pyserial only after SS releases the port. Exclusive USB for command/reply is permanent. Do not repair SS.
EVIDENCE: `docs/DECISIONS.md` D19 (D18 Revisit superseded); `docs/mir/SERIAL_STUDIO.md`; `src/edgeai/serial_studio.py` `SERIAL_STUDIO_NOT_TRANSPORT`; `docs/agent/HANDOFF.md` shuttle DEAD/DEMOTED.
COMMAND: none. Do not open Serial Studio. Do not talk :7777. Do not touch `/dev/cu.usbmodem*`. Do not DTR/RTS/1200-baud. Do not `K1-MAIN-RPL-USB-RESET-RX-GO`. Do not fix the shuttle.
METHOD_RISK: Docs/source compare only. No USB. No shuttle retest. `RX_RECOVERY = FAIL` left parked (logging, not cadence). D20 already closed cadence silicon; L17 does not reopen it.
NEXT: Leave SS parked. C1 does not need the shuttle. Tests vs D19 belong to L39.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L17: SERIAL_STUDIO vs D19 PASS; shuttle demoted; do not repair SS. |
