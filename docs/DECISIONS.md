---
abstract: "D1–D17. Feasibility PASS. C0 FAIL INVALID_TEMPORAL_EXECUTION 2026-08-31. Two-clock runner retired. C0-v2 next. C1 blocked. No more nets."
---

# Decisions

Each entry: chosen / why / rejected / revisit evidence.

## D1 — Separate research repo

**Chosen:** `SpectraSynq-EdgeAI-Lab`, not K1 firmware.
**Why:** experimental ML deps must not contaminate production firmware.
**Rejected:** a branch inside K1 Firmware.
**Revisit:** when a model has on-silicon evidence and a planned integration.

## D2 — Python 3.12 + uv for training; Python 3.10 x86 for RUHMI

**Chosen:** host venv is CPython 3.12 (Homebrew/uv). System Python 3.14 is not used.
**Why:** PyTorch/torchaudio/onnxruntime wheels trail the newest CPython. RUHMI/MERA ships `cp310` manylinux x86_64 and win_amd64 only (mera 2.6.0+pkg.4815).
**Rejected:** one environment for both lanes; native macOS RUHMI (does not exist).
**Revisit:** if Renesas ships an arm64 / cp312 wheel.

## D3 — CNN consumes log-mel, not PCM

**Chosen:** host frontend is 16 kHz mono, 1.0 s, 25 ms window, 10 ms hop, 64 mels, 100 frames. Exported NPU graph input is `(1, 1, 64, 100)` log-mel.
**Why:** FFT/STFT is cheap on M85 and hostile to U55. Golden tensors then isolate “did the NPU run this graph?” from “did we compute mel correctly?”
**Rejected:** exporting the STFT into the U55 graph; instance-max normalisation (silence becomes noise).
**Revisit:** if a measured frontend on M85 exceeds its budget, or a different rate (12.8 / 24 / 32 kHz) wins an A/B.

## D4 — Depthwise-separable CNN, ReLU, pooling head, sigmoid

**Chosen:** MobileNet-like DS-CNN, ~100k–300k params, ReLU, pool over HxW, linear → 3 logits, sigmoid at export.
**Why:** RUHMI has compiled MobileNetV2 / MnasNet / EfficientNet / ResNet18 / INT8 KWS. Quantizer table lists Conv2d, BatchNorm, ReLU, ReduceMean, Gemm, Sigmoid as A8 on MCU_ETHOS. ONNX Sigmoid is F32 on MCU_CPU — another reason to target `--npu`.
**Rejected:** transformers, foundation models, SiLU-only graphs, custom ops.
**Revisit:** if Vela/RUHMI reports material CPU fallback on this graph; then change the graph before squeezing desktop accuracy.

> **Superseded in part by D11.** The U55 witness graph must not export `tensor.mean` / ONNX ReduceMean on NCHW spatial axes. Use `AdaptiveAvgPool2d((1,1))`. ReduceMean remains in the quantizer table and still split the smoke subgraph (GHA 33318864219).

## D5 — ONNX opset 14, RUHMI quantizer flow

**Chosen:** `torch.onnx.export` opset 14, static batch=1. RUHMI compile uses `--npu --quantize` (ONNX frontend is documented as quantizer-flow only).
**Why:** RA8P1 zoo includes several opset-14 ONNX nets. Host ORT INT8 is a **different** quantizer than MERA — both are recorded, never treated as equivalent.
**Rejected:** waiting for a beautiful FP32 model before the first compile; TFLite-only path as a gate (RUHMI accepts ONNX).
**Revisit:** if ONNX→TFL lowering drops DepthwiseConv; then export TFLite or rewrite groups.

## D6 — Synthetic corpus now; MUSDB18 as optional research source

**Chosen:** always-on synthetic stem generator so TRAIN/EVAL/EXPORT work with zero Zenodo access. MUSDB18 adapter + official train/test folders + hashed val carve when `MUSDB_ROOT` exists.
**Why:** MUSDB requires an access request and is not a shipping licence. Blocking the lab on a 22 GB download is busywork.
**Rejected:** committing any audio corpus; treating synthetic F1 as product evidence.
**Revisit:** when MUSDB (or a cleared corpus) is on disk; then re-train and replace SYNTHETIC receipts.

## D7 — Activity is log-RMS of each stem, not mix share, not binary

**Chosen:** per-stem RMS mapped log-scale from silence `1e-4` to loud `0.15`, clipped to [0, 1]. Loss is `BCEWithLogits` on those soft targets.
**Why:** a quiet drum hit should still modulate lights; mix-share would hide it behind a loud vocal.
**Rejected:** hard 0/1 labels; softmax (sources coexist).
**Revisit:** if MUSDB labels from this mapping do not correlate with listening; then change the mapping, not the split rule.

