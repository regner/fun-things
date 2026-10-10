"""Independent contract samples for the corner-shop fascia and its exact reproduction."""
import io
import unittest

from PIL import Image, ImageChops

import author


class CornerCupboardArtworkTests(unittest.TestCase):
    """Test delivered pixels, safe content and the original grocery motif."""

    def test_exact_reproduction(self):
        """Require deterministic committed bytes and the carrier's literal 5:1 aspect."""
        image = author.create_artwork()
        self.assertEqual(image.size, (2000, 400))
        self.assertEqual(image.mode, "RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", compress_level=9)
        self.assertEqual(buffer.getvalue(), author.OUTPUT.read_bytes())

    def test_safe_margin_and_quiet_field(self):
        """Protect all 20 outer texels and keep the majority of the face unprinted ivory."""
        image = Image.open(author.OUTPUT).convert("RGB")
        ivory = (246, 241, 220)
        for box in ((0, 0, 2000, 20), (0, 380, 2000, 400),
                    (0, 0, 20, 400), (1980, 0, 2000, 400)):
            margin = image.crop(box)
            self.assertIsNone(ImageChops.difference(
                margin, Image.new("RGB", margin.size, ivory)).getbbox())
        self.assertGreater(sum(pixel == ivory for pixel in image.get_flattened_data()), 600000)

    def test_groceries_and_family_palette(self):
        """Sample independently selected bottle, loaf, bag and handle pixels."""
        image = Image.open(author.OUTPUT)
        self.assertEqual(image.getpixel((165, 100)), (82, 109, 134))
        self.assertEqual(image.getpixel((280, 140)), (99, 81, 104))
        self.assertEqual(image.getpixel((210, 240)), (99, 81, 104))
        self.assertEqual(image.getpixel((175, 178)), (246, 241, 220))
        # The four-pixel divider is filtered; allow the expected small ivory edge contribution.
        for actual, expected in zip(image.getpixel((1200, 242)), (82, 109, 134)):
            self.assertLessEqual(abs(actual - expected), 6)

    def test_small_motif_contrast_proxy(self):
        """Retain a broad grocery silhouette at 1/8 texture size, not gameplay acceptance."""
        image = Image.open(author.OUTPUT).resize((250, 50), Image.Resampling.LANCZOS)
        bag = image.getpixel((26, 30))
        field = image.getpixel((45, 30))
        self.assertLess(max(bag), 125)
        self.assertGreater(min(field), 210)


if __name__ == "__main__":
    unittest.main()
