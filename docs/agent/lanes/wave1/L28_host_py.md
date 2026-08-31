STATUS: PASS
CLAIM: HOST.md training pin CPython 3.12.11 (`.python-version` = `3.12`) sits inside `pyproject.toml` `requires-python = ">=3.11,<3.14"`; Homebrew `/usr` 3.14.3 is banned by HOST.md and excluded by the upper bound.
EVIDENCE: `docs/HOST.md:16`; `.python-version:1`; `pyproject.toml:6`; `uv.lock:3` `>=3.11, <3.14`; `README.md:27` `uv sync --python 3.12`.
COMMAND: not executed; L28 is source-read only. Do not run `uv sync`. Do not play audio.
METHOD_RISK: HOST-ONLY. Range still allows 3.11 and 3.13; this lane did not probe installed interpreters.
NEXT: optional tighten `requires-python` to `>=3.12,<3.13` if lockstep with HOST pin is wanted; extras belong to L30.
PROOF: 3.12.11 satisfies `>=3.11` and `<3.14`. 3.14.3 fails `<3.14`. Pin ⊂ range; not a contradiction.
TEST: none this lane (docs vs manifest).
DOCTRINE: D22 L28; `docs/HOST.md`; do not use `/usr` 3.14 for this lab.
AUDIO: none played.
