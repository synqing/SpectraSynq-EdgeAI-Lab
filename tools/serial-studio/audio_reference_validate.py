#!/usr/bin/env python3
"""Strict quantitative validation for a Serial Studio Audio CSV witness.

This tool deliberately does not share code with Serial Studio's ``csv2wav``
example.  It never repairs samples, removes DC, normalises channels, dithers,
clips, skips malformed rows, guesses a sample representation, installs a
dependency, plays audio or touches a DUT.

The CSV ``Elapsed (s)`` column is HOST_AUDIO_REFERENCE_TIME.  It is not a K1
device clock and cannot prove the K1 microphone/PDM/PCM capture path.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

try:
    import numpy as np
    import soundfile as sf
    from scipy import signal
except ImportError as import_error:  # pragma: no cover - exercised by subprocess policy tests
    np = None  # type: ignore[assignment]
    sf = None  # type: ignore[assignment]
    signal = None  # type: ignore[assignment]
    DEPENDENCY_ERROR: ImportError | None = import_error
else:
    DEPENDENCY_ERROR = None


SCHEMA = "spectrasynq.audio-reference-validation.v1"
PROFILE_SCHEMA = "spectrasynq.audio-reference-scoring-profile.v1"
TOOL_ID = "spectrasynq.audio-reference-validate"
TOOL_VERSION = "1.0.0"
TIME_AUTHORITY = "HOST_AUDIO_REFERENCE_TIME"
CHANNEL_PATTERN = re.compile(r"^Channel ([1-9][0-9]*)$")
INTEGER_PATTERN = re.compile(r"^[+-]?[0-9]+$")

FORMAT_CONTRACTS: dict[str, dict[str, Any]] = {
    "float32_normalized": {"kind": "float", "minimum": -1.0, "maximum": 1.0, "scale": 1.0},
    "float32_native": {"kind": "float", "minimum": None, "maximum": None, "scale": 1.0},
    "uint8_native": {"kind": "integer", "minimum": 0, "maximum": 255, "scale": 128.0, "offset": 128.0},
    "int16_native": {"kind": "integer", "minimum": -32768, "maximum": 32767, "scale": 32768.0, "offset": 0.0},
    "int24_native": {"kind": "integer", "minimum": -8388608, "maximum": 8388607, "scale": 8388608.0, "offset": 0.0},
    "int32_native": {"kind": "integer", "minimum": -2147483648, "maximum": 2147483647, "scale": 2147483648.0, "offset": 0.0},
}


class ValidationFailure(Exception):
    """Stable, machine-readable validation failure."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class Capture:
    times_s: Any
    raw_samples: Any
    samples: Any
    headers: tuple[str, ...]
    representation: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _finite_float(text: str, *, row: int, column: str) -> float:
    if text.strip() == "":
        raise ValidationFailure("CSV_BLANK_CELL", f"row {row} column {column} is blank")
    try:
        value = float(text)
    except ValueError as error:
        raise ValidationFailure(
            "CSV_NONNUMERIC", f"row {row} column {column} is not numeric"
        ) from error
    if not math.isfinite(value):
        code = "TIMESTAMP_NONFINITE" if column == "Elapsed (s)" else "SAMPLE_NONFINITE"
        raise ValidationFailure(code, f"row {row} column {column} is not finite")
    return value


def _decode_sample(text: str, representation: str, *, row: int, column: str) -> tuple[float, float]:
    contract = FORMAT_CONTRACTS[representation]
    if contract["kind"] == "integer":
        if not INTEGER_PATTERN.fullmatch(text.strip()):
            try:
                possible_nonfinite = float(text)
            except ValueError:
                possible_nonfinite = None
            if possible_nonfinite is not None and not math.isfinite(possible_nonfinite):
                raise ValidationFailure(
                    "SAMPLE_NONFINITE", f"row {row} column {column} is not finite"
                )
            raise ValidationFailure(
                "SAMPLE_NOT_INTEGER",
                f"row {row} column {column} is not an integer in {representation}",
            )
        raw: float = float(int(text, 10))
    else:
        raw = _finite_float(text, row=row, column=column)

    minimum = contract["minimum"]
    maximum = contract["maximum"]
    if minimum is not None and (raw < minimum or raw > maximum):
        raise ValidationFailure(
            "SAMPLE_OUT_OF_RANGE",
            f"row {row} column {column} value {raw:g} is outside "
            f"[{minimum}, {maximum}] for {representation}",
        )
    offset = float(contract.get("offset", 0.0))
    normalised = (raw - offset) / float(contract["scale"])
    return raw, normalised


