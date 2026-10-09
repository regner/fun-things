# City asset tracker

Production commission supplement: [grant and scope](../../assets/production/commission.md),
[durable queue](../../assets/production/queue.json) and [current progress](../../assets/production/progress.md).
The commission supersedes historical concept-only restrictions below; road-tool ownership remains.

**The central list of assets we need and the districts that use them.** Updated
9 October 2026. Regner accepted the Signal Row breakdown as the starting set.
Asset-specific designs are still to be refined; no modelling or implementation
is commissioned by this tracker.

[Signal Row concept](signal-row.md) · [Old Quay concept](old-quay.md) ·
[East Docks concept](east-docks.md) · [East Docks breakdown](east-docks-assets.md) · [Ironreach concept](ironreach.md) · [Ironreach breakdown](ironreach-assets.md) · [Broadlot concept](broadlot.md) · [Broadlot breakdown](broadlot-assets.md) · [Glassward concept](glassward.md) · [Glassward breakdown](glassward-assets.md) · [Terrace Ward concept](terrace-ward.md) · [Terrace Ward breakdown](terrace-ward-assets.md) · [Northpoint concept](northpoint.md) · [Northpoint breakdown](northpoint-assets.md) · [The Crescents concept](the-crescents.md) · [The Crescents breakdown](the-crescents-assets.md) ·
[Signal Row breakdown](signal-row-assets.md) · [Old Quay breakdown](old-quay-assets.md) ·
[District review queue](README.md) · [Map areas](map-context.md).

## How to use this tracker

- Each row identifies one reusable design, component, finish or assembly reference.
  Output type distinguishes geometry from artwork/material studies and reuse-only
  references. A required assembly reference does not add another unique mesh. Record it once and
  add districts to that row as reuse is confirmed. Counts are not placed instances.
- **Needed** means included in a requested or liked district concept asset set. **To confirm** means a
  supporting item still needs a district decision. **Candidate** means preliminary
  demand inferred from a district identity. **Option** means an alternative not
  added to the current required set. **Deferred** means held outside active demand
  until surface-tooling ownership is resolved.
- **Needed in** and **Unconfirmed uses** own the district-demand relationship here.
  A district appearing under Candidate is not yet a commitment to use that asset.
- The stage and next action track progress. Required demand does not mean a finished
  asset design has been selected. Advance from asset concept to selected
  concept only after the owner's decision. Later production/import/placement stages
  are reserved for separately commissioned work; no new environment asset is built.
- Linked briefs own design details, dimensions, variants and acceptance evidence.
  Codex owns current briefs/concepts; Regner owns selection. Future production
  owners are unassigned. Keep the tracker updated when district decisions change.
- Named assembly members are tracked separately where useful, but they are not
  additional complete buildings: Terrace Ward assembly references reuse its module
  entries; a hall roof ring belongs to its hall, and the
  footbridge's three spans belong to one bridge. A row containing an artwork or
  variant set is explicitly a set; split it when individual variants are selected.

Current environment coverage: **223 member/set records across 62 brief families**.
**164 records are needed**, including **7 assembly/interface references**
that reuse other records. **29 records have supporting uses to confirm**;
some are already needed elsewhere. **15 records are deferred** at the surface-tooling
boundary; the remaining records are candidates or options. Counts are unique
planning records, not placed instances or independent 3D model counts.

[Registry review and ownership decisions](asset-registry-review.md).

Road surfaces are excluded and delegated to future automatic tooling. Existing
roads remain layout context; The Crescents’ requested eastern cul-de-sac is a
concept-only addition and does not introduce road-surface assets. Road-marking references remain deferred to future tooling; parking asphalt,
walkway output and apron artwork await that ownership boundary.

## District key and review state

| Code | District | Demand review |
| --- | --- | --- |
| 01 | Northpoint | Detailed breakdown recorded; university/lighthouse revisions in review; pavilion liked |
| 02 | The Crescents | Revision 02 liked; building/prop and boardwalk breakdown recorded |
| 03 | Terrace Ward | Detailed set recorded; modular kit required; supporting props to confirm |
| 04 | Glassward | Direction liked; district asset set recorded; supporting details to confirm |
| 05 | Old Quay | Detailed set reconciled with current concept; supporting props to confirm |
| 06 | Signal Row | Starting set agreed; supporting props to confirm |
| 07 | Broadlot | Detailed district set recorded; supporting props to confirm |
| 08 | Ironreach | Revision 02 liked; detailed district set and shared uses recorded; supporting props to confirm |
| 09 | East Docks | Direction liked; detailed asset set recorded; boardwalk excluded |

District names may change; codes follow the selected map polygons. “All nine”
means codes 01–09 and is used only for candidate reuse, not blanket approval.

## Shared assets and Signal Row starting set

