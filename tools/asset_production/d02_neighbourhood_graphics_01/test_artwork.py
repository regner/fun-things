"""Independent artwork contract expectations through the production drawing API."""
import io
import unittest
from collections import Counter

from PIL import Image

from author import OUTPUT, create_artwork


class WatchArtworkTests(unittest.TestCase):
    """Protect opaque deterministic output, safe margins and quiet residential colour masses."""

    def test_runtime_png_matches_recipe(self):
        """The delivered texture must equal a fresh production recipe result byte-for-byte."""
        image = create_artwork()
        self.assertEqual(image.mode, "RGB")
        self.assertEqual(image.size, (1220, 820))
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", compress_level=9)
        self.assertEqual(buffer.getvalue(), OUTPUT.read_bytes())

    def test_copy_stays_inside_hardware_safe_rectangle(self):
        """Forty texels of uninterrupted ivory protect the carrier's rounded crop boundary."""
        image = create_artwork()
        ivory = (246, 241, 220)
        for bounds in [(0, 0, 1220, 40), (0, 780, 1220, 820),
                       (0, 0, 40, 820), (1180, 0, 1220, 820)]:
            self.assertEqual(set(image.crop(bounds).get_flattened_data()), {ivory})

    def test_domestic_palette_and_curtain_emblem(self):
        """Literal sample points protect the non-text motif and broad quiet field."""
        image = create_artwork()
        ivory, plum, blue = (246, 241, 220), (99, 81, 104), (82, 109, 134)
        self.assertEqual(image.getpixel((171, 220)), plum)
        self.assertEqual(image.getpixel((358, 220)), plum)
        self.assertEqual(image.getpixel((265, 360)), blue)
        self.assertEqual(image.getpixel((245, 365)), ivory)
        self.assertEqual(image.getpixel((265, 477)), blue)
        counts = Counter(image.get_flattened_data())
        self.assertGreater(counts[ivory] / (1220 * 820), 0.75)
        self.assertGreater(counts[plum], counts[blue])

    def test_motif_survives_texture_downsample(self):
        """The curtain area remains darker than whitespace; this is not overhead readability."""
        image = create_artwork().resize((61, 41), Image.Resampling.LANCZOS).convert("L")
        self.assertLess(image.getpixel((8, 11)), image.getpixel((22, 24)) - 70)


if __name__ == "__main__":
    unittest.main()
