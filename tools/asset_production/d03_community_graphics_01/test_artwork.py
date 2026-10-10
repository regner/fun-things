"""Independent region, original-copy and reproducibility tests for the community board."""
import hashlib
import io
import json
from pathlib import Path
import unittest

from PIL import Image, ImageColor

import author

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = Path("C:/tmp/ft/assets/d03_community_graphics_01")


class CommunityArtworkTests(unittest.TestCase):
    """Keep expected copy, notice layout, safe margins and palette independent of drawing math."""

    def setUp(self):
        """Load the committed RGB artwork, not an uncommitted render substitute."""
        self.raw = author.OUTPUT.read_bytes()
        self.image = Image.open(io.BytesIO(self.raw)).convert("RGB")

    def test_deterministic_png(self):
        """The original Pillow recipe must reproduce the exact committed texture bytes."""
        output = io.BytesIO()
        author.create_artwork().save(output, format="PNG", compress_level=9)
        self.assertEqual(self.raw, output.getvalue())
        self.assertEqual(self.image.size, (1640,1040))
        self.assertEqual(Image.open(io.BytesIO(self.raw)).mode, "RGB")

    def test_literal_copy(self):
        """Reject accidental missing words and unapproved identity/brand copy."""
        self.assertEqual(author.COPY, ["SHARED SPACE.", "INDIVIDUAL OPINIONS.", "COURT CHAT",
                         "ALL WELCOME", "LAUNDRY", "SHARE THE LINE.", "NOT THE SOCKS.",
                         "TAKE A SEAT", "LEAVE ROOM."])
        self.assertTrue(set("".join(author.COPY).replace(" ","")) <= set(author.GLYPHS))

    def test_palette_regions(self):
        """Check literal flat field, paper, gutter, icon and accent samples independently."""
        regions = {
            "#587D7C": [(30,40),(1540,270),(243,744),(389,704),(534,744)],
            "#CECDB8": [(30,1020),(736,520),(1200,740),(100,120)],
            "#E6E1CC": [(90,950),(680,650),(1530,930)],
            "#B98377": [(280,200),(300,396),(1440,470),(390,910)],
            "#C5D0C3": [(1550,680),(1340,526)],
            "#294B50": [(823,840),(1380,437)],
        }
        for color, points in regions.items():
            for point in points:
                self.assertEqual(self.image.getpixel(point), ImageColor.getrgb(color), point)

    def test_each_copy_region_contains_ink(self):
        """All nine copy lines occupy nonempty separate regions, rather than blank notice cards."""
        regions = [(375,80,1420,195),(380,223,1170,284),(98,457,685,543),
                   (98,560,574,626),(795,417,1230,506),(795,544,1330,605),
                   (795,616,1305,677),(795,802,1300,872),(795,896,1155,954)]
        for index, bounds in enumerate(regions):
            target = ImageColor.getrgb("#E6E1CC" if index < 2 else "#294B50")
            pixels = self.image.crop(bounds).get_flattened_data()
            # Thin secondary strokes contain antialiased color, not only exact palette bytes.
            ink_pixels = sum(max(abs(a-b) for a,b in zip(pixel,target)) <= 12 for pixel in pixels)
            self.assertGreater(ink_pixels, 400, bounds)

    def test_safe_frame_gutters(self):
        """The 30 mm inherited safe-copy inset contains all content except flat background."""
        for y in range(1040):
            expected = ImageColor.getrgb("#587D7C" if y < 316 else "#CECDB8")
            if 316 <= y <= 324:
                continue
            for x in (0,29,1610,1639):
                self.assertEqual(self.image.getpixel((x,y)), expected)
        for y in (0,29,1010,1039):
            expected = ImageColor.getrgb("#587D7C" if y < 30 else "#CECDB8")
            for x in range(1640):
                self.assertEqual(self.image.getpixel((x,y)), expected)


def main():
    """Write a lean scratch receipt only when every independent artwork test passes."""
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CommunityArtworkTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    raw = author.OUTPUT.read_bytes()
    receipt = {"ok":True,"tests":result.testsRun,"size":[1640,1040],"mode":"RGB8 sRGB",
               "byte_identical_reproduction":True,"png_bytes":len(raw),
               "png_sha256":hashlib.sha256(raw).hexdigest(),"independent_region_samples":20,
               "safe_copy_inset_pixels":30,"original_copy":author.COPY}
    SCRATCH.mkdir(parents=True,exist_ok=True)
    (SCRATCH / "artwork-check.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8", newline="\n")
    print("COMMUNITY_ARTWORK_TEST_PASS")


if __name__ == "__main__":
    main()
