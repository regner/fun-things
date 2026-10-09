# Larger vehicle concepts — bus and dock/workshop truck

9 October 2026. Regner approved all three city cars, then requested:
“Can we add a larger bus, and a truck you might see in the docks or workshop area.”
Producer: vehicle lead Codex. Accepting owner: Regner. D/E art approval pending.

[Gallery](review.html) · [Exact prompts](expansion_prompts.json).

## D — Tandem city bus

A rigid single-deck urban bus, warm ivory roof, dark petrol body, broad coral band,
blunt front windshield and two curb-side passenger door sets. A shallow rear roof
vent enclosure and small forward emergency hatch help distinguish front/back from
the game camera. No articulated joint or passenger gameplay is proposed.

Provisional construction brief after visual self-review: W 2.50 × H 3.15 × L 12.0 m,
excluding mirrors from the width until source measurement; three axles, front steer
axle plus tandem rear group. A longer city workhorse with a quiet readable roof.
At the camera's frame centre, the nominal ground footprint is approximately
55 × 266 px; roof elevation enlarges the actual image. These are analytical estimates,
not measured pixels or Godot acceptance.

## E — Keel dock/workshop truck

A rigid cab-over dropside truck, broad orange cab, petrol bed sides and a pale empty
cargo deck. The empty open bed identifies its practical cargo role from above and
can accept later source-owned cargo variants if required. No crane, container trailer,
loading mechanics or cargo system is included. The current street plan already
reserves loading/apron space; this asset does not change those roads or placements.

Provisional construction brief after visual self-review: W 2.40 × H 2.90 × L 7.20 m,
excluding mirrors from the width until source measurement; three axles, front steer
axle plus tandem rear group. Nominal ground footprint approximately 53 × 160 px.
These dimensions are larger than every approved car; no S04 collider or handling
scale applies automatically. Dock/workshop turns, exits and parking remain integrator checks.

## Self-review and prompt departures

The generation prompts asked for two axles, 10.8 m bus length and 6.6 m truck length.
Both generated three-quarter views instead show a tandem rear group (three axles).
Rather than claiming the prompts were matched, the final proposal intentionally
retains the heavier silhouette with the larger provisional lengths above. Regner
can keep or revise this wheel arrangement at concept approval. The original prompts
remain verbatim; they are not overwritten with a fictitious successful specification.

Both sheets provide a clear complete three-quarter view, strict overhead view and
small auxiliary studies. Bus auxiliary views are mostly side/front/back; the truck
also includes an overhead study. They are line-and-window studies, not pure masks.
The bus passenger doors appear on the visible flank, so the generated camera-side
description is not reliable; source authoring will fix doors to local +X/right curb
side. Tire layout is incompletely represented in overhead views. The eventual source
must have one explicitly documented wheel hierarchy matching the accepted axle layout.

Bus ivory roof and truck orange cab/pale open deck carry strong small-scale color
blocks. They clearly differ from the short car roofs and from one another. Bus
windows, seats, wheel hubs and trim are more detailed than the desired chunky model;
simplify those while retaining primary masses. Truck bed rail/deck seams should also
be simplified. No visible brands, textual logos, weapons, people or external assets.
Enlarged illustrations are attractive references, not exact turnarounds, physical
dimensions or working bus doors. Saved Godot camera/lighting checks remain pending.

## Source and integration proposal

If accepted, IDs are `bus_tandem_a` and `truck_keel_a` in family `city_commercial`:
`art/source/models/city_commercial/<asset_id>.blend`, explicit
`art/models/city_commercial/<asset_id>.glb`, imported visual wrappers under
`scenes/prefabs/city_commercial/` and asset-local previews under
`scenes/previews/city_commercial/`. Keep independent sources/exports and material
ownership. Axle pivots, driver/entry/exit source markers follow existing axis/origin
contracts; no chassis simulation, cargo/passenger systems or new collision rules.
Final driver fit depends on player dimensions; passenger doors are visual only until
the integrator defines requirements. No generic humanoid rig binding is needed for
rigid vehicle parts.

Original prompt authorship by Codex vehicle lead from Regner's expanded brief.
Generated with built-in `image_gen.imagegen`; copied unchanged from this agent's
output directory. No external model/library or branded reference intentionally used.
Future models will be original Blender-authored geometry. PNG fingerprints are in
`checks.json`; this is an initial concept self-review, not production-completion audit.
