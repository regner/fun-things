"""Author original periodic swell textures; no downloaded images or random noise."""
from pathlib import Path
import argparse

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
NID = "city_water_look_01"
SIZE = 512
TILE_METRES = 16.0


def texture_arrays():
    """Sample analytic periodic swells and their OpenGL tangent-space normals."""
    v, u = np.mgrid[0:SIZE, 0:SIZE] / SIZE
    tau = 2.0 * np.pi
    phase = tau * (u + 3.0 * v + 0.12 * np.sin(tau * u))
    height = 0.10 * np.sin(phase)
    dx = 0.10 * np.cos(phase) * tau * (1.0 + 0.12 * tau * np.cos(tau * u))
    dy = 0.10 * np.cos(phase) * tau * 3.0
    for amplitude, x_cycles, y_cycles, offset in [
        (0.045, 3, 5, 0.7), (0.028, 5, -2, 1.2), (0.016, 9, 7, 2.1)
    ]:
        phase = tau * (x_cycles * u + y_cycles * v) + offset
        height += amplitude * np.sin(phase)
        dx += amplitude * tau * x_cycles * np.cos(phase)
        dy += amplitude * tau * y_cycles * np.cos(phase)
    normals = np.stack((-dx / TILE_METRES, -dy / TILE_METRES, np.ones_like(u)), axis=-1)
    normals /= np.linalg.norm(normals, axis=-1, keepdims=True)
    normal = np.rint((normals * 0.5 + 0.5) * 255).astype(np.uint8)
    # Gentle body-colour variation only: specular reflections come from the lighting.
    colour = np.array([23.0, 67.0, 81.0])
    albedo = np.rint(colour * (1.0 + height[..., None] * 0.20)).astype(np.uint8)
    # Array row zero is image top, while analytic V increases from image bottom.
    return {"open_sea_albedo": np.flipud(albedo), "open_sea_normal": np.flipud(normal)}


def main():
    """Write deterministic 512-square PNGs to the runtime or an explicit scratch directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / f"art/textures/environment/{NID}")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for name, pixels in texture_arrays().items():
        Image.fromarray(pixels).save(args.output / f"{name}.png", compress_level=9)
    print("WATER_TEXTURES_PASS: two original periodic 512x512 RGB textures; 16m tile")


if __name__ == "__main__":
    main()
