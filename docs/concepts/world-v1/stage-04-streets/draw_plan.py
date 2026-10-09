#!/usr/bin/env python3
"""Draw a reference-only road/block proposal; never author production city geometry."""

from collections import defaultdict
from html import escape
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import textwrap


ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('macro', ROOT.parent/'stage-02-city-structure/draw_maps.py')
macro = importlib.util.module_from_spec(spec)
spec.loader.exec_module(macro)
LAND = macro.LAND
ZONES = macro.OPTIONS[0]
BOUNDARIES_PATH = ROOT/'district-editor/brackett-districts.json'
BOUNDARIES = json.loads(BOUNDARIES_PATH.read_text())['districts']
assert [(d['id'], d['name']) for d in BOUNDARIES] == [
    (i+1, name) for i, (name, _) in enumerate(macro.DISTRICTS)]
INK, MUTED = '#F4EEDD', '#B5C7D0'
# Carriageway and total corridor widths in metres, illustrative at this stage.
TYPES = {
    'avenue': (14, 24, '#F5C06E', '4 lanes / selected connector'),
    'street': (9, 17, '#91D5DE', '2 lanes / ordinary street'),
    'local': (7, 12, '#A8B7D5', '2 lanes / smaller local street'),
    'freight': (10, 14, '#ED9F86', '2 broad lanes / working access'),
    'service': (4.5, 7.5, '#B7CAA8', '1 lane / service link candidate'),
}
WATER_PATH = 'M320 425 C263 425 242 482 267 519 C286 540 315 548 316 566 L315 690 L385 690 L387 562 C452 527 466 451 409 433 C385 421 350 417 320 425 Z'


def bezier(a,b,c,d,t):
    return tuple((1-t)**3*a[k]+3*(1-t)**2*t*b[k]+3*(1-t)*t*t*c[k]+t**3*d[k] for k in (0,1))


def water_polygon():
    result=[]
    for controls in [((320,425),(263,425),(242,482),(267,519)),
                     ((267,519),(286,540),(315,548),(316,566))]:
        result.extend(bezier(*controls,i/16) for i in range(17))
    result += [(315,690),(385,690),(387,562)]
    for controls in [((387,562),(452,527),(466,451),(409,433)),
                     ((409,433),(385,421),(350,417),(320,425))]:
        result.extend(bezier(*controls,i/16) for i in range(17))
    return result


WATER = water_polygon()


def smooth(points):
    result=[points[0]]
    for i in range(len(points)-1):
        p0,p1=points[max(0,i-1)],points[i]
        p2,p3=points[i+1],points[min(len(points)-1,i+2)]
        c1=tuple(p1[k]+(p2[k]-p0[k])/6 for k in (0,1))
        c2=tuple(p2[k]-(p3[k]-p1[k])/6 for k in (0,1))
        steps=max(3,math.ceil(math.dist(p1,p2)/10))
        result.extend(bezier(p1,c1,c2,p2,j/steps) for j in range(1,steps+1))
    return result


def project(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    den=dx*dx+dy*dy
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)) if den else 0
    q=(a[0]+t*dx,a[1]+t*dy)
    return math.dist(p,q),q