def read_serial_studio_csv(path: Path, representation: str) -> Capture:
    """Read every CSV row strictly and apply only the declared affine PCM decode."""

    if representation not in FORMAT_CONTRACTS:
        raise ValidationFailure("FORMAT_UNKNOWN", f"unsupported representation: {representation}")
    try:
        handle = path.open("r", encoding="utf-8-sig", errors="strict", newline="")
    except (OSError, UnicodeError) as error:
        raise ValidationFailure("CSV_UNREADABLE", f"cannot open CSV: {error}") from error

    times: list[float] = []
    raw_rows: list[list[float]] = []
    decoded_rows: list[list[float]] = []
    try:
        with handle:
            reader = csv.reader(handle)
            try:
                header = next(reader)
            except StopIteration as error:
                raise ValidationFailure("CSV_EMPTY", "CSV is empty") from error
            if not header or header[0] != "Elapsed (s)":
                raise ValidationFailure(
                    "CSV_ELAPSED_HEADER", "first column must be exactly Elapsed (s)"
                )
            if len(header) < 2:
                raise ValidationFailure("CSV_NO_CHANNELS", "CSV has no Audio channel columns")
            channel_numbers: list[int] = []
            for item in header[1:]:
                match = CHANNEL_PATTERN.fullmatch(item)
                if match is None:
                    raise ValidationFailure(
                        "CSV_CHANNEL_HEADER", f"invalid Audio channel header: {item!r}"
                    )
                channel_numbers.append(int(match.group(1)))
            expected_numbers = list(range(1, len(channel_numbers) + 1))
            if channel_numbers != expected_numbers:
                raise ValidationFailure(
                    "CSV_CHANNEL_IDENTITY",
                    f"Audio channels must be unique and contiguous: expected {expected_numbers}, "
                    f"got {channel_numbers}",
                )

            for row_number, row in enumerate(reader, start=2):
                if row == header:
                    raise ValidationFailure(
                        "CSV_REPEATED_HEADER", f"header repeated at row {row_number}"
                    )
                if len(row) != len(header):
                    raise ValidationFailure(
                        "CSV_FIELD_COUNT",
                        f"row {row_number} has {len(row)} fields; expected {len(header)}",
                    )
                timestamp = _finite_float(row[0], row=row_number, column="Elapsed (s)")
                if times:
                    if timestamp == times[-1]:
                        raise ValidationFailure(
                            "TIMESTAMP_DUPLICATE", f"row {row_number} duplicates its timestamp"
                        )
                    if timestamp < times[-1]:
                        raise ValidationFailure(
                            "TIMESTAMP_NON_MONOTONIC",
                            f"row {row_number} moves backwards in host reference time",
                        )
                raw_values: list[float] = []
                decoded_values: list[float] = []
                for column, text in zip(header[1:], row[1:], strict=True):
                    raw, decoded = _decode_sample(
                        text, representation, row=row_number, column=column
                    )
                    raw_values.append(raw)
                    decoded_values.append(decoded)
                times.append(timestamp)
                raw_rows.append(raw_values)
                decoded_rows.append(decoded_values)
    except UnicodeError as error:
        raise ValidationFailure("CSV_INVALID_UTF8", f"CSV is not valid UTF-8: {error}") from error

    if len(times) < 2:
        raise ValidationFailure("CSV_TOO_FEW_ROWS", "CSV requires at least two sample rows")
    assert np is not None
    return Capture(
        times_s=np.asarray(times, dtype=np.float64),
        raw_samples=np.asarray(raw_rows, dtype=np.float64),
        samples=np.asarray(decoded_rows, dtype=np.float64),
        headers=tuple(header[1:]),
        representation=representation,
    )


