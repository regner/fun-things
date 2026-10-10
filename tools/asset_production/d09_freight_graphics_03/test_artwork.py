"""Independent layout expectations and byte reproduction for the loading-location artwork."""
import io
from pathlib import Path
import unittest

from PIL import Image, ImageColor

import author


class LoadingArtworkTests(unittest.TestCase):
    """Protect both carrier aspects, safety gutters, semantic clusters and deterministic source."""

    def test_format_quiet_field_and_safe_margins(self):
        """Both faces must remain opaque, correctly sized and safely inside rounded carrier edges."""
        field = ImageColor.getrgb("#143344")
        for variant, size, margin in [("wall", (1220, 820), 40), ("low", (1440, 390), 30)]:
            with Image.open(author.ROOT / f"art/textures/environment/{author.NID}/loading_{variant}_albedo.png") as image:
                self.assertEqual(image.size, size)
                self.assertEqual(image.mode, "RGB")
                width, height = size
                for box in [(0, 0, width, margin), (0, height-margin, width, height),
                            (0, 0, margin, height), (width-margin, 0, width, height)]:
                    self.assertEqual(set(image.crop(box).get_flattened_data()), {field})
                count = sum(pixel == field for pixel in image.get_flattened_data())
                self.assertGreater(count / (width*height), .60)

    def test_independent_parcel_clock_and_gutter_pixels(self):
        """Check ink, inset clock, hands, cargo bars and separation at hand-picked landmarks."""
        expected = {
            "wall": {"amber": [(120, 400), (245, 500)], "field": [(245, 350), (430, 480)],
                     "steel": [(1050, 720)], "ivory": [(540, 480)]},
            "low": {"amber": [(80, 160), (188, 200)], "field": [(188, 75), (360, 180)],
                    "steel": [(1260, 80)], "ivory": [(408, 210)]},
        }
        for variant, groups in expected.items():
            image = author.create_artwork(variant)
            for role, points in groups.items():
                for point in points:
                    self.assertEqual(image.getpixel(point), ImageColor.getrgb(author.PALETTE[role]),
                                     (variant, role, point))

    def test_family_and_native_aspects(self):
        """Use the existing family palette/outlines and distinct layouts, not stretched sibling art."""
        self.assertEqual(author.PALETTE, {"field": "#143344", "amber": "#FFC05A",
                                         "ivory": "#F6F1DC", "steel": "#85929D"})
        self.assertIs(author.GLYPHS["4"], author.FAMILY.GLYPHS["4"])
        wall, low = author.create_artwork("wall"), author.create_artwork("low")
        self.assertNotEqual(wall.resize(low.size).tobytes(), low.tobytes())

    def test_fresh_png_bytes(self):
        """The committed runtime files must reproduce exactly from the original vector recipe."""
        for variant in ("wall", "low"):
            fresh = io.BytesIO()
            author.create_artwork(variant).save(fresh, format="PNG", compress_level=9)
            path = Path(author.ROOT / f"art/textures/environment/{author.NID}/loading_{variant}_albedo.png")
            self.assertEqual(fresh.getvalue(), path.read_bytes())


if __name__ == "__main__":
    unittest.main()