| Asset and stable ID | Output type | Needed in | Unconfirmed uses | Stage | Next action | Brief |
| --- | --- | --- | --- | --- | --- | --- |
| Ordinary street pole · `city_lights.01` | Model design | 01, 02, 03, 04, 05, 06, 07, 08, 09 | — | Source/export delivered | Godot integration and independent review pending | [Brief](../../assets/city_lights.md) |
| Short pedestrian fixture · `city_lights.02` | Model design | 01, 02, 03, 04, 05, 06, 07, 08 | — | Source/export delivered | Godot integration and independent review pending | [Brief](../../assets/city_lights.md) |
| Wall light · `city_lights.04` | Model design | 01, 02, 03, 04, 05, 06, 07, 08, 09 | — | Source/export delivered | Godot integration and independent review pending | [Brief](../../assets/city_lights.md) |
| Flat wall panel · `city_sign_supports.01` | Model design | 01, 02, 04, 05, 06, 07, 08, 09 | Candidate: 03 | Modeling | Astra medium source production; see production queue | [Brief](../../assets/city_sign_supports.md) |
| Low rectangular planter · `city_planting.01` | Model design | 03, 04, 05, 06, 07 | Candidate: 01, 02 | Modeling | Astra medium source production; see production queue | [Brief](../../assets/city_planting.md) |
| Round planter · `city_planting.02` | Model design | 03, 04, 05, 06, 07 | Candidate: 01, 02 | Modeling | Astra medium source production; see production queue | [Brief](../../assets/city_planting.md) |
| Low shrub cluster · `city_planting.03` | Model design | 01, 02, 03, 04, 05, 06, 07, 08, 09 | — | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_planting.md) |
| Small broad-canopy tree · `city_planting.04` | Model design | 01, 02, 03, 04, 05, 06, 07, 08, 09 | — | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_planting.md) |
| Low weed/rough-grass clump set · `city_planting.05` | Component set | 08 | — | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_planting.md) |
| Broad vent · `city_roof_details.01` | Component design | 04, 06, 07, 08, 09 | Candidate: 01, 02, 03, 05 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_roof_details.md) |
| Compact plant enclosure · `city_roof_details.02` | Component design | 04, 06, 07, 08, 09 | Candidate: 01, 02, 03, 05 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_roof_details.md) |
| Short canopy · `city_shop_fittings.01` | Component design | 02, 05, 06, 07 | Candidate: 03 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_shop_fittings.md) |
| Flat fascia frame · `city_shop_fittings.02` | Component design | 02, 05, 06, 07 | Candidate: 03 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_shop_fittings.md) |
| Recessed entrance surround · `city_shop_fittings.03` | Component design | 02, 05, 06, 07 | Candidate: 03 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_shop_fittings.md) |
| Display-window glazing and frame bay · `city_shop_fittings.05` | Component design | 02, 05, 06, 07 | Candidate: 03 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_shop_fittings.md) |
| Glazed entrance door leaf, with single/double-width variants · `city_shop_fittings.06` | Component design | 02, 05, 06, 07 | Candidate: 03 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_shop_fittings.md) |
| Broad upper-floor window group · `city_shop_fittings.07` | Component design | 05, 06 | Candidate: 02, 03, 07 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_shop_fittings.md) |
| Projecting blade-sign body and mounting bracket · `city_shop_fittings.08` | Component design | 06 | Candidate: 02, 03, 05, 07 | Asset concept needed | Define asset shape / variants | [Brief](../../assets/city_shop_fittings.md) |
| Narrow inline shell · `city_small_shop_shells.01` | Model design | 06, 07 | Candidate: 02, 03, 05 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_small_shop_shells.md) |
| Wide standalone shell · `city_small_shop_shells.02` | Model design | 06, 07 | Candidate: 02, 03, 05 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_small_shop_shells.md) |
| Compact square shop shell · `city_small_shop_shells.04` | Model design | 06, 07 | Candidate: 02, 03, 05 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_small_shop_shells.md) |
| Rounded hall shell · `d06_entertainment_hall.01` | Model design | 06 | — | Asset concept needed | Define asset shape / variants | [Brief](../../assets/d06_entertainment_hall.md) |
| Broad roof-ring trim · `d06_entertainment_hall.02` | Component design | 06 | — | Asset concept needed | Define asset shape / variants | [Brief](../../assets/d06_entertainment_hall.md) |
| Entry canopy · `d06_entertainment_hall.03` | Component design | 06 | — | Asset concept needed | Define asset shape / variants | [Brief](../../assets/d06_entertainment_hall.md) |
| Short cylindrical poster support · `d06_poster_drum.01` | Model design | 06 | — | Asset concept needed | Define asset shape / variants | [Brief](../../assets/d06_poster_drum.md) |
| Cap variant · `d06_poster_drum.02` | Component design | 06 | — | Asset concept needed | Define asset shape / variants | [Brief](../../assets/d06_poster_drum.md) |
| Hall title graphic · `d06_commercial_graphics.01` | Artwork set | 06 | — | Asset concept needed | Explore fictional tenant graphics | [Brief](../../assets/d06_commercial_graphics.md) |
| Three contrasting shop-fascia artworks · `d06_commercial_graphics.02` | Artwork set | 06 | — | Asset concept needed | Explore fictional tenant graphics | [Brief](../../assets/d06_commercial_graphics.md) |
| Two poster wraps · `d06_commercial_graphics.03` | Artwork set | 06 | — | Asset concept needed | Explore fictional tenant graphics | [Brief](../../assets/d06_commercial_graphics.md) |
| Passage wayfinding face · `d06_commercial_graphics.04` | Artwork set | 06 | — | Asset concept needed | Explore fictional tenant graphics | [Brief](../../assets/d06_commercial_graphics.md) |
| Continuous long building shell and roof · `d06_southern_shopping_parade.01` | Model design | 06 | — | Asset concept needed | Define asset shape / variants | [Brief](../../assets/d06_southern_shopping_parade.md) |
| Repeatable storefront bay interface · `d06_southern_shopping_parade.02` | Interface reference | 06 | — | Reference; no extra mesh | Define openings/mounts; reuse city_shop_fittings | [Brief](../../assets/d06_southern_shopping_parade.md) |
| North-end facade facing the bridge forecourt · `d06_southern_shopping_parade.03` | Component design | 06 | — | Asset concept needed | Define asset shape / variants | [Brief](../../assets/d06_southern_shopping_parade.md) |
| Shared raised junction deck · `d06_harbour_footbridge.01` | Component design | 05, 06 | — | Asset concept needed | Resolve three landings and deck form | [Brief](../../assets/d06_harbour_footbridge.md) |
| Main-area connecting span · `d06_harbour_footbridge.02` | Component design | 05, 06 | — | Asset concept needed | Resolve three landings and deck form | [Brief](../../assets/d06_harbour_footbridge.md) |
| Southern-area connecting span · `d06_harbour_footbridge.03` | Component design | 05, 06 | — | Asset concept needed | Resolve three landings and deck form | [Brief](../../assets/d06_harbour_footbridge.md) |
| Westward Old Quay connecting span · `d06_harbour_footbridge.04` | Component design | 05, 06 | — | Asset concept needed | Resolve three landings and deck form | [Brief](../../assets/d06_harbour_footbridge.md) |
| Ground-access stair/landing assembly, adapted at three ends · `d06_harbour_footbridge.05` | Component set | 05, 06 | — | Asset concept needed | Resolve three landings and deck form | [Brief](../../assets/d06_harbour_footbridge.md) |
| Matching railing, edge-light and support family · `d06_harbour_footbridge.06` | Component set | 05, 06 | — | Asset concept needed | Resolve three landings and deck form | [Brief](../../assets/d06_harbour_footbridge.md) |

## Old Quay requested docks and yachts

The owner requested docks with yachts after liking the harbour direction. Two dock
clusters and six moored boats are illustration choices, not selected quantities.
The two yacht silhouettes are proposed designs within the requested yacht family.
These reusable assets currently have only district 05 as a needed user.