def read_reference(path: Path) -> tuple[Any, int, str]:
    assert sf is not None and np is not None
    try:
        samples, sample_rate = sf.read(path, dtype="float64", always_2d=True)
        info = sf.info(path)
    except (OSError, RuntimeError) as error:
        raise ValidationFailure("REFERENCE_UNREADABLE", f"cannot decode reference audio: {error}") from error
    if samples.shape[0] < 2 or samples.shape[1] < 1:
        raise ValidationFailure("REFERENCE_TOO_SHORT", "reference audio is empty or too short")
    if not np.isfinite(samples).all():
        raise ValidationFailure("REFERENCE_NONFINITE", "reference audio contains non-finite samples")
    return samples, int(sample_rate), str(info.subtype)


def percentile(values: Any, q: float) -> float:
    assert np is not None
    return float(np.percentile(values, q))


def timing_metrics(times_s: Any, expected_rate_hz: float) -> dict[str, Any]:
    assert np is not None
    deltas = np.diff(times_s)
    duration = float(times_s[-1] - times_s[0])
    measured_rate = float((len(times_s) - 1) / duration)
    ideal_delta = 1.0 / expected_rate_hz
    multiples = deltas / ideal_delta
    estimated_missing = int(np.maximum(np.rint(multiples).astype(np.int64) - 1, 0).sum())
    delta_error_us = (deltas - ideal_delta) * 1_000_000.0
    return {
        "authority": TIME_AUTHORITY,
        "sample_count": int(len(times_s)),
        "duration_s": duration,
        "expected_rate_hz": float(expected_rate_hz),
        "measured_rate_hz": measured_rate,
        "rate_error_ppm": (measured_rate / expected_rate_hz - 1.0) * 1_000_000.0,
        "timestamp_delta_us": {
            "minimum": float(deltas.min() * 1_000_000.0),
            "p50": percentile(deltas * 1_000_000.0, 50),
            "p95": percentile(deltas * 1_000_000.0, 95),
            "p99": percentile(deltas * 1_000_000.0, 99),
            "maximum": float(deltas.max() * 1_000_000.0),
            "absolute_error_p99": percentile(np.abs(delta_error_us), 99),
        },
        "estimated_missing_samples": estimated_missing,
        "gap_count_over_1_5_periods": int(np.count_nonzero(multiples > 1.5)),
    }


def channel_metrics(raw: Any, samples: Any, representation: str) -> list[dict[str, Any]]:
    assert np is not None
    contract = FORMAT_CONTRACTS[representation]
    output: list[dict[str, Any]] = []
    for channel in range(samples.shape[1]):
        native = raw[:, channel]
        values = samples[:, channel]
        minimum = contract["minimum"]
        maximum = contract["maximum"]
        clipped = 0
        if minimum is not None:
            clipped = int(np.count_nonzero((native == minimum) | (native == maximum)))
        output.append(
            {
                "channel": channel + 1,
                "native_minimum": float(native.min()),
                "native_maximum": float(native.max()),
                "minimum": float(values.min()),
                "maximum": float(values.max()),
                "peak": float(np.max(np.abs(values))),
                "rms": float(np.sqrt(np.mean(np.square(values)))),
                "dc_offset": float(np.mean(values)),
                "clipped_samples": clipped,
            }
        )
    return output


def _overlap(reference: Any, capture: Any, lag: int) -> tuple[Any, Any]:
    """Return reference/capture views for lag = capture delayed by lag samples."""

    if lag >= 0:
        count = min(len(reference), len(capture) - lag)
        return reference[: max(0, count)], capture[lag : lag + max(0, count)]
    shift = -lag
    count = min(len(reference) - shift, len(capture))
    return reference[shift : shift + max(0, count)], capture[: max(0, count)]


