# Signal Row building and prop breakdown

This is the proposed unique asset set for [concept revision 03](06-signal-row-v03.png),
within Signal Row's selected boundary and including its bridge landing in Old Quay.
The concept can be built from **five building designs and one pedestrian-bridge
assembly**, with reusable storefront fittings and street props. Repeated placements,
different tenants and different colours do not each require another building model.

Each item below links to its owning brief. These are concept requirements and design
proposals, not a modelling commission. Exact dimensions and placed quantities remain
to be settled. “Visible” means the form is identifiable in the image; it does not
mean its small details or construction are resolved.

## Buildings

| Ref | Unique design | Where it appears and what distinguishes it | Reuse and brief |
| --- | --- | --- | --- |
| B01 | Rounded entertainment hall | Main northern area, beside the plaza. Round/oval mass, low broad roof, luminous magenta ring, distinct entrance. | District landmark. [Hall shell, roof ring and canopy](../../assets/d06_entertainment_hall.md). |
| B02 | Long multi-store shopping parade | Southern strip. One continuous roof and structure, multiple tenant entrances and signs, bridge forecourt at its north end. | District building. [Continuous shell and storefront bays](../../assets/d06_southern_shopping_parade.md). Six bays are illustrative, not a selected tenant count. |
| B03 | Compact square shop | Smaller nearly square buildings around the northern block and south of the hall. Short frontage and compact roof. | Shared shell `city_small_shop_shells.04`; [brief](../../assets/city_small_shop_shells.md). Repeated with different fittings and artwork. |
| B04 | Wide rectangular shop or short shop row | Broad roofs along the northern edge and east/southeast of the hall. Can contain one wide tenant or several small storefronts. | Shared shell `city_small_shop_shells.02`; [brief](../../assets/city_small_shop_shells.md). Tenant divisions do not change the shell identity. |
| B05 | Narrow deep shop | Slim rectangular buildings along the eastern edge, with a small street frontage and deeper roof. | Shared shell `city_small_shop_shells.01`; [brief](../../assets/city_small_shop_shells.md). Rotation and facade placement provide variants. |

For B03–B05, use a small number of low-rise height/facade variants with shared
windows, parapet treatment and roof details. We do not need a separate bespoke
building for every rectangle in the image. Final height variants need a closer
building study; this overhead image does not reliably establish storey counts.

The earlier `d06_shopfront_blocks` and `d06_mixed_use_infill` families are broader
exploration briefs. They are not additional requirements from this rendering.
L-shaped shops, chamfered blocks, rear-court shells and stepped upper-floor blocks
remain options for later refinement rather than automatic additions to this list.

## Pedestrian bridge

| Ref | Unique assembly | Required parts | Reuse and brief |
| --- | --- | --- | --- |
| X01 | Three-way pedestrian bridge | Central junction deck; north, south and west spans; three ground-access stair/landing arrangements; railings; supports; restrained edge-light trim. | One bespoke connection shared by Signal Row and Old Quay. [Bridge brief](../../assets/d06_harbour_footbridge.md). Reuse railing, stair and support designs where geometry permits. |

All three ends must connect to ground: main-area walking space, southern shopping
forecourt and Old Quay on land. The northern descent remains unclear in the image
and needs its own detail concept. Supports and landing footprints must avoid road
lanes and pedestrian entrances. This is an elevated pedestrian structure, not the
separate existing harbour-mouth road bridge or a rooftop walkway.

## Reusable building fittings

These form part of the buildings' appearance but can be designed once and reused.
Roof parapets and ordinary wall/roof surfaces belong to the shells; they are not
separate freestanding prop commissions.

| Ref | Item | Brief and treatment |
| --- | --- | --- |
| F01 | Horizontal fascia / illuminated sign box | [Shop fittings](../../assets/city_shop_fittings.md), `.02`. Shared frame; shop-specific colour and artwork. Clearly visible across the frontages. |
| F02 | Projecting vertical sign / blade sign | [Shop fittings](../../assets/city_shop_fittings.md), `.08`. Reusable bracket and sign body. The side-facing bright panels suggest this form; exact projection needs a close study. |
| F03 | Glazed shop entrance and frame | [Shop fittings](../../assets/city_shop_fittings.md), `.03` and `.06`. One combined entrance assembly; single/double-width variants as needed. Doors are implicit in the store brief, not individually countable overhead. |
| F04 | Shop display-window bay | [Shop fittings](../../assets/city_shop_fittings.md), `.05`. Repeated glazing/frame unit; no detailed interior commissioned. |
| F05 | Upper-floor window group | [Shop fittings](../../assets/city_shop_fittings.md), `.07`. Broad grouped windows for the taller-looking shop variants; verify in building elevations. |
| F06 | Short shop canopy / awning | [Shop fittings](../../assets/city_shop_fittings.md), `.01`. One restrained form with width/colour variants, used selectively. |
| F07 | Flat wall poster / sign frame | [Sign supports](../../assets/city_sign_supports.md), `.01`. Generic frame, district artwork; avoid a new mesh for every poster. |
| F08 | Low rooftop vent | [Roof details](../../assets/city_roof_details.md), `.01`. Small, quiet rooftop fitting repeated on the shops. Exact mechanical type is a design interpretation. |
| F09 | Box-shaped rooftop plant / air-conditioning enclosure | [Roof details](../../assets/city_roof_details.md), `.02`. The larger raised roof boxes; a simple recognisable form, not detailed machinery. |

The hall's luminous roof ring and entrance canopy are already included in B01.
Bridge railings, stairs, support columns and light strips are already included in
X01. They must not be counted again as additional structures or prop families.

## Visible street props and planting