| Asset and stable ID | Output type | Needed in | Unconfirmed uses | Stage | Next action | Brief |
| --- | --- | --- | --- | --- | --- | --- |
| Main floating-pontoon section · `city_marina_docks.01` | Component design | 05 | — | Asset concept needed | Refine dock fit and yacht silhouettes | [Brief](../../assets/city_marina_docks.md) |
| Narrow finger-pontoon section · `city_marina_docks.02` | Component design | 05 | — | Asset concept needed | Refine dock fit and yacht silhouettes | [Brief](../../assets/city_marina_docks.md) |
| Shore-to-pontoon gangway and landing connector · `city_marina_docks.03` | Component design | 05 | — | Asset concept needed | Refine dock fit and yacht silhouettes | [Brief](../../assets/city_marina_docks.md) |
| Dock end/corner connector and edge bumper treatment · `city_marina_docks.04` | Component design | 05 | — | Asset concept needed | Refine dock fit and yacht silhouettes | [Brief](../../assets/city_marina_docks.md) |
| Small dock mooring cleat · `city_marina_docks.05` | Component design | 05 | — | Asset concept needed | Refine dock fit and yacht silhouettes | [Brief](../../assets/city_marina_docks.md) |
| Compact motor yacht, hull/deck/cabin assembly · `city_moored_yachts.01` | Model design | 05 | — | Asset concept needed | Refine dock fit and yacht silhouettes | [Brief](../../assets/city_moored_yachts.md) |
| Small sailing yacht with simple mast and furled sail · `city_moored_yachts.02` | Model design | 05 | — | Asset concept needed | Refine dock fit and yacht silhouettes | [Brief](../../assets/city_moored_yachts.md) |

## Shared supporting items to confirm

| Asset and stable ID | Output type | Needed in | Unconfirmed uses | Stage | Next action | Brief |
| --- | --- | --- | --- | --- | --- | --- |
| Freestanding low panel · `city_sign_supports.02` | Model design | 04, 05, 07, 08, 09 | Confirm: 01, 02, 06; Candidate: 03 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_sign_supports.md) |
| Straight bench · `city_seating.01` | Model design | 01, 03, 04, 05 | Confirm: 02, 06, 07, 08 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_seating.md) |
| Short low plaza seat · `city_seating.02` | Model design | — | Confirm: 06; Candidate: 01, 02, 03, 04, 05, 07 | Brief drafted | Confirm against Signal Row detail concept | [Brief](../../assets/city_seating.md) |
| Public bin · `city_waste.01` | Model design | — | Confirm: 01, 02, 03, 04, 05, 06, 07, 08, 09 | Brief drafted | Confirm supporting uses in district detail concepts | [Brief](../../assets/city_waste.md) |
| Short bollard · `city_barriers.01` | Model design | — | Confirm: 03, 04, 05, 06, 07, 08, 09; Candidate: 01, 02 | Brief drafted | Confirm supporting uses in district detail concepts | [Brief](../../assets/city_barriers.md) |
| Utility cabinet · `city_service_furniture.01` | Model design | — | Confirm: 03, 04, 05, 06, 07, 08, 09; Candidate: 01, 02 | Brief drafted | Confirm supporting uses in district detail concepts | [Brief](../../assets/city_service_furniture.md) |
| Closed service door and surround · `city_service_furniture.03` | Model design | — | Confirm: 03, 04, 05, 06, 07, 08, 09; Candidate: 01, 02 | Brief drafted | Confirm supporting uses in district detail concepts | [Brief](../../assets/city_service_furniture.md) |
| Closed shutter · `city_shop_fittings.04` | Component design | — | Confirm: 06; Candidate: 02, 03, 05, 07 | Brief drafted | Confirm against Signal Row detail concept | [Brief](../../assets/city_shop_fittings.md) |

## Shared island boardwalk

The owner likes the Crescents revision and requests its asset breakdown. The deck kit
is needed in Northpoint, The Crescents, Terrace Ward, Glassward, Broadlot and Ironreach.
Old Quay route fit remains to confirm; East Docks is excluded. Timber appearance and exact kit dimensions still need asset review.

| Asset and stable ID | Output type | Needed in | Unconfirmed uses | Stage | Next action | Brief |
| --- | --- | --- | --- | --- | --- | --- |
| Straight deck section · `city_boardwalk.01` | Component design | 01, 02, 03, 04, 07, 08 | Candidate: 05 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_boardwalk.md) |
| Bend/corner deck section · `city_boardwalk.02` | Component design | 01, 02, 03, 04, 07, 08 | Candidate: 05 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_boardwalk.md) |
| Edge fascia and trim · `city_boardwalk.03` | Component design | 01, 02, 03, 04, 07, 08 | Candidate: 05 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_boardwalk.md) |
| Coastal support assembly · `city_boardwalk.04` | Component design | 01, 02, 03, 04, 07, 08 | Candidate: 05 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_boardwalk.md) |
| Landward access / promenade transition · `city_boardwalk.05` | Component design | 01, 02, 03, 04, 07, 08 | Candidate: 05 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_boardwalk.md) |

East Docks has no boardwalk demand. The northern and southwestern terminals
belong to Ironreach (08) and Broadlot (07), reusing deck fascia/trim, landward
transitions and the shared low waterfront rail.

## Shared city assets and candidates

