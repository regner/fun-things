"""Independent region, variant and deterministic-export tests for the four number faces."""
import hashlib
import io
import json
import unittest
from pathlib import Path
from PIL import Image
from artwork import create_artwork
ROOT=Path(__file__).resolve().parents[3]
NID='d03_community_graphics_02'
SCRATCH=Path(f'C:/tmp/ft/assets/{NID}')


class EntranceArtworkTests(unittest.TestCase):
    """Protect the four-number set, safe margins and subdued colors."""

    def test_reproduction(self):
        """Every final PNG must exactly reproduce from the committed original recipe."""
        for number in ('01','02','03','04'):
            path=ROOT/f'art/textures/environment/{NID}/entrance_{number}_albedo.png'
            output=io.BytesIO()
            create_artwork(number).save(output,format='PNG',compress_level=9)
            self.assertEqual(path.read_bytes(),output.getvalue())

    def test_regions_and_margin(self):
        """Literal probes assert ink, teal field, coral accent and blank margins."""
        for number in ('01','02','03','04'):
            image=Image.open(ROOT/f'art/textures/environment/{NID}/entrance_{number}_albedo.png')
            self.assertEqual(image.size,(280,200))
            self.assertEqual(image.mode,'RGB')
            probes=[((10,10),(88,125,124)),((138,90),(88,125,124)),
                    ((40,170),(185,131,119)),((84,42),(206,205,184)),
                    ((84,92),(88,125,124))]
            for point,color in probes:
                self.assertEqual(image.getpixel(point),color)
            for x in range(280):
                self.assertEqual(image.getpixel((x,10)),(88,125,124))
                self.assertEqual(image.getpixel((x,189)),(88,125,124))
            for y in range(200):
                self.assertEqual(image.getpixel((10,y)),(88,125,124))
                self.assertEqual(image.getpixel((269,y)),(88,125,124))

    def test_distinct_digits(self):
        """Second digits differ, zero is shared, and explicit landmarks distinguish 1-4."""
        images=[Image.open(ROOT/f'art/textures/environment/{NID}/entrance_{n}_albedo.png')
                for n in ('01','02','03','04')]
        self.assertEqual(len({i.crop((145,30,235,153)).tobytes() for i in images}),4)
        self.assertEqual(len({i.crop((40,30,125,153)).tobytes() for i in images}),1)
        for image,point in zip(images,[(192,90),(180,145),(192,94),(190,109)]):
            self.assertEqual(image.getpixel(point),(206,205,184))


def main():
    """Write a receipt only after the complete independent test suite passes."""
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(EntranceArtworkTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    textures={}
    for number in ('01','02','03','04'):
        raw=(ROOT/f'art/textures/environment/{NID}/entrance_{number}_albedo.png').read_bytes()
        textures[number]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    receipt={'ok':True,'tests':result.testsRun,'byte_identical_reproduction':True,'textures':textures}
    (SCRATCH/'artwork-check.json').write_text(
        json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':
    main()
