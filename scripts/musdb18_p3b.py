#!/usr/bin/env python3
"""P3-B: full MUSDB18. Oracle ranks events; then two visual questions.

P3-B1 continuous: A baseline, B mix RMS, C source abs, D source share.
P3-B2 events: existing onset/flux/novelty vs share-delta / composition_change.

HOST-ONLY. Standard STEMS, not HQ. No Demucs. No student.
commercial_training_lineage=false.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from edgeai.mir.conventional import extract_onset_bundle
from edgeai.mir.semantic_trace import write_trace
from edgeai.mir.source_oracle import SOURCES, source_oracle, timebase
from edgeai.mir.visual_hook import (
    FROZEN_MAP_VERSION,
    MODULATION_WEIGHT,
    apply_frozen_map,
    fit_frozen_map,
    modulate,
)

ROOT = Path("datasets/musdb18")
OUT = Path("artifacts/source_activity")
CACHE = OUT / "musdb18_oracle_cache"
SR = 16_000
HOP = 512
LAG_S = 0.5
SEED_NAMES = (
    "Fergessen - Back From The Start",
    "Hollow Ground - Ill Fate",
    "Helado Negro - Mitad Del Mundo",
)


def _mono(x: np.ndarray) -> np.ndarray:
    y = np.asarray(x, dtype=np.float32)
    if y.ndim == 2:
        y = y.mean(axis=-1)
    return y.reshape(-1)


def _pearson(a: np.ndarray, b: np.ndarray) -> float:
    n = min(len(a), len(b))
    if n < 8:
        return float("nan")
    a, b = np.asarray(a[:n], dtype=np.float64), np.asarray(b[:n], dtype=np.float64)
    if a.std() < 1e-12 or b.std() < 1e-12:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def _safe(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in name)


def load_db():
    import musdb

    train = ROOT / "train"
    nested = ROOT / "musdb18" / "train"
    root = ROOT / "musdb18" if nested.is_dir() and not train.is_dir() else ROOT
    if not (root / "train").is_dir():
        raise SystemExit(f"MUSDB18 train/ missing under {ROOT}. Run scripts/download_musdb.py --fetch")
    return musdb.DB(root=str(root.resolve()), is_wav=False, sample_rate=SR)


def oracle_for_track(track) -> dict[str, np.ndarray]:
    mix = _mono(track.audio)
    stems = {name: _mono(track.targets[name].audio) for name in SOURCES}
    return source_oracle(stems, sr=int(track.rate), hop=HOP, mix=mix)


def cache_path(track) -> Path:
    return CACHE / f"{track.subset}_{_safe(track.name)}.npz"


def load_or_compute(track) -> dict[str, np.ndarray]:
    path = cache_path(track)
    if path.is_file():
        data = np.load(path)
        return {k: data[k] for k in data.files}
    oracle = oracle_for_track(track)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **oracle)
    return oracle


def pooled_and_within(rows_oracles: list[tuple[dict, dict]]) -> dict:
    within: dict[str, list[float]] = {
        "vocals_abs": [],
        "vocals_share": [],
        "drums_abs": [],
        "drums_share": [],
        "bass_abs": [],
        "bass_share": [],
    }
    pooled = {k: [] for k in within}
    pooled_mix = []
    for rec, oracle in rows_oracles:
        mix = oracle["mix_rms"]
        pooled_mix.append(mix)
        for src in ("vocals", "drums", "bass"):
            within[f"{src}_abs"].append(_pearson(oracle[f"{src}_abs"], mix))
            within[f"{src}_share"].append(_pearson(oracle[f"{src}_share"], mix))
            pooled[f"{src}_abs"].append(oracle[f"{src}_abs"])
            pooled[f"{src}_share"].append(oracle[f"{src}_share"])
    mix_all = np.concatenate(pooled_mix)
    out = {}
    for key, series in within.items():
        xs = [x for x in series if np.isfinite(x)]
        out[f"within_mean_r_{key}_vs_mix"] = float(np.mean(xs)) if xs else float("nan")
        src, kind = key.rsplit("_", 1)
        arr = np.concatenate(pooled[key])
        out[f"pooled_r_{key}_vs_mix"] = _pearson(arr, mix_all)
    return out


def event_scores(oracle: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    mix = oracle["mix_rms"].astype(np.float64)
    d_rms = np.abs(np.diff(mix, prepend=mix[:1]))
    cc = oracle["composition_change"].astype(np.float64)
    out = {
        "d_rms": d_rms,
        "composition_change": cc,
        "loudness_without_composition": d_rms - cc,
        "composition_without_loudness": cc - d_rms,
    }
    for src in ("vocals", "drums", "bass"):
        d_share = np.abs(oracle[f"{src}_delta"].astype(np.float64))
        out[f"{src}_ownership_change"] = d_share - d_rms
        out[f"{src}_dominance"] = oracle[f"{src}_share"].astype(np.float64) - mix
    return out


def rank_events(items: list[tuple[dict, dict]]) -> dict[str, list[dict]]:
    classes = (
        "vocals_ownership_change",
        "drums_ownership_change",
        "bass_dominance",
        "composition_without_loudness",
        "loudness_without_composition",
    )
    ranked: dict[str, list[dict]] = {c: [] for c in classes}
    for rec, oracle in items:
        sc = event_scores(oracle)
        t = oracle["times"]
        for cls, key in (
            ("vocals_ownership_change", "vocals_ownership_change"),
            ("drums_ownership_change", "drums_ownership_change"),
            ("bass_dominance", "bass_dominance"),
            ("composition_without_loudness", "composition_without_loudness"),
            ("loudness_without_composition", "loudness_without_composition"),
        ):
            arr = sc[key]
            i = int(np.argmax(arr))
            ranked[cls].append(
                {
                    "track": rec["track"],
                    "subset": rec["subset"],
                    "t": float(t[i]),
                    "score": float(arr[i]),
                    "p95": float(np.percentile(arr, 95)),
                    "source": "vocals" if "vocals" in cls else "drums" if "drums" in cls else "bass" if "bass" in cls else "composition",
                }
            )
    for cls in ranked:
        ranked[cls].sort(key=lambda r: r["score"], reverse=True)
    return ranked


def select_balanced(ranked: dict[str, list[dict]], k_per: int = 4) -> list[dict]:
    chosen: dict[str, dict] = {}
    for cls, rows in ranked.items():
        n = 0
        for row in rows:
            if row["track"] in chosen:
                chosen[row["track"]]["classes"].append(cls)
                continue
            if n >= k_per:
                continue
            chosen[row["track"]] = {**row, "classes": [cls], "select_class": cls}
            n += 1
    for seed in SEED_NAMES:
        if seed in chosen:
            chosen[seed]["seed_check"] = True
    return list(chosen.values())


def write_b1_html(selected: list[dict], lookup: dict[str, dict], fmap: dict) -> None:
    payload = {}
    meta = []
    for row in selected:
        oracle = lookup[row["track"]]
        src = row["source"] if row["source"] in ("vocals", "drums", "bass") else "vocals"
        onset = apply_frozen_map(oracle["mix_rms"], fmap["mix_rms"])  # A uses mix as existing energy spine
        # Existing-behaviour stand-in: frozen mix_rms dimmed — onset is added in B2.
        a = [0.35 * v for v in onset]
        b = modulate(a, apply_frozen_map(oracle["mix_rms"], fmap["mix_rms"]))
        c = modulate(a, apply_frozen_map(oracle[f"{src}_abs"], fmap[f"{src}_abs"]))
        d = modulate(a, apply_frozen_map(oracle[f"{src}_share"], fmap[f"{src}_share"]))
        payload[row["track"]] = _thin_payload(
            {
                "t": [float(x) for x in oracle["times"]],
                "A": a,
                "B": b,
                "C": c,
                "D": d,
            }
        )
        meta.append(
            {
                "id": row["track"],
                "cls": row["select_class"],
                "src": src,
                "t_event": row["t"],
                "score": row["score"],
            }
        )
    _write_html(
        Path("docs/mir/visual_replay/p3b1_continuous.html"),
        title="P3-B1 · continuous abs vs share vs RMS",
        sub="Same extra mix. Frozen 5th–95th corpus map, not per-song min-max. HOST-ONLY full MUSDB18.",
        mapping=(
            f"frozen map {FROZEN_MAP_VERSION} · w={MODULATION_WEIGHT}<br/>"
            "A = 0.35·frozen(mix_rms)<br/>"
            "B = (1−w)·A + w·frozen(mix_rms)<br/>"
            "C = (1−w)·A + w·frozen(source_abs)<br/>"
            "D = (1−w)·A + w·frozen(source_share)"
        ),
        payload=payload,
        meta=meta,
        keys=("A", "B", "C", "D"),
        colours={"A": "#8a8a8a", "B": "#3d8bfd", "C": "#e24a4a", "D": "#3dcea8"},
    )


def write_b2_html(selected: list[dict], lookup: dict[str, dict], fmap: dict) -> None:
    payload = {}
    meta = []
    for row in selected:
        oracle = lookup[row["track"]]
        src = row["source"] if row["source"] in ("vocals", "drums", "bass") else "drums"
        # Re-extract onset/novelty on mix for event overlay — selected set only.
        payload[row["track"]] = _thin_payload(
            {
                "t": [float(x) for x in oracle["times"]],
                "A": apply_frozen_map(np.abs(np.diff(oracle["mix_rms"], prepend=oracle["mix_rms"][:1])), fmap["d_rms"]),
                "B": apply_frozen_map(np.abs(oracle[f"{src}_delta"]), fmap[f"{src}_delta_abs"]),
                "C": apply_frozen_map(oracle["composition_change"], fmap["composition_change"]),
            }
        )
        meta.append({"id": row["track"], "cls": row["select_class"], "src": src, "t_event": row["t"]})
    _write_html(
        Path("docs/mir/visual_replay/p3b2_events.html"),
        title="P3-B2 · did the arrangement change?",
        sub="A = |Δ mix_rms|. B = |source share delta|. C = composition_change. Frozen maps. HOST-ONLY.",
        mapping=(
            f"frozen map {FROZEN_MAP_VERSION}<br/>"
            "A = frozen(|Δ mix_rms|)<br/>"
            "B = frozen(|source_delta|)<br/>"
            "C = frozen(composition_change) · causal L1/2 over 0.5 s"
        ),
        payload=payload,
        meta=meta,
        keys=("A", "B", "C"),
        colours={"A": "#8a8a8a", "B": "#e24a4a", "C": "#3dcea8"},
    )


def _thin_payload(d: dict, *, step: int = 8) -> dict:
    """Display at ~4 Hz. Full hop traces stay in artifacts jsonl."""
    return {k: (v[::step] if isinstance(v, list) and k != "id" else v) for k, v in d.items()}


def _write_html(path: Path, *, title, sub, mapping, payload, meta, keys, colours) -> None:
    cards = []
    for m in meta:
        strips = "\n".join(
            f'<div class="lbl">{k}</div><canvas class="lgp" data-id="{m["id"]}" data-src="{k}"></canvas>'
            for k in keys
        )
        cards.append(
            f"""
  <article class="card">
    <h2>{m['id']}</h2>
    <p class="nums">{m.get('cls','')} · src={m.get('src','')} · t≈{m.get('t_event',0):.1f}s</p>
    {strips}
    <canvas class="plot" data-id="{m['id']}"></canvas>
  </article>"""
        )
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<title>{title}</title>
<style>
  :root {{ --bg:#101010; --ink:#eee; --muted:#9a9a9a; }}
  body {{ margin:0; background:var(--bg); color:var(--ink); font:14px/1.45 ui-sans-serif, system-ui; }}
  header {{ padding:20px 22px 8px; max-width:1100px; }}
  h1 {{ font-size:20px; margin:0 0 8px; }}
  .sub,.nums,.lbl {{ color:var(--muted); font-size:12px; }}
  .map {{ font-family:ui-monospace,monospace; font-size:12px; background:#1a1a1a; padding:10px 12px; border-radius:8px; }}
  .grid {{ display:grid; grid-template-columns:1fr; gap:16px; padding:12px 22px 28px; max-width:1100px; }}
  @media (min-width:980px) {{ .grid {{ grid-template-columns:1fr 1fr; }} }}
  .card {{ background:#181818; border:1px solid #2a2a2a; border-radius:10px; padding:14px; }}
  canvas.lgp {{ width:100%; height:40px; display:block; border-radius:5px; }}
  canvas.plot {{ width:100%; height:120px; display:block; background:#0d0d0d; border-radius:6px; margin-top:10px; }}
  h2 {{ font-size:13px; margin:0 0 4px; }}
</style></head><body>
<header>
  <h1>{title}</h1>
  <p class="sub">{sub} Not K1 firmware. Not a student. MUSDB educational/NC.</p>
  <div class="map">{mapping}</div>
</header>
<div class="grid">{''.join(cards)}</div>
<script>
const DATA = {json.dumps(payload)};
const META = {json.dumps(meta)};
const COL = {json.dumps(colours)};
const KEYS = {json.dumps(list(keys))};
function paint(id) {{
  const d = DATA[id];
  const plot = document.querySelector('canvas.plot[data-id="'+id+'"]');
  const pctx = plot.getContext('2d');
  const W = plot.width = plot.clientWidth*2, H = plot.height = plot.clientHeight*2;
  pctx.fillStyle='#0d0d0d'; pctx.fillRect(0,0,W,H);
  const n=d.t.length, t0=d.t[0], t1=d.t[n-1];
  const x=i=>(d.t[i]-t0)/Math.max(t1-t0,1e-6)*W;
  const y=v=>(1-v)*(H-8)+4;
  KEYS.forEach(k => {{
    pctx.beginPath();
    d[k].forEach((v,i)=>i?pctx.lineTo(x(i),y(v)):pctx.moveTo(x(i),y(v)));
    pctx.strokeStyle=COL[k]; pctx.lineWidth=2.2; pctx.stroke();
  }});
  document.querySelectorAll('canvas.lgp[data-id="'+id+'"]').forEach(cv => {{
    const ctx=cv.getContext('2d');
    const w=cv.width=cv.clientWidth*2, h=cv.height=cv.clientHeight*2;
    const key=cv.dataset.src;
    const grad=ctx.createLinearGradient(0,0,w,0);
    for (let i=0;i<n;i++) {{
      const v=d[key][i], c=Math.round(18+v*220);
      let col=`rgb(${{c}},${{c}},${{c}})`;
      if(key==='B') col=`rgb(${{Math.round(c*0.35)}},${{Math.round(c*0.55)}},${{c}})`;
      if(key==='C') col=`rgb(${{c}},${{Math.round(c*0.22)}},${{Math.round(c*0.18)}})`;
      if(key==='D' || key==='C' && KEYS.indexOf('D')<0) col=`rgb(${{Math.round(c*0.2)}},${{c}},${{Math.round(c*0.7)}})`;
      grad.addColorStop(n===1?0:i/(n-1), col);
    }}
    ctx.fillStyle=grad; ctx.fillRect(0,0,w,h);
  }});
}}
META.forEach(m => paint(m.id));
</script></body></html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html)
    print(f"wrote {path}")


def main() -> int:
    mus = load_db()
    print(f"MUSDB18 tracks={len(mus)}", flush=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    items = []
    series: dict[str, list[np.ndarray]] = {
        "mix_rms": [],
        "d_rms": [],
        "composition_change": [],
        "vocals_abs": [],
        "vocals_share": [],
        "vocals_delta_abs": [],
        "drums_abs": [],
        "drums_share": [],
        "drums_delta_abs": [],
        "bass_abs": [],
        "bass_share": [],
        "bass_delta_abs": [],
    }
    lookup = {}
    recs = []
    for i, track in enumerate(mus):
        oracle = load_or_compute(track)
        rec = {
            "track": track.name,
            "subset": getattr(track, "subset", ""),
            "duration_s": float(oracle["times"][-1]) if len(oracle["times"]) else 0.0,
            "n_hops": int(oracle["times"].size),
        }
        recs.append(rec)
        items.append((rec, oracle))
        lookup[track.name] = oracle
        d_rms = np.abs(np.diff(oracle["mix_rms"], prepend=oracle["mix_rms"][:1]))
        series["mix_rms"].append(oracle["mix_rms"])
        series["d_rms"].append(d_rms)
        series["composition_change"].append(oracle["composition_change"])
        for src in ("vocals", "drums", "bass"):
            series[f"{src}_abs"].append(oracle[f"{src}_abs"])
            series[f"{src}_share"].append(oracle[f"{src}_share"])
            series[f"{src}_delta_abs"].append(np.abs(oracle[f"{src}_delta"]))
        print(f"{i:03d} {track.subset} {track.name} hops={rec['n_hops']}", flush=True)

    cat = {k: np.concatenate(v) for k, v in series.items()}
    fmap = fit_frozen_map(cat)
    fmap_path = OUT / "frozen_map_p3b.json"
    fmap_path.write_text(
        json.dumps({"version": FROZEN_MAP_VERSION, "timebase": timebase(sr=SR, hop=HOP, lag_s=LAG_S), "map": fmap}, indent=2)
        + "\n"
    )
    corr = pooled_and_within(items)
    ranked = rank_events(items)
    selected = select_balanced(ranked, k_per=4)
    print("selected", [s["track"] for s in selected], flush=True)

    traces = OUT / "traces_musdb18"
    traces.mkdir(exist_ok=True)
    for row in selected:
        oracle = lookup[row["track"]]
        frames = []
        for k in range(len(oracle["times"])):
            fr = {"t": float(oracle["times"][k]), "rms": float(oracle["mix_rms"][k]), "composition_change": float(oracle["composition_change"][k])}
            for src in ("vocals", "drums", "bass"):
                fr[f"{src}_abs"] = float(oracle[f"{src}_abs"][k])
                fr[f"{src}_share"] = float(oracle[f"{src}_share"][k])
                fr[f"{src}_delta"] = float(oracle[f"{src}_delta"][k])
            frames.append(fr)
        write_trace(
            traces / f"{_safe(row['track'])}.jsonl",
            audio=f"musdb18:{row['track']}",
            provenance=["musdb18_stems", "source_oracle.abs_share_delta", "composition_change"],
            frames=frames,
            extra_header={
                "track": row["track"],
                "select_class": row["select_class"],
                "commercial_training_lineage": False,
                "timebase": timebase(sr=SR, hop=HOP, lag_s=LAG_S),
                "frozen_map_version": FROZEN_MAP_VERSION,
                "signals": {
                    "vocals_share": {"range": "[0,1] stem-power fraction", "cadence_hz": SR / HOP, "smoothing": "none", "alignment": "hop-centre"},
                    "composition_change": {"range": "[0,1] causal L1/2 over 0.5s", "lookahead_s": 0.0},
                },
            },
        )

    write_b1_html(selected, lookup, fmap)
    write_b2_html(selected, lookup, fmap)

    top = {cls: rows[:5] for cls, rows in ranked.items()}
    receipt = {
        "label": "HOST-ONLY",
        "phase": "P3-B",
        "corpus": "MUSDB18 standard STEMS (not HQ)",
        "licence": "educational/NC; commercial_training_lineage=false",
        "n_tracks": len(recs),
        "timebase": timebase(sr=SR, hop=HOP, lag_s=LAG_S),
        "frozen_map_version": FROZEN_MAP_VERSION,
        "frozen_map": str(fmap_path),
        "correlations": corr,
        "selected": selected,
        "top_events": top,
        "seed_present": [n for n in SEED_NAMES if n in lookup],
        "demucs_installed": False,
    }
    outp = OUT / "receipt_musdb18_p3b.json"
    outp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"n": len(recs), **corr, "n_selected": len(selected)}, indent=2))
    print(f"wrote {outp}")
    return 0 if recs else 2


if __name__ == "__main__":
    raise SystemExit(main())
