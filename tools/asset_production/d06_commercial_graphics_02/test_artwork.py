"""Independent artwork expectations, including severe frontage-scale downsampling."""
import io
import unittest

from PIL import Image, ImageColor

from author import OUTPUT, VARIANTS, create_artwork


class FasciaArtworkTests(unittest.TestCase):
    """Protect opaque sizes, safe edges, motif placement and colour-mass contrast."""

    def test_rgb_dimensions_and_reproduction(self):
        """Every committed PNG must reproduce byte-for-byte from the original recipe."""
        for variant in VARIANTS:
            with self.subTest(variant=variant):
                path = OUTPUT / f"{variant}_albedo.png"
                with Image.open(path) as image:
                    self.assertEqual(image.size, (2000, 400))
                    self.assertEqual(image.mode, "RGB")
                buffer = io.BytesIO()
                create_artwork(variant).save(buffer, format="PNG", optimize=False, compress_level=9)
                self.assertEqual(path.read_bytes(), buffer.getvalue())

    def test_safe_edges(self):
        """Artwork must not bleed onto the carrier trim or exceed the safe face."""
        petrol = ImageColor.getrgb("#102C3C")
        for variant in VARIANTS:
            with self.subTest(variant=variant):
                image = Image.open(OUTPUT / f"{variant}_albedo.png")
                for bounds in [(0, 0, 2000, 20), (0, 380, 2000, 400),
                               (0, 0, 20, 400), (1980, 0, 2000, 400)]:
                    self.assertEqual(set(image.crop(bounds).get_flattened_data()), {petrol})

    def test_independent_motif_pixels(self):
        """Check tag hole, bowl/steam negative space, disc and separated right block."""
        expectations = {
            "loose_change": [((80, 200), "#F54BBA"), ((695, 200), "#102C3C"),
                             ((840, 200), "#F54BBA"), ((860, 60), "#102C3C")],
            "second_helping": [((50, 50), "#45DFE5"), ((441, 290), "#102C3C"),
                               ((441, 175), "#45DFE5"), ((267, 151), "#102C3C")],
            "side_b": [((240, 75), "#F6F1DC"), ((240, 200), "#102C3C"),
                       ((950, 200), "#102C3C"), ((1080, 200), "#F54BBA")],
        }
        for variant, probes in expectations.items():
            image = Image.open(OUTPUT / f"{variant}_albedo.png")
            for point, color in probes:
                self.assertEqual(image.getpixel(point), ImageColor.getrgb(color))

    def test_frontage_scale_colour_masses(self):
        """At 75x4, left-magenta, cyan-field and right-magenta remain distinct."""
        small = {v: Image.open(OUTPUT / f"{v}_albedo.png").resize(
            (75, 4), Image.Resampling.LANCZOS) for v in VARIANTS}
        # Literal broad-region expectations, deliberately not a copy of path geometry.
        self.assertGreater(small["loose_change"].getpixel((10, 2))[0], 180)
        self.assertLess(small["loose_change"].getpixel((65, 2))[0], 100)
        self.assertGreater(small["second_helping"].getpixel((65, 2))[1], 180)
        self.assertLess(small["second_helping"].getpixel((65, 2))[0], 110)
        self.assertGreater(small["side_b"].getpixel((65, 2))[0], 130)
        self.assertLess(small["side_b"].getpixel((35, 2))[0], 60)


if __name__ == "__main__":
    unittest.main()