## D8 — MIR-first; Semantic-v0 is an experiment (Amendment 001)

**Chosen:** Host MIR oracle + registry + selection gate **before** freezing any embedded student outputs. Semantic-v0 remains as a U55-shaped toolchain experiment only.
**Why:** vocals/drums/bass on synthetic stems skipped a mature field (MTG tagging, DEAM affect, MERT/MuQ teachers, separator-as-teacher).
**Rejected:** treating Semantic-v0 as architecture authority; inventing BUILDING/DROPPING labels first.
**Revisit:** when the nine gate questions in `docs/mir/SELECTION_GATE.md` have evidence.

## D9 — RUHMI CI pins Release-2026-06-19 / 6c5aad9 and gcc-13 libstdc++

**Chosen:** GHA installs `ppa:ubuntu-toolchain-r/test`, upgrades `libstdc++6`/`libgcc-s1`, gcc-13; clones RUHMI at `6c5aad9`; compiles `ad01_int8.tflite` then `smoke.onnx`.
**Why:** run 33317047371 failed at `fe_onnx_cli` missing GLIBCXX_3.4.31/32. Renesas Ubuntu README already required this. Cloning `main` is not reproducible.
**Rejected:** Docker-as-blocker; floating `main`.
**Revisit:** if a newer RUHMI release ships a cp310 wheel with a documented host recipe.

Run 33318276254 then installed MERA `2.6.0+pkg.4815` and checked out `6c5aad90…` successfully; the job died on `rev-parse HEAD | grep -qx 6c5aad9` because HEAD prints the full SHA. Pin is now the full hash with an equality test.

## D10 — Amendment 002 live-domain (PaRIRset)

**Chosen:** CLEAN / PA_ROOM / PA_ROOM_CROWD evaluation; PaRIRset test venues held out; CrowdioSet gated on per-file licence.
**Why:** studio-trained MIR degrades on PA+room+crowd — the K1 mic's actual world (Gusó & Serra, ISMIR 2026).
**Rejected:** studio-only student scores as product evidence.
**Revisit:** delay-compensated traces exist (2026-08-31). Onset on these three short test IRs is delayed (~100 ms), not killed. Still revisit after more venues, longer tails, and PA/ROOM+CROWD.

## D11 — AdaptiveAvgPool2d, not ReduceMean, for the U55 witness graph

**Chosen:** `nn.AdaptiveAvgPool2d((1,1))` + flatten before the linear head.
**Why:** GHA 33318864219 compiled Renesas `ad01_int8.tflite` (toolchain OK) then quantized `smoke.onnx` (PSNR 27.8, 94.7% NPU ops) and failed C99 with Vela `More than one Ethos-U custom operator found in subgraph`. Cause: `x.mean(dim=(2,3))` → ONNX ReduceMean on `[1,256,8,13]` axes `[2,3]`; Vela parks MEAN on CPU and splits Ethos-U ops. Compiler-reported PRE-SILICON (not on-silicon): SRAM 250 KiB, flash 186.92 KiB, 35.6M MACs/batch, MEAN unsupported.
**Rejected:** keeping ReduceMean because the RUHMI quantizer table lists it as A8.
**Revisit:** if a later MERA/Vela accepts that MEAN layout as a single NPU region.

GHA 33319114336: AdaptiveAvgPool2d `smoke.onnx` produced C99 (RAM 262,414 B, Flash 188,896 B, 35.56 M MACs, 88.9% node coverage). PRE-SILICON.

## D12 — Source oracle is abs / share / delta, not RMS(stem)

**Chosen:** perfect stem traces emit `*_abs` (fixed log-RMS), `*_share` (power / sum of stem powers), `*_delta` (Δ share). Visual control for source is A/B/C/D (baseline / mix energy / abs / share).
**Why:** a moderate vocal in a quiet breakdown can dominate a louder buried vocal. P3-A on 144 MUSDB samples: r(vocals_share, mix)=0.12 vs r(vocals_abs, mix)=0.46.
**Rejected:** a single RMS(stem) channel; Demucs before the perfect oracle wins a full-song visual test.
**Revisit:** P3-B full-song evidence landed. `abs` is demoted (within-track r vs mix 0.44–0.64). `share` passed the incremental-information gate (0.10–0.17). Lighting utility is **not** decided from the P3-B HTML stand-in; that is P3-C.

