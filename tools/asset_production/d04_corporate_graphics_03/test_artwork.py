"""Independent entry-wordmark interface, family consistency and reproduction checks."""
from io import BytesIO
import unittest

from PIL import Image, ImageChops, ImageColor
import author


class EntryWordmarkTests(unittest.TestCase):
    """Protect the actual fascia interface and sparse corporate identity."""

    def test_fascia_aspect_and_opaque_format(self):
        """Map the existing 3.0 x 0.6 metre face without an alpha overlay or distortion."""
        with Image.open(author.OUTPUT) as image:
            self.assertEqual(image.size, (2000, 400))
            self.assertEqual(image.mode, "RGB")
            self.assertEqual(image.width, 5 * image.height)

    def test_hardware_safe_copy_margins(self):
        """Keep every mark inside the inherited 2.94 x 0.54 metre safe area."""
        image = author.create_artwork()
        bounds = ImageChops.difference(image, Image.new("RGB", image.size, "#15263D")).getbbox()
        self.assertIsNotNone(bounds)
        left, top, right, bottom = bounds
        self.assertGreaterEqual(left, 20)
        self.assertGreaterEqual(top, 20)
        self.assertLessEqual(right, 1980)
        self.assertLessEqual(bottom, 380)

    def test_family_emblem_and_single_word_hierarchy(self):
        """Keep the exact palette, sparse magenta and a single fictional name, not advertising."""
        self.assertEqual(author.PALETTE, {
            "field": "#15263D", "cyan": "#57D9E5", "ivory": "#F6F1DC", "magenta": "#EB62B7"
        })
        self.assertEqual(author.COPY, "TOMORROW")
        image = author.create_artwork()
        counts = {color: count for count, color in image.getcolors(image.width * image.height)}
        total = image.width * image.height
        self.assertGreater(counts[ImageColor.getrgb("#15263D")] / total, .80)
        self.assertLess(counts[ImageColor.getrgb("#EB62B7")] / total, .003)
        self.assertGreater(counts[ImageColor.getrgb("#EB62B7")], 100)
        for point in [(104, 180), (200, 104), (240, 165), (317, 270)]:
            self.assertEqual(image.getpixel(point), ImageColor.getrgb("#57D9E5"))
        self.assertEqual(image.getpixel((244, 246)), ImageColor.getrgb("#EB62B7"))
        self.assertEqual(image.getpixel((528, 200)), ImageColor.getrgb("#F6F1DC"))
        # Independent dark gutter expectation separates the logo and word.
        gutter = image.crop((340, 20, 450, 380))
        self.assertEqual(gutter.getcolors(), [(39600, (21, 38, 61))])

    def test_committed_png_byte_reproduction(self):
        """Require a fresh script render to reproduce the actual runtime PNG exactly."""
        output = BytesIO()
        author.create_artwork().save(output, format="PNG", compress_level=9)
        self.assertEqual(output.getvalue(), author.OUTPUT.read_bytes())


if __name__ == "__main__":
    unittest.main()
