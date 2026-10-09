# City asset registry review

9 October 2026. Review of the current nine district concepts, detailed breakdowns,
62 family briefs and central registry. The inventory covers the current concept
scope; individual designs, sizes and placed quantities still need refinement.
[The registry](asset-register.md) remains the single owner of demand and progress.
This is a dated review receipt, not another live tracker.

## Completeness findings resolved

- **Old Quay demand was incomplete.** Its existing detailed breakdown listed the
  hall, frontage buildings, bridge, quay edges, fittings, props and appearance
  studies, but most were still candidates in the registry. Required demand now
  follows that breakdown; uncertain noticeboard/utility details stay to confirm.
- **East Docks lacked its detailed asset pass.** Added the warehouse/annex, crane,
  cargo, graphics and shared working-waterfront breakdown. The liked concept now
  has required district uses and explicit supporting decisions. Boardwalk demand
  remains excluded as requested.
- **Shared appearance studies had missing users.** Open-sea appearance now has
  one record for all coastal districts; basin appearance belongs to Old Quay.
  Residential garden finishes, Signal Row plaza paving and Broadlot's reused sign
  support are reconciled with their district uses.
- **The player handoff link was missing.** The registry now links the existing
  Coral Courier owner record alongside the shared rig contract. Readiness stays
  with that handoff; the environment review does not accept its production work.
- **Scope/status notes had become stale.** Removed the instruction to review the
  other eight districts, reconciled current boardwalk users and explicitly deferred
  road markings, walkway output, parking asphalt and apron artwork at the future
  surface-tooling boundary.

## Overlap and ownership decisions

| Potential overlap | Recorded ownership |
| --- | --- |
| Parking sign versus low freestanding sign | city_parking_furniture.02 is an assembly reference to city_sign_supports.02; district graphics own copy |
| Landward low rail and end posts versus quay/boardwalk rail | city_barriers.02/.04 reuse city_quay_furniture.02; one shared rail/terminal kit |
| Older Signal Row shop row versus generic wide shop | d06_shopfront_blocks.01 is an unselected assembly reference to city_small_shop_shells.02 with shared fittings |
| Apartment compositions versus apartment modules | d03_apartment_family.01–.04 are assembly references using .05–.11; no four extra bespoke building meshes |
| Nested trolleys versus single trolley | d07_trolley_shelter.03 arranges .02; no second trolley design |
| Southern parade storefront interface versus shop fittings | Parade .02 defines openings/mounts; city_shop_fittings owns reusable attachments |
| Commercial fascia versus civic wall panel | Different support forms; use one appropriate body per graphic face, not two stacked frames |
| Building doors versus loose service doors | Integral kit entrances stay with the kit; shared service door attachments cover generic rear access once |
| Boardwalk versus shore, pontoons and bridge | Deck, shore face, floating marina kit and raised connection retain distinct owners and interfaces |
| Pedestrian bollard versus mooring bollard/cleat | Distinct uses and silhouettes; mooring fittings do not duplicate street barriers |
| Ground appearances versus district paving motifs | Shared materials own base appearance; district artwork owns overlays; no duplicate floor models |
| Industrial warehouses versus repair sheds | Shared broad wall/roof vocabulary may be reused, but different massing and loading frontage remain distinct |
| Recolours and worn finishes versus new models | Variants belong to existing designs; colour/wear alone does not add geometry |

Output types are explicit in every registry row. Stable IDs are retained, including
useful assembly/interface references. There are no duplicate registry IDs or
untracked declared brief members. Retaining a reference does not commission another
unique model. Similar unselected building studies remain alternatives until closer
concepts establish a distinct requirement or show they can reuse an existing kit.

## Coverage and remaining decisions

All nine district concepts have a detailed asset breakdown. Required records link
to named members in briefs. Shared actors, vehicles, weapons and effects link to
their existing owner records and stay outside environment counts.

The remaining work is individual asset concept refinement: modular joins, exact
sizes, bridge landings, boardwalk terminals, crane/vehicle clearances, final artwork
variants and supporting prop decisions. The registry does not claim these are
measured or production-ready. Existing greybox placements are context rather than
asset quantities. No new art direction, modelling or implementation was performed.

## Validation

Registry checks cover unique IDs, exact brief-member coverage, output types,
district-demand consistency, deferred scope, reuse references, local links/anchors,
JSON parsing and retained concept hashes. The exact selected boundary hash and all
nine districts' saved greybox translations are unchanged. Current counts and
check results are retained in [checks.json](checks.json).

Runtime, import, collision, animation, camera and performance checks are not
applicable to this documentation-only inventory review. The art-review workflow
was used for concept, ownership and brief evidence; production acceptance remains
with each separately commissioned handoff.