## D13 — Frozen corpus maps; hop-centre timestamps; composition_change is causal

**Chosen:** visual extra-DoF uses a 5th–95th percentile map fitted once on the pooled corpus (`p3b-v1`), not per-song min-max. Hop RMS is timestamped at hop centre. `composition_change` is causal L1/2 of the share vector vs 0.5 s ago, no lookahead.
**Why:** per-song stretching can make a flat RMS look lively. The PaRIRset miss was a timestamp/alignment error. Arrangement change is not loudness.
**Rejected:** eyeballed per-track normalisation; putting abs/share/delta in one undifferentiated A/B/C/D/E strip.
**Revisit:** composition_change passed to P3-C visual-engine evaluation. Do not invent BUILDING/DROPPING. Student I/O still not frozen.

## D14 — P3-C is the visual-engine gate; stems beat Demucs if it passes

**Chosen:** Isolated HOST replay of firmware `light_mode_waveform_tempo` on the product palette path (`K1_Ultraviolet_Bright`, square_iter 0). Same extra DoF for baseline / mix energy / source share (peak + chroma gain in [0.62, 1.0]). Events are firmware `light_mode_comet` over that tempo floor, matched trigger budget. Challenge 10 from the P3-B oracle set plus 10 MUSDB-test holdout tracks stratified by duration, not by share/RMS disagreement. Versions are blinded. No firmware production edits. No Demucs.
**Why:** P3-B HTML was an existing-behaviour stand-in. Chromatic bloom + PHOTONS² was unreadable. Spectrum River was visually usable; Captain preferred Waveform Tempo. Pixel MAD is not a lighting call. If lights never benefit, there is nothing to teach. If they do, MUSDB stems are already perfect supervision — a separator teacher would only add error.
**Rejected:** lighting call from `p3b1_continuous.html` / `p3b2_events.html`; chroma HSV as the colour path; installing Demucs next; training a student before P3-C; freezing student heads for abs/share/delta/composition_change separately; Captain eyes as the P3-C close when dumps exist.
**Revisit:** Quantitative dump close `docs/mir/P3C_QUANT.json`. Binding **`source_share × WaveformTempo × head_position` HOST PASS** on holdout (Δ partial r 0.63, 9/9). Binding **`composition_change × Comet × impact-launch` FAIL** vs `|Δ mix|` at drum attacks. That is not “composition_change is useless.” Student share head is a candidate; event head is not. Student I/O still OPEN. Next: tiny research student on MUSDB stem powers for share only. Demucs still later.

## D15 — Effect semantics live in firmware; EdgeAI consumes a SHA-pinned export

**Chosen:** Canonical Effect Semantics / Response Registry belongs in K1 firmware, pinned to firmware SHA. EdgeAI-Lab imports `effect-semantics.json` and must not grow a competing effect taxonomy. Visual-utility stamps bind `descriptor × mode × lever`. Waveform Tempo is a continuity/reference carrier for source-share, not a universal lighting actuator. MIR student outputs stay effect-agnostic (share/arousal/…), not “Waveform-Tempo-head-position.”
**Why:** P3-C showed the same extra control moves head position and can *lower* mean luminance. Evaluating descriptors on an arbitrary mode manufactures false negatives (composition_change vs Comet) and false positives (brightness as “more music”).
**Rejected:** 174-effect Lightwave catalogue as current inventory; putting canonical mode behaviour in EdgeAI-Lab; treating mean brightness as the default visual metric; blocking the share-student recoverability experiment on a full 22-mode hardware atlas.
**Revisit:** when firmware exports `effect-semantics.json` at SHA `36466cd5` (Atlas lane `docs/effect-response-atlas`). First tranche: inventory + static map + host fingerprints for several archetypes + first compatibility matrix.

## D16 — Three gates; share student now; composition-change parked

**Chosen:** Permanent split: **A** semantic information, **B** visual-carrier (`descriptor × mode × lever`), **C** product/LGP perceptual. Share: A PASS, B HOST PASS on Waveform Tempo head position. C OPEN. Start the four-source share-student recoverability experiment now (mixture → powers → deterministic share). Do not wait for Atlas coverage of the remaining modes. Composition-change **implementation** is parked: no ML head (it is a function of share). Atlas may search for a macro-transition grammar or record a visual-language gap. Evidence ladder: STATIC_SOURCE → HOST_PIXEL_VALIDATED → ON_SILICON_PIXEL_VALIDATED → LGP_PERCEPTUAL_VALIDATED. Registry provenance: `source_firmware_sha` plus `atlas_artifact_sha256` / generation commit, because the Atlas can move while firmware SHA stays `36466cd5`.
**Why:** Waiting on 16 more modes would delay the only remaining MIR recoverability question. Collapsing A/B/C repeats P3-C category errors. Looking at dumps is not looking at the LGP.
**Rejected:** Blocking the student on full Atlas; a composition_change neural head; declaring Gate C from host pixels; treating BPM/phase/tick/confidence as one “tempo” lever.
**Revisit:** student recoverability receipt; Atlas grammar-coverage + tempo sweeps; Gate C only after silicon dumps then LGP taxonomy.

