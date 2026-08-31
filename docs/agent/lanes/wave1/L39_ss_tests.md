STATUS: PASS
CLAIM: `tests/test_serial_studio.py` matches D19. Module states cadence does not use :7777. Eight tests are localhost mocks (ephemeral bind, not port 7777) of parked TCP helpers plus unowned-path refuse. They do not reopen the shuttle, USB, or cadence.
EVIDENCE: `tests/test_serial_studio.py:1`; refuse allow-only `181-182`; mocks `68/129/196/259`; `src/edgeai/serial_studio.py:140-147` `SERIAL_STUDIO_NOT_TRANSPORT`; `150-153` shuttle demoted; `571-577` `open_k1_serial` legacy; `docs/DECISIONS.md` D19.
COMMAND: none. Do not pytest this lane (L29). Do not open Serial Studio. Do not talk :7777. Do not touch `/dev/cu.usbmodem*`. Do not repair the shuttle.
METHOD_RISK: HOST-ONLY source compare. No USB. No live API. Raise-path for `SERIAL_STUDIO_NOT_TRANSPORT` is untested here (`holder_is_serial_studio` never forced True).
NEXT: optional unit test that refuse raises when SS holds USB (mock `lsof`); L38 owns exclusive-port. Leave shuttle parked.
PROOF: D19 demotes shuttle and requires refuse-SS-USB + pyserial after release. Tests never call `open_k1_serial`, never bind 7777, never `io.writeData`. Allow-path refuse on a missing device cannot fire the D19 raise.
TEST: eight functions in `tests/test_serial_studio.py` (source_id, send_line, collect_frames×2, api_up, refuse unowned, PRSM, set_profile). No raise-on-owned-USB case.
DOCTRINE: D19 instrument not transport; D18 Revisit superseded; D20 cadence CLOSED; L17 docs PASS; AGENTS.md observe/record only.
AUDIO: none played.
