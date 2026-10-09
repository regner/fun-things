"""Measure source attachment contacts and reserved envelope independently of authoring."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];E=R/'docs/assets/production/city_shop_fittings_08-evidence'
col=bpy.data.collections['export_city_shop_fittings_08'];report={}
def bounds(name):
    o=bpy.data.objects[name];p=[o.matrix_world@v.co for v in o.data.vertices]
    return [[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]
def near(actual,expected):
    assert all(abs(a-b)<1e-6 for a,b in zip(actual,expected)),(actual,expected)
plate=bounds('wall_backplate');near(plate[0],[-.1,0,-.48]);near(plate[1],[.1,.03,.48])
body=bounds('formed_blade_shell');near(body[0],[-.061,.2,-.58]);near(body[1],[.061,.88,.58])
for level,z in [('lower',-.36),('upper',.36)]:
    arm=bounds('cantilever_arm_'+level);near(arm[0],[-.04,.025,z-.032]);near(arm[1],[.04,.25,z+.032])
    assert plate[1][1]-arm[0][1]>.0049
    assert arm[1][1]-body[0][1]>.0499
    gusset=bounds('tapered_gusset_'+level)
    assert gusset[0][1]<.03 and gusset[1][1]>.23
    report[level]={'arm_bounds':arm,'gusset_bounds':gusset,'arm_plate_overlap_y_m':plate[1][1]-arm[0][1],'arm_shell_overlap_y_m':arm[1][1]-body[0][1]}
for side,x in [('left',-.065),('right',.065)]:
    for level,z in [('lower',-.42),('upper',.42)]:
        box=bounds('captive_hex_'+side+'_'+level)
        assert abs((box[0][0]+box[1][0])/2-x)<1e-6
        assert abs((box[0][2]+box[1][2])/2-z)<1e-6
        assert box[0][1]<.03 and box[1][1]>.03
for side,sign in [('positive_x',1),('negative_x',-1)]:
    face=bounds('face_'+side);report['face_'+side]=face
    near(face[0][1:],[.25,-.53]);near(face[1][1:],[.83,.53])
    assert min(abs(face[0][0]),abs(face[1][0]))<.049
    assert max(abs(face[0][0]),abs(face[1][0]))>.064
# Source and studio isolation, not just export flags.
assert {o.name for o in bpy.data.objects if o not in list(col.objects)}=={'authoring_1m_reference'}
assert not any(o.type in {'LIGHT','CAMERA','ARMATURE'} or o.animation_data for o in bpy.data.objects)
assert not bpy.data.actions
assert not any(i.source!='VIEWER' for i in bpy.data.images)
assert all(not any(n.type=='TEX_IMAGE' for n in m.node_tree.nodes) for m in bpy.data.materials if m.use_nodes)
assert all(not o.modifiers and not o.constraints for o in col.objects)
source=R/'art/source/models/environment/city_shop_fittings_08/city_shop_fittings_08.blend'
glb=R/'art/models/environment/city_shop_fittings_08/city_shop_fittings_08.glb';reexport=E/'reexport_city_shop_fittings_08.glb'
assert glb.read_bytes()==reexport.read_bytes()
report.update(status='PASS',scope='Source and glTF validation only; analytical contact overlaps are not engine attachment/collision tests',plate_bounds=plate,shell_bounds=body,artwork_field_m=[.58,1.06],artwork_safe_content_m=[.50,.98],minimum_body_wall_gap_m=body[0][1],reserved_envelope_blender_m=[[-.2,-.02,-.68],[.2,.98,.68]],recommended_pivot_height_m=3.2,lowest_geometry_height_m=3.2+body[0][2],bounds_tolerance_m=.001,wall_placement_tolerance_m=.002,minimum_adjacent_fitting_gap_m=.1,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(glb.read_bytes()).hexdigest(),glb_bytes=glb.stat().st_size,saved_source_byte_identical_reexport=True,studio_exclusion='exactly one hidden authoring_1m_reference; no saved lights/cameras/graphics')
(E/'attachment_and_reexport_checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