| Asset and stable ID | Output type | Needed in | Unconfirmed uses | Stage | Next action | Brief |
| --- | --- | --- | --- | --- | --- | --- |
| Straight edge · `city_walkways.01` | Model design | — | — | Deferred: surface boundary | Resolve future tooling scope before selecting art outputs | [Brief](../../assets/city_walkways.md) |
| Outside corner · `city_walkways.02` | Model design | — | — | Deferred: surface boundary | Resolve future tooling scope before selecting art outputs | [Brief](../../assets/city_walkways.md) |
| Inside corner · `city_walkways.03` | Model design | — | — | Deferred: surface boundary | Resolve future tooling scope before selecting art outputs | [Brief](../../assets/city_walkways.md) |
| Crossing edge · `city_walkways.04` | Model design | — | — | Deferred: surface boundary | Resolve future tooling scope before selecting art outputs | [Brief](../../assets/city_walkways.md) |
| Alley strip · `city_walkways.05` | Model design | — | — | Deferred: surface boundary | Resolve future tooling scope before selecting art outputs | [Brief](../../assets/city_walkways.md) |
| Plain plaza paving · `city_ground_finishes.01` | Material study | 01, 03, 04, 05, 06, 07 | — | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_ground_finishes.md) |
| Service concrete · `city_ground_finishes.02` | Material study | 08, 09 | Candidate: 06, 07 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_ground_finishes.md) |
| Parking asphalt · `city_ground_finishes.03` | Material study | — | — | Deferred: surface boundary | Resolve future tooling scope before selecting art outputs | [Brief](../../assets/city_ground_finishes.md) |
| Short grass · `city_ground_finishes.04` | Material study | 01, 02, 03, 04, 05, 07, 08 | — | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_ground_finishes.md) |
| Quiet garden soil · `city_ground_finishes.05` | Material study | 01, 02, 03, 04, 05, 07, 08 | — | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_ground_finishes.md) |
| Lane line · `city_road_markings.01` | Artwork set | — | — | Deferred: surface boundary | Resolve future tooling scope before selecting art outputs | [Brief](../../assets/city_road_markings.md) |
| Stop line · `city_road_markings.02` | Artwork set | — | — | Deferred: surface boundary | Resolve future tooling scope before selecting art outputs | [Brief](../../assets/city_road_markings.md) |
| Crossing · `city_road_markings.03` | Artwork set | — | — | Deferred: surface boundary | Resolve future tooling scope before selecting art outputs | [Brief](../../assets/city_road_markings.md) |
| Direction arrow · `city_road_markings.04` | Artwork set | — | — | Deferred: surface boundary | Resolve future tooling scope before selecting art outputs | [Brief](../../assets/city_road_markings.md) |
| Parking bay · `city_road_markings.05` | Artwork set | — | — | Deferred: surface boundary | Resolve future tooling scope before selecting art outputs | [Brief](../../assets/city_road_markings.md) |
| Loading bay · `city_road_markings.06` | Artwork set | — | — | Deferred: surface boundary | Resolve future tooling scope before selecting art outputs | [Brief](../../assets/city_road_markings.md) |
| Low seawall · `city_shore_edges.01` | Component design | 01, 02, 03, 04, 05, 07, 08, 09 | — | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_shore_edges.md) |
| Quay edge · `city_shore_edges.02` | Component design | 05, 09 | Candidate: 01, 02, 03, 04, 07, 08 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_shore_edges.md) |
| Simple rock shore · `city_shore_edges.03` | Component design | 01, 02, 03, 04, 05, 07, 08, 09 | — | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_shore_edges.md) |
| Edge corner · `city_shore_edges.04` | Component set | 01, 02, 03, 04, 05, 07, 08, 09 | — | Asset concept needed | Refine shared corner/end interfaces for coastal edge kit | [Brief](../../assets/city_shore_edges.md) |
| Open sea surface look · `city_water_look.01` | Material study | 01, 02, 03, 04, 05, 07, 08, 09 | — | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_water_look.md) |
| Quieter basin surface look · `city_water_look.02` | Material study | 05 | — | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_water_look.md) |
| Single level-deck bridge · `city_harbour_bridge.01` | Model design | 05 | — | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_harbour_bridge.md) |
| Matching low parapet pair · `city_harbour_bridge.02` | Component set | 05 | — | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_harbour_bridge.md) |
| Bank-end trim · `city_harbour_bridge.03` | Component design | 05 | — | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_harbour_bridge.md) |
| Yard pole · `city_lights.03` | Model design | 07, 08, 09 | — | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_lights.md) |
| Signal pole · `city_traffic_fixtures.01` | Model design | — | Candidate: All nine | Brief drafted | Confirm district use; not in Signal Row starting set | [Brief](../../assets/city_traffic_fixtures.md) |
| Signal head · `city_traffic_fixtures.02` | Model design | — | Candidate: All nine | Brief drafted | Confirm district use; not in Signal Row starting set | [Brief](../../assets/city_traffic_fixtures.md) |
| Small road-sign support · `city_traffic_fixtures.03` | Model design | — | Candidate: All nine | Brief drafted | Confirm district use; not in Signal Row starting set | [Brief](../../assets/city_traffic_fixtures.md) |
| Noticeboard · `city_sign_supports.03` | Model design | — | Confirm: 03, 05; Candidate: 01, 02, 06 | Brief drafted | Confirm supporting uses in district detail concepts | [Brief](../../assets/city_sign_supports.md) |
| Wayfinding post · `city_sign_supports.04` | Model design | — | Confirm: 01; Candidate: 02, 03, 04, 05, 06, 07, 08, 09 | Brief drafted | Confirm supporting uses in district detail concepts | [Brief](../../assets/city_sign_supports.md) |
| Corner seat · `city_seating.03` | Model design | — | Candidate: 01, 02, 03, 04, 05, 06, 07 | Brief drafted | Confirm district use; not in Signal Row starting set | [Brief](../../assets/city_seating.md) |
| Domestic wheelie bin · `city_waste.02` | Model design | — | Confirm: 02, 03 | Brief drafted | Confirm supporting uses in district detail concepts | [Brief](../../assets/city_waste.md) |
| Service dumpster · `city_waste.03` | Model design | 08 | Confirm: 07, 09; Candidate: 05, 06 | Asset concept needed | Confirm supporting uses in district detail concepts | [Brief](../../assets/city_waste.md) |
| Landward-rail assembly reference · `city_barriers.02` | Assembly reference | — | Candidate: All nine | Reference; no extra mesh | Reuse city_quay_furniture.02 with landward mounting | [Brief](../../assets/city_barriers.md) |
| Low service barrier · `city_barriers.03` | Model design | — | Confirm: 08, 09; Candidate: 01, 02, 03, 04, 05, 06, 07 | Brief drafted | Confirm supporting uses in district detail concepts | [Brief](../../assets/city_barriers.md) |
| Rail-terminal assembly reference · `city_barriers.04` | Assembly reference | — | Candidate: All nine | Reference; no extra mesh | Reuse city_quay_furniture.02 terminal/return parts | [Brief](../../assets/city_barriers.md) |
| Chain-link panel · `city_barriers.05` | Model design | 08 | Confirm: 09 | Asset concept needed | Confirm supporting uses in district detail concepts | [Brief](../../assets/city_barriers.md) |
| Chain-link post/bracing set · `city_barriers.06` | Component set | 08 | Confirm: 09 | Asset concept needed | Confirm supporting uses in district detail concepts | [Brief](../../assets/city_barriers.md) |
| Paired chain-link vehicle gate · `city_barriers.07` | Component set | 08 | Confirm: 09 | Asset concept needed | Confirm supporting uses in district detail concepts | [Brief](../../assets/city_barriers.md) |
| Roof access housing · `city_roof_details.03` | Component design | — | Candidate: All nine | Brief drafted | Confirm district use; not in Signal Row starting set | [Brief](../../assets/city_roof_details.md) |
| Drain cover · `city_service_furniture.02` | Model design | — | Confirm: 08, 09; Candidate: 01, 02, 03, 04, 05, 06, 07 | Brief drafted | Confirm supporting uses in district detail concepts | [Brief](../../assets/city_service_furniture.md) |
| Mooring bollard · `city_quay_furniture.01` | Model design | 05, 09 | — | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_quay_furniture.md) |
| Low quay rail · `city_quay_furniture.02` | Model design | 01, 02, 03, 04, 05, 07, 08 | Confirm: 09 | Asset concept needed | Confirm supporting uses in district detail concepts | [Brief](../../assets/city_quay_furniture.md) |
| Edge ladder · `city_quay_furniture.03` | Model design | — | Confirm: 05, 09 | District concept in review | Confirm supporting uses in district detail concepts | [Brief](../../assets/city_quay_furniture.md) |
| Wheel stop · `city_parking_furniture.01` | Model design | 07 | Confirm: 08, 09; Candidate: 01, 02, 03, 04, 05, 06 | Asset concept needed | Confirm supporting uses in district detail concepts | [Brief](../../assets/city_parking_furniture.md) |
| Parking-sign assembly reference · `city_parking_furniture.02` | Assembly reference | 07 | Confirm: 08, 09; Candidate: 01, 02, 03, 04, 05, 06 | Reference; no extra mesh | Reuse city_sign_supports.02 and selected parking artwork | [Brief](../../assets/city_parking_furniture.md) |
| Cycle stand · `city_parking_furniture.03` | Model design | — | Confirm: 01, 03; Candidate: 04, 06 | Brief drafted | Confirm supporting uses in district detail concepts | [Brief](../../assets/city_parking_furniture.md) |
| Simple bus-stop sign · `city_parking_furniture.04` | Model design | — | Candidate: All nine | Brief drafted | Confirm district use; not in Signal Row starting set | [Brief](../../assets/city_parking_furniture.md) |
| L-shaped corner shell · `city_small_shop_shells.03` | Model design | — | Candidate: 02, 03, 05, 07 | Brief drafted | Review in district concept | [Brief](../../assets/city_small_shop_shells.md) |
| Small pitched-roof chimney · `city_roof_details.04` | Component design | 02, 05 | Candidate: 03 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_roof_details.md) |
| Simplified dormer window and roof housing · `city_roof_details.05` | Component design | 02, 05 | Candidate: 03 | Asset concept needed | Refine shared design for recorded districts | [Brief](../../assets/city_roof_details.md) |

