#!/usr/bin/env python3
"""P3-C: blinded host replay of firmware palette path.

Continuous: waveform_tempo (palette-native, tempo-locked scroll).
Events: comet (same palette, bass-onset fire) over that tempo floor.
Not chroma HSV. Not Demucs. HOST-ONLY.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

import numpy as np

from edgeai.mir.host_chroma import extra_gain, host_chroma12, preview_encode
from edgeai.mir.k1_render_host import (
    PALETTE_RENDER_PARAMS,
    compile_mode,
    firmware_root,
    firmware_sha,
    render_mode,
)
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
PREVIEW_EXPOSURE = 2.2
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


def continuous_gains(oracle: dict, fmap: dict, share_name: str) -> dict[str, np.ndarray]:
    n = len(oracle["times"])
    mix_f = apply_frozen_map(oracle["mix_rms"], fmap["mix_rms"])
    share_f = apply_frozen_map(oracle[share_name], fmap[share_name])
    mid = extra_gain(np.array([0.5]))[0]
    return {
        "A": np.full(n, mid, dtype=np.float64),
        "B": extra_gain(np.asarray(mix_f)),
        "D": extra_gain(np.asarray(share_f)),
    }


def event_hits(series: np.ndarray, thresh: float) -> tuple[np.ndarray, list[int], np.ndarray]:
    hops = np.asarray(series, dtype=np.float64)
    ref = max(1, int(round(0.25 / HOP_S)))
    idx = local_peaks(hops, thresh=thresh, refractory=ref)
    fired = np.zeros(len(hops), dtype=np.int32)
    strength = np.zeros(len(hops), dtype=np.float64)
    for i in idx:
        fired[i] = 1
        strength[i] = 1.0
    return fired, idx, strength


def write_still_sheet(
    path: Path,
    scores: list[dict],
    set_name: str,
    *,
    keys: tuple[str, ...],
    labels: tuple[str, ...],
    title: str,
    t_s: float = 2.0,
) -> None:
    """Instrument stills from the LED dump. Not a lighting verdict."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = [s for s in scores if s.get("set") == set_name][:4]
    if not rows:
        return
    n = len(rows)
    fig, axes = plt.subplots(n, len(keys), figsize=(4.2 * len(keys), 1.85 * n), squeeze=False)
    fig.patch.set_facecolor("#f4efe6")
    fig.suptitle(title, fontsize=11, color="#1b1814")
    for r, rec in enumerate(rows):
        npz = np.load(P3C / f"{_safe(rec['track'])}_{set_name}_leds.npz")
        fps = 1.0 / (HOP_S * DISPLAY_STEP)
        fi = int(round(t_s * fps))
        for c, key in enumerate(keys):
            ax = axes[r, c]
            frame = np.asarray(npz[key], dtype=np.uint8)
            fi_c = min(fi, frame.shape[0] - 1)
            rgb = frame[fi_c]
            img = np.repeat(rgb[np.newaxis, :, :], 18, axis=0)
            ax.imshow(img, interpolation="nearest", aspect="auto")
            ax.set_xticks([])
            ax.set_yticks([])
            if r == 0:
                ax.set_title(labels[c], fontsize=9, color="#1b1814")
            if c == 0:
                ax.set_ylabel(rec["track"][:28], fontsize=7, color="#6a645c")
            ax.text(
                2,
                2,
                f"lum {mean_luminance(frame[fi_c : fi_c + 1]):.0f}  max {int(rgb.max())}",
                color="white",
                fontsize=6,
                va="top",
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


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
    print(f"compiling waveform_tempo + comet from {fw} @ {sha[:12]}", flush=True)
    tempo_bin, cmeta = compile_mode(P3C / "_tempo_build", mode="waveform_tempo")
    comet_bin, _ = compile_mode(P3C / "_comet_build", mode="comet")
    print(f"compiler {cmeta.get('compiler')} ok palette_index={PALETTE_RENDER_PARAMS['palette_index']}", flush=True)
    pre_t = np.arange(48, dtype=np.float64) * HOP_S
    pre_c = np.full((48, 12), 0.35, dtype=np.float64)
    pre_c[:, 9] = 0.95
    pre_wf = np.full(48, 0.85, dtype=np.float64)
    pre_raw = render_mode(tempo_bin, times_s=pre_t, chroma=pre_c, waveform_peak=pre_wf)
    pre = preview_encode(pre_raw, exposure=PREVIEW_EXPOSURE)
    pre_occ = occupancy(pre[24:])
    if int(pre.max()) < 80:
        raise RuntimeError(f"palette waveform_tempo preflight too dim max={int(pre.max())}")
    if pre_occ < 0.05:
        raise RuntimeError(f"palette waveform_tempo preflight too sparse occ={pre_occ:.3f}")
    print(
        f"preflight tempo_max={int(pre.max())} lum={float(mean_luminance(pre)):.1f} occ={pre_occ:.3f}",
        flush=True,
    )

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
        print(f"tempo/comet {subset} {name} n={n} start={start:.2f}", flush=True)
        share_name = _share_key(row)
        gains = continuous_gains(oracle, fmap, share_name)
        warm = max(1, int(round(WARMUP_S / HOP_S)))
        times_w = np.arange(n + warm, dtype=np.float64) * HOP_S
        chroma_w = np.vstack([np.repeat(chroma[:1], warm, axis=0), chroma])
        cond_raw = {}
        cond_leds = {}
        for key in ("A", "B", "D"):
            g = np.concatenate([np.repeat(gains[key][:1], warm), gains[key]])
            chroma_g = np.clip(chroma_w * g.reshape(-1, 1), 0.0, 1.0)
            raw = render_mode(
                tempo_bin,
                times_s=times_w,
                chroma=chroma_g,
                waveform_peak=g,
            )
            cond_raw[key] = raw[warm:]
            cond_leds[key] = preview_encode(cond_raw[key], exposure=PREVIEW_EXPOSURE)

        d_rms = np.abs(np.diff(oracle["mix_rms"].astype(np.float64), prepend=oracle["mix_rms"][:1]))
        on_ctrl, idx_ctrl, st_ctrl = event_hits(d_rms, thresh["d_rms"])
        on_mir, idx_mir, st_mir = event_hits(oracle["composition_change"], thresh["composition_change"])
        river_floor = cond_raw["A"]
        event_leds = {}
        for key, onset, strength in (("control", on_ctrl, st_ctrl), ("mir", on_mir, st_mir)):
            on_w = np.concatenate([np.zeros(warm, dtype=np.int32), onset])
            st_w = np.concatenate([np.zeros(warm, dtype=np.float64), strength])
            comet = render_mode(
                comet_bin,
                times_s=times_w,
                chroma=chroma_w,
                bass_onset=on_w,
                bass_strength=st_w,
            )[warm:]
            event_leds[key] = preview_encode(np.maximum(river_floor, comet), exposure=PREVIEW_EXPOSURE)
        print(
            f"  peakA={float(gains['A'].mean()):.3f} lumA={mean_luminance(cond_leds['A']):.1f} "
            f"lumB={mean_luminance(cond_leds['B']):.1f} lumD={mean_luminance(cond_leds['D']):.1f} "
            f"maxA={int(cond_leds['A'].max())} occA={occupancy(cond_leds['A']):.3f}",
            flush=True,
        )
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
            A=cond_leds["A"],
            B=cond_leds["B"],
            D=cond_leds["D"],
            control=event_leds["control"],
            mir=event_leds["mir"],
            gain_A=gains["A"],
            gain_B=gains["B"],
            gain_D=gains["D"],
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
        title="P3-C1 · same Waveform Tempo, extra control from different drivers",
        question="Which version makes more musical sense as extra energy in the same Waveform Tempo?",
        note="Firmware Waveform Tempo on the product palette path (not chroma HSV). Same extra gain, same range. Host preview is exposure-corrected so the page is readable. Labels sealed. HOST-ONLY. Not a product lighting call. MUSDB educational/NC.",
        clips=html_c1,
        n_versions=3,
    )
    write_page(
        HTML2,
        title="P3-C2 · the same comet, different triggers",
        question="Which version picks better moments for the same comet launch? Rates are shown so quantity is not the test.",
        note="Firmware comet launches over the same Waveform Tempo floor. Same launch, same palette. Only the trigger series changes. HOST-ONLY. Not a product lighting call.",
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
        "engine": {
            "continuous": "firmware light_mode_waveform_tempo",
            "events": "firmware light_mode_comet",
            "colour": "PALETTE_MODE + K1_Ultraviolet_Bright (index 43); chromatic HSV off",
            "square_iter": 0.0,
            "preview": f"sRGB + exposure {PREVIEW_EXPOSURE} (host dump is pre-gamma)",
            "host_tempo": "locked 120 BPM phase from frame ms; identical across A/B/D",
        },
        "firmware_root": str(fw),
        "firmware_sha": sha,
        "frozen_map_version": FROZEN_MAP_VERSION,
        "modulation_weight": MODULATION_WEIGHT,
        "extra_dof": "waveform peak + chroma gain in [0.62, 1.0] from frozen mix vs share",
        "timebase": timebase(sr=SR, hop=HOP, lag_s=0.5),
        "display_step": DISPLAY_STEP,
        "segment_s": SEGMENT_S,
        "palette_params": PALETTE_RENDER_PARAMS,
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
    write_still_sheet(
        P3C / "stills_continuous_challenge.png",
        scores,
        "challenge",
        keys=("A", "B", "D"),
        labels=("A", "B", "D"),
        title="HOST-ONLY Waveform Tempo dump  ·  challenge t=2.0s  ·  instrument, not the blinded page",
        t_s=2.0,
    )
    write_still_sheet(
        P3C / "stills_events_challenge.png",
        scores,
        "challenge",
        keys=("control", "mir"),
        labels=("control", "mir"),
        title="HOST-ONLY comet-over-tempo dump  ·  challenge t=2.0s  ·  instrument, not the blinded page",
        t_s=2.0,
    )
    print(json.dumps(receipt["summary"], indent=2))
    print(f"wrote {HTML1} ({HTML1.stat().st_size} bytes)")
    print(f"wrote {HTML2} ({HTML2.stat().st_size} bytes)")
    print(f"wrote {outp}")
    print(f"wrote {P3C / 'stills_continuous_challenge.png'}")
    print(f"wrote {P3C / 'stills_events_challenge.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
