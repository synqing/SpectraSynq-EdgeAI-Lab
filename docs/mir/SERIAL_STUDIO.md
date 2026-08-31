---
abstract: "Serial Studio is the K1 observe/record instrument. Cadence uses pyserial after SS releases USB. Dashboard is not a gate. Shuttle demoted (D19)."
---

# Serial Studio × EdgeAI-Lab

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Stamp: **K1 SERIAL STUDIO INSTRUMENT — OBSERVE/RECORD**. Not transport authority.

Serial Studio Pro 4.0.3 is the dual-K1 logger: dashboard, Historian, CSV, parser, snapshots, offline Python scoring. It is **not** the cadence command path.

Live USB sessions 3/4 are RX-silent (`RX_RECOVERY = FAIL`). That is a broken session, not a dead product. C0-v2, source ownership, Waveform Tempo, and firmware are untouched.

## Authority

| Layer | Job | Not |
| --- | --- | --- |
| Serial Studio | observe, record, visualise, archive | exclusive USB owner for silicon commands |
| pyserial (after SS releases the port) | cadence / dump command I/O | steal `usbmodem` while SS holds it |
| Device `device_ms` | timing | host UART arrival |
| Historian snapshot + raw bytes | evidence | dashboard screenshot |
| Offline Python scorer | verdict | Serial Studio transforms |

Host `QSerialPort::write()` enqueue is not proof the device received bytes. Device→host RX is a separate fact.

## Exclusive port (permanent)

An authoritative silicon test that needs interactive command/reply gets exclusive ownership of that K1 serial port. Serial Studio must release it first. Do not multiplex two owners through software unless a later transport is designed for it.

## Cadence

Cadence **refuses** Serial-Studio-owned USB (`SERIAL_STUDIO_NOT_TRANSPORT`). Close Serial Studio, then `scripts/gate_c0_cadence_silicon.py` talks pyserial. The `k1_gate` shuttle on :7777 is demoted. `SERIAL_STUDIO_NOT_TRANSPORT` is an architectural fact, not “the shuttle needs one more PASS.” USB RX recovery (`K1-MAIN-RPL-USB-RESET-RX-GO`) is optional logging, off the cadence critical path.

Programme order: **C0-v2 PASS → cadence/latency via pyserial → transport contract → C1 LGP.**

## What this is not

Not C0-v2 (already `ON_SILICON_PIXEL_VALIDATED`). Not C1. Not a firmware bug. Not a reason to trash Historian/parser work.

## Ship path

1. Already: D19 in source; cadence refuse-SS-USB; shuttle FAIL left parked.
2. Remaining: (optional later) `K1-MAIN-RPL-USB-RESET-RX-GO` for Main-only physical reset if we want logging RX back; cadence silicon still pyserial.
3. Who: Captain for physical reset; agent for observe/reopen after that GO.
4. Cadence unlock does **not** wait on Serial Studio shuttle PASS.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Exclusive-port rule permanent; USB RX recovery off cadence path. |
| 2026-08-31 | agent:grok | D19: instrument not transport; cadence pyserial; shuttle demoted. |
| 2026-08-31 | agent:grok | Contract: SS acquisition, receipts authority, GATE vs OBSERVE. |
