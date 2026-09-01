#!/usr/bin/env python3
"""J3: frozen MUSDB-5 Demucs share approximation versus the stem oracle.

HOST-ONLY. No playback. No waveform files. Metrics use the unshifted hop grid;
lag is diagnostic only and is never applied to the authority metrics.
"""

from __future__ import annotations

import argparse
import gc
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Mapping

import numpy as np
from numpy.typing import NDArray

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgeai.mir.demucs_local_loader import (  # noqa: E402
    CHECKPOINT,
    CHECKPOINT_SHA256,
    pinned_demucs_model,
)
from edgeai.mir.demucs_teacher import decode_audio_stream, separate_to_envelopes  # noqa: E402
from edgeai.mir.source_power import SOURCES, frame_mean_square  # noqa: E402

SR = 44_100
HOP = 512
SOURCE_STREAMS = {"drums": 1, "bass": 2, "other": 3, "vocals": 4}
FROZEN_TRACKS = (
    ("vocal_dominant", "Side Effects Project - Sing With Me"),
    ("drum_dominant", "PR - Happy Daze"),
    ("bass_heavy", "Skelpolu - Resurrection"),
    ("other_heavy", "Timboz - Pony"),
    ("balanced", "Cristina Vane - So Easy"),
)
MUSDB_TEST = ROOT / "datasets/musdb18/test"
DEFAULT_RECEIPT = ROOT / "docs/mir/receipts/demucs/MUSDB5_CAL.json"


def _share_from_power(power: Mapping[str, NDArray]) -> tuple[NDArray, NDArray]:
    n = min(np.asarray(power[source]).size for source in SOURCES)
    matrix = np.stack(
        [np.asarray(power[source], dtype=np.float64)[:n] for source in SOURCES], axis=1
    )
    total = matrix.sum(axis=1)
    share = np.zeros_like(matrix)
    nonsilent = total > 1e-10
    share[nonsilent] = matrix[nonsilent] / total[nonsilent, None]
    return share, total


def _rankdata(values: NDArray) -> NDArray[np.float64]:
    values = np.asarray(values, dtype=np.float64)
    order = np.argsort(values, kind="mergesort")
    sorted_values = values[order]
    ranks = np.empty(values.size, dtype=np.float64)
    start = 0
    while start < values.size:
        end = start + 1
        while end < values.size and sorted_values[end] == sorted_values[start]:
            end += 1
        ranks[order[start:end]] = 0.5 * (start + end - 1) + 1.0
        start = end
    return ranks


def _pearson(a: NDArray, b: NDArray) -> float:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    n = min(a.size, b.size)
    if n < 8:
        return float("nan")
    a, b = a[:n], b[:n]
    if a.std() < 1e-12 or b.std() < 1e-12:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def _spearman(a: NDArray, b: NDArray) -> float:
    return _pearson(_rankdata(a), _rankdata(b))


def best_source_mapping(
    predicted: Mapping[str, NDArray], oracle: Mapping[str, NDArray]
) -> dict[str, object]:
    """Find the global source assignment; identity must win or J3 is red."""
    scores = {
        (predicted_source, oracle_source): _spearman(
            predicted[predicted_source], oracle[oracle_source]
        )
        for predicted_source in SOURCES
        for oracle_source in SOURCES
    }
    candidates: list[tuple[float, tuple[str, ...]]] = []
    for permutation in itertools.permutations(SOURCES):
        values = [scores[(predicted, target)] for predicted, target in zip(SOURCES, permutation)]
        score = float(np.mean(values)) if all(np.isfinite(values)) else -math.inf
        candidates.append((score, permutation))
    candidates.sort(key=lambda row: row[0], reverse=True)
    best_score, best = candidates[0]
    runner_up = candidates[1][0]
    identity = tuple(SOURCES)
    return {
        "valid": bool(best == identity and np.isfinite(best_score)),
        "best_assignment": {source: target for source, target in zip(SOURCES, best)},
        "best_mean_spearman": best_score,
        "identity_mean_spearman": float(
            np.mean([scores[(source, source)] for source in SOURCES])
        ),
        "margin_over_runner_up": best_score - runner_up,
        "matrix": {
            source: {target: scores[(source, target)] for target in SOURCES}
            for source in SOURCES
        },
    }


