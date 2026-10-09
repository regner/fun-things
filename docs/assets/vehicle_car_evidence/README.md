# Three-car production checkpoint evidence

9 October 2026. [Rendered review gallery](index.html). Separate handoffs:
[Latch](../car_latch_a.md), [Crate](../car_crate_a.md), [Sable](../car_sable_a.md).
Base before production: `9ff045f9c9ed14075a855bc9e0dc0266fc6936a8`.
This is a reviewable first source/import/preview checkpoint, not final art acceptance.

## Actual checks

- Four pinned Blender sources → explicit GLBs, repeated from saved sources into
  private scratch: byte-identical; hashes in `reexport.json`.
- Godot-imported mesh ancestry remains `.glb::` linked. Source/import bounds agree
  within0.002m and all five stable wrapper sockets agree with source markers:
  `import_checks.json` and source records.
- All six wrappers/previews were authored and saved through private Godot MCP.
  After source refresh, close/reopen/save normalized initial redundant imported-node
  type/resource serialization. A second close/reopen/save cycle is byte-identical:
  `roundtrip.json`; full method receipts in `stable-roundtrip.jsonl`.
- Both new GDScripts passed editor `script.write` diagnostics, pinned gdstyle0.3.0
  lint with zero warnings and `fmt --check`. Function comments/tabs/spacing checked.
  No claim of unrelated all-project compilation.
- Nine standalone captures exit0, draw1280×800, and report actual camera/renderer,
  maxFPS60, closed/open visual bounds and hinge-angle/root checks. Corresponding
  `*.stdout.log` records contain no new script/runtime errors. Camera height47m,
  vertical FOV42°, north-up; inspection camera separately saved.
- Original S04 source/body/collider/handling consumers, main, project settings and
  shared planning/catalogue/TODO files are outside this change.

## Diagnostics and limits

Initial authoring used an incorrect assumed imported root path (`Model/Markers`);
actual import nests the named car under Model. That caused partial authoring returns.
Paths were corrected, missing markers/animations repaired through the editor, and
all imported/socket checks rerun successfully. Do not treat early method `success`
alone as validation; Godot logged script errors inside those callbacks.

The addon logs a Godot4.8 compatibility warning and `unfocused_sleep_controller.gd`
`int` conversion error on some MCP connects. Its editor-playtest bridge reported
runtime readiness false and progress-dialog diagnostics. No vendor addon was changed.
Private standalone CLI previews supplied the actual draw evidence instead.
A camera-variable scope error introduced during capture-script cleanup was caught
by editor diagnostics and fixed; final compile, lint and all nine captures passed.

The first background Blender operation completed source/export saving but emitted
an audio wakeup permission message while leaving its shell session alive. Its saved
work was preserved; no process was killed. Subsequent own Blender processes used
`-noaudio` and completed with exit0. Prior Blender save backups and the editor's
auto-generated worktree `.mcp.json` were preserved under private state rather than
committed as asset deliverables.

Private editor PID72501 was verified against the exact worktree and owned sockets
21650/21652/21653/21654; bounded runtime previews used21651. Launch receipt is
`private_editor_launch.json`. XDG state is `/tmp/brackett-vehicle-production`.
MCP authentication tokens are not committed. Other workspaces' services were untouched.

Mechanical clips are cosmetic preview demonstrations. No actual enter/exit animation,
controller, collision, route/seat clearance, multiplayer, damage/wreck, main-renderer
Forward+ parity or target performance has been accepted. Current art remains visibly
simplified; further shape/surface polish and owner model review remain open.
