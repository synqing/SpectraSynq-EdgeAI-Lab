---
abstract: "L38 HOST: refuse_if_serial_studio_owns_usb tests. Allow-unowned exists. Owned-raise untested. No usbmodem."
---

STATUS: GAP (HOST-ONLY)
CLAIM: exclusive-port tests cover only the unowned path. `refuse_if_serial_studio_owns_usb` on a missing fake device returns; the Serial Studio hold → `SERIAL_STUDIO_NOT_TRANSPORT` raise is untested. No test opens usbmodem.
EVIDENCE: `tests/test_serial_studio.py:181-182` `test_refuse_if_serial_studio_owns_usb_allows_unowned_path`; `src/edgeai/serial_studio.py:131-147` `holder_is_serial_studio` / `refuse_if_serial_studio_owns_usb`; `scripts/gate_c0_cadence_silicon.py:509` and `:526`.
COMMAND: none. Do not pytest live CDC. Do not open `/dev/cu.usbmodem*`. Cadence CLOSED.
METHOD_RISK: HOST-ONLY. Allow path runs `lsof` on a non-existent path. Owned path needs a monkeypatch of `holder_is_serial_studio`, not live Serial Studio or a USB steal.
NEXT: optional HOST unit: patch holder True → `SerialStudioError` contains `SERIAL_STUDIO_NOT_TRANSPORT`. L39 owns the rest of `test_serial_studio.py` vs D19. Do not USB-test.
PROOF: one `refuse_if_serial_studio_owns_usb` test; zero `holder_is_serial_studio` tests; zero `usbmodem` in `tests/`.
TEST: `tests/test_serial_studio.py::test_refuse_if_serial_studio_owns_usb_allows_unowned_path` (not executed this lane).
DOCTRINE: D19 exclusive USB; AGENTS.md no multiplex; Serial Studio observe/record.
AUDIO: none played.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Created. L38: exclusive-port tests GAP; allow-unowned only; no usbmodem. |
