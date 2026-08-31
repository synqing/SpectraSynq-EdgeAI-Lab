---
abstract: "C0 2026-08-31 FAIL INVALID_TEMPORAL_EXECUTION. Two-clock runner retired. Successor GATE_C0V2.md. Do not overwrite artifacts/gate_c0/."
---

# Gate C0 — silicon inject + dump path (recon)

**Status:** Silicon run **FAIL — INVALID TEMPORAL EXECUTION** 2026-08-31. Receipt `artifacts/gate_c0/C0_RESULT.json`. Two-clock runner **retired**. Successor [GATE_C0V2.md](GATE_C0V2.md). **Not C0 PASS.** Captain is not the LED validator.

Binding stays exact: `source_share × WaveformTempo × head_position`.

Host extra-DoF (P3-C): A = constant mid gain, B = mix energy, D = oracle share; `extra_gain` maps frozen 0–1 → **[0.62, 1.0]** and multiplies **both** `waveform_peak_scaled` and the 12-bin chroma (`scripts/musdb18_p3c.py`, `src/edgeai/mir/host_chroma.py`). Scorer: `src/edgeai/mir/p3c_quant.py` (partial r of upper-half head vs share | mix). Floor: holdout Δ ≥ **0.15** and ≥ ~70% of native-rate Δ (`docs/mir/GATE_C.md`). HOST holdout Δ was **0.63**, 9/9 (`docs/mir/P3C_QUANT.json`).

## 1. Candidate paths (shortest first)

| Rank | Path | Already in source? | Drives the binding lever? | Blocked by |
| --- | --- | --- | --- | --- |
| **1** | USB-CDC **PRSM** 34-byte frames → authored snapshot `peak_scaled` = Prim8 pressure → Waveform Tempo draw position | Yes (`audio/k1_prsm.*`, `audio/k1_authored_source.*`, `.ino` one-writer publish, `scripts/agent/k1_authored_silicon_proof.py` packer) | **Yes for head_position** (draw `amp = peak`). **No for chroma×gain** | Named **flash GO** of a probe that has **PRSM + `K1_RENDER_TRACE_V1`**. Current product flashes reject `:rtrace_*`. Live USB port this session: **NOT_VERIFIED** |
| 2 | Same PRSM inject, dump via some other LED harvest | Same inject | Same lever | No second dump that is already the rtrace ring. Do not invent a tap. Do not ask Captain to look at the plate |
| 3 | USB-audio UAC PCM of mix vs stems | Source exists as **diagnostic** `k1_usb_audio_mac_probe` only; product Main RPL is **UAC-absent** (`docs/hardware/device-build-registry.md`) | **No** — that retunes the whole DSP, not P3-C extra-DoF on peak+chroma | Wrong experiment. Restored off. Not C0 |
| 4 | Host `k1_render_host.py` / `render_replay` | Yes | Yes, already HOST PASS | **HOST-ONLY.** Not `ON_SILICON_PIXEL_VALIDATED` |

**HARD STOP** (no inject without production **effect** edits): **not triggered.** Waveform Tempo already reads `max(snap.peak_scaled, waveform_peak_scaled)` and paints at `waveform_upper_half_source_position(amp)`. PRSM already writes `snap.peak_scaled`. No edit of `light_mode_waveform_tempo.cpp` is required.

Do **not** flash `lane/colourlab-bench` dirt. Do **not** revert or commit it. Do **not** invent a sibling worktree.

## 2. Can authored drive peak + chroma like host `extra_gain`?

**Peak / head: yes, with one operational caveat.**  
**Chroma × gain: no.** That is acceptable for this binding because the lever is **head position**, not hue.

[FACT] Prim8 map (`k1_authored_map_prim8`): pressure → `vu_level`, `peak_scaled`, `spectral_energy`; impact → `novelty`; mass/momentum/texture → band energies. Hz must be **30–240** or the frame is rejected. Freshness **50 ms**.

[FACT] Publish (`.ino`): authored snapshot copies those scalars, sets `chroma_strength = 0`, does **not** write the global `waveform_peak_scaled`. Core-1 **zeros `chromagram_smooth`** while authored is fresh (palette-only Ember rule). Drop-cut scale forced to 1.

