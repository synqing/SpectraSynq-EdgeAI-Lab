"use strict";

(function exposeHistory(root) {
  function finiteNumber(value) {
    if (value === null || value === undefined || value === "") return null;
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }

  function appendFreshMetric(history, metric, nowMs, windowMs) {
    const value = finiteNumber(metric?.value);
    const generation = finiteNumber(metric?.fresh_generation);
    const observedAt = finiteNumber(metric?.observed_at_unix_ms);
    if (value !== null && generation !== null && observedAt !== null) {
      const previous = history.at(-1);
      if (!previous || previous.generation !== generation) {
        history.push({generation, time: observedAt, value});
      }
    }
    const cutoff = nowMs - windowMs;
    while (history.length && history[0].time < cutoff) history.shift();
    return history;
  }

  const api = {appendFreshMetric};
  root.K1History = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
