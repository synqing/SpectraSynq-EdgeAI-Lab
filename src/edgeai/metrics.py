"""Per-class activity metrics. Never report only a single aggregate number."""

from __future__ import annotations

from typing import Any

import numpy as np

from edgeai.config import CLASSES


def _safe_div(n: float, d: float) -> float:
    return float(n / d) if d else 0.0


def binary_f1(y_true: np.ndarray, y_pred: np.ndarray, thresh: float = 0.5) -> dict[str, float]:
    yt = y_true >= thresh
    yp = y_pred >= thresh
    tp = float(np.sum(yt & yp))
    fp = float(np.sum(~yt & yp))
    fn = float(np.sum(yt & ~yp))
    prec = _safe_div(tp, tp + fp)
    rec = _safe_div(tp, tp + fn)
    f1 = _safe_div(2 * prec * rec, prec + rec) if (prec + rec) else 0.0
    return {"precision": prec, "recall": rec, "f1": f1}


def per_class_report(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    thresh: float = 0.5,
) -> dict[str, Any]:
    """y_*: (N, 3) in [0, 1]."""
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)
    out: dict[str, Any] = {"n": int(y_true.shape[0]), "threshold": thresh, "classes": {}}
    maes = []
    f1s = []
    for i, name in enumerate(CLASSES):
        mae = float(np.mean(np.abs(y_true[:, i] - y_pred[:, i])))
        rmse = float(np.sqrt(np.mean((y_true[:, i] - y_pred[:, i]) ** 2)))
        f = binary_f1(y_true[:, i], y_pred[:, i], thresh)
        out["classes"][name] = {"mae": mae, "rmse": rmse, **f}
        maes.append(mae)
        f1s.append(f["f1"])
    out["macro_mae"] = float(np.mean(maes))
    out["macro_f1"] = float(np.mean(f1s))
    return out


def quantization_delta(fp32: dict[str, Any], int8: dict[str, Any]) -> dict[str, Any]:
    delta: dict[str, Any] = {"classes": {}}
    for name in CLASSES:
        a = fp32["classes"][name]
        b = int8["classes"][name]
        delta["classes"][name] = {
            "mae_delta": b["mae"] - a["mae"],
            "f1_delta": b["f1"] - a["f1"],
        }
    delta["macro_mae_delta"] = int8["macro_mae"] - fp32["macro_mae"]
    delta["macro_f1_delta"] = int8["macro_f1"] - fp32["macro_f1"]
    return delta
