#!/usr/bin/env python3
"""HOST rehearsal of semantic cadence/latency. Not Gate C0. Not silicon. Not LGP.

Reuse P3-C holdout dumps, frozen p3b-v1 maps, extra_gain [0.62, 1.0], firmware
Waveform Tempo, and p3c_quant.score_clip. Zero-order-hold the extra-DoF gain,
delay it causally, re-render. Do not resample LED frames.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

from edgeai.mir.gate_c_cadence import (
    BINDING,
    DELAYS_S,
    FROZEN_MAP_VERSION,
    GAIN_HI,
    GAIN_LO,
    HOLD_RATES_HZ,
    HOP,
    HOP_S,
    NATIVE_HZ,
    NATIVE_KEEP_FRACTION,
    P3C_HOLDOUT_MEDIAN_DELTA,
    PREVIEW_EXPOSURE,
    SHARE_SOURCES,
    SR,
    WARMUP_S,
    actual_delay_s,
    apply_cadence,
    delay_below_absolute_floor_s,
    delay_cliff_s,
    is_native_cell,
    lowest_passing_rate_hz,
    require_four_source_share,
    score_head_delta,
    summarise_holdout,
    sweep_cells,
)
from edgeai.mir.host_chroma import host_chroma12, preview_encode
from edgeai.mir.k1_render_host import compile_mode, firmware_root, firmware_sha, render_mode
from edgeai.mir.p3c_quant import cache_path, leds_path, slice_oracle

ROOT = Path(__file__).resolve().parents[1]
P3C = ROOT / "artifacts" / "source_activity" / "p3c"
CACHE = ROOT / "artifacts" / "source_activity" / "musdb18_oracle_cache"
RECEIPT_IN = P3C / "receipt_musdb18_p3c.json"
MUSDB = ROOT / "datasets" / "musdb18"
OUT = ROOT / "artifacts" / "gate_c_cadence"
CHROMA_CACHE = OUT / "chroma"
DOC = ROOT / "docs" / "mir" / "GATE_C_CADENCE_HOST.md"
FIG = ROOT / "docs" / "mir" / "figures" / "gate_c_cadence_host.png"
COMPILER = "g++-15"


def _safe(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in name)


def _mono(x: np.ndarray) -> np.ndarray:
    y = np.asarray(x, dtype=np.float32)
    if y.ndim == 2:
        y = y.mean(axis=-1)
    return y.reshape(-1)


def _jsonable(obj):
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return _jsonable(obj.tolist())
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, (np.floating, float)):
        return float(obj)
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if obj is None:
        return None
    return obj


def load_holdout_meta() -> list[dict]:
    raw = json.loads(RECEIPT_IN.read_text())
    rows = [dict(s) for s in raw["scores"] if s.get("set") == "holdout"]
    if not rows:
        raise SystemExit(f"no holdout clips in {RECEIPT_IN}")
    return rows


def load_oracle_slice(meta: dict) -> dict:
    oracle = np.load(cache_path(CACHE, meta["track"]))
    require_four_source_share(oracle)
    n = int(meta["n"])
    sliced = slice_oracle(oracle, float(meta["start_s"]), n)
    # Confirm the four-source simplex survived the slice.
    require_four_source_share(sliced)
    return sliced


def pack_leds(dump: dict, leds_b: np.ndarray, leds_d: np.ndarray, gain_b: np.ndarray, gain_d: np.ndarray) -> dict:
    return {
        "A": dump["A"],
        "B": leds_b,
        "D": leds_d,
        "control": dump["control"],
        "mir": dump["mir"],
        "gain_A": dump["gain_A"],
        "gain_B": gain_b,
        "gain_D": gain_d,
    }


def load_musdb_test():
    import musdb

    train = MUSDB / "train"
    nested = MUSDB / "musdb18" / "train"
    root = MUSDB / "musdb18" if nested.is_dir() and not train.is_dir() else MUSDB
    db = musdb.DB(root=str(root.resolve()), is_wav=False, sample_rate=SR, subsets="test")
    return {t.name: t for t in db}


def chroma_for_clip(meta: dict, tracks: dict | None) -> tuple[np.ndarray, str]:
    n = int(meta["n"])
    start = float(meta["start_s"])
    cache = CHROMA_CACHE / f"{_safe(meta['track'])}.npz"
    if cache.is_file():
        z = np.load(cache)
        if int(z["n"]) == n and abs(float(z["start_s"]) - start) < 1e-6:
            c = np.asarray(z["chroma"], dtype=np.float64)
            if c.shape == (n, 12):
                return c, "cache"
    chroma_src = "constant_fixture"
    chroma = np.full((n, 12), 0.35, dtype=np.float64)
    chroma[:, 9] = 0.95
    if tracks is not None and meta["track"] in tracks:
        mix = _mono(tracks[meta["track"]].audio)
        i0 = int(round(start * SR))
        i1 = int(round((start + n * HOP_S) * SR))
        sl = mix[i0:i1]
        _t, chroma_m = host_chroma12(sl, sr=SR, hop=HOP)
        chroma_m = np.asarray(chroma_m, dtype=np.float64)
        if chroma_m.shape[0] >= n:
            chroma = chroma_m[:n]
            chroma_src = "musdb_mix"
        elif chroma_m.shape[0] > 0:
            chroma[: chroma_m.shape[0]] = chroma_m
            chroma_src = "musdb_mix_padded"
    CHROMA_CACHE.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache, chroma=chroma, n=n, start_s=start, source=chroma_src)
    return chroma, chroma_src


def render_gains(binary: Path, chroma: np.ndarray, gain: np.ndarray) -> np.ndarray:
    n = int(gain.size)
    warm = max(1, int(round(WARMUP_S / HOP_S)))
    times = np.arange(n + warm, dtype=np.float64) * HOP_S
    g = np.concatenate([np.repeat(gain[:1], warm), gain])
    chroma_w = np.vstack([np.repeat(chroma[:1], warm, axis=0), chroma])
    chroma_g = np.clip(chroma_w * g.reshape(-1, 1), 0.0, 1.0)
    raw = render_mode(binary, times_s=times, chroma=chroma_g, waveform_peak=g)
    return preview_encode(raw[warm:], exposure=PREVIEW_EXPOSURE)


def write_figure(rate_rows: list[dict], delay_rows: list[dict], native_median: float, path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rel = NATIVE_KEEP_FRACTION * native_median
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.6))
    fig.patch.set_facecolor("#f4efe6")
    fig.suptitle(
        "HOST-ONLY  ·  not C0  ·  source_share × Waveform Tempo × head_position",
        fontsize=11,
        color="#1b1814",
    )

    def _bars(ax, labels, vals, title, xlabel):
        ax.set_facecolor("#f4efe6")
        colours = ["#2f6f3e" if v == v and v >= 0.15 and v >= rel else "#a33b2b" for v in vals]
        x = np.arange(len(vals))
        ax.bar(x, [0.0 if v != v else v for v in vals], color=colours, width=0.72)
        ax.axhline(0.15, color="#6a645c", ls="--", lw=0.9, label="floor 0.15")
        ax.axhline(rel, color="#1b1814", ls=":", lw=0.9, label=f"70% of native ({rel:.2f})")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_ylabel("holdout median Δ partial r  (D−B)")
        ax.set_title(title, fontsize=10)
        ax.set_xlabel(xlabel, fontsize=9)
        ax.grid(axis="y", alpha=0.25)
        ymax = max([0.2] + [v for v in vals if v == v] + [rel, 0.15])
        ax.set_ylim(0.0, ymax * 1.18)
        for i, v in enumerate(vals):
            if v == v:
                ax.text(i, v + 0.012, f"{v:.2f}", ha="center", va="bottom", fontsize=8, color="#1b1814")
        ax.legend(loc="upper left", fontsize=7, frameon=False)

    rate_rows = sorted(rate_rows, key=lambda r: float(r["rate_hz"]))
    _bars(
        axes[0],
        [f"{r['rate_hz']:g} Hz" for r in rate_rows],
        [float(r["median_delta_pos_share"]) for r in rate_rows],
        "Hold rate  ·  delay 0 ms",
        "update rate",
    )
    delay_rows = sorted(delay_rows, key=lambda r: float(r["delay_s"]))
    _bars(
        axes[1],
        [f"{int(round(r['delay_s'] * 1000))} ms" for r in delay_rows],
        [float(r["median_delta_pos_share"]) for r in delay_rows],
        f"Added delay  ·  {NATIVE_HZ:g} Hz",
        "causal delay",
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def write_doc(receipt: dict, path: Path) -> None:
    native = receipt["native"]
    low = receipt.get("lowest_passing_rate_hz")
    cliff = receipt.get("delay_cliff_s")
    abs_cliff = receipt.get("delay_below_absolute_floor_s")
    low_s = "none (native also failed)" if low is None else f"{low:g} Hz"
    if cliff is None:
        cliff_s = f"no combined-rule cliff at or below {int(DELAYS_S[-1] * 1000)} ms"
    else:
        cliff_s = (
            f"{int(round(float(cliff) * 1000))} ms requested "
            f"({int(round(actual_delay_s(float(cliff)) * 1000))} ms after hop rounding)"
        )
    if abs_cliff is None:
        abs_s = f"still ≥ 0.15 out to {int(DELAYS_S[-1] * 1000)} ms"
    else:
        abs_s = f"{int(round(float(abs_cliff) * 1000))} ms requested"
    rate_lines = "\n".join(
        f"| {r['rate_hz']:g} | 0 | {r['median_delta_pos_share']:.3f} | {r['fraction_of_native']:.2f} | {r['wins_positive_delta'][0]}/{r['wins_positive_delta'][1]} | {r['verdict']} |"
        for r in receipt["rate_sweep"]
    )
    delay_lines = "\n".join(
        f"| {r['rate_hz']:g} | {int(round(r['delay_s'] * 1000))} | {int(round(r['actual_delay_s'] * 1000))} | {r['median_delta_pos_share']:.3f} | {r['fraction_of_native']:.2f} | {r['verdict']} |"
        for r in receipt["delay_sweep"]
    )
    tracks = ", ".join(receipt["corpus"]["tracks"])
    chroma_note = receipt["method"]["chroma"]
    rate_by = {float(r["rate_hz"]): r for r in receipt["rate_sweep"]}
    delay_by = {float(r["delay_s"]): r for r in receipt["delay_sweep"]}
    r10 = rate_by.get(10.0, {})
    d50 = delay_by.get(0.05, delay_by.get(0.050, {}))
    d200 = delay_by.get(0.2, delay_by.get(0.200, {}))
    rel = float(native.get("relative_floor") or 0.0)
    r10_s = (
        f"{r10['median_delta_pos_share']:.2f} (above 0.15, {r10['fraction_of_native']:.0%} of native)"
        if r10
        else "n/a"
    )
    d50_s = (
        f"{d50['median_delta_pos_share']:.2f} vs relative floor {rel:.2f}"
        if d50
        else "n/a"
    )
    d200_s = f"{d200['median_delta_pos_share']:.2f}" if d200 else "n/a"
    text = f"""---
