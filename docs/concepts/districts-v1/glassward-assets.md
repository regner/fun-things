# Glassward asset breakdown

The owner likes the [first Glassward concept](04-glassward-v01.png) and requests
the next district. This pass records its asset needs before moving on. The
[central registry](asset-register.md#04-glassward-assets) owns district usage and
status; this page explains the set. Individual designs and dimensions still need
refinement, especially tower height and visibility from the fixed game camera.

## Buildings and architectural parts

| Required design | Brief and coverage |
| --- | --- |
| Rectangular-crown tower | [Tower family](../../assets/d04_towers.md), `.01` |
| Chamfered-crown tower | Same brief, `.02` |
| Rounded-crown tower | Same brief, `.03` |
| Medium-height tower | Same brief, `.04` |
| Low office building | [Podium/office family](../../assets/d04_podiums.md), `.01` |
| Setback podium | Same brief, `.02`; separate modest bases with walking gaps |

Tower records describe reusable building designs, not a unique model for every
placement. Refine common facade/floor sections, glazing, entrance treatment and
roof/crown interfaces within the tower brief. Different heights, footprints and
crown shapes should reuse that vocabulary. Exact module splits remain to establish;
the raster does not demonstrate workable joins. The separate service wing remains
an optional candidate, not an extra required building inferred from every low roof.

Normal facade trim, lobby doors/windows, crowns and luminous architectural panels
belong to these building designs. Broad roof vents and plant enclosures use the
[shared roof-detail family](../../assets/city_roof_details.md), `.01–.02`.

## Artwork and frontage

| Required design | Brief and use |
| --- | --- |
| Broad paving bands and entry-axis motif | [Forecourt graphics](../../assets/d04_forecourt_graphics.md), `.01–.02`; applied to shared quiet paving |
| Large facade panel artwork | [Corporate graphics](../../assets/d04_corporate_graphics.md), `.01`; controlled cyan/magenta identity accents |
| Low directory face | Same brief, `.02`; small forecourt orientation panel |
| Entry wordmark set | Same brief, `.03`; fictional copy to refine, not accepted raster lettering |
| Wall panel and freestanding low panel | [Sign supports](../../assets/city_sign_supports.md), `.01–.02`; reuse hardware under artwork |

The optional inset emblem remains a candidate. The directory must not grow into
a monument. Forecourts are open layouts using these surfaces and props, not unique
raised structures or a requirement for fountains/sculptures.

## Shared city assets

| Required set | Brief and members |
| --- | --- |
| Coastal boardwalk kit | [Boardwalk](../../assets/city_boardwalk.md), `.01–.05`; same deck, bend, fascia, support and access pieces |
| Seaward rail | [Quay furniture](../../assets/city_quay_furniture.md), `.02` |
| Low seawall and rock shore | [Shore edges](../../assets/city_shore_edges.md), `.01`, `.03` |
| Street, pedestrian and wall lights | [City lights](../../assets/city_lights.md), `.01`, `.02`, `.04` |
| Straight bench | [Seating](../../assets/city_seating.md), `.01` |
| Rectangular/round planters, low shrubs and broad-canopy trees | [Planting](../../assets/city_planting.md), `.01–.04`; reduce density during refinement |
| Quiet paving, grass and planted soil | [Ground finishes](../../assets/city_ground_finishes.md), `.01`, `.04–.05` |

Public bins, short bollards, utility cabinets and service doors remain supporting
uses to confirm in the registry. The image does not resolve them reliably. Existing
cars and people remain shared vehicle/actor assets. Road surfaces remain excluded.
No tower interiors, elevators, skybridges, roof gameplay, cutaway/occlusion system,
modelling or implementation is commissioned by this list.

Shared shoreline corner/end connections also use `city_shore_edges.04`.
Open-sea appearance uses the shared `city_water_look.01` visual study.
The central registry records these uses without new district-specific geometry.
