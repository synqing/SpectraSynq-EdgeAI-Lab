---
abstract: "J2 commercial-training lineage map, 2026-09-01. One decision question: what can a shipping SpectraSynq student legally be trained on? Answer: nothing musical, today. Machine-readable twin: lineage_map.json. Test: tests/test_lineage_map.py. Captain decision input, not an authority document, not legal advice."
---

# Commercial-training lineage map — 2026-09-01

Not legal advice. Every classification is a research finding with a citable
source, not a clearance. `UNKNOWN` is recorded as `UNKNOWN`.

Machine-readable twin: `lineage_map.json`. `tests/test_lineage_map.py` fails if this
map and `mir/registry.yaml` ever disagree about an asset.

## The one-line answer

> **No asset in the near-term programme set is `CLEAN_CANDIDATE` for musical
> supervision.** The only `CLEAN_CANDIDATE` in the whole map is **PaRIRset**, and
> that is room acoustics — it can augment a student, it cannot teach one music.

| Class | Count | Assets |
|---|---|---|
| `CLEAN_CANDIDATE` | 1 | parirset (CC0 1.0 — impulse responses only) |
| `CONDITIONAL_PER_ASSET` | 3 | slakh2100, basic-pitch, openmic-2018 |
| `UNKNOWN` | 5 | efficientat, musicfm, htdemucs, mtg-jamendo, crowdioset |
| `RESEARCH_ONLY` | 8 | musdb18, medleydb, moisesdb, deam, mert-v1-95m, muq, maest, share-student-feasibility |
| `NOT_APPLICABLE` | 2 | librosa, essentia (tools) |

## Correction to this review's own earlier claim

The 2026-09-01 first-pass review said *"Slakh2100 (CC BY 4.0) and Basic Pitch
(Apache-2.0) look like the one clean end-to-end lineage."* **Both legs are weaker
than that.**

- **Slakh2100** is CC BY 4.0 on the rendered audio — but `slakh-generation`'s README
  says the rendering used **Native Instruments Kontakt Komplete 12**, a proprietary
  sample library, and neither the README, the WASPAA paper (arXiv 1909.08494) nor
  slakh.com says anything about whether that affects the CC BY grant on the audio it
  produced. That is a documentation *silence*, not a clearance. The source MIDI is
  Lakh MIDI — CC BY 4.0 applied by Raffel to a **scraped, third-party-authored**
  collection, which he says outright he did not transcribe.
  **Cheaper answer if this matters: Flakh2100** renders the same MIDI through
  open-source FluidSynth + the TimGM6mb soundfont.
- **Basic Pitch** is Apache-2.0 on code *and* weights, which is genuinely rare. But
  it was trained on MAESTRO + Slakh-redux + GuitarSet + iKala + **MedleyDB**, and
  MedleyDB is CC BY-NC-SA. A permissive licence on the teacher does not clear a
  student trained on the teacher's outputs — the lab's own D26 discipline.

## The five layers, kept apart

The map separates `source_audio` / `annotations` / `teacher_weights` /
`pseudo_labels` / `derived_student` for every asset, because they diverge. Two cases
where that separation changes the answer:

- **OpenMIC-2018 annotations are clean while its audio is not.** Spotify/MARL's own
  labels are CC BY 4.0. The 20,000 audio clips are third-party FMA recordings under
  whatever licence each artist chose.
- **MUSDB18's Zenodo record carries the machine-readable rights id `other-nc`** — the
  NC status is not an interpretation, it is a field.

## Footgun found, and it is a live one

The OpenMIC-2018 **Zenodo record badge says CC BY 4.0**. Read naively, that appears
to clear 2.6 GB of audio for commercial use with attribution. **It does not.**
Spotify cannot relicense an artist's CC BY-NC recording. The badge covers the
compilation and the labels. This is exactly why the archive ships a per-track
`license_title` column and why Zenodo's own description says *"Track metadata, with
licenses for each audio recording"*. Any future agent that reads only the landing
page will get this wrong.

## OpenMIC / FMA licence-filtered subset — `FEASIBLE_WITH_CONDITIONS`

Verified 2026-09-01 by direct cross-check of the real files, not from secondary
summaries:

- `openmic-2018-metadata.csv` carries `license_title`, `license_url`,
  `license_parent_id` for every row, plus the raw FMA `track_id`.
- All **20,000 / 20,000** OpenMIC rows match FMA's own `raw_tracks.csv`
  `license_title` **byte-for-byte, 0 mismatches**. No join heuristics needed.
- Licence split of the 20,000 clips: **17,777 (88.9%) carry a NonCommercial clause;
  2,223 (11.1%) do not; 2,075 (10.4%) once CC BY-ND is also excluded.**
- No audio download is required to compute the subset.

**Conditions:** the CSV is not offered standalone (it lives inside one 2.6 GB
tarball, md5 `e4ccf187e2bb5ab2e115416e8aafe7f4`); whether CC BY-ND permits model
training is an unsettled legal question, not a metadata one; licences reflect artist
declarations at 2016–17 scrape time.

**Consequence for J4:** a ~2,000-clip, 10-second, real-audio, commercially-filtered
instrument corpus **is** constructible. That is a credible *evaluation* set. It is
thin as a *training* set. So J4 has a plausible real-audio evaluation path without
buying a corpus — and still does not have a training one.

## Is a licensed real-music corpus now a binding strategic decision?

**Yes.** Not as paperwork — as the thing that decides what the programme can ever ship.

The evidence: every real-music corpus in the lab is `RESEARCH_ONLY` or `UNKNOWN`.
Every music-SSL teacher is NC or unverified. The one permissive teacher (Basic Pitch)
carries NC material in its own training set. The one permissive corpus (Slakh) is
synthetic *and* has an unanswered proprietary-sample-library question. The largest
clean real-audio slice anyone can assemble from open sources today is ~2,000
ten-second clips.

Three coherent positions, stated so Captain can pick one rather than drift:

1. **Buy/licence a real-music corpus.** Highest cost, and the only route where a
   student trained on real vocals, real production and real venues can ship.
2. **Synthetic + own material.** Flakh2100-class open-soundfont renders, K1's own
   recordings, commissioned or cleared performances, plus the ~2,000-clip filtered
   FMA slice for evaluation. Cheaper, and it caps what the student can generalise to.
3. **Answer the Slakh question first.** One email to the Slakh authors about the
   Kontakt rendering, and one look at Flakh2100, may convert the largest permissive
   symbolic corpus in the field from `CONDITIONAL` to usable. **Cheapest by a wide
   margin, and it should happen before either of the other two is priced.**

Nothing in J3 is blocked by this. J3 is discovery, and discovery admits research-only
assets. What is blocked is any promotion of a J3 result into a shipping student.

## The discipline this map encodes

> Research-only assets may inform capability **discovery**. They may not silently
> become the targets or training lineage of a **shipping** student.

Discovery and productisation have different admissibility rules. This map is the
productisation rule. It does not gate J3.

---
**Document Changelog**

| Date | Author | Change |
|---|---|---|
| 2026-09-01 | agent:cowork | Created (J2). 19 assets classified across five layers. OpenMIC/FMA filtering verified FEASIBLE_WITH_CONDITIONS by direct 20,000-row cross-check. Slakh Kontakt risk and Basic Pitch corpus exposure recorded as corrections to this review's own earlier claim. |
