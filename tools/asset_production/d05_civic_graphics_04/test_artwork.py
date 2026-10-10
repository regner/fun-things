"""Independent image expectations for the warm shop-front fascia set."""
import io
import unittest

from PIL import Image, ImageChops

import author


class ShopFasciaArtworkTests(unittest.TestCase):
    """Protect deterministic output, safe margins and distinct upright tenant symbols."""

    def test_deterministic_runtime_pngs(self):
        """Every committed albedo must exactly reproduce and retain the 5:1 RGB contract."""
        self.assertEqual(set(author.VARIANTS), {"tide_tea", "quay_pantry", "hem_repairs"})
        for variant in author.VARIANTS:
            with self.subTest(variant=variant):
                image = author.create_artwork(variant)
                self.assertEqual(image.size, (2000, 400))
                self.assertEqual(image.mode, "RGB")
                data = io.BytesIO()
                image.save(data, format="PNG", compress_level=9)
                self.assertEqual(data.getvalue(),
                                 (author.OUTPUT / f"{variant}_albedo.png").read_bytes())

    def test_safe_margins_and_quiet_fields(self):
        """The exact carrier safe rectangle and majority quiet background cannot regress."""
        for variant, background in [("tide_tea", (52, 73, 83)),
                                    ("quay_pantry", (81, 68, 82)),
                                    ("hem_repairs", (52, 73, 83))]:
            image = author.create_artwork(variant)
            for bounds in [(0, 0, 20, 400), (1980, 0, 2000, 400),
                           (0, 0, 2000, 20), (0, 380, 2000, 400)]:
                margin = image.crop(bounds)
                self.assertIsNone(ImageChops.difference(
                    margin, Image.new("RGB", margin.size, background)).getbbox())
            pixels = list(image.get_flattened_data())
            self.assertGreater(pixels.count(background) / len(pixels), 0.75)

    def test_independent_trade_symbol_landmarks(self):
        """Cup handle, jar lid and thread spool are distinct, not three recoloured emblems."""
        ivory, amber = (246, 241, 220), (233, 185, 110)
        expected = {
            "tide_tea": [((300, 184), ivory), ((190, 301), amber), ((177, 84), amber)],
            "quay_pantry": [((200, 114), amber), ((126, 220), ivory), ((200, 260), amber)],
            "hem_repairs": [((200, 112), ivory), ((148, 220), amber), ((200, 297), ivory)],
        }
        for variant, landmarks in expected.items():
            image = author.create_artwork(variant)
            for point, color in landmarks:
                with self.subTest(variant=variant, point=point):
                    self.assertLessEqual(max(abs(a-b) for a, b in zip(
                        image.getpixel(point), color)), 8)

    def test_asymmetric_lettering_and_variant_distinction(self):
        """Literal title strokes and counters catch flipped, missing or substituted copy."""
        ivory = (246, 241, 220)
        expected = {
            "tide_tea": [((495, 94), ivory), ((495, 160), ivory), ((451, 200), (52, 73, 83))],
            "quay_pantry": [((451, 165), ivory), ((493, 160), (81, 68, 82)),
                            ((527, 237), ivory)],
            "hem_repairs": [((451, 165), ivory), ((492, 166), ivory),
                            ((492, 115), (52, 73, 83))],
        }
        for variant, landmarks in expected.items():
            image = author.create_artwork(variant)
            for point, color in landmarks:
                with self.subTest(variant=variant, point=point):
                    self.assertLessEqual(max(abs(a-b) for a, b in zip(
                        image.getpixel(point), color)), 8)


if __name__ == "__main__":
    unittest.main()
