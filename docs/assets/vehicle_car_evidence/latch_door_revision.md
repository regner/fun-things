# Latch: shorter front doors and fixed rear quarters

9 October 2026. Owner requested: “The orange car needs more work. The door shouldn't
go all the way to the back of the car. Compare to the concept image.”
Vehicle lead authored this revision with verified runtime Astra/high, following
checkpoint documentation commit `f6374662c2b717f7787d5ca038761f30d401ef14`.

The [approved sheet](../../concepts/assets-v1/vehicle/01_latch_compact.png) shows a
front door ending ahead of the rear wheel, with fixed rear-quarter body and glazing.
The first model incorrectly carried almost the whole cabin side with each door.
Both sides now split at Blender Y=-0.62 m (Godot Z=+0.62 m):

- Moving panel longitudinal span reduced from 1.932 m to 1.245 m.
- `QuarterPanelLeft/Right` and `QuarterGlassLeft/Right` remain fixed under the car
  root. The shortened panel and window retain their existing hinge parents.
- Fixed dark pillars align with the new split; door handles move forward with the
  shortened panel. Existing hinges, wheel parts, sockets and animation targets keep
  their names and transforms. No collision/handling/seat change.

Authorship recipe: `tools/vehicle_assets/shorten_latch_doors.py`. This one-time
source edit clips and caps the preserved panels/glass, reassigns the fixed halves,
then saves the `.blend` and exports the GLB together. No generated runtime mesh.
The previous Blender save backup is preserved in worktree-private temporary state.

## Checked result

- Viewed the concept alongside new closed/open Godot renders; shorter front doors
  leave rear quarters in place. [Closed](car_latch_a_inspection.png),
  [open](car_latch_a_doors.png), [native game camera](car_latch_a_game.png).
- Exact private editor PID72501/project/ports verified; no unsaved scenes before
  refresh. Closed affected tabs, refreshed, reopened, saved and reopened both Latch
  scenes through editor MCP. Wrapper and preview bytes/UIDs remain unchanged;
  [receipt](latch-door-refresh.jsonl), existing hashes in `roundtrip.json`.
- Source/GLB collection membership and source re-export passed; output byte-identical
  to the new committed GLB. Updated hashes in `reexport.json`.
- Godot-imported bounds still match source within 0.002 m; five socket poses agree;
  all meshes remain linked to the GLB. Updated `import_checks.json`.
- Independent GLB hierarchy inspection confirms all four rear-quarter parts have
  the fixed car root as parent; front panel/window/handle parts retain their hinges.
  See `latch-door-parent-check.json` and source split bounds in the source record.
- Three new 1280×800 Compatibility captures exited 0, with successful saves,
  fixed root and expected 0°/50° hinge poses, capped at 60 FPS/VSync. Logs contain
  no new runtime/script errors. Closed whole-car envelope is unchanged;
  source triangle count is now 10,480.

This is a focused correction, not final model acceptance. Rounded concept forms,
upper door-edge shading, full-loop/intermediate clearances and renderer/gameplay
acceptance remain open. The earlier independent review applies to immutable
`69219f0`; it does not certify this later source revision.
