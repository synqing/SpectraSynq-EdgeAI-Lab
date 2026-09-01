---
abstract: "Review of the GPT SpectraSynq Music Intelligence Programme authority (2026-09-01). Verdict: architecture thesis SOUND, execution authority REJECT — it is SSA_RECEIPT_WAVE_IS_NOT_SHIP at larger scale. 13 factual errors found. Replacement brief: 5 jobs, each with a command that can go red. NOT an authority document. Captain decision input only."
status: REVIEW — not authority, not a lane, not a DONE_WHEN
---

# Review — GPT "SpectraSynq Music Intelligence Programme" execution authority

**This file is a review, not an authority document.** It does not create a lane, does not
stamp a gate, and must not be cited as a decision. Abbreviations are expanded on first use.

---

## 1 · Verdict in three lines

1. **The architectural thesis is right and worth keeping.** "Capabilities are durable,
   teachers are replaceable" is the correct organising principle, and the L0–L7 hierarchy
   plus the three intelligence planes are a genuine improvement on "add another ML head".
2. **The execution authority should be rejected as written.** It is eight new authority
   documents and a 23-row × 15-field registry whose `DONE_WHEN` is "file exists". That is
   `SSA_RECEIPT_WAVE_IS_NOT_SHIP` (D23, scarred 2026-08-31, ~30 hours before this brief
   was written) rebuilt at larger scale with better prose. `tests/test_ssa_wave_not_ship.py`
   exists precisely to stop this.
3. **The lineage question is upstream of the whole programme and the brief buries it.**
   Every teacher the brief nominates except two is non-commercial or unknown. Discovering
   more capabilities has no product path until there is a corpus a shipping student can
   legally be trained on. That question is currently `UNKNOWN` on 13 of 24 registry rows.

---

## 2 · What the brief got right about repo state (credit where due)

Verified against the local worktree at `ad0f65e`:

- Correctly refuses to reopen D26/Demucs, cadence, or Gate C.
- Correctly warns that remote/indexed GitHub state lags the worktree.
- Correctly identifies `semantic_trace.py` and `visual_hook.py` as the right seam.
- Correctly says teachers stay off Titan / Ethos-U55 (matches `AGENTS.md`).
- Correctly says student input/output (I/O) stays unfrozen.
- Correctly says specialists before a shared backbone.
- Correctly flags that Basic Pitch's constant-Q transform (CQT) front end may cost more
  than its 17k-parameter network. That instinct is right and Section 6 below proves it.

**One thing it got wrong about repo state that matters:** it treats Gate C / C1 as live
work to route around. **C1 closed on 2026-09-01 (D25)** — `LGP_PERCEPTUAL_VALIDATED`
stamped from the scored LED dump; Captain voided the qualitative eyes-on scorecard and
ruled `instrument-not-captain-eyes`. So the argument "don't let the source-share gate
choke the programme" is answering a blocker that no longer exists.

---

## 3 · Fact-check of the brief's external claims

Primary sources checked 2026-09-01. **VERIFIED / PARTLY / WRONG.**

