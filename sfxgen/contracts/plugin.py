"""The plugin contract. Everything the host promises and everything it requires."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

import numpy as np
from numpy.typing import NDArray

AudioBuffer = NDArray[np.float32]  # shape: (channels, samples), dtype float32


@dataclass(frozen=True, slots=True)
class PluginManifest:
    id: str
    name: str
    version: str
    author: str
    description: str
    api_version: str = "1"
    requires_gpu: bool = False
    tags: tuple[str, ...] = ()


@dataclass(slots=True)
class RenderRequest:
    prompt: str
    duration: float
    sample_rate: int = 48_000
    channels: int = 2
    seed: int = -1

    def __post_init__(self) -> None:
        if self.duration <= 0 or self.duration > 600:
            raise ValueError(f"duration out of range: {self.duration}")
        if self.sample_rate not in (22_050, 44_100, 48_000, 96_000):
            raise ValueError(f"unsupported sample rate: {self.sample_rate}")


@dataclass(slots=True)
class RenderResult:
    buffer: AudioBuffer
    sample_rate: int
    plugin_id: str
    elapsed_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PluginContext:
    """Everything a plugin is allowed to touch. No globals, no direct IO."""

    cache_dir: Path
    device: str  # "cuda", "cpu", "directml"
    logger: Any
    rng: np.random.Generator


class ProgressReporter(Protocol):
    def __call__(self, fraction: float, message: str = "") -> None: ...


class SfxPlugin(ABC):
    """Base class for every sound-effect plugin."""

    @abstractmethod
    def manifest(self) -> PluginManifest: ...

    @abstractmethod
    def render(self, request: RenderRequest, ctx: PluginContext) -> RenderResult: ...

    def warmup(self, ctx: PluginContext) -> None:
        """Optional: preload weights. Called once at host boot."""
        return None

    def teardown(self) -> None:
        """Optional: release VRAM / file handles."""
        return None