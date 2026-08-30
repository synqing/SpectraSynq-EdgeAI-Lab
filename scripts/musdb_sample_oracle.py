#!/usr/bin/env python3
"""P3-A: MUSDB 7 s samples → abs/share/delta oracle → DSP comparison.

HOST-ONLY. Official musdb sample excerpts, not the 4.7 GB corpus.
No Demucs. No training. No U55. Research/NC audio, gitignored.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from edgeai.mir.conventional import extract_onset_bundle
from edgeai.mir.semantic_trace import write_trace
from edgeai.mir.source_oracle import SOURCES, source_oracle
from edgeai.mir.teachers import activity_envelope, hpss_stems

ROOT = Path("datasets/musdb_sample")
OUT = Path("artifacts/source_activity")
SR = 16_000
HOP = 512
# A handful of traces is enough to prove replay; stats use every sample track.
TRACE_LIMIT = 8


def _pearson(a: np.ndarray, b: np.ndarray) -> float:
    n = min(len(a), len(b))
    if n < 8:
        return float("nan")
    a, b = np.asarray(a[:n], dtype=np.float64), np.asarray(b[:n], dtype=np.float64)
    if a.std() < 1e-12 or b.std() < 1e-12:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def _mono(x: np.ndarray) -> np.ndarray:
    y = np.asarray(x, dtype=np.float32)
    if y.ndim == 2:
        y = y.mean(axis=-1)
    return y.reshape(-1)


def _load_db():
    import musdb

    ROOT.mkdir(parents=True, exist_ok=True)
    return musdb.DB(root=str(ROOT.resolve()), download=True, sample_rate=SR)


def _interp(t_src, y, t_dst):
    return np.interp(t_dst, t_src, y).astype(np.float32)


def analyse_track(track) -> tuple[dict, dict]:
    mix = _mono(track.audio)
    stems = {name: _mono(track.targets[name].audio) for name in SOURCES}
    oracle = source_oracle(stems, sr=int(track.rate), hop=HOP, mix=mix)
    conv = extract_onset_bundle(mix, sr=int(track.rate), hop=HOP)
    hpss = hpss_stems(mix, int(track.rate))
    t_p, e_p = activity_envelope(hpss["percussive"], int(track.rate), hop=HOP)
    t_h, e_h = activity_envelope(hpss["harmonic"], int(track.rate), hop=HOP)

    t = oracle["times"]
    onset = _interp(conv["times"], conv["onset_env"], t)
    flux = _interp(conv["times"], conv["spectral_flux"], t)
    perc = _interp(t_p, e_p, t)
    harm = _interp(t_h, e_h, t)

    rec: dict = {
        "track": track.name,
        "subset": getattr(track, "subset", ""),
        "duration_s": float(mix.size / track.rate),
        "label": "HOST-ONLY",
        "corpus": "musdb_sample_7s",
        "licence": "MUSDB educational/NC — not commercial training lineage",
    }
    for name in ("vocals", "drums", "bass"):
        rec[f"r_{name}_abs_vs_mix"] = _pearson(oracle[f"{name}_abs"], oracle["mix_rms"])
        rec[f"r_{name}_share_vs_mix"] = _pearson(oracle[f"{name}_share"], oracle["mix_rms"])
        rec[f"mean_{name}_abs"] = float(np.mean(oracle[f"{name}_abs"]))
        rec[f"mean_{name}_share"] = float(np.mean(oracle[f"{name}_share"]))
        rec[f"max_{name}_delta"] = float(np.max(np.abs(oracle[f"{name}_delta"])))
    rec["r_drums_abs_vs_onset"] = _pearson(oracle["drums_abs"], onset)
    rec["r_drums_share_vs_onset"] = _pearson(oracle["drums_share"], onset)
    rec["r_drums_abs_vs_flux"] = _pearson(oracle["drums_abs"], flux)
    rec["r_drums_abs_vs_hpss_perc"] = _pearson(oracle["drums_abs"], perc)
    rec["r_drums_share_vs_hpss_perc"] = _pearson(oracle["drums_share"], perc)
    rec["r_vocals_abs_vs_hpss_harm"] = _pearson(oracle["vocals_abs"], harm)
    rec["share_minus_abs_mix_r_drums"] = rec["r_drums_abs_vs_mix"] - rec["r_drums_share_vs_mix"]
    rec["share_minus_abs_mix_r_vocals"] = rec["r_vocals_abs_vs_mix"] - rec["r_vocals_share_vs_mix"]
    rec["share_minus_abs_mix_r_bass"] = rec["r_bass_abs_vs_mix"] - rec["r_bass_share_vs_mix"]
    return rec, oracle


def _mean(rows: list[dict], key: str) -> float:
    xs = [r[key] for r in rows if r.get(key) is not None and np.isfinite(r[key])]
    return float(np.mean(xs)) if xs else float("nan")


def write_visual(selected: list[tuple[dict, dict]]) -> None:
    from edgeai.mir.visual_hook import MODULATION_WEIGHT, modulate, per_song_norm

    payload = {}
    meta = []
    for rec, oracle in selected:
        t = [float(x) for x in oracle["times"]]
        base = per_song_norm([float(x) for x in oracle["mix_rms"]])
        # A is the un-boosted baseline: use a dim mix so B's extra is visible.
        a = [0.35 * v for v in base]
        b = modulate(a, base)
        c = modulate(a, per_song_norm([float(x) for x in oracle["drums_abs"]]))
        d = modulate(a, per_song_norm([float(x) for x in oracle["drums_share"]]))
        key = rec["track"]
        payload[key] = {"t": t, "A": a, "B": b, "C": c, "D": d}
        meta.append(
            {
                "id": key,
                "r_abs": rec["r_drums_abs_vs_mix"],
                "r_share": rec["r_drums_share_vs_mix"],
            }
        )
    out_html = Path("docs/mir/visual_replay/source_abcd.html")
    out_html.parent.mkdir(parents=True, exist_ok=True)
    w = MODULATION_WEIGHT
    cards = []
    for m in meta:
        sid = m["id"]
        cards.append(
            f"""
  <article class="card">
    <h2>{sid}</h2>
    <p class="nums">r(drums_abs, mix)={m['r_abs']:.2f} · r(drums_share, mix)={m['r_share']:.2f} · w={w}</p>
    <div class="lbl">A · baseline</div><canvas class="lgp" data-id="{sid}" data-src="A"></canvas>
    <div class="lbl">B · extra from mix energy</div><canvas class="lgp" data-id="{sid}" data-src="B"></canvas>
    <div class="lbl">C · extra from drums_abs (perfect presence)</div><canvas class="lgp" data-id="{sid}" data-src="C"></canvas>
    <div class="lbl">D · extra from drums_share (perfect dominance)</div><canvas class="lgp" data-id="{sid}" data-src="D"></canvas>
    <canvas class="plot" data-id="{sid}"></canvas>
    <p class="verdict">7 s MUSDB sample. Plumbing, not a product lighting judgement.</p>
  </article>"""
        )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>P3-A source A/B/C/D — HOST-ONLY plumbing</title>
<style>
  :root {{ --bg:#101010; --ink:#eee; --muted:#9a9a9a; }}
  body {{ margin:0; background:var(--bg); color:var(--ink); font:14px/1.45 ui-sans-serif, system-ui; }}
  header {{ padding:20px 22px 8px; max-width:1100px; }}
  h1 {{ font-size:20px; margin:0 0 8px; }}
  .sub,.nums,.lbl,.verdict {{ color:var(--muted); font-size:12px; }}
  .map {{ font-family: ui-monospace, monospace; font-size:12px; background:#1a1a1a; padding:10px 12px; border-radius:8px; }}
  .grid {{ display:grid; grid-template-columns:1fr; gap:16px; padding:12px 22px 28px; max-width:1100px; }}
  @media (min-width: 980px) {{ .grid {{ grid-template-columns:1fr 1fr; }} }}
  .card {{ background:#181818; border:1px solid #2a2a2a; border-radius:10px; padding:14px; }}
  canvas.lgp {{ width:100%; height:44px; display:block; border-radius:5px; }}
  canvas.plot {{ width:100%; height:130px; display:block; background:#0d0d0d; border-radius:6px; margin-top:10px; }}
  h2 {{ font-size:14px; margin:0 0 4px; }}
</style>
</head>
<body>
<header>
  <h1>P3-A · does perfect source dominance differ from mix energy?</h1>
  <p class="sub">MUSDB official 7-second samples. HOST-ONLY. Not K1 firmware. Not a student.
  Same extra mix as the arousal control: A baseline, B mix energy, C drums_abs, D drums_share.</p>
  <div class="map">A = 0.35·mix_rms<br/>B = (1−{w})·A + {w}·mix_rms<br/>C = (1−{w})·A + {w}·drums_abs<br/>D = (1−{w})·A + {w}·drums_share<br/>Research/NC sample audio. Do not train a shipping model on this.</div>
</header>
<div class="grid">{''.join(cards)}</div>
<script>
const DATA = {json.dumps(payload)};
const META = {json.dumps(meta)};
const COL = {{A:'#8a8a8a', B:'#3d8bfd', C:'#e24a4a', D:'#3dcea8'}};
function paint(id) {{
  const d = DATA[id];
  const plot = document.querySelector('canvas.plot[data-id="'+id+'"]');
  const pctx = plot.getContext('2d');
  const W = plot.width = plot.clientWidth * 2;
  const H = plot.height = plot.clientHeight * 2;
  pctx.fillStyle = '#0d0d0d'; pctx.fillRect(0,0,W,H);
  const n = d.t.length, t0 = d.t[0], t1 = d.t[n-1];
  const x = i => (d.t[i]-t0)/Math.max(t1-t0,1e-6)*W;
  const y = v => (1-v)*(H-8)+4;
  for (const k of ['A','B','C','D']) {{
    pctx.beginPath();
    d[k].forEach((v,i) => i?pctx.lineTo(x(i), y(v)):pctx.moveTo(x(i), y(v)));
    pctx.strokeStyle = COL[k]; pctx.lineWidth = k==='D' ? 2.4 : 2; pctx.stroke();
  }}
  document.querySelectorAll('canvas.lgp[data-id="'+id+'"]').forEach(cv => {{
    const ctx = cv.getContext('2d');
    const w = cv.width = cv.clientWidth * 2;
    const h = cv.height = cv.clientHeight * 2;
    const key = cv.dataset.src;
    const grad = ctx.createLinearGradient(0,0,w,0);
    for (let i=0;i<n;i++) {{
      const v = d[key][i];
      const c = Math.round(18 + v*220);
      let col = `rgb(${{c}},${{c}},${{c}})`;
      if (key==='B') col = `rgb(${{Math.round(c*0.35)}},${{Math.round(c*0.55)}},${{c}})`;
      if (key==='C') col = `rgb(${{c}},${{Math.round(c*0.22)}},${{Math.round(c*0.18)}})`;
      if (key==='D') col = `rgb(${{Math.round(c*0.2)}},${{c}},${{Math.round(c*0.7)}})`;
      grad.addColorStop(n===1?0:i/(n-1), col);
    }}
    ctx.fillStyle = grad; ctx.fillRect(0,0,w,h);
  }});
}}
META.forEach(m => paint(m.id));
</script>
</body>
</html>
"""
    out_html.write_text(html)
    print(f"wrote {out_html}")


