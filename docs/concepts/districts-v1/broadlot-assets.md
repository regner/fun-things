# Broadlot asset breakdown

The owner requests an asset pass for [Broadlot revision 01](07-broadlot-v01.png)
before continuing. The [central registry](asset-register.md#07-broadlot-assets)
records needed district uses and remaining candidates. This page explains the
design set; neither image instance counts nor exact asset dimensions are approved.

## Buildings and frontage parts

| Required design | Brief and coverage |
| --- | --- |
| Main large retail box | [Retail buildings](../../assets/d07_retail_buildings.md), `.01`; broad low stepped roof, shell, normal trim and rear service frontage |
| Secondary low retail box | Same brief, `.02`; smaller broad-roofed store with shared architectural treatment |
| Entrance annex | Same brief, `.03`; attached entrance component, not another standalone store |
| Narrow, wide and compact-square small-shop shells | [Shared shop shells](../../assets/city_small_shop_shells.md), `.01`, `.02`, `.04`; repeat on eastern/coastal pads without a unique model per placement |
| Short canopy and fascia frame | [Shop fittings](../../assets/city_shop_fittings.md), `.01–.02`; chiefly smaller shop frontages; the large-store annex owns its larger structure |
| Entrance surround, display window and glazed door | Same brief, `.03`, `.05–.06`; compatible repeated frontage components |
| Broad roof vent and compact plant enclosure | [Roof details](../../assets/city_roof_details.md), `.01–.02`; sparse roof equipment reused across buildings |

This is five reusable building-shell designs plus an entrance component, not a
bespoke store for each of the twenty greybox sites. Refine shared wall, roof and
frontage sections within the retail brief; vary span, depth and colour without
making each placement unique. Entrances and glazing must suit the large store's
scale rather than indiscriminately stretching a small-shop window.

## Retail props and artwork

| Required design | Brief and use |
| --- | --- |
| Low circular sign-island base and sign support | [Sign island](../../assets/d07_sign_island.md), `.01–.02`; keep more restrained than the tall glowing pylon in v01 |
| Short trolley shelter | [Trolley shelter](../../assets/d07_trolley_shelter.md), `.01`; repeated sparsely near entrances and selected parking rows |
| Trolley and nested group | Same brief, `.02–.03`; one trolley design reused in a static nested arrangement, not a new basket model per trolley |
| Retail fascia, sign-island face and parking-zone artwork | [Retail graphics](../../assets/d07_retail_graphics.md), `.01–.03`; fictional identity/copy still to refine |
| Wall sign panel | [Sign supports](../../assets/city_sign_supports.md), `.01`; hardware for selected frontage graphics |
| Wheel stop and parking-sign assembly | [Parking furniture](../../assets/city_parking_furniture.md), `.01–.02`; sparse placements; `.02` reuses city_sign_supports.02 and retail graphics .03 |

Trolleys are static dressing; no pushing, collection, shopping or loose-physics
system is implied. The sign island is a retail orientation prop, not a requirement
for another traffic roundabout. Artwork does not endorse generated lettering.

## Shared coastal and public-space assets

| Required set | Brief and members |
| --- | --- |
| Complete boardwalk kit | [Boardwalk](../../assets/city_boardwalk.md), `.01–.05`; deck, bends, fascia, supports and landward transitions |
| Seaward rail | [Quay furniture](../../assets/city_quay_furniture.md), `.02` |
| Low seawall and rock shore | [Shore edges](../../assets/city_shore_edges.md), `.01`, `.03` |
| Street, pedestrian, yard/parking and wall lights | [City lights](../../assets/city_lights.md), `.01–.04`; vary spacing, not one unique lamp per site |
| Rectangular/round planter, low shrubs and trees | [Planting](../../assets/city_planting.md), `.01–.04`; reduce the image's dense repeated planting |
| Quiet paving, grass and soil appearances | [Ground finishes](../../assets/city_ground_finishes.md), `.01`, `.04–.05`; pedestrian approaches and planted areas |

The boardwalk passes behind the compact coastal pads and continues beyond the
district. No new seawall or boardwalk kit is duplicated for Broadlot. Its final
connections to Old Quay and East Docks still need fit review.

## Supporting items and exclusions

| Item to confirm | Existing brief |
| --- | --- |
| Public bin and rear service dumpster | [Waste](../../assets/city_waste.md), `.01`, `.03` |
| Straight bench | [Seating](../../assets/city_seating.md), `.01`; selected pedestrian/boardwalk spots only |
| Short bollard | [Barriers](../../assets/city_barriers.md), `.01`; store approach protection if selected |
| Utility cabinet and closed service door | [Service furniture](../../assets/city_service_furniture.md), `.01`, `.03`; coordinate with the store shells |

Parking asphalt appearance and bay/road marking candidates remain subject to the
future surface/tooling boundary; this pass commissions no road or parking-surface
geometry. The visible parking arrangement is layout context, not a placed-capacity
promise. Cars and people reuse existing shared assets. No buses, bus shelters,
loading simulation or additional trucks are commissioned from incidental context.
All required designs have briefs; no modelling, scenes or implementation changed.

Shared shoreline corner/end connections also use `city_shore_edges.04`.
Open-sea appearance uses the shared `city_water_look.01` visual study.
The central registry records these uses without new district-specific geometry.
