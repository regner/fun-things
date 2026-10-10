"""Independent pixel and format expectations for the derived low parking panel."""
import io
import unittest

from PIL import Image

import author


class ParkingArtworkTests(unittest.TestCase):
    """Protect the exact carrier interface and readable, safe original-content layout."""

    def test_reproduction_and_format(self):
        """A fresh recipe must match the committed opaque 48:13 texture byte for byte."""
        image = author.create_artwork()
        self.assertEqual(image.size, (1440, 390))
        self.assertEqual(image.mode, "RGB")
        output = io.BytesIO()
        image.save(output, format="PNG", compress_level=9)
        self.assertEqual(output.getvalue(), author.OUTPUT.read_bytes())
        with Image.open(author.OUTPUT) as saved:
            self.assertEqual(saved.size[0] * 13, saved.size[1] * 48)

    def test_safe_margin_and_quiet_field(self):
        """Keep the 30-pixel perimeter empty and avoid turning the low sign into a light bar."""
        image = author.create_artwork()
        petrol = (16, 44, 60)
        for box in [(0, 0, 1440, 30), (0, 360, 1440, 390),
                    (0, 0, 30, 390), (1410, 0, 1440, 390)]:
            self.assertEqual(image.crop(box).getcolors(), [(image.crop(box).width *
                                                         image.crop(box).height, petrol)])
        colors = dict((rgb, count) for count, rgb in image.getcolors(1440 * 390))
        self.assertGreater(colors[petrol] / (1440 * 390), .80)
        self.assertLess(colors[(184, 220, 111)] / (1440 * 390), .004)

    def test_original_content_landmarks(self):
        """Independent broad samples protect P counter, ZONE, A crossbar and small lime ticket."""
        image = author.create_artwork()
        for point, expected in {
            (115, 275): (255, 114, 93),
            (170, 145): (16, 44, 60),
            (410, 107): (246, 241, 220),
            (1025, 208): (255, 114, 93),
            (1025, 150): (16, 44, 60),
            (1290, 193): (184, 220, 111),
        }.items():
            self.assertEqual(image.getpixel(point), expected, point)


if __name__ == "__main__":
    unittest.main()