| # | Claim in the brief | Verdict | What is actually true |
|---|---|---|---|
| 1 | Basic Pitch "fewer than 17,000 parameters" | **VERIFIED** | 16,782 params (ICASSP 2022 paper). |
| 2 | Basic Pitch "under 20 MB peak memory" | **WRONG** | Spotify marketing copy. The same paper measures **490 MB** peak on a 0:35 file and **951 MB** on a 7:45 file. Nothing in the paper supports 20 MB. Do not carry this number into any embedded budget. |
| 3 | Basic Pitch is a lightweight teacher/benchmark | **VERIFIED, with an unstated trap** | 22.05 kHz, hop 256 (≈11.6 ms), **2-second windows**, batch/offline. Its outputs are **non-causal**. See §5.3. |
| 4 | Basic Pitch licensing | **VERIFIED — and better than the brief says** | Apache-2.0 on **both code and weights**. One of only two clean teachers in the whole proposal. The brief under-sells this. |
| 5 | Basic Pitch "works best on one instrument at a time" | **VERIFIED** | Verbatim in the README. |
| 6 | OpenMIC-2018: 20,000 excerpts, 20 classes, CC BY 4.0 | **PARTLY** | Counts and package licence correct. Excerpts are 10 s. **The underlying audio is Free Music Archive (FMA) material under "a small variety of licences" — not verifiably all permissive.** Also ~10–11% label coverage (≈2.2 labels per clip); unknown ≠ negative. |
| 7 | EfficientAT `mn04` = 0.983M params / 0.11G MACs | **VERIFIED** | Matches the repo's own results table. Code MIT; weights carry no separate licence statement (presumed MIT). Front end is **32 kHz**, 128 mel, hop 320. |
| 8 | Slakh2100: 2,100 tracks, 187 patches, 34 classes, CC BY 4.0 | **VERIFIED** | 104.3 GB FLAC (~500 GB WAV). **BabySlakh is 883 MB, 20 tracks, and 16 kHz.** |
| 9 | Slakh duplicate-MIDI split leakage; use deduplicated splits | **VERIFIED** | `slakh2100_flac_redux` with an `omitted/` directory, Zenodo DOI 10.5281/zenodo.4599666. |
| 10 | htdemucs_6s adds guitar/piano, piano is weak | **VERIFIED** | Verbatim caveat in README. Code MIT. **Released weights were trained on MUSDB HQ + 800 undisclosed songs**; provenance question on the issue tracker is unanswered. Matches the repo's existing `weights: UNKNOWN`. |
| 11 | MERT/MuQ released weights are CC-BY-NC | **VERIFIED** | MERT-v1-95M/330M weights CC-BY-NC-4.0 (code Apache-2.0). MuQ weights CC-BY-NC-4.0 (code MIT). |
| 12 | MuQ ~300M; MuQ-MuLan ~700M; strong MIR results | **PARTLY — materially misleading** | MuQ 310M ✓. MuLan variant: paper says 630M, released "large" says ~700M. **Critically: the paper's headline numbers come from a 160,000-hour in-house corpus. The open checkpoint was trained on ~900 hours of Music4All, and the repo's own README warns it "may not achieve the same level of performance."** Probing the released weights and quoting paper results would be an error. |
| 13 | MAEST is a priority-2 research teacher | **PARTLY — a licence hazard the brief never mentions** | Code is **AGPL-3.0**. Weights CC-BY-NC-SA-4.0, commercial licence only on request from MTG. AGPL is a different and larger risk class than NC weights. The lab already flags Essentia's AGPL in `LANDSCAPE.md`; MAEST gets no such flag in the brief. |
| 14 | MusicFM is priority 4 | **INVERTED** | MusicFM (ByteDance) is the **only** music self-supervised model in the set with **permissive (MIT) weights**. For any lane that hopes to reach product it should be first, not fourth — with the caveat that 160k hours of its corpus is undisclosed in-house material. |
| 15 | arXiv 2505.16306 layer-wise study | **VERIFIED** | Early layers → objective tasks (instrument, singer ID); late layers → semantic tasks (structure, genre); **best layer is never the final layer** (MusicFM within first 6, MuQ within first 9). Authors caveat that concatenating all layers can *hurt* on small downstream sets. |
| 16 | Google MuLan as a music/text embedding to use | **WRONG in practice** | Paper only. **No weights or code were ever released.** MuQ-MuLan is a separate Tencent model, CC-BY-NC. |
| 17 | RA8P1: 1 GHz M85 + Helium, 256 GOPS U55, 2 MB SRAM, M33 @250 MHz, xSPI, PDM/I²S | **VERIFIED as spec, with two caveats** | 256-MAC Ethos-U55 @ 500 MHz → 256 GOPS is arithmetic peak, not throughput. "2 MB SRAM" = 2048 KB **including** 256 KB M85 TCM + 128 KB M33 TCM; **user SRAM is 1664 KB dual-core / 1792 KB single-core**, and Renesas' own flyer and datasheet disagree by ~64 KB. |
| 18 | RUHMI accepts ONNX / TFLite / PyTorch-ExecuTorch for RA8P1 + U55 | **VERIFIED** | Generally available, not early access. **Release notes as recent as April 2026 fixed "compiler conversion bugs affecting tensor routing between CPU and NPU subgraphs"** — the partitioning path is still maturing. Golden tensors are not optional. |
| 19 | "MusiMap profiling API exposes OCEAN, MBTI, Enneagram" | **WRONG on the current product, and the company history matters** | The live site claims "psychographic layer", "audience personality and values", mood — **no OCEAN / MBTI / Enneagram / ego-state claims anywhere on it**. MusiMap was acquired by Utopia Music (2021); Utopia went through Swiss bankruptcy (2023–24); the IP moved to Mitchell Asset Management. No published methodology, no validation, no independent evaluation found. |
| 20 | "meta-analysis shows many individual correlations are fairly small" (cited PubMed 29587129) | **WRONG citation, and the real evidence is weaker than implied** | PMID 29587129 is **Nave et al. 2018, an original two-study paper**, not a meta-analysis. The actual meta-analysis is **Schäfer & Mehlhorn 2017**, whose conclusion is blunter: personality traits *"barely account for interindividual differences in music preferences"* — only 6 of 30 reviewed studies reported \|r\| > 0.1. A 2023 cross-cultural replication (N=444) found **most trait–preference associations vanish once age, gender and musical sophistication are controlled**. |

