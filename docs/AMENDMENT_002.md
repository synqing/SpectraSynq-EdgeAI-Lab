---
abstract: "Amendment 002 live-domain: CLEAN vs PA/ROOM vs PA/ROOM+CROWD. Onset delayed ~100 ms (HOST-ONLY, 3 short test IRs), not killed. Cadence CLOSED. C1 OPEN. Do not reopen cadence cells."
---

# Amendment 002 — live-domain robustness

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

**Cadence silicon CLOSED.** Do not reopen cells. Do not run `scripts/gate_c0_cadence_silicon.py` (mechanically RETIRED, D20). No USB. No `/dev/cu.usbmodem*`. No 8 s holdout loop.

**C1 OPEN.** Next Gate-C action is Captain LGP look on **one full song he chooses**. Dumps do not answer C1. Student I/O still unfrozen.

Amendment 001 still owns research sequence and model-selection. This file owns **live/venue-domain scoring**. It does not reopen cadence. It does not freeze a student.

## STATUS

Amendment 002 **in force** for CLEAN / PA/ROOM / PA/ROOM+CROWD. HOST-ONLY delay-aware re-score: onset **delayed ~100 ms, not killed**, on **three short test IRs**. Cadence **CLOSED** (`CAPTAIN_CLOSE_2026-08-31`). C1 **OPEN**. CrowdioSet not ingested.

## CLAIM

1. PaRIRset test-split convolution does **not** kill onsets on the three short IRs already scored. Zero-lag onset r is a **delay artefact**. After aligning wet PCM to `argmax |RIR|`, native-hop F1@50 ms recovers **0.05 → 0.86**. All nine rows are `onset_delayed`.
2. Acoustic-path delay is its own measured variable (`acoustic_path_delay_s`). Mean direct-path **99.7 ms**; envelope xcorr ~**96 ms**. It is **HOST-ONLY**. It is **not** algorithm latency, **not** Titan/U55, **not** a K1 cadence cell.
3. Silicon **100 ms extra delay at 20 Hz is FAIL** (Q1). Do **not** “fix” PaRIRset by adding 100 ms to `extra_gain`. Cadence envelope stays: slowest 0-delay PASS **5 Hz**; largest added delay PASS **50 ms at 20 Hz**; joint **5 Hz + 50 ms FAIL**. Cadence CLOSED. C1 playback is the C0-v2 carrier (~31.25 Hz, 0 ms extra delay) on product firmware.

## EVIDENCE

- `artifacts/parirset_probe/receipt_aligned.json` (HOST-ONLY): `n_comparisons=9`, `verdict_counts.onset_delayed=9`, `mean_direct_path_s=0.0996875`, native onset r 0.0527 → 0.8753, F1@50 0.0525 → 0.8576.
- `docs/mir/PARIRSET_ONSET_ALIGNED.md`; D10 revisit (2026-08-31); AGENTS.md live-domain row; `docs/mir/SELECTION_GATE.md` live/venue bullet.
- Cadence: `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json` (`gate_c0_cadence=CLOSED`, `cadence_close=CAPTAIN_CLOSE_2026-08-31`, `c1="OPEN — next task"`, `student_freeze=false`, `plain.combined_5hz_50ms=FAIL`); `docs/mir/GATE_C0_CADENCE.md`; `docs/mir/GATE_C1.md`; D20/D22.

## COMMAND

Docs + existing receipts only. Do **not** re-run `scripts/parirset_onset_aligned.py`. Do not play DEAM, RIRs, or `holdout_8s_loop.wav`. Do not flash. No USB.

```text
python3 -c "import json,pathlib; a=json.loads(pathlib.Path('artifacts/parirset_probe/receipt_aligned.json').read_text()); s=a['summary']; print(a['label'], a['n_comparisons'], a['verdict_counts']); print({k:round(s[k],4) for k in s}); c=json.loads(pathlib.Path('artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json').read_text()); print('cadence',c['gate_c0_cadence'],c['cadence_close'],'c1',c['c1'],'freeze',c['student_freeze'],'5+50',c['plain']['combined_5hz_50ms'])"
```

Witness this SSA: HOST-ONLY; 9/9 `onset_delayed`; mean direct-path 0.0997 s; cadence CLOSED; C1 OPEN; student_freeze false; combined 5 Hz+50 ms FAIL.

## METHOD_RISK

- **Three short IRs only** (~0.4–0.6 s). 3 of 8 held-out venues. Do not generalise to a long hall tail.
- ~100 ms peak may be **dataset pre-delay** (4410 samples at 44.1 kHz) rather than physical FOH distance. Product-relevant either way: naive convolution injects it.
- Residual aligned F1 is **0.79–0.92**, not 1.0 (smear / extra wet peaks). PA/ROOM still needs delay-aware scoring.
- Unaccounted **100 ms still wrecks a 50 ms lighting-sync budget**. That is a **sync** problem, not “onset dies,” and not permission to reopen the silicon 100 ms cell.
- **Two different 100 ms numbers.** PaRIRset acoustic path = HOST alignment. Cadence 100 ms at 20 Hz = ON-SILICON extra_gain hold **FAIL**. Do not fold them.
- CrowdioSet still gated on per-file licence. No PA/ROOM+CROWD yet.
- HOST-ONLY. Not ON-SILICON. Not a student freeze. Not Titan.

## NEXT

Keep delay-aware Amendment 002. Do **not** freeze “onset dies in PA/ROOM.” Do not ingest CrowdioSet. Do not reopen cadence.

