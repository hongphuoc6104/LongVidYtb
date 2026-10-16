"""Reproducible original procedural sounds; no third-party recordings."""
from __future__ import annotations

import math
import struct
import wave
from pathlib import Path


def build(folder: Path) -> None:
    """Write mono PCM16/48 kHz source assets with deterministic sample values."""
    from audio_processing import synthesize_micro_sfx
    folder.mkdir(parents=True, exist_ok=True)
    sounds = {'pop_clean': 'pop', 'whoosh_soft': 'whoosh', 'page_flip': 'pencil_stroke',
              'pen_highlight': 'pencil_stroke', 'clock_tick': 'pop', 'ding_insight': 'soft_riser'}
    for name, kind in sounds.items():
        samples = synthesize_micro_sfx(kind, duration_sec=.3, amplitude=.1)
        with wave.open(str(folder / (name + '.wav')), 'wb') as handle:
            handle.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
            handle.writeframes(struct.pack(f'<{len(samples)}h', *samples))
    samples = [round(4500 * sum(math.sin(2 * math.pi * frequency * i / 48000) for frequency in (110, 165, 220)) / 3) for i in range(480000)]
    with wave.open(str(folder / 'ambient_focus_loop.wav'), 'wb') as handle:
        handle.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
        handle.writeframes(struct.pack(f'<{len(samples)}h', *samples))


if __name__ == '__main__':
    build(Path(__file__).resolve().parents[1] / 'assets/sfx')