Best-case published numbers for personality-from-music are r ≈ 0.11–0.30, i.e. **1–9% of
variance explained**, at N > 20,000. That is a population-level regularity, not an
individual-level inference.

---

## 4 · Structural objections to the execution authority

### 4.1 It is the scar, rebuilt

`AGENTS.md` HARD FAIL, dated yesterday:

> D22 OPEN is HOST **jobs** (script/test/authority file + a command that can go red).
> It is **not** 20–40 explore SSAs whose `DONE_WHEN` is `docs/agent/lanes/L*.md`.

The brief's Phase A is: create `MUSIC_INTELLIGENCE_ARCHITECTURE.md`, `capabilities.yaml`,
`CAPABILITY_GATES.md`. Phase B/C/D/E add `NOTE_HARMONY_RECON.md`,
`INSTRUMENT_TIMBRE_RECON.md`, `FOUNDATION_REPRESENTATION_RECON.md`,
`MUSIC_STATE_BUS.md`, `LISTENER_INTELLIGENCE.md`. Eight authority documents. Phase A is
explicitly declared a **blocking prerequisite** — "these must land first because they
define the language used by every other lane".

Renaming "40 Lxx receipts" to "8 authority documents" does not change the archetype. The
scar document already named it: **shifting the burden** — census the lane instead of doing
the lane.

### 4.2 It creates a second empty ledger while the first is empty

`mir/registry.yaml`: 24 entries, **0 SHA/hash pins** (L09 FAIL), **13 licence fields
UNKNOWN** (L26). The brief's response is to build `mir/capabilities.yaml` — 23 rows × 15
fields ≈ **345 new cells**, of which 115 are gate cells that every future agent will feel
obliged to fill with a receipt.

That is a receipt-generating machine bolted onto a ledger that has never been filled.

### 4.3 The foundation lane substantially re-does work already landed

`docs/mir/LANDSCAPE.md` already carries assessments the brief proposes to go discover:

| Asset | Already in LANDSCAPE | Brief's proposal |
|---|---|---|
| `maest` | `unsuitable_mcu_npu`, CC-BY-NC-SA, "5–30 s; not realtime" | Priority 2, "interrogate layer-by-layer" |
| `mert-v1-95m` | `unsuitable_mcu_npu`, "frame-rate SSL teacher (75 Hz)" | Priority 1 |
| `muq` | `unsuitable_mcu_npu`, "SSL + MuQ-MuLan zero-shot host probe" | Priority 3 and 5 |
| `slakh2100` | "Permissive synth; not a mic/venue substitute" | Presented as a new discovery |
| `essentia` | AGPL flagged | — |

**Genuinely new and worth adding: Basic Pitch, OpenMIC-2018, EfficientAT, MusicFM.**
Four registry rows, not a reconnaissance programme.

### 4.4 The Music-State Bus is a patch, not an architecture

