---
abstract: "L39 HOST: test_serial_studio.py vs D19. Eight localhost mocks, ephemeral bind not :7777. Shuttle not reopened. Owned-USB raise is L38."
---

# L39 — test_serial_studio.py vs D19

HOST-ONLY source compare. Cadence CLOSED. No Serial Studio. No `:7777`. No USB. Do not repair the shuttle.

STATUS: PASS

CLAIM: `tests/test_serial_studio.py` matches D19. The module states cadence does not use the `:7777` shuttle. Eight tests cover parked TCP helpers on localhost **ephemeral** binds (port 0, never 7777) plus an unowned-path refuse. They do not call `open_k1_serial`, do not bind 7777, do not open `/dev/cu.usbmodem*`, and do not treat Serial Studio as cadence transport. They do not reopen or repair the shuttle.

EVIDENCE:
- D19 Chosen: SS observe/record, not transport; demote exclusive-USB command shuttle; cadence refuses SS-owned USB (`SERIAL_STUDIO_NOT_TRANSPORT`) and uses pyserial after release; exclusive CDC for command/reply; no multiplex. D18 Revisit superseded: cadence must not talk `:7777`. Source: `docs/DECISIONS.md` D19.
- Test module header: `tests/test_serial_studio.py:1` — “Cadence does not use the :7777 shuttle (D19).”
- Imports (`:10-22`): `SerialStudioBus`, `send_line`, `collect_frames`, `api_up`, `refuse_if_serial_studio_owns_usb`, `set_profile`, `SerialStudioPort`. **Zero** `open_k1_serial`.
- Eight functions: `test_source_id_maps_main_rpl_not_bench` (`:53`); `test_send_line_sets_gate_table_not_io_write_data` (`:63`); `test_collect_frames_joins_new_sequences_until_marker` (`:119`); `test_api_up_false_on_closed_port` (`:177`); `test_refuse_if_serial_studio_owns_usb_allows_unowned_path` (`:181`); `test_collect_frames_counts_sequence_gaps` (`:185`); `test_port_refuses_binary_prsm` (`:244`); `test_set_profile_gate_turns_poll_timers_off` (`:253`).
- Mock binds: `srv.bind(("127.0.0.1", 0))` at `:28`, `:69`, `:129`, `:196`, `:259`. Not 7777.
- `test_api_up_false_on_closed_port` uses `api_up(port=1)` — does not probe live Serial Studio on 7777.
- `test_send_line_sets_gate_table_not_io_write_data` asserts `"io.writeData" not in cmds` (`:113`). Direct `io.writeData` is the source-0 bench write the module itself bans (`src/edgeai/serial_studio.py:303-305`).
- Refuse: `:181-182` calls `refuse_if_serial_studio_owns_usb("/dev/does-not-exist-ss-refuse-test")` — allow-unowned only. Implementation: `src/edgeai/serial_studio.py:140-147` (`SERIAL_STUDIO_NOT_TRANSPORT`).
- Parked shuttle in production module (not exercised by these tests): `shuttle_roundtrip_proven` “Cadence does not wait… shuttle is demoted (D19)” (`:150-153`); `open_k1_serial` “Legacy :7777 shuttle opener. Cadence must not call this (D19)” (`:571-577`). `DEFAULT_PORT = 7777` (`:22`) remains on `SerialStudioBus` / `api_up` defaults; tests override the port.
- Sister lanes: L17 docs PASS; L38 GAP (owned-raise untested); L29 already ran the eight tests as HOST units. This lane did not re-run pytest.

COMMAND: none. Do not pytest this lane (L29 already inventoried). Do not open Serial Studio. Do not bind or connect `127.0.0.1:7777`. Do not touch `/dev/cu.usbmodem*`. Do not call `open_k1_serial`. Do not repair the shuttle. Do not `K1-MAIN-RPL-USB-RESET-RX-GO`.

METHOD_RISK: HOST-ONLY file compare. No USB. No live API. Tests still **unit** the demoted TCP helpers (`SerialStudioBus` / `send_line` / `collect_frames` / `set_profile`); that is parked-code coverage, not cadence reopen. Raise-path `holder_is_serial_studio` True → `SERIAL_STUDIO_NOT_TRANSPORT` is **untested here** (allow-unowned on a missing path cannot fire the D19 raise). That gap is L38, not a D19 mismatch in this file. `api_up()` / `SerialStudioBus()` without a port still default to 7777 in `serial_studio.py`; tests never use that default. This lane did not run pytest, did not bind 7777, did not play audio.

NEXT: Leave shuttle parked. Do not add shuttle-repair tests. Owned-USB raise mock (`holder_is_serial_studio` True) stays L38 optional HOST unit. Cadence stays CLOSED.

PROOF: D19 demotes shuttle and requires refuse-SS-USB + pyserial after release. Tests never call `open_k1_serial`, never bind 7777, never send `io.writeData`, never open usbmodem. Allow-path refuse on a missing device cannot fire the D19 raise.

TEST: eight functions in `tests/test_serial_studio.py` (source_id, send_line, collect_frames×2, api_up closed, refuse unowned, PRSM, set_profile). Zero `open_k1_serial`. Zero bind-7777. Zero raise-on-owned-USB.

DOCTRINE: D19 instrument not transport; D18 Revisit superseded; D20 cadence CLOSED; L17 docs PASS; AGENTS.md observe/record only; SAME_SONG_LOOP_MAX_15MIN unused.

AUDIO: none played.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L39: test_serial_studio.py vs D19 PASS; ephemeral mocks; shuttle not repaired. |
