"""Independent material expectations for the original service-concrete recipe."""
import importlib.util
from pathlib import Path
import unittest

from PIL import Image

SPEC = importlib.util.spec_from_file_location("concrete_texture", Path(__file__).with_name("texture.py"))
TEXTURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TEXTURE)


class ServiceConcreteTests(unittest.TestCase):
    """Protect low-contrast concrete without a plaza grid or distracting surface flecks."""

    @classmethod
    def setUpClass(cls):
        """Render the original deterministic source once for independent checks."""
        cls.image = TEXTURE.create_texture()

    def test_committed_texture_matches_recipe(self):
        """The delivered albedo must contain exactly the authored RGB pixels."""
        with Image.open(TEXTURE.OUTPUT) as saved:
            self.assertEqual(saved.mode, "RGB")
            self.assertEqual(saved.size, (512, 512))
            self.assertEqual(saved.tobytes(), self.image.tobytes())

    def test_seamless_borders(self):
        """Opposite edge samples meet in both directions without special border strips."""
        for i in range(512):
            self.assertEqual(self.image.getpixel((0, i)), self.image.getpixel((511, i)))
            self.assertEqual(self.image.getpixel((i, 0)), self.image.getpixel((i, 511)))

    def test_quiet_desaturated_midtone(self):
        """Concrete stays below actor highlights and distinct from blue plaza slate."""
        for low, high in self.image.getextrema():
            self.assertGreaterEqual(low, 130)
            self.assertLessEqual(high, 151)
            self.assertLessEqual(high - low, 9)
            self.assertGreaterEqual(high - low, 5)
        for red, green, blue in self.image.get_flattened_data():
            self.assertGreater(green, blue)
            self.assertLessEqual(max(red, green, blue) - min(red, green, blue), 8)

    def test_no_grit_or_grout_edges(self):
        """Adjacent samples differ by at most one code value, unlike cracks or grout."""
        pixels = self.image.load()
        for y in range(512):
            for x in range(512):
                self.assertLessEqual(abs(pixels[x, y][0] - pixels[(x + 1) % 512, y][0]), 1)
                self.assertLessEqual(abs(pixels[x, y][0] - pixels[x, (y + 1) % 512][0]), 1)

    def test_broad_washes_survive_minification(self):
        """The overhead field retains restrained large forms, never sparkling microdetail."""
        small = self.image.resize((16, 16), Image.Resampling.BOX)
        for low, high in small.getextrema():
            self.assertGreaterEqual(high - low, 5)
            self.assertLessEqual(high - low, 8)


if __name__ == "__main__":
    unittest.main()
