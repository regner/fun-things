# city_barriers — Bollards, barriers and chain-link fences

9 October 2026 · **Draft concept brief; not selected or commissioned for production.**
Scope: Shared / all nine. Brief/concept author: Codex; selection: Regner.

## Purpose and deliverables

Visually separate edges while preserving intentional routes.

Each member below is covered by this brief; these are proposed unique outputs, not
placed quantities or committed runtime IDs. Repeated placements reuse a member.

- `city_barriers.01` — short bollard.
- `city_barriers.02` — landward-rail assembly reference, reusing city_quay_furniture.02.
- `city_barriers.03` — low service barrier.
- `city_barriers.04` — rail-terminal assembly reference, reusing city_quay_furniture.02.
- `city_barriers.05` — repeatable straight chain-link mesh panel.
- `city_barriers.06` — chain-link line, corner and terminal post/bracing set.
- `city_barriers.07` — paired chain-link vehicle gate leaves with hinge/latch fittings.

## Visual direction and constraints

Dark metal and quiet pale concrete, sparse amber safety bands.

Visuals do not decide blocking. Collision extent and removable/destructible states are unassigned, not implied.

Review criterion: **Routes read clearly and low edges do not conceal feet or targets.**

References: [approved district identities](../concepts/world-v1/stage-03-district-identities/README.md), [District review queue](../concepts/districts-v1/README.md), and the
[shared concept contract](../concepts/districts-v1/brief-contract.md).
District names and copy are provisional. This brief inherits the contract's camera,
flat-terrain, source, state and deferred-dimension requirements.

## Ironreach chain-link kit

The owner requests fencing around some Ironreach properties. Members .05–.07 are
needed for district 08. Reuse one mesh/post language with configurable run lengths
and corners; .04 is not a substitute for tall fence terminal/bracing posts. Other
district reuse remains unassigned. Exact panel length, height and gateway width
await a closer yard concept and measured fit before later production.

Use see-through diamond mesh, thin galvanised framing and restrained rust at
joints and post bases. The straight panel stays serviceable; a scuffed/rusted
finish is a shared material variation rather than a second fence model. Gates
reuse the mesh and framing, shown open in the district concept. No barbed wire.
Fencing should enclose selected service edges, not every property or the district.
Preserve two main-yard vehicle openings, a pedestrian gap/bypass and the public
boardwalk. Set posts back from entrances and keep gate leaves clear of routes.

Review a straight run, corner, terminal and open paired gate together. Check mesh
readability at the intended camera distance and that poles/mesh do not hide actors.
Gate animation, interaction, locking and collision are not commissioned by this
visual brief; exact layout and visibility remain to validate.

## Rail and door ownership

The landward low rail .02 is an assembly reference to city_quay_furniture.02,
using that kit's rail sections with landward mounting. The end-post record .04
is a terminal assembly reference using the same kit's end/return parts; it is not
another independent post model. The low service barrier .03 is a short solid
service-edge separator, distinct from see-through rails and chain-link fencing.
Short bollard .01 is pedestrian separation; mooring bollards remain separately
owned by city_quay_furniture.01. Fence posts .06 remain a distinct braced system.

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

- v02, 9 October 2026: owner requests selected Ironreach chain-link enclosures; add three shared kit records and a weathered finish direction.
