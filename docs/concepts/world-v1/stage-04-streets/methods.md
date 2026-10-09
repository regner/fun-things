# Stage 4A methods and provenance

9 October 2026 · Original project concept drawing; prepared in this session.

## Sources

- [Approved macro map A](../stage-02-city-structure/01-neighbourhood-loops.svg) and
  its [source script](../stage-02-city-structure/draw_maps.py): reused coastline,
  harbour shape and broad route anchors. Its district territories remain historical.
- [Owner-exported district boundaries](district-editor/brackett-districts.json):
  the current Stage 4 colour polygons, preserved exactly as supplied on 9 October.
- [Approved district briefs](../stage-03-district-identities/README.md) and
  [urban-scale refinement](../stage-03-district-identities/urban-scale.md).
- [S06](../../../spikes/s06.md) and its
  [topology contract](../../../spikes/s06-contracts.md): technical constraints and
  limits of current evidence, not a source of approved new road dimensions.

## Images

| Files (SVG and PNG) | Method |
| --- | --- |
| `01-city-road-block-plan` | Original vector road/block plan, 2400 × 1500; 1.5 pixels per metre in the main map |
| `02-city-without-zone-colours` | Identical map geometry and framing with district colours removed; visual structure comparison, not a minimap |
| `04-downtown-grid` | 460 × 230 m detail of the revised downtown, on an 1800 × 1250 board |
| `03-same-scale-extracts` | Three 220 × 220 m crops of that same map at 710 pixels per crop, on a 2400 × 1250 board |

Run `python draw_plan.py` in this directory to regenerate all four pairs and
`drawing-check.json`. It uses Python's standard library and `rsvg-convert`.
No generated raster art or external artwork was used. The diagrams and labels are
original project work, with the locally available DejaVu Sans presentation font.
Names remain placeholders.

## What the drawing does

The script imports the prior macro drawing's constants without running its renderer.
Road anchors are explicitly listed for this proposal. Local endpoints project onto
existing centre lines to avoid accidental drawing gaps. The downtown revision uses explicit straight segments for the orthogonal grid;
other curves are sampled into short segments. Intersections split an undirected drawing graph; planar face walks
identify bounded street-enclosed spaces for subtle shading.

This face calculation is not a directed lane graph or a planner. It does not encode
lane directions, legal turns, crosswalks, priorities, obstruction recovery or traffic
population. The face areas are **centre-line areas**, including road share and, for
some faces, harbour water. The report therefore is not a net developable-area or
production block-count measurement. Open coastal strips are not counted as bounded
centre-line faces.

Roof and plot symbols are sparse diagram examples with different footprint ranges
per original district territory. Their geometry is deliberately held fixed while
the owner redraws district boundaries; symbols are not a new zoning allocation.
A deterministic scan places examples away from road and foot-link
strokes and water; it is not a procedural game city, asset generator or final parcel
layout. Dock motifs rotate along the working shoreline. Symbol quantity has no
production or population meaning. Empty space is not a commitment to leave a block
empty. Final saved placement remains later Godot/Blender work under the repository
asset contracts.

The harbour water is drawn over the land; the bridge is drawn back above its open
entrance. No approach slope is implied. All ordinary intersections are at grade.
Lane counts use the agreed exploratory hierarchy; exact widths are provisional
values listed in the stage README. Double/coloured centre lines are diagram keys,
not painted lane-marking specifications.

## Review limits

Rendering and drawing-topology checks are appropriate for this city-plan draft.
They do not validate continuous swept clearances, full corridors near the coast,
traffic, car turns, gameplay-camera visibility, minimap readability or performance.
The SVGs are reference drawings and have no production scene/resource identities.

The polygon editor embeds the regenerated neutral map and the same owner-exported
JSON. Run `python district-editor/generate_map.py` after regenerating the boards.
Its autosave key includes the source revision, so an old browser draft cannot
silently override newly supplied boundaries; previous autosaves remain in storage.
