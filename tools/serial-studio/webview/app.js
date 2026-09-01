"use strict";

const histories = new Map();
const RECORDS = {1: "AP", 2: "EVENT_STATUS", 3: "SYSTEM_FPS", 4: "LED_FPS", 5: "VERSION"};
const view = new URLSearchParams(location.search).get("view") || "mission-control";

const byId = id => document.getElementById(id);
const text = (node, value) => { if (node) node.textContent = value; };
const metric = (source, name) => source?.metrics?.[name] || null;
const number = value => value === null || value === undefined || value === "" ? null : Number.isFinite(Number(value)) ? Number(value) : null;
const shown = (value, digits = 0) => number(value) === null ? "—" : Number(value).toFixed(digits);
const age = value => number(value) === null ? "AGE —" : `${Math.round(Number(value))} ms`;
const record = value => RECORDS[Math.round(Number(value))] || `RECORD ${value ?? "—"}`;

function setDot(id, state) {
  const node = byId(id);
  if (!node) return;
  node.classList.remove("ok", "bad");
  if (state === true) node.classList.add("ok");
  if (state === false) node.classList.add("bad");
}

function metricMarkup(node, item, digits, range) {
  const value = number(item?.value);
  const unit = item?.unit || "";
  const valueNode = node.querySelector(".n");
  text(valueNode, value === null ? "—" : shown(value, digits));
  if (value !== null && unit) {
    const small = document.createElement("small");
    small.textContent = ` ${unit.toUpperCase()}`;
    valueNode.append(small);
  }
  const label = node.querySelector(".label");
  const base = label.dataset.base || label.textContent;
  label.dataset.base = base;
  label.textContent = `${base} · ${age(item?.age_ms)}`;
  const bar = node.querySelector(".bar i");
  if (bar) bar.style.width = value === null ? "0" : `${Math.max(0, Math.min(100, value / range * 100))}%`;
}

function pushHistory(source, item) {
  const key = String(source.source_id);
  const history = histories.get(key) || [];
  const value = number(item?.value);
  const now = performance.now();
  if (value !== null && (!history.length || history.at(-1).value !== value || now - history.at(-1).time > 700)) {
    history.push({time: now, value});
  }
  while (history.length && now - history[0].time > 20000) history.shift();
  histories.set(key, history);
  return history;
}

function drawHistory(article, history) {
  const line = article.querySelector(".line");
  const area = article.querySelector(".area");
  if (!line || !area || !history.length) return;
  const newest = history.at(-1).time;
  const points = history.map(item => {
    const x = 620 - Math.min(620, (newest - item.time) / 20000 * 620);
    const y = 110 - Math.max(0, Math.min(1, item.value / 2)) * 100;
    return [x, y];
  });
  if (points[0][0] > 0) points.unshift([0, points[0][1]]);
  const d = points.map(([x, y], index) => `${index ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`).join(" ");
  line.setAttribute("d", d);
  area.setAttribute("d", `${d} L620 110 L0 110 Z`);
}

function renderSource(article, source, role) {
  const template = byId("device-template");
  article.replaceChildren(template.content.cloneNode(true));
  article.classList.toggle("no-data", source.rx?.has_data === false);
  text(article.querySelector(".role"), role);
  const identity = source.identity || String(source.title || "").split(" ").at(-1) || String(source.source_id);
  text(article.querySelector(".serial"), identity);
  const rx = article.querySelector(".rx");
  rx.replaceChildren(document.createTextNode("RX "));
  const rxAge = document.createElement("b");
  rxAge.textContent = age(source.rx?.age_ms);
  rx.append(rxAge, document.createTextNode(` · ${source.rx?.state || "UNKNOWN"}`));

  const bpm = metric(source, "bpm");
  text(article.querySelector(".tempo strong"), shown(bpm?.value, 0));
  text(article.querySelector(".tempo-meta"), `BPM\n${record(bpm?.record_kind)} · ${age(bpm?.age_ms)}`);
  article.querySelector(".tempo-meta").style.whiteSpace = "pre-line";
  const locked = number(metric(source, "lock")?.value) === 1;
  const lockNode = article.querySelector(".lock");
  lockNode.classList.toggle("off", !locked);
  text(lockNode, locked ? "● TEMPO LOCK" : "○ UNLOCKED");
  const confidence = metric(source, "confidence");
  text(article.querySelector(".confidence"), `CONFIDENCE ${shown(confidence?.value, 2)} · ${record(confidence?.record_kind)}`);

  metricMarkup(article.querySelector('[data-metric="peak_scaled"]'), metric(source, "peak_scaled"), 2, 2);
  metricMarkup(article.querySelector('[data-metric="energy"]'), metric(source, "energy"), 2, 1);
  metricMarkup(article.querySelector('[data-metric="system_fps"]'), metric(source, "system_fps"), 0, 240);
  metricMarkup(article.querySelector('[data-metric="led_fps"]'), metric(source, "led_fps"), 0, 240);
  drawHistory(article, pushHistory(source, metric(source, "peak_scaled")));
}

