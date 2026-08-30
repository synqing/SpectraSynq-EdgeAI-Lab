"""Blind-HTML leak scan and P3-C page writer. Version labels must not name the engine."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_LEAK_WORDS = (
    "ownership",
    "SHARE",
    "share",
    "RMS",
    "baseline",
    "mix energy",
    "composition_change",
    "BASELINE",
    "MAGICAL",
    "source_share",
    "source_abs",
)


def forbidden_version_leaks() -> tuple[str, ...]:
    return _LEAK_WORDS


def scan_blind_html(html: str) -> list[str]:
    leaks: list[str] = []
    for m in re.finditer(r"Version\s+\d+[^<\n]{0,80}", html, flags=re.IGNORECASE):
        chunk = m.group(0)
        for word in _LEAK_WORDS:
            if word in chunk:
                leaks.append(chunk)
                break
    return leaks


def write_page(
    path: Path,
    *,
    title: str,
    question: str,
    note: str,
    clips: list[dict[str, Any]],
    n_versions: int,
) -> Path:
    blob = json.dumps(clips, separators=(",", ":"))
    version_btns = "".join(
        f'<button type="button" data-solo="{i}">V{i + 1}</button>' for i in range(n_versions)
    )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title}</title>
<style>
  :root {{
    --paper:#f4efe6; --ink:#1b1814; --muted:#6a645c; --rule:#d9d0c3;
    --stage:#0c0b0a; --ledgap:#070707; --accent:#c45c26;
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--paper); color:var(--ink);
    font:15px/1.45 "Iowan Old Style", Palatino, "Palatino Linotype", serif; }}
  header {{ padding:28px 24px 12px; max-width:1080px; }}
  h1 {{ font-size:28px; font-weight:600; letter-spacing:-0.02em; margin:0 0 8px; }}
  .q {{ font-size:18px; max-width:42em; }}
  .note {{ color:var(--muted); font-size:13px; max-width:46em; }}
  .host {{ display:inline-block; font:12px/1.2 ui-monospace, Menlo, monospace;
    border:1px solid var(--rule); padding:3px 8px; margin:10px 0; }}
  .toolbar {{ display:flex; gap:8px; flex-wrap:wrap; align-items:center; padding:0 24px 12px; }}
  button {{ font:13px/1.2 ui-sans-serif, system-ui; background:#fff; border:1px solid var(--rule);
    padding:6px 10px; cursor:pointer; }}
  button[aria-pressed="true"] {{ background:var(--ink); color:var(--paper); }}
  .grid {{ padding:8px 24px 40px; display:flex; flex-direction:column; gap:22px; max-width:1080px; }}
  section h2 {{ font-size:13px; text-transform:uppercase; letter-spacing:0.12em; color:var(--muted); }}
  article {{ background:#fff; border:1px solid var(--rule); padding:14px 14px 16px; }}
  .who {{ font:12px/1.3 ui-sans-serif, system-ui; color:var(--muted); margin:0 0 10px; }}
  .stage {{ background:var(--stage); padding:10px; }}
  .row {{ margin:0 0 8px; }}
  .row:last-child {{ margin:0; }}
  .lbl {{ font:11px/1 ui-sans-serif, system-ui; color:#c8c2b8; margin:0 0 4px; letter-spacing:0.08em; }}
  canvas.strip {{ width:100%; height:28px; display:block; image-rendering:pixelated; background:var(--ledgap); }}
  canvas.plate {{ width:100%; height:72px; display:block; image-rendering:pixelated; background:#000; margin-top:4px; }}
  .rate {{ font:11px/1 ui-monospace, Menlo, monospace; color:#a39b90; float:right; }}
  .playhead {{ height:2px; background:var(--accent); width:0%; margin-top:8px; }}
</style>
</head>
<body>
<header>
  <div class="host">HOST-ONLY · not on-device · not a lighting verdict</div>
  <h1>{title}</h1>
  <p class="q">{question}</p>
  <p class="note">{note}</p>
</header>
<div class="toolbar">
  <button type="button" id="play">Play all</button>
  <button type="button" id="pause" aria-pressed="true">Pause</button>
  <span class="note" id="clock">0.0 s</span>
  <button type="button" data-solo="-1" aria-pressed="true">All versions</button>
  {version_btns}
</div>
<div class="grid" id="grid"></div>
<script>
const CLIPS = {blob};
const NVER = {n_versions};
let playing = false, t0 = 0, raf = 0, tAbs = 2.0, solo = -1;

function u8(b64) {{
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i=0;i<bin.length;i++) out[i] = bin.charCodeAt(i);
  return out;
}}
function frameRGB(u, fi, nLed) {{
  const off = fi * nLed * 3;
  return u.subarray(off, off + nLed * 3);
}}
function paintStrip(cv, rgb, nLed) {{
  const w = cv.width = nLed;
  const h = cv.height = 8;
  const ctx = cv.getContext('2d');
  const img = ctx.createImageData(w, h);
  for (let x=0;x<nLed;x++) {{
    const r=rgb[x*3], g=rgb[x*3+1], b=rgb[x*3+2];
    for (let y=0;y<h;y++) {{
      const o = (y*w + x)*4;
      img.data[o]=r; img.data[o+1]=g; img.data[o+2]=b; img.data[o+3]=255;
    }}
  }}
  ctx.putImageData(img, 0, 0);
}}
function paintPlate(cv, rgb, nLed) {{
  const w = cv.width = nLed;
  const h = cv.height = 36;
  const ctx = cv.getContext('2d');
  const img = ctx.createImageData(w, h);
  const centre = (nLed - 1) / 2;
  for (let y=0;y<h;y++) {{
    const fall = Math.pow(1 - y/(h-1), 1.45);
    for (let x=0;x<nLed;x++) {{
      const spread = 1 - Math.min(1, Math.abs(x-centre)/centre * 0.15);
      const o = (y*w + x)*4;
      img.data[o]   = Math.min(255, rgb[x*3]   * fall * spread);
      img.data[o+1] = Math.min(255, rgb[x*3+1] * fall * spread);
      img.data[o+2] = Math.min(255, rgb[x*3+2] * fall * spread);
      img.data[o+3] = 255;
    }}
  }}
  ctx.putImageData(img, 0, 0);
}}
function fiOf(clip, t) {{
  const fps = clip.fps;
  const T = clip.T;
  let i = Math.floor(t * fps);
  if (i < 0) i = 0;
  if (i >= T) i = T-1;
  return i;
}}
function paintClip(article, clip, t) {{
  const i = fiOf(clip, t);
  const nLed = clip.n_led;
  article.querySelectorAll('[data-ver]').forEach((row, vi) => {{
    if (solo >= 0 && vi !== solo) {{ row.style.display = 'none'; return; }}
    row.style.display = '';
    const rgb = frameRGB(row._u8, i, nLed);
    paintStrip(row.querySelector('canvas.strip'), rgb, nLed);
    paintPlate(row.querySelector('canvas.plate'), rgb, nLed);
  }});
  const ph = article.querySelector('.playhead');
  ph.style.width = (100 * i / Math.max(1, clip.T-1)) + '%';
}}
function mount() {{
  const grid = document.getElementById('grid');
  const groups = {{challenge:[], holdout:[]}};
  CLIPS.forEach(c => (groups[c.set] || groups.challenge).push(c));
  for (const [name, list] of [['Challenge', groups.challenge], ['Holdout', groups.holdout]]) {{
    if (!list.length) continue;
    const sec = document.createElement('section');
    sec.innerHTML = '<h2>'+name+'</h2>';
    list.forEach(clip => {{
      const art = document.createElement('article');
      art.dataset.clip = clip.id;
      const rates = clip.versions.map(v => v.triggers_per_min);
      const rateHtml = (v) => (v.triggers_per_min==null) ? '' :
        '<span class="rate">'+Number(v.triggers_per_min).toFixed(1)+' /min</span>';
      art.innerHTML = '<p class="who">'+clip.title+' · '+clip.duration_s.toFixed(1)+' s · 160 LEDs</p>' +
        clip.versions.map((v,i) =>
          '<div class="row" data-ver="'+i+'"><div class="lbl">'+v.label+' '+rateHtml(v)+'</div>'+
          '<canvas class="strip"></canvas><canvas class="plate"></canvas></div>'
        ).join('') + '<div class="playhead"></div>';
      art.querySelectorAll('[data-ver]').forEach((row, i) => {{
        row._u8 = u8(clip.versions[i].leds);
      }});
      sec.appendChild(art);
      paintClip(art, clip, tAbs);
    }});
    grid.appendChild(sec);
  }}
}}
function maxT() {{
  return Math.max(...CLIPS.map(c => c.T / c.fps));
}}
function tick(now) {{
  if (!playing) return;
  tAbs = (now - t0) / 1000;
  const span = maxT();
  if (tAbs > span) {{ tAbs = 0; t0 = now; }}
  document.getElementById('clock').textContent = tAbs.toFixed(2)+' s';
  document.querySelectorAll('article').forEach((art, idx) => {{
    const clip = CLIPS.find(c => c.id === art.dataset.clip);
    paintClip(art, clip, tAbs);
  }});
  raf = requestAnimationFrame(tick);
}}
document.getElementById('play').onclick = () => {{
  playing = true; t0 = performance.now() - tAbs*1000;
  document.getElementById('play').setAttribute('aria-pressed','true');
  document.getElementById('pause').setAttribute('aria-pressed','false');
  cancelAnimationFrame(raf); raf = requestAnimationFrame(tick);
}};
document.getElementById('pause').onclick = () => {{
  playing = false;
  document.getElementById('play').setAttribute('aria-pressed','false');
  document.getElementById('pause').setAttribute('aria-pressed','true');
}};
document.querySelectorAll('[data-solo]').forEach(btn => {{
  btn.onclick = () => {{
    solo = Number(btn.dataset.solo);
    document.querySelectorAll('[data-solo]').forEach(b => b.setAttribute('aria-pressed', b===btn ? 'true':'false'));
    document.querySelectorAll('article').forEach(art => {{
      const clip = CLIPS.find(c => c.id === art.dataset.clip);
      paintClip(art, clip, tAbs);
    }});
  }};
}});
mount();
document.getElementById('clock').textContent = tAbs.toFixed(2)+' s';
</script>
</body>
</html>
"""
    leaks = scan_blind_html(html)
    if leaks:
        raise ValueError("blind HTML leaked version names: " + "; ".join(leaks[:5]))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html)
    return path

