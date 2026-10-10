"""Independent content and reproducibility checks for the retail fascia artwork."""
import io
import unittest
from collections import Counter

from PIL import Image, ImageColor

from author import OUTPUT, create_artwork


class RetailFasciaArtworkTests(unittest.TestCase):
    """Protect the output contract without deriving expectations from drawing formulas."""

    def test_texture_format_and_reproduction(self):
        """The committed opaque albedo must exactly match a fresh recipe run."""
        with Image.open(OUTPUT) as image:
            self.assertEqual(image.size, (2000, 400))
            self.assertEqual(image.mode, "RGB")
        output = io.BytesIO()
        create_artwork().save(output, format="PNG", compress_level=9)
        self.assertEqual(output.getvalue(), OUTPUT.read_bytes())

    def test_safe_perimeter_and_quiet_field(self):
        """The 2.94-by-.54-m safe region leaves no coloured edge bleeding."""
        with Image.open(OUTPUT) as image:
            petrol = ImageColor.getrgb("#102C3C")
            for rectangle in [(0, 0, 2000, 20), (0, 380, 2000, 400),
                              (0, 0, 20, 400), (1980, 0, 2000, 400)]:
                self.assertEqual(set(image.crop(rectangle).get_flattened_data()), {petrol})
            counts = Counter(image.get_flattened_data())
            self.assertGreater(counts[petrol] / (2000 * 400), .78)
            self.assertLess(counts[ImageColor.getrgb("#B8DC6F")] / (2000 * 400), .003)

    def test_original_icon_and_copy_colours(self):
        """Independent samples protect coral bag, lime ticket, open corner and copy levels."""
        with Image.open(OUTPUT) as image:
            self.assertEqual(image.getpixel((92, 220)), (255, 114, 93))
            self.assertEqual(image.getpixel((260, 91)), (184, 220, 111))
            self.assertEqual(image.getpixel((245, 139)), (16, 44, 60))
            self.assertEqual(image.getpixel((392, 100)), (246, 241, 220))
            self.assertEqual(image.getpixel((392, 250)), (255, 114, 93))


if __name__ == "__main__":
    unittest.main()
