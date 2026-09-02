#!/usr/bin/env python3
"""J3E Captain-facing artefact — CONTROL | TREATMENT side by side.

Excerpt selection is DETERMINISTIC and driven by J3D challenge membership ONLY:
for each category, the fixed-length window with the highest count of that
category's frames, ties broken by lowest track name then lowest start index.
Nothing is chosen after looking at rendered output.

Decision support for Captain. NOT a perceptual gate, NOT D25/C1, does not reopen
Gate C, not a product mode.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from edgeai.mir.harmonic_movement import within_track_rank  # noqa: E402
from edgeai.mir.harmonic_visual import EXPOSURE, frame_delta_e, render_strip  # noqa: E402
from edgeai.mir.host_chroma import preview_encode  # noqa: E402
from edgeai.mir.note_register import HOP, SR  # noqa: E402

WINDOW_HOPS = 188  # ~6.0 s at 31.25 Hz
RIBBON_H = 44
CATEGORIES = ["HARMONIC_CHANGE_FLAT_ENERGY", "HARMONIC_CHANGE_NO_ONSET",
              "ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE", "ORDINARY_HOLDOUT"]


def png_data_uri(rgb: np.ndarray) -> str:
    from PIL import Image

    im = Image.fromarray(np.ascontiguousarray(rgb.astype(np.uint8)), mode="RGB")
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def ribbon(colour_window: np.ndarray) -> str:
    leds = render_strip(colour_window)
    shown = preview_encode(leds[:, :1, :], exposure=EXPOSURE)[:, 0, :]
    return png_data_uri(np.repeat(shown[None, :, :], RIBBON_H, axis=0))


def marks(mask_window: np.ndarray, w: int) -> str:
    band = np.full((8, w, 3), 24, dtype=np.uint8)
    band[:, mask_window] = np.array([255, 240, 120], dtype=np.uint8)
    return png_data_uri(band)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--colours", type=Path, required=True)
    ap.add_argument("--result", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    from j3e_harmonic_visual import build  # same code path, same masks

    res = json.loads(args.result.read_text())
    if res["outcome"] != "HARMONIC_VISUAL_INFORMATION_GAIN":
        print("artefact is only produced on HARMONIC_VISUAL_INFORMATION_GAIN", file=sys.stderr)
        return 2

    npz = np.load(args.colours)
    blocks = [b for b in (build(d) for d in sorted(
        p for p in args.corpus.iterdir() if p.is_dir() and (p / "all_src.mid").is_file())) if b]

    groups = np.concatenate([np.full(int(b["valid"].sum()), b["track"]) for b in blocks])
    vM = np.concatenate([b["M_oracle"][b["valid"]] for b in blocks])
    vO = np.concatenate([b["B_onset"][b["valid"]] for b in blocks])
    vR = np.concatenate([b["B_rms"][b["valid"]] for b in blocks])
    rM, rO, rR = (within_track_rank(x, groups) for x in (vM, vO, vR))
    cls = {"HARMONIC_CHANGE_FLAT_ENERGY": (rM >= 0.95) & (rR <= 0.50),
           "HARMONIC_CHANGE_NO_ONSET": (rM >= 0.95) & (rO <= 0.50),
           "ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE": (rO >= 0.95) & (rM <= 0.50)}
    cls["ORDINARY_HOLDOUT"] = ~(cls["HARMONIC_CHANGE_FLAT_ENERGY"]
                                | cls["HARMONIC_CHANGE_NO_ONSET"]
                                | cls["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"])
    got = {k: int(cls[k].sum()) for k in CATEGORIES[:3]}
    assert got == res["challenge_membership"]["expected_from_J3D_A_v2"], got

    # per-track contiguous masks
    per_track = {}
    off = 0
    for b in blocks:
        nv = int(b["valid"].sum())
        idx = np.nonzero(b["valid"])[0]
        m = {}
        for k in CATEGORIES:
            full = np.zeros(b["n"], dtype=bool)
            full[idx] = cls[k][off:off + nv]
            m[k] = full
        per_track[b["track"]] = m
        off += nv

    picks = []
    for cat in CATEGORIES:
        best = None
        for tr in sorted(per_track):
            m = per_track[tr][cat].astype(np.int32)
            if m.size < WINDOW_HOPS:
                continue
            c = np.convolve(m, np.ones(WINDOW_HOPS, dtype=np.int32), mode="valid")
            s = int(np.argmax(c))
            if best is None or c[s] > best[2]:
                best = (tr, s, int(c[s]))
        picks.append({"category": cat, "track": best[0], "start_hop": best[1],
                      "count_in_window": best[2],
                      "start_s": round(best[1] * HOP / SR, 2),
                      "duration_s": round(WINDOW_HOPS * HOP / SR, 2)})

    rows = []
    for p in picks:
        tr, s = p["track"], p["start_hop"]
        sl = slice(s, s + WINDOW_HOPS)
        c_ctrl = npz[f"CONTROL__{tr}"][sl]
        c_trt = npz[f"TREATMENT__{tr}"][sl]
        de_c = np.nan_to_num(frame_delta_e(c_ctrl), nan=0.0)
        de_t = np.nan_to_num(frame_delta_e(c_trt), nan=0.0)
        rows.append({**p,
                     "control_png": ribbon(c_ctrl), "treatment_png": ribbon(c_trt),
                     "marks_png": marks(per_track[tr][p["category"]][sl], WINDOW_HOPS),
                     "control_mean_dE": round(float(de_c.mean()), 2),
                     "treatment_mean_dE": round(float(de_t.mean()), 2)})

    P = res["results"]["without_floor"]
    html = ["<title>J3E — Harmonic Colour Transition</title>", "<style>",
            ":root{--bg:#f7f7f5;--fg:#16150f;--mut:#6b6a62;--line:#dcdad2;--acc:#7a5cff}",
            "@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#111110;--fg:#f2f1ec;--mut:#9a988e;--line:#2c2b27}}",
            ":root[data-theme=dark]{--bg:#111110;--fg:#f2f1ec;--mut:#9a988e;--line:#2c2b27}",
            "body{background:var(--bg);color:var(--fg);font:14px/1.55 ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;padding:28px}",
            ".w{max-width:1000px;margin:0 auto}h1{font-size:19px;margin:0 0 4px}",
            ".sub{color:var(--mut);margin:0 0 22px}",
            ".lbl{font:11px/1 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.06em;color:var(--mut);text-transform:uppercase}",
            ".card{border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 18px}",
            ".cat{font-weight:650;margin:0 0 2px}",
            "img{width:100%;display:block;border-radius:4px;image-rendering:pixelated}",
            ".r{margin:8px 0 2px}table{border-collapse:collapse;width:100%;font-size:13px}",
            "th,td{text-align:left;padding:6px 10px;border-bottom:1px solid var(--line)}",
            "th{color:var(--mut);font-weight:500}.n{font-variant-numeric:tabular-nums}",
            ".warn{border-left:3px solid var(--acc);padding-left:12px;color:var(--mut);margin:18px 0}",
            "</style>", "<div class=w>",
            "<h1>J3E — Harmonic Colour Transition</h1>",
            "<p class=sub><code>HOST_ORACLE_VISUAL_FEASIBILITY</code> · perfect-information oracle vs "
            "<code>host_chroma12</code> · same renderer, same frozen constants, only the musical "
            "information differs · photons held fixed so luminance carries nothing.</p>"]

    html.append("<table><tr><th>event-tolerant response rate</th><th>CONTROL</th><th>TREATMENT</th></tr>")
    for k, nm in (("HARMONIC_CHANGE_FLAT_ENERGY", "harmonic change, flat energy"),
                  ("HARMONIC_CHANGE_NO_ONSET", "harmonic change, no onset"),
                  ("ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE", "acoustic only — should stay quiet")):
        html.append(f"<tr><td>{nm}</td><td class=n>{P['CONTROL']['event_tolerant'][k]:.3f}</td>"
                    f"<td class=n>{P['TREATMENT']['event_tolerant'][k]:.3f}</td></tr>")
    html.append(f"<tr><td>resting colour churn (median ΔE)</td>"
                f"<td class=n>{P['CONTROL']['holdout']['median_deltaE']:.2f}</td>"
                f"<td class=n>{P['TREATMENT']['holdout']['median_deltaE']:.2f}</td></tr></table>")

    for r in rows:
        html += [f"<div class=card><div class=cat>{r['category'].replace('_',' ').title()}</div>",
                 f"<div class=lbl>{r['track']} · {r['start_s']}s + {r['duration_s']}s · "
                 f"{r['count_in_window']} frames of this class in window</div>",
                 f"<div class=r><span class=lbl>marked frames</span></div><img src='{r['marks_png']}' alt=''>",
                 f"<div class=r><span class=lbl>control — host chroma · mean ΔE {r['control_mean_dE']}</span></div>"
                 f"<img src='{r['control_png']}' alt=''>",
                 f"<div class=r><span class=lbl>treatment — oracle harmony · mean ΔE {r['treatment_mean_dE']}</span></div>"
                 f"<img src='{r['treatment_png']}' alt=''>", "</div>"]

    html += ["<div class=warn>Time runs left to right. Yellow ticks mark frames belonging to that "
             "challenge class, selected from J3D membership <b>before</b> rendering. This is decision "
             "support, not a perceptual gate: it is not Gate B, not Gate C, not D25/C1, and no product "
             "mode or firmware was touched.</div>", "</div>"]
    args.out.write_text("\n".join(html))
    print(json.dumps({"picks": picks, "out": str(args.out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