function delta(a, b, name, digits, suffix = "") {
  const av = number(metric(a, name)?.value);
  const bv = number(metric(b, name)?.value);
  if (av === null || bv === null) return "—";
  const value = av - bv;
  return `${value >= 0 ? "+" : ""}${value.toFixed(digits)}${suffix}`;
}

function renderDetail(snapshot) {
  const timing = view === "timing";
  text(byId("surface-title"), timing ? "K1 TIMING & TRANSPORT" : "K1 SYSTEM HEALTH");
  text(byId("detail-title"), timing ? "TIMING & TRANSPORT" : "SYSTEM HEALTH");
  byId("mission-control").classList.add("hidden");
  byId("delta").classList.add("hidden");
  byId("detail-panel").classList.remove("hidden");
  const grid = byId("detail-grid");
  grid.replaceChildren();
  for (const source of snapshot.sources || []) {
    const facts = timing ? [
      ["RAW FRAME AGE", age(source.rx?.age_ms), "io.getLatestFrame"],
      ["AP AGE", age(metric(source, "bpm")?.age_ms), "update_mask"],
      ["EVENT_STATUS AGE", age(metric(source, "energy")?.age_ms), "update_mask"],
      ["SYSTEM FPS AGE", age(metric(source, "system_fps")?.age_ms), "update_mask"],
      ["LED FPS AGE", age(metric(source, "led_fps")?.age_ms), "update_mask"],
      ["DEVICE CLOCK", number(metric(source, "device_ms")?.value) === null ? "NOT INSTRUMENTED" : shown(metric(source, "device_ms")?.value, 0) + " ms", "device"],
    ] : [
      ["SOURCE RX", source.rx?.state || "UNKNOWN", age(source.rx?.age_ms)],
      ["SYSTEM FPS", shown(metric(source, "system_fps")?.value, 0) + " Hz", age(metric(source, "system_fps")?.age_ms)],
      ["LED FPS", shown(metric(source, "led_fps")?.value, 0) + " Hz", age(metric(source, "led_fps")?.age_ms)],
      ["PARSER SEQUENCE", shown(metric(source, "host_parse_seq")?.value, 0), "HOST DIAGNOSTIC ONLY"],
    ];
    for (const fact of facts) {
      const row = document.createElement("div");
      row.className = "detail-row";
      for (const value of [`${source.title} · ${fact[0]}`, fact[1], fact[2]]) {
        const cell = document.createElement("span"); cell.textContent = value; row.append(cell);
      }
      grid.append(row);
    }
  }
}

