"""Independent low-panel format, safety and directional graphic expectations."""
import io
import unittest

from PIL import Image

from author import OUTPUT, create_artwork


class DirectionArtworkTests(unittest.TestCase):
    """Protect reproducible artwork and asymmetric arrow/copy layout on the existing carrier."""

    def test_runtime_format_and_reproduction(self):
        """Require opaque 48:13 runtime PNG bytes to match the original source recipe."""
        with Image.open(OUTPUT) as image:
            self.assertEqual(image.mode, "RGB")
            self.assertEqual(image.size, (1440, 390))
        buffer = io.BytesIO()
        create_artwork().save(buffer, format="PNG", compress_level=9)
        self.assertEqual(buffer.getvalue(), OUTPUT.read_bytes())

    def test_carrier_safe_rectangle(self):
        """Keep antialiased ink inside the hardware's 30-pixel inset safe rectangle."""
        with Image.open(OUTPUT) as image:
            for box in [(0, 0, 1440, 30), (0, 360, 1440, 390),
                        (0, 0, 30, 390), (1410, 0, 1440, 390)]:
                self.assertEqual(set(image.crop(box).get_flattened_data()), {(52, 73, 83)})

    def test_three_arrow_bearings(self):
        """Independent solid/empty samples distinguish left, ahead and right without mirroring."""
        with Image.open(OUTPUT) as image:
            for point in [(196, 200), (249, 190), (700, 160), (690, 231),
                          (1214, 200), (1110, 190)]:
                self.assertEqual(image.getpixel(point), (233, 185, 110), point)
            for point in [(205, 165), (312, 236), (663, 241), (735, 155),
                          (1205, 165), (1095, 236)]:
                self.assertEqual(image.getpixel(point), (52, 73, 83), point)

    def test_upright_lettering_and_quiet_field(self):
        """Fixed asymmetric letter strokes catch absent, flipped or mirrored destinations."""
        with Image.open(OUTPUT) as image:
            for point, color in [((607, 310), (246, 241, 220)),
                                 ((623, 298), (52, 73, 83)),
                                 ((185, 310), (52, 73, 83)),
                                 ((62, 67), (233, 185, 110)),
                                 ((850, 200), (52, 73, 83))]:
                for actual, expected in zip(image.getpixel(point), color):
                    self.assertLessEqual(abs(actual - expected), 8, point)


if __name__ == "__main__":
    unittest.main()