def roads():
    result=[]
    def add(name,kind,points,snap=False,dead=False,straight=False):
        pts=list(points)
        if snap:
            for end in ([0] if dead else [0,-1]):
                distance,q=min(project(pts[end],a,b) for r in result for a,b in zip(r['points'],r['points'][1:]))
                assert distance<32,(name,end,distance)
                pts[end]=q
        result.append(dict(name=name,kind=kind,points=pts if straight else smooth(pts),dead=dead))
    add('North coast','street',macro.COAST[:7])
    add('Working coast','freight',macro.COAST[6:10])
    add('Retail coast','street',macro.COAST[9:])
    add('Western coast','street',[(309,590),(235,525),(160,450),(110,360),(100,270),(125,185)])
    add('Harbour bridge','street',[(309,590),(400,590)])
    add('Western neighbourhood circuit','street',ZONES['routes'][0])
    add('Campus-downtown link','street',[(370,245),(565,245)])
    add('Central avenue / downtown grid','avenue',[(565,245),(850,245),(850,350)],straight=True)
    add('Central avenue / southern return','avenue',[(850,350),(770,455),(565,440),(585,600)])
    add('Apartment-commercial link','street',[(480,150),(450,340),(565,440)])
    add('Downtown east link','street',[(850,350),(950,350)],straight=True)
    add('Working approach','freight',[(950,350),(1045,380),(1080,330)])
    add('Repair circuit','street',[(770,455),(930,500),(1045,380)])
    add('Port-retail link','freight',[(930,500),(930,580)])
    add('Quay inland return','local',[(205,345),(235,525)])
    add('Commercial west approach','street',[(450,340),(510,345),(570,350)])
    add('Downtown south cross street','street',[(570,350),(850,350)],straight=True)
    coast=result[0]['points']
    for x,end_y in [(650,350),(735,350),(850,245),(950,350)]:
        a,b=next((a,b) for a,b in zip(coast,coast[1:]) if a[0]<=x<=b[0])
        y=a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0])
        add(f'Downtown grid north-south {x}','street',[(x,y),(x,end_y)],straight=True)
    add('Downtown short eastern cross street','street',[(850,300),(950,300)],straight=True)
    local=[
        ('Campus courts','local',[(320,110),(340,165),(310,225)],False),
        ('West crescent','local',[(220,205),(230,250),(195,285),(205,345)],False),
        ('East crescent','local',[(370,245),(325,290),(330,350),(360,395)],False),
        ('Housing north link','local',[(230,250),(280,265),(325,290)],False),
        ('Housing south link','local',[(195,285),(245,318),(330,350)],False),
        ('Housing court','local',[(280,265),(290,283),(282,301)],True),
        ('Quay neighbourhood','local',[(110,360),(150,395),(205,410),(180,450),(160,450)],False),
        ('Quay short link','local',[(150,395),(175,373),(205,345)],False),
        ('Quay access court','local',[(215,407),(250,400),(290,405)],True),
        ('Apartment west','local',[(405,131),(400,185),(370,245)],False),
        ('Apartment court link','local',[(400,185),(434,202),(465,215)],False),
        ('Apartment east','street',[(560,157),(555,200),(565,245)],False),
        ('Apartment cross street','local',[(465,205),(555,200)],False),
        ('Commercial west link','street',[(565,245),(570,350)],False),
        ('M1 mixed-use west','local',[(650,350),(655,390),(660,448)],False),
        ('M1 mixed-use middle','local',[(735,350),(715,390),(700,452)],False),
        ('M1 mixed-use east','local',[(815,347),(785,390),(770,455)],False),
        ('M1 small cross-link','local',[(655,390),(715,390),(785,390)],False),
        ('Hall and plaza return','local',[(450,340),(470,400),(505,450),(490,535),(450,575)],False),
        ('Shop link','local',[(505,450),(565,440)],False),
        ('Harbour-retail link','local',[(490,535),(580,550)],False),
        ('Retail access','street',[(580,530),(705,530),(820,550),(930,580)],False),
        ('Retail rear return','local',[(705,530),(735,575),(775,620)],False),
        ('Workshop west','local',[(850,350),(895,405),(930,500)],False),
        ('Workshop cross-link','local',[(895,405),(970,435),(1000,434)],False),
        ('Workshop service link','service',[(970,435),(960,482)],False),
        ('Working south court','local',[(930,500),(975,540),(1020,525)],False),
        ('Dock loading access','freight',[(1100,370),(1090,390),(1085,425),(1090,445)],True),
    ]
    for name,kind,points,dead in local:
        add(name,kind,points,True,dead)
    return result


def cross(a,b):
    return a[0]*b[1]-a[1]*b[0]


