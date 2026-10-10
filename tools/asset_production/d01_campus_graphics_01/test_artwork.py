"""Protect the campus-map texture contract using independent pixel and file expectations."""
import hashlib
import io
from pathlib import Path
import sys
import unittest

from PIL import Image, ImageChops

sys.path.insert(0, str(Path(__file__).parent))
import author


class CampusMapArtworkTests(unittest.TestCase):
    """Check deterministic source output, safe margins and distinct broad graphic anchors."""

    @classmethod
    def setUpClass(cls):
        """Read the shipped PNG, not just the authoring function's in-memory image."""
        cls.image = Image.open(author.OUTPUT)
        cls.image.load()

    def test_opaque_correct_aspect_and_size(self):
        """The unchanged carrier requires a 41:26 opaque face with no alpha channel."""
        self.assertEqual(self.image.mode, "RGB")
        self.assertEqual(self.image.size, (1640, 1040))

    def test_fresh_artwork_byte_identical(self):
        """A clean draw under the recorded Pillow version must reproduce every PNG byte."""
        data = io.BytesIO()
        author.create_artwork().save(data, format="PNG", compress_level=9)
        self.assertEqual(hashlib.sha256(data.getvalue()).hexdigest(),
                         hashlib.sha256(author.OUTPUT.read_bytes()).hexdigest())

    def test_print_stays_inside_carrier_safe_rectangle(self):
        """Rounded hardware clips no authored copy; the outer 30 pixels are unprinted."""
        field = Image.new("RGB", self.image.size, "#233F4A")
        bounds = ImageChops.difference(self.image, field).getbbox()
        self.assertGreaterEqual(bounds[0], 30)
        self.assertGreaterEqual(bounds[1], 30)
        self.assertLessEqual(bounds[2], 1610)
        self.assertLessEqual(bounds[3], 1010)

    def test_distinct_map_and_crest_anchor_colors(self):
        """Independent interior samples protect the mint book, warm point and field masses."""
        for point, rgb in [((1430, 165), (163, 220, 197)),
                           ((1465, 85), (255, 192, 90)),
                           ((567, 475), (85, 123, 112)),
                           ((392, 500), (255, 114, 93)),
                           ((400, 765), (163, 220, 197))]:
            with self.subTest(point=point):
                self.assertEqual(self.image.getpixel(point), rgb)

    def test_no_duplicate_carrier_asset(self):
        """Artwork delivery must remain linked to shared Blender hardware, not a new carrier."""
        for folder in ("art/source/models/environment", "art/models/environment"):
            self.assertFalse((author.ROOT / folder / author.NID).exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
