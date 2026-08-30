#!/usr/bin/env python3
"""A / B / C visual-oracle replay. Not production firmware.

A — baseline: existing deterministic proxy (onset envelope)
B — same extra degree of freedom driven by RMS
C — same extra degree of freedom driven by human DEAM arousal

If B and C look the same, arousal is not earning a student.
"""

from __future__ import annotations

import json
from pathlib import Path

from edgeai.mir.semantic_trace import read_trace
from edgeai.mir.visual_hook import MODULATION_WEIGHT, modulate, per_song_norm

TRACES = Path("artifacts/deam_arousal/traces")
OUT_HTML = Path("docs/mir/visual_replay/index.html")
OUT_PNG = Path("docs/mir/figures/visual_oracle_replay.png")

# 2015 full songs. Two energy-like controls, three residuals.
SONGS = (
    (2030, "control · arousal ≈ RMS", 0.81, 0.76),
    (2028, "control · arousal ≈ RMS", 0.80, 0.70),
    (2034, "residual · arousal ≉ energy", 0.10, 0.02),
    (2041, "residual · arousal ≉ energy", 0.07, 0.03),
    (2056, "residual · arousal ≉ energy", -0.07, 0.04),
)


def _load(sid: int) -> dict:
    header, frames = read_trace(TRACES / f"deam_{sid}.jsonl")
    t = [float(f["t"]) for f in frames]
    onset = per_song_norm([float(f.get("onset", 0.0)) for f in frames])
    rms = per_song_norm([float(f.get("rms", 0.0)) for f in frames])
    arousal = per_song_norm([float(f.get("arousal", 0.0)) for f in frames])
    a = onset  # baseline: deterministic attack proxy
    b = modulate(onset, rms)
    c = modulate(onset, arousal)
    return {
        "t": t,
        "A": a,
        "B": b,
        "C": c,
        "onset": onset,
        "rms": rms,
        "arousal": arousal,
        "header": header,
    }


def write_png(bundle: dict) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    n = len(SONGS)
    fig, axes = plt.subplots(n, 1, figsize=(12.2, 2.15 * n), sharex=False)
    if n == 1:
        axes = [axes]
    fig.suptitle(
        f"HOST-ONLY  ·  A baseline onset  ·  B +RMS  ·  C +arousal  ·  same mix w={MODULATION_WEIGHT}",
        fontsize=11,
    )
    colours = {"A": "#8a8a8a", "B": "#3d8bfd", "C": "#e24a4a"}
    for ax, (sid, role, r, r2) in zip(axes, SONGS):
        d = bundle[sid]
        t = d["t"]
        ax.plot(t, d["A"], color=colours["A"], lw=1.1, label="A baseline (onset)")
        ax.plot(t, d["B"], color=colours["B"], lw=1.3, label="B + RMS extra")
        ax.plot(t, d["C"], color=colours["C"], lw=1.5, label="C + arousal extra")
        ax.set_ylabel("0–1")
        ax.set_title(f"{sid}  ·  {role}  ·  r(arousal,RMS)={r:.2f}  R²_energy={r2:.2f}", loc="left", fontsize=9)
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, alpha=0.25)
        ax.legend(loc="upper right", fontsize=7, ncol=3)
    axes[-1].set_xlabel("time (s)  ·  DEAM annotations start ~15 s")
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=130)
    plt.close(fig)


def write_html(bundle: dict) -> None:
    payload = {}
    meta = []
    for sid, role, r, r2 in SONGS:
        d = bundle[sid]
        payload[sid] = {"t": d["t"], "A": d["A"], "B": d["B"], "C": d["C"]}
        meta.append({"sid": sid, "role": role, "r": r, "r2": r2})
    blob = json.dumps(payload)
    meta_blob = json.dumps(meta)
    w = MODULATION_WEIGHT
    cards = []
    for sid, role, r, r2 in SONGS:
        cards.append(
            f"""
  <article class="card" id="c{sid}">
    <h2>{sid} <span>{role}</span></h2>
    <p class="nums">r(arousal, RMS) = {r:.2f} · R² energy = {r2:.2f} · mix w = {w}</p>
    <div class="lbl">A · baseline (onset only)</div>
    <canvas class="lgp" data-src="A"></canvas>
    <div class="lbl">B · extra DoF from RMS (energy control)</div>
    <canvas class="lgp" data-src="B"></canvas>
    <div class="lbl">C · extra DoF from human arousal (oracle)</div>
    <canvas class="lgp" data-src="C"></canvas>
    <canvas class="plot"></canvas>
    <p class="verdict">{'Expect B ≈ C. If they match, arousal is not adding a visual job.' if r > 0.6 else 'Expect C to diverge from B. If it does not, the residual is not visually usable.'}</p>
  </article>"""
        )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>EdgeAI A/B/C visual oracle — HOST-ONLY</title>
