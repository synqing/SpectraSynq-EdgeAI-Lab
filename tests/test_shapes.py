import torch

from edgeai.config import LabConfig
from edgeai.frontend import LogMelFrontend
from edgeai.semantic_v0 import SemanticV0, count_parameters


def test_frontend_and_model_shapes():
    lab = LabConfig()
    fe = LogMelFrontend(lab.frontend)
    pcm = torch.randn(2, lab.frontend.n_samples)
    logmel = fe(pcm)
    assert tuple(logmel.shape) == (2, 1, lab.frontend.n_mels, lab.frontend.n_frames)
    model = SemanticV0(lab.model)
    logits = model(logmel)
    assert tuple(logits.shape) == (2, 3)
    n = count_parameters(model)
    assert 50_000 < n < 500_000
