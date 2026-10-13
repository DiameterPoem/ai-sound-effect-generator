"""Render pipeline — normalizes, limits, and writes any plugin output."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from sfxgen.contracts.plugin import AudioBuffer


@dataclass(slots=True)
class PostChain:
    peak_db: float = -1.0
    fade_ms: float = 8.0
    dc_block: bool = True

    def apply(self, buffer: AudioBuffer, sample_rate: int) -> AudioBuffer:
        out = buffer.astype(np.float32, copy=True)
        if self.dc_block:
            out = out - out.mean(axis=1, keepdims=True)
        fade = max(1, int(sample_rate * self.fade_ms / 1000.0))
        ramp = np.linspace(0.0, 1.0, fade, dtype=np.float32)
        out[:, :fade] *= ramp
        out[:, -fade:] *= ramp[::-1]
        peak = float(np.max(np.abs(out)) or 1.0)
        target = 10 ** (self.peak_db / 20.0)
        if peak > target:
            out *= target / peak
        return out
</｜｜DSML｜｜ parameter>
</｜｜DSML｜｜ invoke>
</｜｜DSML｜｜ calls>