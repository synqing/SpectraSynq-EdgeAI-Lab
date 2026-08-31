---
abstract: "W4-L17 observe-only USB inventory. Two usbmodem nodes present. No port open. Cadence RETIRED."
---

# K1 USB present — observe only

HOST-ONLY inventory. Cadence silicon **CLOSED**. Runner `scripts/gate_c0_cadence_silicon.py` **RETIRED**. Exclusive USB: observe only. Serial Studio not stolen.

HARD FAIL: `SAME_SONG_LOOP_MAX_15MIN`. No 8 s loop. No flash. No pyserial.

STATUS: PASS — not `EMPTY-THIS-SHELL`

CLAIM: This Mac currently has **two** CDC `usbmodem` nodes and **zero** `usbserial` nodes. Captain’s “K1s are connected” matches the node names. Serial Studio’s same-day project backup names both as Espressif `USB JTAG/serial debug unit` (VID `303A` PID `1001`). This lane did not open a port, did not flash, did not call pyserial, did not bind `:7777`, and did not take the CDC from Serial Studio.

EVIDENCE:

Live `/dev` directory listing (this shell, `list_dir` on `/dev`, nodes only — no `open()`, no `lsof`, no pyserial):

Every `/dev/cu.*` (4):

| Node |
| --- |
| `/dev/cu.Bluetooth-Incoming-Port` |
| `/dev/cu.debug-console` |
| `/dev/cu.usbmodem12201` |
| `/dev/cu.usbmodem1401` |

Every `/dev/tty.*` that is not a pty slave letter-grid (`ttyp*` / `ttyq*` / … / `ttyw*`):

| Node |
| --- |
| `/dev/tty` |
| `/dev/tty.Bluetooth-Incoming-Port` |
| `/dev/tty.debug-console` |
| `/dev/tty.usbmodem12201` |
| `/dev/tty.usbmodem1401` |
| `/dev/ttys000` … `/dev/ttys013` (14 pts) |

Also present: `/dev/uart.debug-console` (not `cu`/`tty` USB).

usbmodem (every):

| cu | tty |
| --- | --- |
| `/dev/cu.usbmodem12201` | `/dev/tty.usbmodem12201` |
| `/dev/cu.usbmodem1401` | `/dev/tty.usbmodem1401` |

usbserial (every): **none**.

IOUSB names — `ioreg -p IOUSB` was **not** run in this shell (no process spawn onto CDC). Same-day Serial Studio 4.0.3 auto-backup (observe file only; not a port steal) stores QSerialPort `deviceId` strings that are the USB product / serial descriptors:

| portName | USB Product Name (`description`) | VID | PID | USB Serial Number | SS title |
| --- | --- | --- | --- | --- | --- |
| `cu.usbmodem12201` | `USB JTAG/serial debug unit` | `303A` | `1001` | `B4:3A:45:A5:87:90` | K1 Main RPL `9087A500` |
| `cu.usbmodem1401` | `USB JTAG/serial debug unit` | `303A` | `1001` | `B4:3A:45:A5:89:B4` | K1 Bench `B489A500` |

Source: `/Users/spectrasynq/Library/Application Support/Alex Spataru/Serial-Studio/backups/K1 Dual UART Observability-dfb79214/2026-08-31T13-59-10-678__auto.ssproj` (`takenAt` `2026-08-31T13:59:10Z`). Cursor Serial Monitor init logs the same day also enumerate both ports as `friendlyName=Espressif` `vid=303a` `pid=1001` (enumerate log, not an open by this agent).

Prior roster (not this listing): `docs/agent/lanes/LAUNCHED_W4.md` already named the same two nodes. HANDOFF last-verified Main RPL USB `B4:3A:45:A5:87:90` typically `/dev/cu.usbmodem12201`.

COMMAND: none. Directory list + read SS backup / Cursor enumerate logs. Do **not** `open` `/dev/cu.usbmodem*`. Do **not** pyserial. Do **not** `lsof`. Do **not** DTR/RTS/1200-baud. Do **not** `k1-flash`. Do **not** `scripts/gate_c0_cadence_silicon.py`. Do **not** talk `:7777`. Do **not** take Serial Studio’s CDC.

METHOD_RISK: HOST-ONLY. `/dev` names are this-shell fact. IOUSB product/serial strings are Serial Studio’s stored `deviceId`, not a live `ioreg` dump — if a cable moved after `13:59:10Z`, serial↔BSD name can swap (historically has). `list_dir` does not prove a process owns the CDC. Cadence stays CLOSED regardless of nodes present.

NEXT: Leave Serial Studio as observe/record owner. Do not open these ports from a HOST lane. C1 look does not need this agent on USB.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Created. Two usbmodem present; usbserial none; SS USB names observed, ports not opened. |
