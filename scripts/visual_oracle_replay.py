#!/usr/bin/env python3
"""P5: isolated visual-oracle replay. Not production firmware.

Question: if arousal were perfect and realtime, would it drive lights
differently from RMS? High-residual DEAM 2034 vs energy-like 2030.
"""

from __future__ import annotations

import json
from pathlib import Path

from edgeai.mir.semantic_trace import read_trace

TRACES = {
    2030: Path("artifacts/deam_arousal/traces/deam_2030.jsonl"),
    2034: Path("artifacts/deam_arousal/traces/deam_2034.jsonl"),
}
OUT_HTML = Path("docs/mir/visual_replay/index.html")
OUT_PNG = Path("docs/mir/figures/visual_oracle_replay.png")


def _load(sid: int) -> tuple[list[float], list[float], list[float]]:
    header, frames = read_trace(TRACES[sid])
    t = [float(f["t"]) for f in frames]
    a = [float(f.get("arousal", 0.0)) for f in frames]
    r = [float(f.get("rms", 0.0)) for f in frames]
    return t, a, r


def _norm(xs: list[float]) -> list[float]:
    lo, hi = min(xs), max(xs)
    span = (hi - lo) or 1.0
    return [(x - lo) / span for x in xs]


def write_png(data: dict) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 1, figsize=(11, 6.2), sharex=False)
    fig.suptitle("HOST-ONLY  ·  if arousal were perfect, would the lights differ from RMS?", fontsize=12)
    for ax, sid, label in (
        (axes[0], 2030, "2030  ·  energy-like  (human arousal ≈ RMS, r≈0.81)"),
        (axes[1], 2034, "2034  ·  residual  (human arousal ≉ RMS, R²_energy≈0.02)"),
    ):
        t, a, r = data[sid]["t"], data[sid]["a_n"], data[sid]["r_n"]
        ax.plot(t, r, color="#888888", lw=1.4, label="RMS (existing lights proxy)")
        ax.plot(t, a, color="#c43c3c", lw=1.6, label="human arousal (oracle)")
        ax.fill_between(t, r, a, color="#c43c3c", alpha=0.18)
        ax.set_ylabel("0–1 (per-song)")
        ax.set_title(label, loc="left", fontsize=10)
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, alpha=0.25)
        ax.legend(loc="upper right", fontsize=8)
    axes[1].set_xlabel("time (s)  ·  DEAM annotations start ~15 s")
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=140)
    plt.close(fig)


def write_html(data: dict) -> None:
    payload = {
        sid: {"t": d["t"], "arousal": d["a_n"], "rms": d["r_n"]} for sid, d in data.items()
    }
    blob = json.dumps(payload)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>EdgeAI visual oracle replay — HOST-ONLY</title>
