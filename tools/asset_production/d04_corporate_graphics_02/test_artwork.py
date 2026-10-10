"""Independent low-directory layout, family consistency and deterministic output checks."""
import hashlib
from io import BytesIO
from pathlib import Path
import unittest

from PIL import Image, ImageChops, ImageColor
import author


class DirectoryArtworkTests(unittest.TestCase):
    """Protect the actual small-carrier interface rather than merely checking PNG existence."""

    def test_carrier_aspect_and_opaque_format(self):
        """Keep the 1.44 x .39 metre face undistorted, with no transparent overlay."""
        with Image.open(author.OUTPUT) as image:
            self.assertEqual(image.size, (1440, 390))
            self.assertEqual(image.mode, "RGB")
            self.assertEqual(image.width * 13, image.height * 48)

    def test_safe_copy_margins(self):
        """Confine all marks to the hardware's 1.38 x .33 metre safe rectangle."""
        image = author.create_artwork()
        field = Image.new("RGB", image.size, "#15263D")
        bounds = ImageChops.difference(image, field).getbbox()
        self.assertIsNotNone(bounds)
        left, top, right, bottom = bounds
        self.assertGreaterEqual(left, 30)
        self.assertGreaterEqual(top, 30)
        self.assertLessEqual(right, 1410)
        self.assertLessEqual(bottom, 360)

    def test_family_palette_and_directory_hierarchy(self):
        """Keep a quiet field, rare magenta, distinct rows and the sibling appointment emblem."""
        self.assertEqual(author.PALETTE, {
            "field": "#15263D", "cyan": "#57D9E5", "ivory": "#F6F1DC", "magenta": "#EB62B7"
        })
        image = author.create_artwork()
        counts = {color: count for count, color in image.getcolors(image.width * image.height)}
        total = image.width * image.height
        self.assertGreater(counts[ImageColor.getrgb("#15263D")] / total, .80)
        self.assertLess(counts[ImageColor.getrgb("#EB62B7")] / total, .003)
        self.assertGreater(counts[ImageColor.getrgb("#EB62B7")], 100)
        self.assertEqual(author.COPY, ("DIRECTORY", "A", "TOMORROW", "B", "LATER"))
        # Independent samples on the two cyan corners, rare marker and two distinct row labels.
        for point in [(86, 140), (230, 81), (200, 142), (305, 275), (399, 213), (399, 310)]:
            self.assertEqual(image.getpixel(point), ImageColor.getrgb("#57D9E5"))
        self.assertEqual(image.getpixel((226, 226)), ImageColor.getrgb("#EB62B7"))
        # The separating dark gutter must remain blank above the cyan rule.
        self.assertEqual(image.crop((395, 235, 1338, 246)).getcolors(), [(10373, (21, 38, 61))])

    def test_reproducible_committed_png(self):
        """Require a fresh author pass to match the actual runtime texture byte for byte."""
        output = BytesIO()
        author.create_artwork().save(output, format="PNG", compress_level=9)
        self.assertEqual(output.getvalue(), Path(author.OUTPUT).read_bytes())
        self.assertEqual(hashlib.sha256(output.getvalue()).digest(),
                         hashlib.sha256(Path(author.OUTPUT).read_bytes()).digest())


if __name__ == "__main__":
    unittest.main()
