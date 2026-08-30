#!/usr/bin/env python3
"""P3-C: blinded host replay of firmware bloom + apply_brightness.

Not Demucs. Not a student. Not a lighting verdict. HOST-ONLY.
Challenge = oracle-ranked segments. Holdout = MUSDB test, not oracle-ranked.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

import numpy as np

from edgeai.mir.host_chroma import bloom_chromagram, host_chroma12
from edgeai.mir.k1_photons import PHOTONS_CURVE_MODE, apply_photons
from edgeai.mir.k1_render_host import compile_bloom, firmware_root, firmware_sha, render_bloom
from edgeai.mir.k1_visual_hooks import DEFAULT_HOOK_CONFIG, VisualHooks
from edgeai.mir.p3c_blind import permute_conditions, sealed_key
from edgeai.mir.p3c_html import write_page
from edgeai.mir.p3c_score import mean_abs_diff, mean_luminance, occupancy
from edgeai.mir.p3c_sets import challenge_ten, holdout_ten
from edgeai.mir.source_oracle import timebase
from edgeai.mir.trigger_budget import local_peaks, match_thresholds, triggers_per_minute
from edgeai.mir.visual_hook import (
    FROZEN_MAP_VERSION,
    MODULATION_WEIGHT,
    apply_frozen_map,
    modulate,
)

ROOT = Path("datasets/musdb18")
OUT = Path("artifacts/source_activity")
CACHE = OUT / "musdb18_oracle_cache"
P3C = OUT / "p3c"
HTML1 = Path("docs/mir/visual_replay/p3c1_continuous.html")
HTML2 = Path("docs/mir/visual_replay/p3c2_events.html")
KEY1 = Path("docs/mir/visual_replay/P3C1_BLIND_KEY_OPEN_AFTER_JUDGING.json")
KEY2 = Path("docs/mir/visual_replay/P3C2_BLIND_KEY_OPEN_AFTER_JUDGING.json")
SR = 16_000
HOP = 512
HOP_S = HOP / SR
SEGMENT_S = 8.0
PRE_S = 5.0
EVENT_TARGET_PER_MIN = 15.0
DISPLAY_STEP = 2
WARMUP_S = 1.0
BASE_PHOTONS = 0.675
SALT_C1 = "p3c1-v1"
SALT_C2 = "p3c2-v1"
HOLDOUT_SEED = 20260831


def _safe(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in name)


def _mono(x: np.ndarray) -> np.ndarray:
    y = np.asarray(x, dtype=np.float32)
    if y.ndim == 2:
        y = y.mean(axis=-1)
    return y.reshape(-1)


def _encode(leds: np.ndarray) -> str:
    return base64.b64encode(np.ascontiguousarray(leds, dtype=np.uint8).tobytes()).decode("ascii")


def _window(t_event: float, duration: float) -> tuple[float, float]:
    start = float(t_event) - PRE_S
    end = start + SEGMENT_S
    if start < 0.0:
        start = 0.0
        end = min(float(duration), SEGMENT_S)
    if end > duration:
        end = float(duration)
        start = max(0.0, end - SEGMENT_S)
    return start, max(0.5, end - start)


def _share_key(row: dict) -> str:
    cls = str(row.get("select_class") or "")
    src = str(row.get("source") or "")
    blob = cls + " " + src
    if "drums" in blob:
        return "drums_share"
    if "bass" in blob:
        return "bass_share"
    return "vocals_share"


def load_db():
    import musdb

    train = ROOT / "train"
    nested = ROOT / "musdb18" / "train"
    root = ROOT / "musdb18" if nested.is_dir() and not train.is_dir() else ROOT
    if not (root / "train").is_dir():
        raise SystemExit(f"MUSDB18 train/ missing under {ROOT}")
    return musdb.DB(root=str(root.resolve()), is_wav=False, sample_rate=SR)


def load_frozen() -> dict:
    raw = json.loads((OUT / "frozen_map_p3b.json").read_text())
    return raw["map"]


def load_cache(subset: str, name: str) -> dict:
    path = CACHE / f"{subset}_{_safe(name)}.npz"
    if not path.is_file():
        raise FileNotFoundError(path)
    data = np.load(path)
    return {k: data[k] for k in data.files}


def test_catalog() -> list[dict]:
    names = [p.name.replace(".stem.mp4", "") for p in sorted((ROOT / "test").glob("*.stem.mp4"))]
    rows = []
    for name in names:
        oracle = load_cache("test", name)
        dur = float(oracle["times"][-1]) + 0.5 * HOP_S
        rows.append({"track": name, "subset": "test", "duration_s": dur})
    return rows


def slice_oracle(oracle: dict, start: float, length: float) -> dict:
    t = np.asarray(oracle["times"], dtype=np.float64)
    i0 = int(np.searchsorted(t, start, side="left"))
    i1 = int(np.searchsorted(t, start + length, side="left"))
    i1 = max(i0 + 2, i1)
    out = {}
    for k, v in oracle.items():
        a = np.asarray(v)
        if a.shape[0] == t.shape[0]:
            out[k] = a[i0:i1]
        else:
            out[k] = a
    return out


def corpus_event_thresholds(items: list[tuple[dict, dict]]) -> dict:
    d_rms = []
    cc = []
    for _rec, oracle in items:
        mix = np.asarray(oracle["mix_rms"], dtype=np.float64)
        d_rms.append(np.abs(np.diff(mix, prepend=mix[:1])))
        cc.append(np.asarray(oracle["composition_change"], dtype=np.float64))
    a = np.concatenate(d_rms)
    b = np.concatenate(cc)
    ta, tb, na, nb = match_thresholds(
        a, b, hop_s=HOP_S, refractory_s=0.25, target_per_min=EVENT_TARGET_PER_MIN
    )
    return {
        "d_rms": float(ta),
        "composition_change": float(tb),
        "n_d_rms": int(na),
        "n_cc": int(nb),
        "refractory_s": 0.25,
        "hop_s": HOP_S,
    }


def photons_continuous(oracle: dict, fmap: dict, share_name: str) -> dict[str, np.ndarray]:
    n = len(oracle["times"])
    base = [BASE_PHOTONS] * n
    mix_f = apply_frozen_map(oracle["mix_rms"], fmap["mix_rms"])
    share_f = apply_frozen_map(oracle[share_name], fmap[share_name])
    return {
        "A": np.full(n, BASE_PHOTONS, dtype=np.float64),
        "B": np.asarray(modulate(base, mix_f, weight=MODULATION_WEIGHT), dtype=np.float64),
        "D": np.asarray(modulate(base, share_f, weight=MODULATION_WEIGHT), dtype=np.float64),
    }


def photons_events(series: np.ndarray, thresh: float) -> tuple[np.ndarray, list[int]]:
    hops = np.asarray(series, dtype=np.float64)
    ref = max(1, int(round(0.25 / HOP_S)))
    idx = local_peaks(hops, thresh=thresh, refractory=ref)
    fired = set(idx)
    hooks = VisualHooks(DEFAULT_HOOK_CONFIG)
    out = np.zeros(len(hops), dtype=np.float64)
    last_id = 0
    last_i = 0
    for i in range(len(hops)):
        is_on = i in fired
        if is_on:
            last_id = i + 1
            last_i = i
            age = 0
        else:
            age = int(round((i - last_i) * HOP_S * 1000.0)) if last_id else 10**6
        tick = hooks.tick(
            now_ms=int(round(i * HOP_S * 1000.0)),
            onset=is_on,
            onset_strength=1.0 if is_on else 0.0,
            event_id=last_id if last_id else 0,
            event_age_ms=age,
        )
        out[i] = hooks.apply_photons_knob(BASE_PHOTONS, tick.photon_scalar)
    return out, idx


def _clip_payload(clip_id: str, title: str, set_name: str, leds_map: dict, order: list[str], extra: dict) -> dict:
    fps = 1.0 / (HOP_S * DISPLAY_STEP)
    versions = []
    thin_t = 0
    for i, cond in enumerate(order):
        thin = leds_map[cond][::DISPLAY_STEP]
        thin_t = int(thin.shape[0])
        rec = {"label": f"Version {i + 1}", "leds": _encode(thin)}
        if extra.get("rates"):
            rec["triggers_per_min"] = extra["rates"][cond]
        versions.append(rec)
    return {
        "id": clip_id,
        "title": title,
        "set": set_name,
        "duration_s": float(thin_t / fps) if fps else 0.0,
        "fps": fps,
        "n_led": 160,
        "T": thin_t,
        "versions": versions,
    }


def main() -> int:
    fmap = load_frozen()
    receipt_b = json.loads((OUT / "receipt_musdb18_p3b.json").read_text())
    selected = receipt_b["selected"]
    challenge = challenge_ten(selected, k_per=2)
    held = holdout_ten(test_catalog(), challenge, n=10, seed=HOLDOUT_SEED)
    clips_spec = challenge + held

    # Load every cache once (thresholds need the whole corpus).
    cache_items: list[tuple[dict, dict]] = []
    lookup: dict[str, tuple[str, dict]] = {}
    for p in sorted(CACHE.glob("*.npz")):
        subset, _, rest = p.stem.partition("_")
        data = {k: np.load(p)[k] for k in np.load(p).files}
        rec = {"subset": subset, "track": rest}
        cache_items.append((rec, data))
    for row in clips_spec:
        lookup[row["track"]] = (row.get("subset") or "train", load_cache(row.get("subset") or "train", row["track"]))

    # Re-load with real names for challenge/holdout via musdb for mix PCM.
    db = load_db()
    tracks = {t.name: t for t in db}
    fw = firmware_root()
    sha = firmware_sha(fw)
    workdir = P3C / "_bloom_build"
    print(f"compiling bloom from {fw} @ {sha[:12]}", flush=True)
    binary, cmeta = compile_bloom(workdir)
    print(f"compiler {cmeta.get('compiler')} ok", flush=True)
    pre = render_bloom(
        binary,
        chroma=np.full((16, 12), 0.7, dtype=np.float32),
        times_s=np.arange(16, dtype=np.float64) * HOP_S,
    )
    if int(pre.max()) < 16:
        raise RuntimeError(f"bloom preflight black max={int(pre.max())}; extra DoF would be a no-op")
    print(f"preflight bloom_max={int(pre.max())}", flush=True)

    thresh = corpus_event_thresholds(cache_items)
    print("event thresholds", thresh, flush=True)

    keys_c1: dict = {}
    keys_c2: dict = {}
    html_c1: list[dict] = []
    html_c2: list[dict] = []
    scores: list[dict] = []

    P3C.mkdir(parents=True, exist_ok=True)

    for row in clips_spec:
        name = row["track"]
        subset = row.get("subset") or tracks[name].subset
        oracle_full = load_cache(subset, name)
        duration = float(oracle_full["times"][-1]) + 0.5 * HOP_S
        start, length = _window(float(row.get("t") or 0.0), duration)
        oracle = slice_oracle(oracle_full, start, length)
        track = tracks[name]
        mix = _mono(track.audio)
        i0 = int(round(start * SR))
        i1 = int(round((start + length) * SR))
        sl = mix[i0:i1]
        _ct, chroma = host_chroma12(sl, sr=SR, hop=HOP)
        n = min(len(oracle["times"]), chroma.shape[0])
        oracle = {k: (v[:n] if np.asarray(v).shape[:1] == (len(oracle["times"]),) else v) for k, v in oracle.items()}
        chroma = chroma[:n]
        times = np.arange(n, dtype=np.float64) * HOP_S
        drive = bloom_chromagram(chroma, oracle["mix_rms"][:n])
        print(f"bloom {subset} {name} n={n} start={start:.2f}", flush=True)
        warm = max(1, int(round(WARMUP_S / HOP_S)))
        drive_w = np.vstack([np.repeat(drive[:1], warm, axis=0), drive])
        times_w = np.arange(drive_w.shape[0], dtype=np.float64) * HOP_S
        leds_w = render_bloom(binary, chroma=drive_w, times_s=times_w)
        leds = leds_w[warm:]
        print(
            f"  chroma_max={float(chroma.max()):.3f} drive_mean={float(drive.mean()):.3f} bloom_max={int(leds.max())} mix={float(np.mean(oracle['mix_rms'])):.3f}",
            flush=True,
        )
        if leds.shape[0] != n:
            n = min(n, leds.shape[0])
            leds = leds[:n]
            chroma = chroma[:n]
            oracle = {k: (v[:n] if isinstance(v, np.ndarray) and v.shape[:1] == (len(times),) else v) for k, v in oracle.items()}
            times = times[:n]

        share_name = _share_key(row)
        ph = photons_continuous(oracle, fmap, share_name)
        cond_leds = {k: apply_photons(leds, ph[k]) for k in ("A", "B", "D")}

        d_rms = np.abs(np.diff(oracle["mix_rms"].astype(np.float64), prepend=oracle["mix_rms"][:1]))
        ph_ctrl, idx_ctrl = photons_events(d_rms, thresh["d_rms"])
        ph_mir, idx_mir = photons_events(oracle["composition_change"], thresh["composition_change"])
        event_leds = {
            "control": apply_photons(leds, ph_ctrl),
            "mir": apply_photons(leds, ph_mir),
        }
        dur_s = n * HOP_S
        rates = {
            "control": triggers_per_minute(len(idx_ctrl), dur_s),
            "mir": triggers_per_minute(len(idx_mir), dur_s),
        }

        cid = _safe(name) + "_" + row.get("set", "x")
        order1, key1 = permute_conditions(("A", "B", "D"), clip_id=cid, salt=SALT_C1)
        order2, key2 = permute_conditions(("control", "mir"), clip_id=cid, salt=SALT_C2)
        keys_c1[cid] = {**key1, "track": name, "set": row.get("set"), "share_driver": share_name}
        keys_c2[cid] = {**key2, "track": name, "set": row.get("set")}

        html_c1.append(_clip_payload(cid, name, row.get("set", "challenge"), cond_leds, order1, extra={}))
        html_c2.append(
            _clip_payload(cid, name, row.get("set", "challenge"), event_leds, order2, extra={"rates": rates})
        )

        np.savez_compressed(
            P3C / f"{cid}_leds.npz",
            bloom=leds,
            A=cond_leds["A"],
            B=cond_leds["B"],
            D=cond_leds["D"],
            control=event_leds["control"],
            mir=event_leds["mir"],
            photons_A=ph["A"],
            photons_B=ph["B"],
            photons_D=ph["D"],
        )
        scores.append(
            {
                "track": name,
                "set": row.get("set"),
                "share_driver": share_name,
                "n": n,
                "start_s": start,
                "mad_B_vs_D": mean_abs_diff(cond_leds["B"], cond_leds["D"]),
                "mad_A_vs_B": mean_abs_diff(cond_leds["A"], cond_leds["B"]),
                "mad_A_vs_D": mean_abs_diff(cond_leds["A"], cond_leds["D"]),
                "mad_control_vs_mir": mean_abs_diff(event_leds["control"], event_leds["mir"]),
                "lum_A": mean_luminance(cond_leds["A"]),
                "lum_B": mean_luminance(cond_leds["B"]),
                "lum_D": mean_luminance(cond_leds["D"]),
                "occ_B": occupancy(cond_leds["B"]),
                "occ_D": occupancy(cond_leds["D"]),
                "triggers_control": len(idx_ctrl),
                "triggers_mir": len(idx_mir),
                "triggers_per_min_control": rates["control"],
                "triggers_per_min_mir": rates["mir"],
            }
        )

    write_page(
        HTML1,
        title="P3-C1 · extra brightness on the same bloom",
        question="Which version makes more musical sense as extra brightness on the same visual engine?",
        note="Firmware bloom, then the shipping brightness curve. Same extra control, same range, same gain. Labels are sealed. HOST-ONLY. Not a product lighting call. MUSDB educational/NC.",
        clips=html_c1,
        n_versions=3,
    )
    write_page(
        HTML2,
        title="P3-C2 · the same structural accent, different triggers",
        question="Which version picks better moments for the same flash? Rates are shown so quantity is not the test.",
        note="Existing onset→brightness accent (tau 100 ms, gain 0.16). Only the trigger series changes. HOST-ONLY. Not a product lighting call.",
        clips=html_c2,
        n_versions=2,
    )
    KEY1.write_text(json.dumps(sealed_key(keys_c1), indent=2) + "\n")
    KEY2.write_text(json.dumps(sealed_key(keys_c2), indent=2) + "\n")

    def _mean(field: str, set_name: str) -> float:
        xs = [s[field] for s in scores if s.get("set") == set_name]
        return float(np.mean(xs)) if xs else float("nan")

    receipt = {
        "label": "HOST-ONLY",
        "phase": "P3-C",
        "engine": "firmware light_mode_bloom + apply_brightness photons_curve",
        "photons_curve_mode": PHOTONS_CURVE_MODE,
        "firmware_root": str(fw),
        "firmware_sha": sha,
        "frozen_map_version": FROZEN_MAP_VERSION,
        "modulation_weight": MODULATION_WEIGHT,
        "base_photons": BASE_PHOTONS,
        "timebase": timebase(sr=SR, hop=HOP, lag_s=0.5),
        "display_step": DISPLAY_STEP,
        "segment_s": SEGMENT_S,
        "chroma": "HOST-ONLY causal 12-bin STFT; identical across A/B/D",
        "commercial_training_lineage": False,
        "demucs_installed": False,
        "student_gate": "OPEN",
        "event_thresholds": thresh,
        "n_challenge": sum(1 for r in clips_spec if r.get("set") == "challenge"),
        "n_holdout": sum(1 for r in clips_spec if r.get("set") == "holdout"),
        "challenge_tracks": [r["track"] for r in challenge],
        "holdout_tracks": [r["track"] for r in held],
        "scores": scores,
        "summary": {
            "challenge_mean_mad_B_vs_D": _mean("mad_B_vs_D", "challenge"),
            "holdout_mean_mad_B_vs_D": _mean("mad_B_vs_D", "holdout"),
            "challenge_mean_mad_control_vs_mir": _mean("mad_control_vs_mir", "challenge"),
            "holdout_mean_mad_control_vs_mir": _mean("mad_control_vs_mir", "holdout"),
            "challenge_mean_trig_control": _mean("triggers_per_min_control", "challenge"),
            "challenge_mean_trig_mir": _mean("triggers_per_min_mir", "challenge"),
            "holdout_mean_trig_control": _mean("triggers_per_min_control", "holdout"),
            "holdout_mean_trig_mir": _mean("triggers_per_min_mir", "holdout"),
        },
        "html": [str(HTML1), str(HTML2)],
        "blind_keys": [str(KEY1), str(KEY2)],
        "not_a_lighting_verdict": True,
    }
    outp = P3C / "receipt_musdb18_p3c.json"
    outp.write_text(json.dumps(receipt, indent=2) + "\n")
    # Copy a small committed receipt pointer without LED dumps.
    Path("docs/mir/P3C_RECEIPT.json").write_text(json.dumps({k: receipt[k] for k in receipt if k != "scores"}, indent=2) + "\n")
    print(json.dumps(receipt["summary"], indent=2))
    print(f"wrote {HTML1} ({HTML1.stat().st_size} bytes)")
    print(f"wrote {HTML2} ({HTML2.stat().st_size} bytes)")
    print(f"wrote {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
