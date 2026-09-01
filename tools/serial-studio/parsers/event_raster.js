// Read-only event/state raster for one K1 source.
// Dataset order is fixed by v2.workspace-manifest.json:
// beat, onset, bass, silence, lock, record_kind, update_mask,
// host_parse_seq, event_tid.

const WINDOW_MS = 20000;
const MAX_EVENTS = 4096;
const events = [];
const silenceHistory = [];
const lockHistory = [];
let lastParseSeq = -1;

function bitFresh(mask, oneBasedSlot) {
  return (mask & (1 << (oneBasedSlot - 1))) !== 0;
}

function pushState(history, now, value) {
  const v = value >= 0.5 ? 1 : 0;
  const previous = history.length ? history[history.length - 1] : null;
  if (!previous || previous.value !== v)
    history.push({time: now, value: v, lastFresh: now});
  else
    previous.lastFresh = now;
}

function trimHistory(history, cutoff) {
  while (history.length > 1 && history[1].time < cutoff)
    history.shift();
}

function onFrame() {
  if (datasets.length < 9)
    return;

  const seq = datasets[7].value;
  if (!isFinite(seq) || seq === lastParseSeq)
    return;
  lastParseSeq = seq;

  const now = frame.timestampMs;
  const kind = Math.round(datasets[5].value);
  const mask = Math.round(datasets[6].value);
  const tid = Math.round(datasets[8].value);

  if (bitFresh(mask, 4) && datasets[0].value >= 0.5)
    events.push({time: now, lane: kind === 1 ? 0 : 1, type: "beat", tid: tid});
  if (bitFresh(mask, 5) && datasets[1].value >= 0.5)
    events.push({time: now, lane: 2, type: "onset", tid: tid});
  if (bitFresh(mask, 6) && datasets[2].value >= 0.5)
    events.push({time: now, lane: 3, type: "bass", tid: tid});
  if (bitFresh(mask, 7))
    pushState(silenceHistory, now, datasets[3].value);
  if (bitFresh(mask, 3))
    pushState(lockHistory, now, datasets[4].value);

  const cutoff = now - WINDOW_MS;
  while (events.length && (events[0].time < cutoff || events.length > MAX_EVENTS))
    events.shift();
  trimHistory(silenceHistory, cutoff);
  trimHistory(lockHistory, cutoff);
}

function xFor(time, now, x, width) {
  return x + Math.max(0, Math.min(1, (time - (now - WINDOW_MS)) / WINDOW_MS)) * width;
}

function drawState(ctx, history, lane, now, x, y, width, laneH, color) {
  if (!history.length)
    return;
  const cutoff = now - WINDOW_MS;
  for (let i = 0; i < history.length; ++i) {
    const item = history[i];
    if (!item.value)
      continue;
    const next = i + 1 < history.length ? history[i + 1].time : item.lastFresh;
    const x0 = xFor(Math.max(cutoff, item.time), now, x, width);
    const x1 = xFor(Math.max(item.time, next), now, x, width);
    ctx.fillStyle = color;
    ctx.globalAlpha = 0.55;
    ctx.fillRect(x0, y + lane * laneH + 3, Math.max(1, x1 - x0), laneH - 6);
    ctx.globalAlpha = 1;
    if (i === history.length - 1 && item.lastFresh < now) {
      const heldX = xFor(item.lastFresh, now, x, width);
      ctx.strokeStyle = color;
      ctx.setLineDash([3, 3]);
      ctx.strokeRect(heldX, y + lane * laneH + 4, Math.max(1, x + width - heldX), laneH - 8);
      ctx.setLineDash([]);
    }
  }
}

function paint(ctx, w, h) {
  const labels = ["TEMPO BEAT", "IOI BEAT", "ONSET", "BASS", "SILENCE", "LOCK"];
  const colours = theme.widget_colors || [theme.widget_highlight, theme.accent, theme.alarm];
  const now = frame.timestampMs;
  const labelW = 112;
  const pad = 12;
  const top = 34;
  const plotX = labelW;
  const plotW = Math.max(1, w - labelW - pad);
  const laneH = Math.max(24, (h - top - pad) / labels.length);

  ctx.fillStyle = theme.widget_base;
  ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = theme.widget_text;
  ctx.font = "bold 12px sans-serif";
  ctx.textAlign = "start";
  ctx.fillText("FRESH EVENTS · 20 s", pad, 20);
  ctx.fillStyle = theme.placeholder_text;
  ctx.font = "12px sans-serif";
  ctx.textAlign = "end";
  ctx.fillText("held state is dashed", w - pad, 20);

  for (let i = 0; i < labels.length; ++i) {
    const ly = top + i * laneH;
    ctx.fillStyle = i % 2 ? theme.alternate_base : theme.widget_base;
    ctx.fillRect(0, ly, w, laneH);
    ctx.strokeStyle = theme.widget_border;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(plotX, ly + laneH);
    ctx.lineTo(w - pad, ly + laneH);
    ctx.stroke();
    ctx.fillStyle = theme.placeholder_text;
    ctx.font = "bold 12px sans-serif";
    ctx.textAlign = "start";
    ctx.fillText(labels[i], pad, ly + laneH * 0.62);
  }

  drawState(ctx, silenceHistory, 4, now, plotX, top, plotW, laneH, colours[3 % colours.length]);
  drawState(ctx, lockHistory, 5, now, plotX, top, plotW, laneH, colours[4 % colours.length]);

  for (let i = 0; i < events.length; ++i) {
    const event = events[i];
    const ex = xFor(event.time, now, plotX, plotW);
    const ey = top + event.lane * laneH;
    ctx.strokeStyle = colours[event.lane % colours.length];
    ctx.lineWidth = event.type === "bass" ? 3 : 2;
    ctx.beginPath();
    ctx.moveTo(ex, ey + 4);
    ctx.lineTo(ex, ey + laneH - 4);
    ctx.stroke();
  }

  ctx.fillStyle = theme.placeholder_text;
  ctx.font = "12px sans-serif";
  ctx.textAlign = "start";
  ctx.fillText("−20 s", plotX, h - 2);
  ctx.textAlign = "end";
  ctx.fillText("now", w - pad, h - 2);
}
