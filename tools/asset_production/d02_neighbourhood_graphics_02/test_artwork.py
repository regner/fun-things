"""Independent parking-notice expectations through the production artwork API."""
import io
import unittest
from collections import Counter

from PIL import Image

from author import OUTPUT, create_artwork


class ParkingRequestArtworkTests(unittest.TestCase):
    """Protect the delivered recipe, safe face crop and restrained one-car/one-bay motif."""

    def test_runtime_png_matches_recipe(self):
        """A fresh drawing must reproduce the complete runtime PNG exactly."""
        image = create_artwork()
        self.assertEqual(image.mode, "RGB")
        self.assertEqual(image.size, (1220, 820))
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", compress_level=9)
        self.assertEqual(buffer.getvalue(), OUTPUT.read_bytes())

    def test_copy_stays_inside_hardware_safe_rectangle(self):
        """Uninterrupted ivory on the outer forty texels protects rounded hardware cropping."""
        image = create_artwork()
        for bounds in [(0, 0, 1220, 40), (0, 780, 1220, 820),
                       (0, 0, 40, 820), (1180, 0, 1220, 820)]:
            self.assertEqual(set(image.crop(bounds).get_flattened_data()), {(246, 241, 220)})

    def test_one_car_inside_one_bay_and_quiet_palette(self):
        """Literal interior samples distinguish windows, car body, bay lines and whitespace."""
        image = create_artwork()
        ivory, plum, blue = (246, 241, 220), (99, 81, 104), (82, 109, 134)
        for point in [(268, 224), (268, 340), (268, 430)]:
            self.assertEqual(image.getpixel(point), plum)
        for point in [(268, 270), (268, 395), (162, 350), (374, 350)]:
            self.assertEqual(image.getpixel(point), ivory)
        for point in [(139, 350), (397, 350), (268, 485)]:
            self.assertEqual(image.getpixel(point), blue)
        counts = Counter(image.get_flattened_data())
        self.assertGreater(counts[ivory] / (1220 * 820), 0.75)
        self.assertGreater(counts[plum], counts[blue])

    def test_car_survives_texture_downsample(self):
        """A small-texture contrast proxy protects the motif, not gameplay-camera legibility."""
        image = create_artwork().resize((61, 41), Image.Resampling.LANCZOS).convert("L")
        self.assertLess(image.getpixel((13, 17)), image.getpixel((21, 17)) - 70)


if __name__ == "__main__":
    unittest.main()
