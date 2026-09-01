/**
 * K1 USB-serial frame parser (schema v1.2, replay-compatible).
 *
 * Slots 1-24 are append-only. Slots 23-24 are presentation-derived and are
 * not operational evidence. update_mask is the only freshness authority for
 * held dataset values. Unknown or malformed records publish nothing.
 */
var SCHEMA = 1.2;
var last = [
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
];
var parseSeq = 0;
var mask = 0;

function kv(s, key) {
  var re = new RegExp("(?:^|[\\s,|])" + key + "=(-?[0-9]+(?:\\.[0-9]+)?)");
  var m = s.match(re);
  return m ? Number(m[1]) : null;
}

function setKv(s, key, idx) {
  var v = kv(s, key);
  if (v !== null && isFinite(v)) {
    last[idx] = v;
    mask |= (1 << idx);
  }
}

function recomputeOrbit(s) {
  setKv(s, "phase", 21);
  var peak = last[8];
  var ph = last[21];
  last[22] = peak * Math.cos(2 * Math.PI * ph);
  last[23] = peak * Math.sin(2 * Math.PI * ph);
  mask |= (1 << 22) | (1 << 23);
}

function publish(kind) {
  parseSeq += 1;
  last[17] = parseSeq;
  last[19] = kind;
  mask |= (1 << 17) | (1 << 19) | (1 << 20);
  last[20] = mask;
  return last.slice();
}

function parse(frame) {
  var s = typeof frame === "string" ? frame : "";
  s = s.replace(/\r/g, "").trim();
  if (!s)
    return [];

  mask = 0;

  if (s.indexOf("[AP]") === 0) {
    var c4 = s.length > 4 ? s.charCodeAt(4) : 32;
    if (c4 === 32 || c4 === 9 || c4 === 44 || c4 === 124 || s.length === 4) {
      setKv(s, "bpm", 0);
      setKv(s, "conf", 1);
      setKv(s, "lock", 2);
      setKv(s, "beat", 3);
      setKv(s, "onset", 4);
      setKv(s, "bass", 5);
      setKv(s, "silence", 6);
      setKv(s, "agc_gain", 7);
      setKv(s, "peak_scaled", 8);
      setKv(s, "SSL", 9);
      setKv(s, "lightshow", 14);
      recomputeOrbit(s);
      return publish(1);
    }
  }

  if (s.indexOf("EVENT_STATUS") === 0) {
    setKv(s, "beat", 3);
    setKv(s, "onset", 4);
    setKv(s, "bass", 5);
    setKv(s, "sil", 6);
    setKv(s, "energy", 10);
    setKv(s, "nov", 11);
    setKv(s, "conf", 1);
    setKv(s, "t", 15);
    setKv(s, "frame_ms", 16);
    setKv(s, "tid", 18);
    recomputeOrbit(s);
    return publish(2);
  }

  if (s.indexOf("SYSTEM_FPS:") === 0) {
    var fpsRest = s.substring(11).trim();
    var fps = Number(fpsRest);
    if (fpsRest === "" || !isFinite(fps))
      return [];
    last[12] = fps;
    mask |= (1 << 12);
    return publish(3);
  }

  if (s.indexOf("LED_FPS:") === 0) {
    var ledRest = s.substring(8).trim();
    var led = Number(ledRest);
    if (ledRest === "" || !isFinite(led))
      return [];
    last[13] = led;
    mask |= (1 << 13);
    return publish(4);
  }

  if (s.indexOf("VERSION:") === 0)
    return publish(5);

  return [];
}

