"""Independent contracts for original repair artwork, separate from rendering receipts."""
import io
import unittest

from PIL import Image, ImageChops

import author


class RepairArtworkTests(unittest.TestCase):
    """Protect deliverable dimensions, shared service cue and deterministic paint variants."""

    def test_committed_pngs_reproduce(self):
        """Both runtime textures must reproduce exactly without external assets or fonts."""
        for variant in ("fixed_enough", "fixed_enough_patched"):
            image = author.create_artwork(variant)
            self.assertEqual(image.size, (1220, 820))
            self.assertEqual(image.mode, "RGB")
            stream = io.BytesIO()
            image.save(stream, format="PNG", compress_level=9)
            self.assertEqual(stream.getvalue(),
                             (author.OUTPUT / f"{variant}_albedo.png").read_bytes())

    def test_face_border_and_service_badge(self):
        """The clipped edge stays dark while independent spanner/badge samples retain contrast."""
        image = Image.open(author.OUTPUT / "fixed_enough_albedo.png")
        petrol = (38, 63, 67)
        ivory = (233, 223, 193)
        amber = (220, 174, 102)
        for point in ((5, 5), (1215, 5), (5, 815), (1215, 815)):
            self.assertEqual(image.getpixel(point), petrol)
        self.assertEqual(image.getpixel((215, 310)), petrol)
        self.assertEqual(image.getpixel((130, 245)), ivory)
        self.assertEqual(image.getpixel((410, 100)), amber)
        self.assertEqual(image.getpixel((130, 515)), (120, 172, 169))

    def test_patch_does_not_damage_shop_identity(self):
        """Finish changes stay below the badge, primary copy and cyan service bars."""
        base = Image.open(author.OUTPUT / "fixed_enough_albedo.png")
        patched = Image.open(author.OUTPUT / "fixed_enough_patched_albedo.png")
        bounds = ImageChops.difference(base, patched).getbbox()
        self.assertIsNotNone(bounds)
        self.assertGreaterEqual(bounds[1], 570)
        self.assertLessEqual(bounds[3], 770)
        self.assertEqual(patched.getpixel((1100, 700)), (220, 205, 165))
        self.assertEqual(base.getpixel((1100, 700)), (38, 63, 67))

    def test_front_facing_mip_proxy_preserves_spanner_contrast(self):
        """At 61x41 the service badge remains distinct; this is not an overhead copy test."""
        image = Image.open(author.OUTPUT / "fixed_enough_albedo.png")
        small = image.resize((61, 41), Image.Resampling.LANCZOS)
        dark = small.getpixel((10, 15))
        light = small.getpixel((6, 12))
        self.assertGreater(sum(light) - sum(dark), 250)

    def test_unknown_variant_rejected(self):
        """Misspelled names must not silently author the wrong shop finish."""
        with self.assertRaises(ValueError):
            author.create_artwork("unknown")


if __name__ == "__main__":
    unittest.main()
