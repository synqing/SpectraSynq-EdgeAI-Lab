---
abstract: "Serial Studio is the D24 universal passive observability sidecar. The live v1 project is frozen for replay; the separately named v2 follows K1_SERIAL_STUDIO_CANON. Cadence remains CLOSED and its runner RETIRED."
---

# Serial Studio × EdgeAI-Lab

> **Current authority (D24, 2026-09-01):** `docs/K1_SERIAL_STUDIO_CANON/` and
> `docs/serial-studio/ADR-001-observability-sidecar.md` govern new work. The live
> v1 project and its 3D/FFT/LED layout are frozen replay history; they are not the
> v2 information architecture. Do not overwrite v1. The separately named v2 is
> generated at
> `tools/serial-studio/projects/K1-Dual-UART-Observability-v2.ssproj`.

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

## Frozen v1 dashboard wiring (historical replay only, 2026-08-31)

This section records the v1 repair and remains load-bearing for old sessions.
Its “keep the widget” instruction means preserve the v1 artefact; it does not
require v2 to reproduce an instrument that does not answer a current engineering
question. V2 has no FFT until sampling cadence is proven and no 3D or transient
event lamps on Mission Control. Its workspaces are defined by the D24 canon.

The UART is not the bug. The live `.ssproj` was plotting **all 21 parser slots plus clocks/bitmasks on one Y axis** (update_mask ~2e6), so BPM/conf/peak vanished. LED panel was bound to `unused_slot_17`. 3D plots 2/3 read parser indices 21–26 that do not exist. “New FFT Plot” was an LED+FFT dataset on slot 27 (empty). There is **no audio FFT on the wire** — FFT is KissFFT of `peak_scaled` (envelope), 133 Hz, 256 samples.

Live file: `~/Documents/Serial Studio/Projects/K1 Dual UART Observability.ssproj`.
Backup: `K1 Dual UART Observability.bak-1788185916.ssproj`.

Now:
- Multiplot: BPM, conf, lock, beat, onset, bass, silence, AGC, peak, energy, novelty only.
- LED: lock / beat / onset / bass / silence (`ledHigh=0.5`).
- 3D plots restored as a tempo-phase orbit (not bars). Parser v1.2 appends `phase` (slot 22, on the wire) plus `orbit_x`/`orbit_y` (slots 23–24, `peak_scaled * cos/sin(2π phase)`). 3D-1 Bench X/Y=orbit Z=energy; 3D-2 Main same; 3D-3 Bench X/Y=orbit Z=conf. Dataset tags `widget: x|y|z`. Interpolation on, auto-center on.
- **Keep the widget.** Do not swap plot3d for barpanel because the first bind was a scribble. New parser slots must also exist as `graph: true` on the Bench/Main multiplot or Plot3D uniqueIds keep the old channel (Peak). After `project.loadJson`, call `project.activate`. Scar: `docs/agent/SESSION_SCAR_2026-08-31_SSA_SWARM.md`.
- Envelope FFT: `peak_scaled` index 9, `fft=true`, `led=false`.
- Web View: `K1 Live Web View` → `http://127.0.0.1:8765/` (read-only bridge of `dashboard.getData`). Dual Bench/Main: BPM, lock/beat/onset/bass/silence, peak/energy/novelty. Start `tools/serial-studio/webview/bridge.py`. No UART writes.

## What this is not

Not C0-v2 (already `ON_SILICON_PIXEL_VALIDATED`). Not C1. Not a firmware bug. Not a reason to trash Historian/parser work. Not a green light to launch Serial Studio, bind `127.0.0.1:7777`, `lsof` a live K1 port, DTR/RTS/1200-baud, or play `holdout_8s_loop.wav`.

Programme (load-bearing): **C0-v2 PASS → cadence CLOSED (runner retired) → transport contract frozen → C1 LGP.** Serial Studio is not on that path.

## V2 promotion status

