#!/usr/bin/env python3
"""Render original 2D identity diagrams, never game-world geometry or 3D assets."""

from html import escape
import json
from pathlib import Path
import subprocess
import textwrap


ROOT = Path(__file__).resolve().parent
INK = '#F4EEDD'
MUTED = '#B5C7D0'


def text(x, y, value, size=20, color=INK, weight=400):
    return (f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" '
            f'font-weight="{weight}">{escape(value)}</text>')


def para(x, y, value, width=36, size=20, color=INK, leading=27):
    lines = textwrap.wrap(value, width=width, break_long_words=False)
    return ''.join(text(x, y + i * leading, line, size, color)
                   for i, line in enumerate(lines))


def rect(x, y, w, h, color, radius=0, stroke='none', sw=1):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
            f'fill="{color}" stroke="{stroke}" stroke-width="{sw}"/>')


def path(d, color, width, dash=None):
    extra = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round"{extra}/>')


def circle(x, y, r, fill, stroke='none', sw=1):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def road(d, width=43):
    return path(d, '#637383', width + 17) + path(d, '#172D40', width)


def roof(x, y, w, h, color, accent=None, angle=0):
    result = f'<g transform="rotate({angle} {x+w/2} {y+h/2})">'
    result += rect(x+7, y+9, w, h, '#091B2B', 4)
    result += rect(x, y, w, h, color, 4, '#8296A1', 1.5)
    result += path(f'M{x+9} {y+10} H{x+w-9}', accent or '#91A5B0', 4)
    result += path(f'M{x+10} {y+h/2} H{x+w-10}', '#172D40', 2)
    return result + '</g>'


def parking(x, y, rows=2, count=5):
    result = rect(x-8, y-8, count*37+13, rows*72, '#334855', 6)
    for row in range(rows):
        for col in range(count):
            px, py = x+col*37, y+row*65
            result += path(f'M{px} {py} V{py+38} H{px+29} V{py}', '#849AA5', 1.5)
            if (row*count+col) % 4 == 1:
                result += rect(px+6, py+6, 17, 28, '#C6CECB', 4)
    return result


