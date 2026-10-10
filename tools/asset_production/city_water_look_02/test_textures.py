"""Independent image-level contracts for the quieter basin material study."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
TEXTURES = ROOT / "art/textures/environment/city_water_look_02"


def pixels(path):
    """Read committed RGB pixels without colour-space conversion."""
    with Image.open(path) as image:
        assert image.size == (512, 512) and image.mode == "RGB"
        return np.asarray(image).astype(float)


class QuietBasinTextureTests(unittest.TestCase):
    """Protect quiet family colour, calibrated slope difference, seams and reproduction."""

    def test_quiet_family_albedo(self):
        """Preserve the sea's dark teal body with at most two levels of channel variation."""
        colour = pixels(TEXTURES / "quiet_basin_albedo.png")
        self.assertTrue(np.all(colour[..., 0] < colour[..., 1]))
        self.assertTrue(np.all(colour[..., 1] < colour[..., 2]))
        np.testing.assert_allclose(colour.mean(axis=(0, 1)), [23, 67, 81], atol=0.1)
        self.assertLessEqual(np.ptp(colour, axis=(0, 1)).max(), 2)
        self.assertLessEqual(colour.max(), 82)

    def test_normals_are_unit_and_calm_but_not_flat(self):
        """Keep finite outward unit normals, with visible but strictly low-amplitude slopes."""
        vectors = pixels(TEXTURES / "quiet_basin_normal.png") / 127.5 - 1
        self.assertLess(np.abs(np.linalg.norm(vectors, axis=-1) - 1).max(), 0.007)
        self.assertGreater(vectors[..., 2].min(), 0.99)
        for channel in (0, 1):
            self.assertLess(vectors[..., channel].min(), -0.01)
            self.assertGreater(vectors[..., channel].max(), 0.01)
            self.assertLess(np.abs(vectors[..., channel]).max(), 0.04)

    def test_basin_slopes_quieter_than_delivered_open_sea(self):
        """Compare actual delivered maps, not a duplicate of the authoring formula."""
        basin = pixels(TEXTURES / "quiet_basin_normal.png") / 127.5 - 1
        sea = pixels(ROOT / "art/textures/environment/city_water_look_01/open_sea_normal.png")
        sea = sea / 127.5 - 1
        basin_rms = np.sqrt(np.mean(basin[..., :2] ** 2))
        sea_rms = np.sqrt(np.mean(sea[..., :2] ** 2))
        self.assertGreater(basin_rms, 0.005)
        self.assertLess(basin_rms, sea_rms * 0.20)
        print(f"BASIN_SLOPE_RMS: {basin_rms:.6f}; sea {sea_rms:.6f}; ratio {basin_rms / sea_rms:.6f}")

    def test_repeat_edges_have_no_extra_jump(self):
        """Wrap transitions cannot exceed ordinary adjacent texels or one RGB code step."""
        for suffix in ("albedo", "normal"):
            image = pixels(TEXTURES / f"quiet_basin_{suffix}.png")
            for axis in (0, 1):
                interior = np.abs(np.diff(image, axis=axis)).max()
                wrap = np.abs(np.take(image, 0, axis=axis) - np.take(image, -1, axis=axis)).max()
                self.assertLessEqual(wrap, interior)
                self.assertLessEqual(wrap, 1)

    def test_recipe_reproduces_png_bytes(self):
        """Run the production author in scratch and compare complete encoded PNG bytes."""
        with tempfile.TemporaryDirectory(prefix="quiet-basin-textures-") as directory:
            subprocess.run([sys.executable, str(Path(__file__).with_name("author_textures.py")),
                            "--output", directory], check=True, timeout=30)
            for suffix in ("albedo", "normal"):
                name = f"quiet_basin_{suffix}.png"
                self.assertEqual((TEXTURES / name).read_bytes(), (Path(directory) / name).read_bytes())


if __name__ == "__main__":
    result = unittest.main(exit=False).result
    if not result.wasSuccessful():
        sys.exit(1)
    basin = pixels(TEXTURES / "quiet_basin_normal.png") / 127.5 - 1
    sea_path = ROOT / "art/textures/environment/city_water_look_01/open_sea_normal.png"
    sea = pixels(sea_path) / 127.5 - 1
    basin_rms = float(np.sqrt(np.mean(basin[..., :2] ** 2)))
    sea_rms = float(np.sqrt(np.mean(sea[..., :2] ** 2)))
    receipt = Path("C:/tmp/ft/assets/city_water_look_02/texture-tests.json")
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps({
        "status": "PASS", "tests": result.testsRun,
        "basin_xy_normal_rms": basin_rms, "open_sea_xy_normal_rms": sea_rms,
        "basin_to_open_sea_slope_ratio": basin_rms / sea_rms,
        "albedo_channel_range_max": 2, "wrap_jump_limit_rgb_codes": 1,
        "fresh_png_bytes_identical": True,
    }, indent=2) + "\n", newline="\n")
