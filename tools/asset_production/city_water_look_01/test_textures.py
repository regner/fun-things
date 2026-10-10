"""Independent texture contract tests for the original open-sea material study."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
TEXTURES = ROOT / "art/textures/environment/city_water_look_01"


class OpenSeaTextureTests(unittest.TestCase):
    """Protect size, seam continuity, normal conventions and deterministic production."""

    def pixels(self, suffix):
        """Read committed RGB pixels without colour-space conversions."""
        with Image.open(TEXTURES / f"open_sea_{suffix}.png") as image:
            self.assertEqual(image.size, (512, 512))
            self.assertEqual(image.mode, "RGB")
            return np.asarray(image).astype(float)

    def test_quiet_dark_blue_teal_albedo(self):
        """Keep the body colour quiet: no foam, alpha or baked bright reflections."""
        pixels = self.pixels("albedo")
        self.assertTrue(np.all(pixels[..., 0] < pixels[..., 1]))
        self.assertTrue(np.all(pixels[..., 1] < pixels[..., 2]))
        self.assertLessEqual(pixels.max(), 85)
        self.assertLessEqual(np.ptp(pixels, axis=(0, 1)).max(), 7)

    def test_positive_unit_normal_map(self):
        """Normals point out of the swatch and retain small quantization error only."""
        vectors = self.pixels("normal") / 127.5 - 1
        lengths = np.linalg.norm(vectors, axis=-1)
        self.assertLess(np.abs(lengths - 1).max(), 0.007)
        self.assertGreater(vectors[..., 2].min(), 0.85)
        self.assertLess(vectors[..., 0].min(), -0.10)
        self.assertGreater(vectors[..., 0].max(), 0.10)
        self.assertLess(vectors[..., 1].min(), -0.10)
        self.assertGreater(vectors[..., 1].max(), 0.10)

    def test_repeat_edges_have_no_extra_jump(self):
        """A wrap transition must be no larger than ordinary adjacent texels."""
        for suffix in ("albedo", "normal"):
            pixels = self.pixels(suffix)
            for axis in (0, 1):
                interior = np.abs(np.diff(pixels, axis=axis)).max()
                wrap = np.abs(np.take(pixels, 0, axis=axis)
                              - np.take(pixels, -1, axis=axis)).max()
                self.assertLessEqual(wrap, interior)
                self.assertLessEqual(wrap, 4)

    def test_recipe_reproduces_png_bytes(self):
        """Run the production author in scratch and compare full encoded PNG bytes."""
        with tempfile.TemporaryDirectory(prefix="open-sea-textures-") as directory:
            subprocess.run([sys.executable, str(Path(__file__).with_name("author_textures.py")),
                            "--output", directory], check=True, timeout=30)
            for suffix in ("albedo", "normal"):
                name = f"open_sea_{suffix}.png"
                self.assertEqual((TEXTURES / name).read_bytes(), (Path(directory) / name).read_bytes())


if __name__ == "__main__":
    unittest.main()