## 01 Northpoint assets

| Asset and stable ID | Output type | Needed in | Unconfirmed uses | Stage | Next action | Brief |
| --- | --- | --- | --- | --- | --- | --- |
| Main university hall with connected wings · `d01_academic_buildings.01` | Model design | 01 | — | University revision in review | Review collegiate hall design and map fit | [Brief](../../assets/d01_academic_buildings.md) |
| Long teaching wing · `d01_academic_buildings.02` | Model design | 01 | — | Asset concept needed | Refine design from Northpoint breakdown | [Brief](../../assets/d01_academic_buildings.md) |
| Compact annex · `d01_academic_buildings.03` | Model design | 01 | — | Asset concept needed | Refine design from Northpoint breakdown | [Brief](../../assets/d01_academic_buildings.md) |
| Crescent sports pavilion · `d01_sports_pavilion.01` | Model design | 01 | — | Direction liked | Preserve curved field-side design; refine asset details | [Brief](../../assets/d01_sports_pavilion.md) |
| Short end-wing variant · `d01_sports_pavilion.02` | Model design | — | Candidate: 01 | District concept in review | Review campus direction and plot fit | [Brief](../../assets/d01_sports_pavilion.md) |
| Oval track finish and lane graphics · `d01_sports_surface.01` | Artwork set | 01 | — | Asset concept needed | Refine design from Northpoint breakdown | [Brief](../../assets/d01_sports_surface.md) |
| Field line graphics · `d01_sports_surface.02` | Artwork set | 01 | — | Asset concept needed | Refine design from Northpoint breakdown | [Brief](../../assets/d01_sports_surface.md) |
| Small court graphics · `d01_sports_surface.03` | Artwork set | — | Candidate: 01 | District concept in review | Review campus direction and plot fit | [Brief](../../assets/d01_sports_surface.md) |
| Campus-map face · `d01_campus_graphics.01` | Artwork set | — | Confirm: 01 | District concept in review | Confirm supporting uses in district detail concepts | [Brief](../../assets/d01_campus_graphics.md) |
| Entry panel face · `d01_campus_graphics.02` | Artwork set | 01 | — | Asset concept needed | Refine design from Northpoint breakdown | [Brief](../../assets/d01_campus_graphics.md) |
| Route-arrow set · `d01_campus_graphics.03` | Artwork set | — | Confirm: 01 | District concept in review | Confirm supporting uses in district detail concepts | [Brief](../../assets/d01_campus_graphics.md) |
| Coastal lighthouse assembly · `d01_lighthouse.01` | Model design | 01 | — | Lighthouse concept in review | Refine tower, lantern and coastal fit | [Brief](../../assets/d01_lighthouse.md) |

## 02 The Crescents assets

| Asset and stable ID | Output type | Needed in | Unconfirmed uses | Stage | Next action | Brief |
| --- | --- | --- | --- | --- | --- | --- |
| Detached house · `d02_house_family.01` | Model design | 02 | — | Asset concept needed | Refine asset design from Crescents v02 | [Brief](../../assets/d02_house_family.md) |
| Paired house · `d02_house_family.02` | Model design | 02 | — | Asset concept needed | Refine asset design from Crescents v02 | [Brief](../../assets/d02_house_family.md) |
| Short terrace · `d02_house_family.03` | Model design | 02 | — | Asset concept needed | Refine asset design from Crescents v02 | [Brief](../../assets/d02_house_family.md) |
| Compact corner home · `d02_house_family.04` | Model design | — | Candidate: 02 | Optional design candidate | Use core buildings unless a distinct design is selected | [Brief](../../assets/d02_house_family.md) |
| Wedge-footprint shop shell · `d02_corner_shop.01` | Model design | 02 | — | Asset concept needed | Refine asset design from Crescents v02 | [Brief](../../assets/d02_corner_shop.md) |
| Small rear annex · `d02_corner_shop.02` | Model design | — | Candidate: 02 | Optional design candidate | Use core buildings unless a distinct design is selected | [Brief](../../assets/d02_corner_shop.md) |
| Short garden-wall run · `d02_domestic_details.01` | Model design | 02 | — | Asset concept needed | Refine asset design from Crescents v02 | [Brief](../../assets/d02_domestic_details.md) |
| Wall return · `d02_domestic_details.02` | Model design | 02 | — | Asset concept needed | Refine asset design from Crescents v02 | [Brief](../../assets/d02_domestic_details.md) |
| Mailbox · `d02_domestic_details.03` | Model design | — | Confirm: 02 | District concept in review | Confirm supporting use in district detail concepts | [Brief](../../assets/d02_domestic_details.md) |
| Small porch canopy · `d02_domestic_details.04` | Model design | 02 | — | Asset concept needed | Refine asset design from Crescents v02 | [Brief](../../assets/d02_domestic_details.md) |
| Watch notice · `d02_neighbourhood_graphics.01` | Artwork set | — | Confirm: 02 | District concept in review | Confirm supporting use in district detail concepts | [Brief](../../assets/d02_neighbourhood_graphics.md) |
| Parking-request notice · `d02_neighbourhood_graphics.02` | Artwork set | — | Confirm: 02 | District concept in review | Confirm supporting use in district detail concepts | [Brief](../../assets/d02_neighbourhood_graphics.md) |
| Corner-shop fascia art · `d02_neighbourhood_graphics.03` | Artwork set | 02 | — | Asset concept needed | Refine asset design from Crescents v02 | [Brief](../../assets/d02_neighbourhood_graphics.md) |