[FACT] Waveform Tempo draw: `peak = clamp01(max(snap.peak_scaled, waveform_peak_scaled))`; `pos = waveform_upper_half_source_position(peak)` then mirror. Colour: `effect_palette_or_chroma_colour`; if chroma is black and peak ≥ 0.02, **peak-seeded fallback**.

[FACT] Host P3-C: `waveform_peak = extra_gain(...)` **and** `chroma * extra_gain`. Host also freezes tempo at 120 BPM in the harness stub (`k1_render_host.py`).

[INFERENCE] For C0 head_position, pack `prim8[0] = round(extra_gain * 65535)` (A/B/D series). Leave other Prim8 at values that keep presence (`peak ≥ 0.02`, not the all-zero silence latch). Colour will be fallback, not host chroma×gain. Luma-weighted centroid can therefore differ from HOST absolute r; the **delta D vs B after partialling mix** is still the pass law.

[FACT] Tempo uses `fmax(snap.peak_scaled, waveform_peak_scaled)`. Live I2S still updates the global even when snapshot updates are suppressed. If the mic peak exceeds authored pressure, extra-DoF is swamped. Operational control: quiet room / no playback. Do not edit the effect to paper over that.

## 3. Dump tool and env

[FACT] Serial: `:rtrace_arm=<seconds 1..600>[,<every_n 1..100>]`, `:rtrace_status=1`, `:rtrace_dump=1` (`visual/k1_render_trace.{h,cpp}`). Compiles to **nothing** without `-DK1_RENDER_TRACE_V1`.

[FACT] Shipping `k1_main_rpl_im69d` must **not** carry that flag. Registry: Main RPL `9087A500` / USB `B4:3A:45:A5:87:90` last identity `git=acaecaa8 env=k1_main_rpl_im69d` — **`:rtrace_*` rejected.** Bench `B489A500` last `git=f2014c29 env=k1_bench_im69d_led150` — rtrace rejected. Ports drift; chip-ID is truth.

[FACT] Probe envs already in `platformio.ini`:

- Main RPL 160 WS2816 (P3-C canvas): `k1_main_rpl_rtrace_probe` extends `k1_main_rpl_im69d` + `-DK1_RENDER_TRACE_V1`. Tap is Lever-2 packed wire → dump `fmt=rgb16hex`.
- Bench 150-px WS2812: `k1_bench_im69d_led150_rtrace` → `fmt=rgb8hex`. **Wrong physical loom for a 160-LED host match.** Prefer Main RPL.

[FACT] Decoder: occupancy `scripts/regression-harness/score_rtrace_occupancy.py` (`rgb16hex` → R16BE G16BE B16BE). `hue_coverage.rtrace_frames` is **RGB8 only** — do not feed it `rgb16hex` and call it 160 pixels.

C0 8-bit frames for `head_position_upper`: take `rgb16 >> 8` → `uint8 (T, 160, 3)`. Do **not** use MAD. Do **not** use mean luminance as the stamp (Tempo polarity: extra gain often **lowers** luma). Host HTML used `preview_encode`; silicon close should score the dump bytes (preview only as a diagnostic vs HOST 0.63).

Authored Prim8 packer already in firmware tree: `scripts/agent/k1_authored_silicon_proof.py` `prsm()` — 34 bytes, magic `PRSM`, v1, hz, seq u32le, t_us u64le, eight u16le. That script pins Ember 16 on B489; C0 must pin **mode 18** (`LIGHT_MODE_WAVEFORM_TEMPO`) and palette **43** (`K1_Ultraviolet_Bright`) to match P3-C `PALETTE_RENDER_PARAMS`.

`+<audio/k1_*.cpp>` already compiles PRSM into hardware envs. rtrace `.cpp` is always in the src-filter; the flag is what arms it.

## 4. Remaining ship path (C0 FAIL, not closed)

