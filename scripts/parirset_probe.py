#!/usr/bin/env python3
"""P4: CLEAN vs PA/ROOM on real DEAM audio using held-out PaRIRset RIRs.

HOST-ONLY. Does not ingest CrowdioSet. Does not train.
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import numpy as np

from edgeai.mir.conventional import extract as extract_conventional
from edgeai.mir.deam import audio_path, load_arousal
from edgeai.mir.live_domain import (
    PARIRSET_HF,
    convolve_rir,
    load_rir_wav,
    venue_from_parirset_name,
)
from edgeai.mir.semantic_trace import write_trace

CACHE = Path("datasets/parirset/test")
OUT = Path("artifacts/parirset_probe")
HF_API = "https://huggingface.co/api/datasets/enricguso/parirset/tree/main/test"
SONG_IDS = (2030, 2034, 2041)
N_VENUES = 3


def _pearson(a: np.ndarray, b: np.ndarray) -> float:
    if a.size < 8 or a.std() < 1e-8 or b.std() < 1e-8:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def _list_test_files() -> list[str]:
    paths: list[str] = []
    url = HF_API
    while url:
        req = urllib.request.Request(url, headers={"User-Agent": "SpectraSynq-EdgeAI-Lab"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode())
            link = resp.headers.get("Link", "")
        batch = payload if isinstance(payload, list) else payload.get("tree", payload)
        for row in batch:
            p = row.get("path", "")
            if p.endswith("_test.wav"):
                paths.append(Path(p).name)
        url = None
        if 'rel="next"' in link:
            for part in link.split(","):
                if 'rel="next"' in part:
                    url = part.split(";")[0].strip().strip("<>")
    return paths


def _pick_one_per_venue(names: list[str], n: int) -> list[str]:
    seen: dict[str, str] = {}
    for name in names:
        venue = venue_from_parirset_name(name)
        if venue not in seen:
            seen[venue] = name
        if len(seen) >= n:
            break
    return list(seen.values())


def _download(name: str) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    dest = CACHE / name
    if dest.is_file() and dest.stat().st_size > 1000:
        return dest
    url = f"{PARIRSET_HF}/test/{name}"
    urllib.request.urlretrieve(url, dest)
    return dest


def _load_mono(path: Path, sr: int = 16_000) -> np.ndarray:
    import librosa

    y, _ = librosa.load(str(path), sr=sr, mono=True)
    return y.astype(np.float32)


def _align(conv: dict, t_gt: np.ndarray) -> dict[str, np.ndarray]:
    t = conv["times"]
    keys = ("rms", "onset_env", "spectral_flux", "novelty", "band_low", "band_mid", "band_high")
    return {k: np.interp(t_gt, t, conv[k]).astype(np.float32) for k in keys}


def main() -> int:
    names = _list_test_files()
    if not names:
        print("no PaRIRset test listing")
        return 2
    picks = _pick_one_per_venue(names, N_VENUES)
    rirs = []
    for name in picks:
        path = _download(name)
        rir = load_rir_wav(path, sr=16_000)
        rirs.append(
            {
                "file": name,
                "venue": venue_from_parirset_name(name),
                "split": "test",
                "n_samples": int(rir.size),
                "rir": rir,
            }
        )
        print(f"rir {name} venue={venue_from_parirset_name(name)} n={rir.size}", flush=True)

    arousal = load_arousal()
    OUT.mkdir(parents=True, exist_ok=True)
    traces = OUT / "traces"
    traces.mkdir(exist_ok=True)
    rows = []
    for sid in SONG_IDS:
        try:
            wav = audio_path(sid)
        except FileNotFoundError:
            continue
        if sid not in arousal:
            continue
        t_gt, a_gt = arousal[sid]
        clean = _load_mono(wav)
        clean_f = _align(extract_conventional(clean, sr=16_000), t_gt)
        for r in rirs:
            wet = convolve_rir(clean, r["rir"], mix=1.0)
            wet_f = _align(extract_conventional(wet, sr=16_000), t_gt)
            rec = {
                "song_id": sid,
                "venue": r["venue"],
                "rir_file": r["file"],
                "split": "test",
                "r_clean_rms_vs_wet_rms": _pearson(clean_f["rms"], wet_f["rms"]),
                "r_human_arousal_vs_clean_rms": _pearson(a_gt, clean_f["rms"]),
                "r_human_arousal_vs_wet_rms": _pearson(a_gt, wet_f["rms"]),
                "r_clean_flux_vs_wet_flux": _pearson(clean_f["spectral_flux"], wet_f["spectral_flux"]),
                "r_clean_onset_vs_wet_onset": _pearson(clean_f["onset_env"], wet_f["onset_env"]),
                "label": "HOST-ONLY",
                "domain": "PA_ROOM",
            }
            print(json.dumps({k: v for k, v in rec.items() if k != "label"}), flush=True)
            rows.append(rec)
            frames = [
                {
                    "t": float(t_gt[i]),
                    "arousal": float(a_gt[i]),
                    "rms_clean": float(clean_f["rms"][i]),
                    "rms_wet": float(wet_f["rms"][i]),
                }
                for i in range(len(t_gt))
            ]
            write_trace(
                traces / f"deam_{sid}_{r['venue']}.jsonl",
                audio=str(wav),
                provenance=["deam_human_arousal_2Hz", "parirset_test", r["file"]],
                frames=frames,
                extra_header={"song_id": sid, "venue": r["venue"], "split": "test"},
            )

    receipt = {
        "label": "HOST-ONLY",
        "dataset": "PaRIRset test split + DEAM",
        "licence": "PaRIRset CC0; DEAM research/UNKNOWN commercial",
        "held_out_venues_intact": True,
        "crowdioset_ingested": False,
        "n_comparisons": len(rows),
        "rows": rows,
    }
    (OUT / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"wrote {OUT / 'receipt.json'}")
    return 0 if rows else 2


if __name__ == "__main__":
    raise SystemExit(main())
