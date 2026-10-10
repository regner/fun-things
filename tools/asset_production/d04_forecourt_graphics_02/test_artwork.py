"""Independent entry-axis footprint, negative-space and minification expectations."""
import io
import unittest

from PIL import Image

import artwork


class EntryAxisMotifTests(unittest.TestCase):
    """Protect the sparse paired-axis hierarchy without duplicating the drawing recipe."""

    def test_opaque_aspect(self):
        """Keep 64 px/m equal density over the provisional 8 x 16 m footprint."""
        with Image.open(artwork.TEXTURE) as image:
            self.assertEqual(image.mode, "RGB")
            self.assertEqual(image.size, (512, 1024))

    def test_open_axis_and_blank_margins(self):
        """Require two longitudinal strokes, inward north shoulders and an open pale centre."""
        with Image.open(artwork.TEXTURE) as image:
            for point in [(20, 512), (490, 512), (256, 512), (256, 140),
                          (110, 40), (400, 980), (170, 860), (340, 860)]:
                self.assertEqual(image.getpixel(point), (197, 203, 202))
            for point in [(110, 300), (400, 300), (110, 860), (400, 860),
                          (170, 140), (340, 140)]:
                self.assertEqual(image.getpixel(point), (133, 146, 157))

    def test_sparse_palette_and_north_accent(self):
        """Keep over 88 percent pale ground and under 0.3 percent cyan, with no magenta."""
        with Image.open(artwork.TEXTURE) as image:
            counts = {color: count for count, color in image.getcolors(image.width * image.height)}
            total = image.width * image.height
            self.assertEqual(image.getpixel((256, 224)), (87, 217, 229))
            self.assertEqual(image.getpixel((256, 800)), (197, 203, 202))
            self.assertGreater(counts[(197, 203, 202)] / total, .88)
            self.assertLess(counts[(87, 217, 229)] / total, .003)
            self.assertGreater(counts[(87, 217, 229)], 500)
            self.assertNotIn((235, 98, 183), counts)

    def test_gameplay_minification(self):
        """Both broad slate strokes must remain distinct at the approximate 47m pixel density."""
        with Image.open(artwork.TEXTURE) as image:
            small = image.resize((160, 320), Image.Resampling.LANCZOS)
            centre = small.getpixel((80, 160))
            for x in (35, 125):
                self.assertGreater(sum(centre) - sum(small.getpixel((x, 160))), 140)
            self.assertGreater(sum(small.getpixel((80, 40))), 580)

    def test_png_byte_reproduction(self):
        """The committed PNG must exactly regenerate from the original recipe."""
        output = io.BytesIO()
        artwork.draw().save(output, format="PNG", compress_level=9)
        self.assertEqual(output.getvalue(), artwork.TEXTURE.read_bytes())


if __name__ == "__main__":
    unittest.main()