def main() -> int:
    mus = _load_db()
    print(f"musdb sample tracks={len(mus)} root={ROOT.resolve()}", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    traces = OUT / "traces_musdb_sample"
    traces.mkdir(exist_ok=True)
    rows = []
    oracles = []
    for i, track in enumerate(mus):
        rec, oracle = analyse_track(track)
        rows.append(rec)
        oracles.append(oracle)
        print(
            f"{i:03d} {track.name!r} r_drums_abs={rec['r_drums_abs_vs_mix']:.3f} "
            f"r_drums_share={rec['r_drums_share_vs_mix']:.3f}",
            flush=True,
        )

    # Traces: largest |share vs mix − abs vs mix| — the interesting plumbing cases.
    ranked = sorted(
        range(len(rows)),
        key=lambda i: abs(rows[i]["share_minus_abs_mix_r_drums"])
        + abs(rows[i]["share_minus_abs_mix_r_vocals"]),
        reverse=True,
    )
    selected_idx = ranked[:TRACE_LIMIT]
    for i in selected_idx:
        rec, oracle = rows[i], oracles[i]
        frames = []
        n = len(oracle["times"])
        for k in range(n):
            fr = {"t": float(oracle["times"][k]), "rms": float(oracle["mix_rms"][k])}
            for name in ("vocals", "drums", "bass"):
                fr[f"{name}_abs"] = float(oracle[f"{name}_abs"][k])
                fr[f"{name}_share"] = float(oracle[f"{name}_share"][k])
                fr[f"{name}_delta"] = float(oracle[f"{name}_delta"][k])
            frames.append(fr)
        safe = rec["track"].replace("/", "_").replace(" ", "_")
        write_trace(
            traces / f"{safe}.jsonl",
            audio=f"musdb_sample:{rec['track']}",
            provenance=["musdb_sample_7s", "source_oracle.abs_share_delta"],
            frames=frames,
            extra_header={
                "track": rec["track"],
                "corpus": "musdb_sample_7s",
                "commercial_training_lineage": False,
                "signals": {
                    "drums_abs": {
                        "meaning": "absolute drum-stem energy, log-RMS D7 map",
                        "range": "[0,1]",
                        "cadence_hz": SR / HOP,
                        "smoothing": "none",
                        "provenance": "MUSDB sample stem RMS",
                    },
                    "drums_share": {
                        "meaning": "drum power / sum of stem powers",
                        "range": "[0,1]",
                        "cadence_hz": SR / HOP,
                        "smoothing": "none",
                        "provenance": "MUSDB sample stems",
                    },
                    "drums_delta": {
                        "meaning": "first difference of drums_share",
                        "range": "[-1,1]",
                        "cadence_hz": SR / HOP,
                        "smoothing": "none",
                    },
                },
            },
        )

    summary = {
        "n_tracks": len(rows),
        "mean_r_vocals_abs_vs_mix": _mean(rows, "r_vocals_abs_vs_mix"),
        "mean_r_vocals_share_vs_mix": _mean(rows, "r_vocals_share_vs_mix"),
        "mean_r_drums_abs_vs_mix": _mean(rows, "r_drums_abs_vs_mix"),
        "mean_r_drums_share_vs_mix": _mean(rows, "r_drums_share_vs_mix"),
        "mean_r_bass_abs_vs_mix": _mean(rows, "r_bass_abs_vs_mix"),
        "mean_r_bass_share_vs_mix": _mean(rows, "r_bass_share_vs_mix"),
        "mean_r_drums_abs_vs_hpss_perc": _mean(rows, "r_drums_abs_vs_hpss_perc"),
        "mean_r_drums_share_vs_hpss_perc": _mean(rows, "r_drums_share_vs_hpss_perc"),
        "mean_r_drums_abs_vs_onset": _mean(rows, "r_drums_abs_vs_onset"),
        "frac_share_less_redundant_than_abs_drums": float(
            np.mean([r["r_drums_share_vs_mix"] < r["r_drums_abs_vs_mix"] - 0.05 for r in rows])
        ),
        "frac_share_less_redundant_than_abs_vocals": float(
            np.mean([r["r_vocals_share_vs_mix"] < r["r_vocals_abs_vs_mix"] - 0.05 for r in rows])
        ),
    }
    receipt = {
        "label": "HOST-ONLY",
        "phase": "P3-A",
        "corpus": "musdb official 7s sample (not full MUSDB18)",
        "licence": "educational/non-commercial; commercial_training_lineage=false",
        "demucs_installed": False,
        "n_tracks": len(rows),
        "summary": summary,
        "trace_tracks": [rows[i]["track"] for i in selected_idx],
        "rows": rows,
    }
    (OUT / "receipt_musdb_sample.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    write_visual([(rows[i], oracles[i]) for i in selected_idx[:4]])
    print(f"wrote {OUT / 'receipt_musdb_sample.json'}")
    return 0 if rows else 2


if __name__ == "__main__":
    raise SystemExit(main())