function renderAudioSurface(snapshot, apValidation) {
  const audio = snapshot.audio_reference || {};
  const capture = audio.capture || {};
  const expected = capture.expected_device_id || {};
  const hostReceipt = audio.validation_receipt || {};
  const apState = snapshot.ap_validation || {};
  const apReceipt = apState.receipt || {};
  text(byId("surface-title"), apValidation ? "K1 AP VALIDATION" : "K1 AUDIO REFERENCE");
  text(byId("detail-title"), apValidation ? "AP VALIDATION" : "AUDIO REFERENCE");
  byId("mission-control").classList.add("hidden");
  byId("delta").classList.add("hidden");
  byId("detail-panel").classList.remove("hidden");
  const grid = byId("detail-grid");
  grid.replaceChildren();

  const hostScore = hostReceipt.score_status || "NO RECEIPT";
  const readiness = apReceipt.receipt_sha256
    ? apReceipt.score_status === "PASS" || apReceipt.score_status === "FAIL"
      ? `COMPLETE · ${apReceipt.score_status}` : "READY · UNSCORED"
    : `BLOCKED · ${(apState.reason_codes || ["NO AP SCORER RECEIPT"]).join(" · ")}`;
  const facts = apValidation ? [
    ["VALIDATION STATE", readiness, apReceipt.receipt_sha256 ? `AP RECEIPT ${apReceipt.receipt_sha256.slice(0, 12)}` : "NO AP VERDICT"],
    ["AUDIO REFERENCE", audio.state || "NOT INSTRUMENTED", hostReceipt.receipt_sha256 ? `HOST CAPTURE RECEIPT ${hostScore}` : audio.non_claim || "HOST REFERENCE · NOT DEVICE INPUT"],
    ["BENCH AP", (snapshot.sources || []).some(source => Number(source.source_id) === 0) ? "OBSERVED" : "MISSING", "K1 TELEMETRY"],
    ["MAIN AP", (snapshot.sources || []).some(source => Number(source.source_id) === 1) ? "OBSERVED" : "MISSING", "K1 TELEMETRY"],
    ["CLOCK MAP", "UNALIGNED", "HOST ARRIVAL CANNOT AUTHORISE DEVICE DELTAS"],
    ["AP SCORING PROFILE", apReceipt.profile_id || "—", apReceipt.profile_sha256 ? apReceipt.profile_sha256.slice(0, 16) : "NOT BOUND"],
    ["REFERENCE SHA", hostReceipt.reference_sha256 ? hostReceipt.reference_sha256.slice(0, 16) : "—", "HOST CAPTURE EVIDENCE ONLY"],
    ["DEVICE COMPARISON", "SUPPRESSED", "NO CLOCK MAP"],
  ] : [
    ["CAPTURE STATE", audio.state || "NOT INSTRUMENTED", age(audio.age_ms)],
    ["PROVENANCE", audio.provenance_state || "unbound", (audio.reason_codes || []).join(" · ") || "—"],
    ["INPUT DEVICE", expected.inputDeviceName || capture.title || "—", capture.binding_sha256 ? capture.binding_sha256.slice(0, 16) : "BINDING —"],
    ["SAMPLE RATE", expected.sampleRateValue ? `${expected.sampleRateValue} Hz` : "—", "HOST AUDIO REFERENCE TIME"],
    ["FORMAT", expected.formatName || "—", expected.channelCount ? `${expected.channelCount} CHANNELS` : "CHANNELS —"],
    ["LEVEL", capture.level_dbfs === null || capture.level_dbfs === undefined ? "NOT INSTRUMENTED" : `${shown(capture.level_dbfs, 1)} dBFS`, "NO EMPTY CHART AS SILENCE"],
    ["CONTINUITY", capture.drop_count === null || capture.drop_count === undefined ? "NOT INSTRUMENTED" : `${capture.drop_count} DROPS`, capture.sequence === null || capture.sequence === undefined ? "SEQUENCE —" : `SEQUENCE ${capture.sequence}`],
    ["QUANTITATIVE RECEIPT", hostReceipt.receipt_sha256 ? hostScore : "NOT LOADED", hostReceipt.receipt_sha256 ? hostReceipt.receipt_sha256.slice(0, 16) : "—"],
  ];
  for (const fact of facts) {
    const row = document.createElement("div");
    row.className = "detail-row";
    for (const value of fact) {
      const cell = document.createElement("span");
      cell.textContent = value;
      row.append(cell);
    }
    grid.append(row);
  }
}

