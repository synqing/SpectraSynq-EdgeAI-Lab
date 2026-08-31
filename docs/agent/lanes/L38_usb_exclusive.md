---
abstract: "L38 HOST: refuse_if_serial_studio_owns_usb tests. Allow-unowned exists. Owned-raise untested. No usbmodem. Cadence CLOSED."
---

# L38 — exclusive-port tests

HOST-ONLY source. Cadence CLOSED. No USB. Do not open `/dev/cu.usbmodem*`. Do not pytest live CDC. HARD FAIL `SAME_SONG_LOOP_MAX_15MIN` unused (no audio).

STATUS: GAP (HOST-ONLY)

CLAIM: exclusive-port tests cover only the unowned path. `refuse_if_serial_studio_owns_usb` on a missing fake device returns; the Serial Studio hold → `SERIAL_STUDIO_NOT_TRANSPORT` raise is untested. No test opens usbmodem.

EVIDENCE:
- Guard: `src/edgeai/serial_studio.py:131-147`. `holder_is_serial_studio` runs `lsof -n -P <dev>` and matches `"Serial-St"` or `"Serial Studio"`. `refuse_if_serial_studio_owns_usb` raises `SerialStudioError` with `SERIAL_STUDIO_NOT_TRANSPORT` only if that is True. D19 exclusive-port rule in the docstring.
- Sole test: `tests/test_serial_studio.py:181-182` `test_refuse_if_serial_studio_owns_usb_allows_unowned_path` calls `refuse_if_serial_studio_owns_usb("/dev/does-not-exist-ss-refuse-test")` with no assert. Missing path → `lsof` empty → holder False → return. Zero `pytest.raises`. Zero `monkeypatch`. Zero `holder_is_serial_studio` tests. Eight functions in that file; seven are TCP mocks / PRSM / source_id, not USB.
- Cadence caller (not a test; Cadence CLOSED): `scripts/gate_c0_cadence_silicon.py:509` refuse before flash; `:517-521` extra `holder_is_serial_studio` refuse-flash; `:526` refuse after `wait_port`. This lane did not run that script.
- Doctrine: `docs/DECISIONS.md` D19 (refuse SS-owned USB; exclusive port permanent); `docs/mir/SERIAL_STUDIO.md` Exclusive port + `SERIAL_STUDIO_NOT_TRANSPORT`; `AGENTS.md` Serial Studio observe/record; no multiplex.
- `tests/` has no `usbmodem` string. No live CDC pytest.

COMMAND: none. HOST read only. Do not pytest live CDC. Do not open `/dev/cu.usbmodem*`. Do not `lsof` a live K1 port. Do not run `gate_c0_cadence_silicon.py`. Cadence CLOSED.

METHOD_RISK: HOST-ONLY. Allow path runs `lsof` on a non-existent path (vacuous pass). Owned-raise needs a monkeypatch of `holder_is_serial_studio` (or stubbed `lsof` stdout containing `Serial Studio`), not live Serial Studio and not a USB steal. `gate_c0_silicon.py` / `gate_c0v2_silicon.py` open pyserial without this refuse — out of this lane’s test census; do not reopen them. `open_k1_serial` (`serial_studio.py:571-593`) is legacy :7777, not the exclusive-port unit.

NEXT: optional HOST unit: patch holder True → `SerialStudioError` contains `SERIAL_STUDIO_NOT_TRANSPORT`. L39 owns the rest of `test_serial_studio.py` vs D19. Do not USB-test. Leave cadence closed.

PROOF: one `refuse_if_serial_studio_owns_usb` test; zero `holder_is_serial_studio` tests; zero `usbmodem` in `tests/`; raise-on-owned-USB untested.

TEST: `tests/test_serial_studio.py::test_refuse_if_serial_studio_owns_usb_allows_unowned_path` (source-read; not executed this lane).

DOCTRINE: D19 exclusive USB; AGENTS.md no multiplex; Serial Studio observe/record; D20 cadence CLOSED; D22 L38.

AUDIO: none played.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Created. L38: exclusive-port tests GAP; allow-unowned only; no usbmodem. |
| 2026-08-31 | agent:grok | Re-derived HOST: SS-owned raise still untested; one allow-unowned test; cadence refuse not a test. |
