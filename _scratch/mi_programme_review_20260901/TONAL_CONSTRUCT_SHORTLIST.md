---
abstract: "Decision input after J3C. Three ranked TONAL/MELODIC constructs worth testing next, each with construct, minimum representation, strongest existing baseline, oracle, one visual lever, one interaction hypothesis, and decisive FAIL/PASS. NOT an authority document. NOT to be executed until Captain/PM selects one."
---

# Next tonal/melodic constructs — ranked shortlist of three

Decision input only. **Do not execute.** Ranking is by: plausible visual value ·
difference from existing DSP · multiplier potential with an already-useful
capability · trustworthy ground truth · falsifiability · frontend implications.

The ranking is driven by one measured fact from J3C's label diagnostic:
**corr(highest sounding voice, lowest sounding voice) = 0.066** across 145,928
frames. The top and bottom of the texture move independently. That is evidence
about where tonal information lives, and it puts voice-conditioning first.

---

## 1 · VOICE-CONDITIONED REGISTER — top-voice and bass-voice as two states

| Field | Value |
|---|---|
| **Exact construct** | The register of the melodic top voice and the register of the bass voice, held as **two independent states**, not averaged. |
| **Minimum representation** | Two scalars in semitones (or two coarse 4-band states), plus a validity flag per voice. |
| **Strongest existing baseline** | The same `host_spectrogram80` deterministic estimators J3C already built — the weighted q90 and q10 of the spectral distribution are the natural spectral analogues of top and bottom voice — plus the six DSP scalars. No new frontend. |
| **Oracle / teacher** | BabySlakh exact MIDI for the synthetic leg (already downloaded, md5-verified). MUSDB18 stems for a later real-audio leg — research-only lineage, never a shipping corpus. |
| **One plausible visual lever** | The C1-closed binding is `source_share × WaveformTempo × head_position`. Top-voice register maps onto a **second, orthogonal** degree of freedom on the same proven carrier (palette position or vertical extent) without competing for `head_position`. |
| **One interaction hypothesis** | `bass_share × bass_register`. Bass owning the mix while *descending* is a different visual event from bass owning while static. Neither share nor register says that alone — and share is the lab's only capability with a closed Gate C, so this is the cheapest real multiplier available. |
| **Decisive FAIL** | Top-voice register is recovered from the existing frontend no better than the global mean was (out-of-fold R² < 0.40) **and** shows no larger excursion than the global mean at moments where mix RMS is flat. Then voice-conditioning bought nothing and the register family closes for this frontend. |
| **Decisive PASS** | Top-voice register recoverable at R² ≥ 0.55 from the **existing** frontend **and** its motion is materially decoupled from RMS/onset (low partial correlation). That would be a genuinely new lever at zero frontend cost. |

**Why first:** it is the only candidate whose central claim is already supported by
measured evidence in hand, it needs no new frontend, it needs no new corpus, its
oracle is exact, and it multiplies with the one capability that has cleared Gate C.

---

## 2 · HARMONIC MOVEMENT — change, not state

| Field | Value |
|---|---|
| **Exact construct** | The **rate and magnitude of change** in the pitch-class distribution — chord/tonal movement events — rather than which chord is sounding. |
| **Minimum representation** | One continuous change signal plus a sparse event stream (time, magnitude). Not a chord vocabulary. |
| **Strongest existing baseline** | Chroma flux (frame-to-frame delta of `host_chroma12`) and the existing spectral flux / onset detector. The real question is **temporal**: do harmonic-change events land where the DSP onset does *not*? |
| **Oracle / teacher** | BabySlakh exact MIDI gives exact pitch-class-set change times. No teacher model required. |
| **One plausible visual lever** | Palette-family transition — a lever no current descriptor drives, and one the effect pin already exposes through chromagram-fed modes. |
| **One interaction hypothesis** | `harmonic_change × beat_position`. A chord change on a downbeat is structurally different from one mid-bar; the lab already has tempo/beat fields on nine `LIGHT_MODE_*` entries. |
| **Decisive FAIL** | More than ~80% of exact harmonic-change events fall within ±1 hop of an existing spectral-flux/onset peak. The DSP already fires there; the capability is redundant *as an event source*. |
| **Decisive PASS** | A substantial fraction of harmonic changes occur with **no** DSP onset and **flat RMS** — the "harmonic change without energy change" challenge class — establishing an event class the current system is blind to. |

