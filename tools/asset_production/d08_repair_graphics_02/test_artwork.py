"""Independent depot artwork contracts, separate from source/export and engine receipts."""
import io
import unittest

from PIL import Image, ImageChops

import author


class DepotArtworkTests(unittest.TestCase):
    """Protect the shared carrier aspect, rightward cue, family palette and weathered variants."""

    def test_committed_pngs_reproduce(self):
        """Both exact RGB outputs must reproduce without external images or fonts."""
        for variant in ("depot_right", "depot_right_patched"):
            image = author.create_artwork(variant)
            self.assertEqual(image.size, (1440, 390))
            self.assertEqual(image.mode, "RGB")
            stream = io.BytesIO()
            image.save(stream, format="PNG", compress_level=9)
            self.assertEqual(stream.getvalue(),
                             (author.OUTPUT / f"{variant}_albedo.png").read_bytes())

    def test_border_and_family_palette(self):
        """Use independent RGB and position expectations for the faded service-sign colours."""
        image = author.create_artwork()
        for point in ((5, 5), (1435, 5), (5, 385), (1435, 385)):
            self.assertEqual(image.getpixel(point), (38, 63, 67))
        self.assertEqual(image.getpixel((970, 180)), (220, 174, 102))
        self.assertEqual(image.getpixel((790, 84)), (120, 172, 169))
        self.assertEqual(image.getpixel((80, 26)), (38, 63, 67))
        self.assertEqual(image.getpixel((250, 22)), (182, 167, 126))

    def test_arrow_points_right_without_mirroring(self):
        """The upper/lower arrowhead lobes are on the right; the left has only a shaft."""
        for variant in ("depot_right", "depot_right_patched"):
            image = author.create_artwork(variant)
            for point in ((1100, 192), (1300, 192), (1240, 130), (1240, 255)):
                self.assertEqual(image.getpixel(point), (38, 63, 67))
            for point in ((1100, 130), (1100, 255), (1355, 192)):
                self.assertEqual(image.getpixel(point), (233, 223, 193))

    def test_patch_preserves_primary_direction_and_copy(self):
        """Repaint stays below the depot/cyan line and left of the complete arrow field."""
        base = author.create_artwork()
        patched = author.create_artwork("depot_right_patched")
        bounds = ImageChops.difference(base, patched).getbbox()
        self.assertIsNotNone(bounds)
        self.assertGreaterEqual(bounds[1], 229)
        self.assertLessEqual(bounds[2], 971)
        self.assertLessEqual(bounds[3], 357)
        self.assertEqual(patched.getpixel((900, 290)), (220, 205, 165))
        self.assertEqual(base.getpixel((900, 290)), (38, 63, 67))

    def test_front_facing_mip_proxy_preserves_arrow_contrast(self):
        """A 96x26 face-on proxy retains the arrow, not a claim of overhead readability."""
        image = author.create_artwork().resize((96, 26), Image.Resampling.LANCZOS)
        self.assertGreater(sum(image.getpixel((72, 8))) - sum(image.getpixel((86, 12))), 250)

    def test_unknown_variant_rejected(self):
        """Invalid variant names must not silently generate a wrong directional face."""
        with self.assertRaises(ValueError):
            author.create_artwork("depot_left")


if __name__ == "__main__":
    unittest.main()
