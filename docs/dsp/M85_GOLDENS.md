---
abstract: "Prepared host golden vectors for later Cortex-M85/Helium DSP comparison. No silicon numbers."
---

# M85 / Helium golden DSP (prepared, not executed on silicon)

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Titan answers two independent questions:

1. U55 learned semantics
2. **What does Cortex-M85 + Helium buy vs the current realtime MCU DSP?**

MIR work must not erase (2).

Host vectors (generate with `uv run python scripts/make_dsp_goldens.py`):

- rFFT magnitude of a known 2048-sample PCM
- Goertzel at 440 Hz
- Hann-windowed rFFT

When the board exists, run the **same PCM** through M85 kernels and diff.
No M85 latency/throughput claims before silicon.

Kernels to port later: FFT/GDFT, Goertzel, ACF/tempo, mel/frontend, feature extraction.
