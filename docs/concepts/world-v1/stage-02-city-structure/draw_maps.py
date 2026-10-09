#!/usr/bin/env python3
"""Draw reference-only Brackett macro maps; never author game-world placement."""

from html import escape
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parent
LAND = [(55, 175), (95, 95), (195, 45), (315, 55), (470, 95),
        (650, 115), (830, 145), (1000, 215), (1145, 300), (1210, 405),
        (1190, 500), (1110, 565), (985, 620), (800, 665), (625, 655),
        (470, 635), (300, 590), (195, 525), (100, 425), (55, 315)]
COLORS = ['#326469', '#355773', '#555d85', '#344a82', '#865550',
          '#865174', '#827345', '#506269', '#4b6880']
DISTRICTS = [
    ('Northpoint', 'Campus, quadrangles and sports fields'),
    ('The Crescents', 'Low-rise homes; loops and cul-de-sacs'),
    ('Terrace Ward', 'Apartment courts and short cross-links'),
    ('Glassward', 'Large downtown; towers and broad blocks'),
    ('Old Quay', 'Older harbour streets and civic squares'),
    ('Signal Row', 'Shops, entertainment and crowded corners'),
    ('Broadlot', 'Big retail roofs and open surface parking'),
    ('Ironreach', 'Workshops, repair courts and service lanes'),
    ('East Docks', 'Warehouses, loading yards and cranes'),
]
COAST = [(125, 185), (170, 115), (320, 110), (480, 150), (700, 170),
         (920, 225), (1080, 330), (1140, 440), (1060, 525), (930, 580),
         (775, 620), (585, 600), (450, 575), (400, 590)]
WEST_COAST = [(307, 590), (235, 525), (160, 450), (110, 360), (100, 270), (125, 185)]
OPTIONS = [
    dict(slug='01-neighbourhood-loops', letter='A', title='Neighbourhood loops',
         subtitle='Selected macro plan and M1 area. Exact local geometry refines in later stages.',
         seeds=[(185, 155), (250, 300), (495, 195), (800, 260), (220, 460),
                (535, 395), (650, 570), (945, 435), (1095, 535)],
         weights=[8000, 1500, 2000, 16000, 0, 1000, 3000, 5000, 1000],
         m1=(610, 355), harbour_top=425,
         routes=[
             [(170, 115), (220, 205), (370, 245), (450, 340), (360, 395), (205, 345), (100, 270)],
             [(480, 150), (450, 340), (565, 440), (770, 455), (850, 350), (700, 170)],
             [(370, 245), (565, 245), (750, 275), (850, 350), (1045, 380), (1080, 330)],
             [(565, 440), (585, 600)],
             [(770, 455), (930, 500), (1045, 380)],
             [(930, 500), (930, 580)],
             [(235, 525), (205, 345)],
         ],
         local=[[(220, 205), (280, 240), (250, 285)],
                [(360, 395), (360, 350), (310, 330)],
                [(930, 500), (1010, 485), (1020, 445)]],
         foot=[[(565, 440), (455, 480)], [(770, 455), (750, 525)]],
         hook='Selected M1 area: Signal Row / Ironreach edge',
         why=['Strongest mix of shops, homes and workshops.',
              'Local loops share traffic across several routes.',
              'Risk: too many links could blur district identity.']),
    dict(slug='02-harbour-heart', letter='B', title='Harbour heart',
         subtitle='The old quay and a central civic junction bring the districts together.',
         seeds=[(185, 150), (240, 300), (500, 185), (850, 270), (220, 475),
                (520, 390), (670, 565), (930, 455), (1100, 530)],
         weights=[7000, 1500, 1000, 19000, 4000, 7000, 5000, 1000, 1000],
         m1=(465, 355), harbour_top=380,
         routes=[
             [(170, 115), (235, 215), (355, 275), (520, 350), (600, 430), (585, 600)],
             [(100, 270), (235, 215)],
             [(480, 150), (520, 350)],
             [(520, 350), (690, 290), (780, 210), (920, 225)],
             [(690, 290), (850, 350), (1040, 410), (1080, 330)],
             [(600, 430), (850, 350)],
             [(600, 430), (775, 510), (930, 580)],
             [(775, 510), (1040, 410)],
             [(235, 525), (225, 410), (355, 275)],
         ],
         local=[[(235, 215), (305, 190), (330, 165)],
                [(225, 410), (180, 370), (195, 335)],
                [(1040, 410), (1055, 460), (1015, 485)]],
         foot=[[(520, 350), (470, 435)], [(600, 430), (635, 510)]],
         hook='M1 candidate: Signal Row / Old Quay fringe',
         why=['A strong harbour identity and central meeting place.',
              'The larger basin gives the bridge more presence.',
              'Risk: central junctions and basin head may congest.']),
    dict(slug='03-bent-spine', letter='C', title='The bent spine',
         subtitle='A memorable cross-city route, backed by coastal and neighbourhood circuits.',
         seeds=[(175, 150), (255, 310), (490, 200), (800, 255), (225, 460),
                (550, 405), (690, 575), (945, 420), (1100, 530)],
         weights=[6500, 0, 3000, 19000, 1500, 3000, 2500, 6000, 1000],
         m1=(785, 395), harbour_top=425,
         routes=[
             [(125, 185), (280, 220), (405, 305), (590, 310), (740, 365), (935, 375), (1060, 525)],
             [(480, 150), (490, 225), (590, 310)],
             [(920, 225), (875, 310), (935, 375)],
             [(235, 525), (260, 375), (405, 305)],
             [(260, 375), (125, 185)],
             [(405, 305), (500, 475), (650, 530), (740, 365)],
             [(650, 530), (775, 620)],
             [(935, 375), (1000, 450), (930, 580)],
         ],
         local=[[(280, 220), (250, 175), (290, 150)],
                [(500, 475), (460, 420), (495, 385)],
                [(1000, 450), (1060, 425), (1070, 400)]],
         foot=[[(500, 475), (425, 500)], [(740, 365), (810, 450)]],
         hook='M1 candidate: Ironreach / Glassward fringe',
         why=['Easy city-wide orientation and a strong driving route.',
              'Industrial yards and downtown form a clear contrast.',
              'Risk: traffic concentrates along the main spine.']),
]