def split_graph(routes):
    """Split drawing intersections to extract block faces; this is not a lane graph."""
    segments=[(a,b) for r in routes for a,b in zip(r['points'],r['points'][1:]) if math.dist(a,b)>1e-6]
    splits=[{0.0,1.0} for _ in segments]
    for i,(a,b) in enumerate(segments):
        u=(b[0]-a[0],b[1]-a[1])
        for j in range(i+1,len(segments)):
            c,d=segments[j]
            if max(a[0],b[0])+1e-5<min(c[0],d[0]) or max(c[0],d[0])+1e-5<min(a[0],b[0]):continue
            if max(a[1],b[1])+1e-5<min(c[1],d[1]) or max(c[1],d[1])+1e-5<min(a[1],b[1]):continue
            v=(d[0]-c[0],d[1]-c[1]); den=cross(u,v)
            if abs(den)<1e-9:continue
            ac=(c[0]-a[0],c[1]-a[1]);t=cross(ac,v)/den;q=cross(ac,u)/den
            if -1e-7<=t<=1+1e-7 and -1e-7<=q<=1+1e-7:
                splits[i].add(max(0,min(1,t)));splits[j].add(max(0,min(1,q)))
    graph=defaultdict(set)
    for (a,b),ts in zip(segments,splits):
        pts=[(round(a[0]+t*(b[0]-a[0]),4),round(a[1]+t*(b[1]-a[1]),4)) for t in sorted(ts)]
        for p,q in zip(pts,pts[1:]):
            if p!=q:graph[p].add(q);graph[q].add(p)
    ordered={p:sorted(qs,key=lambda q:math.atan2(q[1]-p[1],q[0]-p[0])) for p,qs in graph.items()}
    seen=set();faces=[]
    for p,qs in ordered.items():
        for q in qs:
            if (p,q) in seen:continue
            face=[];a,b=p,q
            while (a,b) not in seen:
                seen.add((a,b));face.append(a)
                ns=ordered[b];c=ns[(ns.index(a)-1)%len(ns)];a,b=b,c
            area=sum(cross(a,b) for a,b in zip(face,face[1:]+face[:1]))/2
            if area>100:faces.append((area,face))
    remaining=set(graph);components=0
    while remaining:
        components+=1;pending=[remaining.pop()]
        while pending:
            for q in graph[pending.pop()]:
                if q in remaining:remaining.remove(q);pending.append(q)
    return graph,faces,components


def inside(p,poly):
    x,y=p;hit=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
    return hit


def motif_district(p):
    """Keep the existing illustrative roofs fixed while owner boundaries change."""
    return min(range(9),key=lambda i:math.dist(p,ZONES['seeds'][i])**2-ZONES['weights'][i])


def building_motifs(routes):
    """Place sparse explanatory plot/roof symbols, not an asset or world-layout generator."""
    road_segments=[(a,b,TYPES[r['kind']][1]/2+2) for r in routes for a,b in zip(r['points'],r['points'][1:])]
    road_segments.extend((a,b,3) for a,b in foot_links(routes))
    bins=defaultdict(list)
    for segment in road_segments:
        a,b,clearance=segment
        for ix in range(math.floor((min(a[0],b[0])-clearance)/40),math.floor((max(a[0],b[0])+clearance)/40)+1):
            for iy in range(math.floor((min(a[1],b[1])-clearance)/40),math.floor((max(a[1],b[1])+clearance)/40)+1):
                bins[ix,iy].append(segment)
    # Different grain per district; placements remain diagram examples only.
    dimensions=[(40,32,28,18),(18,27,10,13),(39,38,28,23),(55,51,29,26),
                (19,27,13,17),(28,31,19,19),(110,85,75,32),(44,39,30,19),(95,65,72,30)]
    result=[]
    occupied=[]
    for zone in [8,6,3,2,7,0,5,4,1]:
        dx,dy,w,h=dimensions[zone]
        step=9
        for row,y in enumerate(range(65,640,step)):
            for col,x in enumerate(range(85,1190,step)):
                x=x+(row%2)*step*.17; y0=y+(col%3)*2
                w0=w*(0.85+0.10*((row+col)%3));h0=h*(0.85+0.1*(col%3))
                p=(x+w0/2,y0+h0/2)
                if motif_district(p)!=zone:continue
                corners=[(x-2,y0-2),(x+w0+2,y0-2),(x+w0+2,y0+h0+7),(x-2,y0+h0+7)]
                angle=(55 if p[1]<470 else -25) if zone==8 else 0
                radians=math.radians(angle)
                def rotate(v):
                    u,vv=v[0]-p[0],v[1]-p[1]
                    return (p[0]+u*math.cos(radians)-vv*math.sin(radians),p[1]+u*math.sin(radians)+vv*math.cos(radians))
                corners=[rotate(v) for v in corners]
                box=(min(v[0] for v in corners)-1,min(v[1] for v in corners)-1,
                     max(v[0] for v in corners)+1,max(v[1] for v in corners)+1)
                if any(box[0]<b[2] and box[2]>b[0] and box[1]<b[3] and box[3]>b[1] for b in occupied):continue
                samples=corners+[p]+[tuple((a[k]+b[k])/2 for k in (0,1)) for a,b in zip(corners,corners[1:]+corners[:1])]
                if not all(inside(v,LAND) and not inside(v,WATER) for v in samples):continue
                near={s for ix in range(math.floor(box[0]/40),math.floor(box[2]/40)+1)
                      for iy in range(math.floor(box[1]/40),math.floor(box[3]/40)+1) for s in bins[ix,iy]}
                if any(project(v,a,b)[0]<clearance for v in samples for a,b,clearance in near):continue
                if any(inside(a,corners) for a,b,_ in near):continue
                if 195<x<315 and 115<y0<185:continue
                result.append((zone,x,y0,w0,h0,angle))
                occupied.append(box)
    return result