abstract: "HOST-ONLY cadence of source_share × WaveformTempo × head_position. Lowest passing hold {low_s}; 50 ms fails 70%-of-native; 200 ms fails 0.15. Not C0. I/O unfrozen."
---

# Gate C cadence — HOST rehearsal

This is a **host pixel** rehearsal of how slowly and how late the extra control can update before Waveform Tempo stops carrying source ownership. It is **not** Gate C, **not** C0, **not** silicon, **not** LGP.

Binding (unchanged): `{BINDING}`.

Label: **HOST-ONLY / HOST_PIXEL_VALIDATED**. Student I/O is still OPEN.

## What this run did

It took the existing P3-C holdout dumps (same clips, same frozen p3b-v1 maps, same extra gain in [0.62, 1.0]) and asked: if the extra-DoF gain is only refreshed at 2 / 5 / 10 / 20 / 31.25 Hz, or arrives 50 / 100 / 200 ms late, does the head still track share after mix is partialled out?

Native 31.25 Hz with 0 ms extra delay **reuses the P3-C LED dumps**. Other cells zero-order-hold that gain series, delay it causally, then re-render Waveform Tempo. LED frames are not resampled.

Corpus: P3-C holdout, n={receipt['corpus']['n_scored']} of {receipt['corpus']['n_requested']}. Tracks: {tracks}.