def _signed_correlation(left: Any, right: Any) -> float | None:
    assert np is not None
    if len(left) < 2 or len(right) < 2:
        return None
    left_centred = left - np.mean(left)
    right_centred = right - np.mean(right)
    denominator = float(np.linalg.norm(left_centred) * np.linalg.norm(right_centred))
    if denominator == 0:
        return None
    return float(np.dot(left_centred, right_centred) / denominator)


def best_global_lag(reference: Any, capture: Any, max_lag_samples: int) -> tuple[int, float | None]:
    assert np is not None and signal is not None
    channel_count = min(reference.shape[1], capture.shape[1])
    correlation_magnitude = None
    lags = None
    for channel in range(channel_count):
        ref_centred = reference[:, channel] - np.mean(reference[:, channel])
        cap_centred = capture[:, channel] - np.mean(capture[:, channel])
        correlation = signal.correlate(cap_centred, ref_centred, mode="full", method="fft")
        if lags is None:
            lags = signal.correlation_lags(len(cap_centred), len(ref_centred), mode="full")
            correlation_magnitude = np.zeros_like(correlation, dtype=np.float64)
        assert correlation_magnitude is not None
        correlation_magnitude += np.abs(correlation)
    assert lags is not None and correlation_magnitude is not None
    selected = np.abs(lags) <= max_lag_samples
    if not np.any(selected):
        return 0, None
    local = correlation_magnitude[selected]
    local_lags = lags[selected]
    lag = int(local_lags[int(np.argmax(local))])
    signed: list[float] = []
    for channel in range(channel_count):
        ref_view, cap_view = _overlap(reference[:, channel], capture[:, channel], lag)
        value = _signed_correlation(ref_view, cap_view)
        if value is not None:
            signed.append(value)
    return lag, float(np.mean(signed)) if signed else None


def _best_assignment(scores: Any) -> list[tuple[int, int]]:
    """Deterministic signed-correlation assignment without hidden abs()."""

    channels = min(scores.shape)
    if channels > 8:
        raise ValidationFailure(
            "CHANNEL_COUNT_UNSUPPORTED", "channel assignment is limited to eight channels"
        )
    best: tuple[float, tuple[int, ...]] | None = None
    for permutation in itertools.permutations(range(scores.shape[1]), channels):
        score = sum(float(scores[row, permutation[row]]) for row in range(channels))
        candidate = (score, permutation)
        if best is None or candidate > best:
            best = candidate
    assert best is not None
    return [(row, best[1][row]) for row in range(channels)]


