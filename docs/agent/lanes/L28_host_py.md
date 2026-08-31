---
abstract: "L28 HOST-ONLY: HOST.md python pin vs pyproject requires-python + extras mismatch list. No USB, no audio."
---

# L28 — HOST.md vs pyproject python/extras

STATUS: PASS_WITH_GAPS (HOST-ONLY, docs-only). Pin ⊂ range; extras absent from HOST.md.
CLAIM: Training pin CPython **3.12.11** (HOST.md) sits inside `requires-python = ">=3.11,<3.14"`. Homebrew **3.14.3** is banned by HOST.md and excluded by `<3.14`. HOST.md names **zero** extras; `pyproject.toml` names four (`musdb`, `mir`, `dev`, `silicon`). Not an install contradiction. Gaps: range still allows 3.11 and 3.13; HOST.md does not record extras; README reproduce line only installs `mir`+`dev`.
EVIDENCE: `docs/HOST.md` L15–18; `.python-version` = `3.12`; `pyproject.toml` L6 `requires-python`, L9–18 core deps, L20–24 extras; `uv.lock` L3 `>=3.11, <3.14` + L4–7 resolution-markers `>=3.13` / `==3.12.*` / `<3.12`; `README.md` L27 `uv sync --python 3.12 --extra mir --extra dev`; D2 in `docs/DECISIONS.md` L16–18.
COMMAND: not executed. Source-read only. Do not `uv sync`. Do not play audio. Do not USB. Cadence CLOSED.
METHOD_RISK: HOST-ONLY file compare. Did not probe installed interpreters, did not open `.venv`, did not lock extras (L30 owns lock coverage). `.python-version` is `3.12` not `3.12.11`.
NEXT: optional (1) tighten `requires-python` to `>=3.12,<3.13` if lockstep with HOST pin is wanted; (2) add one HOST.md row listing the four extras and which the 2026-08-30 venv actually had. Do not invent the venv extra set without a probe. L30 owns lock vs extras.

## Mismatch list

| # | Axis | HOST.md | pyproject.toml | Verdict |
| --- | --- | --- | --- | --- |
| 1 | Training Python | CPython **3.12.11** via `uv` (cites `.python-version`) | `requires-python = ">=3.11,<3.14"` | **GAP not contradiction.** Pin is a subset. Manifest also allows **3.11** and **3.13**. `uv.lock` even has a `python_full_version >= '3.13'` marker. |
| 2 | `.python-version` vs HOST patch | HOST.md writes **3.12.11**; file on disk is `3.12` | no patch pin | **PATCH DRIFT** between HOST snapshot and the pin file HOST.md cites. Both still inside the range. |
| 3 | System `/usr` Python | Homebrew **3.14.3** — do not use | excluded by `<3.14` | **ALIGNED** (ban matches upper bound). |
| 4 | Extras inventory | **none named** (no `musdb`/`mir`/`dev`/`silicon`) | four: `musdb`, `mir`, `dev`, `silicon` | **HOST.md SILENT.** Manifest has extras HOST.md does not document. |
| 5 | Extra `musdb` | not mentioned | `musdb>=0.4.0`, `stempeg>=0.2.0` | **UNDOCUMENTED on HOST.md.** |
| 6 | Extra `mir` | not mentioned | `librosa>=0.10`, `matplotlib>=3.8`, `mir_eval>=0.7` | **UNDOCUMENTED on HOST.md.** README reproduce does install this extra. |
| 7 | Extra `dev` | not mentioned | `pytest>=8.0` | **UNDOCUMENTED on HOST.md.** README reproduce does install this extra. |
| 8 | Extra `silicon` | not mentioned | `pyserial>=3.5` | **UNDOCUMENTED on HOST.md.** README reproduce **omits** it. Extra is a pip extra, not a serial-port open. Cadence CLOSED. |
| 9 | Reproduce extras (adjacent README, not HOST.md) | HOST.md has no sync command | four extras in manifest | README L27: `--extra mir --extra dev` only. **musdb** and **silicon** are defined but not in the default sync line. |

Not extras, same pin-vs-floor pattern (do not treat as an extra mismatch): HOST.md torch **2.13.0** / torchaudio **2.11.0**; pyproject core `torch>=2.4`, `torchaudio>=2.4`. Snapshot ⊂ floor.

PROOF: `3.12.11` satisfies `>=3.11` and `<3.14`. `3.14.3` fails `<3.14`. HOST.md grep for extra names: zero hits. pyproject L20–24: four extras.
TEST: none this lane (docs vs manifest).
DOCTRINE: D22 L28; D2 Python 3.12 + uv; do not use `/usr` 3.14. SAME_SONG_LOOP_MAX_15MIN unused (no audio).
AUDIO: none played.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L28 mismatch list: HOST.md python pin vs pyproject range + four extras. |
