"""Independent expectations for the civic fascia's runtime artwork and margins."""
import io
import unittest

from PIL import Image

from author import OUTPUT, create_artwork


class HallFasciaArtworkTests(unittest.TestCase):
    """Protect file reproducibility, the face contract and warm civic graphic landmarks."""

    def test_runtime_format_and_reproduction(self):
        """The committed opaque 5:1 PNG is the exact output of the retained recipe."""
        with Image.open(OUTPUT) as image:
            self.assertEqual(image.mode, "RGB")
            self.assertEqual(image.size, (2000, 400))
        output = io.BytesIO()
        create_artwork().save(output, format="PNG", compress_level=9)
        self.assertEqual(output.getvalue(), OUTPUT.read_bytes())

    def test_safe_content_and_quiet_field(self):
        """Keep all artwork inside the carrier's 2.94 by 0.54 metre safe content area."""
        image = Image.open(OUTPUT)
        slate = (52, 73, 83)
        for box in [(0, 0, 2000, 20), (0, 380, 2000, 400),
                    (0, 0, 20, 400), (1980, 0, 2000, 400)]:
            self.assertEqual(set(image.crop(box).get_flattened_data()), {slate})
        self.assertGreater(sum(pixel == slate for pixel in image.get_flattened_data()) / 800000, 0.75)

    def test_seal_and_asymmetric_copy_landmarks(self):
        """Fixed emblem, empty counters and heading pixels catch mirroring or missing layers."""
        image = Image.open(OUTPUT)
        for point, color in [((174, 63), (233, 185, 110)),
                             ((207, 200), (246, 241, 220)),
                             ((185, 205), (52, 73, 83)),
                             ((420, 100), (233, 185, 110)),
                             ((444, 240), (246, 241, 220)),
                             ((1868, 333), (233, 185, 110))]:
            for actual, expected in zip(image.getpixel(point), color):
                self.assertLessEqual(abs(actual - expected), 8, point)


if __name__ == "__main__":
    unittest.main()