## D17 — PRE-PRODUCT FEASIBILITY PASS; Gate C next; no more nets yet

**Chosen:** Stamp **Source Ownership Programme — PRE-PRODUCT FEASIBILITY PASS** (A PASS, B HOST PASS on Tempo head, recoverability HOST PASS, C OPEN, I/O unfrozen). Stop hop-level/streaming student work. Next load-bearing experiment is Gate C on the physical K1: **C0** silicon LED dumps of the same extra-DoF (A/B/D) plus cadence 2/5/10/20/~31 Hz and delays 0/50/100/200 ms; **C1** LGP perceptual only after C0. Effect semantics set the semantic-lane clock; do not freeze 31.25 Hz because the host renderer used it. Freeze the **contract** (four-source including `other`, share vs powers, cadence, latency, silence) only if C passes, then deploy. Tempo bindings stay specific (`beat_phase × WaveformTempo × transport`, `beat_tick × PulsePrism × pulse_event`), not `supports_tempo`.
**Why:** The 21k net proved recoverability is plausible. Making that net deployment-grade before C says the semantic deserves silicon is the wrong leverage point. Host cadence is rehearsal, not C0. C1 is the first human visual judgement that is actually load-bearing.
**Rejected:** Streaming student now; treating HOST recoverability as Gate C; dropping `other`; flashing without a named GO; Captain eyes for C0 dumps.
**Revisit:** C0 silicon 2026-08-31 **FAIL — INVALID TEMPORAL EXECUTION** (`artifacts/gate_c0/C0_RESULT.json`): Q1 Spearman 0.13 < 0.40, Q2/Q3 6/9 wins. Two clocks. +14 hops is diagnosis, not a PASS. Two-clock runner retired. Next is C0-v2 device epoch (`docs/mir/GATE_C0V2.md`), not Tempo edits, not another net, not cadence in the same attempt. C1 still blocked.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Created with D1–D7 at lab bootstrap. |
| 2026-08-30 | agent:edgeai | D8 — Amendment 001 MIR-first. |
| 2026-08-30 | agent:edgeai | D9 RUHMI pin + gcc-13; D10 Amendment 002. |
| 2026-08-30 | agent:edgeai | D9: pin full SHA after grep-short-SHA CI fail. |
| 2026-08-30 | agent:edgeai | D11 AdaptiveAvgPool2d after smoke C99 split. |
| 2026-08-31 | agent:edgeai | D8 nine gate questions; D10 onset result provisional. |
| 2026-08-31 | agent:edgeai | D4 pooling note vs D11; D10 onset delayed-not-killed. |
| 2026-08-31 | agent:edgeai | D12 source oracle abs/share/delta. |
| 2026-08-31 | agent:edgeai | D13 frozen maps, hop-centre timebase, composition_change. |
| 2026-08-31 | agent:edgeai | D12 revisit (abs demoted); D14 P3-C visual-engine gate, no Demucs. |
| 2026-08-31 | agent:edgeai | D14: continuous engine is Waveform Tempo on the palette path, not bloom/river. |
| 2026-08-31 | agent:edgeai | D14 revisit: dump-scored share PASS / composition-change events FAIL; no Captain eyes. |
| 2026-08-31 | agent:edgeai | D15 firmware Effect Semantics export; D14 stamps narrowed to descriptor × mode × lever. |
| 2026-08-31 | agent:edgeai | D16 three gates; share student unblocked; composition-change parked; Atlas provenance hash. |
| 2026-08-31 | agent:edgeai | D17 feasibility PASS stamp; Gate C is next; stop streaming-student work. |
| 2026-08-31 | agent:edgeai | D17 revisit: C0 silicon FAIL on Main RPL; C1 blocked; no new net. |
| 2026-08-31 | agent:edgeai | D17: C0 FAIL is INVALID_TEMPORAL_EXECUTION; C0-v2 replaces two-clock harness. |
