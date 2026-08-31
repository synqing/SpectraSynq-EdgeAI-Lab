---
abstract: "L10 docs-only: LANDSCAPE.md vs mir/registry.yaml name/id mismatch. No USB."
---
STATUS: FAIL_MISMATCH (HOST-ONLY, docs-only)
CLAIM: LANDSCAPE is not a 1:1 map of registry. Eight landscape names have no `id:`; seven registry ids are absent from the map; one licence string disagrees.
EVIDENCE: `docs/mir/LANDSCAPE.md` (changelog 2026-08-30) · `mir/registry.yaml` (`updated: 2026-08-31`, 23 `id:` entries)
COMMAND: `python3 -c "import re,pathlib; L=pathlib.Path('docs/mir/LANDSCAPE.md').read_text(); R=pathlib.Path('mir/registry.yaml').read_text(); print(re.findall(r'^- id: (\\S+)',R,re.M))"`
METHOD_RISK: String inventory of the two files only — no licence URL fetch, no weight download, no USB, no song loop.
LANDSCAPE_ONLY: madmom; MERT-v1-330M; Open-Unmix; QSCNet; CLAP-class; deam-msd-musicnn; deam-audioset-vggish; VGGish-as-own-id (MuQ-MuLan and HT-Demucs 6s are rows in LANDSCAPE, folded under `muq` / `htdemucs` in registry)
REGISTRY_ONLY: musdb-sample; medleydb; slakh2100; parirset; crowdioset; msst; semantic-v0-experiment (LANDSCAPE only names Semantic-v0 as “not evidence”)
LICENCE_DRIFT: mir_eval LANDSCAPE=`BSD` vs registry=`BSD-ish (check package)` — all other cited licences (librosa ISC, Essentia AGPL+NC-SA/ND conflict, MERT/MuQ CC BY-NC, Demucs MIT code/#327 weights UNKNOWN, Jamendo mixed, DEAM mixed, Banquet 24.9M MIT/UNKNOWN) agree
ALIGNED: librosa, essentia, essentia-models, musicnn (3 s / TF1 blocked), mtg-jamendo 87/40/56, deam 1802@2 Hz, discogs-effnet, maest ~344 MB, mert-v1-95m 75 Hz, muq ~25 Hz/~300M, musdb18, moisesdb, htdemucs, banquet
NEXT: Either add the eight landscape-only ids to `mir/registry.yaml` or delete them from LANDSCAPE; add a LANDSCAPE section for the seven registry-only ids (venue/synth/student). Do not treat LANDSCAPE as authority until that edit.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L10 mismatch contract. LANDSCAPE vs registry. |
