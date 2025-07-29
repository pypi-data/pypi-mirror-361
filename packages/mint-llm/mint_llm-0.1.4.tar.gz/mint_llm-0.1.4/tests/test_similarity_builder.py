import sys
from pathlib import Path

import torch
from safetensors.torch import save_file, load_file

from mint.similarity import build_low_rank_isvd, build_low_rank_isvd_fast


def _write_eye(path: Path, size: int) -> None:
    emb = torch.eye(size, dtype=torch.get_default_dtype())
    save_file({"embedding": emb}, str(path))


def test_build_creates_w_and_residual(tmp_path):
    emb_file = tmp_path / "emb.safetensors"
    _write_eye(emb_file, 4)

    out_dir = tmp_path / "sim"
    print(f"emb_file {emb_file}")
    build_low_rank_isvd(str(emb_file), out_dir, rank=2, keep_residual=True)

    W = load_file(str(out_dir / "W.safetensors"))["W"]
    QSR = load_file(str(out_dir / "R.safetensors"))

    assert W.shape == (4, 2)
    assert QSR["Q"].shape == (4, 2)
    assert QSR["S"].shape == (2, 2)
    assert QSR["R"].shape == (4, 2)
    assert torch.all(QSR["S"].diagonal().abs() > 1e-4)
    assert torch.all(QSR["Q"] == QSR["R"])


def test_build_dry_run(tmp_path):
    old_dtype = torch.get_default_dtype()
    torch.set_default_dtype(torch.float64)
    emb_file = tmp_path / "emb.safetensors"
    _write_eye(emb_file, 3)

    out_dir = tmp_path / "sim"
    build_low_rank_isvd(str(emb_file), out_dir, rank=1, dry_run=True)

    assert not (out_dir / "W.safetensors").exists()
    assert not (out_dir / "R.safetensors").exists()
    torch.set_default_dtype(old_dtype)


def test_build_uses_tqdm_when_tty(monkeypatch, tmp_path):
    calls: list[bool] = []

    def fake_tqdm(iterable):
        calls.append(True)
        return iterable

    monkeypatch.setattr(sys.stderr, "isatty", lambda: True)
    monkeypatch.setattr("mint.brand_svd.tqdm", fake_tqdm)

    old_dtype = torch.get_default_dtype()
    torch.set_default_dtype(torch.float64)
    emb_file = tmp_path / "emb.safetensors"
    _write_eye(emb_file, 3)

    out_dir = tmp_path / "sim"
    build_low_rank_isvd(str(emb_file), out_dir, rank=1)
    torch.set_default_dtype(old_dtype)

    assert calls


def test_build_no_tqdm_without_tty(monkeypatch, tmp_path):
    calls: list[bool] = []

    def fake_tqdm(iterable):
        calls.append(True)
        return iterable

    monkeypatch.setattr(sys.stderr, "isatty", lambda: False)
    monkeypatch.setattr("mint.brand_svd.tqdm", fake_tqdm)

    old_dtype = torch.get_default_dtype()
    torch.set_default_dtype(torch.float64)
    emb_file = tmp_path / "emb.safetensors"
    _write_eye(emb_file, 3)

    out_dir = tmp_path / "sim"
    build_low_rank_isvd(str(emb_file), out_dir, rank=1)
    torch.set_default_dtype(old_dtype)

    assert not calls


def test_build_fast_creates_w(tmp_path):
    emb_file = tmp_path / "emb_fast.safetensors"
    _write_eye(emb_file, 4)

    out_dir = tmp_path / "fast"
    build_low_rank_isvd_fast(str(emb_file), out_dir, rank=2)

    W = load_file(str(out_dir / "W.safetensors"))["W"]
    assert W.shape == (4, 2)


def test_build_fast_dry_run(tmp_path):
    old_dtype = torch.get_default_dtype()
    torch.set_default_dtype(torch.float64)
    emb_file = tmp_path / "emb_fast.safetensors"
    _write_eye(emb_file, 3)

    out_dir = tmp_path / "fast"
    build_low_rank_isvd_fast(str(emb_file), out_dir, rank=1, dry_run=True)

    assert not (out_dir / "W.safetensors").exists()
    assert not (out_dir / "R.safetensors").exists()
    torch.set_default_dtype(old_dtype)