def text(x,y,value,size=20,color=INK,weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(value)}</text>'


def para(x,y,value,width=40,size=20,leading=28):
    return ''.join(text(x,y+i*leading,line,size,MUTED) for i,line in enumerate(textwrap.wrap(value,width)))


def path(points):
    return 'M '+' L '.join(f'{x:.3f},{y:.3f}' for x,y in points)


def stroke(d,color,width,dash=''):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>'


def foot_links(routes):
    links=[]
    for a,b in [((282,301),(325,310)),((290,405),(321,390)),((680,360),(700,390))]:
        a=min(project(a,c,d) for r in routes for c,d in zip(r['points'],r['points'][1:]))[1]
        b=min(project(b,c,d) for r in routes for c,d in zip(r['points'],r['points'][1:]))[1]
        links.append((a,b))
    return links


def base_map(routes,faces,motifs,neutral=False,labels=True):
    s=f'<polygon points="{macro.polygon(LAND)}" fill="#304750" stroke="#98B7BE" stroke-width="2"/>'
    s+='<g clip-path="url(#land)">'
    if not neutral:
        for i, district in enumerate(BOUNDARIES):
            points=' '.join(f'{x},{y}' for x,y in district['points'])
            s+=f'<polygon data-district="{district["id"]}" points="{points}" fill="{macro.COLORS[i]}" fill-opacity=".45"/>'
    for area,face in faces:
        s+=f'<polygon points="{macro.polygon(face)}" fill="'+('#52636B' if neutral else '#789091')+'" fill-opacity=".17"/>'
    for zone,x,y,w,h,angle in motifs:
        color='#A6B4B9' if neutral else ['#85B3A6','#AB9BAE','#A1ACC7','#8CAEC9','#B8A29D','#B294B8','#C1B38C','#96ACB0','#9FB1C4'][zone]
        s+=f'<g transform="rotate({angle} {x+w/2} {y+h/2})">'
        s+=f'<rect x="{x-2:.2f}" y="{y-2:.2f}" width="{w+4:.2f}" height="{h+9:.2f}" fill="none" stroke="{color}" stroke-width=".5" opacity=".55"/>'
        s+=f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="1" fill="{color}" opacity=".7"/>'
        if zone==3:
            s+=f'<rect x="{x+5:.2f}" y="{y+5:.2f}" width="{w-10:.2f}" height="{h-10:.2f}" fill="#425A70"/>'
        s+='</g>'
    # Reserve a recognisable field; it is an open-space symbol, not a regulation sports layout.
    s+='<rect x="210" y="127" width="98" height="53" rx="15" fill="#3A6C5D" stroke="#A9C6AF" stroke-width="1.5"/>'
    s+='<rect x="222" y="137" width="74" height="33" fill="none" stroke="#A9C6AF" stroke-width="1"/>'
    for layer in (1,0):
        for r in routes:
            if r['name']=='Harbour bridge':continue
            carriage,corridor,color,_=TYPES[r['kind']]
            s+=stroke(path(r['points']),'#60727D' if layer else '#172B39',corridor if layer else carriage)
            if r['dead']:
                x,y=r['points'][-1];radius=15 if r['kind']=='freight' else 10
                s+=f'<circle cx="{x}" cy="{y}" r="{radius+(2 if layer else 0)}" fill="'+('#60727D' if layer else '#172B39')+'"/>'
    for r in routes:
        if r['name']=='Harbour bridge':continue
        color= '#C2CED0' if neutral else TYPES[r['kind']][2]
        s+=stroke(path(r['points']),color,1.5 if r['kind']=='avenue' else .8,'3 3' if r['kind']=='service' else '')
        if r['kind']=='avenue':s+=stroke(path(r['points']),color,3.5)+stroke(path(r['points']),'#172B39',1.1)
    s+=f'<path d="{WATER_PATH}" fill="#102C40" stroke="#91B6C2" stroke-width="1.4"/>'
    bridge=next(r for r in routes if r['name']=='Harbour bridge')
    s+=stroke(path(bridge['points']),'#A6A6AD',17)+stroke(path(bridge['points']),'#172B39',9)+stroke(path(bridge['points']),'#EC9EBC',2)
    for a,b in foot_links(routes):
        s+=stroke(path([a,b]),'#DDE1BE',2,'2 4')
    # This is the accepted area envelope, deliberately without equal-size lot rectangles.
    s+='<rect x="610" y="355" width="260" height="163" rx="3" fill="none" stroke="#FFE082" stroke-width="2.5" stroke-dasharray="7 5"/>'
    s+='</g>'
    if labels:
        for i,(x,y) in enumerate([(186,194),(270,351),(498,180),(872,254),(475,480),(519,385),(660,581),(953,402),(1122,462)]):
            s+=f'<circle cx="{x}" cy="{y}" r="13" fill="#102332" stroke="#D6E0DD" stroke-width="1"/>'
            s+=text(x-4 if i<8 else x-4,y+4,str(i+1),12,INK,700)
        s+=text(322,485,'HARBOUR',10,'#A7D0D7')
        s+=text(618,343,'M1 / AREA REFERENCE',12,'#FFE082',700)
        for x,y in [(565,245),(585,600)]:
            s+=f'<circle cx="{x}" cy="{y}" r="7" fill="#F5C06E" stroke="#102332" stroke-width="2"/>'
    return s


