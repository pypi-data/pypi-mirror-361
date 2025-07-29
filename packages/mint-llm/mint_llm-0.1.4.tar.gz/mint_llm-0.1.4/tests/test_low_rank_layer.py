import torch
import pytest

from mint.low_rank_layer import LowRankRedistributor

Modes = LowRankRedistributor.Modes


W = torch.tensor(
    [
        [1.0, 0.0],
        [0.0, 1.0],
        [1.0, 1.0],
        [0.0, 0.0],
    ],
    dtype=torch.float64,
)

LOGITS = torch.tensor([[1.0, 2.0, 3.0, 4.0]], dtype=torch.float64)


def _rescaled_mint(
    logits: torch.Tensor, mask: torch.Tensor | None = None
) -> torch.Tensor:
    if mask is not None:
        lp_a = ((logits * (~mask)) @ W) @ W.T
        lp_b = (((logits * mask) @ W) @ W.T) * (~mask)
        blend = float(mask.sum() / mask.numel())
        lp_raw = lp_a * (1 - blend) + lp_b * blend
    else:
        lp_raw = ((logits @ W) @ W.T) - logits
    scale = logits.abs().max() / lp_raw.abs().max().clamp_min(
        torch.finfo(logits.dtype).eps
    )
    return lp_raw * scale


def _top_p_cutoff_indices(logits: torch.Tensor, alpha: float) -> torch.Tensor:
    sf = torch.softmax(logits, 1).view(-1)
    end = sf.numel()
    prev, cutoff = 1, max(1, end // 4)
    while True:
        topp_v, topp_idx = sf.topk(cutoff)
        if cutoff == prev:
            break
        if topp_v.sum() > alpha:
            cums = topp_v.cumsum(0)
            over = (cums <= alpha).nonzero(as_tuple=False)
            cutoff = max(1, over.numel())
            topp_idx = topp_idx[:cutoff]
            break
        prev, cutoff = cutoff, (cutoff + end) // 2
    return topp_idx


def expected_output(mode: Modes, alpha: float) -> torch.Tensor:
    logits = LOGITS.clone()
    if mode is Modes.Lerp:
        minted = _rescaled_mint(logits)
        logits = torch.lerp(minted, logits, alpha)
    elif mode is Modes.LogitScale:
        minted = _rescaled_mint(logits)
        l_scale = torch.softmax(logits, 1)
        logits = torch.lerp(minted, logits, (1 - l_scale) * alpha)
    elif mode is Modes.MintScale:
        minted = _rescaled_mint(logits)
        m_scale = torch.softmax(minted, 1)
        logits = torch.lerp(minted, logits, (1 - m_scale) * alpha)
    elif mode is Modes.TopK:
        _rescaled_mint(logits)
        logits = logits
    elif mode is Modes.TopP:
        idx = _top_p_cutoff_indices(logits, alpha)
        minted = _rescaled_mint(logits)
        logits[0, idx] = minted[0, idx]
    elif mode is Modes.MinP:
        sf = torch.softmax(logits, 1)
        minted = _rescaled_mint(logits)
        mask = sf > sf.max() * alpha
        logits = (~mask) * logits + mask * minted
    elif mode is Modes.PromoteOnly:
        minted = _rescaled_mint(logits)
        mask = minted > logits
        logits = torch.lerp(minted, logits, 1 - (mask * alpha))
    elif mode is Modes.DemoteOnly:
        minted = _rescaled_mint(logits)
        mask = logits > minted
        logits = torch.lerp(minted, logits, 1 - (mask * alpha))
    elif mode is Modes.MuddleTopK:
        _, idx = logits.topk(round(alpha))
        mask = torch.zeros_like(logits, dtype=torch.bool)
        mask[0, idx] = True
        logits = _rescaled_mint(logits, mask)
    elif mode is Modes.MuddleTopP:
        idx = _top_p_cutoff_indices(logits, alpha)
        mask = torch.zeros_like(logits, dtype=torch.bool)
        mask[0, idx] = True
        logits = _rescaled_mint(logits, mask)
    elif mode is Modes.MuddleMinP:
        sf = torch.softmax(logits, 1)
        mask = sf > sf.max() * alpha
        logits = _rescaled_mint(logits, mask)
    else:
        raise AssertionError(mode)
    return logits


@pytest.mark.parametrize(
    "mode,alpha",
    [
        (Modes.Lerp, 0.5),
        (Modes.LogitScale, 0.5),
        (Modes.MintScale, 0.5),
        (Modes.TopK, 2.0),
        (Modes.TopP, 0.5),
        (Modes.MinP, 0.5),
        (Modes.PromoteOnly, 0.5),
        (Modes.DemoteOnly, 0.5),
        (Modes.MuddleTopK, 2.0),
        (Modes.MuddleTopP, 0.5),
        (Modes.MuddleMinP, 0.5),
    ],
)
def test_modes_outputs(mode: Modes, alpha: float) -> None:
    layer = LowRankRedistributor(W, mode=mode, alpha=alpha)
    out = layer(torch.zeros(1, dtype=torch.long), LOGITS.clone())
    expected = expected_output(mode, alpha)
    assert torch.allclose(out, expected)


def test_rescaling_and_cross_influence() -> None:
    mask = torch.tensor([[False, False, True, True]])
    nomask = _rescaled_mint(LOGITS)
    masked = _rescaled_mint(LOGITS, mask)
    assert torch.isclose(nomask.abs().max(), LOGITS.abs().max())
    assert torch.isclose(masked.abs().max(), LOGITS.abs().max())
    assert not torch.allclose(masked, nomask)
