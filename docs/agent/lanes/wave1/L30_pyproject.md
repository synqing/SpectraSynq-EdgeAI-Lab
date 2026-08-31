---
abstract: "L30 HOST-ONLY: four pyproject extras (musdb, mir, dev, silicon) are all covered by uv.lock. No USB, no audio."
---

# L30 — pyproject extras vs uv.lock

STATUS: PASS (HOST-ONLY lock coverage).
CLAIM: extras `musdb` (`musdb>=0.4.0`, `stempeg>=0.2.0`), `mir` (`librosa>=0.10`, `matplotlib>=3.8`, `mir_eval>=0.7`), `dev` (`pytest>=8.0`), `silicon` (`pyserial>=3.5`) — lock `provides-extras` matches; all four resolved.
EVIDENCE: `pyproject.toml` L20–24; `uv.lock` rev 3 `provides-extras = ["musdb", "mir", "dev", "silicon"]` + `[package.optional-dependencies]` L1576–1612.
COMMAND: none. Source-read only. No `uv sync`. No USB. No audio. No 8 s loop.
LOCKED: musdb 0.4.3, stempeg 0.2.6, librosa 0.11.0 (<3.12) / 1.0.0 (>=3.12), matplotlib 3.11.1, mir-eval 0.8.2, pytest 9.1.1, pyserial 3.5.
METHOD_RISK: lock includes extras; they are not default deps. `silicon` is pyserial, not a serial-port open. Cadence CLOSED.
NEXT: none this lane. Install only via `uv sync --extra <name>` when a HOST lane needs it.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L30 contract: four extras covered by uv.lock. |
