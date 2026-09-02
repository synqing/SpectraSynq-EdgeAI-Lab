"""J3Q - tiny causal restraint policy head.

Not a chroma model, not transcription, not a frontend. It outputs one number
per frame, q(t) in [0,1], which scales C3 movement:

    M_J3Q(t) = C3_movement(t) * q(t)

Topology 53 -> 32 ReLU -> 1 sigmoid, 1761 trainable parameters, implemented
directly in NumPy so the committed code reproduces bit-for-bit with no deep
learning framework installed. The gradients are verified against finite
differences in the test suite.

Pre-registration: docs/mir/receipts/learned_restraint/J3Q_PREREGISTRATION.json
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

__all__ = ["FEATURE_BLOCKS", "N_FEATURES", "N_HIDDEN", "RECIPE", "TinyHead", "standardiser"]

FEATURE_BLOCKS = (
    ("c3_state_t", 12), ("c3_state_t_minus_lag", 12),
    ("p0_state_t", 12), ("p0_state_t_minus_lag", 12),
    ("c3_movement", 1), ("p0_movement", 1),
    ("spectral_flux", 1), ("onset_descriptor", 1), ("delta_log_rms", 1),
)
N_FEATURES = sum(d for _, d in FEATURE_BLOCKS)          # 53
N_HIDDEN = 32

RECIPE = {
    "loss": "balanced binary cross entropy",
    "class_weighting": "equal TOTAL positive and negative weight inside each training fold",
    "optimiser": "Adam",
    "learning_rate": 1e-3,
    "weight_decay": 1e-4,
    "weight_decay_form": "L2 added to the gradient (as torch.optim.Adam(weight_decay=...)), applied to weights only, NOT to biases",
    "batch_size": 4096,
    "epochs": 30,
    "beta1": 0.9, "beta2": 0.999, "eps": 1e-8,
    "seed": 20260902,
    "init": "He/Kaiming normal for the ReLU layer, Xavier/Glorot normal for the output layer, biases zero",
}


def standardiser(x_train: NDArray) -> tuple[NDArray, NDArray]:
    """Mean and standard deviation from TRAINING ROWS ONLY."""
    mu = np.asarray(x_train, dtype=np.float64).mean(axis=0)
    sd = np.asarray(x_train, dtype=np.float64).std(axis=0)
    sd[sd < 1e-9] = 1.0
    return mu, sd


def _sigmoid(z: NDArray) -> NDArray:
    out = np.empty_like(z)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out


class TinyHead:
    """53 -> N_HIDDEN ReLU -> 1 sigmoid. 1761 parameters at the frozen size."""

    def __init__(self, n_in: int = N_FEATURES, n_hidden: int = N_HIDDEN, *, seed: int = RECIPE["seed"]):
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0.0, np.sqrt(2.0 / n_in), size=(n_in, n_hidden))
        self.b1 = np.zeros(n_hidden)
        self.W2 = rng.normal(0.0, np.sqrt(1.0 / n_hidden), size=(n_hidden, 1))
        self.b2 = np.zeros(1)
        self._m = {k: np.zeros_like(v) for k, v in self.params.items()}
        self._v = {k: np.zeros_like(v) for k, v in self.params.items()}
        self._t = 0

    @property
    def params(self) -> dict[str, NDArray]:
        return {"W1": self.W1, "b1": self.b1, "W2": self.W2, "b2": self.b2}

    @property
    def n_parameters(self) -> int:
        return sum(v.size for v in self.params.values())

    def forward(self, x: NDArray) -> NDArray:
        h = np.maximum(x @ self.W1 + self.b1, 0.0)
        return _sigmoid((h @ self.W2 + self.b2).ravel())

    def _loss_and_grads(self, x: NDArray, y: NDArray, w: NDArray):
        a = x @ self.W1 + self.b1
        h = np.maximum(a, 0.0)
        z = (h @ self.W2 + self.b2).ravel()
        q = _sigmoid(z)
        eps = 1e-12
        wsum = w.sum() + eps
        loss = float(-(w * (y * np.log(q + eps) + (1 - y) * np.log(1 - q + eps))).sum() / wsum)
        dz = (w * (q - y) / wsum).reshape(-1, 1)
        gW2 = h.T @ dz
        gb2 = dz.sum(axis=0)
        dh = dz @ self.W2.T
        dh[a <= 0.0] = 0.0
        gW1 = x.T @ dh
        gb1 = dh.sum(axis=0)
        return loss, {"W1": gW1, "b1": gb1, "W2": gW2, "b2": gb2}

    def _adam_step(self, grads: dict[str, NDArray], lr: float, wd: float) -> None:
        b1, b2, eps = RECIPE["beta1"], RECIPE["beta2"], RECIPE["eps"]
        self._t += 1
        for k, p in self.params.items():
            g = grads[k]
            if k.startswith("W"):
                g = g + wd * p                       # L2, weights only
            self._m[k] = b1 * self._m[k] + (1 - b1) * g
            self._v[k] = b2 * self._v[k] + (1 - b2) * (g * g)
            mh = self._m[k] / (1 - b1 ** self._t)
            vh = self._v[k] / (1 - b2 ** self._t)
            p -= lr * mh / (np.sqrt(vh) + eps)

    def fit(self, x: NDArray, y: NDArray, *, seed: int = RECIPE["seed"]) -> dict:
        """The frozen recipe. No early stopping, no sweeps, no selection."""
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        n_pos, n_neg = float((y > 0.5).sum()), float((y <= 0.5).sum())
        if n_pos == 0 or n_neg == 0:
            raise ValueError("balanced BCE needs both classes present")
        w = np.where(y > 0.5, 1.0 / n_pos, 1.0 / n_neg)   # equal TOTAL weight per class
        rng = np.random.default_rng(seed)
        n, bs = x.shape[0], RECIPE["batch_size"]
        history = []
        for _ in range(RECIPE["epochs"]):
            order = rng.permutation(n)
            ep = 0.0
            for s in range(0, n, bs):
                idx = order[s:s + bs]
                if idx.size < 2:
                    continue
                loss, g = self._loss_and_grads(x[idx], y[idx], w[idx])
                self._adam_step(g, RECIPE["learning_rate"], RECIPE["weight_decay"])
                ep += loss * idx.size
            history.append(ep / n)
        return {"epochs": RECIPE["epochs"], "final_epoch_mean_loss": round(history[-1], 6),
                "first_epoch_mean_loss": round(history[0], 6), "n_train_rows": int(n),
                "n_positive": int(n_pos), "n_negative": int(n_neg)}