Ship path:

1. **Already on disk:** delay-aware HOST re-score (9/9 `onset_delayed`); C0-v2 `ON_SILICON_PIXEL_VALIDATED`; cadence CLOSED; C1 protocol in `docs/mir/GATE_C1.md`.
2. **Remaining:** Captain C1 LGP look, one full song he chooses, no 8 s loop. Later HOST: more venues, longer tails, PA/ROOM+CROWD if licences clear.
3. **Who acts:** Captain for C1. Nobody flashes cadence. Nobody loops the holdout clip.
4. **Stamp that means shipped for C1:** `LGP_PERCEPTUAL_VALIDATED`. This amendment staying in force is not that stamp.

---

Every serious descriptor or student must eventually be scored on:

1. **CLEAN/STUDIO**
2. **PA/ROOM** (convolve with PaRIRset test-split RIRs — 8 held-out venues)
3. **PA/ROOM + CROWD** (PaRIRset wet + CrowdioSet-class audience, only with per-file provenance)

PaRIRset: 40 professional concert venues through actual PA, measured at FOH. Train 32 venues / test 8 never seen. **CC0**. Paper: Gusó & Serra, ISMIR 2026, arXiv:2607.27828. Dataset: `enricguso/parirset`.

CrowdioSet: companion audience-noise set. **Do not ingest until each file's licence is recorded.** Do not mix NC material into a future commercial-safe corpus.

Held-out venue split is load-bearing. Do not train on `test/`.

Question:

> Does `vocal_activity = 0.84` or `arousal = 0.72` survive PA, room, and a crowd?

That is product-relevant. Improving studio SDR is not.

Plumbing: `edgeai.mir.live_domain.convolve_rir`. A synthetic exponential IR exists only to test the function — it is **not** PaRIRset.

Acoustic path delay is measured with `acoustic_path_delay_s` (RIR `argmax |h|`). It is **not** algorithm latency. On the three short test IRs used so far it is ~100 ms. Preserve it as its own variable. Score delay-aware at native hop. Do not use unaligned 2 Hz Pearson as product truth for onsets.

### Update — 2026-08-30: first held-out venue convolution

Three **test-split** RIRs (venues never in PaRIRset train): olivenzaOutdoors, valenciaMoon, palmaEsGremi. Convolved onto DEAM 2030 / 2034 / 2041. CrowdioSet not ingested.

The onset column below is **unaligned 2 Hz Pearson**. Keep it as a historical trap, not as product truth.

| song | venue | r(clean RMS, wet RMS) | r(clean onset, wet onset) 2 Hz zero-lag |
| --- | --- | --- | --- |
| 2030 | olivenzaOutdoors | 0.74 | 0.23 |
| 2030 | valenciaMoon | 0.64 | 0.28 |
| 2030 | palmaEsGremi | 0.57 | 0.29 |
| 2034 | olivenzaOutdoors | 0.55 | −0.27 |
| 2034 | valenciaMoon | 0.40 | −0.29 |
| 2034 | palmaEsGremi | 0.37 | −0.27 |

### Update — 2026-08-31: delay-aware re-score **invalidates** “onset dies”

Same nine comparisons. Native hop (~32 ms). Align wet PCM to `argmax |RIR|` (~100 ms on these three files).

| metric | mean |
| --- | ---: |
| onset r native zero-lag | 0.05 |
| onset r native delay-aligned | 0.88 |
| event F1 @ 50 ms unaligned | 0.05 |
| event F1 @ 50 ms aligned | 0.86 |

All nine rows: **onset delayed**, not killed. 2034’s negative r recovers to ~0.82–0.92 after alignment. Residual aligned F1 is 0.79–0.92 (some smear / extra peaks), not a collapse.

> **Superseded** — do not quote the 2026-08-30 onset column as “PA/room kills onset”. See `docs/mir/PARIRSET_ONSET_ALIGNED.md`.

HOST-ONLY. Receipts: `artifacts/parirset_probe/receipt.json` (old, unaligned) and `receipt_aligned.json`.

### Update — 2026-08-31: cadence CLOSED; C1 OPEN (W3-L36)

Live-domain scoring stays **HOST** and **OPEN** (D22). It does **not** consume the K1 USB port. It does **not** reopen cadence silicon.

| Stamp | Authority |
| --- | --- |
| Onset on 3 short test IRs | **delayed ~100 ms, not killed** (this amendment + `receipt_aligned.json`) |
| Cadence silicon | **CLOSED** — D20; runner retired; no 8 s loop |
| C1 LGP | **OPEN** — Captain, one full song, product firmware |
| Student I/O | still **unfrozen** until `docs/mir/SELECTION_GATE.md` and C1 |

Do not treat PaRIRset ~100 ms as the cadence 100 ms FAIL cell. Do not AND 5 Hz with 50 ms. C1 is the remaining Gate-C look.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Amendment 002. |
| 2026-08-30 | agent:edgeai | First PaRIRset test-split convolution; onset dies. |
| 2026-08-31 | agent:edgeai | Qualify onset result as provisional pending delay compensation. |
| 2026-08-31 | agent:edgeai | Delay-aware re-score: onset delayed, not killed. |
| 2026-08-31 | agent:edgeai | Name acoustic path delay as its own measured variable. |
| 2026-08-31 | agent:grok-ssa-w3-l36 | W3-L36: onset delayed ~100 ms not killed; Cadence CLOSED; C1 OPEN; two 100 ms numbers split. |
