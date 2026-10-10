"""Independent expectations for the delivered parking-zone graphic and safe face margins."""
from collections import Counter
from io import BytesIO
import unittest

from PIL import Image, ImageColor

import author


class ParkingArtworkTests(unittest.TestCase):
    """Check output bytes, rounded-carrier safety and recognizable graphic components."""

    def test_opaque_format_and_reproducibility(self):
        """The committed texture must exactly match a fresh original-path render."""
        image = Image.open(BytesIO(author.OUTPUT.read_bytes()))
        self.assertEqual(image.size, (1220, 820))
        self.assertEqual(image.mode, "RGB")
        fresh = BytesIO()
        author.create_artwork().save(fresh, format="PNG", compress_level=9)
        self.assertEqual(fresh.getvalue(), author.OUTPUT.read_bytes())

    def test_safe_margins_and_sparse_accents(self):
        """All copy fits inside the physical safe region, with mostly quiet petrol."""
        image = Image.open(BytesIO(author.OUTPUT.read_bytes()))
        petrol = ImageColor.getrgb("#102C3C")
        counts = Counter(image.get_flattened_data())
        self.assertGreater(counts[petrol] / (1220 * 820), .78)
        self.assertLess(counts[ImageColor.getrgb("#B8DC6F")] / (1220 * 820), .003)
        for box in [(0, 0, 1220, 40), (0, 780, 1220, 820),
                    (0, 0, 40, 820), (1180, 0, 1220, 820)]:
            self.assertEqual(set(image.crop(box).get_flattened_data()), {petrol})

    def test_parking_p_zone_a_and_ticket(self):
        """Literal samples protect P's stem/counter, A's gap and the one lime ticket."""
        image = Image.open(BytesIO(author.OUTPUT.read_bytes()))
        samples = {
            "#FF725D": [(160, 590), (414, 290), (280, 185), (738, 620), (807, 545)],
            "#102C3C": [(280, 290), (320, 570), (807, 605), (1033, 415)],
            "#F6F1DC": [(625, 176)],
            "#B8DC6F": [(1033, 370)],
        }
        for color, points in samples.items():
            for point in points:
                with self.subTest(point=point):
                    self.assertEqual(image.getpixel(point), ImageColor.getrgb(color))


if __name__ == "__main__":
    unittest.main()
