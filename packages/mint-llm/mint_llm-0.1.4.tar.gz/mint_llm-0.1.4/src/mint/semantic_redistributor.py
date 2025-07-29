from __future__ import annotations

from safetensors.torch import load_file
import torch
from transformers.generation.logits_process import LogitsProcessor


class MintProcessor(LogitsProcessor):
    """Apply semantic redistribution during generation."""

    def __init__(self, weights: str, alpha: float = 0.0) -> None:
        data = load_file(weights)
        self.W = data["W"]
        self.alpha = float(alpha)

    def __call__(self, _input_ids: torch.Tensor, scores: torch.Tensor) -> torch.Tensor:
        logits = scores
        W = self.W.to(logits.device, logits.dtype)
        common = torch.result_type(logits, W)
        logits = logits.to(common)
        W = W.to(common)
        lp_raw = (logits @ W) @ W.T - logits
        denom = (
            lp_raw.abs()
            .amax(dim=-1, keepdim=True)
            .clamp_min(torch.finfo(logits.dtype).eps)
        )
        scale = logits.abs().amax(dim=-1, keepdim=True) / denom
        minted = lp_raw * scale
        out = self.alpha * logits + (1 - self.alpha) * minted
        return out.to(scores.dtype)
