#!/usr/bin/env python3
"""P3: source-activity teacher signal vs mixture energy. HOST-ONLY.

Default teacher is HPSS (deterministic). HT-Demucs runs only if installed.
No separator training. No U55.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from edgeai.mir.deam import audio_path, load_arousal
from edgeai.mir.semantic_trace import write_trace
from edgeai.mir.teachers import (
    activity_envelope,
    envelope_vs_mixture,
    hpss_stems,
    try_demucs,
)

OUT = Path("artifacts/source_activity")
SONG_IDS = (2030, 2034, 2041)
SR = 16_000
EXCERPT_S = 45.0


def _load(path: Path, sr: int = SR) -> np.ndarray:
    import librosa

    y, _ = librosa.load(str(path), sr=sr, mono=True, duration=EXCERPT_S)
    return y.astype(np.float32)


def _pearson(a: np.ndarray, b: np.ndarray) -> float:
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    if n < 8 or a.std() < 1e-8 or b.std() < 1e-8:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def _interp_to(t_src, y, t_dst):
    return np.interp(t_dst, t_src, y).astype(np.float32)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    traces = OUT / "traces"
    traces.mkdir(exist_ok=True)
    demucs = try_demucs()
    arousal = load_arousal()
    rows = []
    for sid in SONG_IDS:
        try:
            wav = audio_path(sid)
        except FileNotFoundError:
            continue
        pcm = _load(wav)
        stems = hpss_stems(pcm, SR)
        stats = envelope_vs_mixture(stems, SR)
        rec = {
            "song_id": sid,
            "teacher": "hpss",
            "excerpt_s": EXCERPT_S,
            **stats,
            "demucs_available": demucs is not None,
        }
        t_p, e_p = activity_envelope(stems["percussive"], SR)
        t_h, e_h = activity_envelope(stems["harmonic"], SR)
        t_m, e_m = activity_envelope(stems["mixture"], SR)
        if sid in arousal:
            t_gt, a_gt = arousal[sid]
            rec["r_human_arousal_vs_perc"] = _pearson(a_gt, _interp_to(t_p, e_p, t_gt))
            rec["r_human_arousal_vs_harm"] = _pearson(a_gt, _interp_to(t_h, e_h, t_gt))
            rec["r_human_arousal_vs_mix"] = _pearson(a_gt, _interp_to(t_m, e_m, t_gt))
        if demucs is not None:
            try:
                sep = demucs.separate(pcm, SR)
                sep["mixture"] = pcm
                rec["demucs"] = envelope_vs_mixture(sep, SR)
            except Exception as exc:  # pragma: no cover
                rec["demucs_error"] = str(exc)
        print(json.dumps(rec), flush=True)
        rows.append(rec)
        n = min(len(t_m), len(t_p), len(t_h))
        frames = [
            {
                "t": float(t_m[i]),
                "rms": float(e_m[i]),
                "percussive": float(e_p[i]),
                "harmonic": float(e_h[i]),
            }
            for i in range(n)
        ]
        write_trace(
            traces / f"hpss_{sid}.jsonl",
            audio=str(wav),
            provenance=["librosa.effects.hpss", "activity_envelope"],
            frames=frames,
            extra_header={"song_id": sid, "teacher": "hpss"},
        )

    (OUT / "receipt.json").write_text(
        json.dumps(
            {
                "label": "HOST-ONLY",
                "note": "Teacher signal is envelopes, not SDR. HPSS is the always-on baseline. Demucs only if installed.",
                "demucs_installed": demucs is not None,
                "songs": rows,
            },
            indent=2,
        )
        + "\n"
    )
    return 0 if rows else 2


if __name__ == "__main__":
    raise SystemExit(main())
