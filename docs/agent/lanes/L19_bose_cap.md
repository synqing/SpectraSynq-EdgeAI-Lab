STATUS: PASS
CLAIM: 15-minute same-song kill is encoded. Module `SAME_SONG_LOOP_MAX_S = 15 * 60` (=900) in `scripts/gate_c0v2_silicon.py`; `BoseSession` consumes it. `test_same_song_loop_max_is_fifteen_minutes` exists. Not a class attribute named `BoseSession.SAME_SONG_LOOP_MAX_S`.
EVIDENCE: `scripts/gate_c0v2_silicon.py:69` `SAME_SONG_LOOP_MAX_S = 15 * 60`. `class BoseSession` at L139. Uses: `assert_alive` L187, `_expired` L196, `_run` deadline L199; kill prints L211/L219/L231. Test `tests/test_gate_c0v2.py:218–222` imports module const and `assert SAME_SONG_LOOP_MAX_S == 15 * 60`. D21 + AGENTS.md HARD FAIL `SAME_SONG_LOOP_MAX_15MIN`.
COMMAND: source-read only. Did not run pytest. Did not start ffplay. Did not open USB.
METHOD_RISK: HOST-ONLY. Arithmetic 15*60=900 is certain from source. Cap is wall-clock in `BoseSession._run` / `assert_alive`; this lane did not play a song so did not exercise the kill. Cadence CLOSED.
NEXT: none for L19. Keep D21 HARD FAIL. Do not reopen Cadence. Do not loop a song in the room.
PROOF: 15*60=900. Named test present. Offence (missing cap or missing test) not found — do not kill.
DOCTRINE: D21 SAME_SONG_LOOP_MAX_15MIN; AGENTS.md HARD FAIL; no 8 s room loop this lane.
AUDIO: none played.
