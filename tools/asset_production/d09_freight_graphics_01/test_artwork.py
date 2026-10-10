"""Independent palette, layout, opacity and reproducibility expectations for the fascia."""
import io
import unittest

from PIL import Image

import author


class WarehouseFasciaTests(unittest.TestCase):
    """Protect artwork delivery and the shared carrier's safe-content interface."""

    def test_runtime_format(self):
        """Require the exact opaque five-to-one runtime texture, not a preview image."""
        with Image.open(author.OUTPUT) as image:
            self.assertEqual(image.size, (2000, 400))
            self.assertEqual(image.mode, "RGB")

    def test_safe_margins_and_quiet_field(self):
        """All outer 20 pixels remain field; most pixels stay visually quiet."""
        image = author.create_artwork()
        field = (20, 51, 68)
        for box in [(0, 0, 2000, 20), (0, 380, 2000, 400),
                    (0, 0, 20, 400), (1980, 0, 2000, 400)]:
            self.assertEqual(image.crop(box).getextrema(), tuple((v, v) for v in field))
        self.assertGreater(sum(count for count, color in image.getcolors(800001)
                               if color == field) / 800000, 0.70)

    def test_cargo_clock_and_cluster_separation(self):
        """Literal sample positions protect the amber parcel, dark tape and clock hand."""
        image = author.create_artwork()
        self.assertEqual(image.getpixel((95, 110)), (255, 192, 90))
        self.assertEqual(image.getpixel((205, 90)), (20, 51, 68))
        self.assertEqual(image.getpixel((204, 210)), (255, 192, 90))
        self.assertEqual(image.getpixel((170, 230)), (20, 51, 68))
        self.assertEqual(image.getpixel((375, 200)), (20, 51, 68))
        self.assertEqual(image.getpixel((1300, 280)), (133, 146, 157))

    def test_fresh_png_byte_identity(self):
        """A fresh scripted render must exactly reproduce the committed runtime PNG."""
        output = io.BytesIO()
        author.create_artwork().save(output, format="PNG", compress_level=9)
        self.assertEqual(output.getvalue(), author.OUTPUT.read_bytes())


if __name__ == "__main__":
    unittest.main()
