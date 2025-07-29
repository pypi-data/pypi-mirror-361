import pytest
import torch
from safetensors.torch import save_file

from mint.similarity import load_embeddings


def test_load_embeddings_success(tmp_path):
    emb = torch.eye(3)
    path = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(path))
    loaded = load_embeddings(str(path), torch.device("cpu"))
    assert torch.equal(loaded, emb)


def test_load_embeddings_missing_key(tmp_path):
    path = tmp_path / "emb.safetensors"
    save_file({"wrong": torch.zeros(1)}, str(path))
    with pytest.raises(KeyError):
        load_embeddings(str(path), torch.device("cpu"))


def test_load_embeddings_device_transfer(monkeypatch, tmp_path):
    emb = torch.eye(2)
    path = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(path))

    called: dict[str, torch.device] = {}

    def fake_load_file(p):
        class Dummy:
            def to(self, device):
                called["device"] = device
                return emb.to(device)

        return {"embedding": Dummy()}

    monkeypatch.setattr("mint.similarity.load_file", fake_load_file)

    device = torch.device("cpu")
    result = load_embeddings(str(path), device)
    assert called["device"] == device
    assert torch.equal(result, emb)
