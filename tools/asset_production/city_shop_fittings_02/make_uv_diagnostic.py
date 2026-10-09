"""Original scratch diagnostic only. Standard-library PNG; no fonts or district artwork."""
import struct,zlib
from pathlib import Path
E=Path(__file__).resolve().parents[3]/'docs/assets/production/city_shop_fittings_02-evidence'
w,h=1500,300
colors=[(216,118,103),(86,122,175),(214,201,156),(92,139,123)]
glyphs={'T':['11111','00100','00100','00100','00100','00100','00100'],'L':['10000','10000','10000','10000','10000','10000','11111'],'R':['11110','10001','10001','11110','10100','10010','10001'],'B':['11110','10001','10001','11110','10001','10001','11110']}
pixels=bytearray()
for y in range(h):
    pixels.append(0)
    for x in range(w):
        col=colors[(2 if y>=150 else 0)+(1 if x>=750 else 0)]
        label=('B' if y>=150 else 'T')+('R' if x>=750 else 'L')
        lx=x-(1370 if x>=750 else 35);ly=y-(210 if y>=150 else 30)
        if 0<=lx<78 and 0<=ly<42:
            char=lx//42;gx=lx%42//6;gy=ly//6
            if char<2 and gx<5 and glyphs[label[char]][gy][gx]=='1':col=(255,255,255)
        if (250<x<1205 and abs(y-150)<3) or (1205<=x<=1250 and abs(y-150)<(1250-x)*.45):col=(255,255,255)
        if (abs(x-750)<3 and 85<y<235) or (45<=y<=85 and abs(x-750)<(y-45)*.5):col=(255,255,255)
        if x%150<3 and y>285:col=(255,255,255)
        pixels.extend(col)
def chunk(tag,data):return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
(E/'uv_diagnostic.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(pixels))+chunk(b'IEND',b''))
print('ORIGINAL_SCRATCH_DIAGNOSTIC_COMPLETE')