`visual_hook.SemanticFrame` already uses `None` for absent (never zero), already carries
`provenance: list[str]`, and already has an open `extras: dict` extension point.
`semantic_trace.v1` already omits `None` keys on write and already declares that a visual
engine may consume it without knowing the teacher.

What is actually missing: **per-field** provenance, confidence, and causal age. That is a
~30-line change to one dataclass and one writer, plus assertions in the existing
`tests/test_semantic_trace.py`. The brief specifies a versioned schema document with
design principles, compatibility adapters and a test matrix for it.

Worse, there is a live hazard: `SEMANTIC_TRANSPORT_CONTRACT.md` is **FROZEN_FOR_C1**.
Introducing a second, richer, unfrozen contract alongside a frozen one, without a written
rule that firmware never reads the new one, is how an unfrozen research schema quietly
becomes a firmware obligation.

### 4.5 Listener Intelligence is built on the weakest evidence in the document

The exemplar is a company whose acquirer went bankrupt, which publishes no methodology and
whose current product does not claim the outputs attributed to it. The science behind it is
a mis-cited paper standing in for a meta-analysis that concludes the opposite. The brief
does hedge honestly ("derived hypothesis", "not identity truth") — but it still authorises
a lane, a document and a validation protocol.

**The useful idea survives without any of that.** "Which visual interpretations does *this*
listener like?" is a preference-learning problem over the render policy. It needs no
personality model, no music-information-retrieval (MIR) input, no third-party API, and no
General Data Protection Regulation (GDPR) profiling exposure. It is testable on one person
with a few dozen A/B choices. Everything OCEAN-shaped is a strictly worse version of the
same feature with added legal and reputational surface.

---

## 5 · Technical objections

### 5.1 The hard constraint is the Cortex-M85, not the NPU — and the shared thing that must come first is the front end, not the backbone

Verified against Arm's Vela `SUPPORTED_OPS` specification:

- **No FFT, no complex, no CQT operators exist on Ethos-U55 at all.** Every spectrogram,
  mel filterbank and constant-Q front end runs on the **M85** (Helium / CMSIS-DSP), not the
  NPU.
- No `MATMUL`/`BATCH_MATMUL` on U55 (U85 only) → **no transformer attention**.
- No `LAYER_NORM`, no `GELU` → CPU fallback.
- No `CONV_1D` — 1-D audio convolutions must be reshaped to 2-D.
- No `GRU`; only a heavily constrained `UNIDIRECTIONAL_SEQUENCE_LSTM` (no CIFG, peephole,
  projection or normalisation). Any temporal/prediction layer must be a causal CNN or hold
  state on the M85.
- **U55 has no dedicated SRAM** — `Dedicated_Sram` is Ethos-U65 only. The tensor arena
  shares the same ~1664 KB of user SRAM as the audio ring buffers, the DSP working set and
  the LED framebuffer.
- Measured, not marketing: MobileNetV2 int8 fully delegated ≈ **19 ms/inference** on a real
  256-MAC U55; independent benchmarking across small CNNs shows 12–21 ms and real
  utilisation **well under 50%** of peak GOPS.

Now put the brief's own capability set on that part. Three current front ends:

| Lane | Sample rate | Front end |
|---|---|---|
| existing HOST oracle / C1 carrier | **16 kHz**, hop 512 (31.25 Hz), n_fft 2048 | mel / chroma |
| Basic Pitch (note lane) | **22.05 kHz**, hop 256 | **Harmonic CQT**, 2 s window |
| EfficientAT (instrument lane) | **32 kHz**, hop 320 | 128-mel |

Three sample rates and three transforms, all on one M85 that is simultaneously running the
audio pipeline, the DSP that already drives the lights, the state fusion and the renderer.
The NPU has headroom; **the M85 does not**.

**Conclusion the brief inverts:** "specialists first → shared backbone second" is right
about *backbones* and wrong about *front ends*. Front-end unification is the earlier and
harder constraint. Any capability that cannot be computed from the front end the product
already runs should have to justify a second one **before** its accuracy is measured, not
after. That single rule would have reordered most of the proposed work.

### 5.2 BabySlakh cannot serve both lanes — the brief's best idea has a sample-rate flaw

