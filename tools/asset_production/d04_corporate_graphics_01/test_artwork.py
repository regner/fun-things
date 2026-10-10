"""Independent panel artwork expectations: aspect, hierarchy, margins and reproducibility."""
import hashlib
import io
from pathlib import Path
import unittest

from PIL import Image
import artwork

PNG = Path(__file__).resolve().parents[3] / (
    "art/textures/environment/d04_corporate_graphics_01/tomorrow_albedo.png")


class CorporateArtworkTests(unittest.TestCase):
    """Protect the original artwork's output contract, not its drawing implementation."""

    def test_face_aspect_and_opacity(self):
        """The 5.36 by 3.76 m face uses exactly 300 pixels/metre in RGB."""
        with Image.open(PNG) as image:
            self.assertEqual(image.size, (1608, 1128))
            self.assertEqual(image.mode, "RGB")

    def test_safe_margins(self):
        """A 60 px perimeter keeps all important marks clear of the bevel and frame."""
        with Image.open(PNG) as image:
            field = (21, 38, 61)
            for box in [(0, 0, 1608, 60), (0, 1068, 1608, 1128),
                        (0, 0, 60, 1128), (1548, 0, 1608, 1128)]:
                self.assertEqual(set(image.crop(box).get_flattened_data()), {field})

    def test_restrained_palette_and_emblem(self):
        """Quiet dark area dominates; rare magenta stays a single tiny appointment marker."""
        with Image.open(PNG) as image:
            pixels = list(image.get_flattened_data())
            self.assertGreater(pixels.count((21, 38, 61))/len(pixels), .8)
            self.assertLess(pixels.count((235, 98, 183))/len(pixels), .003)
            self.assertEqual(image.getpixel((200, 138)), (87, 217, 229))
            self.assertEqual(image.getpixel((330, 330)), (235, 98, 183))
            self.assertEqual(image.getpixel((330, 385)), (21, 38, 61))

    def test_exact_reauthor(self):
        """A fresh render of the committed Python recipe reproduces the PNG byte-for-byte."""
        output = io.BytesIO()
        artwork.create_artwork().save(output, format="PNG", compress_level=9)
        self.assertEqual(hashlib.sha256(output.getvalue()).digest(),
                         hashlib.sha256(PNG.read_bytes()).digest())


if __name__ == "__main__":
    unittest.main()