def alignment_metrics(
    reference: Any, capture: Any, sample_rate_hz: int, max_lag_s: float
) -> dict[str, Any]:
    assert np is not None
    max_lag_samples = max(0, int(round(max_lag_s * sample_rate_hz)))
    lag, global_correlation = best_global_lag(reference, capture, max_lag_samples)
    pair_scores = np.full((reference.shape[1], capture.shape[1]), -1.0, dtype=np.float64)
    for reference_channel in range(reference.shape[1]):
        for capture_channel in range(capture.shape[1]):
            ref_view, cap_view = _overlap(
                reference[:, reference_channel], capture[:, capture_channel], lag
            )
            pair_scores[reference_channel, capture_channel] = (
                _signed_correlation(ref_view, cap_view) or -1.0
            )

    assignment = _best_assignment(pair_scores)
    identity_polarity: list[bool] = []
    for channel in range(min(reference.shape[1], capture.shape[1])):
        ref_identity, cap_identity = _overlap(
            reference[:, channel], capture[:, channel], lag
        )
        denominator = float(np.dot(ref_identity, ref_identity))
        identity_gain = (
            float(np.dot(ref_identity, cap_identity) / denominator) if denominator else None
        )
        identity_polarity.append(identity_gain is not None and identity_gain >= 0)
    channels: list[dict[str, Any]] = []
    for reference_channel, capture_channel in assignment:
        ref_view, cap_view = _overlap(
            reference[:, reference_channel], capture[:, capture_channel], lag
        )
        if len(ref_view) < 2:
            raise ValidationFailure("ALIGNMENT_NO_OVERLAP", "alignment produces no sample overlap")
        denominator = float(np.dot(ref_view, ref_view))
        gain = float(np.dot(ref_view, cap_view) / denominator) if denominator else None
        residual = cap_view - ref_view
        residual_rms = float(np.sqrt(np.mean(np.square(residual))))
        reference_rms = float(np.sqrt(np.mean(np.square(ref_view))))
        reference_dc = float(np.mean(ref_view))
        capture_dc = float(np.mean(cap_view))
        snr_db = (
            20.0 * math.log10(reference_rms / residual_rms)
            if reference_rms > 0 and residual_rms > 0
            else None
        )
        gain_error_db = (
            20.0 * math.log10(abs(gain)) if gain is not None and gain != 0 else None
        )
        channels.append(
            {
                "reference_channel": reference_channel + 1,
                "capture_channel": capture_channel + 1,
                "signed_correlation": _signed_correlation(ref_view, cap_view),
                "polarity_inverted": gain is not None and gain < 0,
                "gain": gain,
                "gain_error_db": gain_error_db,
                "reference_dc_offset": reference_dc,
                "capture_dc_offset": capture_dc,
                "dc_offset_error": capture_dc - reference_dc,
                "residual_rms": residual_rms,
                "snr_db": snr_db,
                "overlap_samples": int(len(ref_view)),
            }
        )
    return {
        "lag_samples": lag,
        "lag_ms": lag / sample_rate_hz * 1000.0,
        "search_limit_samples": max_lag_samples,
        "global_signed_correlation": global_correlation,
        "channel_identity_match": all(
            reference_channel == capture_channel
            for reference_channel, capture_channel in assignment
        ),
        "positive_polarity": all(identity_polarity),
        "channel_assignment": channels,
    }


def drift_metrics(
    reference: Any, capture: Any, sample_rate_hz: int, lag: int, *, windows: int = 8
) -> dict[str, Any]:
    """Estimate relative drift from windowed local lags; diagnostic, not clock authority."""

    assert np is not None
    ref_mono = np.mean(reference, axis=1)
    cap_mono = np.mean(capture, axis=1)
    usable = min(len(ref_mono), len(cap_mono))
    window_size = usable // windows
    if window_size < 256:
        return {"status": "INSUFFICIENT_DATA", "drift_ppm": None, "window_lags": []}
    search = max(2, int(round(sample_rate_hz * 0.01)))
    centres: list[float] = []
    lags: list[float] = []
    for window in range(windows):
        start = window * window_size
        stop = start + window_size
        reference_window = ref_mono[start:stop]
        capture_start = start + lag
        if capture_start < 0 or capture_start + window_size > len(cap_mono):
            continue
        capture_window = cap_mono[capture_start : capture_start + window_size]
        local_lag, correlation = best_global_lag(
            reference_window[:, None], capture_window[:, None], search
        )
        if correlation is None:
            continue
        centres.append((start + window_size / 2) / sample_rate_hz)
        lags.append(float(lag + local_lag))
    if len(lags) < 3:
        return {"status": "INSUFFICIENT_DATA", "drift_ppm": None, "window_lags": lags}
    slope_samples_per_second, _ = np.polyfit(np.asarray(centres), np.asarray(lags), 1)
    return {
        "status": "MEASURED_DIAGNOSTIC",
        "drift_ppm": float(slope_samples_per_second / sample_rate_hz * 1_000_000.0),
        "window_lags": lags,
    }