- Project-config safety: **PROVEN** by generated v2, semantic lint, zero configured writes, and the Mission Control structural invariant.
- Application-source safety: **PROVEN** at Serial Studio commit `b47031d13b9226687e7b3c93d68d74921e40e058`.
- Bounded GPL runtime policy: **PASS**. The identified GPL binary served TCP/gRPC reads and refused command/raw writes with `OBSERVE_ONLY_PROJECT`; test instances were loopback-only, network/update-free, serial-FD-free, and project-write-free.
- Full Pro and installed-binary runtime: **OPEN**. GPL removes the second source and leaves four expected Pro-edition workspace refs unresolved, so it cannot prove the complete instrument.
- Session 19: **INVALID / diagnostic fixture forever**. Its real two-source bytes do not overcome embedded-project drift.
- Tier C passive HIL: **OPEN**. No current device RX, Historian, or zero-host-TX claim is made here.

## Optional Audio Reference v2.1

D27 adds a host Audio Reference / Stimulus Witness without changing the base
two-UART project. The default profile remains `PASSIVE_DUAL_UART`. The separate
`PASSIVE_DUAL_UART_AUDIO_REF` profile can add Serial Studio Pro Audio source 2
only from an exact saved binding. It is currently `BLOCKED_UNBOUND`: this host
has no admitted virtual loopback input and no frozen Source C binding.

`tools/serial-studio/audio_reference_validate.py` compares strict Audio CSV to
a known WAV without normalisation, DC removal, dither, repair or format
inference. `HOST_AUDIO_REFERENCE_TIME` is not K1 device time. Even a profile-
scored PASS validates only the named host-capture contract; it does not prove
the K1 microphone/PDM/PCM path or acoustic delivery. See
`docs/serial-studio/ADR-002-host-audio-reference.md`.

The bounded runtime receipt is `tools/serial-studio/projects/tier-b-gpl-policy.v1.json`.

## Ship path

1. Build commit `b47031d13b9226687e7b3c93d68d74921e40e058` as Serial Studio Pro and bind tag, configuration, source commit, and binary SHA-256.
2. Repeat Tier B on that Pro binary: two sources, all six workspaces, zero dangling refs, Mission Control one-Web-View invariant, local fonts, deterministic reload, and every TCP/gRPC/raw egress refusal.
3. Install and re-hash that exact Pro binary, then run Tier C passive HIL with identity-qualified Bench/Main ingress, parser and Historian progression, an independent zero host-to-DUT byte witness, clean session close, closed snapshot, and embedded-project equality.
4. Only after those receipts pass, stamp `K1_SERIAL_STUDIO_OBSERVABILITY_V2=PASS` and enable it in applicable workflows as a passive sidecar. It must never become a prerequisite or regain command/transport authority.
5. Separately, install and characterise a loopback input, freeze its Pro-saved Source C binding, build the fail-closed Audio identity patch into an identified Pro binary, and validate host Audio capture before admitting `PASSIVE_DUAL_UART_AUDIO_REF`.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-09-01 | Codex | Bound Tier A and GPL Tier B policy proof; left Pro, installed-binary, and passive-HIL promotion explicitly open. |
| 2026-09-01 | Codex | Marked v1 dashboard wiring as frozen replay history; D24 canon now governs separately named v2. |
| 2026-09-01 | agent:grok | Keep-the-widget; Plot3D needs multiplot-subscribed slots. |
| 2026-08-31 | agent:grok | 3D restored: tempo-phase orbit from v1.2 parser slots 22–24. Bars gone. |
| 2026-08-31 | agent:grok | Exclusive-port rule permanent; USB RX recovery off cadence path. |
| 2026-08-31 | agent:grok | D19: instrument not transport; cadence pyserial; shuttle demoted. |
| 2026-08-31 | agent:grok | Contract: SS acquisition, receipts authority, GATE vs OBSERVE. |
| 2026-08-31 | agent:grok | D20: cadence runner RETIRED so SS is never cadence transport; exclusive USB still binds. |
| 2026-08-31 | agent:grok | Dashboard: stop graphing clocks/masks; LED flags; 3D musical axes; envelope FFT of peak_scaled. |
