# city_boardwalk — Shared island boardwalk

9 October 2026 · **Shared kit needed in The Crescents, Northpoint, Terrace Ward, Glassward, Broadlot and Ironreach; other coastal uses to review.**
Scope: Shared / coastal districts. Brief/concept author: Codex; selection: Regner.

## Purpose and deliverables

Give the island a consistent pedestrian route and visual treatment along its outer
coast. First explored in [The Crescents v02](../concepts/districts-v1/the-crescents.md).
The owner suggested a consistent boardwalk around the island and later excluded
East Docks, ending the route at its two district boundaries. Timber and the
following kit breakdown are concept proposals, not production approval.

- `city_boardwalk.01` — straight deck section.
- `city_boardwalk.02` — bend/corner deck section, with angle variants to fit the coast.
- `city_boardwalk.03` — exposed edge fascia and low edge trim.
- `city_boardwalk.04` — simple coastal support assembly for constrained shore sections.
- `city_boardwalk.05` — landward access / promenade transition section.

These are reusable members, not five complete routes or a placed-quantity estimate.
The [central tracker](../concepts/districts-v1/asset-register.md) owns district demand.
The Crescents, Northpoint, Terrace Ward, Glassward, Broadlot and Ironreach are needed uses. Old Quay remains a candidate user; East Docks is excluded;
exact route coverage remains to review.
Signal Row is inland and reaches the waterfront through its shared pedestrian bridge.

## Visual direction and constraints

Explore muted weathered warm-brown timber decking, broad quiet seams and dark
slate fascia/supports. Aim for one recognisable treatment across district boundaries.
The image prompt explores roughly 3–4 m walking width for visual scale only;
final width, joints, origins and support spacing require later fit review.

Reuse the [shared low waterfront rail](city_quay_furniture.md), `.02`, with mounting
appropriate to decking. Reuse [city lights](city_lights.md), especially `.02`, and
[seating](city_seating.md) where selected. Do not create a second set of lamps,
benches, railings or generic waterfront props in this brief. Keep furniture sparse
and outside the walking line; maintain openings at landward footpath connections.

Follow the existing coast and retain seawall/rock beneath or beside the boardwalk.
The [shore-edge kit](city_shore_edges.md) owns seawalls and rocks; this kit owns
the walking deck and its supporting/transition pieces. Where land is narrow,
edge-supported sections are an option rather than land reclamation. No changes
to island polygons or terrain are implied.

The boardwalk is an outer-coast route. It does not automatically become a timber
ring around Old Quay's inner basin or duplicate the [marina docks](city_marina_docks.md).
Review continuity at the harbour-mouth road bridge and industrial access.
The owner explicitly ends the boardwalk on either side of East Docks: no coastal
deck or landward bypass passes through district 09. End the Ironreach (08) section
at the northern boundary and Broadlot (07) at the southwestern boundary. Use .03
fascia/trim for clean terminal caps, .05 for landward connections and the shared
quay rail .02 for safe end returns; do not create a new duplicate terminal kit.
Refine these two connections in closer concepts outside the freight working area. Use compatible promenade/bridge transitions
where needed; do not add a bridge blocking navigable water to force a closed ring.
A closed whole-island boardwalk loop is no longer intended; remaining route
connections still need fit review.

Road surfaces remain excluded. The cul-de-sac is a district layout proposal, not
a boardwalk component or a bespoke road-surface asset.

Review criterion: **A recognisable, unobstructed coastal walk continues between
districts without changing the shoreline or duplicating existing shared props.**

## Selection and later handoff

Exact section dimensions, junctions, rail mounting, support positions and shore
access need refinement after visual selection. No sources, exports, prefabs,
collision, navigation, performance measurements or saved-world placements exist
for this proposal. No modelling or implementation is commissioned.

Follow the [shared concept contract](../concepts/districts-v1/brief-contract.md).
Future production owners remain unassigned; use the
[handoff template](../templates/asset-handoff.md) only if production is separately
commissioned. Approval of this concept does not itself commission production.

## Revision record

- v01, 9 October 2026: owner suggests a consistent island boardwalk alongside
  The Crescents cul-de-sac revision; shared kit and timber appearance proposed.

- v02, 9 October 2026: owner ends the boardwalk on either side of East Docks; remove district 09 demand and use existing members for the neighbouring terminals.