## 03 Terrace Ward assets

| Asset and stable ID | Output type | Needed in | Unconfirmed uses | Stage | Next action | Brief |
| --- | --- | --- | --- | --- | --- | --- |
| L-shaped apartment group assembly reference · `d03_apartment_family.01` | Assembly reference | 03 | — | Reference; no extra mesh | Compose from d03_apartment_family.05–.11; no one-off building | [Brief](../../assets/d03_apartment_family.md) |
| U-shaped open group assembly reference · `d03_apartment_family.02` | Assembly reference | 03 | — | Reference; no extra mesh | Compose from d03_apartment_family.05–.11; no one-off building | [Brief](../../assets/d03_apartment_family.md) |
| Short infill block assembly reference · `d03_apartment_family.03` | Assembly reference | 03 | — | Reference; no extra mesh | Compose from d03_apartment_family.05–.11; no one-off building | [Brief](../../assets/d03_apartment_family.md) |
| Stepped bar assembly reference · `d03_apartment_family.04` | Assembly reference | 03 | — | Reference; no extra mesh | Compose from d03_apartment_family.05–.11; no one-off building | [Brief](../../assets/d03_apartment_family.md) |
| Short frame · `d03_laundry_frames.01` | Model design | 03 | — | Asset concept needed | Refine design from Terrace Ward breakdown | [Brief](../../assets/d03_laundry_frames.md) |
| Corner frame · `d03_laundry_frames.02` | Model design | — | Candidate: 03 | District direction liked; asset candidate | Refine district asset selection | [Brief](../../assets/d03_laundry_frames.md) |
| Two restrained hanging-cloth shapes · `d03_laundry_frames.03` | Component set | 03 | — | Asset concept needed | Refine design from Terrace Ward breakdown | [Brief](../../assets/d03_laundry_frames.md) |
| Large circular paving motif · `d03_court_graphics.01` | Artwork set | 03 | — | Asset concept needed | Refine design from Terrace Ward breakdown | [Brief](../../assets/d03_court_graphics.md) |
| Small play-marking graphic · `d03_court_graphics.02` | Artwork set | 03 | — | Asset concept needed | Refine design from Terrace Ward breakdown | [Brief](../../assets/d03_court_graphics.md) |
| Community board face · `d03_community_graphics.01` | Artwork set | — | Confirm: 03 | District direction liked; asset candidate | Confirm supporting uses in district detail concepts | [Brief](../../assets/d03_community_graphics.md) |
| Entrance-number set · `d03_community_graphics.02` | Artwork set | 03 | — | Asset concept needed | Refine design from Terrace Ward breakdown | [Brief](../../assets/d03_community_graphics.md) |
| Local-shop fascia art · `d03_community_graphics.03` | Artwork set | — | Candidate: 03 | District direction liked; asset candidate | Refine district asset selection | [Brief](../../assets/d03_community_graphics.md) |
| Straight one-storey apartment bay · `d03_apartment_family.05` | Component design | 03 | — | Modular concept needed | Refine common dimensions, joins and assembly examples | [Brief](../../assets/d03_apartment_family.md) |
| Inside/outside corner bay set · `d03_apartment_family.06` | Component set | 03 | — | Modular concept needed | Refine common dimensions, joins and assembly examples | [Brief](../../assets/d03_apartment_family.md) |
| Finished end bay / wall closure · `d03_apartment_family.07` | Component design | 03 | — | Modular concept needed | Refine common dimensions, joins and assembly examples | [Brief](../../assets/d03_apartment_family.md) |
| Ground-floor entrance bay · `d03_apartment_family.08` | Component design | 03 | — | Modular concept needed | Refine common dimensions, joins and assembly examples | [Brief](../../assets/d03_apartment_family.md) |
| Balcony / loggia frontage insert · `d03_apartment_family.09` | Component design | 03 | — | Modular concept needed | Refine common dimensions, joins and assembly examples | [Brief](../../assets/d03_apartment_family.md) |
| Straight/end/corner roof-cap set · `d03_apartment_family.10` | Component set | 03 | — | Modular concept needed | Refine common dimensions, joins and assembly examples | [Brief](../../assets/d03_apartment_family.md) |
| Height-step closure · `d03_apartment_family.11` | Component design | 03 | — | Modular concept needed | Refine common dimensions, joins and assembly examples | [Brief](../../assets/d03_apartment_family.md) |

The four apartment composition records above reuse the seven proposed module
records. They are not additional unique whole-building commissions.

## 04 Glassward assets

