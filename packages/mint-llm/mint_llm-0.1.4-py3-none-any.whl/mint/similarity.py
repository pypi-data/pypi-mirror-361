from __future__ import annotations

from pathlib import Path
from typing import Optional

from safetensors.torch import load_file, save_file
import torch  # type: ignore

from . import brand_svd


def load_embeddings(path: str | Path, device: torch.device) -> torch.Tensor:
    state = load_file(str(Path(path)))
    if "embedding" not in state:
        raise KeyError("expected key `embedding`")
    return state["embedding"].to(device)


def build_low_rank_isvd(
    embeddings: str | Path | torch.Tensor,
    output_dir: str | Path,
    *,
    rank: int = 1024,
    keep_residual: bool = False,
    device: str | torch.device = "cpu",
    dry_run: bool = False,
) -> Optional[torch.Tensor]:
    """Construct a low-rank similarity factor using streaming isvd."""

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    w_path = out_dir / "W.safetensors"

    dev = torch.device(device)
    E = (
        load_embeddings(embeddings, dev)
        if isinstance(embeddings, (str, Path))
        else embeddings.to(dev)
    )

    n, d = E.shape
    original_type = E.dtype
    promoted_type = torch.promote_types(original_type, torch.float32)
    E = E.to(promoted_type)
    bytes_per = torch.finfo(promoted_type).bits // 8
    w_bytes = n * rank * bytes_per
    if dry_run:
        print(
            f"[mint·dry-run] n={n:,}  d={d}  r={rank}  "
            f"• est W size {w_bytes / 1024 ** 2:.1f} MiB"
        )
        return None
    qsr = brand_svd.run_isvd_cosine_sim(
        E, max_rank=rank, dtype=promoted_type, device=dev, progress=True
    )
    W = brand_svd.build_final_w_matrix(
        qsr,
        final_ops=brand_svd.FinalOperations.ColWhiten
        | brand_svd.FinalOperations.RowNorm,
    ).to(original_type)
    save_file({"W": W.cpu()}, str(w_path))

    if keep_residual:
        Q, S, R = qsr
        r_path = out_dir / "R.safetensors"
        save_file({"Q": Q.cpu(), "S": S.cpu(), "R": R.cpu()}, str(r_path))

    print(
        f"[mint] build complete → {w_path}"
        + (" & R.safetensors" if keep_residual else "")
    )
    return W.cpu()


def build_low_rank_isvd_fast(
    embeddings: str | Path | torch.Tensor,
    output_dir: str | Path,
    *,
    rank: int = 1024,
    keep_residual: bool = False,
    device: str | torch.device = "cpu",
    dry_run: bool = False,
) -> Optional[torch.Tensor]:
    """Construct a low-rank similarity factor using streaming isvd."""

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    w_path = out_dir / "W.safetensors"

    dev = torch.device(device)
    E = (
        load_embeddings(embeddings, dev)
        if isinstance(embeddings, (str, Path))
        else embeddings.to(dev)
    )

    n, d = E.shape
    original_type = E.dtype
    promoted_type = torch.promote_types(original_type, torch.float32)
    E = E.to(promoted_type)
    bytes_per = torch.finfo(promoted_type).bits // 8
    w_bytes = n * rank * bytes_per
    if dry_run:
        print(
            f"[mint·dry-run] n={n:,}  d={d}  r={rank}  "
            f"• est W size {w_bytes / 1024 ** 2:.1f} MiB"
        )
        return None
    qsr = brand_svd.run_isvd(
        E, max_rank=rank, dtype=promoted_type, device=dev, progress=True
    )
    W = brand_svd.build_final_w_matrix(
        qsr,
        final_ops=brand_svd.FinalOperations.Fast
        | brand_svd.FinalOperations.ColWhiten
        | brand_svd.FinalOperations.RowNorm,
    ).to(original_type)
    save_file({"W": W.cpu()}, str(w_path))

    if keep_residual:
        Q, S, R = qsr
        r_path = out_dir / "R.safetensors"
        save_file({"Q": Q.cpu(), "S": S.cpu(), "R": R.cpu()}, str(r_path))

    print(
        f"[mint] build complete → {w_path}"
        + (" & R.safetensors" if keep_residual else "")
    )
    return W.cpu()
