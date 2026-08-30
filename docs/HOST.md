---
abstract: "Host/platform assumptions for SpectraSynq-EdgeAI-Lab training. M4 Pro, MPS, Python 3.12. RUHMI is not this host."
---

# Host assumptions

Recorded 2026-08-30 on this workstation. Re-probe with `uv run edgeai-host-probe`.

| Item | Value |
| --- | --- |
| Machine | Apple MacBook Pro, M4 Pro (arm64) |
| OS | macOS 26.1 (Build 25B78) |
| Default `/usr` python | Homebrew CPython **3.14.3** — **do not use for this lab** |
| Training python | CPython **3.12.11** via `uv` (`.python-version`) |
| Accelerator | Apple MPS — **confirmed available and used** |
| torch / torchaudio | 2.13.0 / 2.11.0 in the lab venv |
| Package manager | `uv` 0.9.8 |
| Docker | 28.5.2 client present; **daemon was not running** on 2026-08-30 so a local RUHMI image was not built |
| RUHMI/MERA | not installed on macOS; x86_64 manylinux cp310 wheel only. **PRE-SILICON C99** later produced on GitHub Actions (Ubuntu), not on this Mac. |

Device selection in code: `mps` if available, else `cuda`, else `cpu`. Export always runs on CPU.

CUDA/cloud NVIDIA is allowed later if a measured reason appears. Do not buy an NVIDIA GPU to start.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Host probe snapshot. |
| 2026-08-31 | agent:edgeai | GHA, not this Mac, produced RUHMI C99. |
