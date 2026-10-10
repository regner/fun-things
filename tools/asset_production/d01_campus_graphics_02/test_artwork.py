"""Independent acceptance checks for the entry-panel image and inherited family interface."""
import io
import unittest

from PIL import Image, ImageChops

import author


class EntryPanelArtworkTests(unittest.TestCase):
    """Protect the supplied carrier aspect, safe margins, family mark and reproducibility."""

    def setUp(self):
        """Read actual committed runtime pixels, not a second invocation of drawing formulas."""
        self.image = Image.open(author.OUTPUT)

    def tearDown(self):
        """Release the runtime image after each independent expectation."""
        self.image.close()

    def test_entry_panel_size_and_opaque_color(self):
        """The low-panel carrier requires an opaque 48:13 albedo domain."""
        self.assertEqual(self.image.size, (1440, 390))
        self.assertEqual(self.image.mode, "RGB")

    def test_entry_panel_png_is_reproducible(self):
        """The complete PNG byte stream must regenerate without external font dependencies."""
        data = io.BytesIO()
        author.create_artwork().save(data, format="PNG", compress_level=9)
        self.assertEqual(data.getvalue(), author.OUTPUT.read_bytes())

    def test_entry_panel_safe_copy_rectangle(self):
        """All visible ink must respect the hardware's literal 30-pixel safe inset."""
        background = Image.new("RGB", (1440, 390), "#233F4A")
        bounds = ImageChops.difference(self.image, background).getbbox()
        self.assertIsNotNone(bounds)
        left, top, right, bottom = bounds
        self.assertGreaterEqual(left, 30)
        self.assertGreaterEqual(top, 30)
        self.assertLessEqual(right, 1410)
        self.assertLessEqual(bottom, 360)

    def test_entry_panel_crest_and_hierarchy_colors(self):
        """Independent pixels protect the warm point, mint book and slate breathing room."""
        for point, expected in {
            (152, 80): (255, 192, 90),
            (80, 150): (163, 220, 197),
            (220, 150): (163, 220, 197),
            (152, 170): (35, 63, 74),
            (30, 30): (35, 63, 74),
        }.items():
            self.assertEqual(self.image.getpixel(point), expected)
        # Both primary title rows must have substantial ink, not only footer copy.
        for region, color in [((330, 45, 950, 128), (246, 241, 220)),
                              ((330, 140, 1300, 250), (163, 220, 197))]:
            crop = self.image.crop(region)
            # Count near-color ink as well as exact pixels: supersampling intentionally
            # antialiases the narrow title strokes, without changing their hierarchy.
            ink = sum(count for count, rgb in crop.getcolors(crop.width*crop.height)
                      if max(abs(a-b) for a, b in zip(rgb, color)) < 20)
            self.assertGreater(ink / (crop.width*crop.height), 0.10)

    def test_entry_panel_reuses_family_mark(self):
        """The palette and continuous glyph paths are linked rather than redefined locally."""
        self.assertIs(author.PALETTE, author.family.PALETTE)
        self.assertTrue(issubclass(author.Canvas, author.family.Canvas))
        self.assertEqual(author.PALETTE["mint"], "#A3DCC5")
        self.assertEqual(author.PALETTE["amber"], "#FFC05A")

    def test_entry_panel_has_no_duplicate_carrier(self):
        """Artwork reuse forbids a private model/source directory for unchanged hardware."""
        for prefix in ("art/models/environment", "art/source/models/environment"):
            self.assertFalse((author.ROOT / prefix / author.NID).exists())
        scene = (author.ROOT / "scenes/prefabs/environment/d01_campus_graphics_02.tscn").read_text()
        self.assertIn("city_sign_supports_02.tscn", scene)
        self.assertEqual(scene.count("surface_material_override/0"), 1)
        self.assertNotIn("ArrayMesh", scene)


if __name__ == "__main__":
    unittest.main(verbosity=2)
