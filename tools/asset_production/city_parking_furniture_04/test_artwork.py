"""Independent pixel landmarks and deterministic-output checks for the bus-stop symbol."""
import io
import unittest

from PIL import Image, ImageColor

import author


class BusStopArtworkTests(unittest.TestCase):
    """Protect the quiet field, bus features and unchanged source-to-runtime image path."""

    def setUp(self):
        """Read the actual delivered texture, not merely the author's in-memory image."""
        self.image = Image.open(author.OUTPUT)
        self.addCleanup(self.image.close)

    def test_dimensions_and_opaque_rgb(self):
        """The square face expects a small opaque RGB texture with no alpha fringes."""
        self.assertEqual(self.image.size, (512, 512))
        self.assertEqual(self.image.mode, "RGB")

    def test_safe_margins_and_quiet_field(self):
        """Keep all graphic content inside the carrier's safe 0.600 m rectangle."""
        petrol = ImageColor.getrgb("#123646")
        for point in [(32, 256), (479, 256), (256, 32), (256, 479), (60, 60)]:
            self.assertEqual(self.image.getpixel(point), petrol)
        quiet = sum(pixel == petrol for pixel in self.image.get_flattened_data())
        self.assertGreater(quiet / (512 * 512), .70)

    def test_bus_landmarks(self):
        """Require split windshield, warm header, distinct lamps and two separate feet."""
        for point in [(180, 220), (332, 220), (168, 328), (344, 328), (256, 401)]:
            self.assertEqual(self.image.getpixel(point), ImageColor.getrgb("#123646"))
        for point in [(256, 220), (156, 399), (352, 399), (256, 355)]:
            self.assertEqual(self.image.getpixel(point), ImageColor.getrgb("#F6F1DC"))
        self.assertEqual(self.image.getpixel((256, 132)), ImageColor.getrgb("#FFC05A"))

    def test_png_byte_identity(self):
        """Rebuilding the artwork must reproduce the committed PNG bytes exactly."""
        output = io.BytesIO()
        author.artwork().save(output, format="PNG", compress_level=9)
        self.assertEqual(output.getvalue(), author.OUTPUT.read_bytes())


if __name__ == "__main__":
    unittest.main()
