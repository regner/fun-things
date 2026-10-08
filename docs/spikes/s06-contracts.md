# S06 bounded topology and controller contract

This new fixture supplement refines the unchanged canonical
[owners](../architecture.md), [scene contract](../scene-structure.md) and
[CityData API](../api-contracts.md#city-presentation-and-settings). It is provisional
technical evidence, not production traffic or a second normative architecture.
The [predeclaration/results](s06.md) own acceptance and limits.

## One authored representation

Saved `west.tscn` and `east.tscn` own linked model placement, deliberate static
island collision, explicit `S06Sector.world_id`, `S06Anchor.world_id` and
`S06Link` connectivity/Curve3D controls. The saved intersection instances both
sectors at identity transforms. X=0 splits visible geometry; there is no duplicate
floor collider, and planar immutable bodies need no gravity/floor integration.
New island boxes are solid World collision. No procedural city or runtime hierarchy.

Explicit IDs use `s06/sector/*`, `s06/foot/*`, `s06/lane/*`, `s06/road/*`, separately
from engine resource/node IDs and dynamic actor/car identity. Reparenting does not
change IDs; it intentionally changes the placement signature. West owns the shared
road-centre anchor, foot crossing link and eastbound→northbound turn; East owns
westbound→southbound turn and east road/foot continuation. Links reference endpoint
IDs across sectors. Both legal left turns follow right-hand lanes and cross X=0.
This is ownership of connectivity, not duplicate junction geometry.

`S06City.route(kind, from_id, to_id)` returns canonical `code`, topology revision,
link IDs, world points and visited count. FOOT uses undirected links; TRAFFIC uses
directed links and refuses reversing a legal lane. `map_data()` returns district,
revision, bake fingerprint, imported-road world XZ bounds and roads from those same saved ROAD links/widths.
Road widths describe this neutral source's measured9 m carriageway. Road curves
and traffic curves serve different semantics; neither writes geometry at runtime.
The minimap Control's saved origin(80,80)/3 px per metre projects world XZ, with
only the supplied controlled-body marker. No independently authored map street list.

## Alternatives and bounded decision

| Alternative | Bounded assessment / decision |
| --- | --- |
| Explicit sidewalk graph | Chosen for the single flat corridor/crossing: crossing identity, legality and reservation boundary remain inspectable. Undirected walking is intentional; one BFS suffices. Corners/avoidance/fleeing remain future integration. |
| Navmesh / NavigationAgent | Not implemented as a second planner. Useful for area wandering/obstacle detours, but polygon connectivity alone would not encode crossing permission or directed car lanes; still needs semantic anchors and stale-bake ownership. This experiment does not measure navmesh performance or disprove it. Revisit when an accepted pedestrian area fixture requires free-space detours. |
| Directed lane graph with polyline controls | Graph is required for legality and junction ownership. Hand-authored chord samples would duplicate curve editing or introduce discontinuous heading; no second complete planner implemented. |
| Directed graph with scene-authored curves | Chosen. Curve controls preserve tangent intent; graph owns endpoint connectivity. Engine-sampled points are derived read-only route values. The actual shared S04 steering owner remains responsible for movement, rather than PathFollow overwriting body poses. |

Bounds:64 anchors,128 links,16 controls/link,128 m control-polygon length/link,
fixed0.25 m bake interval,64 visited nodes,64 returned links/4096 route samples.
BFS scans at most64×128 links. Each curve allocation is bounded before engine baking;
all vectors and positive ROAD widths must be finite. Derived minimap total samples <=4096. Controller nearest
search <=32 samples/tick, lookahead <=4096 samples/tick worst case. These are finite
spike limits, not production performance budgets or population capacity results.

## Bake, update and admission

`S06City` is the sole content-query/bake rule owner. Signature SHA256 covers district,
revision/tool version, authored node paths/local transforms, sector/anchor/link IDs,
connectivity/kind/width, curve controls/bake interval, deliberate collision sizes/
flags/layers/masks and exact linked GLB/import bytes. It excludes its own derived
resource, avoiding self-reference. Extra ROAD-data equality validation detects a
manually corrupted/missing/duplicate derived road, not just changed placement.

The editor-only `S06EditorProbe.bake_city` creates/saves `derived.tres`, then assigns
the external resource to City. Save the scene batch, close/reopen base and inherited
variant and inspect signature/IDs before play. Any placement/source/collision/
connectivity/envelope change requires explicit affected bake and route/map checks.
Increase topology revision for an intentional topology change; content handshake
uses district/revision/signature, separate from display/engine version. Runtime
never rebakes or moves authored anchors. Missing/stale/invalid content returns
`CONTENT_INVALID` before route/controller/map admission. No production join codec
is implemented; canonical admission must perform this validation before world-ready.

Isolated proof deliberately moves West by1 m, saves/reloads the changed scene and
rejects the original signature through route, map and controller APIs. It also
changes connectivity, removes an endpoint ID, duplicates an anchor ID, changes revision and corrupts a
derived road. A coherent1 m City translation remains connected but requires an
explicit new bake; its route/map follow actual translated scene values. The copy
restores original data before actual-body trajectories. These saved counterexample
files are retained with the raw check; no shared editor scene was mutated by them.

## Host commands and provisional recovery for M1-C3

`S06Controller.bind_route(city, kind, from, to, host)` rejects passive ownership or
invalid current content. `intent(public_body_state, kind)` emits facing-relative
foot intent or shared S04 drive commands. `clear()` cancels producer state.
`S06Fixture` configures bodies passive before child entry, admits one host route,
calls unchanged body `step` once/physics tick, neutralizes before completion and
clears bindings on teardown. S02 lacks a role API, so the new enclosing fixture
controls its collision admission; no original script changes. Offline host-only
scope: no RPC, client simulation/prediction, production entity binding or transport.

Actual fixture recovery is a hard1200-tick foot/1800-tick car deadline followed by
neutralization, passive collision and a timed-out report. It does not reroute around
obstacles. The following is a **specified, unimplemented** M1-C3 starting policy,
to validate with accepted M1 bodies/world/lifecycle owners, not product ratification:

- Blockage: host clearance query includes World/Actor/Vehicle/Wreck. Stop intent
  before the blocked link; retry at most twice/second for2 s, then at most two route
  replans per10 s. Never invent an off-road bypass or teleport through collision.
- Junction/crossing: host reserves the provisional XZ[-8.5,8.5]×[-8.5,8.5] junction
  conflict zone before entry; eight waiting requests
  maximum, order by accepted tick then EntityRef. One holder
  for this starting policy,8 s car/4 s foot lease. Expiry stops intent but cannot
  grant another actor while actual query shows the zone occupied. Release on actual
  cleared exit or coherent lifecycle cancellation; controller ownership/life/control
  revisions fence obsolete reservations. Real contested priority remains untested.
- Stuck: progress <0.25 m over4 s triggers stop and bounded replanning; two failures
  park the car or leave pedestrian waiting, report the state and schedule bounded
  Population cleanup/replenishment. No automatic AI restart after player transfer.
- Wreck: invalidate affected link availability through current authoritative
  collision/life revision, wait/replan with the same bounds. Wreck cleanup belongs
  to Explosions/lifecycle, never to the route planner or cosmetic cap. S05's current
  five-second stationary box is only a provisional obstruction assumption; this
  experiment contains no actual destroyed-car/contact or effect demonstration.

World bit1, Actor bit2, Vehicle bit4 follow immutable S02/S04 fixtures. Wreck bit8
and Interaction bit16 remain canonical reserved roles; no project layer setting
was changed or final wreck mask selected. Spawn/exit, admitted players, contested
crossings, offscreen population/reset/join and full recovery remain M1-C3/B1/B3/D3.
S07 needs actual content/effects/hardware/views/residency before capacity evidence.