def shell(width,height,title):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><title>{escape(title)}</title><style>text{{font-family:DejaVu Sans,sans-serif}}</style><rect width="100%" height="100%" fill="#0C1B29"/><defs><clipPath id="land"><polygon points="{macro.polygon(LAND)}"/></clipPath></defs>'


def overview(routes,faces,motifs,neutral=False):
    title='The same plan, without district colours' if neutral else 'Connected neighbourhoods. Unequal blocks.'
    s=shell(2400,1500,title)
    s+=text(55,48,'BRACKETT / STAGE 4A / WHOLE-CITY ROAD AND BLOCK PROPOSAL',20,'#91D5DE',600)
    s+=text(55,112,title,49,INK,700)
    s+=text(55,162,'Owner-drawn district boundaries; proposed local streets, lane hierarchy and block subdivisions.',25,MUTED)
    s+=f'<g transform="translate(30 225) scale(1.5)">{base_map(routes,faces,motifs,neutral)}</g>'
    s+=text(1990,233,'STREET HIERARCHY',23,'#91D5DE',700)
    for i,(kind,(carriage,corridor,color,label)) in enumerate(TYPES.items()):
        y=280+i*101
        s+=stroke(f'M1993 {y} H2050',color,7)+text(2070,y+7,kind.upper(),20,INK,700)
        s+=text(1993,y+37,label,19,MUTED)
    s+=text(1990,810,'DISTRICTS / PLACEHOLDERS',21,'#91D5DE',700)
    for i,(name,_) in enumerate(macro.DISTRICTS):s+=text(1990,853+i*34,f'{i+1:02d}  {name}',22,INK)
    s+=text(1990,1210,'Yellow dashed: M1 area',20,'#FFE082')
    s+=text(1990,1241,'Dots: avenue-end junctions',18,MUTED)
    s+=text(1990,1272,'Dotted links: walking only',18,MUTED)
    s+=text(55,1300,'WEST: SMALL PLOTS + SHORT LINKS',22,'#91D5DE',700)
    s+=text(810,1300,'CENTRE: MIXED BLOCKS + SELECTED AVENUE',22,'#F5C06E',700)
    s+=text(55,1342,'Campus grounds, curved housing streets and older quay plots.',22,MUTED)
    s+=text(810,1342,'Large tower sites, short shop blocks and larger retail courts.',22,MUTED)
    s+=stroke('M55 1400 H355 M55 1393 V1407 M205 1393 V1407 M355 1393 V1407',INK,2)
    s+=text(55,1438,'0',17)+text(185,1438,'100',17)+text(327,1438,'200 m',17)
    s+=text(470,1408,'EAST: LARGER WORKING SITES / BROAD TWO-LANE ACCESS',22,'#ED9F86',700)
    s+=text(470,1445,'Flat island ≈ 1.2 × 0.65 km • Blocks follow streets; plot/roof symbols are illustrative • No traffic or camera validation',18,MUTED)
    return s+'</svg>'


