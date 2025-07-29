from __future__ import annotations

import torch
import typer


def select_device(cpu: bool, gpu: int | None, sdk: str | None) -> torch.device:
    """Choose a computation device.

    Parameters
    ----------
    cpu:
        Force CPU usage when ``True``.
    gpu:
        Optional CUDA device index used when ``sdk`` is ``"cuda"``.
    sdk:
        Name of the acceleration backend. ``None`` defaults to ``"cuda"``.

    Returns
    -------
    ``torch.device`` describing the selected backend.

    ``BadParameter`` is raised for unknown ``sdk`` values.
    """
    if cpu:
        return torch.device("cpu")

    backend = "cuda" if sdk is None else sdk.lower()
    if backend == "cuda":
        if torch.cuda.is_available():
            idx = 0 if gpu is None else gpu
            return torch.device(f"cuda:{idx}")
        return torch.device("cpu")

    if backend == "vulkan":
        vulkan = getattr(torch.backends, "vulkan", None)
        if vulkan is not None and vulkan.is_available():
            return torch.device("vulkan")
        return torch.device("cpu")

    raise typer.BadParameter(f"Unknown backend: {sdk}")
