# city_shore_edges — Island and harbour edge kit

9 October 2026 · **Draft concept brief; not selected or commissioned for production.**
Scope: Shared / coastal districts. Brief/concept author: Codex; selection: Regner.

## Purpose and deliverables

Give the island and open basin a consistent edge.

Coordinate with the proposed [island boardwalk](city_boardwalk.md): this brief
owns the underlying seawall/rock edge, while that brief owns its pedestrian deck.

Each member below is covered by this brief; these are proposed unique outputs, not
placed quantities or committed runtime IDs. Repeated placements reuse a member.

- `city_shore_edges.01` — low seawall.
- `city_shore_edges.02` — quay edge.
- `city_shore_edges.03` — simple rock shore.
- `city_shore_edges.04` — edge corner.

## Visual direction and constraints

Broad slate masses, sparse joints, clean water boundary.

Follow the saved coast and harbour polygons; no terrain raising, shoreline redesign or implied water-entry mechanic.

Review criterion: **Old Quay and East Docks can differ through placement without incompatible seams.**

References: [approved district identities](../concepts/world-v1/stage-03-district-identities/README.md), [District review queue](../concepts/districts-v1/README.md), and the
[shared concept contract](../concepts/districts-v1/brief-contract.md).
District names and copy are provisional. This brief inherits the contract's camera,
flat-terrain, source, state and deferred-dimension requirements.

## Edge interfaces

Member .01 owns the low seawall body, .02 the heavier working/harbour quay face,
.03 the rock-shore treatment and .04 their compatible corner/end connector set.
Straight edge designs reuse .04 rather than creating separate standalone corner
families. Visible caps/normal trim stay with their edge pieces. Quay furniture owns
rails, mooring bollards and ladders; marina docks own floating deck and connectors.
Boardwalk decks and supports do not replace or duplicate the underlying shore.

## Selection and later handoff

Concept selection: pending Regner's district/asset review. Exact X/Y/Z bounds,
attachment/connector sizes, origins and overhang clearances: pending Codex brief
refinement with the layout owner after visual selection, before any later production
commission. Do not infer those values from a generated image.

Source/export/prefab/placement: none created by this brief. Rig, clips and sockets:
not requested for this concept family. Material slots, texture specifications,
collision, measured performance and engine acceptance: not specified or tested.
Future source/integration owners remain unassigned; current scope is concepts and
briefs only, including after concept approval. Use the
[handoff template](../templates/asset-handoff.md) if production is separately commissioned.

## Revision record

- v01, 9 October 2026: first draft from approved city/district identity and current
  owner request. Asset-family breakdown is a Codex proposal, not owner acceptance.
