"""Independent pixel, layout and reproducibility checks for the container-ID face set."""
import io
import unittest

from PIL import ImageColor

import author


class ContainerArtworkTests(unittest.TestCase):
    """Protect literal family colors, margins and different decorative identities."""

    def test_format_and_margin(self):
        """Every face is opaque, correctly proportioned and safely inset at its edges."""
        for variant in ("long", "short"):
            image = author.create_artwork(variant)
            self.assertEqual(image.size, (1400, 460))
            self.assertEqual(image.mode, "RGB")
            field = (20, 51, 68)
            for box in ((0, 0, 1400, 30), (0, 430, 1400, 460),
                        (0, 0, 30, 460), (1370, 0, 1400, 460)):
                self.assertEqual(image.crop(box).getextrema(), tuple((v, v) for v in field))
            quiet_pixels = sum(pixel == field for pixel in image.get_flattened_data())
            self.assertGreater(quiet_pixels / (1400*460), .65)

    def test_parcel_clock_and_separated_clusters(self):
        """Check independent landmarks, safe gutter and restrained steel-bar grouping."""
        image = author.create_artwork("long")
        for point, color in [((80, 215), "#FFC05A"), ((205, 98), "#143344"),
                             ((205, 220), "#FFC05A"), ((155, 250), "#143344"),
                             ((400, 230), "#143344"), ((450, 220), "#F6F1DC"),
                             ((1254, 100), "#85929D"), ((1233, 100), "#143344")]:
            self.assertEqual(image.getpixel(point), ImageColor.getrgb(color))

    def test_variants_preserve_family_and_differ_only_in_id(self):
        """Both variants retain identical symbol/header while their primary ID differs."""
        long = author.create_artwork("long")
        short = author.create_artwork("short")
        self.assertEqual(long.crop((0, 0, 400, 460)).tobytes(),
                         short.crop((0, 0, 400, 460)).tobytes())
        self.assertEqual(long.crop((400, 0, 1400, 150)).tobytes(),
                         short.crop((400, 0, 1400, 150)).tobytes())
        self.assertNotEqual(long.crop((700, 150, 1400, 400)).tobytes(),
                            short.crop((700, 150, 1400, 400)).tobytes())

    def test_committed_png_bytes_reproduce(self):
        """Fresh authoring must reproduce both actual runtime PNG byte streams."""
        for variant in ("long", "short"):
            output = io.BytesIO()
            author.create_artwork(variant).save(output, format="PNG", compress_level=9)
            path = author.ROOT / f"art/textures/environment/{author.NID}/container_id_{variant}_albedo.png"
            self.assertEqual(output.getvalue(), path.read_bytes())


if __name__ == "__main__":
    unittest.main()
