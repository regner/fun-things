# Stage 3 methods and provenance

9 October 2026 · Original project concept work, prepared in this session.

## Inputs

- [Approved cyberpunk island image](../stage-01-setting/15-long-island-cyberpunk.png)
  and its [generation provenance](../stage-01-setting/prompts-v4.json): the shared
  stylised 3D direction, ordinary architecture and cool/warm colour relationships.
- [Approved map A and district list](../stage-02-city-structure/README.md): district
  roles and relationships; no revised macro placement is proposed.
- [Selected M1 programme](../stage-02-city-structure/m1-candidate.md) and the
  [owner decision log](../decisions.md).
- [World concept handover](../../../workflows/world-concept-handover.md): Stage 3
  content requirements and gameplay constraints, as revised by recorded decisions.

## Every board

Boards `01-northpoint` through `09-east-docks`, each supplied as SVG and PNG, are
drawn by [draw_boards.py](draw_boards.py) from [briefs.json](briefs.json). The script
uses Python's standard library to write original vector artwork, then `rsvg-convert`
to render 1800 × 1320 PNGs. Run `python draw_boards.py` from this directory to rebuild.

Board `10-urban-scale.svg/.png` is also drawn by the same script, at 1800 × 1180.
Unlike the individually framed identity motifs, it compares three samples at one
shared scale: 520 pixels represent 180 m in every sample. Buildings, plot boundaries,
roads and fixed 4.2 × 1.8 m car symbols all follow that scale. Example road dimensions
are listed in [urban-scale.md](urban-scale.md); they are illustrative choices, not
approved engineering values or measurements extracted from the setting image.

The nine roof/open-space motifs are intentionally schematic identity illustrations:
simple coloured footprints, road curves, open courts, parking symbols and accent
bands. They are not an alternative 2D game-art direction, a measured local map, a
3D render, production placement, a complete traffic graph or an engine capture.
They do not establish scale, heights, turn radii, occlusion or camera readability.
District architecture remains the approved smooth stylised 3D direction.

No raster image generation or external art was used for this stage. No third-party
artwork, logos or licensed reference assets were imported. Text, sign suggestions
and illustrations are original project concepts; names and signs are provisional.
The boards use the locally available DejaVu Sans font for presentation.

## Review

Check all nine identity boards and the scale comparison for readable text, clipping, diagram overflow and
visually distinct roof/open-space motifs. Check SVG parsing, PNG dimensions and size,
gallery links and whitespace. Review against the accepted M1 scope, flat terrain,
camera constraints and shared population budget. No game/editor validation is implied.
