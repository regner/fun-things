"""Create an external diagnostic image using only Python standard libraries."""
import struct,zlib
from pathlib import Path
out=Path(__file__).resolve().parents[3]/'docs/assets/production/city_sign_supports_01-evidence/uv_diagnostic.png'
w,h=1220,820
colors=[(255,115,93),(35,95,204),(246,241,220),(21,86,79)]
glyphs={'T':['11111','00100','00100','00100','00100','00100','00100'],'L':['10000','10000','10000','10000','10000','10000','11111'],'R':['11110','10001','10001','11110','10100','10010','10001'],'B':['11110','10001','10001','11110','10001','10001','11110']}
pixels=bytearray()
for y in range(h):
    pixels.append(0)
    for x in range(w):
        col=colors[(2 if y>=410 else 0)+(1 if x>=610 else 0)]
        label=('B' if y>=410 else 'T')+('R' if x>=610 else 'L')
        lx=x%610-70;ly=y%410-65
        if 0<=lx<130 and 0<=ly<70:
            char=lx//70;gx=(lx%70)//10;gy=ly//10
            if char<2 and gx<5 and glyphs[label[char]][gy][gx]=='1':col=(255,255,255)
        if (582<=x<=638 and 330<=y<580) or (230<=y<330 and abs(x-610)<(y-230)*.65):col=(255,255,255)
        pixels.extend(col)
def chunk(tag,data): return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
out.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(pixels))+chunk(b'IEND',b''))
print(str(out))
