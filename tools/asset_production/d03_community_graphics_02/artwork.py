"""Original four entrance numbers; reuse the lane's original numeral paths, never external fonts."""
import argparse
import importlib.util
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
NID = 'd03_community_graphics_02'
SIZE = (280, 200)
NUMBERS = ('01', '02', '03', '04')
COLORS = {'teal':'#587D7C', 'ivory':'#CECDB8', 'coral':'#B98377', 'ink':'#294B50'}
spec = importlib.util.spec_from_file_location('court_art', ROOT / 'tools/asset_production/d03_court_graphics_02/artwork.py')
court = importlib.util.module_from_spec(spec)
spec.loader.exec_module(court)
DIGITS = {str(k):v for k,v in court.DIGITS.items()}
# Original rounded zero, sharing the preceding court set's monoline proportions.
DIGITS['0'] = [[(.3,0),(.7,0),(.95,.14),(1,.35),(1,.65),(.95,.86),(.7,1),(.3,1),(.05,.86),(0,.65),(0,.35),(.05,.14),(.3,0)]]


def create_artwork(number):
    """Draw two large ivory numerals and a restrained coral corner on a quiet teal field."""
    assert number in NUMBERS
    scale = 4
    image = Image.new('RGB', (SIZE[0]*scale,SIZE[1]*scale), COLORS['teal'])
    draw = ImageDraw.Draw(image)
    # Only one small coral accent: not a luminous commercial fascia or wayfinding arrow.
    draw.rounded_rectangle((20*scale,164*scale,61*scale,175*scale), radius=5*scale, fill=COLORS['coral'])
    for char,x in zip(number,(53,161)):
        for path in DIGITS[char]:
            points = [((x+u*62)*scale,(42+v*103)*scale) for u,v in path]
            draw.line(points,fill=COLORS['ivory'],width=11*scale,joint='curve')
            for px,py in points:
                r=5.5*scale
                draw.ellipse((px-r,py-r,px+r,py+r),fill=COLORS['ivory'])
    return image.resize(SIZE,Image.Resampling.LANCZOS)


def main():
    """Write the four deterministic opaque face textures at 500 texels per metre."""
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/f'art/textures/environment/{NID}')
    out=parser.parse_args().output
    out.mkdir(parents=True,exist_ok=True)
    for number in NUMBERS:
        create_artwork(number).save(out/f'entrance_{number}_albedo.png',compress_level=9)
    print('ENTRANCE_ARTWORK_PASS: 01 02 03 04')


if __name__=='__main__':
    main()
