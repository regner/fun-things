# Stage 2 map provenance and reproduction

All three diagrams are original in-project vector illustrations. No image-generation
tool, external map, external artwork or licensed visual reference was used in this stage.

- Author: Codex, this session, 9 October 2026.
- Source: [draw_maps.py](draw_maps.py), Python standard library only.
- Rendering: installed `rsvg-convert` (librsvg); SVG and 1800×1200 PNG retained.
- Reference: approved [Brackett setting](../stage-01-setting/15-long-island-cyberpunk.png),
  [owner decisions](../decisions.md), [world brief](../../../world-layout.md),
  [S07 scale record](../../../spikes/s07-environment-scale.md) and
  [handover](../../../workflows/world-concept-handover.md).
- District names, outline, route anchors, candidate locations and annotations are
  original proposed design decisions. Colours are diagram keys, not art swatches.

| SVG and PNG stem | Method |
| --- | --- |
| 01-neighbourhood-loops | Shared island outline; linked local circuits and central mixed-use candidate |
| 02-harbour-heart | Shared outline; deeper harbour and central meeting junction, western candidate |
| 03-bent-spine | Shared outline; a bending cross-city route with secondary circuits, eastern candidate |

The script stores explicit map anchors and styling. A weighted planar partition lays
out the coloured district cells, clipped to the common island outline; those cells
are diagram boundaries only. Roads use smooth curves through explicit junction
anchors. The harbour is drawn as a water cut reaching the sea, with a separate bridge.
M1 lots and envelope use the existing reference dimensions; roads under that overlay
remain schematic. One map unit represents one provisional metre.

Run from the repository root:

```sh
python docs/concepts/world-v1/stage-02-city-structure/draw_maps.py
```

This is intentional procedural **2D concept drawing**, not a procedural city system,
runtime placement writer, Godot resource generator or visible production 3D mesh.
The SVG files are editable source deliverables; changes should be made in the script
and regenerated if reproducibility is to be retained.

Validation performed: all three PNGs visually inspected; lettering, legends, candidate
highlights and bridge/open-water relationship reviewed. A collision between option C's
district marker and candidate label was corrected. Sources parsed as XML, image
dimensions/size checked, and gallery/document links checked. No gameplay claims follow.

