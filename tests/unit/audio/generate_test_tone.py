#!/usr/bin/env python3
"""Generate the deterministic placeholder tone used by audio policy tests."""

import math
from pathlib import Path
import struct
import wave

SAMPLE_RATE = 22_050
DURATION_SECONDS = 2
FREQUENCY_HZ = 440.0
AMPLITUDE = 0.05
OUTPUT = Path(__file__).with_name("audio") / "policy_test_tone.wav"


def main():
    """Write one mono 16-bit PCM sine tone with no external source material."""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUTPUT), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for sample_index in range(SAMPLE_RATE * DURATION_SECONDS):
            phase = 2.0 * math.pi * FREQUENCY_HZ * sample_index / SAMPLE_RATE
            value = round(math.sin(phase) * AMPLITUDE * 32767)
            frames.extend(struct.pack("<h", value))
        output.writeframes(frames)


if __name__ == "__main__":
    main()