def motif(b):
    c, secondary, accent, extra = b['colors']
    kind = b['motif']
    s = rect(0, 0, 750, 620, '#203644', 15)
    if kind == 'campus':
        s += road('M-20 550 C60 610 120 580 120 440 V170 Q120 75 225 75 H610 Q680 75 680 180 V650')
        s += rect(205, 185, 210, 225, '#385D58', 6)
        for args in [(190,150,250,40),(185,200,50,235),(265,415,165,45)]:
            s += roof(*args,c,extra)
        s += rect(480,205,155,255,'#487566',65,extra,3)
        s += rect(503,235,109,195,'#355F55',45,'#ABCABD',2)
        s += path('M505 331 H610','#ABCABD',2)
        s += roof(485,487,135,54,secondary,accent)
        s += path('M260 290 H405 M340 200 V400', '#A4B6AC', 9)
    elif kind == 'housing':
        s += road('M-20 540 C90 520 125 450 150 355 S280 180 385 180 S600 260 775 210')
        s += road('M360 180 C355 280 455 290 470 375 V435',34)
        s += circle(470,435,42,'#172D40','#637383',8)
        s += path('M505 461 C560 520 610 535 720 515','#B9C9BD',8,'10 12')
        for i,(x,y,w,h,a) in enumerate([(60,290,54,69,20),(140,140,68,60,35),(240,90,110,42,-10),(405,65,65,57,15),(530,130,92,50,20),(625,290,63,84,-5),(285,315,72,85,-10),(360,495,92,52,15),(548,407,55,72,0),(120,485,80,61,-25)]):
            s += roof(x,y,w,h,c if i%3 else secondary,accent if i%3==0 else None,a)
    elif kind == 'courts':
        s += road('M-20 315 H250 Q320 315 360 345 L435 385 H775')
        s += road('M530 -30 V145 Q530 215 480 250 L450 385',35)
        for x,y in [(65,60),(540,60),(80,410),(445,465)]:
            s += rect(x,y,165,155,secondary,9)
            s += roof(x,y,175,40,c,accent)
            s += roof(x,y+46,40,109,c)
            s += roof(x+55,y+120,120,40,c,extra)
        s += roof(290,75,125,55,secondary,accent)
        s += path('M232 230 L275 280 M286 384 L318 520 H410','#BED0C3',8,'10 12')
    elif kind == 'towers':
        s += road('M-20 475 H260 Q360 475 420 420 L505 335 Q550 295 780 295')
        s += road('M275 -20 V155 Q275 230 320 280 L400 435',39)
        for x,y,w,h in [(55,70,143,184),(392,56,174,160),(545,398,154,157)]:
            s += roof(x,y,w,h,secondary)
            s += roof(x+25,y+23,w-52,h-45,c,accent)
            s += rect(x+36,y+36,w-74,h-72,'#1A2B4B',5)
        s += circle(435,263,58,secondary,'#8296A1',2)
        s += circle(435,263,39,c,extra,5)
        s += rect(60,535,170,50,secondary,4)
        s += path('M365 388 L433 347','#B7CAD1',18)
    elif kind == 'quay':
        s += path('M790 230 Q545 230 490 400 T180 660','#143E55',215)
        s += road('M-30 525 Q160 520 330 410 T560 170 Q650 100 780 115')
        for i,(x,y,a) in enumerate([(35,370,5),(105,340,12),(180,285,23),(265,220,32),(360,140,34),(455,60,15)]):
            s += roof(x,y,47+8*(i%2),90+10*(i%3),c if i%2 else secondary,accent,a)
        s += rect(70,70,170,125,'#6D757E',8)
        s += roof(50,57,200,57,c,accent)
        s += circle(160,155,18,'#9BB5B9')
        s += path('M330 485 Q475 403 543 278','#6F999F',8)
    elif kind == 'shops':
        s += road('M-20 265 H210 Q280 265 330 325 L460 450 H785')
        s += road('M215 -20 V90 Q215 135 260 150 H555 Q625 150 625 240 V450',34)
        s += rect(435,295,140,80,'#637486',8)
        s += circle(455,218,78,secondary,'#97B4BC',2)
        s += circle(455,218,56,c,accent,7)
        s += circle(455,218,29,'#253850',extra,3)
        for i,(x,y,w,h) in enumerate([(45,100,125,87),(50,340,73,114),(157,358,72,90),(65,500,156,57),(300,55,105,55),(437,55,105,50),(545,524,121,61)]):
            s += roof(x,y,w,h,secondary if i%2 else c,accent if i%2 else extra)
        s += path('M140 339 V491','#D0CDD0',8,'9 10')
        s += parking(320,509,1,4)
    elif kind == 'retail':
        s += road('M-20 545 H575 Q685 545 685 430 V-20')
        s += road('M-20 95 H510 Q575 95 575 160 V200',32)
        s += roof(60,170,370,150,c,accent)
        s += roof(365,260,113,60,secondary,extra)
        s += parking(80,360,2,10)
        s += roof(526,240,105,75,secondary,accent)
        s += roof(552,363,76,109,c,extra)
        s += circle(500,145,24,'#697D76',extra,3)
    elif kind == 'workshops':
        s += road('M-20 170 H180 Q245 170 285 215 L410 345 Q445 375 510 375 H775')
        s += road('M85 650 V355 Q85 300 140 300 H230',32)
        s += road('M590 375 V510 Q590 552 530 552 H85',32)
        for i,(x,y,w,h) in enumerate([(40,35,145,82),(254,48,224,100),(560,70,145,150),(173,355,90,156),(335,427,170,78)]):
            s += roof(x,y,w,h,c if i%2 else secondary,accent)
        s += road('M490 375 V245 H720 V375',20)
        s += parking(523,282,1,4)
        s += path('M280 508 V370 L250 341','#BBD0C8',7,'10 10')
    elif kind == 'docks':
        s += rect(550,0,200,620,'#143E55')
        s += road('M-20 350 H325 Q385 350 385 300 V-20')
        s += road('M-20 565 H435 Q485 565 485 515 V225',33)
        s += roof(40,55,265,101,c)
        s += roof(40,210,265,85,c)
        s += roof(70,435,255,74,secondary)
        s += rect(526,70,70,180,'#6C7E86')
        s += rect(526,365,110,190,'#6C7E86')
        for x,y in [(531,140),(561,446)]:
            s += path(f'M{x-22} {y+42} V{y-35} H{x+105} M{x+25} {y+42} V{y-35}',accent,11)
            s += path(f'M{x+2} {y-35} L{x+94} {y-14}',accent,4)
        s += path('M435 60 V215 M425 415 V490','#B8CDD0',3,'8 12')
    return s