1. **Already on silicon / in source:** 2026-08-31 Main RPL two-clock C0 corpse (FAIL INVALID_TEMPORAL_EXECUTION). C0-v2 probe instrument in firmware `probe/c0-epoch-v2` + host `scripts/gate_c0v2_silicon.py`. Product last restored `k1_main_rpl_im69d` @ `acaecaa8`.
2. **Remaining:** Flash `k1_main_rpl_rtrace_probe` with C0-v2 flags → timing self-test → one nominal C0-v2 (no cadence) → restore product env. State duration before the long capture.
3. **Who:** Agent, under the C0-v2 brief. Captain is not the LED validator.
4. **Stamp that means C0 shipped:** C0-v2 `PASS` / `ON_SILICON_PIXEL_VALIDATED` with metadata join and no lag correction, plus restore IDENTITY OK. Not a lagged rescore of the corpse. Not Captain eyes.

## 5. What C0 PASS means

Reuse `p3c_quant.score_clip` + `summarise` on silicon LED cubes keyed `A`,`B`,`D` plus `gain_*` and the same oracle slices as P3-C holdout.

| Must | Must not |
| --- | --- |
| Q1 Spearman(head_position, extra_gain) ≥ 0.40 | MAD(B,D) as the stamp |
| Q2 median Δ partial r(head, share \| mix) ≥ 0.15 and ≥ 70% clips Δ>0 | Mean luminance / occupancy as the binding |
| Q3 source-abs after mix still moves (same function as HOST Q3) | Captain looking at the plate |
| Holdout is the close (challenge is diagnostic) | Declaring C1 / student freeze |
| Cadence later: ZOH + delay still clear Δ≥0.15 **and** ≥ ~70% of that clip’s native-rate Δ | Running 2/5/10/20/31 Hz × 0/50/100/200 ms on hardware in this recon |

`head_position_upper`: luma centroid of LEDs 80–159; 0 = centre seam, 79 = tip (`p3c_score.py`).

## 6. Cadence / delay protocol (describe only — do not run)

Oracle hop is 31.25 Hz (512/16000). Extra_gain series is that hop grid.

**Packet rate ≠ descriptor rate.** Authored **rejects** `hz < 30` and drops AUTHORED if age > 50 ms. Therefore:

- Sample (or ZOH) extra_gain at the **hold rate** 2 / 5 / 10 / 20 / ~31 Hz.
- Apply causal delay 0 / 50 / 100 / 200 ms on that series.
- **Re-send** PRSM packets at **≥ 30 Hz** (recommend 31 or 120) with `hz` in 30–240, repeating the held sample. Seq must be monotonic (gap > 3 re-acquires).

2 Hz and 5 Hz **must not** put `hz=2` on the wire.

Tempo on silicon is live `k1_tempo` from the authored snapshot, not the host 120 BPM stub. Treat that as a confound to report, not a licence to edit Tempo.

## 7. Field coverage vs P3-C extra_gain

| Host extra_gain target | Authored Prim8 / snapshot | C0 |
| --- | --- | --- |
| `waveform_peak_scaled` | `peak_scaled` ← pressure (global peak **not** overwritten) | Use; keep mic quiet |
| chroma[12] × gain | **none**; chromagram **zeroed** | Colour via peak fallback. Not host-identical. Binding lever still peak→head |
| frozen 120 BPM | live tempo from authored novelty/peak | Report; do not retune the effect |
| palette 43 / mood 0.65 | must pin on device | Operator serial, not a new renderer |

A prior authored silicon **energy** proof (`k1_authored_silicon_proof.py`, B489, Ember 16, git `feb472ba`) is **not** C0: no LED dump, wrong mode, wrong device vs 160 WS2816 RPL.

---
**Document Changelog**
| Date | Author | Change |
| --- | --- | --- |
| 2026-08-31 | agent:edgeai-ssa | Ranked existing PRSM+rtrace path; chroma gap; flash GO; C0 scorer law. Not PASS. |
| 2026-08-31 | agent:edgeai | Silicon run FAIL; Q1 0.13 / Q2–Q3 6/9; product restored acaecaa8 im69d. |
| 2026-08-31 | agent:edgeai | Cause: arm-before-PRSM; +14 hop diagnostic would pass; stamp stays FAIL. |
| 2026-08-31 | agent:edgeai | INVALID_TEMPORAL_EXECUTION; runner retired; C0-v2 is the path. |
