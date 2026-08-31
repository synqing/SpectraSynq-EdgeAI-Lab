---
abstract: "L09 registry holes vs docs. 23 entries, 0 sha pins. 13/23 UNKNOWN licence. Statuses stop at HOST P3; none stamp C0-v2 PASS or cadence CLOSED. Four researched entries already executed in receipts. HOST docs only."
---

# L09 — MIR registry holes vs docs

**Lane:** L09. **Write-only this file.** Cadence CLOSED. No USB. No download. No 8 s loop. HARD FAIL `SAME_SONG_LOOP_MAX_15MIN`.

**Authority compared:** `mir/registry.yaml` (`schema_version: 1`, `updated: 2026-08-31`, 23 `id:`) vs `AGENTS.md`, `docs/DECISIONS.md` D20, `docs/mir/GATE_C.md`, `GATE_C0V2.md`, `GATE_C0_CADENCE.md`, `SELECTION_GATE.md`, `SOURCE_ACTIVITY.md`, `ESSENTIA_ORACLE.md`, `SHARE_STUDENT.md`, `LANDSCAPE.md`, `EFFECT_SEMANTICS_CONSUME.md`. Loader: `src/edgeai/mir/registry.py` (REQUIRED has no hash field).

**Method:** Read YAML + named docs + receipts. Counted `id:` / licence tokens / hash keys. Did not fetch GitHub/HF. Did not `shasum` blobs. Did not download models. Did not open USB.

## Contract

STATUS: FAIL (holes present; audit complete; no USB)
CLAIM: 23 entries; **0** sha/md5/git pins in YAML; 13/23 carry UNKNOWN; programme stamps C0-v2 PASS / cadence CLOSED live in AGENTS/D20/HANDOFF and **not** in the registry; 4 entries still `researched` after HOST receipts executed them; share-student absent
EVIDENCE: `mir/registry.yaml` · `docs/agent/lanes/L09_registry.md` · `artifacts/gate_c0v2/C0V2_RESULT.json` (`c0v2: PASS`) · `docs/mir/GATE_C0_CADENCE.md` (CLOSED) · `docs/mir/SOURCE_ACTIVITY.md` (musdb18.zip md5) · `docs/mir/ESSENTIA_ORACLE.md`
COMMAND: none (read-only). Equivalent inventory: `python3 -c "import yaml,re,pathlib; p=pathlib.Path('mir/registry.yaml'); d=yaml.safe_load(p.read_text()); print(len(d['entries']), sum('UNKNOWN' in str(e) for e in d['entries']), bool(re.search(r'sha256|sha1|^\\s+md5:', p.read_text(), re.I)))"`
METHOD_RISK: strings transcribed, not re-fetched SPDX/cards; local `.pb`/zips not hashed this lane; UNKNOWN is allowed (not a clearance and not a defect by itself)
NEXT: add pin fields (`sha256`/`md5`/`git`) to schema + musdb18 md5 from SOURCE_ACTIVITY; bump essentia-family status to `executed`; do not ingest CrowdioSet; do not treat teacher NC as student clearance. L26 owns the UNKNOWN field list. L10 owns LANDSCAPE name mismatch. L18/L22 own GATE_C / GATE_C0V2 body-stale.

## 1. Missing SHA (registry vs docs that already pin)

`mir/registry.yaml` has **no** `sha256`, `sha1`, `md5`, `git`, or `commit` key on any of 23 entries. `registry.py` REQUIRED tuple also omits hashes. D16 / `SELECTION_GATE.md` / `EFFECT_SEMANTICS_CONSUME.md` require `source_firmware_sha` **and** `atlas_artifact_sha256` as registry provenance — those fields are not on the MIR YAML.