def details(routes,faces,motifs):
    s=shell(2400,1250,'Three neighbourhoods at one scale')
    s+=text(55,48,'BRACKETT / STAGE 4A / SAME-SCALE EXTRACTS FROM THE PROPOSED CITY PLAN',20,'#91D5DE',600)
    s+=text(55,112,'The difference is in the land pattern.',49,INK,700)
    s+=text(55,162,'Each window is a 220 × 220 m crop of the same plan. District and block sizes are not tied to the frame.',24,MUTED)
    samples=[(145,200,'CURVED HOUSING + SMALL PLOTS','Frequent connections and small plots make walking alternatives useful. Some courts end for cars while foot links continue.'),
             (605,320,'M1 AREA / REVISED DISTRICT CONTEXT','The owner-drawn boundaries place more of this area in Glassward. The six-theme M1 layout still needs its own fit study.'),
             (950,340,'WORKSHOPS TO LOADING YARDS','Fewer through streets leave larger working sites. Broad two-lane access meets smaller repair streets and a loading court.')]
    for i,(cx,cy,title,caption) in enumerate(samples):
        ox=55+i*790
        s+=text(ox,228,title,22,['#A8B7D5','#F5C06E','#ED9F86'][i],700)
        s+=f'<defs><clipPath id="crop{i}"><rect x="{ox}" y="265" width="710" height="710"/></clipPath></defs><g clip-path="url(#crop{i})">'
        s+=f'<rect x="{ox}" y="265" width="710" height="710" fill="#102C40"/>'
        scale=710/220
        s+=f'<g transform="translate({ox-cx*scale} {265-cy*scale}) scale({scale})">{base_map(routes,faces,motifs,False,False)}</g></g>'
        s+=para(ox,1020,caption,54,23,32)
    s+=text(55,1205,'Concept plan only • Road widths are provisional • Yellow dashed line locates M1; it does not authorize a larger playable area',20,MUTED)
    return s+'</svg>'


def downtown_detail(routes,faces,motifs):
    s=shell(1800,1250,'Glassward: a stronger downtown grid')
    s+=text(55,48,'BRACKETT / STAGE 4A / OWNER-DIRECTED DOWNTOWN REVISION',18,'#91D5DE',600)
    s+=text(55,109,'Glassward: a stronger downtown grid.',43,INK,700)
    s+=text(55,156,'Straight cross streets and rectangular blocks; varied plot sizes and curved district edges.',22,MUTED)
    s+='<defs><clipPath id="downtown"><rect x="55" y="200" width="1690" height="845"/></clipPath></defs>'
    s+='<g clip-path="url(#downtown)"><rect x="55" y="200" width="1690" height="845" fill="#102C40"/>'
    scale=1690/460
    s+=f'<g transform="translate({55-540*scale} {200-155*scale}) scale({scale})">{base_map(routes,faces,motifs,False,False)}</g></g>'
    s+=text(55,1100,'A clear downtown pattern, without equal-sized blocks everywhere.',26,'#91D5DE',700)
    s+=text(55,1145,'The grid meets the curved coast to the north and the smaller commercial streets to the south.',22,MUTED)
    s+=text(55,1208,'Proposal only • Same geometry as the city plan • Junction corners, lane turns and camera visibility remain unvalidated',18,MUTED)
    return s+'</svg>'


def main():
    r=roads();graph,faces,components=split_graph(r);motifs=building_motifs(r)
    print(f'{len(r)} road strokes; {components} undirected drawing components; {len(faces)} bounded faces; {len(motifs)} plot/roof motifs')
    for name,content in [('01-city-road-block-plan',overview(r,faces,motifs)),
                         ('02-city-without-zone-colours',overview(r,faces,motifs,True)),
                         ('03-same-scale-extracts',details(r,faces,motifs)),
                         ('04-downtown-grid',downtown_detail(r,faces,motifs))]:
        source=ROOT/f'{name}.svg';source.write_text(content)
        subprocess.run(['rsvg-convert',str(source),'-o',str(source.with_suffix('.png'))],check=True)
    report=dict(road_strokes=len(r),drawing_components=components,bounded_centerline_faces=len(faces),
                centerline_face_areas_m2=sorted(round(a,1) for a,f in faces),plot_roof_motifs=len(motifs),
                note='Drawing topology only. Faces include water/road area; not net developable blocks or a directed traffic graph.')
    (ROOT/'drawing-check.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
