import sys
from pathlib import Path

import torch

from mint import brand_svd


CACHE_DIR = Path(__file__).resolve().parents[1] / ".cache" / "mint"


def test_build_similarity_uses_tqdm(monkeypatch):
    calls: list[bool] = []

    def fake_tqdm(iterable):
        calls.append(True)
        return iterable

    monkeypatch.setattr(sys.stderr, "isatty", lambda: True)
    monkeypatch.setattr("mint.brand_svd.tqdm", fake_tqdm)

    emb = torch.eye(3, dtype=torch.get_default_dtype())
    brand_svd.run_isvd_cosine_sim(emb, dtype=emb.dtype, progress=True)

    assert calls