| Asset (docs/receipts) | Pin that exists outside YAML | In `registry.yaml` |
| --- | --- | --- |
| MUSDB18 zip | `SOURCE_ACTIVITY.md`: Zenodo 1117372 `musdb18.zip` md5 `af06762477334799bfc5abf237648207` | `musdb18` `executed`, **no md5** |
| Share-student run | `experiments/share_student/receipt.json` `commit` `b95d3298db8ef20a6ec48975a71ba0fbc9a38414` | **no entry** |
| C0-v2 probe | `GATE_C0V2.md` probe `349d3cd4`; product restore `acaecaa8` / `k1_main_rpl_im69d` | not a MIR id; YAML silent |
| Atlas export | D16 firmware SHA `36466cd5`; in-file `atlas_artifact_sha256` on `docs/mir/effect_semantics/*.json` | not in YAML |
| Essentia `.pb` on disk | `artifacts/essentia_models/{deam-msd-musicnn-2,msd-musicnn-1,discogs-effnet-bs64-1,mtg_jamendo_moodtheme-discogs-effnet-1}.pb` (+ json sidecars, **no checksum keys**) | family `researched`, **no sha** |
| DEAM / PaRIRset / CrowdioSet / MSST / HT-Demucs / Banquet / MERT / MuQ / MAEST | docs cite URLs/versions only | versions as strings; **no commit/sha** |
| Semantic-v0 experiment | `src/edgeai/semantic_v0.py`; weights in `experiments/` | `executed`, **no weight hash** |

Do not invent hashes. Do not download to obtain them.

## 2. UNKNOWN licence (allowed; still a hole vs a pin)

Header: code ≠ weights ≠ dataset; **UNKNOWN is allowed**; not legal advice. L26 owns the 28-field list. Census here:

