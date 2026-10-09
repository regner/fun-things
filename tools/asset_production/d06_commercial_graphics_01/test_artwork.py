"""Independent output/interface expectations for the hall title artwork."""
import hashlib
import importlib.util
import io
from pathlib import Path
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
PNG = ROOT / "art/textures/environment/d06_commercial_graphics_01/hall_title_albedo.png"
SPEC = importlib.util.spec_from_file_location("hall_author", Path(__file__).with_name("author.py"))
AUTHOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUTHOR)


class HallTitleArtworkTests(unittest.TestCase):
    """Protect the accepted fascia aspect, quiet margin, emblem and reproducible output."""

    def test_fascia_aspect_and_opaque_rgb(self):
        """The shared 3.0 x 0.6 m face takes one opaque 2000 x 400 albedo."""
        with Image.open(PNG) as image:
            self.assertEqual(image.size, (2000, 400))
            self.assertEqual(image.mode, "RGB")

    def test_safe_rectangle_and_quiet_background(self):
        """Important shapes stay within the existing 2.94 x 0.54 m safe rectangle."""
        with Image.open(PNG) as image:
            petrol = (16, 44, 60)
            for region in [(0, 0, 2000, 20), (0, 380, 2000, 400),
                           (0, 0, 20, 400), (1980, 0, 2000, 400)]:
                self.assertEqual(set(image.crop(region).get_flattened_data()), {petrol})
            pixels = list(image.get_flattened_data())
            self.assertGreater(pixels.count(petrol) / len(pixels), 0.65)

    def test_emblem_colors_and_gaps(self):
        """Broad top/bottom chromatic arcs stay separated at the horizontal axis."""
        with Image.open(PNG) as image:
            self.assertEqual(image.getpixel((216, 73)), (245, 75, 186))
            self.assertEqual(image.getpixel((216, 327)), (69, 223, 229))
            self.assertEqual(image.getpixel((89, 200)), (16, 44, 60))
            self.assertEqual(image.getpixel((343, 200)), (16, 44, 60))

    def test_reauthor_byte_identical(self):
        """Fresh scripted authoring reproduces every committed PNG byte."""
        output = io.BytesIO()
        AUTHOR.create_artwork().save(output, format="PNG", optimize=False, compress_level=9)
        self.assertEqual(hashlib.sha256(output.getvalue()).digest(),
                         hashlib.sha256(PNG.read_bytes()).digest())


if __name__ == "__main__":
    unittest.main()