<style>
  :root {{ --bg:#101010; --ink:#eee; --muted:#9a9a9a; --a:#8a8a8a; --b:#3d8bfd; --c:#e24a4a; }}
  body {{ margin:0; background:var(--bg); color:var(--ink); font:14px/1.45 ui-sans-serif, system-ui; }}
  header {{ padding:20px 22px 8px; max-width:1100px; }}
  h1 {{ font-size:20px; margin:0 0 8px; }}
  .sub {{ color:var(--muted); }}
  .map {{ font-family: ui-monospace, monospace; font-size:12px; color:#cfcfcf; background:#1a1a1a; padding:10px 12px; border-radius:8px; margin-top:10px; }}
  .grid {{ display:grid; grid-template-columns:1fr; gap:16px; padding:12px 22px 28px; max-width:1100px; }}
  @media (min-width: 980px) {{ .grid {{ grid-template-columns:1fr 1fr; }} }}
  .card {{ background:#181818; border:1px solid #2a2a2a; border-radius:10px; padding:14px; }}
  h2 {{ font-size:15px; margin:0 0 4px; }}
  h2 span {{ color:var(--muted); font-weight:400; }}
  .nums, .lbl, .verdict {{ color:var(--muted); font-size:12px; }}
  .lbl {{ margin:8px 0 4px; }}
  canvas.lgp {{ width:100%; height:52px; display:block; border-radius:5px; }}
  canvas.plot {{ width:100%; height:140px; display:block; background:#0d0d0d; border-radius:6px; margin-top:10px; }}
  .verdict {{ margin-top:8px; }}
  kbd {{ background:#222; padding:1px 6px; border-radius:4px; }}
</style>
</head>
<body>
<header>
  <h1>Does perfect arousal change the lights more than extra energy?</h1>
  <p class="sub">Isolated diagnostic. Not K1 firmware. Condition A is the deterministic onset proxy.
  B and C add <em>the same</em> extra degree of freedom — only the driver changes.
  Visual judgement is the product call; this page is the evidence, not the verdict.</p>
  <div class="map">A = onset<br/>B = (1−{w})·onset + {w}·RMS<br/>C = (1−{w})·onset + {w}·arousal<br/>Same weight, same mix, per-song 0–1. HOST-ONLY. DEAM 2015.</div>
</header>
<div class="grid">
{''.join(cards)}
</div>
<script>
const DATA = {blob};
const META = {meta_blob};
const COL = {{A:'#8a8a8a', B:'#3d8bfd', C:'#e24a4a'}};
function paint(card, sid) {{
  const d = DATA[sid];
  const plots = card.querySelector('canvas.plot');
  const pctx = plots.getContext('2d');
  const W = plots.width = plots.clientWidth * 2;
  const H = plots.height = plots.clientHeight * 2;
  pctx.fillStyle = '#0d0d0d'; pctx.fillRect(0,0,W,H);
  const n = d.t.length;
  const t0 = d.t[0], t1 = d.t[n-1];
  function x(i) {{ return (d.t[i]-t0)/(t1-t0) * W; }}
  function y(v) {{ return (1-v) * (H-8) + 4; }}
  for (const key of ['A','B','C']) {{
    pctx.beginPath();
    d[key].forEach((v,i) => {{ i?pctx.lineTo(x(i), y(v)):pctx.moveTo(x(i), y(v)); }});
    pctx.strokeStyle = COL[key]; pctx.lineWidth = key==='C' ? 2.4 : 2; pctx.stroke();
  }}
  card.querySelectorAll('canvas.lgp').forEach(cv => {{
    const ctx = cv.getContext('2d');
    const w = cv.width = cv.clientWidth * 2;
    const h = cv.height = cv.clientHeight * 2;
    const key = cv.dataset.src;
    const grad = ctx.createLinearGradient(0,0,w,0);
    for (let i=0;i<n;i++) {{
      const v = d[key][i];
      const c = Math.round(18 + v*220);
      let col;
      if (key==='A') col = `rgb(${{c}},${{c}},${{c}})`;
      else if (key==='B') col = `rgb(${{Math.round(c*0.35)}},${{Math.round(c*0.55)}},${{c}})`;
      else col = `rgb(${{c}},${{Math.round(c*0.22)}},${{Math.round(c*0.18)}})`;
      grad.addColorStop(n===1?0:i/(n-1), col);
    }}
    ctx.fillStyle = grad; ctx.fillRect(0,0,w,h);
  }});
}}
META.forEach(m => paint(document.getElementById('c'+m.sid), m.sid));
</script>
</body>
</html>
"""
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html)
    print(f"wrote {OUT_HTML}")


def main() -> int:
    bundle = {}
    for sid, *_ in SONGS:
        path = TRACES / f"deam_{sid}.jsonl"
        if not path.is_file():
            print(f"missing {path}")
            return 2
        bundle[sid] = _load(sid)
    write_png(bundle)
    write_html(bundle)
    print(f"wrote {OUT_PNG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