def tone_metrics(samples: Any, sample_rate_hz: int, tone_hz: float) -> list[dict[str, Any]]:
    assert np is not None
    if not (0 < tone_hz < sample_rate_hz / 2):
        raise ValidationFailure("TONE_FREQUENCY_INVALID", "tone must be below Nyquist")
    output: list[dict[str, Any]] = []
    for channel in range(samples.shape[1]):
        values = samples[:, channel] - np.mean(samples[:, channel])
        window = np.hanning(len(values))
        spectrum = np.fft.rfft(values * window)
        frequencies = np.fft.rfftfreq(len(values), 1.0 / sample_rate_hz)
        power = np.abs(spectrum) ** 2
        fundamental = int(np.argmin(np.abs(frequencies - tone_hz)))
        fundamental_power = float(power[fundamental])
        harmonic_power = 0.0
        harmonic_bins: list[int] = []
        harmonic = 2
        while harmonic * tone_hz < sample_rate_hz / 2:
            index = int(np.argmin(np.abs(frequencies - harmonic * tone_hz)))
            harmonic_bins.append(index)
            harmonic_power += float(power[index])
            harmonic += 1
        excluded = {0, fundamental, *harmonic_bins}
        noise_power = float(sum(value for index, value in enumerate(power) if index not in excluded))
        output.append(
            {
                "channel": channel + 1,
                "requested_hz": tone_hz,
                "detected_bin_hz": float(frequencies[fundamental]),
                "thd_ratio": math.sqrt(harmonic_power / fundamental_power)
                if fundamental_power > 0
                else None,
                "thd_plus_n_ratio": math.sqrt((harmonic_power + noise_power) / fundamental_power)
                if fundamental_power > 0
                else None,
            }
        )
    return output


def load_profile(path: Path | None) -> tuple[dict[str, Any] | None, str | None]:
    if path is None:
        return None, None
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValidationFailure("PROFILE_UNREADABLE", f"cannot read scoring profile: {error}") from error
    if not isinstance(profile, dict) or profile.get("schema") != PROFILE_SCHEMA:
        raise ValidationFailure("PROFILE_SCHEMA", f"profile schema must be {PROFILE_SCHEMA}")
    if not isinstance(profile.get("profile_id"), str) or not profile["profile_id"]:
        raise ValidationFailure("PROFILE_ID", "profile_id is required")
    thresholds = profile.get("thresholds")
    if not isinstance(thresholds, dict) or not thresholds:
        raise ValidationFailure("PROFILE_THRESHOLDS", "profile requires explicit thresholds")
    return profile, sha256_file(path)


