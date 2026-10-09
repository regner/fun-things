# city_shop_fittings — Shared shop frontage fittings

9 October 2026 · **Draft concept brief; not selected or commissioned for production.**
Scope: Shared / Crescents, Terrace Ward, Old Quay, Signal Row, Broadlot. Brief/concept author: Codex; selection: Regner.

## Purpose and deliverables

Reuse practical shop components across different shells.

Each member below is covered by this brief; these are proposed unique outputs, not
placed quantities or committed runtime IDs. Repeated placements reuse a member.

- `city_shop_fittings.01` — short canopy.
- `city_shop_fittings.02` — flat fascia frame.
- `city_shop_fittings.03` — recessed entrance surround.
- `city_shop_fittings.04` — closed shutter.
- `city_shop_fittings.05` — display-window glazing and frame bay.
- `city_shop_fittings.06` — glazed entrance door leaf, with single/double-width variants.
- `city_shop_fittings.07` — broad upper-floor window group.
- `city_shop_fittings.08` — projecting blade-sign body and mounting bracket.

The [Signal Row v03 breakdown](../concepts/districts-v1/signal-row-assets.md)
identifies these additional reusable facade pieces. Combine `.03` and `.06` as
one entrance assembly; do not author competing entrance frames in building kits.
Window bays use simple opaque/tinted interior suggestion, not detailed shop interiors.
The blade-sign projection and bracket need an elevation concept before dimensions
are selected. Graphic faces belong to the district graphics brief. Static closed
doors/shutters only; no opening mechanics or animations are added by this revision.

## Visual direction and constraints

Smooth forms, limited projection; district-specific trim/graphic variants.

Frontage attachments only; no interiors or opening animation. Exact facade interfaces and clearances pending shell selection.

Review criterion: **Different shells remain recognisable under consistent fittings.**

References: [approved district identities](../concepts/world-v1/stage-03-district-identities/README.md), [District review queue](../concepts/districts-v1/README.md), and the
[shared concept contract](../concepts/districts-v1/brief-contract.md).
District names and copy are provisional. This brief inherits the contract's camera,
flat-terrain, source, state and deferred-dimension requirements.

## Boundaries with building kits

These members own reusable commercial frontage attachments. Building shells own
wall openings and ordinary structural trim. The southern parade's bay interface
is a placement/connection specification using these fittings, not another set of
shop doors and windows. Shop shutters .04 are frontage closures; workshop/depot
roller doors are integral larger industrial bays in their building briefs.
Closed rear service doors use city_service_furniture.03 where a shell does not
already include the same appearance. Do not author duplicate integral and loose
door geometry for one opening. Fascia .02 differs from a shallow civic/poster wall
panel city_sign_supports.01; select one body for each graphic face.

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
