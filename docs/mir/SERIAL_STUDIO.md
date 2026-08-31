---
abstract: "Serial Studio is K1 observe/record only. Cadence runner RETIRED (D20) so SS is never cadence transport. Exclusive USB-CDC still binds. Shuttle demoted (D19). Do not open SS for command/reply."
---

# Serial Studio × EdgeAI-Lab

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Stamp: **K1 SERIAL STUDIO INSTRUMENT — OBSERVE/RECORD**. Not transport. Not cadence. Cadence silicon is **CLOSED**.

Serial Studio Pro 4.0.3 is the dual-K1 logger: dashboard, Historian, CSV, parser, snapshots, offline Python scoring. Agents may **observe and record**. They must **not** open Serial Studio as a command path, talk `:7777` for silicon I/O, or steal `usbmodem` while it holds the port.

## Cadence never uses Serial Studio

`scripts/gate_c0_cadence_silicon.py` is mechanically **RETIRED** (D20). `main()` calls `refuse_if_cadence_closed()` **before** argparse, flash, USB, or Bose. `--resume` is not an escape. Closed means closed.

Because that runner dies before it can open a port, Serial Studio is **never cadence transport**. Not via the demoted `k1_gate` `:7777` shuttle. Not via “close SS then pyserial cadence.” Do not run the retired script. Use existing receipts only: `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json`.

D18 said cadence talks `:7777` while SS holds USB. **Superseded** by D19 (instrument, not transport). D20 then retired the pyserial cadence runner. D22 keeps SS observe/record.

The `k1_gate` shuttle on `:7777` stays **demoted**. `open_k1_serial` is legacy residue. `SERIAL_STUDIO_NOT_TRANSPORT` is an architectural fact, not “the shuttle needs one more PASS.” Parked FAIL: `artifacts/serial_studio/MAIN_RPL_SHUTTLE_ROUNDTRIP.json` (`MAIN_RPL_SHUTTLE_ROUNDTRIP=FAIL`). Do not repair it. C1 does not need it (`docs/mir/GATE_C1.md` — Not this run).

Live USB sessions 3/4 are RX-silent (`RX_RECOVERY = FAIL`). That is a broken session, not a dead product. C0-v2, source ownership, Waveform Tempo, and firmware are untouched. Optional later `K1-MAIN-RPL-USB-RESET-RX-GO` is Captain GO only — logging recovery, not a cadence reopen.

## Exclusive USB-CDC (permanent)

An authoritative silicon test that needs interactive command/reply gets **exclusive** ownership of that K1 serial port. Serial Studio must release it first. Do not multiplex two owners on one USB-CDC unless a later transport is designed for it.

This rule **still binds** after cadence closed (D19, D22, `AGENTS.md`). Cadence is not that test. If silicon command/reply ever returns, it is pyserial after SS releases the port — never the `:7777` shuttle, never two Python processes on one `usbmodem`. Host `QSerialPort::write()` enqueue is not proof the device received bytes.

Guard in source: `refuse_if_serial_studio_owns_usb` / `holder_is_serial_studio` in `src/edgeai/serial_studio.py`. Cadence’s copy of that refuse is dead code on the retired path (`refuse_if_cadence_closed` fires first). The exclusive-port rule is not retired.

## Authority

| Layer | Job | Not |
| --- | --- | --- |
| Serial Studio | observe, record, visualise, archive | exclusive USB owner for silicon commands; cadence transport |
| Retired cadence runner | dead before USB | reopen cells; talk `:7777`; steal `usbmodem` |
| pyserial (after SS releases the port) | only if a later authorised silicon command/reply exists | cadence cells; multiplex with SS |
| Device `device_ms` | timing | host UART arrival |
| Historian snapshot + raw bytes | evidence | dashboard screenshot |
| Offline Python scorer | verdict | Serial Studio transforms |

Dashboard is awareness. Live Historian SHA is `LIVE_DB_FINGERPRINT` only. Gate identity is a closed SQLite backup snapshot. Parser may not invent `firmware_sha` / `frame_seq` / `AP_us`.

## Dashboard wiring (2026-08-31)

The UART is not the bug. The live `.ssproj` was plotting **all 21 parser slots plus clocks/bitmasks on one Y axis** (update_mask ~2e6), so BPM/conf/peak vanished. LED panel was bound to `unused_slot_17`. 3D plots 2/3 read parser indices 21–26 that do not exist. “New FFT Plot” was an LED+FFT dataset on slot 27 (empty). There is **no audio FFT on the wire** — FFT is KissFFT of `peak_scaled` (envelope), 133 Hz, 256 samples.

Live file: `~/Documents/Serial Studio/Projects/K1 Dual UART Observability.ssproj`.
Backup: `K1 Dual UART Observability.bak-1788185916.ssproj`.

Now:
- Multiplot: BPM, conf, lock, beat, onset, bass, silence, AGC, peak, energy, novelty only.
- LED: lock / beat / onset / bass / silence (`ledHigh=0.5`).
- 3D-1 Bench: peak × energy × novelty. 3D-2 Main: same. 3D-3 Bench: BPM × conf × peak.
- Envelope FFT: `peak_scaled` index 9, `fft=true`, `led=false`.

## What this is not

Not C0-v2 (already `ON_SILICON_PIXEL_VALIDATED`). Not C1. Not a firmware bug. Not a reason to trash Historian/parser work. Not a green light to launch Serial Studio, bind `127.0.0.1:7777`, `lsof` a live K1 port, DTR/RTS/1200-baud, or play `holdout_8s_loop.wav`.

Programme (load-bearing): **C0-v2 PASS → cadence CLOSED (runner retired) → transport contract frozen → C1 LGP.** Serial Studio is not on that path.

## Ship path

1. Already on disk: D19 observe/record; D20 runner dies before USB; D22 exclusive USB still binds; shuttle FAIL parked; this stamp OBSERVE/RECORD.
2. Remaining: leave Serial Studio parked. Do not repair the shuttle. Do not run `gate_c0_cadence_silicon.py`. C1 is Captain’s one full song, not an SS command session.
3. Who: agents observe/record only. Captain only for C1 look, or for a named physical Main-only USB reset (`K1-MAIN-RPL-USB-RESET-RX-GO`) if logging RX is wanted later.
4. Shipped for this contract when this file stamps OBSERVE/RECORD and no agent treats SS as cadence transport. C1 shipped stamp is `LGP_PERCEPTUAL_VALIDATED` in `docs/mir/GATE_C1.md` — separate gate.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Exclusive-port rule permanent; USB RX recovery off cadence path. |
| 2026-08-31 | agent:grok | D19: instrument not transport; cadence pyserial; shuttle demoted. |
| 2026-08-31 | agent:grok | Contract: SS acquisition, receipts authority, GATE vs OBSERVE. |
| 2026-08-31 | agent:grok | D20: cadence runner RETIRED so SS is never cadence transport; exclusive USB still binds. |
| 2026-08-31 | agent:grok | Dashboard: stop graphing clocks/masks; LED flags; 3D musical axes; envelope FFT of peak_scaled. |