def score(receipt: dict[str, Any], profile: dict[str, Any] | None, profile_sha: str | None) -> None:
    if profile is None:
        receipt["score"] = {
            "status": "NOT_SCORED",
            "profile_id": None,
            "profile_sha256": None,
            "checks": [],
        }
        return

    timing = receipt["timing"]
    alignment = receipt["alignment"]
    drift = receipt["drift"]
    channels = alignment["channel_assignment"]
    thresholds = profile["thresholds"]
    checks: list[dict[str, Any]] = []

    def check(
        name: str,
        actual: float | int | bool | None,
        limit: float | int | bool,
        relation: str,
    ) -> None:
        passed = False
        if actual is not None:
            if relation == "abs_lte":
                passed = abs(float(actual)) <= float(limit)
            elif relation == "lte":
                passed = float(actual) <= float(limit)
            elif relation == "gte":
                passed = float(actual) >= float(limit)
            elif relation == "eq":
                passed = actual == limit
            else:  # pragma: no cover - internal invariant
                raise AssertionError(relation)
        checks.append(
            {"name": name, "actual": actual, "relation": relation, "limit": limit, "pass": passed}
        )

    mapping: dict[str, tuple[Any, str]] = {
        "max_abs_rate_error_ppm": (timing["rate_error_ppm"], "abs_lte"),
        "max_timestamp_error_p99_us": (
            timing["timestamp_delta_us"]["absolute_error_p99"],
            "lte",
        ),
        "max_missing_samples": (timing["estimated_missing_samples"], "lte"),
        "max_abs_lag_ms": (alignment["lag_ms"], "abs_lte"),
        "max_abs_drift_ppm": (drift.get("drift_ppm"), "abs_lte"),
        "min_signed_correlation": (
            min(
                (item["signed_correlation"] for item in channels if item["signed_correlation"] is not None),
                default=None,
            ),
            "gte",
        ),
        "max_abs_gain_error_db": (
            max(
                (abs(item["gain_error_db"]) for item in channels if item["gain_error_db"] is not None),
                default=None,
            ),
            "lte",
        ),
        "max_residual_rms": (
            max((item["residual_rms"] for item in channels), default=None),
            "lte",
        ),
        "max_abs_dc_offset_error": (
            max(
                (abs(item["dc_offset_error"]) for item in channels),
                default=None,
            ),
            "lte",
        ),
        "max_interchannel_gain_error_db": (
            (
                max(item["gain_error_db"] for item in channels if item["gain_error_db"] is not None)
                - min(item["gain_error_db"] for item in channels if item["gain_error_db"] is not None)
            )
            if sum(item["gain_error_db"] is not None for item in channels) >= 2
            else 0.0,
            "lte",
        ),
        "max_clipped_samples_per_channel": (
            max((item["clipped_samples"] for item in receipt["capture"]["channels"]), default=None),
            "lte",
        ),
    }
    for threshold_name, limit in thresholds.items():
        if threshold_name not in mapping:
            raise ValidationFailure(
                "PROFILE_THRESHOLD_UNKNOWN", f"unknown threshold: {threshold_name}"
            )
        actual, relation = mapping[threshold_name]
        check(threshold_name, actual, limit, relation)
    requirements = profile.get("requirements") or {}
    if not isinstance(requirements, dict):
        raise ValidationFailure("PROFILE_REQUIREMENTS", "profile requirements must be an object")
    requirement_mapping: dict[str, Any] = {
        "channel_identity_match": alignment["channel_identity_match"],
        "positive_polarity": alignment["positive_polarity"],
        "exact_sample_count": (
            receipt["timing"]["sample_count"] == receipt["reference"]["sample_count"]
        ),
    }
    for requirement_name, required in requirements.items():
        if requirement_name not in requirement_mapping or required is not True:
            raise ValidationFailure(
                "PROFILE_REQUIREMENT_UNKNOWN",
                f"unknown or non-true requirement: {requirement_name}",
            )
        check(requirement_name, requirement_mapping[requirement_name], True, "eq")
    receipt["score"] = {
        "status": "PASS" if all(item["pass"] for item in checks) else "FAIL",
        "profile_id": profile["profile_id"],
        "profile_sha256": profile_sha,
        "checks": checks,
    }


