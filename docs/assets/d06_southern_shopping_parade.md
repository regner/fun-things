# d06_southern_shopping_parade — Southern multi-store building

9 October 2026 · **Owner-requested concept revision; visual design in review.**
Scope: Signal Row. Brief/concept author: Codex; selection: Regner.

## Purpose and deliverables

Replace the three detached shops in Signal Row's southern strip with one long
building containing multiple independent stores. It must read as one continuous
structure with a shared roof, rather than three shops touching at their corners.

- `d06_southern_shopping_parade.01` — continuous long building shell and roof.
- `d06_southern_shopping_parade.02` — repeatable storefront bay interface.
- `d06_southern_shopping_parade.03` — north-end facade facing the bridge forecourt.

Use [shared fittings](city_shop_fittings.md) for doors, fascias, shutters and
canopies, and [Signal Row graphics](d06_commercial_graphics.md) for individual
store identity. Do not create a separate building asset for each tenant.

## Map fit

Use the [selected district 06](../concepts/districts-v1/map-context.md#district-06).
The affected greybox IDs are `brackett/district_06/building_0001`, `building_0008`
and `building_0005`. They remain unchanged in the saved scene; consolidation is a
concept proposal and any eventual saved-identity migration belongs to later work.

The prompt explores approximately 18 m east-west by 60 m north-south, with one or
two storeys and six illustrative shop bays. These proportions and tenant count are
Codex proposals, not owner-selected dimensions. Fit the irregular southern strip,
leave ground-level walking space along both long sides, and reserve a forecourt
at the north end for the pedestrian bridge landing. Do not widen the selected area
or absorb the surrounding roads to fit the shell.

## Visual direction and constraints

Quiet continuous blue/slate roof, muted plum structure and differing broad cyan,
magenta and warm storefront panels. Vary fascia widths and entrances without
breaking the building into separate pavilions. Roof services remain sparse.

The [footbridge](d06_harbour_footbridge.md) lands in the north forecourt, not on the
roof. Shop interiors, opening doors and rooftop traversal are not requested.

Review criterion: **One long building is immediately apparent, while several stores
remain distinguishable and its north end has usable space for a bridge approach.**

## Bay interface ownership

Member .02 is an interface reference: wall opening, facade rhythm and mounting
positions for city_shop_fittings. It does not commission duplicate door, window,
fascia or canopy meshes. Member .03 owns the distinctive north-end facade treatment
within the single parade assembly, not another building at the bridge landing.

## Selection and later handoff

The owner selected the continuous-building requirement; the image, final footprint,
bay count, height, origins, overhangs, attachments and clearance envelopes remain
pending concept review. Apply the [common brief contract](../concepts/districts-v1/brief-contract.md)
and [Signal Row review](../concepts/districts-v1/signal-row.md).

Source/export/prefab/placement: none created. Static intact appearance only; rig,
clips and sockets not requested. Material slots, collision and performance remain
unmeasured. Modelling and implementation remain outside this commission. Future
owners are unassigned; use the [handoff template](../templates/asset-handoff.md)
only if production is separately commissioned.

## Revision record

- v01: follows Regner's request to combine the three southern shops. The continuous
  shell is a new district-specific family; ordinary northern shops keep their existing briefs.