function render(snapshot) {
  text(byId("mode-kicker"), snapshot.mode === "fixture" ? "FIXTURE · NOT DEVICE EVIDENCE" : "LIVE OBSERVABILITY");
  const apiUp = snapshot.bridge?.api_state === "UP";
  text(byId("api-state"), snapshot.bridge?.api_state || "UNKNOWN");
  setDot("api-dot", apiUp);
  const policy = snapshot.instrument?.policy || {};
  const projectObserveOnly = policy.project_policy === "OBSERVE_ONLY";
  text(byId("policy"), projectObserveOnly ? "OBSERVE-ONLY" : "POLICY NOT CONFIRMED");
  setDot("policy-dot", projectObserveOnly ? null : apiUp ? null : false);
  text(byId("app-egress-guard"), policy.app_egress_guard === "STOCK_PRO_NOT_PATCHED" ? "STOCK PRO / NOT PATCHED" : (policy.app_egress_guard || "UNKNOWN"));
  const witness = policy.tx_witness || "REQUIRED_PENDING";
  text(byId("tx-witness"), witness === "ZERO_BYTES" ? "TX WITNESS · ZERO BYTES" : witness === "FAIL" ? "TX WITNESS · FAIL · QUARANTINE" : "TX WITNESS REQUIRED · PENDING");
  const historian = snapshot.instrument?.historian || {};
  text(byId("historian-state"), historian.state || "UNKNOWN");
  setDot("historian-dot", historian.state === "RECORDING" ? true : historian.state === "NOT_RECORDING" ? false : null);
  const sessionId = historian.session_id;
  text(byId("session"), sessionId === null || sessionId === undefined ? "SESSION —" : `SESSION #${sessionId}`);
  text(byId("raw-rate"), snapshot.instrument?.raw_bytes_per_second ?? "NOT INSTRUMENTED");
  const audio = snapshot.audio_reference || {};
  const audioState = audio.state || "NOT INSTRUMENTED";
  const audioAge = number(audio.age_ms);
  const audioLabel = audioAge === null ? audioState.replaceAll("_", " ") : `${audioState.replaceAll("_", " ")} · ${Math.round(audioAge)} ms`;
  text(byId("audio-ref-state"), audioLabel);
  setDot(
    "audio-ref-dot",
    audioState === "CAPTURE_READY" ? true :
      ["REQUIRED_MISSING", "STALE", "PROVENANCE_MISMATCH", "INVALID"].includes(audioState) ? false : null
  );
  text(byId("clock"), new Date().toLocaleString("en-GB", {timeZone: "Australia/Perth", hour12: false}) + " AWST");

  const sources = snapshot.sources || [];
  if (view === "timing" || view === "health") { renderDetail(snapshot); return; }
  if (view === "audio-reference") { renderAudioSurface(snapshot, false); return; }
  if (view === "ap-validation") { renderAudioSurface(snapshot, true); return; }
  const bench = sources.find(source => Number(source.source_id) === 0) || sources[0];
  const main = sources.find(source => Number(source.source_id) === 1) || sources[1];
  if (bench) renderSource(byId("source-0"), bench, "BENCH");
  if (main) renderSource(byId("source-1"), main, "MAIN");
  text(byId("delta-bpm"), delta(bench, main, "bpm", 0));
  text(byId("delta-confidence"), delta(bench, main, "confidence", 2));
  text(byId("delta-peak"), delta(bench, main, "peak_scaled", 2));
  text(byId("delta-system_fps"), delta(bench, main, "system_fps", 0, " Hz"));
  text(byId("delta-led_fps"), delta(bench, main, "led_fps", 0, " Hz"));
}

async function update() {
  try {
    const response = await fetch("/api/v1/snapshot", {cache: "no-store"});
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    render(await response.json());
  } catch (error) {
    text(byId("api-state"), "BRIDGE DOWN");
    text(byId("policy"), "POLICY NOT CONFIRMED");
    setDot("api-dot", false);
    setDot("policy-dot", false);
  }
}

update();
setInterval(update, 500);