def validate(
    csv_path: Path,
    reference_path: Path,
    representation: str,
    *,
    expected_rate_hz: float | None = None,
    max_lag_s: float = 1.0,
    profile_path: Path | None = None,
    tone_hz: float | None = None,
) -> dict[str, Any]:
    if DEPENDENCY_ERROR is not None:
        raise ValidationFailure(
            "DEPENDENCY_MISSING",
            f"managed environment is missing {DEPENDENCY_ERROR.name}; no installation was attempted",
        )
    capture = read_serial_studio_csv(csv_path, representation)
    reference, reference_rate_hz, reference_subtype = read_reference(reference_path)
    rate_hz = float(expected_rate_hz or reference_rate_hz)
    if expected_rate_hz is not None and not math.isclose(
        expected_rate_hz, reference_rate_hz, rel_tol=0.0, abs_tol=1e-9
    ):
        raise ValidationFailure(
            "REFERENCE_RATE_MISMATCH",
            f"reference WAV is {reference_rate_hz} Hz, expected {expected_rate_hz:g} Hz",
        )
    if capture.samples.shape[1] != reference.shape[1]:
        raise ValidationFailure(
            "CHANNEL_COUNT_MISMATCH",
            f"capture has {capture.samples.shape[1]} channels; reference has {reference.shape[1]}",
        )
    profile, profile_sha = load_profile(profile_path)
    timing = timing_metrics(capture.times_s, rate_hz)
    alignment = alignment_metrics(reference, capture.samples, int(round(rate_hz)), max_lag_s)
    drift = drift_metrics(
        reference,
        capture.samples,
        int(round(rate_hz)),
        int(alignment["lag_samples"]),
    )
    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "tool": {"id": TOOL_ID, "version": TOOL_VERSION},
        "integrity_status": "VALID",
        "authority": "HOST_AUDIO_REFERENCE",
        "time_authority": TIME_AUTHORITY,
        "capture": {
            "path": str(csv_path),
            "sha256": sha256_file(csv_path),
            "bytes": csv_path.stat().st_size,
            "representation": representation,
            "channel_count": int(capture.samples.shape[1]),
            "channels": channel_metrics(capture.raw_samples, capture.samples, representation),
        },
        "reference": {
            "path": str(reference_path),
            "sha256": sha256_file(reference_path),
            "bytes": reference_path.stat().st_size,
            "sample_rate_hz": reference_rate_hz,
            "sample_count": int(reference.shape[0]),
            "channel_count": int(reference.shape[1]),
            "subtype": reference_subtype,
        },
        "transform_policy": {
            "format_inferred": False,
            "normalisation_applied": False,
            "dc_removed": False,
            "dither_applied": False,
            "clipping_applied": False,
            "malformed_rows_skipped": 0,
            "declared_pcm_affine_decode_only": representation not in {"float32_normalized", "float32_native"},
        },
        "timing": timing,
        "alignment": alignment,
        "drift": drift,
        "tone": tone_metrics(capture.samples, int(round(rate_hz)), tone_hz)
        if tone_hz is not None
        else None,
        "reason_codes": [],
        "claims": {
            "host_audio_reference_measured": True,
            "k1_capture_pipeline_validated": False,
            "acoustic_delivery_validated": False,
            "device_time_alignment_validated": False,
            "product_verdict": False,
        },
        "non_claims": [
            "Serial Studio Elapsed (s) is host audio reference time, not K1 device time.",
            "This receipt does not prove speaker output, room acoustics, microphone capture, PDM, or K1 PCM fidelity.",
            "A score is meaningful only when bound to the named scoring profile in this receipt.",
        ],
    }
    score(receipt, profile, profile_sha)
    return receipt


def invalid_receipt(failure: ValidationFailure) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "tool": {"id": TOOL_ID, "version": TOOL_VERSION},
        "integrity_status": "INVALID",
        "authority": "HOST_AUDIO_REFERENCE",
        "time_authority": TIME_AUTHORITY,
        "score": {
            "status": "INVALID",
            "profile_id": None,
            "profile_sha256": None,
            "checks": [],
        },
        "reason_codes": [failure.code],
        "error": failure.message,
        "claims": {
            "host_audio_reference_measured": False,
            "k1_capture_pipeline_validated": False,
            "acoustic_delivery_validated": False,
            "device_time_alignment_validated": False,
            "product_verdict": False,
        },
    }


def serialise(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("capture_csv", type=Path)
    parser.add_argument("reference_wav", type=Path)
    parser.add_argument("--representation", required=True, choices=sorted(FORMAT_CONTRACTS))
    parser.add_argument("--expected-rate-hz", type=float)
    parser.add_argument("--max-lag-s", type=float, default=1.0)
    parser.add_argument("--scoring-profile", type=Path)
    parser.add_argument("--tone-hz", type=float)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    try:
        if args.max_lag_s < 0:
            raise ValidationFailure("LAG_LIMIT_INVALID", "max-lag-s must be non-negative")
        receipt = validate(
            args.capture_csv,
            args.reference_wav,
            args.representation,
            expected_rate_hz=args.expected_rate_hz,
            max_lag_s=args.max_lag_s,
            profile_path=args.scoring_profile,
            tone_hz=args.tone_hz,
        )
        status = 0 if receipt["score"]["status"] != "FAIL" else 2
    except ValidationFailure as failure:
        receipt = invalid_receipt(failure)
        status = 1

    payload = serialise(receipt)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    sys.stdout.buffer.write(payload)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
