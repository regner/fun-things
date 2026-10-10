"""Independent expectations for the delivered service-warning textures and finish variants."""
import io
import unittest

from PIL import Image, ImageChops

import author


class ServiceWarningArtworkTests(unittest.TestCase):
    """Protect dimensions, warning contrast, unchanged identity and deterministic authorship."""

    def test_committed_pngs_reproduce(self):
        """Both committed opaque textures must reproduce without external fonts or images."""
        for variant in ("service_warning", "service_warning_patched"):
            image = author.create_artwork(variant)
            self.assertEqual(image.size, (1220, 820))
            self.assertEqual(image.mode, "RGB")
            stream = io.BytesIO()
            image.save(stream, format="PNG", compress_level=9)
            self.assertEqual(stream.getvalue(),
                             (author.OUTPUT / f"{variant}_albedo.png").read_bytes())

    def test_family_palette_and_border(self):
        """Keep the dark clipping border, sun-faded amber field and restrained cyan signature."""
        image = Image.open(author.OUTPUT / "service_warning_albedo.png")
        for point in ((5, 5), (1215, 5), (5, 815), (1215, 815)):
            self.assertEqual(image.getpixel(point), (38, 63, 67))
        self.assertEqual(image.getpixel((440, 90)), (220, 174, 102))
        self.assertEqual(image.getpixel((135, 510)), (120, 172, 169))
        self.assertEqual(image.getpixel((100, 49)), (182, 167, 126))

    def test_warning_symbol_has_separated_exclamation(self):
        """Independent interior samples require a dark bar and dot with a light separating gap."""
        for variant in ("service_warning", "service_warning_patched"):
            image = Image.open(author.OUTPUT / f"{variant}_albedo.png")
            self.assertEqual(image.getpixel((230, 285)), (38, 63, 67))
            self.assertEqual(image.getpixel((230, 355)), (233, 223, 193))
            self.assertEqual(image.getpixel((230, 380)), (38, 63, 67))
            self.assertEqual(image.getpixel((175, 340)), (233, 223, 193))
            self.assertEqual(image.getpixel((110, 428)), (38, 63, 67))

    def test_patch_leaves_warning_and_primary_copy_identical(self):
        """Weathering variants may change only the lower repaint, not the service warning."""
        base = Image.open(author.OUTPUT / "service_warning_albedo.png")
        patched = Image.open(author.OUTPUT / "service_warning_patched_albedo.png")
        bounds = ImageChops.difference(base, patched).getbbox()
        self.assertIsNotNone(bounds)
        self.assertGreaterEqual(bounds[1], 577)
        self.assertLessEqual(bounds[3], 770)
        self.assertEqual(patched.getpixel((1050, 700)), (220, 205, 165))
        self.assertEqual(base.getpixel((1050, 700)), (38, 63, 67))

    def test_repaint_preserves_lower_wording(self):
        """The lower text silhouette stays unchanged when its light/dark paint is inverted."""
        base = author.create_artwork("service_warning").crop((220, 635, 920, 710))
        patched = author.create_artwork("service_warning_patched").crop((220, 635, 920, 710))
        # High-contrast interior pixels identify the lettering independent of paint colour.
        base_mask = base.convert("L").point(lambda value: 255 if value > 130 else 0)
        patch_mask = patched.convert("L").point(lambda value: 255 if value < 130 else 0)
        changed = ImageChops.difference(base_mask, patch_mask).histogram()[255]
        self.assertLess(changed, 90)  # Only antialiased edge threshold differences are permitted.

    def test_front_facing_mip_proxy_preserves_warning_contrast(self):
        """At 61x41 front-facing, the triangle field contrasts; this is not an overhead test."""
        image = Image.open(author.OUTPUT / "service_warning_albedo.png")
        small = image.resize((61, 41), Image.Resampling.LANCZOS)
        dark = small.getpixel((11, 14))
        light = small.getpixel((8, 17))
        self.assertGreater(sum(light) - sum(dark), 250)

    def test_unknown_variant_rejected(self):
        """Misspelled variant names must fail rather than silently selecting another finish."""
        with self.assertRaises(ValueError):
            author.create_artwork("unknown")


if __name__ == "__main__":
    unittest.main()