| Asset and stable ID | Output type | Needed in | Unconfirmed uses | Stage | Next action | Brief |
| --- | --- | --- | --- | --- | --- | --- |
| Rectangular-crown tower · `d04_towers.01` | Model design | 04 | — | Asset concept needed | Refine design from Glassward breakdown | [Brief](../../assets/d04_towers.md) |
| Chamfered-crown tower · `d04_towers.02` | Model design | 04 | — | Asset concept needed | Refine design from Glassward breakdown | [Brief](../../assets/d04_towers.md) |
| Rounded-crown tower · `d04_towers.03` | Model design | 04 | — | Asset concept needed | Refine design from Glassward breakdown | [Brief](../../assets/d04_towers.md) |
| Mid-height tower · `d04_towers.04` | Model design | 04 | — | Asset concept needed | Refine design from Glassward breakdown | [Brief](../../assets/d04_towers.md) |
| Low office block · `d04_podiums.01` | Model design | 04 | — | Asset concept needed | Refine design from Glassward breakdown | [Brief](../../assets/d04_podiums.md) |
| Setback podium · `d04_podiums.02` | Model design | 04 | — | Asset concept needed | Refine design from Glassward breakdown | [Brief](../../assets/d04_podiums.md) |
| Short service-wing shell · `d04_podiums.03` | Model design | — | Candidate: 04 | District concept in review | Review tower/forecourt direction and map fit | [Brief](../../assets/d04_podiums.md) |
| Broad paving band · `d04_forecourt_graphics.01` | Artwork set | 04 | — | Asset concept needed | Refine design from Glassward breakdown | [Brief](../../assets/d04_forecourt_graphics.md) |
| Entry-axis motif · `d04_forecourt_graphics.02` | Artwork set | 04 | — | Asset concept needed | Refine design from Glassward breakdown | [Brief](../../assets/d04_forecourt_graphics.md) |
| Quiet inset emblem · `d04_forecourt_graphics.03` | Artwork set | — | Candidate: 04 | District concept in review | Review tower/forecourt direction and map fit | [Brief](../../assets/d04_forecourt_graphics.md) |
| Large facade panel art · `d04_corporate_graphics.01` | Artwork set | 04 | — | Asset concept needed | Refine design from Glassward breakdown | [Brief](../../assets/d04_corporate_graphics.md) |
| Low directory face · `d04_corporate_graphics.02` | Artwork set | 04 | — | Asset concept needed | Refine design from Glassward breakdown | [Brief](../../assets/d04_corporate_graphics.md) |
| Entry wordmark · `d04_corporate_graphics.03` | Artwork set | 04 | — | Asset concept needed | Refine design from Glassward breakdown | [Brief](../../assets/d04_corporate_graphics.md) |

## 05 Old Quay assets

| Asset and stable ID | Output type | Needed in | Unconfirmed uses | Stage | Next action | Brief |
| --- | --- | --- | --- | --- | --- | --- |
| Narrow shop-home · `d05_quay_frontages.01` | Model design | 05 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d05_quay_frontages.md) |
| Short frontage row · `d05_quay_frontages.02` | Model design | 05 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d05_quay_frontages.md) |
| Compact hipped-roof infill house · `d05_quay_frontages.03` | Model design | 05 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d05_quay_frontages.md) |
| Deep-roof corner shell · `d05_quay_frontages.04` | Model design | — | Candidate: 05 | Breakdown drafted | Review Old Quay asset set | [Brief](../../assets/d05_quay_frontages.md) |
| Harbour hall exterior · `d05_harbour_hall.01` | Model design | 05 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d05_harbour_hall.md) |
| Entry canopy · `d05_harbour_hall.02` | Component design | 05 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d05_harbour_hall.md) |
| Hall fascia art · `d05_civic_graphics.01` | Artwork set | 05 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d05_civic_graphics.md) |
| Noticeboard face · `d05_civic_graphics.02` | Artwork set | — | Confirm: 05 | Breakdown drafted | Confirm supporting uses in district detail concepts | [Brief](../../assets/d05_civic_graphics.md) |
| Quay direction panel · `d05_civic_graphics.03` | Artwork set | 05 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d05_civic_graphics.md) |
| Broad quay border motif · `d05_quay_paving.01` | Artwork set | 05 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d05_quay_paving.md) |
| Simple civic-square inset · `d05_quay_paving.02` | Artwork set | 05 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d05_quay_paving.md) |
| Warm shop-front fascia artwork set · `d05_civic_graphics.04` | Artwork set | 05 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d05_civic_graphics.md) |

## 06 Signal Row options

| Asset and stable ID | Output type | Needed in | Unconfirmed uses | Stage | Next action | Brief |
| --- | --- | --- | --- | --- | --- | --- |
| Short-row assembly reference · `d06_shopfront_blocks.01` | Assembly reference | — | Option: 06 | Reference; no extra mesh | Reuse city_small_shop_shells.02 and city_shop_fittings | [Brief](../../assets/d06_shopfront_blocks.md) |
| Deep rear-court shell · `d06_shopfront_blocks.02` | Model design | — | Option: 06 | Alternative study | Revisit only if current shared-shell set cannot cover selected massing | [Brief](../../assets/d06_shopfront_blocks.md) |
| Chamfered corner block · `d06_shopfront_blocks.03` | Model design | — | Option: 06 | Alternative study | Revisit only if current shared-shell set cannot cover selected massing | [Brief](../../assets/d06_shopfront_blocks.md) |
| Narrow upper-floor block · `d06_mixed_use_infill.01` | Model design | — | Option: 06 | Alternative study | Revisit only if current shared-shell set cannot cover selected massing | [Brief](../../assets/d06_mixed_use_infill.md) |
| Stepped corner infill · `d06_mixed_use_infill.02` | Model design | — | Option: 06 | Alternative study | Revisit only if current shared-shell set cannot cover selected massing | [Brief](../../assets/d06_mixed_use_infill.md) |
| Short rear wing · `d06_mixed_use_infill.03` | Model design | — | Option: 06 | Alternative study | Revisit only if current shared-shell set cannot cover selected massing | [Brief](../../assets/d06_mixed_use_infill.md) |

## 07 Broadlot assets

| Asset and stable ID | Output type | Needed in | Unconfirmed uses | Stage | Next action | Brief |
| --- | --- | --- | --- | --- | --- | --- |
| Giant stepped retail box · `d07_retail_buildings.01` | Model design | 07 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d07_retail_buildings.md) |
| Secondary low retail box · `d07_retail_buildings.02` | Model design | 07 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d07_retail_buildings.md) |
| Small entrance annex · `d07_retail_buildings.03` | Component design | 07 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d07_retail_buildings.md) |
| Low circular island base · `d07_sign_island.01` | Model design | 07 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d07_sign_island.md) |
| Large restrained sign support · `d07_sign_island.02` | Model design | 07 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d07_sign_island.md) |
| Short shelter · `d07_trolley_shelter.01` | Model design | 07 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d07_trolley_shelter.md) |
| Single trolley · `d07_trolley_shelter.02` | Model design | 07 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d07_trolley_shelter.md) |
| Compact nested trolley group · `d07_trolley_shelter.03` | Assembly reference | 07 | — | Reference; no extra mesh | Arrange trolley .02; no second trolley model | [Brief](../../assets/d07_trolley_shelter.md) |
| Retail fascia art · `d07_retail_graphics.01` | Artwork set | 07 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d07_retail_graphics.md) |
| Sign-island face · `d07_retail_graphics.02` | Artwork set | 07 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d07_retail_graphics.md) |
| Parking-zone panel · `d07_retail_graphics.03` | Artwork set | 07 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d07_retail_graphics.md) |

## 08 Ironreach assets

