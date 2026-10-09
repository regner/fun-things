#!/usr/bin/env python
"""Generate deterministic, original placeholder audio for the S14 fixture."""

from __future__ import annotations

import math
import random
import struct
import wave
from collections.abc import Callable
from pathlib import Path

SAMPLE_RATE = 44_100
OUTPUT = Path(__file__).resolve().parent / "audio"


def _write(name: str, duration: float, sample: Callable[[int, float], float]) -> None:
    """Write one mono 16-bit PCM WAV from a bounded sample function."""
    frames = bytearray()
    frame_count = round(duration * SAMPLE_RATE)
    for index in range(frame_count):
        time_seconds = index / SAMPLE_RATE
        value = max(-1.0, min(1.0, sample(index, time_seconds)))
        frames.extend(struct.pack("<h", round(value * 32767.0)))

    OUTPUT.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUTPUT / name), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        output.writeframes(frames)


def _noise(seed: int) -> Callable[[], float]:
    """Return a deterministic bipolar noise source."""
    generator = random.Random(seed)
    return lambda: generator.uniform(-1.0, 1.0)


def _fade(time_seconds: float, duration: float, attack: float = 0.01) -> float:
    """Return a short attack and quadratic release envelope."""
    attack_level = min(1.0, time_seconds / attack)
    release_level = max(0.0, 1.0 - time_seconds / duration) ** 2
    return attack_level * release_level


def _generate() -> None:
    """Generate all fixture sounds without external samples."""
    engine_noise = _noise(1401)
    _write(
        "engine_loop.wav",
        3.0,
        lambda _index, time_seconds: 0.22
        * (
            math.sin(math.tau * 72.0 * time_seconds)
            + 0.45 * math.sin(math.tau * 144.0 * time_seconds)
            + 0.08 * engine_noise()
        ),
    )

    for variant, seed in enumerate((1411, 1421, 1431), start=1):
        burst_noise = _noise(seed)
        duration = 0.65 + variant * 0.04
        _write(
            f"explosion_{variant}.wav",
            duration,
            lambda _index, time_seconds, noise=burst_noise, length=duration, offset=variant: (
                0.72 * noise() + 0.28 * math.sin(math.tau * (58.0 + offset * 7.0) * time_seconds)
            )
            * _fade(time_seconds, length, 0.004),
        )

    for variant, seed in enumerate((1451, 1459), start=1):
        shot_noise = _noise(seed)
        duration = 0.11 + variant * 0.01
        _write(
            f"smg_{variant}.wav",
            duration,
            lambda _index, time_seconds, noise=shot_noise, length=duration, offset=variant: (
                0.65 * noise() + 0.35 * math.sin(math.tau * (190.0 + offset * 30.0) * time_seconds)
            )
            * _fade(time_seconds, length, 0.0015),
        )

    ambience_noise = _noise(1471)
    _write(
        "ambience.wav",
        3.0,
        lambda _index, time_seconds: 0.035
        * (ambience_noise() + math.sin(math.tau * 43.0 * time_seconds)),
    )
    _write(
        "music.wav",
        3.0,
        lambda _index, time_seconds: 0.08
        * (
            math.sin(math.tau * 110.0 * time_seconds)
            + 0.5 * math.sin(math.tau * 138.59 * time_seconds)
        ),
    )


if __name__ == "__main__":
    _generate()