| Ref | Unique item | Location / appearance | Owning brief |
| --- | --- | --- | --- |
| P01 | Cylindrical poster drum | Beside the main plaza and northern bridge approach; round cap, illuminated advertising wrap. | [Signal Row poster drum](../../assets/d06_poster_drum.md). District-specific feature. |
| P02 | Street light pole | Repeated at road and pavement edges; slim dark pole with a warm lamp. | [Shared lights](../../assets/city_lights.md), `.01`. |
| P03 | Short pedestrian light | Smaller warm lights along walking areas and shop approaches. Exact fixture style is not resolved. | [Shared lights](../../assets/city_lights.md), `.02`. |
| P04 | Facade / entrance light | Warm frontage accents separate from the coloured fascia signs. | [Shared lights](../../assets/city_lights.md), `.04`. Light fitting, not a new building. |
| P05 | Street tree | Repeated at the plaza, pavements and southern strip. | [Shared planting](../../assets/city_planting.md), `.04`. Propose two crown variants within this design to avoid obvious repetition. |
| P06 | Low shrub cluster | Low green masses at building edges and in planted spaces. | [Shared planting](../../assets/city_planting.md), `.03`. |
| P07 | Rectangular planter | Linear planting at frontages and path edges; exact pot edges are small in the image. | [Shared planting](../../assets/city_planting.md), `.01`. |
| P08 | Round planter / tree surround | Planted circular bases in open pedestrian areas. | [Shared planting](../../assets/city_planting.md), `.02`. Reuse the container with different planting. |

Trees, shrubs and containers are separate reusable designs; a tree in a planter
does not become another unique tree asset. Placement should be sparser than the
rendering where foliage competes with entrances or bridge access.

## Supporting props to confirm

These belong to the established district brief or ordinary shop servicing, but are
too small or obscured to identify confidently in v03. Keep them separate from the
visible extraction rather than treating every dot in the image as a new asset.

| Ref | Proposed item | Purpose and brief |
| --- | --- | --- |
| S01 | Straight bench | Plaza/forecourt seating; [shared seating](../../assets/city_seating.md), `.01`. |
| S02 | Short low plaza seat | Alternative seating shape beside the hall; [shared seating](../../assets/city_seating.md), `.02`. May be unnecessary if the bench covers the selected design. |
| S03 | Public litter bin | Shop and plaza approaches; [shared waste](../../assets/city_waste.md), `.01`. No separate bin per district. |
| S04 | Short bollard | Selected pedestrian edges, with bridge approaches kept clear; [shared barriers](../../assets/city_barriers.md), `.01`. |
| S05 | Low wayfinding panel | Main plaza / bridge destination directions; [shared sign supports](../../assets/city_sign_supports.md), `.02`. |
| S06 | Utility cabinet | A small service-edge detail; [shared service furniture](../../assets/city_service_furniture.md), `.01`. |
| S07 | Closed service door and frame | Rear/side access on shop shells; [shared service furniture](../../assets/city_service_furniture.md), `.03`. Static appearance only. |
| S08 | Closed shop shutter | Optional storefront state; [shared shop fittings](../../assets/city_shop_fittings.md), `.04`. No opening animation requested. |

These supporting items are not a request to populate every available pavement space.
No bus stop, trolley shelter, bicycle, traffic-signal system, cafe table/chair set,
fountain or statue is required by this extraction.

## Graphics and materials

| Set | Required variation | Brief |
| --- | --- | --- |
| Tenant fascia artwork | Several fictional businesses, reused across the small shops and southern parade; colour, lettering and graphic shapes vary. | [Commercial graphics](../../assets/d06_commercial_graphics.md), `.02`. Final tenant/variant count remains open. |
| Entertainment-hall identity | One recognisable destination graphic, with the roof ring carrying its large-scale identity. | [Commercial graphics](../../assets/d06_commercial_graphics.md), `.01`. |
| Poster wraps | Alternate advertising artwork on the same cylindrical support. | [Commercial graphics](../../assets/d06_commercial_graphics.md), `.03`. |
| Pedestrian wayfinding | Main area, southern shops and harbour-area directions; final district names remain placeholders. | [Commercial graphics](../../assets/d06_commercial_graphics.md), `.04`, on shared supports. |

Quiet slate/blue roofs, muted shop walls, dark frames/glazing, warm window treatment,
selective cyan/magenta sign emission and bridge deck/rail materials belong to the
relevant asset briefs. They are not additional buildings. Sidewalk/plaza finishes
remain shared environment design context; road surfaces are excluded for future
automatic tooling, and painted road markings are not modelled props in this list.

## Existing assets and neighbouring context

Reuse the existing player, pedestrian and vehicle tracks linked in the
[city register](asset-register.md#existing-shared-actor-vehicle-weapon-and-effects-tracks).
Cars and people in the image establish activity/scale; they do not commission new designs.

Glassward towers above the boundary, Broadlot's large buildings to the right/bottom,
Old Quay's buildings and waterfront to the left, and the sea are neighbouring
context. Their assets will be identified during those districts' reviews. Only the
west bridge landing and its immediate pedestrian connection need cross-district
coordination in Signal Row's current asset set.

## Review status

Regner accepted this breakdown as the starting point. The
[central asset tracker](asset-register.md) now owns live district demand and progress.
This file remains the visual breakdown of v03; supporting items retain their
explicit need for confirmation.


The five-shell grouping is a proposed economical interpretation of v03, not proof
that every illustrated building is identical to a selected reusable design. Before
asset concept sheets, settle B03–B05 silhouettes and confirm the supporting props.
The image does not establish quantities, dimensions, mechanical details or actual
camera/clearance acceptance. No modelling or implementation is part of this breakdown.
