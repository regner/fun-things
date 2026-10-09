# District polygon editor

Open [index.html](index.html) directly in a modern browser. No server, installation,
build, or network connection is needed. The concept gallery also links here.

Select a numbered district, drag its round vertices, and double-click an edge to
insert a point on that edge. **Add point** inserts a corner at your click after the
nearest edge. Select a vertex and use **Delete selected point** or the Delete key;
a polygon must retain at least three points. Coordinate fields provide precise
placement. Use the wheel or buttons to zoom; choose **Pan map** or hold Space while
dragging to pan. Undo/Redo covers geometry changes, imports, and resets.

Edits autosave in browser storage when available. File URL storage support and
scope vary by browser, so use **Export JSON** to keep a portable copy and **Import
JSON** to restore it. Import requires the nine original numeric IDs and placeholder
names. No existing approved map or generator data is modified by editing.

Polygons are independent, with no automatic shared-edge, topology or tessellation
constraints: overlaps, gaps and self-intersections are possible. Fills are masked
at the island coast and harbour; exported points retain the complete edited
polygon. The supplied owner-drawn boundaries are the current starting point. Reset
restores that revision, rather than the earlier macro-map polygons.

## Export convention

JSON version 1 contains a `coordinates` object and nine `districts`, each with
stable discussion `id` (1–9), placeholder `name`, and an ordered `points` array of
`[x, y]` pairs. The polygon closes implicitly from last point to first. Coordinates
use concept-map metres, X right/east and Y down/south, with the origin at the upper
left of the original 1260 × 720 map frame. No Godot world transform is implied.
The mask is for display only and is not baked into the exported polygons.

## Map provenance

`generate_map.py` embeds the actual saved map group from
`../02-city-without-zone-colours.svg`, preserving its road, plot, coast, harbour
and M1 geometry. Fixed district badges are removed so labels follow edited
polygons. Current district points come from `brackett-districts.json`; the island
outline comes from `../../stage-02-city-structure/draw_maps.py`. Browser autosaves
are scoped to the supplied file's revision so an older draft cannot replace it.
The generated `map-data.js` is loaded
as a local script to avoid file URL fetch restrictions. Regenerate after an
intentional source-map update with:

```sh
python docs/concepts/world-v1/stage-04-streets/district-editor/generate_map.py
```

This is a planning interface; it does not validate gameplay or author production
world data.