def _simplex_js(predicted: NDArray, oracle: NDArray) -> float:
    p = np.asarray(predicted, dtype=np.float64)
    q = np.asarray(oracle, dtype=np.float64)
    active = (p.sum(axis=1) > 0) | (q.sum(axis=1) > 0)
    if not np.any(active):
        return 0.0
    p, q = p[active], q[active]
    p_sum = p.sum(axis=1, keepdims=True)
    q_sum = q.sum(axis=1, keepdims=True)
    p = np.divide(p, p_sum, out=np.zeros_like(p), where=p_sum > 0)
    q = np.divide(q, q_sum, out=np.zeros_like(q), where=q_sum > 0)
    middle = 0.5 * (p + q)
    p_term = np.zeros_like(p)
    q_term = np.zeros_like(q)
    p_mask = p > 0
    q_mask = q > 0
    p_term[p_mask] = p[p_mask] * np.log(p[p_mask] / middle[p_mask])
    q_term[q_mask] = q[q_mask] * np.log(q[q_mask] / middle[q_mask])
    return float(np.mean(0.5 * (p_term.sum(axis=1) + q_term.sum(axis=1))))


def _best_lag_seconds(predicted: NDArray, oracle: NDArray, *, max_seconds: float = 1.0) -> float:
    max_hops = int(round(max_seconds * SR / HOP))
    best = (-math.inf, 0)
    for lag in range(-max_hops, max_hops + 1):
        if lag < 0:
            a, b = predicted[-lag:], oracle[:lag]
        elif lag > 0:
            a, b = predicted[:-lag], oracle[lag:]
        else:
            a, b = predicted, oracle
        score = _pearson(a, b)
        if np.isfinite(score) and score > best[0]:
            best = (score, lag)
    return float(best[1] * HOP / SR)


def _decode_oracle(track_path: Path) -> tuple[dict[str, NDArray], int]:
    power: dict[str, NDArray] = {}
    sample_count = 0
    for source in SOURCES:
        waveform = decode_audio_stream(
            track_path,
            stream_index=SOURCE_STREAMS[source],
            samplerate=SR,
            channels=2,
        )
        sample_count = max(sample_count, waveform.shape[1])
        # ffmpeg helper is channel-first; the shared oracle primitive consumes
        # time-first stereo, exactly as musdb.Track target audio does.
        power[source] = frame_mean_square(waveform.T, HOP)
        del waveform
    return power, sample_count