| Asset and stable ID | Output type | Needed in | Unconfirmed uses | Stage | Next action | Brief |
| --- | --- | --- | --- | --- | --- | --- |
| Small pitched repair shed · `d08_workshop_buildings.01` | Model design | 08 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d08_workshop_buildings.md) |
| Sawtooth workshop · `d08_workshop_buildings.02` | Model design | 08 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d08_workshop_buildings.md) |
| Larger depot · `d08_workshop_buildings.03` | Model design | 08 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d08_workshop_buildings.md) |
| Attached office · `d08_workshop_buildings.04` | Component design | 08 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d08_workshop_buildings.md) |
| Tool cabinet · `d08_repair_furniture.01` | Model design | 08 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d08_repair_furniture.md) |
| Tyre rack · `d08_repair_furniture.02` | Model design | 08 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d08_repair_furniture.md) |
| Low parts trolley · `d08_repair_furniture.03` | Model design | 08 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d08_repair_furniture.md) |
| Compact workbench · `d08_repair_furniture.04` | Model design | 08 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d08_repair_furniture.md) |
| Repair fascia art · `d08_repair_graphics.01` | Artwork set | 08 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d08_repair_graphics.md) |
| Depot direction panel · `d08_repair_graphics.02` | Artwork set | 08 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d08_repair_graphics.md) |
| Service-warning face · `d08_repair_graphics.03` | Artwork set | 08 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d08_repair_graphics.md) |
| Broad work-bay marking · `d08_work_apron_graphics.01` | Artwork set | — | — | Deferred: surface boundary | Resolve future tooling scope before selecting art outputs | [Brief](../../assets/d08_work_apron_graphics.md) |
| Short caution band · `d08_work_apron_graphics.02` | Artwork set | — | — | Deferred: surface boundary | Resolve future tooling scope before selecting art outputs | [Brief](../../assets/d08_work_apron_graphics.md) |
| Yard entry marker · `d08_work_apron_graphics.03` | Artwork set | — | — | Deferred: surface boundary | Resolve future tooling scope before selecting art outputs | [Brief](../../assets/d08_work_apron_graphics.md) |

## 09 East Docks assets

| Asset and stable ID | Output type | Needed in | Unconfirmed uses | Stage | Next action | Brief |
| --- | --- | --- | --- | --- | --- | --- |
| Long ridge warehouse · `d09_warehouses.01` | Model design | 09 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d09_warehouses.md) |
| Wide low warehouse · `d09_warehouses.02` | Model design | 09 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d09_warehouses.md) |
| Loading-face annex · `d09_warehouses.03` | Component design | 09 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d09_warehouses.md) |
| Larger dock crane · `d09_cranes.01` | Model design | 09 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d09_cranes.md) |
| Smaller dock crane · `d09_cranes.02` | Model design | 09 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d09_cranes.md) |
| Long container · `d09_storage.01` | Model design | 09 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d09_storage.md) |
| Short container · `d09_storage.02` | Model design | 09 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d09_storage.md) |
| Low covered stack · `d09_storage.03` | Model design | 09 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d09_storage.md) |
| Simple crate group · `d09_storage.04` | Component set | 09 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d09_storage.md) |
| Warehouse fascia art · `d09_freight_graphics.01` | Artwork set | 09 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d09_freight_graphics.md) |
| Container ID panel · `d09_freight_graphics.02` | Artwork set | 09 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d09_freight_graphics.md) |
| Loading-location sign · `d09_freight_graphics.03` | Artwork set | 09 | — | Asset concept needed | Refine design from district asset breakdown | [Brief](../../assets/d09_freight_graphics.md) |

## Existing shared actor, vehicle, weapon and effects tracks

These existing tracks are citywide dependencies; placement/population by district
is not assigned. Their live progress and acceptance remain in the linked handoffs.
They are not new environment commissions and are not included in the entry counts above.

| Asset | District usage | Tracking status / next action | Brief or handoff |
| --- | --- | --- | --- |
| Player and shared humanoid rig | Citywide | Existing Coral Courier track; readiness stays in owner handoff | [Coral Courier](../../assets/player_character/README.md) · [Shared rig](../../assets/shared_humanoid_rig.md) |
| Civilian pedestrian | Citywide | Existing track; use owner handoff for readiness | [Civilian](../../assets/pedestrian_civilian_first.md) |
| Latch compact | Citywide | Existing track; use owner handoff for readiness | [Latch](../../assets/car_latch_a.md) |
| Crate hatch | Citywide | Existing track; use owner handoff for readiness | [Crate](../../assets/car_crate_a.md) |
| Sable sedan | Citywide | Existing track; use owner handoff for readiness | [Sable](../../assets/car_sable_a.md) |
| Bus | District distribution unassigned | Existing concept proposal; selection pending in owner record | [Larger vehicles](../assets-v1/vehicle/larger_vehicles.md) |
| Service truck | District distribution unassigned; workshop/dock use proposed | Existing concept proposal; selection pending in owner record | [Larger vehicles](../assets-v1/vehicle/larger_vehicles.md) |
| Pistol | Citywide player equipment | Existing track; use owner handoff for readiness | [Coral Stub](../../assets/pistol_coral_stub.md) |
| SMG | Citywide player equipment | Existing track; use owner handoff for readiness | [Wedgewire](../../assets/smg_wedgewire_a.md) |
| Rocket launcher | Citywide player equipment | Existing track; use owner handoff for readiness | [Dock Thumper](../../assets/rocket_launcher_dock_thumper.md) |
| Weapon effects | Citywide gameplay presentation | Existing track; use owner handoff for readiness | [Effects A](../../assets/weapon_effects_a.md) |
| Whole-city greybox | All nine | Layout reference; not finished environment art | [Greybox](../../assets/brackett_greybox.md) |

## Open decisions

- Refine individual building/module concepts and dimensions, including Terrace Ward
  joins, Glassward heights, the university/lighthouse and warehouse/crane parts.
- Resolve Signal Row's three bridge descents, Old Quay hall fit and the boardwalk
  terminals in Ironreach and Broadlot with closer concepts.
- Confirm the supporting district uses shown in the rows. Alternatives remain
  unselected; they are not extra required building designs.
- Resolve sidewalk, parking-asphalt and apron-artwork ownership with future surface
  tooling before selecting outputs. Road markings remain deferred.
- Assign actual placed quantities only after district arrangements and clearances
  are settled. Record existing actor/vehicle readiness in their linked handoffs.

## Maintenance rule

Update this file when an asset is added, removed, selected, reused in another district,
or advances to a newly authorized stage. Update its linked brief when its design
changes. District concept breakdowns are visual/reference snapshots, not competing
live status lists. The repository asset catalogue links here for environment demand;
the JSON family index remains a discovery index only and does not own tracking state.
