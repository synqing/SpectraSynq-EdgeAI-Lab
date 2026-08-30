from pathlib import Path

from edgeai.mir.semantic_trace import read_trace, write_trace


def test_semantic_trace_roundtrip(tmp_path: Path):
    p = tmp_path / "t.jsonl"
    write_trace(
        p,
        audio="x.wav",
        provenance=["deam_human_arousal_2Hz"],
        frames=[{"t": 15.0, "arousal": 0.2, "rms": 0.1}, {"t": 15.5, "arousal": 0.3}],
    )
    header, frames = read_trace(p)
    assert header["schema"] == "spectrasynq.semantic_trace.v1"
    assert frames[0]["t"] == 15.0
    assert "arousal" in frames[0]


def test_live_convolve_length():
    import numpy as np

    from edgeai.mir.live_domain import convolve_rir, synthetic_room_ir

    pcm = np.zeros(16000, dtype=np.float32)
    pcm[100] = 1.0
    y = convolve_rir(pcm, synthetic_room_ir(16000), mix=1.0)
    assert y.shape == pcm.shape
    assert np.max(np.abs(y)) > 0
