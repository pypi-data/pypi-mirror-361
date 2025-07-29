import subprocess
import sys
from pathlib import Path

import pytest
import torch
from safetensors.torch import load_file, save_file

from mint.semantic_redistributor import MintProcessor


def ref_mint(logits: torch.Tensor, W: torch.Tensor, alpha: float) -> torch.Tensor:
    lp_raw = (logits @ W) @ W.T - logits
    denom = (
        lp_raw.abs().amax(dim=-1, keepdim=True).clamp_min(torch.finfo(logits.dtype).eps)
    )
    scale = logits.abs().amax(dim=-1, keepdim=True) / denom
    minted = lp_raw * scale
    return alpha * logits + (1 - alpha) * minted


def test_equiv(tmp_path):
    logits = torch.randn(2, 4)
    W = torch.randn(4, 2)
    W, _ = torch.linalg.qr(W)
    W = W.contiguous()
    path = tmp_path / "W.safetensors"
    save_file({"W": W}, str(path))
    proc = MintProcessor(str(path), alpha=0.3)
    out = proc(
        torch.ones_like(logits, dtype=logits.dtype, device=logits.device),
        logits.clone(),
    )
    expected = ref_mint(logits, W, 0.3)
    assert torch.allclose(out, expected, atol=1e-5)


def test_lora_shape(tmp_path):
    from transformers import GPT2Config, GPT2LMHeadModel

    config = GPT2Config(n_embd=4, n_layer=1, n_head=1, vocab_size=8)
    model = GPT2LMHeadModel(config)
    model_dir = tmp_path / "base"
    model.save_pretrained(model_dir)

    out = tmp_path / "out"
    subprocess.check_call(
        [
            sys.executable,
            str(
                Path(__file__).resolve().parents[1] / "scripts/export_redistributor.py"
            ),
            "--model",
            str(model_dir),
            "--rank",
            "2",
            "--out",
            str(out),
            "--gamma-calib",
            "1.0",
        ]
    )

    data = load_file(str(out.with_name(out.name + "_approx_lora.safetensors")))
    A = data["lm_head.lora_A.weight"]
    B = data["lm_head.lora_B.weight"]
    scale = data["lm_head.scaling"]

    assert A.shape == (2, config.n_embd)
    assert B.shape == (config.vocab_size, 2)
    assert A.dtype == torch.float16
    assert B.dtype == torch.float16
    assert scale.dtype == torch.float32 and scale.numel() == 1


@pytest.mark.skip(reason="Vulkan support currently under development.")
def test_merge_to_gguf():
    pytest.xfail("gguf tooling absent")
