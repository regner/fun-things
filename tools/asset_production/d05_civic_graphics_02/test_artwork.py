"""Independent expectations for the noticeboard's runtime file and three-card composition."""
import io
import unittest

from PIL import Image

from author import OUTPUT, create_artwork


class NoticeboardArtworkTests(unittest.TestCase):
    """Protect reproducibility, safe margins and upright, asymmetric civic graphic landmarks."""

    def test_runtime_format_and_reproduction(self):
        """The committed opaque 41:26 PNG must exactly match the reproducible source recipe."""
        with Image.open(OUTPUT) as image:
            self.assertEqual(image.mode, "RGB")
            self.assertEqual(image.size, (1640, 1040))
        buffer = io.BytesIO()
        create_artwork().save(buffer, format="PNG", compress_level=9)
        self.assertEqual(buffer.getvalue(), OUTPUT.read_bytes())

    def test_carrier_safe_rectangle(self):
        """Keep even antialiased artwork inside the carrier's 30-pixel inset safe rectangle."""
        with Image.open(OUTPUT) as image:
            for box in [(0, 0, 1640, 30), (0, 1010, 1640, 1040),
                        (0, 0, 30, 1040), (1610, 0, 1640, 1040)]:
                self.assertEqual(set(image.crop(box).get_flattened_data()), {(52, 73, 83)})

    def test_three_notice_fields(self):
        """The large ivory notice, amber meeting card and quiet lost-time card stay distinct."""
        with Image.open(OUTPUT) as image:
            for box, color in [((100, 350, 930, 370), (246, 241, 220)),
                               ((1020, 345, 1540, 355), (233, 185, 110)),
                               ((1030, 660, 1540, 675), (52, 73, 83))]:
                self.assertEqual(set(image.crop(box).get_flattened_data()), {color})

    def test_asymmetric_lettering_and_seal(self):
        """Fixed heading, hourglass and letter counters catch blank, mirrored or flipped art."""
        with Image.open(OUTPUT) as image:
            for point, color in [((145, 180), (246, 241, 220)),
                                 ((268, 195), (246, 241, 220)),
                                 ((295, 194), (52, 73, 83)),
                                 ((200, 701), (52, 73, 83)),
                                 ((750, 750), (246, 241, 220)),
                                 ((1004, 800), (233, 185, 110))]:
                for actual, expected in zip(image.getpixel(point), color):
                    self.assertLessEqual(abs(actual - expected), 8, point)


if __name__ == "__main__":
    unittest.main()
