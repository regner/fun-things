# Common requirements for district concept briefs

9 October 2026. Owner scope: **concept images, iteration and asset briefs only**.
Regner selects concepts. Codex prepares images, inventories and briefs. Selection
does not commission modelling, editor work, implementation or world replacement.

## Map fit comes first

The [owner-exported polygons](../world-v1/stage-04-streets/district-editor/brackett-districts.json)
own each district's area. The [current road plan](../world-v1/stage-04-streets/README.md)
and [greybox handoff](../../assets/brackett_greybox.md) provide layout context.
Do not substitute the older broad island illustration, M1 rectangle or identity
board diagrams for these exact selected areas. Preserve independent boundaries,
including gaps/overlaps; do not snap or expand them.

Before generating each district, inspect its exact polygon, the streets through
and around it, footprint sizes, open-space availability and neighbouring districts.
Make a map extract at known scale. Use that extract as the geometry reference and
the accepted island image as style only. Read [map measurements](map-context.md).
An image that invents a new waterfront, annexes a neighbour or enlarges the district
must be revised, even if its mood is attractive.

Existing greybox placements are context rather than finished parcels. A concept
may propose replacing or removing a placeholder for a landmark or public space;
record the affected IDs and area, preserve streets/boundaries, and call the change
a proposal. Do not silently apply it to saved scenes. Asset counts are counts of
unique reusable designs; placed quantities follow an approved local arrangement.

Road-surface assets are excluded at the owner’s request; future tooling will handle
them automatically. Preserve current road geometry as concept context without
commissioning a hand-authored surface kit.

## Visual language and scale

Follow the accepted [Cyberpunk Long Island](../world-v1/stage-01-setting/15-long-island-cyberpunk.png)
and the [approved district identities](../world-v1/stage-03-district-identities/README.md).
Smooth stylised ordinary architecture, broad roof silhouettes, quiet dark surfaces,
selective vibrant accents, readable blue-hour fill. Names remain placeholders.
Vary footprints, roof rhythms, setbacks, density and empty space before adding detail.

Presentation concepts may show a district overview. The eventual gameplay reference
is vertical-down perspective, north-up, provisional 47 m height / 42° vertical FOV,
1280 × 800. A generated overhead image is not a calibrated capture or visibility test.
Preserve flat terrain, existing road widths and ground datums as reference constraints.
No interiors, rooftop gameplay or weather/time system is implied. The owner has
requested one elevated pedestrian connection between Signal Row and Old Quay; its
concept is allowed, while traversal and implementation remain unvalidated.

## What every family brief records

Purpose, named outputs/variants, district use, appearance, route/visibility constraints,
review criterion, reference links and decision status. Each enumerated member is
covered by that brief; separate buildings need not get separate duplicate documents
when they form a tightly related kit. A mere recolour is not a new building family.
Shared hardware owns its shape; district graphics briefs own copy/artwork.

Exact X/Y/Z bounds, overhangs, clearances, origin, connectors and material/texture
specifications remain pending unless explicitly recorded as a proposal or inherited
measurement. Codex refines them with the layout/asset owner after visual selection,
before any separately commissioned production. Never measure them from imagegen.
Static intact appearance is the default for new environment concepts; destruction,
working doors, rigs, animation and physics are not silently added.

No new sources, exports, imports, prefabs, sockets, colliders or runtime identities
are created in this phase. Future source and integration owners are unassigned.
If production is later commissioned, expand the record with the
[handoff template](../../templates/asset-handoff.md) and follow the
[asset workflow](../../assets.md), including Blender provenance, linked exports and
actual camera/clearance checks. None of those checks is claimed by a concept brief.

## Review loop

1. Review one district's exact map extract and proposed arrangement.
2. Iterate its concept image against that geometry and accepted style.
3. Reconcile visible objects with the shared and district-specific briefs: reuse,
   add a brief for a newly desired object, or explicitly exclude incidental details.
4. Record Regner's decision and outstanding questions; then move to the next district.

The first district round now covers all nine selected map areas. The central
registry records demand from these concepts; closer asset drawings, dimensions
and supporting decisions remain open. Road surfaces remain outside this pass.
