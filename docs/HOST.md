---
abstract: "Host/platform assumptions. M4 Pro, MPS, CPython 3.12.11. Four uv extras musdb/mir/dev/silicon. silicon extra is pyserial, not a port. Cadence CLOSED. Demucs is not an extra. RUHMI is not this host."
---

# Host assumptions

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

**Cadence silicon CLOSED.** This file does not open `/dev/cu.usbmodem*`, Serial Studio, or Cadence.

Recorded 2026-08-30 on this workstation. Re-probe with `uv run edgeai-host-probe`.

| Item | Value |
| --- | --- |
| Machine | Apple MacBook Pro, M4 Pro (arm64) |
| OS | macOS 26.1 (Build 25B78) |
| Default `/usr` python | Homebrew CPython **3.14.3** — **do not use for this lab** |
| Training python | CPython **3.12.11** via `uv` (`.python-version` is `3.12`; patch pin is 3.12.11) |
| Accelerator | Apple MPS — **confirmed available and used** |
| torch / torchaudio | 2.13.0 / 2.11.0 in the lab venv |
| Package manager | `uv` 0.9.8 |
| Docker | 28.5.2 client present; **daemon was not running** on 2026-08-30 so a local RUHMI image was not built |
| RUHMI/MERA | not installed on macOS; x86_64 manylinux cp310 wheel only. **PRE-SILICON C99** later produced on GitHub Actions (Ubuntu), not on this Mac. |

Device selection in code: `mps` if available, else `cuda`, else `cpu`. Export always runs on CPU.

CUDA/cloud NVIDIA is allowed later if a measured reason appears. Do not buy an NVIDIA GPU to start.

## Optional extras (HOST packaging)

`pyproject.toml` `[project.optional-dependencies]` names **four** extras. `uv.lock` `provides-extras` matches. They are **not** on the default `dependencies` list. Default `uv sync` without `--extra` leaves them out. `README.md` reproduce line installs `--extra mir --extra dev` only.

**Demucs is not an extra.** No `demucs` extra, no Demucs pin in core deps.

| Extra | Specifiers | Meaning |
| --- | --- | --- |
| `musdb` | `musdb>=0.4.0`, `stempeg>=0.2.0` | HOST MUSDB readers |
| `mir` | `librosa>=0.10`, `matplotlib>=3.8`, `mir_eval>=0.7` | HOST MIR/plot |
| `dev` | `pytest>=8.0` | HOST tests |
| `silicon` | `pyserial>=3.5` | **PyPI package only.** Installing this extra is **not** a serial-port open, not ON-SILICON, not Cadence, not USB-CDC ownership. |

Install when needed: `uv sync --python 3.12 --extra musdb --extra mir --extra dev --extra silicon`. `--extra silicon` is **not** permission to open the K1 port. Cadence stays CLOSED.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Host probe snapshot. |
| 2026-08-31 | agent:edgeai | GHA, not this Mac, produced RUHMI C99. |
| 2026-08-31 | agent:grok-build | Recorded four extras musdb/mir/dev/silicon; silicon=pyserial not a port; Demucs not an extra; Cadence CLOSED. |