def run_calibration() -> tuple[dict[str, object], int]:
    pooled_predicted = {source: [] for source in SOURCES}
    pooled_oracle = {source: [] for source in SOURCES}
    track_receipts: list[dict[str, object]] = []
    all_sum_error: list[NDArray] = []
    finite_count = 0
    value_count = 0
    silence_ok = True

    with pinned_demucs_model(CHECKPOINT) as model:
        source_order = list(model.sources)
        if source_order != ["drums", "bass", "other", "vocals"]:
            raise RuntimeError(f"DEMUCS_SOURCE_ORDER_INVALID: {source_order}")
        for index, (role, track) in enumerate(FROZEN_TRACKS, start=1):
            path = MUSDB_TEST / f"{track}.stem.mp4"
            print(f"J3_TRACK_START {index}/5 {track}", flush=True)
            mixture = decode_audio_stream(path, stream_index=0, samplerate=SR, channels=2)
            demucs = separate_to_envelopes(model, mixture, samplerate=SR, hop=HOP)
            del mixture
            oracle_power, sample_count = _decode_oracle(path)
            oracle_share, oracle_total = _share_from_power(oracle_power)
            predicted_share = np.stack(
                [np.asarray(demucs["share"][source]) for source in SOURCES], axis=1
            )
            predicted_total = np.asarray(demucs["total_power"])
            n = min(predicted_share.shape[0], oracle_share.shape[0])
            predicted_share = predicted_share[:n]
            predicted_total = predicted_total[:n]
            oracle_share = oracle_share[:n]
            oracle_total = oracle_total[:n]

            for source_index, source in enumerate(SOURCES):
                pooled_predicted[source].append(predicted_share[:, source_index])
                pooled_oracle[source].append(oracle_share[:, source_index])
            expected_sum = (predicted_total > 1e-10).astype(np.float64)
            all_sum_error.append(np.abs(predicted_share.sum(axis=1) - expected_sum))
            finite_count += int(np.isfinite(predicted_share).sum())
            value_count += int(predicted_share.size)
            predicted_silent = predicted_total <= 1e-10
            oracle_silent = oracle_total <= 1e-10
            silence_ok = silence_ok and bool(
                np.all(predicted_share[predicted_silent] == 0)
                and np.all(oracle_share[oracle_silent] == 0)
            )
            track_receipts.append(
                {
                    "role": role,
                    "track": track,
                    "source_file": str(path),
                    "samples": sample_count,
                    "hops": n,
                    "oracle_silent_hops": int(oracle_silent.sum()),
                    "demucs_silent_hops": int(predicted_silent.sum()),
                    "finite": bool(np.all(np.isfinite(predicted_share))),
                }
            )
            print(f"J3_TRACK_DONE {index}/5 {track} hops={n}", flush=True)
            del demucs, oracle_power, oracle_share, predicted_share
            gc.collect()

    predicted = {source: np.concatenate(pooled_predicted[source]) for source in SOURCES}
    oracle = {source: np.concatenate(pooled_oracle[source]) for source in SOURCES}
    per_source: dict[str, dict[str, float]] = {}
    lag_diagnostic: dict[str, float] = {}
    for source in SOURCES:
        delta = predicted[source] - oracle[source]
        per_source[source] = {
            "spearman": _spearman(predicted[source], oracle[source]),
            "pearson": _pearson(predicted[source], oracle[source]),
            "mae": float(np.mean(np.abs(delta))),
            "rmse": float(np.sqrt(np.mean(delta * delta))),
        }
        lag_diagnostic[source] = _best_lag_seconds(predicted[source], oracle[source])

    predicted_matrix = np.stack([predicted[source] for source in SOURCES], axis=1)
    oracle_matrix = np.stack([oracle[source] for source in SOURCES], axis=1)
    mapping = best_source_mapping(predicted, oracle)
    sum_error = np.concatenate(all_sum_error)
    finite_fraction = finite_count / value_count if value_count else 0.0
    hard_checks = {
        "frozen_n_is_five": len(track_receipts) == 5,
        "mapping_valid": mapping["valid"],
        "silence_ok": silence_ok,
        "finite_hop_fraction_is_one": finite_fraction == 1.0,
        "simplex_error_p99_lte_1e-6": float(np.percentile(sum_error, 99)) <= 1e-6,
    }
    passed = all(hard_checks.values())
    receipt: dict[str, object] = {
        "job": "J3",
        "label": "HOST-ONLY",
        "verdict": "FUNCTIONAL_CALIBRATION_PASS" if passed else "FUNCTIONAL_CALIBRATION_RED",
        "teacher_authority": "MUSDB_STEMS",
        "demucs_role": "approximation_calibration_only",
        "teacher_schema": "DEMUCS_TEACHER_SCHEMA_V1",
        "checkpoint_sha256": CHECKPOINT_SHA256,
        "n": len(track_receipts),
        "claim": "N=5 FUNCTIONAL_CALIBRATION — NOT GENERALIZATION CLAIM",
        "stems_beat_demucs": True,
        "tracks": [track for _, track in FROZEN_TRACKS],
        "track_receipts": track_receipts,
        "per_source": per_source,
        "share_sum_error_p99": float(np.percentile(sum_error, 99)),
        "simplex_js_mean": _simplex_js(predicted_matrix, oracle_matrix),
        "timing_lag_diagnostic_s": lag_diagnostic,
        "source_mapping": mapping,
        "mapping_valid": mapping["valid"],
        "silence_ok": silence_ok,
        "finite_hop_fraction": finite_fraction,
        "lag_corrected": False,
        "sdr_used_for_pass": False,
        "waveforms_persisted": False,
        "network_fetch": False,
        "titan": False,
        "student_io_frozen": False,
        "hard_checks": hard_checks,
    }
    return receipt, 0 if passed else 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the frozen MUSDB-5 Demucs calibration.")
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args(argv)
    receipt, code = run_calibration()
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(receipt["verdict"], flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
