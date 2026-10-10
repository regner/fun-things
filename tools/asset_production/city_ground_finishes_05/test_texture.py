"""Independent soil expectations for quiet warm colour, broad forms and seamless repeats."""
import importlib.util
from pathlib import Path
import unittest

from PIL import Image

SPEC = importlib.util.spec_from_file_location("soil_texture", Path(__file__).with_name("texture.py"))
TEXTURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TEXTURE)


class QuietGardenSoilTests(unittest.TestCase):
    """Keep soil distinct from grass and paving without competing with actor accents."""

    @classmethod
    def setUpClass(cls):
        """Produce one deterministic image for independent pixel expectations."""
        cls.image = TEXTURE.create_texture()

    def test_committed_texture_matches_recipe(self):
        """The committed RGB texture is exactly reproducible from the source recipe."""
        with Image.open(TEXTURE.OUTPUT) as saved:
            self.assertEqual(saved.mode, "RGB")
            self.assertEqual(saved.size, (512, 512))
            self.assertEqual(saved.tobytes(), self.image.tobytes())

    def test_seamless_borders(self):
        """Both pairs of opposing borders meet exactly with ordinary repeat sampling."""
        for i in range(512):
            self.assertEqual(self.image.getpixel((0, i)), self.image.getpixel((511, i)))
            self.assertEqual(self.image.getpixel((i, 0)), self.image.getpixel((i, 511)))

    def test_muted_earth_below_actor_highlights(self):
        """Warm low-chroma loam excludes green lawn, orange accents and near-black mud."""
        for channel, (floor, ceiling) in enumerate(((100, 110), (86, 96), (74, 83))):
            low, high = self.image.getextrema()[channel]
            self.assertGreaterEqual(low, floor)
            self.assertLessEqual(high, ceiling)
            self.assertLessEqual(high - low, 8)
        for red, green, blue in self.image.get_flattened_data():
            self.assertGreaterEqual(red - green, 12)
            self.assertGreaterEqual(green - blue, 10)
            self.assertLessEqual(red - blue, 30)

    def test_no_grit_or_crack_edges(self):
        """No channel jumps more than one code value between adjacent repeat samples."""
        pixels = self.image.load()
        for y in range(512):
            for x in range(512):
                for channel in range(3):
                    value = pixels[x, y][channel]
                    self.assertLessEqual(abs(value - pixels[(x + 1) % 512, y][channel]), 1)
                    self.assertLessEqual(abs(value - pixels[x, (y + 1) % 512][channel]), 1)

    def test_soft_loam_survives_minification(self):
        """Broad earth variation stays subdued at roughly gameplay-camera texel density."""
        small = self.image.resize((16, 16), Image.Resampling.BOX)
        for channel in (0, 1):
            low, high = small.getextrema()[channel]
            self.assertGreaterEqual(high - low, 5)
            self.assertLessEqual(high - low, 8)


if __name__ == "__main__":
    unittest.main()
