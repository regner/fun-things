from pathlib import Path
import re,subprocess,json
root=Path('/home/regner/.paseo/worktrees/0u71f39f/s06-provisional-turn-seam');scratch=Path('/tmp/s06-format')
for p in list((root/'tests/fixtures/s06').glob('*.gd'))+list((root/'tools/s06').glob('*.gd')):
 s=p.read_text()
 if p.name=='city.gd':
  a=s.index('\tvar queue: Array[StringName] = [from_id]');b=s.index('\tvar steps: Array[Dictionary] = []',a);c=s.index('\n\n\n## Supplies shared',b)
  search=s[a:b];assemble=s[b:c]
  s=s[:a]+'\tvar search: Dictionary = _search(records.links, kind, from_id, to_id)\n\tif search.code != "OK":\n\t\treturn search\n\n\treturn _assemble(search.previous, from_id, to_id, search.visits)\n\n\n## Visits each reachable anchor once with a bounded directed link scan.\nfunc _search(links: Array[S06Link], kind: String, from_id: StringName,\n\t\tto_id: StringName) -> Dictionary:\n'+search.replace('records.links','links')+'\treturn { "code": "OK", "previous": previous, "visits": visits }\n\n\n## Reconstructs the selected authored links within the route sample bound.\nfunc _assemble(previous: Dictionary, from_id: StringName, to_id: StringName,\n\t\tvisits: int) -> Dictionary:\n'+assemble+s[c:]
 if p.name=='controller.gd':
  a=s.index('\tvar speed: float = state.velocity.length()');s=s[:a]+'\treturn _car_intent(state, direction, error)\n\n\n## Converts lookahead error to bounded steering/throttle through the shared handling scale.\nfunc _car_intent(state: Dictionary, direction: Vector3, error: float) -> Dictionary:\n'+s[a:]
 if p.name=='fixture.gd':
  s=s.replace('var controller:', '@onready var _minimap: S06Minimap = $Ui/Minimap\n\nvar controller:')
  s=s.replace('($UI/Minimap as S06Minimap)', '_minimap')
 if p.name in ['fixture.gd','minimap.gd']:
  a=s.index('##',s.index('\n\n\n'));header=s[:a]
  blocks=re.split(r'\n\n\n(?=##)',s[a:]);virtual=[x for x in blocks if re.search(r'^func _(enter_tree|ready|physics_process|exit_tree|draw)\(',x,re.M)]
  other=[x for x in blocks if x not in virtual];s=header+'\n\n\n'.join(virtual+other).rstrip()+'\n'
 if p.name=='proof.gd':
  # Long finite diagnostic coroutine has multiple independent observations; split route loop and rebake.
  a=s.index('\tfor case_name: String in CASES:');b=s.index('\n\tvar map_json:',a)
  route=s[a:b];s=s[:a]+'\tawait _test_routes(fixture)\n'+s[b:]
  a=s.index('\n\t# Coherent authored translation');b=s.index('\n\n\n## Records',a)
  rebake=s[a:b];s=s[:a]+'\t_rebake_counterexample(city, original)\n\n\n## Proves explicit bake refresh follows a coherent authored translation.\nfunc _rebake_counterexample(city: S06City, original: S06Bake) -> void:\n'+rebake+s[b:]
  s+='\n\n## Runs exactly three finite physics routes; each owner has a hard tick deadline.\nfunc _test_routes(fixture: S06Fixture) -> void:\n'+route.replace('await fixture.route_finished','await fixture.route_finished  # gdstyle:ignore=quality/await-in-loop')+'\n'
  # Initial diagnostic combines scene/install/content/geometry/result receipt within a finite fixture.
  s=s.replace('func _run() -> void:', 'func _run() -> void:  # gdstyle:ignore=quality/max-local-variables')
 if p.name=='editor_probe.gd':
  s=s.replace('\tvar edited: Node = EditorInterface.get_edited_scene_root()\n\tvar parent:', '\tassert(spec.anchors.size() <= S06City.MAX_ANCHORS)\n\tassert(spec.links.size() <= S06City.MAX_LINKS)\n\tvar edited: Node = EditorInterface.get_edited_scene_root()\n\tvar parent:',1)
  for line in ['var anchor: S06Anchor = S06Anchor.new()','var link: S06Link = S06Link.new()','link.curve = Curve3D.new()']:
   s=s.replace(line,line+'  # gdstyle:ignore=quality/allocation-in-loop')
  s=s.replace('## Adds scene-authored stable anchors', '## Editor-only finite allocations author stable anchors')
 (scratch/p.name).write_text(s)
subprocess.run(['/home/regner/.local/share/mise/installs/github-atelico-gdstyle/0.3.0/gdstyle','fmt',str(scratch)],check=True)
# Formatter has no preserving wrapper: restore purpose-block/function separation, keeping member order.
for p in scratch.glob('*.gd'):
 s=p.read_text();s=re.sub(r'\n{2,}(?=##)', '\n\n\n',s);p.write_text(s)
print(json.dumps({p.name:p.read_text() for p in scratch.glob('*.gd')}))
