"""Independent artwork expectations: sparse parallel harbour lines, warm field and clean seams."""
import io
import unittest

from PIL import Image

from artwork import TEXTURE, draw_artwork


class QuayBorderArtworkTests(unittest.TestCase):
    """Guard the delivered PNG, not merely successful execution of the drawing recipe."""

    def test_exact_reproduction(self):
        """The committed original artwork is deterministically reproducible."""
        buffer = io.BytesIO()
        draw_artwork().save(buffer, format="PNG", compress_level=9)
        self.assertEqual(buffer.getvalue(), TEXTURE.read_bytes())
        with Image.open(TEXTURE) as image:
            self.assertEqual(image.size, (1280, 192))
            self.assertEqual(image.mode, "RGB")

    def test_quiet_field_and_restrained_coverage(self):
        """More than three quarters stays exactly quiet field, with no gritty fill."""
        with Image.open(TEXTURE) as image:
            colors = image.getcolors(image.width * image.height)
            quiet = sum(count for count, color in colors if color == (166, 167, 158))
            self.assertGreater(quiet / (1280 * 192), .78)
            self.assertLess(quiet / (1280 * 192), .86)
            self.assertEqual(image.getpixel((320, 0)), (166, 167, 158))
            self.assertEqual(image.getpixel((320, 191)), (166, 167, 158))
            for y in list(range(24)) + list(range(168, 192)):
                self.assertEqual(set(image.crop((0, y, 1280, y + 1)).get_flattened_data()),
                                 {(166, 167, 158)})

    def test_two_separated_broad_lines(self):
        """Every measured cross-section has two independent 0.1 m strokes, not a filled barrier."""
        with Image.open(TEXTURE) as image:
            for x in (0, 160, 320, 480, 640, 800, 960, 1120, 1279):
                runs = []
                for y in range(192):
                    if image.getpixel((x, y))[0] < 130:
                        if not runs or y != runs[-1][-1] + 1:
                            runs.append([])
                        runs[-1].append(y)
                self.assertEqual(len(runs), 2)
                self.assertTrue(all(14 <= len(run) <= 18 for run in runs))
                self.assertGreater(runs[1][0] - runs[0][-1], 45)
            # Independent crest/trough landmarks prove broad variation rather than straight rails.
            self.assertLess(image.getpixel((0, 73))[0], 130)
            self.assertLess(image.getpixel((320, 48))[0], 130)
            self.assertEqual(image.getpixel((320, 73)), (166, 167, 158))

    def test_repeat_seam_and_minified_readability(self):
        """X repeats meet exactly; top/bottom edges are quiet and broad minified strokes survive."""
        with Image.open(TEXTURE) as image:
            self.assertEqual(image.crop((0, 0, 1, 192)).tobytes(),
                             image.crop((1279, 0, 1280, 192)).tobytes())
            small = image.resize((160, 24), Image.Resampling.LANCZOS)
            self.assertGreater(max(c[0] for c in small.get_flattened_data()) -
                               min(c[0] for c in small.get_flattened_data()), 40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
