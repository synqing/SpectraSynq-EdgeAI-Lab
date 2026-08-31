---
abstract: "L30 HOST-ONLY: pyproject extras musdb/mir/dev/silicon equal uv.lock provides-extras. silicon extra is pyserial>=3.5, not a serial-port open."
---

# L30 — pyproject extras vs uv.lock

STATUS: PASS (HOST-ONLY). Cadence CLOSED. No USB.

CLAIM: `[project.optional-dependencies]` names `{musdb, mir, dev, silicon}` equal `uv.lock` `provides-extras` on the editable `spectrasynq-edgeai-lab` 0.1.0 package. Each extra’s pins in `pyproject.toml` match `[package.metadata] requires-dist` extra markers. None of the four extras sit on the default `dependencies` list. Extra `silicon` is the PyPI wheel `pyserial>=3.5` (locked 3.5). Installing or locking that extra does not open `/dev/cu.usbmodem*`, Serial Studio, or Cadence.

EVIDENCE:

- `pyproject.toml` L20–24 — four extras, no fifth:
  - `musdb = ["musdb>=0.4.0", "stempeg>=0.2.0"]`
  - `mir = ["librosa>=0.10", "matplotlib>=3.8", "mir_eval>=0.7"]`
  - `dev = ["pytest>=8.0"]`
  - `silicon = ["pyserial>=3.5"]`
- `pyproject.toml` L9–18 default deps: torch, torchaudio, numpy, scipy, soundfile, onnx, onnxruntime, pyyaml. No musdb, librosa, pytest, pyserial.
- `uv.lock` L1–2 `version = 1`, `revision = 3`; L3 `requires-python = ">=3.11, <3.14"`.
- `uv.lock` L1560–1612 editable package `spectrasynq-edgeai-lab` 0.1.0:
  - default `dependencies` L1563–1574 = the eight runtime names (numpy split by `<3.12` / `>=3.12`).
  - `[package.optional-dependencies]` L1576–1592: `dev`→pytest; `mir`→librosa+matplotlib+mir-eval; `musdb`→musdb+stempeg; `silicon`→pyserial only.
  - `[package.metadata] requires-dist` L1595–1611 extra markers: `extra == 'mir'|'musdb'|'silicon'|'dev'` with the same specifiers as pyproject (PEP 503: `mir_eval` → `mir-eval`).
  - L1612 `provides-extras = ["musdb", "mir", "dev", "silicon"]`.
- Locked extra roots (PyPI, not a device): musdb 0.4.3 (`uv.lock` L782–783); stempeg 0.2.6 (L1615–1616); librosa 0.11.0 when `python_full_version < '3.12'` (L513–517) and 1.0.0 when `>= '3.12'` (L540–546); matplotlib 3.11.1 (L638–639); mir-eval 0.8.2 (L689–690); pytest 9.1.1 (L1294–1295); pyserial 3.5 (L1285–1286).
- `src/spectrasynq_edgeai_lab.egg-info/requires.txt` extras sections `[dev]`, `[mir]`, `[musdb]`, `[silicon]` match pyproject.
- Other lock `[package.optional-dependencies]` at L258 is `cuda-toolkit`, not this project.

COMMAND: none this lane. Source-read only. Did not run `uv sync`, `uv lock`, pytest, pyserial, or any serial open. No USB. No audio. No 8 s loop.

METHOD_RISK: HOST-ONLY lock coverage. `provides-extras` means the lock *can* resolve those extras; it does not mean they are installed in `.venv`. Default `uv sync` without `--extra` / `--all-extras` leaves them out. Extra name `silicon` is a packaging label for pyserial — not ON-SILICON, not Cadence, not a port owner. This lane did not import pyserial or enumerate `/dev/cu.*`. Cadence silicon stays CLOSED.

NEXT: none this lane. HOST consumers install with `uv sync --extra <name>` when needed (`musdb` / `mir` / `dev` / `silicon`). Do not treat `--extra silicon` as permission to open the K1 USB-CDC port. Exclusive-port tests stay L38; Serial Studio vs D19 stays L39.

PROOF: set(`pyproject` extras) == set(`provides-extras`) == `{musdb, mir, dev, silicon}` (order in lock: musdb, mir, dev, silicon). Seven extra-root pins in requires-dist match the seven strings in pyproject L21–24. silicon member count in lock optional-deps = 1 (`pyserial`). pyserial is absent from default dependencies.

TEST: none this lane (manifest vs lock). L29 already ran HOST pytest; this lane did not.

DOCTRINE: D22 L30; AGENTS.md Cadence CLOSED / no USB multiplex; `SAME_SONG_LOOP_MAX_15MIN` unused (no audio).

AUDIO: none played.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L30: four extras covered by uv.lock; silicon extra is pyserial not a port. |
| 2026-08-31 | agent:grok-build | Re-derived pyproject L20–24 vs lock revision 3 provides-extras + optional-deps. |