<style>
  :root {{ --bg:#111; --ink:#eee; --muted:#9a9a9a; --rms:#8a8a8a; --aro:#e24a4a; }}
  body {{ margin:0; background:var(--bg); color:var(--ink); font:14px/1.4 ui-sans-serif, system-ui; }}
  header {{ padding:18px 22px 8px; }}
  h1 {{ font-size:18px; margin:0 0 6px; }}
  .sub {{ color:var(--muted); max-width:820px; }}
  .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; padding:12px 22px 24px; }}
  .card {{ background:#1b1b1b; border:1px solid #2a2a2a; border-radius:10px; padding:14px; }}
  canvas.lgp {{ width:100%; height:72px; display:block; border-radius:6px; }}
  canvas.plot {{ width:100%; height:160px; display:block; background:#101010; border-radius:6px; }}
  .row {{ display:flex; gap:10px; margin-top:8px; }}
  .sw {{ flex:1; height:28px; border-radius:4px; }}
  .lbl {{ color:var(--muted); font-size:12px; margin:8px 0 4px; }}
  .verdict {{ margin-top:10px; font-size:13px; }}
  kbd {{ background:#222; padding:1px 6px; border-radius:4px; }}
</style>
</head>
<body>
<header>
  <h1>Would a perfect arousal oracle change the lights?</h1>
  <p class="sub">Isolated diagnostic. Not K1 firmware. Left strip = brightness from RMS (what we already have).
  Right strip = brightness from human DEAM arousal (the oracle). Same song, same time.
  If the two strips look the same, do not train a student on that song.</p>
</header>
<div class="grid">
  <div class="card" id="c2030">
    <strong>2030 · energy-like</strong>
    <div class="lbl">RMS-driven strip</div>
    <canvas class="lgp" data-src="rms"></canvas>
    <div class="lbl">Arousal-driven strip</div>
    <canvas class="lgp" data-src="arousal"></canvas>
    <canvas class="plot"></canvas>
    <div class="verdict">Expect: similar motion. Arousal here is mostly energy.</div>
  </div>
  <div class="card" id="c2034">
    <strong>2034 · residual vs energy</strong>
    <div class="lbl">RMS-driven strip</div>
    <canvas class="lgp" data-src="rms"></canvas>
    <div class="lbl">Arousal-driven strip</div>
    <canvas class="lgp" data-src="arousal"></canvas>
    <canvas class="plot"></canvas>
    <div class="verdict">Expect: different motion if the oracle is visually useful.
    Grey fill in the plot is the disagreement.</div>
  </div>
</div>
<script>
const DATA = {blob};
function paint(card, sid) {{
  const d = DATA[sid];
  const plots = card.querySelector('canvas.plot');
  const pctx = plots.getContext('2d');
  const W = plots.width = plots.clientWidth * 2;
  const H = plots.height = plots.clientHeight * 2;
  pctx.fillStyle = '#101010'; pctx.fillRect(0,0,W,H);
  const n = d.t.length;
  const t0 = d.t[0], t1 = d.t[n-1];
  function x(i) {{ return (d.t[i]-t0)/(t1-t0) * W; }}
  function y(v) {{ return (1-v) * (H-8) + 4; }}
  pctx.beginPath();
  d.rms.forEach((v,i) => {{ i?pctx.lineTo(x(i), y(v)):pctx.moveTo(x(i), y(v)); }});
  pctx.strokeStyle = '#8a8a8a'; pctx.lineWidth = 2; pctx.stroke();
  pctx.beginPath();
  d.arousal.forEach((v,i) => {{ i?pctx.lineTo(x(i), y(v)):pctx.moveTo(x(i), y(v)); }});
  pctx.strokeStyle = '#e24a4a'; pctx.lineWidth = 2.4; pctx.stroke();
  const lgps = card.querySelectorAll('canvas.lgp');
  lgps.forEach(cv => {{
    const ctx = cv.getContext('2d');
    const w = cv.width = cv.clientWidth * 2;
    const h = cv.height = cv.clientHeight * 2;
    const key = cv.dataset.src;
    const grad = ctx.createLinearGradient(0,0,w,0);
    for (let i=0;i<n;i++) {{
      const v = d[key][i];
      const c = Math.round(20 + v*220);
      grad.addColorStop(i/(n-1), key==='rms' ? `rgb(${{c}},${{c}},${{c}})` : `rgb(${{c}},${{Math.round(c*0.25)}},${{Math.round(c*0.2)}})`);
    }}
    ctx.fillStyle = grad; ctx.fillRect(0,0,w,h);
  }});
}}
paint(document.getElementById('c2030'), 2030);
paint(document.getElementById('c2034'), 2034);
</script>
</body>
</html>
"""
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html)
    print(f"wrote {OUT_HTML}")


def main() -> int:
    data = {}
    for sid in (2030, 2034):
        if not TRACES[sid].is_file():
            print(f"missing {TRACES[sid]}")
            return 2
        t, a, r = _load(sid)
        data[sid] = {"t": t, "a_n": _norm(a), "r_n": _norm(r)}
    write_png(data)
    write_html(data)
    print(f"wrote {OUT_PNG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