The brief's strongest efficiency claim is that one bounded corpus drives both note and
instrument reconnaissance. **BabySlakh is 16 kHz.**

- **Note/pitch lane: fine, and better than fine.** Highest piano fundamental is ~4.2 kHz;
  16 kHz matches the lab's existing `host_chroma12` grid *exactly* (16 kHz, hop 512).
- **Instrument/timbre lane: not fine.** 8 kHz Nyquist removes the brightness and
  articulation cues instrument recognition leans on, and EfficientAT expects 32 kHz.
  Upsampling 16 kHz into a 32 kHz model is a domain shift, not a bounded first stage.

So the two lanes do **not** share a bounded corpus. They share it only if the instrument
lane pays for full Slakh (104 GB) or uses OpenMIC — whose audio licensing is unverified.
This is an argument for **splitting** them and running only the clean one first.

### 5.3 Label causality — the trap the lab has already fallen into once

Basic Pitch emits from **2-second, non-causal windows**. Every derived target the brief
proposes — melodic direction, harmonic density, tonal movement, note-onset density —
inherits that smoothing and that look-ahead.

Train a causal streaming student on non-causal labels and it either learns to be
systematically late or learns to predict the future, and the error shows up as a
lag you cannot see in a correlation table. **The lab has already eaten this exact bug**:
PaRIRset onset read as "dead" until it was rescored delay-aware and recovered
F1 0.05 → 0.86.

Any note/harmony receipt must report causal alignment explicitly, exactly as the PaRIRset
receipt does. The brief does not mention label causality once.

### 5.4 Every capability multiplies demand on Gate B, and Gate B is where things actually die

Gate B binds `descriptor × mode × lever` against the firmware pin
(`effect-semantics.json` @ `36466cd5`, 23 enabled `LIGHT_MODE_*`). Of the three bindings
ever tested, **two FAILED** (`composition_change × Comet × impact-launch`,
`composition_change × WaveformTempo × head_position`). The one PASS is
`source_share × WaveformTempo × head_position`.

The scarce resource is not descriptors. It is **levers with evidence**. A capability with
no candidate lever in `compatibility.json` is not a research lane — it is a wish. The brief
proposes 23 capabilities and names visual levers only in prose.

---

## 6 · Lenses, briefly

**Cynefin.** DSP baselines are Clear. Ethos-U55 operator support, licence lineage and RUHMI
behaviour are **Complicated** — knowable by reading authoritative documents, so *read them,
do not run experiments to discover them*. "Does this capability improve the light show" is
**Complex** — only probe-sense-respond answers it. The brief's error is the standard one:
it pours effort into the Complicated domain because it yields legible metrics, while the
binding question lives in the Complex domain.

**Theory of constraints.** With C1 closed, the binding constraint is no longer Captain's
eyes. It is **legally-clean supervised signal**. MUSDB is `commercial_training_lineage:
false`; every nominated foundation teacher except MusicFM is non-commercial; Demucs weights
are UNKNOWN; OpenMIC's audio is unverified. Adding capabilities does not relieve this and
cannot until it is relieved.

**Second-order.** (a) `capabilities.yaml` with 115 OPEN gate cells will be read by future
agents as 115 tasks. (b) A rich unfrozen Music-State Bus alongside a frozen transport
contract becomes a de-facto firmware obligation. (c) Shipping "your lamp reads your
personality" invites scrutiny of a claim with r ≈ 0.2 behind it — the reputational
downside is asymmetric to the feature's value. (d) Probing NC-licensed teachers produces
"distillation targets" the product may never legally use, so the lane's real output must be
*information cartography*, not distillation targets — and the brief names distillation
targets as the deliverable.