**Why second:** it directly answers the "we measured state when the system needs
change" objection, it is cheap, and it is the natural first **challenge-set**
experiment rather than a corpus-average one. It ranks below #1 only because its
visual lever is less proven than the C1-closed carrier.

---

## 3 · MELODIC CONTOUR OF THE PREDOMINANT VOICE

| Field | Value |
|---|---|
| **Exact construct** | Signed direction and magnitude of the top-voice pitch trajectory over a short causal window. |
| **Minimum representation** | One signed scalar, or a three-state {falling, stable, rising} with confidence. |
| **Strongest existing baseline** | Spectral-centroid delta and chroma flux on the existing frontend. |
| **Oracle / teacher** | BabySlakh MIDI for the synthetic leg. A real-audio leg would be the first legitimate trigger for **Basic Pitch** (Apache-2.0), with full non-causal-context accounting. |
| **One plausible visual lever** | Motion direction on the already-proven transport carrier. |
| **One interaction hypothesis** | `melodic_contour × source=vocals × section_state` — an ascending vocal line into a chorus is the canonical "musical cause" event in the North Star example. |
| **Decisive FAIL** | Contour direction is predictable from spectral-centroid delta at balanced accuracy ≥ 0.70. |
| **Decisive PASS** | Contour direction recoverable at usable accuracy **and** decoupled from centroid delta specifically at the "melody over stable accompaniment" challenge moments. |

**Why third:** it is downstream of #1 — you cannot have the contour of a voice you
cannot isolate — and it is the only one of the three that may eventually require
Basic Pitch and therefore a real-audio lineage decision.

---

## Deliberately NOT shortlisted, and why

- **Global pitch-class mass** — PARKED / UNDER-SPECIFIED. Do not re-run it as-is.
- **Tonal centre / key** — a state, and slower than the visual system's decision rate; it should follow #2 (movement) rather than precede it.
- **Tension / resolution** — the highest-value construct in the family and the hardest to falsify cheaply. It needs #2 in place first, because tension is a function of harmonic movement, not of harmonic state.
- **Chord vocabulary** — a large output space with no named visual lever. Do not open it before a lever exists.
- **Instrument-conditioned pitch** — depends on the instrument lane, which is held behind real-audio lineage and the 32 kHz front-end question.

---
**Document Changelog**

| Date | Author | Change |
|---|---|---|
| 2026-09-01 | agent:cowork | Created after J3C. Ranking driven by the measured corr(top voice, bottom voice) = 0.066. Decision input; not executed. |

---

# Research-method addendum — 2026-09-01, after J3D

Added to the working method, deliberately **not** as a new authority document.

## Existing visual grammar is a baseline, not a prison

For any new Music Intelligence capability, these are **different findings** and must
never be collapsed:

1. **`NO_PRODUCT_BINDING`** — the current pinned K1 visual vocabulary has no
   adequate carrier for the construct. This is an **L6/L7 discovery**.
2. **`NO_VISUAL_VALUE`** — the construct genuinely does not improve the show.

A capability that reveals a missing visual grammar has told us something about the
renderer, not about the perception. Do not solve that discovery with a production
firmware change. **First prove the visual verb in HOST research**, labelled
`HOST_VISUAL_GRAMMAR_PROTOTYPE` — never a product mode, never a compatibility row,
never a Gate-B close.

The trap this exists to prevent: the visual engine was designed around information
K1 already had. Requiring every future capability to fit that historical grammar
manufactures architectural false negatives.

## Seven questions, never collapsed

`Q1 existence · Q2 incrementality · Q3 representation · Q4 interaction ·
Q5 visual utility · Q6 recoverability · Q7 cost/productisation`

`VALUE ≠ RECOVERABILITY ≠ COMPUTE COST.` A capability can be high-value but
expensive, cheap but useless, informative but redundant in combination, or weak
alone and powerful in interaction.

## Construct validity before closure

Absence of evidence is evidence of absence **only** when the experiment had enough
construct coverage and sensitivity to make the phenomenon detectable. Every
experiment states: exact construct · proxy used · why the proxy is adequate ·
what a PASS permits · what a FAIL permits · what stays forbidden.

## Register branch — preserved, not executed

`highest sounding note ≠ perceptual melody`. Before it runs it must define
separately: lower/bass pitched state · upper pitched state · predominant/lead state
only if a defensible oracle exists · pitched instruments only · percussion excluded.
**Do not recreate the global-mean target.**
