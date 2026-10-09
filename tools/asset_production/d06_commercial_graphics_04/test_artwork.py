"""Protect the passage face's usable border, direction and deterministic original artwork."""
import io
import unittest

from PIL import Image, ImageColor

import author


class PassageArtworkTests(unittest.TestCase):
    """Check independent pixel landmarks rather than reconstructing the drawing recipe."""

    @classmethod
    def setUpClass(cls):
        """Render once for all appearance assertions."""
        cls.image = author.create_artwork()

    def test_texture_and_reproduction(self):
        """Require the committed opaque face to exactly reproduce from the author script."""
        self.assertEqual(self.image.size, (1220, 820))
        self.assertEqual(self.image.mode, "RGB")
        stream = io.BytesIO()
        self.image.save(stream, format="PNG", optimize=False, compress_level=9)
        self.assertEqual(stream.getvalue(), author.OUTPUT.read_bytes())

    def test_safe_margins(self):
        """Keep all copy within the inherited 1.14-by-.74-m safe rectangle."""
        petrol = ImageColor.getrgb("#102C3C")
        for bounds in [(0, 0, 1220, 40), (0, 780, 1220, 820),
                       (0, 0, 40, 820), (1180, 0, 1220, 820)]:
            colors = self.image.crop(bounds).getcolors(1220 * 820)
            self.assertEqual(len(colors), 1)
            self.assertEqual(colors[0][1], petrol)

    def test_direction_and_open_door(self):
        """The ivory point faces right; the cyan door retains a dark open gap."""
        for point, hex_color in {
            (230, 300): "#45DFE5", (390, 350): "#102C3C",
            (600, 350): "#F6F1DC", (1030, 350): "#F6F1DC",
            (600, 235): "#102C3C", (880, 235): "#F6F1DC",
            (300, 573): "#F54BBA", (1140, 350): "#102C3C",
        }.items():
            self.assertEqual(self.image.getpixel(point), ImageColor.getrgb(hex_color), point)

    def test_small_face_symbol_contrast(self):
        """Check low-resolution doorway/arrow separation, not overhead gameplay visibility."""
        small = self.image.resize((61, 41), Image.Resampling.LANCZOS)
        cyan = small.getpixel((11, 15))
        gap = small.getpixel((19, 17))
        arrow = small.getpixel((32, 17))
        self.assertGreater(cyan[1] - cyan[0], 100)
        self.assertLess(max(gap), 80)
        self.assertGreater(min(arrow), 180)


if __name__ == "__main__":
    unittest.main()