- **13/23** entries have ≥1 `UNKNOWN` token.
- **Weight UNKNOWN:** `musicnn`, `htdemucs` (MIT code ≠ weights; #327 scientific-only), `banquet` (not verified).
- **Dataset / commercial UNKNOWN:** `mirdata` (per set), `mtg-jamendo`, `deam`, `crowdioset`, `msst`, `banquet`.
- **Derived student UNKNOWN/LEGAL REVIEW (9):** `essentia-models`, `discogs-effnet`, `maest`, `musicnn`, `mert-v1-95m`, `muq`, `htdemucs`, `banquet`, `msst`. Teacher use ≠ clearance.
- **CrowdioSet fully UNKNOWN** (`dataset_licence` / `research_use` / `commercial_use` / `redistribution`) until per-file provenance. Docs: not ingested. Keep that.
- **CONFLICT (not UNKNOWN):** `essentia-models` `weight_licence` models.html CC BY-NC-SA 4.0 vs licensing_information.html CC BY-NC-ND 4.0.
- **`code_licence` unpinned (check/UNKNOWN):** `mir_eval` BSD-ish, `maest` check repo, `medleydb` check repo, `slakh2100` check, `moisesdb` check repo, `msst` UNKNOWN until repo pin.
- **`commercial_training_lineage`:** present on 4/23 (`musdb18`/`musdb-sample`/`medleydb` false; `slakh2100` candidate-synth-only). Missing on 19, including every NC teacher.

Not holes: `librosa` ISC commercial yes; `essentia` AGPLv3 filled (not free-for-product); `parirset` CC0; `musdb18` educational NC + lineage false.

## 3. Stale status vs C0-v2 PASS / cadence CLOSED

Programme stamps (binding, not in YAML):

| Stamp | Where it is true | In `registry.yaml` |
| --- | --- | --- |
| C0-v2 `ON_SILICON_PIXEL_VALIDATED` / `c0v2: PASS` | `AGENTS.md` Source oracle lane; `artifacts/gate_c0v2/C0V2_RESULT.json`; `GATE_C.md` abstract/changelog | **absent** |
| Cadence silicon **CLOSED** (5 Hz / 50 ms; joint 5+50 FAIL) | D20; `GATE_C0_CADENCE.md` abstract; `HANDOFF.md` | **absent** |
| C1 **OPEN** | D20; `GATE_C1.md`; `AGENTS.md` | **absent** |
| Two-clock C0 corpse **FAIL** `INVALID_TEMPORAL_EXECUTION` | `artifacts/gate_c0/`; D17 revisit | **absent** (correct not to treat corpse as PASS; YAML never named it) |

`musdb18.spectrasynq` still stops at “P3-B perfect V/D/B oracle… Not a shipping corpus.” It does not record Gate A PASS, B HOST PASS, C0-v2 silicon PASS, or cadence CLOSED. That is the load-bearing stale note on the source-oracle dataset.

Docs that still contradict the same stamps (not YAML, but “registry vs docs” readers will hit them):

| File | Stale claim | Current programme |
| --- | --- | --- |
| `SELECTION_GATE.md` abstract | “C0 FAIL … C0-v2 next. C1 blocked.” | C0-v2 PASS; C1 OPEN |
| `GATE_C.md` § C0 body | “2026-08-31 silicon close: FAIL — INVALID TEMPORAL EXECUTION” (changelog already says C0-v2 PASS) | corpse FAIL; C0-v2 PASS |
| `GATE_C0V2.md` abstract + § silicon | “Cadence OPEN. C1 blocked.” | cadence CLOSED; C1 OPEN |
| `GATE_C0_SILICON_PATH.md` abstract | C0 FAIL; successor C0-v2 (path doc, not close) | C0-v2 already closed |

L18/L22 own those body edits. This lane does not patch them.

## 4. Entry `status` vs executed receipts

Allowed statuses (`mir/README.md`): `researched` \| `runnable` \| `executed` \| `benchmarked` \| `rejected` \| `candidate` \| `blocked`. YAML uses only **executed / researched / blocked**. Never `runnable`/`benchmarked`/`rejected`/`candidate`.

| id | YAML status | Docs/receipts |
| --- | --- | --- |
| `librosa` | executed | `ORACLE_RECEIPT.md` + DEAM DSP — OK |
| `deam` | executed | `DEAM_AROUSAL_RECEIPT.md` — OK |
| `musdb18` / `musdb-sample` | executed | P3-A/B/C — OK as HOST ingest; silicon stamps missing (above) |
| `semantic-v0-experiment` | executed | toolchain witness — OK; still “not architecture authority” |
| `parirset` | executed | `PARIRSET_ONSET_ALIGNED.md` — OK |
| `musicnn` | **blocked** | TF1 + numpy&lt;1.17; prefer Essentia `msd-musicnn.pb` — OK |
| `essentia` | **researched** | `ESSENTIA_ORACLE.md` native TF HOST-ONLY ran |
| `essentia-models` | **researched** | same; `.pb` present under `artifacts/essentia_models/` |
| `discogs-effnet` | **researched** | Jamendo mood path used `discogs-effnet-bs64` |
| `mtg-jamendo` | **researched** | `jamendo_receipt.json` + ESSENTIA_ORACLE table |
| `htdemucs` | researched | `SOURCE_ACTIVITY.md`: Demucs **not installed** — status OK; AGENTS “HOST-only teacher probe” is not `executed` |
| `mir_eval` / `mirdata` | researched | pyproject extra; no execution receipt |
| rest | researched | no HOST run claimed |

Missing registry id vs executed lab work: **share-student** (`docs/mir/SHARE_STUDENT.md` HOST recoverability PASS, four-source incl. `other`, `commercial_training_lineage: false`). Semantic-v0 is listed; the recoverability net is not.

## Bound

Do not ingest CrowdioSet. Do not mix NC teachers into a shipping student. Do not freeze student I/O. Do not reopen cadence. Do not download models to fill SHA holes.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok-ssa-l09 | Created. 23 entries, 1 blocked, licence holes from mir/registry.yaml. |
| 2026-08-31 | agent:grok-ssa-l09 | vs docs: 0 sha pins, UNKNOWN census, stale vs C0-v2 PASS / cadence CLOSED, 4 researched-after-execute. |