Share driver stays four-source (vocals / drums / bass / **other**). `composition_change` is not used.

Chroma for re-render: {chroma_note}. Head position is peak-driven; chroma is the same extra-DoF gain applied to the P3-C chromagram path.

## Pass rule

A rate (delay 0) **passes** when holdout median Δ partial r (D−B) of head position vs share | mix is:

1. ≥ 0.15 (P3-C extra-DoF floor), and
2. ≥ 70% of **this run's** native-rate median Δ.

P3-C documented holdout median Δ was {P3C_HOLDOUT_MEDIAN_DELTA:.2f}. This run's native dump median Δ is {native['median_delta_pos_share']:.3f} ({native['verdict']}).

## Result

**Lowest rate that still passes: {low_s}.**  
**Delay that fails the combined pass rule (0.15 and 70% of native): {cliff_s}.**  
**Delay that drops under the absolute 0.15 extra-DoF floor: {abs_s}.**

10 Hz still has median Δ {r10_s} — it fails only the 70% keep-rate. 50 ms delay is the same shape: Δ {d50_s}. 200 ms is the first delay that also falls under 0.15 (Δ {d200_s}).

### Hold rate (delay 0)

| rate Hz | delay ms | median Δ | fraction of native | wins | verdict |
| ---: | ---: | ---: | ---: | ---: | --- |
{rate_lines}

