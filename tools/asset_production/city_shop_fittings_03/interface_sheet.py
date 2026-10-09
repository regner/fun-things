"""Dimensioned orthographic interface drawing, metres; no leaf or wall mesh creation."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_shop_fittings_03-evidence'
checks=json.loads((E/'interface_checks.json').read_text()); assert len(checks)==2
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1000" viewBox="0 0 1440 1000">', '<rect width="1440" height="1000" fill="#f4f1e8"/>', '<style>text{font-family:DejaVu Sans,sans-serif;fill:#223d49;font-size:19px}.small{font-size:16px}.title{font-size:30px;font-weight:bold}.sub{font-size:23px;font-weight:bold}.dim{stroke:#425966;stroke-width:1.5;fill:none}.guide{stroke:#b85845;stroke-width:2;stroke-dasharray:7 5;fill:none}</style>']
def text(x,y,t,cls=''):svg.append(f'<text x="{x}" y="{y}" class="{cls}">{t}</text>')
def line(x1,y1,x2,y2,cls='dim'):svg.append(f'<path d="M{x1},{y1} L{x2},{y2}" class="{cls}"/>')
def rect(x,y,w,h,fill,stroke='none'):svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"/>')
text(45,48,'city_shop_fittings.03 / entrance interface','title')
text(45,78,'Metres · source-space elevations + section · dimensions are authored choices, not measured gameplay acceptance','small')
scale=150; base=515
for cx,w,label in [(200,1.04,'SINGLE'),(565,1.84,'DOUBLE')]:
    text(cx-90,128,label,'sub')
    outer=w+.5
    rect(cx-outer/2*scale,base-2.48*scale,outer*scale,2.48*scale,'#c8c2ad')
    rect(cx-(w+.205)/2*scale,base-2.355*scale,(w+.205)*scale,2.355*scale,'#405b68')
    rect(cx-w/2*scale,base-2.24*scale,w*scale,2.22*scale,'#f4f1e8')
    rect(cx-(w+.36)/2*scale,base-.02*scale,(w+.36)*scale,.02*scale,'#929d9f')
    line(cx-outer/2*scale,550,cx+outer/2*scale,550)
    for x in [cx-outer/2*scale,cx+outer/2*scale]:line(x,541,x,559)
    text(cx-72,579,f'{outer:.2f} overall')
    line(cx-w/2*scale,340,cx+w/2*scale,340,'guide'); text(cx-72,331,f'{w:.2f} aperture')
    text(cx-94,610,'2.48 overall height')
    text(cx-94,637,'2.24 aperture head')
text(880,128,'CENTRE HEADER / SILL SECTION','sub')
# Section exaggerated width relative to elevation only for dimension legibility.
sy=150; sx=480; bx=1190; bz=515
# Header cross-section: Y front at right, Z up.
pts=[(-.52,2.24),(-.40,2.24),(-.07,2.36),(.045,2.36),(.045,2.44),(-.52,2.44)]
svg.append('<polygon points="'+' '.join(f'{bx+y*sx},{bz-z*sy}' for y,z in pts)+'" fill="#405b68"/>')
rect(bx+.01*sx,bz-2.48*sy,.075*sx,.125*sy,'#c8c2ad')
rect(bx-.516*sx,bz-2.275*sy,.035*sx,.051*sy,'#293b43')
pts=[(-.52,0),(.11,0),(.11,.004),(.045,.020),(-.50,.020),(-.52,.014)]
svg.append('<polygon points="'+' '.join(f'{bx+y*sx},{bz-z*sy}' for y,z in pts)+'" fill="#929d9f"/>')
line(bx,135,bx,545,'guide');text(bx+10,300,'Wall Y=0','small')
line(bx-.430*sx,bz-2.232*sy,bx-.430*sx,bz-.030*sy,'guide')
text(865,400,'Leaf front Y=-0.430','small'); text(865,425,'Dashed datum only','small')
line(890,base,1340,base);text(1170,540,'Floor Z=0','small')
line(bx-.52*sx,570,bx+.11*sx,570)
text(950,597,'0.63 total depth','small');text(930,625,'0.52 back / 0.11 front','small')
text(45,699,'STATIC .06 LEAF ENVELOPE — no leaves supplied','sub')
text(45,732,'Single: X [-0.512, +0.512]; double: [-0.912, -0.004] and [+0.004, +0.912].')
text(45,761,'Both: Y [-0.475, -0.430], Z [0.030, 2.232]. Single leaf 1.024 wide; paired leaves 0.908 each.')
text(45,790,'Gaps: 8 mm sides + head; 10 mm above sill; 6 mm rear stop; 8 mm double meeting seam.')
text(45,837,'SHELL + INSTALLATION INTERFACE','sub')
text(45,869,'Shell owns plain opening: 1.42 / 2.22 wide × 2.45 high, floor Z=0; reserve depth to Y=-0.54.')
text(45,898,'10 mm jamb/head installation gap; casing covers rough opening by 60 mm sides / 30 mm head.')
text(45,927,'Bounds ±1 mm; installation translation ±2 mm; unscaled orthogonal fit. Keep other trim 50 mm clear.')
text(45,961,'Blender +Y street / +Z up → Godot -Z street / +Y up. Source-only interface, later .06 assembly validation required.','small')
svg.append('</svg>'); (E/'interface_sheet.svg').write_text('\n'.join(svg)+'\n')
import subprocess
argv=['/usr/bin/rsvg-convert','-o',str(E/'interface_sheet.png'),str(E/'interface_sheet.svg')]
print('RENDER_ARGV',json.dumps(argv),flush=True)
subprocess.run(argv,check=True)
print('INTERFACE_SHEET_COMPLETE')
