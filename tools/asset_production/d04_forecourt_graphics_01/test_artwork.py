"""Independent broad-band artwork expectations, including low-resolution readability."""
import io
import unittest

from PIL import Image, ImageColor

import artwork


class BroadPavingBandTests(unittest.TestCase):
    """Protect the fixed ground footprint and sparse, non-directional graphic hierarchy."""

    def test_opaque_aspect(self):
        """Keep 64px/m equal density over the documented 24 x 4 m footprint."""
        with Image.open(artwork.TEXTURE) as image:
            self.assertEqual(image.mode, "RGB")
            self.assertEqual(image.size, (1536, 256))

    def test_band_and_shoulders(self):
        """Independent pixel probes require 1.25m shoulders and a 1.5m uninterrupted band."""
        with Image.open(artwork.TEXTURE) as image:
            for x in (0, 400, 800, 1535):
                for y in (0, 40, 75, 180, 215, 255):
                    self.assertEqual(image.getpixel((x, y)), (197, 203, 202))
                for y in (85, 100, 128, 160, 170):
                    self.assertEqual(image.getpixel((x, y)), (133, 146, 157))

    def test_single_sparse_cyan_inset(self):
        """Keep the corporate cyan under 0.4% and forbid text, magenta or competing signals."""
        with Image.open(artwork.TEXTURE) as image:
            counts = {color: count for count, color in image.getcolors(image.width * image.height)}
            self.assertEqual(image.getpixel((1390, 128)), (87, 217, 229))
            cyan = counts[ImageColor.getrgb("#57D9E5")]
            self.assertGreater(cyan, 500)
            self.assertLess(cyan / (1536 * 256), .004)
            self.assertNotIn((235, 98, 183), counts)
            pale = counts[(197, 203, 202)] / (1536 * 256)
            self.assertGreater(pale, .60)

    def test_gameplay_minification(self):
        """Broad neutral band must remain distinct at approximately 47m camera pixel density."""
        with Image.open(artwork.TEXTURE) as image:
            small = image.resize((480, 80), Image.Resampling.LANCZOS)
            shoulder, centre = small.getpixel((200, 15)), small.getpixel((200, 40))
            self.assertGreater(sum(shoulder) - sum(centre), 140)

    def test_png_byte_reproduction(self):
        """The committed PNG must be exactly regenerated from the original recipe."""
        output = io.BytesIO()
        artwork.draw().save(output, format="PNG", compress_level=9)
        self.assertEqual(output.getvalue(), artwork.TEXTURE.read_bytes())


if __name__ == "__main__":
    unittest.main()
