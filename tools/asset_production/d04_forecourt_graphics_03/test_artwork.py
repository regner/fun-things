"""Independent quiet-emblem footprint, negative-space and minification expectations."""
import io
import unittest

from PIL import Image

import artwork


class QuietInsetEmblemTests(unittest.TestCase):
    """Protect the compact offset-corner hierarchy without copying the drawing recipe."""

    def test_opaque_aspect(self):
        """Keep equal 64 px/m density over the provisional 8 x 8 m footprint."""
        with Image.open(artwork.TEXTURE) as image:
            self.assertEqual(image.mode, "RGB")
            self.assertEqual(image.size, (512, 512))

    def test_offset_corners_and_blank_margins(self):
        """Require two distinct open corners, not a closed ring or long entry-axis marking."""
        with Image.open(artwork.TEXTURE) as image:
            for point in [(30, 256), (480, 256), (256, 30), (256, 480),
                          (256, 256), (128, 380), (350, 128), (208, 350)]:
                self.assertEqual(image.getpixel(point), (197, 203, 202))
            for point in [(128, 128), (128, 300), (300, 128), (208, 208),
                          (400, 208), (400, 390)]:
                self.assertEqual(image.getpixel(point), (133, 146, 157))

    def test_sparse_palette_and_inset_accent(self):
        """Keep over 90 percent pale ground and under 0.3 percent cyan, with no magenta."""
        with Image.open(artwork.TEXTURE) as image:
            counts = {color: count for count, color in image.getcolors(image.width * image.height)}
            total = image.width * image.height
            self.assertEqual(image.getpixel((304, 306)), (87, 217, 229))
            self.assertGreater(counts[(197, 203, 202)] / total, .90)
            self.assertLess(counts[(87, 217, 229)] / total, .003)
            self.assertGreater(counts[(87, 217, 229)], 200)
            self.assertNotIn((235, 98, 183), counts)

    def test_gameplay_minification(self):
        """Both slate corner strokes must survive the approximate 47m pixel density."""
        with Image.open(artwork.TEXTURE) as image:
            small = image.resize((160, 160), Image.Resampling.LANCZOS)
            centre = small.getpixel((80, 80))
            for point in [(40, 80), (80, 40), (125, 100), (80, 65)]:
                self.assertGreater(sum(centre) - sum(small.getpixel(point)), 140)
            self.assertGreater(sum(small.getpixel((80, 145))), 580)

    def test_png_byte_reproduction(self):
        """The committed PNG must exactly regenerate from the original recipe."""
        output = io.BytesIO()
        artwork.draw().save(output, format="PNG", compress_level=9)
        self.assertEqual(output.getvalue(), artwork.TEXTURE.read_bytes())


if __name__ == "__main__":
    unittest.main()
