from typer.testing import CliRunner
import os
import pytest

import torch
from safetensors.torch import save_file, load_file

from mint.cli import app


def test_cli_blend_writes_W(tmp_path):
    runner = CliRunner()
    emb = torch.eye(3)
    emb_file = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    out_dir = tmp_path / "out"
    result = runner.invoke(app, ["blend", str(emb_file), str(out_dir), "--rank", "2"])
    assert result.exit_code == 0
    W = load_file(str(out_dir / "W.safetensors"))["W"]
    assert W.shape == (3, 2)


def test_cli_blend_cpu_option(monkeypatch, tmp_path):
    runner = CliRunner()
    emb = torch.eye(2)
    emb_file = tmp_path / "emb_cpu.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    out_dir = tmp_path / "sim_cpu"
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    result = runner.invoke(
        app,
        ["blend", str(emb_file), str(out_dir), "--rank", "1", "--cpu"],
    )
    assert result.exit_code == 0
    assert "Chose device cpu" in result.stdout
    W = load_file(str(out_dir / "W.safetensors"))["W"]
    assert W.shape == (2, 1)


def test_cli_blend_creates_subdirs(tmp_path):
    runner = CliRunner()
    emb = torch.eye(2)
    emb_file = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    out_dir = tmp_path / "nested"
    result = runner.invoke(app, ["blend", str(emb_file), str(out_dir), "--rank", "2"])
    assert result.exit_code == 0
    assert (out_dir / "W.safetensors").exists()
    W = load_file(str(out_dir / "W.safetensors"))["W"]
    assert W.shape == (2, 2)


def test_cli_blend_vulkan(tmp_path):
    if os.environ.get("GITHUB_ACTIONS") == "true":
        pytest.skip("vulkan unsupported on github")
    if (
        not hasattr(torch.backends, "vulkan")
        or not torch.backends.vulkan.is_available()
    ):
        pytest.skip("vulkan backend not available")

    runner = CliRunner()
    emb = torch.eye(2)
    emb_file = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    result = runner.invoke(
        app,
        ["blend", str(emb_file), str(tmp_path), "--rank", "1", "--sdk", "vulkan"],
    )
    assert result.exit_code == 0
    assert "Chose device vulkan" in result.stdout
    W = load_file(str(tmp_path / "W.safetensors"))["W"]
    assert W.shape == (2, 1)


def test_cli_blend_zluda_error(tmp_path):
    runner = CliRunner()
    emb = torch.eye(2)
    emb_file = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    result = runner.invoke(
        app,
        ["blend", str(emb_file), str(tmp_path), "--rank", "1", "--sdk", "zluda"],
    )
    assert result.exit_code != 0
    assert "Unknown backend: zluda" in result.output


def test_cli_blend_rocm_error(tmp_path):
    runner = CliRunner()
    emb = torch.eye(2)
    emb_file = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    result = runner.invoke(
        app,
        ["blend", str(emb_file), str(tmp_path), "--rank", "1", "--sdk", "rocm"],
    )
    assert result.exit_code != 0
    assert "Unknown backend: rocm" in result.output


def test_cli_blend_metal_error(tmp_path):
    runner = CliRunner()
    emb = torch.eye(2)
    emb_file = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    result = runner.invoke(
        app,
        ["blend", str(emb_file), str(tmp_path), "--rank", "1", "--sdk", "metal"],
    )
    assert result.exit_code != 0
    assert "Unknown backend: metal" in result.output


def test_cli_blend_fast(monkeypatch, tmp_path):
    runner = CliRunner()
    emb = torch.eye(2)
    emb_file = tmp_path / "emb_fast.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    called: dict[str, tuple] = {}

    def fake_build(src, dest, *, rank, keep_residual, device, dry_run):
        called["args"] = (src, dest, rank, keep_residual, device, dry_run)

    monkeypatch.setattr("mint.cli.build_low_rank_isvd_fast", fake_build)

    out_dir = tmp_path / "fast"
    result = runner.invoke(
        app,
        ["blend", str(emb_file), str(out_dir), "--rank", "1", "--fast", "--cpu"],
    )

    assert result.exit_code == 0
    assert called["args"] == (
        str(emb_file),
        str(out_dir),
        1,
        False,
        torch.device("cpu"),
        False,
    )