### Added delay (native rate)

| rate Hz | requested ms | actual ms (hop-rounded) | median Δ | fraction of native | verdict |
| ---: | ---: | ---: | ---: | ---: | --- |
{delay_lines}

50 ms request rounds to {int(round(actual_delay_s(0.050) * 1000))} ms at a 32 ms hop. That rounding is part of the host grid, not a product clock.

Figure: `docs/mir/figures/gate_c_cadence_host.png`.

## What this is not

- Not C0 (`ON_SILICON_PIXEL_VALIDATED`). Host bytes are pre-gamma / pre-dither / pre-LGP.
- Not C1. Nobody looked at the plate. Head-position Δ is the instrument.
- Not a student I/O freeze. Cadence numbers here are **design evidence** for a later contract, if C0/C1 pass.
- Not a Demucs run. Not a new net.

## Ship path

1. Already in source: this HOST rehearsal plus the P3-C dumps it reused.
2. Remaining: C0 silicon LED dumps of the same extra-DoF at these holds/delays; then C1 LGP perceptual.
3. Who: a named Captain GO to flash / dump on the physical K1. Not this script.
4. Shipped for C0 means silicon dumps scored with the same Δ floor, stamped `ON_SILICON_PIXEL_VALIDATED`.

Firmware SHA {receipt['firmware_sha'][:12]}. Compiler {receipt['compiler']}. Frozen map {FROZEN_MAP_VERSION}.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:edgeai | HOST cadence rehearsal of P3-C extra-DoF; lowest passing rate and delay cliff. Not C0. |
"""
    path.write_text(text)


def main() -> int:
    os.environ.setdefault("SPECTRASYNQ_K1_FIRMWARE", "/Users/spectrasynq/SpectraSynq_K1_Firmware")
    meta_rows = load_holdout_meta()
    print(f"holdout clips {len(meta_rows)} from {RECEIPT_IN}", flush=True)

    fw = firmware_root()
    sha = firmware_sha(fw)
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"compiling waveform_tempo with {COMPILER} from {fw} @ {sha[:12]}", flush=True)
    binary, cmeta = compile_mode(OUT / "_tempo_build", mode="waveform_tempo", compiler=COMPILER)
    print(f"compiler {cmeta.get('compiler')} ok {binary}", flush=True)

    try:
        tracks = load_musdb_test()
    except Exception as exc:  # noqa: BLE001 — musdb is optional at runtime
        print(f"musdb unavailable ({exc}); chroma falls back to fixture", flush=True)
        tracks = None

    cells = sweep_cells()
    per_cell: dict[tuple[str, float, float], list[dict]] = {c: [] for c in cells}
    chroma_sources: list[str] = []

    for meta in meta_rows:
        name = meta["track"]
        dump_path = leds_path(P3C, name, "holdout")
        dump_npz = np.load(dump_path)
        dump = {k: dump_npz[k] for k in dump_npz.files}
        oracle = load_oracle_slice(meta)
        chroma, chroma_src = chroma_for_clip(meta, tracks)
        chroma_sources.append(chroma_src)
        n = int(meta["n"])
        gain_b0 = np.asarray(dump["gain_B"], dtype=np.float64)[:n]
        gain_d0 = np.asarray(dump["gain_D"], dtype=np.float64)[:n]
        print(f"{name} n={n} chroma={chroma_src} share={meta['share_driver']}", flush=True)

        for family, rate, delay in cells:
            g_b = apply_cadence(gain_b0, hop_s=HOP_S, rate_hz=rate, delay_s=delay)
            g_d = apply_cadence(gain_d0, hop_s=HOP_S, rate_hz=rate, delay_s=delay)
            if is_native_cell(rate, delay):
                leds_b = np.asarray(dump["B"])[:n]
                leds_d = np.asarray(dump["D"])[:n]
                src = "p3c_led_dump"
            else:
                leds_b = render_gains(binary, chroma, g_b)
                leds_d = render_gains(binary, chroma, g_d)
                src = "zoh_delay_rerender"
            packed = pack_leds(dump, leds_b, leds_d, g_b, g_d)
            rec = score_head_delta(packed, oracle, meta)
            rec.update(
                {
                    "family": family,
                    "rate_hz": float(rate),
                    "delay_s": float(delay),
                    "actual_delay_s": actual_delay_s(delay),
                    "leds_source": src,
                    "chroma_source": chroma_src,
                    "gain_lo": float(g_d.min()),
                    "gain_hi": float(g_d.max()),
                }
            )
            per_cell[(family, rate, delay)].append(rec)
            print(
                f"  {family} {rate:g}Hz +{int(round(delay * 1000))}ms  "
                f"Δ={rec['delta_pos_share']!r}  src={src}",
                flush=True,
            )

    # Native median from the dump cell (rate sweep at NATIVE_HZ, delay 0).
    native_key = ("rate", float(NATIVE_HZ), 0.0)
    native_deltas = [float(r["delta_pos_share"]) for r in per_cell[native_key]]
    native_sum = summarise_holdout(native_deltas, native_median=P3C_HOLDOUT_MEDIAN_DELTA)
    # Pass rule uses *this run's* native median, not the documented 0.63, once measured.
    native_median = native_sum["median_delta_pos_share"]
    native_sum = summarise_holdout(native_deltas, native_median=native_median)
    native_sum.update(
        {
            "rate_hz": float(NATIVE_HZ),
            "delay_s": 0.0,
            "actual_delay_s": 0.0,
            "source": "p3c_led_dumps",
            "documented_p3c_holdout_median_delta": P3C_HOLDOUT_MEDIAN_DELTA,
        }
    )

    rate_sweep = []
    delay_sweep = [dict(native_sum)]
    for family, rate, delay in cells:
        deltas = [float(r["delta_pos_share"]) for r in per_cell[(family, rate, delay)]]
        summary = summarise_holdout(deltas, native_median=native_median)
        summary.update(
            {
                "family": family,
                "rate_hz": float(rate),
                "delay_s": float(delay),
                "actual_delay_s": actual_delay_s(delay),
            }
        )
        if family == "rate":
            rate_sweep.append(summary)
        else:
            delay_sweep.append(summary)

    rate_sweep.sort(key=lambda r: r["rate_hz"])
    delay_sweep.sort(key=lambda r: r["delay_s"])
    low = lowest_passing_rate_hz(rate_sweep)
    cliff = delay_cliff_s(delay_sweep)
    abs_cliff = delay_below_absolute_floor_s(delay_sweep)

    chroma_set = sorted(set(chroma_sources))
    chroma_note = (
        "MUSDB mix chromagram, same window as P3-C"
        if chroma_set == ["musdb_mix"] or set(chroma_set) <= {"musdb_mix", "cache"}
        else f"sources={chroma_set}"
    )

    receipt = {
        "label": "HOST-ONLY",
        "evidence_ladder": "HOST_PIXEL_VALIDATED",
        "not_c0": True,
        "not_silicon": True,
        "not_lgp": True,
        "student_gate": "OPEN",
        "phase": "GATE_C_CADENCE_HOST",
        "classification": "I/O cadence DESIGN evidence; not Gate C",
        "binding": BINDING,
        "firmware_root": str(fw),
        "firmware_sha": sha,
        "compiler": cmeta.get("compiler") or COMPILER,
        "frozen_map_version": FROZEN_MAP_VERSION,
        "gain_range": [GAIN_LO, GAIN_HI],
        "share_sources": list(SHARE_SOURCES),
        "composition_change_used": False,
        "native_hz": NATIVE_HZ,
        "hop_s": HOP_S,
        "hold_rates_hz": list(HOLD_RATES_HZ),
        "delays_s": list(DELAYS_S),
        "pass_rule": {
            "median_delta_min": 0.15,
            "fraction_of_native_min": NATIVE_KEEP_FRACTION,
            "p3c_holdout_median_delta_documented": P3C_HOLDOUT_MEDIAN_DELTA,
        },
        "corpus": {
            "set": "p3c_holdout",
            "n_requested": 10,
            "n_scored": len(meta_rows),
            "tracks": [m["track"] for m in meta_rows],
        },
        "method": {
            "hold": "zero-order hold of extra-DoF gain, then causal delay, then re-render",
            "native_zero_delay": "reuse P3-C LED dumps (do not resample LED frames)",
            "score": "p3c_quant.score_clip; Δ = partial r(head, share | mix) D minus B",
            "chroma": chroma_note,
        },
        "native": native_sum,
        "rate_sweep": rate_sweep,
        "delay_sweep": delay_sweep,
        "lowest_passing_rate_hz": low,
        "delay_cliff_s": cliff,
        "delay_below_absolute_floor_s": abs_cliff,
        "clips": {f"{fam}|{rate:g}|{delay:g}": per_cell[(fam, rate, delay)] for fam, rate, delay in cells},
    }
    outp = OUT / "receipt.json"
    outp.write_text(json.dumps(_jsonable(receipt), indent=2) + "\n")
    write_figure(rate_sweep, delay_sweep, native_median, FIG)
    write_doc(receipt, DOC)
    print(json.dumps(_jsonable({
        "label": receipt["label"],
        "not_c0": True,
        "native_median_delta": native_median,
        "lowest_passing_rate_hz": low,
        "delay_cliff_s": cliff,
        "delay_below_absolute_floor_s": abs_cliff,
        "rate_sweep": [{k: r[k] for k in ("rate_hz", "median_delta_pos_share", "verdict")} for r in rate_sweep],
        "delay_sweep": [{k: r[k] for k in ("delay_s", "median_delta_pos_share", "verdict")} for r in delay_sweep],
    }), indent=2))
    print(f"wrote {outp}")
    print(f"wrote {DOC}")
    print(f"wrote {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
