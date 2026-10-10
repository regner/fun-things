"""Independent output, layout and family-identity tests for the sign-island face."""
import io
import unittest
from collections import Counter

from PIL import Image

from author import OUTPUT, create_artwork


class SignIslandFaceArtworkTests(unittest.TestCase):
    """Protect literal content expectations rather than repeating layout formulas."""

    def test_texture_format_and_reproduction(self):
        """The opaque 48:23 artwork must reproduce the committed bytes exactly."""
        with Image.open(OUTPUT) as image:
            self.assertEqual(image.size, (1920, 920))
            self.assertEqual(image.mode, "RGB")
        output = io.BytesIO()
        create_artwork().save(output, format="PNG", compress_level=9)
        self.assertEqual(output.getvalue(), OUTPUT.read_bytes())

    def test_safe_perimeter_and_quiet_field(self):
        """Keep a 60-pixel quiet perimeter and sparse lime rather than a luminous carpet."""
        with Image.open(OUTPUT) as image:
            petrol = (16, 44, 60)
            for rectangle in [(0, 0, 1920, 60), (0, 860, 1920, 920),
                              (0, 0, 60, 920), (1860, 0, 1920, 920)]:
                self.assertEqual(set(image.crop(rectangle).get_flattened_data()), {petrol})
            counts = Counter(image.get_flattened_data())
            self.assertGreater(counts[petrol] / (1920 * 920), .78)
            self.assertLess(counts[(184, 220, 111)] / (1920 * 920), .003)

    def test_original_icon_and_copy_colours(self):
        """Check independent samples of the bag, ticket, missing corner and three copy lines."""
        with Image.open(OUTPUT) as image:
            self.assertEqual(image.getpixel((144, 560)), (255, 114, 93))
            self.assertEqual(image.getpixel((490, 303)), (184, 220, 111))
            self.assertEqual(image.getpixel((450, 399)), (16, 44, 60))
            self.assertEqual(image.getpixel((690, 220)), (246, 241, 220))
            self.assertEqual(image.getpixel((690, 450)), (255, 114, 93))
            self.assertEqual(image.getpixel((690, 700)), (255, 114, 93))


if __name__ == "__main__":
    unittest.main()
