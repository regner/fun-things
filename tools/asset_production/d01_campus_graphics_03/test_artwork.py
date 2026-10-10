"""Independent runtime-pixel and source-link checks for the campus route-arrow set."""
import io
import unittest

from PIL import Image, ImageChops

import author


class RouteArrowArtworkTests(unittest.TestCase):
    """Protect direction silhouettes, common identity, carrier bounds and PNG reproducibility."""

    def setUp(self):
        """Load actual runtime outputs so expectations do not simply rerun drawing formulas."""
        self.images = {v: Image.open(author.OUTPUT_DIR / f"route_{v}_albedo.png")
                       for v in ("left", "ahead", "right")}

    def tearDown(self):
        """Close every loaded image between tests."""
        for image in self.images.values():
            image.close()

    def test_route_arrow_dimensions_and_opacity(self):
        """All three opaque albedos fit the carrier's exact 48:13 image domain."""
        for image in self.images.values():
            self.assertEqual(image.size, (1440, 390))
            self.assertEqual(image.mode, "RGB")

    def test_route_arrow_reproduction(self):
        """Each original PNG must reproduce byte-for-byte without a system font."""
        for variant in self.images:
            output = io.BytesIO()
            author.create_artwork(variant).save(output, format="PNG", compress_level=9)
            self.assertEqual(output.getvalue(),
                             (author.OUTPUT_DIR / f"route_{variant}_albedo.png").read_bytes())

    def test_route_arrow_safe_margins(self):
        """All authored ink stays inside the hardware's independently fixed safe rectangle."""
        background = Image.new("RGB", (1440, 390), "#233F4A")
        for image in self.images.values():
            left, top, right, bottom = ImageChops.difference(image, background).getbbox()
            self.assertGreaterEqual(left, 30)
            self.assertGreaterEqual(top, 30)
            self.assertLessEqual(right, 1410)
            self.assertLessEqual(bottom, 360)

    def test_route_arrow_directions_and_reduced_silhouettes(self):
        """Literal interior samples distinguish left/right/ahead even after 10x reduction."""
        # Tips and shoulders differ, while each direction retains a connected broad stem.
        expected = {
            "left": {(110, 195): True, (270, 125): False, (200, 125): True,
                     (350, 195): True, (235, 65): False},
            "right": {(360, 195): True, (270, 125): True, (200, 125): False,
                      (120, 195): True, (235, 65): False},
            "ahead": {(235, 65): True, (235, 300): True, (150, 165): True,
                      (110, 195): False, (360, 195): False},
        }
        for variant, samples in expected.items():
            for point, mint in samples.items():
                color = (163, 220, 197) if mint else (35, 63, 74)
                self.assertEqual(self.images[variant].getpixel(point), color)
            reduced = self.images[variant].resize((144, 39), Image.Resampling.LANCZOS)
            point = {"left": (13, 19), "right": (34, 19), "ahead": (23, 9)}[variant]
            rgb = reduced.getpixel(point)
            self.assertLess(max(abs(a-b) for a, b in zip(rgb, (163, 220, 197))), 20)

    def test_route_arrow_common_identity_is_not_mirrored(self):
        """Only the arrow changes; all copy and the exact campus mark remain identical."""
        common = self.images["ahead"].crop((420, 0, 1440, 390))
        for image in self.images.values():
            self.assertIsNone(ImageChops.difference(
                common, image.crop((420, 0, 1440, 390))).getbbox())
            self.assertEqual(image.getpixel((1303, 194)), (255, 192, 90))
            self.assertEqual(image.getpixel((1250, 238)), (163, 220, 197))
        self.assertIs(author.PALETTE, author.family.family.PALETTE)

    def test_route_arrow_linked_prefabs_without_duplicate_geometry(self):
        """Three independently placeable faces inherit the unchanged collision-bearing support."""
        for prefix in ("art/models/environment", "art/source/models/environment"):
            self.assertFalse((author.ROOT / prefix / author.NID).exists())
        for variant in self.images:
            suffix = "" if variant == "ahead" else "_"+variant
            scene = (author.ROOT / f"scenes/prefabs/environment/{author.NID}{suffix}.tscn").read_text()
            self.assertIn("city_sign_supports_02.tscn", scene)
            self.assertIn(f"route_{variant}.tres", scene)
            self.assertEqual(scene.count("surface_material_override/0"), 1)
            self.assertNotIn("ArrayMesh", scene)

    def test_route_arrow_invalid_variant_is_rejected(self):
        """A typo must not silently produce a different direction."""
        with self.assertRaises(ValueError):
            author.create_artwork("back")


if __name__ == "__main__":
    unittest.main(verbosity=2)
