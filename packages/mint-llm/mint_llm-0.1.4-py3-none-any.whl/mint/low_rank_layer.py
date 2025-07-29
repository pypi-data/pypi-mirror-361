from __future__ import annotations

from torch import nn, Tensor
import torch
from typing import NamedTuple, Optional, Tuple, Type
from enum import StrEnum, unique
from dataclasses import dataclass

from .utils import skip_outside_pytest


@skip_outside_pytest()
def debug_print(*args, **kwargs):
    print(*args, **kwargs)


class LowRankRedistributor(nn.Module):
    @unique
    class Modes(StrEnum):
        Lerp = "Linearly blend minted and original logits"
        LogitScale = "Scale blend by original logit magnitude"
        MintScale = "Scale blend by minted logit magnitude"
        TopK = "Replace top-k logits with minted logits"
        TopP = "Replace top a% of token probabilities with minted logits"
        MinP = "Replace top token probabilities based on (max * a) with minted logits"
        PromoteOnly = "TODO: Mint may only increase the score of original logits"
        DemoteOnly = "TODO: Mint may only decrease the score of original logits"
        # While all blend modes are still experimental, the below modes are more
        # experimental than most.
        # ==================================================================================
        # TopK, TopP, and MinP samplers currently mask logits and replace those masked logits with MINT's scores.
        # This could reinforce some of the selected logits, demote others, or leave some unchanged. However, it
        # doesn't allow those logits' "gained" or "lost" 'energy' to transfer to other tokens. Perhaps we could do
        # something more dynamic here? Perhaps we could mask the original logits, and run MINT with the others
        # as zeros, then, then do the inverse? Replace all the masked tokens with the non-masked spread and
        # Spread the masked tokens's contribution to the unmasked ones? Will need more consideration.
        MuddleTopK = "TODO: cross-influence masked by TopK where we zero out self-contribution from masked tokens"
        MuddleTopP = "TODO: cross-influence masked by TopP where we zero out self-contribution from masked tokens"
        MuddleMinP = "TODO: cross-influence masked by MinP where we zero out self-contribution from masked tokens"
        NoConfidence = "TODO: Rework this nonsense description: 'drop out all logit influence where both logits & mint are low-scoring, then re-norm'"

    # Presets are a stub for now - revisit this later
    @dataclass(frozen=True)
    class Presets(dict):
        class Preset(NamedTuple):
            mode: LowRankRedistributor.Modes
            alpha: float

        Basic: Preset
        Grimm: Preset
        Stable: Preset
        Surreal: Preset

    def __init__(
        self,
        W: Tensor,
        /,
        mode: Modes = Modes.Lerp,
        alpha: float = 0.0,
        device: Optional[torch.device] = None,
    ):
        # Presets are a stub for now - revisit this later
        self._presets = self.Presets(
            Basic=self.Presets.Preset(self.Modes.Lerp, 0.4),
            Grimm=self.Presets.Preset(self.Modes.MintScale, 0.4),
            Stable=self.Presets.Preset(self.Modes.LogitScale, 0.3),
            Surreal=self.Presets.Preset(self.Modes.MintScale, 0.35),
        )

        print = debug_print
        super().__init__()
        print("==================================")
        print("Low Rank Redistributor Initialized")
        print("==================================")
        print(f"- Alpha:    \t{alpha}")
        print(f"- Operation:\t{mode.name}")
        print(f"- Device:   \t{device}")
        print(f"- W.shape:  \t{W.shape}")
        print(f"- W.dtype:  \t{W.dtype}")
        print("==================================")
        # register as buffer so it moves with the module
        self.W: Tensor
        self.register_buffer("W", W)
        self.mode = mode
        self.alpha = alpha
        self._w_type_checked = False
        if device is not None:
            self.to(device)

    def forward(self, _token_ids: Tensor, logits: Tensor) -> Tensor:
        print = debug_print
        Modes: Type = LowRankRedistributor.Modes
        # Figure out the higher‐precision dtype for this call
        return_type = logits.dtype
        common_dtype = torch.result_type(logits, self.W)

        # 1) Upcast logits if needed, track for casting back
        cast_logits = logits.dtype != common_dtype
        if cast_logits:
            logits = logits.to(common_dtype)

        # 2) Upcast W once if it’s lower precision
        elif not self._w_type_checked:
            if self.W.dtype != common_dtype:
                # replace the buffer in-place so future calls skip this
                self.W = self.W.to(common_dtype)
                self.type(common_dtype)
            self._w_type_checked = True

        # 3) Do your low-rank smoothing + demotion
        print(f"Alpha           :\t{self.alpha}")
        print(f"Original Logits :\n\t{logits}")
        print(f"Pre-mint |max|  :\t{logits.abs().max():.4}")

        def _mint_logits(logits: Tensor) -> Tensor:
            return (logits @ self.W) @ self.W.T

        def _normalize(A: Tensor) -> Tuple[Tensor, float]:
            A_n = float(A.norm())
            return A / A_n, A_n

        def _rescale_A_to_B_norm(A: Tensor, B_n: float) -> Tensor:
            return (A / float(A.norm())) * B_n

        def _rescaled_mint_no_cast(
            logits: Tensor,
            cross_exclude_mask: Optional[Tensor] = None,
            /,
            *,
            W: Tensor = self.W,
            remove_basis: bool = True,
        ) -> Tensor:
            """
            Pure-bf16 interface; relies on matmul’s fp32 accumulator.
            Guarantees  max|L'| ≤ max|L|.
            """
            # ---------- 1.  Do the raw Gram product  -----------------
            # v2 =  Eᵀ · L      (bf16 -> internal fp32 accumulator -> bf16)
            # v2 = logits @ W
            # L′_raw =  (E · v2) (same kernel rules)
            # Lp_raw = v2 @ W.T  # bf16 result, still un-scaled

            Lp_raw: Tensor
            # Cross-logits-mask is for if we're doing cross-masking between 2
            # sets, ignores 'remove_bases' as this would be redundant
            if cross_exclude_mask is not None:
                # Lp_A is the full contribution of all non-masked tokens on all tokens
                # Lp_B is the contributon of the masked tokens onto only unmasked tokens
                Lp_A = ((logits * (~cross_exclude_mask)) @ W) @ W.T
                Lp_B = (((logits * cross_exclude_mask) @ W) @ W.T) * (
                    ~cross_exclude_mask
                )
                mask_blend = float(
                    cross_exclude_mask.sum() / cross_exclude_mask.numel()
                )
                # TODO: Scale Lp_A and B based on the number of zero'd tokens to
                # make their overall values congruent
                Lp_raw = (Lp_A * (1 - mask_blend)) + (Lp_B * mask_blend)
            else:
                # Option - remove the original contribution
                Lp_raw = (
                    ((logits @ W) @ W.T) - logits
                    if remove_basis
                    else (logits @ W) @ W.T
                )

            print(f"Minted pre-scale:\n\t{Lp_raw.abs().max()}")

            # ---------- 2.  Rescale so the headline range matches L --
            scale = logits.abs().max() / Lp_raw.abs().max().clamp_min(
                torch.finfo(logits.dtype).eps
            )  # avoid x/0.0
            return Lp_raw * scale

        def _top_p_cutoff_indices(logits: Tensor, alpha: float = self.alpha) -> Tensor:
            sf = torch.softmax(logits, 1).view(-1)
            end = sf.numel()
            prev, cutoff = 1, max(1, end // 4)
            topp_idx: Tensor

            # binary-search on k, but trim overshoot via cumsum instead of a Python loop
            while True:
                topp_v, topp_idx = sf.topk(cutoff)  # top-cutoff probs & their indices
                if cutoff == prev:
                    break
                if topp_v.sum() > self.alpha:
                    # vectorized trim: return all idx where cum is <= a
                    cums = topp_v.cumsum(dim=0)
                    over = (cums.less_equal(self.alpha)).nonzero(as_tuple=False)
                    cutoff = max(1, over.numel())
                    topp_idx = topp_idx[:cutoff]
                    break
                # still under α → adjust low/high and continue
                prev, cutoff = cutoff, (cutoff + end) // 2
            return topp_idx

        match self.mode:
            case Modes.Lerp:
                minted = _rescaled_mint_no_cast(logits)
                logits = torch.lerp(minted, logits, self.alpha)

            case Modes.LogitScale:
                minted = _rescaled_mint_no_cast(logits)
                l_scale = torch.softmax(logits, 1)
                print(f"LogitScale |max|:\n\t{l_scale.max()}")
                logits = torch.lerp(minted, logits, (1 - l_scale) * self.alpha)

            case Modes.MintScale:
                minted = _rescaled_mint_no_cast(logits)
                m_scale = torch.softmax(minted, 1)
                print(f"MintScale |max|:\n\t{m_scale.max()}")
                logits = torch.lerp(minted, logits, (1 - m_scale) * self.alpha)

            case Modes.TopK:
                _, topk_idx = logits.topk(round(self.alpha))
                minted = _rescaled_mint_no_cast(logits)
                logits[0, topk_idx].copy_(minted[0, topk_idx])

            case Modes.TopP:
                topp_idx = _top_p_cutoff_indices(logits)
                minted = _rescaled_mint_no_cast(logits)
                logits[0, topp_idx] = minted[0, topp_idx]

            case Modes.MinP:
                sf = torch.softmax(logits, 1)
                minted = _rescaled_mint_no_cast(logits)
                mask = sf.greater(sf.max() * self.alpha)
                logits = (~mask * logits) + (mask * minted)

            case Modes.PromoteOnly:
                minted = _rescaled_mint_no_cast(logits)
                mask = minted.greater(logits)
                logits = torch.lerp(minted, logits, 1 - (mask * self.alpha))

            case Modes.DemoteOnly:
                minted = _rescaled_mint_no_cast(logits)
                mask = logits.greater(minted)
                logits = torch.lerp(minted, logits, 1 - (mask * self.alpha))

            case Modes.MuddleTopK:
                _, topk_idx = logits.topk(round(self.alpha))
                mask = torch.zeros_like(logits, dtype=torch.bool, device=logits.device)
                mask[0, topk_idx] = torch.ones_like(
                    topk_idx, dtype=torch.bool, device=logits.device
                )
                logits = _rescaled_mint_no_cast(logits, mask)

            case Modes.MuddleTopP:
                topp_idx = _top_p_cutoff_indices(logits)
                mask = torch.zeros_like(logits, dtype=torch.bool, device=logits.device)
                mask[0, topp_idx] = torch.ones_like(
                    topp_idx, dtype=torch.bool, device=logits.device
                )
                logits = _rescaled_mint_no_cast(logits, mask)

            case Modes.MuddleMinP:
                sf = torch.softmax(logits, 1)
                mask = sf.greater(sf.max() * self.alpha)
                logits = _rescaled_mint_no_cast(logits, mask)

            case _:
                raise Exception(f"Mode not implemented (TODO): {self.mode}")

        print(f"Post mint |max| :\t{logits.abs().max():.4}")
        print(f"MINTED Logits   :\n\t{logits}")
        print("===============================================================")

        # 4) Cast result back to original dtype if we upcasted logits
        if cast_logits:
            return logits.to(return_type)

        return logits
