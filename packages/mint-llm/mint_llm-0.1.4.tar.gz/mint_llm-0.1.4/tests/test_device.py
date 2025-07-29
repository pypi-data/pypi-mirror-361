import pytest
from typer import BadParameter
import torch
import types

from mint.device import select_device


def test_select_cuda(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    d = select_device(False, None, None)
    assert d == torch.device("cuda:0")


def test_select_cuda_with_index(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    d = select_device(False, 2, "cuda")
    assert d == torch.device("cuda:2")


def test_select_cuda_unavailable(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    d = select_device(False, None, "cuda")
    assert d == torch.device("cpu")


def test_select_force_cpu(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    d = select_device(True, None, None)
    assert d == torch.device("cpu")


def test_select_vulkan(monkeypatch):
    vulkan = types.SimpleNamespace(is_available=lambda: True)
    monkeypatch.setattr(torch.backends, "vulkan", vulkan, raising=False)
    d = select_device(False, None, "vulkan")
    assert d == torch.device("vulkan")


def test_select_vulkan_unavailable(monkeypatch):
    vulkan = types.SimpleNamespace(is_available=lambda: False)
    monkeypatch.setattr(torch.backends, "vulkan", vulkan, raising=False)
    d = select_device(False, None, "vulkan")
    assert d == torch.device("cpu")


def test_select_unknown_sdk():
    with pytest.raises(BadParameter):
        select_device(False, None, "unknown")
