"""Author original low-amplitude periodic basin ripples, without foam or baked highlights."""
from pathlib import Path
import argparse

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
NID = "city_water_look_02"
SIZE = 512
TILE_METRES = 16.0


def texture_arrays():
    """Differentiate a few broad periodic ripples into linear OpenGL tangent normals."""
    v, u = np.mgrid[0:SIZE, 0:SIZE] / SIZE
    tau = 2.0 * np.pi
    height = np.zeros_like(u)
    dx = np.zeros_like(u)
    dy = np.zeros_like(u)
    # Much smaller slopes than the open sea, with no short-wave noise layer.
    for amplitude, x_cycles, y_cycles, offset in [
        (0.025, 1, 2, 0.3), (0.008, 3, -1, 1.1), (0.004, 4, 5, 2.0)
    ]:
        phase = tau * (x_cycles * u + y_cycles * v) + offset
        height += amplitude * np.sin(phase)
        dx += amplitude * tau * x_cycles * np.cos(phase)
        dy += amplitude * tau * y_cycles * np.cos(phase)
    normals = np.stack((-dx / TILE_METRES, -dy / TILE_METRES, np.ones_like(u)), axis=-1)
    normals /= np.linalg.norm(normals, axis=-1, keepdims=True)
    normal = np.rint((normals * 0.5 + 0.5) * 255).astype(np.uint8)
    # Shared family body colour; reflections are lighting-dependent, not painted in.
    colour = np.array([23.0, 67.0, 81.0])
    albedo = np.rint(colour * (1.0 + height[..., None] * 0.20)).astype(np.uint8)
    # Analytic V increases upward, while PNG row zero starts at the top.
    return {"quiet_basin_albedo": np.flipud(albedo), "quiet_basin_normal": np.flipud(normal)}


def main():
    """Write deterministic 512-square RGB PNGs to runtime or explicit scratch storage."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / f"art/textures/environment/{NID}")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for name, pixels in texture_arrays().items():
        Image.fromarray(pixels).save(args.output / f"{name}.png", compress_level=9)
    print("BASIN_TEXTURES_PASS: two original periodic 512x512 RGB textures; 16m tile")


if __name__ == "__main__":
    main()
