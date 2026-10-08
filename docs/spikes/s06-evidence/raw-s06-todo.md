- [ ] **S06 — Shared city topology, navigation and minimap.**
  Needs: [S01 pipeline evidence](docs/spikes/s01.md), [S02 actor/camera envelope](docs/spikes/s02.md),
  [reviewed S04 technical dimensions](docs/assets/s04_kit.md#measured-technical-geometry)
  and [accepted district brief](docs/world-layout.md).
  Ready for one bounded saved two-sector topology/turn/seam experiment after root
  assigns a direct Sol lead and exclusive new scene/source lease. Use explicit
  provisional actor/car/camera assumptions; the S04 one-second steering displacement
  is not a full turn radius or swept corridor. Measure both driving directions,
  legal turn, foot crossing and seam/minimap agreement with actual bodies. Final
  S04 dimensions/turning/exit and S02 feel/camera ratification remain open; record
  sensitivity and rerun affected clearances after those choices.
  Question: which authored representation supports lanes, sidewalks, seams and road-map drawing?
  Minimum: one intersection split across two saved sectors; one person takes a
  sidewalk/crossing route, one car makes a legal turn, and minimap roads align at
  the seam. Compare sidewalk graph/navmesh choices and lane graph/curves for cars.
  Validate stale derived data. Scene placement owns geometry/transforms; topology
  references it and owns connectivity, avoiding an independent layout writer.
  Decision: representation, stable IDs/layers, host AI/controller APIs and bake/update
  workflow. Specify bounded blockage/junction/stuck/wreck recovery for M1-C3.

