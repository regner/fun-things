"""Independent surface expectations for the plain plaza paving source recipe."""
import importlib.util
from pathlib import Path
import unittest

from PIL import Image

SPEC = importlib.util.spec_from_file_location("plaza_texture", Path(__file__).with_name("texture.py"))
TEXTURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TEXTURE)


class PlainPlazaPavingTests(unittest.TestCase):
    """Protect quiet midtone color, seamless tiling and the committed original output."""

    @classmethod
    def setUpClass(cls):
        """Render the deterministic texture once for all independent expectations."""
        cls.image = TEXTURE.create_texture()

    def test_committed_texture_matches_recipe(self):
        """The delivered PNG must contain exactly the authored RGB pixels."""
        with Image.open(TEXTURE.OUTPUT) as saved:
            self.assertEqual(saved.mode, "RGB")
            self.assertEqual(saved.size, (512, 512))
            self.assertEqual(saved.tobytes(), self.image.tobytes())

    def test_opposite_borders_match(self):
        """Edge samples meet without a bright/dark jump in either tiling direction."""
        for i in range(512):
            self.assertEqual(self.image.getpixel((0, i)), self.image.getpixel((511, i)))
            self.assertEqual(self.image.getpixel((i, 0)), self.image.getpixel((i, 511)))

    def test_midtone_and_low_contrast(self):
        """No channel gains the high-frequency/high-contrast energy reserved for actors."""
        for low, high in self.image.getextrema():
            self.assertGreaterEqual(low, 120)
            self.assertLessEqual(high, 162)
            self.assertLessEqual(high - low, 12)
        self.assertEqual(self.image.getpixel((64, 64)), (134, 147, 158))

    def test_sparse_broad_slab_rhythm(self):
        """A four-metre tile has only two joints along a line through slab centres."""
        scan = [self.image.getpixel((x, 64))[0] < 129 for x in range(512)]
        starts = sum(scan[x] and not scan[(x - 1) % 512] for x in range(512))
        self.assertEqual(starts, 2)
        self.assertLessEqual(sum(scan), 12)

    def test_mipmap_quietness(self):
        """Minified overview remains a neutral field instead of a high-contrast grid."""
        overview = self.image.resize((16, 16), Image.Resampling.BOX)
        self.assertLessEqual(max(hi - lo for lo, hi in overview.getextrema()), 5)


if __name__ == "__main__":
    unittest.main()
