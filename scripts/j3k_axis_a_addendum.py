#!/usr/bin/env python3
"""J3K ADDENDUM - Axis A: OLD <-> NEW top-5% harmonic-event correspondence.

Uses the already-specified old/new mixture targets. No new threshold, no
representation scoring, no re-render. The J3K receipt is NOT modified.

Pre-registration: docs/mir/receipts/mixture_activation/J3K_PREREGISTRATION.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import j3g_common as C  # noqa: E402

sys.path.insert(0, str(C.ROOT / "src"))
from edgeai.mir import acoustic_activation as AA  # noqa: E402
from edgeai.mir.harmonic_movement import (  # noqa: E402
    is_tonal_instrument, lagged_abs_delta, pitch_class_state, tv_movement, within_track_rank,
)
from edgeai.mir.note_register import Note  # noqa: E402

EVENT_RANK, STABLE_RANK, TOL = 0.95, 0.50, 2
CURVES = Path("/tmp/j3j_curves.npz")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    import pretty_midi

    z = np.load(CURVES)
    kb = AA.KernelBank([{"track": str(t), "family": str(f), "curve": c}
                        for t, f, c in zip(z["tracks"], z["families"], z["curves"])])

    per_track, disp_all = [], []
    tot_old = tot_new = matched_old = matched_new = exact = 0
    cls_names = ("HARMONIC_CHANGE_FLAT_ENERGY", "HARMONIC_CHANGE_NO_ONSET",
                 "ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE")
    cls_tot = {k: [0, 0, 0] for k in cls_names}   # old count, new count, intersection

    for d in sorted(p for p in args.corpus.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        b = C.cached_track(d)
        n = b["n"]
        pm = pretty_midi.PrettyMIDI(str(d / "all_src.mid"))
        rect = np.zeros((n, 12)); act = np.zeros((n, 12))
        for inst in pm.instruments:
            if not is_tonal_instrument(inst.is_drum, inst.program):
                continue
            notes = [Note(float(x.start), float(x.end), int(x.pitch), int(x.velocity)) for x in inst.notes]
            if not notes:
                continue
            kern, _ = kb.for_stem(C.family_of(int(inst.program)), d.name)
            rect += pitch_class_state(notes, n)["pc_mass"]
            act += AA.acoustic_activation_state(notes, n, kern)["pc_mass"]
        Mo, Mn = tv_movement(rect), tv_movement(act)
        m = b["valid"][:n] & np.isfinite(Mo) & np.isfinite(Mn)
        idx = np.nonzero(m)[0]
        g = np.zeros(int(m.sum()))
        ro, rn = within_track_rank(Mo[m], g), within_track_rank(Mn[m], g)
        eo, en = ro >= EVENT_RANK, rn >= EVENT_RANK
        pos = {int(i): j for j, i in enumerate(idx)}

        def nearest(src, dst):
            out = []
            for j in np.nonzero(src)[0]:
                found = None
                for k in range(0, TOL + 1):
                    for s in ((0,) if k == 0 else (-k, k)):
                        q = pos.get(int(idx[j]) + s)
                        if q is not None and dst[q]:
                            found = s
                            break
                    if found is not None:
                        break
                out.append(found)
            return out

        mo, mn = nearest(eo, en), nearest(en, eo)
        no, nn = int(eo.sum()), int(en.sum())
        ex = int((eo & en).sum())
        got_o = sum(1 for x in mo if x is not None)
        got_n = sum(1 for x in mn if x is not None)
        disp_all.extend([x for x in mo if x is not None])
        tot_old += no; tot_new += nn; matched_old += got_o; matched_new += got_n; exact += ex
        per_track.append({"track": d.name, "n_old_events": no, "n_new_events": nn,
                          "exact_overlap": ex,
                          "old_unmatched_fraction": round(1.0 - got_o / max(no, 1), 4),
                          "new_unmatched_fraction": round(1.0 - got_n / max(nn, 1), 4)})

        # optional REPORTED_DIAGNOSTIC: challenge-class membership overlap
        rO = within_track_rank(lagged_abs_delta(np.zeros(n))[m] * 0 + b["B_onset"][:n][m], g)
        rR = within_track_rank(b["B_rms"][:n][m], g)
        for key, old_mask, new_mask in (
            (cls_names[0], (ro >= EVENT_RANK) & (rR <= STABLE_RANK), (rn >= EVENT_RANK) & (rR <= STABLE_RANK)),
            (cls_names[1], (ro >= EVENT_RANK) & (rO <= STABLE_RANK), (rn >= EVENT_RANK) & (rO <= STABLE_RANK)),
            (cls_names[2], (rO >= EVENT_RANK) & (ro <= STABLE_RANK), (rO >= EVENT_RANK) & (rn <= STABLE_RANK))):
            cls_tot[key][0] += int(old_mask.sum()); cls_tot[key][1] += int(new_mask.sum())
            cls_tot[key][2] += int((old_mask & new_mask).sum())

    dv = np.array(disp_all, dtype=np.float64)
    old_unmatched = 1.0 - matched_old / max(tot_old, 1)
    new_unmatched = 1.0 - matched_new / max(tot_new, 1)
    material = bool(old_unmatched >= 0.10)

    out = {
        "schema": "spectrasynq.mixture_activation_axis_a_addendum.v1",
        "job": "J3K-ADDENDUM", "date": "2026-09-02",
        "label": "ADDENDUM ONLY - the J3K receipt is not modified. No new threshold, no representation scoring, no re-render.",
        "what_this_completes": "Axis A of the intended J3K brief: OLD<->NEW top-5% harmonic-event correspondence, which the derived pre-registration did not record.",
        "definitions": {"event": "within-track percentile rank of target movement >= 0.95 - the same convention used throughout",
                        "match_window_hops": TOL,
                        "frames": "the identical J3K frame set - cached J3E validity intersected with finiteness of both movement series"},
        "totals": {"old_top5_events": tot_old, "new_top5_events": tot_new,
                   "exact_frame_overlap": exact,
                   "exact_overlap_fraction_of_old": round(exact / max(tot_old, 1), 4),
                   "old_matched_within_2_hops": matched_old,
                   "old_UNMATCHED_fraction": round(old_unmatched, 4),
                   "new_matched_within_2_hops": matched_new,
                   "new_UNMATCHED_fraction": round(new_unmatched, 4),
                   "median_displacement_hops": round(float(np.median(dv)), 3) if dv.size else None,
                   "mean_abs_displacement_hops": round(float(np.mean(np.abs(dv))), 3) if dv.size else None,
                   "displacement_histogram_hops": {str(k): int((dv == k).sum()) for k in (-2, -1, 0, 1, 2)}},
        "per_track": per_track,
        "REPORTED_DIAGNOSTIC_challenge_class_membership_overlap": {
            k: {"old": v[0], "new": v[1], "intersection": v[2],
                "jaccard": round(v[2] / max(v[0] + v[1] - v[2], 1), 4)} for k, v in cls_tot.items()},
        "threshold_from_the_brief": {"rule": "unmatched OLD events >= 10% means the corrected oracle changes which musical moments count as the strongest harmonic events",
                                     "value": 0.10, "no_new_threshold_invented": True},
        "axis_A_material": material,
        "classification": ("MIXTURE_TARGET_STATE_MATERIAL / ATTRIBUTION_IMMATERIAL" if material
                           else "MIXTURE_TARGET_STATE_IMMATERIAL / ATTRIBUTION_IMMATERIAL"),
        "J3K_receipt_modified": False,
    }
    args.out.write_text(json.dumps(out, indent=2, sort_keys=False) + "\n")
    print(json.dumps({k: out[k] for k in ("totals", "axis_A_material", "classification",
                                          "REPORTED_DIAGNOSTIC_challenge_class_membership_overlap")}, indent=2))
    print(f"addendum -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
