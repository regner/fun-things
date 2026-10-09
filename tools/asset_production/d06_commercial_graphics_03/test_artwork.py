"""Independent output contracts for the two original cylindrical poster wraps."""
import io
import unittest

from PIL import Image, ImageChops, ImageColor, ImageStat

import author


class PosterWrapArtworkTests(unittest.TestCase):
    """Protect byte reproducibility, UV repeat continuity, quiet margins and distinct shapes."""

    @classmethod
    def setUpClass(cls):
        """Render each source recipe once for all output assertions."""
        cls.images = {variant: author.create_artwork(variant) for variant in author.VARIANTS}

    def test_opaque_size_and_exact_reproduction(self):
        """Each delivered PNG must equal a fresh source render, not only have a valid header."""
        for variant, image in self.images.items():
            with self.subTest(variant=variant):
                self.assertEqual(image.size, (2400, 1000))
                self.assertEqual(image.mode, "RGB")
                encoded = io.BytesIO()
                image.save(encoded, format="PNG", optimize=False, compress_level=9)
                self.assertEqual(encoded.getvalue(),
                                 (author.OUTPUT / f"{variant}_albedo.png").read_bytes())

    def test_front_back_repeat_and_rear_seam(self):
        """Rear boundary must be the same continuous neighbourhood as the interior front."""
        for variant, image in self.images.items():
            with self.subTest(variant=variant):
                self.assertIsNone(ImageChops.difference(
                    image.crop((0, 0, 1200, 1000)), image.crop((1200, 0, 2400, 1000))
                ).getbbox())
                rear = Image.new("RGB", (80, 1000))
                rear.paste(image.crop((2360, 0, 2400, 1000)), (0, 0))
                rear.paste(image.crop((0, 0, 40, 1000)), (40, 0))
                front = image.crop((1160, 0, 1240, 1000))
                self.assertIsNone(ImageChops.difference(rear, front).getbbox())

    def test_quiet_top_bottom_and_independent_motif_pixels(self):
        """Literal colour landmarks distinguish burst/tickets and keep edge trim quiet."""
        petrol = ImageColor.getrgb("#102C3C")
        for image in self.images.values():
            for box in [(0, 0, 2400, 65), (0, 940, 2400, 1000)]:
                strip = image.crop(box)
                self.assertEqual(strip.getextrema(), tuple((v, v) for v in petrol))
        self.assertEqual(self.images["last_call"].getpixel((1120, 140)),
                         ImageColor.getrgb("#F54BBA"))
        self.assertEqual(self.images["last_call"].getpixel((1200, 610)), petrol)
        self.assertEqual(self.images["small_prices"].getpixel((1200, 140)),
                         ImageColor.getrgb("#45DFE5"))
        self.assertEqual(self.images["small_prices"].getpixel((1200, 325)), petrol)
        self.assertEqual(self.images["small_prices"].getpixel((1200, 390)),
                         ImageColor.getrgb("#45DFE5"))

    def test_small_scale_colour_masses_differ(self):
        """A low-resolution texture proxy distinguishes variants without reading their copy."""
        reduced = [image.resize((48, 20), Image.Resampling.LANCZOS)
                   for image in self.images.values()]
        difference = ImageStat.Stat(ImageChops.difference(*reduced))
        self.assertGreater(sum(difference.mean) / 3, 18)


if __name__ == "__main__":
    unittest.main()