def polygon(points):
    """Serialize map points without implying saved gameplay geometry."""
    return ' '.join(f'{x:.1f},{y:.1f}' for x, y in points)


def cell(seeds, weights, index):
    """Clip a weighted district diagram against its neighbouring seed half-planes."""
    poly = [(0, 0), (1260, 0), (1260, 720), (0, 720)]
    x, y = seeds[index]
    for j, (u, v) in enumerate(seeds):
        if j == index:
            continue
        a, b = 2 * (u - x), 2 * (v - y)
        c = u*u + v*v - x*x - y*y + weights[index] - weights[j]
        result = []
        for p, q in zip(poly, poly[1:] + poly[:1]):
            dp, dq = a*p[0] + b*p[1] - c, a*q[0] + b*q[1] - c
            if dp <= 0:
                result.append(p)
            if (dp <= 0) != (dq <= 0):
                t = dp / (dp - dq)
                result.append((p[0] + t*(q[0]-p[0]), p[1] + t*(q[1]-p[1])))
        poly = result
    return poly


def curve(points):
    """Use a smooth curve through specified junction anchors for schematic roads."""
    d = f'M {points[0][0]} {points[0][1]}'
    for i in range(len(points)-1):
        p0, p1 = points[max(0, i-1)], points[i]
        p2, p3 = points[i+1], points[min(len(points)-1, i+2)]
        c1 = (p1[0]+(p2[0]-p0[0])/6, p1[1]+(p2[1]-p0[1])/6)
        c2 = (p2[0]-(p3[0]-p1[0])/6, p2[1]-(p3[1]-p1[1])/6)
        d += f' C {c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]} {p2[1]}'
    return d


def text(x, y, value, size=18, color='#eff4f2', extra=''):
    """Create escaped text in a shared readable map typeface."""
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{escape(value)}</text>'