def board(b, number):
    accent = b['colors'][2]
    s = '<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1320" viewBox="0 0 1800 1320">'
    s += f'<title>{escape(b["name"])} — approved district identity brief</title>'
    s += '<g font-family="DejaVu Sans, sans-serif">'
    s += rect(0,0,1800,1320,'#102332')
    s += text(55,46,'BRACKETT / STAGE 03 / DISTRICT IDENTITY / APPROVED DIRECTION',17,MUTED,600)
    s += text(55,112,f'{number:02d}  {b["name"]}',48,INK,700)
    s += text(55,160,b['role'],26,accent)
    s += text(55,201,b['mood'],19,MUTED)
    s += '<defs><clipPath id="motif"><rect width="750" height="620" rx="15"/></clipPath></defs>'
    s += f'<g transform="translate(55 240)" clip-path="url(#motif)">{motif(b)}</g>'
    s += text(75,890,'ROOF + OPEN-SPACE MOTIF',16,accent,700)
    for i,label in enumerate(b['diagram_labels']):
        s += text(75,926+i*28,f'{i+1:02d}  {label}',20,INK)
    s += text(75,1020,'Schematic only: no scale, height or route validation.',17,MUTED)
    fields = [('PLAY','play'),('ARCHITECTURE','architecture'),('STREETS + ROUTES','roads'),
              ('PROP FAMILIES','props'),('LIGHT + ACCENT PLACEMENT','lighting'),('SIGNAGE + HUMOUR','humor')]
    for i,(label,key) in enumerate(fields):
        x,y = 870+(i%2)*445,260+(i//2)*250
        s += text(x,y,label,16,accent,700)
        s += para(x,y+38,b[key],width=36)
    for i,(color,name) in enumerate(zip(b['colors'],b['color_names'])):
        x = 870+(i%2)*445
        y = 982+(i//2)*48
        s += rect(x,y-18,28,28,color,4,'#8296A1')
        s += text(x+40,y+3,name,18,MUTED)
    s += path('M55 1060 H1745','#455B68',1)
    s += text(55,1098,'LANDMARK SEED',16,accent,700)
    s += para(255,1098,b['landmark'],width=122,size=20,leading=28)
    s += text(55,1190,'M1 RELATIONSHIP',16,accent,700)
    s += para(255,1190,b['m1'],width=122,size=20,leading=28)
    s += text(55,1290,'ALL NAMES ARE PLACEHOLDERS • Fixed blue-hour direction • Original 2D concept diagram, not game art',17,MUTED)
    return s+'</g></svg>'


def scale_comparison():
    """Compare three cropped land samples using identical metres-to-pixels scaling."""
    s = '<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1180" viewBox="0 0 1800 1180">'
    s += '<title>Unequal blocks and streets — three land samples at the same scale</title>'
    s += '<g font-family="DejaVu Sans, sans-serif">'+rect(0,0,1800,1180,'#102332')
    s += text(55,48,'BRACKETT / SPATIAL REFINEMENT / PROPOSED PROPORTIONS',17,MUTED,600)
    s += text(55,112,'Different uses need different amounts of space.',43,INK,700)
    s += text(55,159,'Each square shows 180 × 180 m at the same scale. These are land samples, not district boundaries.',23,MUTED)
    titles = ['SMALL RESIDENTIAL PLOTS','MIXED COMMERCIAL / WORKSHOPS','LARGE WAREHOUSE / YARD SITES']
    captions = [
        'Many small house-and-garden plots occupy several unequal blocks. Narrow two-way streets connect to larger routes outside this crop.',
        'Several shops can share a short block opposite one larger workshop site. A four-lane connector, ordinary street and narrow service link have different jobs.',
        'Long roofs and loading aprons need much more land. Broad two-lane freight streets provide turning space without making every road four lanes.'
    ]

    def street(d, width, foot=2):
        return path(d,'#819098',width+2*foot)+path(d,'#172D40',width)

    def plot(x,y,w,h):
        return rect(x,y,w,h,'#29454B',0, '#758D8F',0.4)

    def building(x,y,w,h,color):
        return rect(x,y,w,h,color,0.8,'#ACB8BD',0.35)

    def car(x,y):
        return rect(x,y,1.8,4.2,'#F4EEDD',0.5)

    for index in range(3):
        ox=55+index*575
        s += text(ox,214,titles[index],20,['#FFD2A0','#ED73BC','#FFBD74'][index],700)
        s += f'<defs><clipPath id="sample{index}"><rect width="180" height="180"/></clipPath></defs>'
        s += f'<g transform="translate({ox} 240) scale({520/180})" clip-path="url(#sample{index})">'
        s += rect(0,0,180,180,'#203644')
        if index == 0:
            s += street('M145 -10 V190',7)
            s += street('M-10 55 H145',7)
            s += street('M-10 118 Q50 118 70 132 H145',7)
            s += path('M145 -10 V190','#A5B2B7',0.3,'3 4')
            for row,(y,h) in enumerate([(12,29),(75,29),(149,28)]):
                x=5
                for col,w in enumerate([15,18,14,20,16,17,15]):
                    s += plot(x,y,w,h)
                    s += building(x+3,y+4,8+(col%3),11+(row%2)*3,'#596B83' if col%2 else '#80647A')
                    if col%3==1:s += car(x+w-4,y+h-6)
                    x += w+2
            for y,h in [(8,33),(68,45),(144,31)]:
                s += plot(157,y,22,h)+building(161,y+4,12,15,'#596B83')
            s += car(146,88)
        elif index == 1:
            s += street('M25 -10 V190',14,4)
            for x in [21.5,25,28.5]:
                s += path(f'M{x} -10 V190','#A5B2B7',0.3,'3 4')
            s += street('M25 112 H190',9,4)
            s += street('M105 112 V44 H190',4.5,1.5)
            for x,y,w,h in [(45,7,22,28),(70,7,25,28),(45,43,49,54),(115,6,64,29),(114,53,65,43),(45,129,47,46),(102,129,77,47)]:
                s += plot(x,y,w,h)
            for x,y,w,h in [(48,11,15,18),(74,10,17,20),(49,48,25,16),(48,72,31,20),(120,10,52,19),(121,59,42,16),(48,134,16,25),(72,134,16,18),(120,148,52,23)]:
                s += building(x,y,w,h,'#655A76' if x<100 else '#426C74')
            for x,y in [(84,52),(87,82),(156,84),(162,84),(111,141),(118,141),(20,62),(27,154)]:
                s += car(x,y)
        else:
            s += street('M15 -10 V190',10,2)
            s += street('M15 94 H190',10,2)
            s += path('M15 -10 V190 M15 94 H190','#A5B2B7',0.35,'3 4')
            s += plot(29,5,146,76)+plot(29,108,100,68)+plot(136,108,40,68)
            s += building(44,12,115,43,'#4C627F')
            s += rect(44,58,115,18,'#657982')
            s += building(40,128,77,39,'#4C627F')
            s += rect(40,114,77,10,'#657982')
            s += building(143,114,25,19,'#426C74')
            for x in [64,88,112,136]:
                s += path(f'M{x} 58 V73','#C2CECA',0.4)
            for x,y in [(33,61),(33,68),(141,146),(145,146),(17,42),(113,95)]:
                s += car(x,y)
        s += '</g>'
        s += para(ox,807,captions[index],width=44,size=21,leading=29)
    s += path('M55 982 H1745','#455B68',1)
    s += text(55,1021,'DISTRICT ≠ BLOCK ≠ PLOT ≠ BUILDING',22,'#FFC580',700)
    s += para(55,1060,'Districts have unequal areas. Blocks contain different numbers and sizes of plots. Roads vary by role, including within a district.',width=136,size=21,leading=28)
    s += text(55,1148,'Shared car size: 4.2 × 1.8 m • Illustration values only; final lane widths, turns and camera readability remain unvalidated.',18,MUTED)
    return s+'</g></svg>'


def main():
    briefs = json.loads((ROOT/'briefs.json').read_text())
    for index,brief in enumerate(briefs,1):
        source = ROOT/f'{brief["id"]}.svg'
        source.write_text(board(brief,index))
        subprocess.run(['rsvg-convert',str(source),'-o',str(source.with_suffix('.png'))],check=True)
    source = ROOT/'10-urban-scale.svg'
    source.write_text(scale_comparison())
    subprocess.run(['rsvg-convert',str(source),'-o',str(source.with_suffix('.png'))],check=True)


if __name__ == '__main__':
    main()