**Steel-man of the brief, at its strongest.** SELECTION_GATE Q1 ("which descriptors do the
lights actually need") is genuinely open, genuinely Captain's, and genuinely unanswered.
Source share is the only mature candidate, and freezing an architecture around the first
model that worked is a real failure mode that the lab is currently exposed to. Widening the
capability search **now**, before I/O freeze, is correct timing. The five super-gates
faithfully absorb the existing nine criteria without weakening them. Bounded-corpus-first
and "do not build the shared backbone yet" are both right. **Keep all of that. Reject only
the execution shape.**

---

## 7 · Replacement brief — what I would actually authorise

Five jobs. One writer per file. Each has a command that can go red. No new authority
documents. No `capabilities.yaml` until at least two capabilities have evidence to put in
it.

### J1 — LINEAGE (blocks everything; do this first)

Fill the licence and provenance fields for all 24 existing `mir/registry.yaml` entries plus
four new rows: `basic-pitch`, `openmic-2018`, `efficientat`, `musicfm`. Separate fields for
code licence, weight licence, dataset licence, `commercial_training_lineage`. Pin published
SHA-256 values where a Zenodo or Hugging Face record states one — **do not download to
obtain a hash, do not invent one, `UNKNOWN` is a legal value.**

`DONE_WHEN`: `pytest tests/test_mir_registry.py` extended to fail if any entry is missing
any of the four fields. Goes red today.

### J2 — CLEAN-CORPUS MEMO (Captain decision input, one page, not an authority doc)

One question: **what can a shipping student legally be trained on?** Candidates with
evidence, no recommendation. Slakh2100 (CC BY 4.0) currently looks like the only clean
corpus in the entire proposal set; Basic Pitch (Apache-2.0, code and weights) looks like
the only clean teacher. If that holds, it reorders the whole programme.

`DONE_WHEN`: memo exists **and** J1's registry fields agree with it (a test asserting the
memo's named corpora match `commercial_training_lineage: true` rows).

### J3 — NOTE / PITCH-CLASS, one lane, BabySlakh only

The only lane whose lineage survives end to end. Exact MIDI means **no teacher is needed
for the labels** — Basic Pitch is a real-audio benchmark only, run later if at all.

Single question: **does causal 12-bin pitch-class mass + register centroid, derived from
exact aligned MIDI, carry information that the existing causal `host_chroma12` does not?**

Constraints: BabySlakh (883 MB) only; 16 kHz matches the existing oracle grid exactly;
song-level splits; deduplicated splits if it ever scales; report causal alignment
explicitly (PaRIRset lesson); residual/partial correlation against `host_chroma12`, not
accuracy against a teacher.

A FAIL here is a **successful, cheap outcome** — it closes a lane in ~2 days and tells
Captain that chroma already carries the visual information, which is a real answer to
SELECTION_GATE Q1.

`DONE_WHEN`: script + JSON receipt + test, mirroring the P3-B/P3-C shape.

### J4 — INSTRUMENT / TIMBRE: HELD, not opened

Blocked on J1/J2. BabySlakh's 16 kHz cannot validate a 32 kHz instrument model (§5.2), and
OpenMIC's audio lineage is unverified. Opening it now buys a metric with no product path.

### J5 — SEMANTIC FRAME PATCH (not a bus, not a document)

Add optional per-field `provenance`, `confidence`, `causal_age_s` to
`visual_hook.SemanticFrame` and `semantic_trace.v1`. Keep missing ≠ zero. Keep v1 traces
readable. **Write into the code a rule that firmware never reads this schema** — the frozen
transport contract stays the only firmware-facing one.

`DONE_WHEN`: `pytest tests/test_semantic_trace.py` extended — old traces still parse,
optional fields stay optional, provenance survives a round trip.

### Not authorised

- **Foundation-representation reconnaissance.** `LANDSCAPE.md` already assessed MERT, MuQ
  and MAEST as `unsuitable_mcu_npu`; the released MuQ weights do not match the paper; MAEST
  is AGPL; all of them are non-commercial. Add **MusicFM** to the registry (MIT weights,
  the only permissive music-SSL candidate) and record the layer-wise finding — best layer
  is early, not final. Probe only if a capability appears that has **no labels**, which
  pitch and instrument do not.
- **`capabilities.yaml`.** Not until two capabilities have evidence rows.
- **`MUSIC_INTELLIGENCE_ARCHITECTURE.md` as a blocking Phase A.** The thesis belongs in
  `AGENTS.md` as ~8 lines of principle. If Captain wants the full hierarchy written down,
  it is a Captain-facing design note written **after** J3 returns, not a prerequisite that
  gates other work.
- **Listener Intelligence lane.** Reframe as a preference/bandit layer over the render
  policy if wanted. No personality inference, no MusiMap, no OCEAN.

---

## 8 · Decisions only Captain can make

1. **Corpus.** Is there budget or appetite to license a commercially-trainable music corpus?
   If not, the programme's ceiling is "Slakh-trained + own recordings", and that should be
   stated now rather than discovered at freeze time.
2. **Which descriptors the lights need** (SELECTION_GATE Q1) — still open, still yours.
   J3 is designed to give you one concrete data point on it cheaply.
3. **Whether the front-end rule is adopted:** *a capability that needs a second audio front
   end must justify it before its accuracy is measured.* This is the highest-leverage single
   line in this review.
4. **Listener Intelligence:** preference-learning over render policy — yes or no. Personality
   inference — recommend no, on evidence and on exposure.

---

**Status flags for this review**

- production K1 firmware changed: **NO**
- Titan touched: **NO**
- student I/O frozen: **NO**
- large teacher placed on U55: **NO**
- existing semantic traces broken: **NO**
- D25 / D26 / cadence / Gate C reopened: **NO**
- new authority document created: **NO** (this file is a review)

---
**Document Changelog**

| Date | Author | Change |
|---|---|---|
| 2026-09-01 | agent:cowork | Created. Review of GPT MI programme authority. Repo state verified at `ad0f65e`; 20 external claims fact-checked against primary sources. |

---

# ADDENDUM — 2026-09-01, second pass

Three corrections were raised against this review. **All three are verified and this
review was wrong on all three.** Corrected here rather than silently.

## C1 · Ethos-U55 does now have BATCH_MATMUL — §5.1 was stale

**Vela 5.0.0, 26/02/2026** added `BATCH_MATMUL with Int8 inputs` for **Ethos-U55/U65**
(not U85, which got TOSA EXT-CONTROLFLOW instead). Same release also added `LOG`, `PADV2`,
`REDUCE_MAX`, `REDUCE_MIN`, `REVERSE_V2`, `SUM`, `TILE` for U55/U65.
Source: `nxp-imx/ethos-u-vela` CHANGELOG @ `lf-6.18.20_2.0.0`.

The review's subagent read `SUPPORTED_OPS.md` at an **older** mirror tag
(`lf-6.12.3_1.0.0`). My error: I did not check the operator set's date against the
compiler generation.

**What changes:** the sentence "no MATMUL/BATCH_MATMUL → no transformer attention" is
withdrawn.

**What does not change:** `LAYER_NORM` and `GELU` are still absent from that release's
additions, so an attention block still partially falls back to CPU; and there is still no
FFT/complex/CQT operator of any kind, so the front-end argument in §5.1 — the load-bearing
one — is untouched. The lab already encodes half of this as **D3: "Banned: STFT inside the
NPU graph (export CNN on log-mel)."**

**New, and checkable today:** the operative fact is not what upstream Vela supports, it is
what the **pinned** toolchain supports. The lab pins RUHMI `6c5aad9` /
**Release-2026-06-19 / MERA 2.6.0+pkg.4815**, and **no Vela version is recorded anywhere in
the repo.** June 2026 postdates Vela 5.0.0, so it probably carries it — probably is not a
pin. One line in the RUHMI CI job printing the bundled Vela version, asserted in
`docs/ruhmi/COMPILE_RECEIPT.md`, closes this permanently and can go red.

## C2 · MusiMap's developer API does expose OCEAN / MBTI / Enneagram — §3 row 19 was wrong

`developers.musimap.com/api/profiling` documents profile types verbatim as:
`musical, musical_abridged, ocean, mbti, enneagram, ego_equilibrium, ego_description`.

My check read the marketing site (`/faq`, `/solutions/audience-intelligence`) and inferred
the product from it. That was the wrong surface, and the claim overreached.

**What changes:** "the current product makes no such claims" is withdrawn. Captain's
experience was with a live, documented capability.

**What does not change:** the scientific objection, which is now *stronger*, not weaker. A
live API emitting MBTI and Enneagram outputs is emitting two frameworks with weaker
psychometric standing than the Big Five, layered on top of a preference→personality link
that the actual meta-analysis (Schäfer & Mehlhorn 2017) puts near zero — only 6 of 30
studies above |r| = 0.1. The company-history caveat (Utopia acquisition, Swiss bankruptcy,
IP to Mitchell Asset Management), the absence of published methodology, and the absence of
any independent evaluation all stand.

## C3 · The released MuQ checkpoint is MSD-trained, not Music4All — §3 row 12 was wrong

The MuQ README states verbatim: *"Please note that the open-sourced MuQ was trained on the
Million Song Dataset. Due to differences in dataset size, the open-sourced model may not
achieve the same level of performance as reported in the paper."* Checkpoint is
`OpenMuQ/MuQ-large-msd-iter`.

**What changes:** the "~900 h Music4All" description is withdrawn.
**What does not change:** the conclusion — do not quote the paper's 160,000-hour results as
the released checkpoint's expected performance.

---

# ADDENDUM — errors in this review's own J3, found on second pass

## A · The register comparator was wrong, and would have manufactured a PASS

§7 J3 proposed testing *"pitch-class mass + register centroid"* against `host_chroma12`.

**Chroma is octave-folded by construction.** It cannot represent register. Testing register
centroid against a baseline that structurally cannot contain the signal guarantees a
favourable residual — the exact class of error this review criticised elsewhere (scoring
against a comparator chosen to lose).

**Correction:** split the comparators.
- `pitch_class_mass` vs `host_chroma12` — a fair test, chroma is the right rival.
- `register_centroid` vs existing **band energies / spectral centroid** — the DSP that
  actually carries octave information.

Consequence worth pre-registering: if pitch class is redundant but register survives,
**register centroid is cheap deterministic DSP and needs no student at all.** That is a
successful outcome that closes an ML lane, and it should be written down as such *before*
the run, or there will be pressure to convert it into a model.

## B · BabySlakh is synthetic, and this repo's own gate already refuses synthetic evidence

`docs/mir/SELECTION_GATE.md`, criterion 3:

> **Real-audio incremental information vs DSP** — … **Synthetic r=0.99 is not this evidence.**

BabySlakh is MIDI rendered through sampled instruments: clean note boundaries, no
performance-timing noise, no room, no microphone. A G1 information result measured on it
is an **upper bound**, not real-audio evidence, and therefore **cannot satisfy criterion
3** no matter how strong it is. Neither this review nor the brief it reviewed caught that.

**Correction to J3:**
- Receipt must stamp `SYNTHETIC_UPPER_BOUND` and state explicitly that criterion 3 remains
  unanswered.
- A FAIL is decisive and closes the lane cheaply (if the information is not there on clean
  synthetic audio, it will not appear on real audio).
- A PASS unlocks only a **real-audio second leg** — and that leg needs a real-audio label
  source, which is where **Basic Pitch (Apache-2.0, code and weights)** is the correct
  teacher.

This partially restores the original brief's position on Basic Pitch. "Do not use Basic
Pitch at all" was too aggressive: it is wrong as a *label source for the synthetic leg*
where exact MIDI exists, and right as the *label source for the real-audio leg* where
nothing else clean exists. The teacher-causality requirement in §5.3 applies in full to
that second leg.

## C · Lineage framing — conceded

The §6 Theory-of-Constraints framing ("legally-clean supervised signal is *the* binding
constraint") compressed two tracks into one. The correct statement, adopted:

> Research-only assets may inform capability **discovery**. They may not silently become
> the targets or training lineage of a **shipping** student.

Discovery and productisation have different admissibility rules. This review's §7 J4 and
foundation-lane deferral were argued on duplication with `LANDSCAPE.md` and absence of a
triggering question — not on lineage — so no job changes. Only the framing does.

---
**Addendum changelog**

| Date | Author | Change |
|---|---|---|
| 2026-09-01 | agent:cowork | C1–C3 corrections verified and accepted. Two errors found in this review's own J3 (register comparator; synthetic evidence vs SELECTION_GATE criterion 3). Basic Pitch position partially restored for the real-audio leg. |