def render(option):
    """Compose one editorial macro board and export its SVG and PNG."""
    s = ['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1200" viewBox="0 0 1800 1200">',
         '<style>text{font-family:DejaVu Sans,sans-serif} .road{fill:none;stroke-linecap:round;stroke-linejoin:round}</style>',
         '<rect width="1800" height="1200" fill="#0c1b29"/>',
         '<rect x="28" y="174" width="1310" height="842" rx="18" fill="#102c40"/>',
         '<rect x="1364" y="174" width="408" height="842" rx="18" fill="#152735"/>',
         text(48, 46, 'BRACKETT (WORKING NAME) / STAGE 2 / CITY STRUCTURE', 15, '#65d7db'),
         text(48, 102, f'{option["letter"]} — {option["title"]}', 42, extra='font-weight="bold"'),
         text(48, 139, option['subtitle'], 19, '#c5d4dd'),
         text(1750, 45, 'STAGE 2 APPROVED • MACRO PLAN' if option['letter'] == 'A'
              else 'EARLIER COMPARISON OPTION', 14, '#ffcf68', 'text-anchor="end"'),
         '<defs><clipPath id="island"><polygon points="'+polygon(LAND)+'"/></clipPath></defs>',
         '<g transform="translate(56 224)">',
         '<polygon points="'+polygon(LAND)+'" fill="#2b4b5c" stroke="#92bdc7" stroke-width="3"/>',
         '<g clip-path="url(#island)">']
    for i in range(9):
        s.append(f'<polygon points="{polygon(cell(option["seeds"], option["weights"], i))}" fill="{COLORS[i]}" stroke="#becad0" stroke-opacity=".24" stroke-width="2"/>')
    paths = [COAST, WEST_COAST] + option['routes']
    for pts in paths:
        d = curve(pts)
        s += [f'<path class="road" d="{d}" stroke="#182a38" stroke-width="17"/>',
              f'<path class="road" d="{d}" stroke="#afd4db" stroke-width="5"/>']
    for pts in option['local']:
        s.append(f'<path class="road" d="{curve(pts)}" stroke="#a9b9c5" stroke-width="4" stroke-dasharray="7 6"/>')
        x, y = pts[-1]
        s.append(f'<circle cx="{x}" cy="{y}" r="9" fill="#243b4e" stroke="#b6c7d0" stroke-width="3"/>')
    for pts in option['foot']:
        s.append(f'<path class="road" d="{curve(pts)}" stroke="#d0d9b2" stroke-width="3" stroke-dasharray="2 7"/>')
    t = option['harbour_top']
    water = f'M 320 {t} C 263 {t} 242 482 267 519 C 286 540 315 548 316 566 L 315 690 L 385 690 L 387 562 C 452 527 466 {t+26} 409 {t+8} C 385 {t-4} 350 {t-8} 320 {t} Z'
    s += [f'<path d="{water}" fill="#102c40" stroke="#7cabbc" stroke-width="2"/>',
          '<path d="M 337 557 L 337 672 M 366 557 L 366 672" stroke="#76bccc" stroke-width="1.5" stroke-dasharray="5 7" opacity=".7"/>',
          '<path d="M 309 590 L 400 590" stroke="#112233" stroke-width="18"/>',
          '<path d="M 309 590 L 400 590" stroke="#ff8eaa" stroke-width="7"/>',
          '<path d="M 309 578 L 309 602 M 400 578 L 400 602" stroke="#ff8eaa" stroke-width="3"/>']
    # The six lots use the accepted brief's real dimensions; surrounding streets remain schematic.
    mx, my = option['m1']
    s.append(f'<rect x="{mx}" y="{my}" width="260" height="163" rx="5" fill="#ffc85c" fill-opacity=".1" stroke="#ffe082" stroke-width="3" stroke-dasharray="10 6"/>')
    for row in range(2):
        for col in range(3):
            s.append(f'<rect x="{mx+17+81*col}" y="{my+17+73*row}" width="64" height="56" fill="#ffe082" fill-opacity=".13" stroke="#ffe082" stroke-width="1"/>')
    s.append(f'<rect x="{mx+12}" y="{my-30}" width="205" height="27" rx="5" fill="#ffe082"/>')
    s.append(text(mx+22, my-11, 'M1  SELECTED SIX-BLOCK AREA' if option['letter'] == 'A'
                  else 'M1?  SIX-BLOCK CANDIDATE', 11, '#243139', 'font-weight="bold"'))
    # Diagram symbols identify area functions; they are not building designs or placement.
    s += ['<rect x="195" y="60" width="75" height="44" rx="13" fill="none" stroke="#b8dfca" stroke-width="3"/>',
          '<rect x="206" y="69" width="53" height="26" fill="none" stroke="#b8dfca" stroke-width="1.5"/>',
          '<g fill="#bdd4e9" opacity=".7"><rect x="790" y="215" width="20" height="38"/><rect x="817" y="190" width="20" height="63"/><rect x="844" y="205" width="20" height="48"/></g>',
          '<g fill="none" stroke="#d4c68d" stroke-width="2"><rect x="645" y="555" width="83" height="43"/><path d="M 655 562 V 591 M 669 562 V 591 M 683 562 V 591 M 697 562 V 591 M 711 562 V 591"/></g>',
          '<g fill="none" stroke="#afcde1" stroke-width="3"><path d="M 1130 485 L 1175 510 M 1115 510 L 1160 540 M 1090 540 L 1130 570"/></g>']
    s.append('</g>')
    # Consistent number markers connect the diagram to the district key.
    for i, (x, y) in enumerate(option['seeds']):
        if i == 0: y += 50
        if i == 3: y += 35
        if i == 6: x -= 45; y += 20
        if i == 7: x += 35; y -= 28
        if i == 7 and option['letter'] == 'C': y -= 52
        if i == 8: x += 18; y -= 2
        if i == 5: x -= 15; y -= 20
        s += [f'<circle cx="{x}" cy="{y}" r="18" fill="#0e2332" stroke="{COLORS[i]}" stroke-width="4"/>',
              text(x, y+6, str(i+1), 17, extra='text-anchor="middle" font-weight="bold"')]
    s += [text(322, 482 if t == 425 else 458, 'HARBOUR', 12, '#97cbd6'),
          text(180, 647, 'OPEN WATER', 13, '#80b5c7'),
          text(448, 652, '01  Harbour-mouth bridge', 13, '#ff9eb5'),
          '<path d="M 445 634 L 399 601" fill="none" stroke="#ff9eb5" stroke-width="1.5"/>',
          '<path d="M 1175 95 V 30 M 1166 47 L 1175 30 L 1184 47" fill="none" stroke="#e8f0ee" stroke-width="3"/>',
          text(1175, 17, 'N', 18, extra='text-anchor="middle"'), '</g>']
    s += [text(1390, 211, 'NINE DISTRICT IDENTITIES', 16, '#65d7db'),
          text(1390, 232, 'City and district names are placeholders.', 11, '#c2d2dc')]
    for i, (name, description) in enumerate(DISTRICTS):
        y = 255 + i*65
        s += [f'<circle cx="1405" cy="{y-4}" r="14" fill="{COLORS[i]}"/>',
              text(1405, y+1, str(i+1), 13, extra='text-anchor="middle" font-weight="bold"'),
              text(1431, y, name, 20, extra='font-weight="bold"'),
              text(1431, y+23, description, 12, '#c2d2dc')]
    s += [text(1390, 871, 'DIAGRAM KEY', 14, '#65d7db'),
          '<path d="M 1395 895 H 1430" stroke="#afd4db" stroke-width="5"/>', text(1442, 900, 'Main street centre line', 14),
          '<path d="M 1395 927 H 1430" stroke="#a9b9c5" stroke-width="4" stroke-dasharray="7 5"/>', text(1442, 932, 'Local access / turning court', 14),
          '<path d="M 1395 959 H 1430" stroke="#d0d9b2" stroke-width="3" stroke-dasharray="2 6"/>', text(1442, 964, 'Possible walking link', 14),
          '<rect x="1395" y="983" width="35" height="15" fill="none" stroke="#ffe082" stroke-width="2" stroke-dasharray="5 3"/>', text(1442, 997, 'M1 area; approximate extent' if option['letter'] == 'A' else 'Unselected M1 size study', 14),
          text(55, 953, option['hook'], 18, '#ffe082', 'font-weight="bold"'),
          text(55, 981, '260 × 163 m street envelope • six 64 × 56 m lots • overlay is a size test, not a finished grid', 14, '#c2d2dc'),
          text(48, 1062, 'PROVISIONAL SCALE', 14, '#65d7db'),
          '<path d="M 48 1090 H 248 M 48 1083 V 1097 M 148 1083 V 1097 M 248 1083 V 1097" stroke="#eef3ee" stroke-width="3"/>',
          text(48, 1120, '0', 13), text(135, 1120, '100', 13), text(231, 1120, '200 m', 13),
          text(48, 1152, 'Island envelope ≈ 1.2 × 0.65 km', 15, '#c2d2dc'),
          text(360, 1058, option['why'][0], 18), text(360, 1087, option['why'][1], 17, '#c2d2dc'),
          text(360, 1116, option['why'][2], 17, '#ffc67e'),
          text(360, 1155, 'Flat terrain • one bridge • whole-city vision • M1 scope unchanged', 15, '#c2d2dc'),
          text(1750, 1180, 'Roads are schematic centre lines, not engineered widths. No traffic or camera validation claimed.', 12, '#829dab', 'text-anchor="end"'),
          '</svg>']
    path = ROOT / (option['slug']+'.svg')
    path.write_text('\n'.join(s)+'\n')
    subprocess.run(['rsvg-convert', str(path), '-o', str(path.with_suffix('.png'))], check=True)


if __name__ == '__main__':
    for option in OPTIONS:
        render(option)
        print(option['slug'])
