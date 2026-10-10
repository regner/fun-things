"""Independent pixel expectations for the delivered open civic-square inset."""
import io
import unittest

from PIL import Image

from artwork import TEXTURE, draw_artwork


class CivicInsetArtworkTests(unittest.TestCase):
    """Protect sparse composition, open approaches and real-scale stroke readability."""

    def test_exact_reproduction(self):
        """Require exact committed PNG reproduction and the physical-resolution contract."""
        buffer = io.BytesIO()
        draw_artwork().save(buffer, format="PNG", compress_level=9)
        self.assertEqual(buffer.getvalue(), TEXTURE.read_bytes())
        with Image.open(TEXTURE) as image:
            self.assertEqual(image.size, (960, 960))
            self.assertEqual(image.mode, "RGB")

    def test_quiet_centre_openings_and_margins(self):
        """The centre, two-metre cardinal approaches and outer margin remain undecorated."""
        with Image.open(TEXTURE) as image:
            for box in [(160, 160, 800, 800), (324, 0, 636, 960), (0, 324, 960, 636),
                        (0, 0, 960, 64), (0, 896, 960, 960),
                        (0, 0, 64, 960), (896, 0, 960, 960)]:
                self.assertEqual(set(image.crop(box).get_flattened_data()), {(166, 167, 158)})
            quiet = sum(n for n, color in image.getcolors(960 * 960)
                        if color == (166, 167, 158)) / (960 * 960)
            self.assertGreater(quiet, .93)
            self.assertLess(quiet, .96)

    def test_four_corners_and_rounded_elbows(self):
        """Independent landmarks require four separated brackets rather than a frame or target."""
        with Image.open(TEXTURE) as image:
            for x, y in [(240, 94), (720, 94), (240, 866), (720, 866),
                         (94, 240), (866, 240), (94, 720), (866, 720),
                         (110, 110), (850, 110), (110, 850), (850, 850)]:
                self.assertEqual(image.getpixel((x, y)), (101, 126, 123))
            for point in [(80, 80), (880, 80), (80, 880), (880, 880), (480, 480)]:
                self.assertEqual(image.getpixel(point), (166, 167, 158))
            stroke = [y for y in range(160) if image.getpixel((240, y))[0] < 130]
            self.assertGreaterEqual(len(stroke), 27)
            self.assertLessEqual(len(stroke), 31)

    def test_minified_readability(self):
        """At roughly gameplay size each bracket survives while the central approach stays quiet."""
        with Image.open(TEXTURE) as image:
            small = image.resize((120, 120), Image.Resampling.LANCZOS)
            for point in [(30, 12), (90, 12), (30, 108), (90, 108)]:
                self.assertLess(small.getpixel(point)[0], 135)
            self.assertEqual(small.getpixel((60, 12)), (166, 167, 158))
            self.assertEqual(small.getpixel((60, 60)), (166, 167, 158))


if __name__ == "__main__":
    unittest.main(verbosity=2)
