---
abstract: "L05 MATCH. Share-student receipt is four-source simplex including other. PASS scored on vocals/drums/bass only; other stays in metrics/MAE. HOST-ONLY. No USB."
---

# L05 — share-student receipt vs four-source other

STATUS: MATCH

CLAIM: `artifacts/share_student/receipt.json` matches the four-source including-`other` simplex contract. Sources order is vocals, drums, bass, other. Share is hop stem-power / sum; silence → zeros not 1/4. Head is 4 logits → softplus powers → share. Verdict PASS is HOST recoverability on vocals/drums/bass; `other` is present in student, mix-linear, and MAE tables (r=0.547, MAE=0.138) and is not dropped. I/O unfrozen. 20788 params.

EVIDENCE: `artifacts/share_student/receipt.json` (`label_definition.sources`, `label_definition.share`, `metrics.student.other`, `metrics.student_mae.other`, `verdict=PASS`, `model.params=20788`, `student_io_frozen=false`). Twin: `experiments/share_student/receipt.json`. Contract: `docs/mir/SHARE_STUDENT.md`; D17 `docs/DECISIONS.md`; transport channels `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md`. Code: `src/edgeai/mir/source_oracle.py:26` `SOURCES`; `src/edgeai/share_student.py` `shares_from_powers` + `verdict_from_metrics` core `("vocals","drums","bass")`; `scripts/share_student_feasibility.py` `pack_source_metrics` iterates `SOURCES`. Cadence guard (not this receipt): `require_four_source_share` in `src/edgeai/mir/gate_c_cadence.py`.

COMMAND: `python3 -c "import json; r=json.load(open('artifacts/share_student/receipt.json')); print(r['verdict'], r['label_definition']); print(list(r['metrics']['student'])); print(r['metrics']['student_mae']); print(r['model']['params'], r['student_io_frozen'])"` — HOST JSON only. No USB. No song playback.

METHOD_RISK: HOST-ONLY. Receipt stores simplex as text, not a sum-to-1 checksum of test shares. `verdict_from_metrics` never scores `other`; a three-source metrics dict can still PASS that helper. Applying the same inequalities to this receipt's `other` also beats mix-energy (0.547 ≥ 0.30; 0.547 > 0.116+0.05; r_pred_mix −0.385 is not mix-copy). P3-B ref omits `other` (`null`) because P3-B never published it — not a three-source student. `STEM_INDEX` is MUSDB file order (mix/drums/bass/other/vocals); labels use named stems.

NEXT: Keep `other`. Do not freeze I/O. Do not start a hop-level/streaming product student until Gate C. Cadence CLOSED. No USB.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L05 MATCH: receipt vs four-source other simplex; V/D/B verdict; other in MAE. |
