# Initial light batch — saved technical checkpoint

9 October 2026. Source/export delivered for city_lights.01 and .02. Integration
is partial; **neither row is READY**. No independent review has run. Whole-city
placement, gameplay/multiplayer clearance and device/performance acceptance remain pending.

Sources and producer reports/manifests are unchanged. Integration readback verified
complete expected sets and all byte counts/hashes: 32 files for .01 (including
observed importer sidecars), 20 producer files for .02; separate .02 GLB sidecars
are integrator-owned. Readback receipts are in integration-evidence/.

Godot 4.8-dev7 (official c971f93e7) imported both warm/cool variants. Four saved
prefabs under scenes/prefabs/environment/ keep Visuals/Model as identity-transform
GLB instances, without editable imported children or embedded render meshes.
Static pole bodies have one direct CylinderShape3D, layer1/mask0:

- city_lights_01 and _cool: radius0.21 m, height5.45 m, centreY2.725 m,
  adopting the source brief's conservative pole envelope; overhead arm/head decorative.
- city_lights_02 and _cool: radius0.135 m, height2.63 m, centreY1.315 m,
  conservative base-width envelope beneath the head. Canopy remains decorative.

These are authored collider proposals awaiting actual movement/query acceptance,
not proof of actor/car collision compatibility. Bounds measured through saved
PackedScene instances match source GLBs within0.001 m. .01 min(-.36,0,-1.40),
size(.72,6.20,1.61); .02 min(-.36,0,-.36), size(.72,3,.72).
Both warm/cool wrappers were saved, closed and reopened. .01 also resaved after reopen.
Source records and imported meshes remain linked; measured ancestry and tree outputs
are retained in light01/light02-results.jsonl. No production runtime script is attached.

## Private editor and tools

Private process PID178546, project
/home/regner/.paseo/worktrees/0u71f39f/asset-register-production, engine path
/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot.
Editor/runtime/LSP CLI pins22650/22651/22652; XDG directories scoped under
/tmp/asset-register-production-editor. Registry path, PID cwd/cmdline and authenticated
editor context verified this project. Registry reports LSP6005 because addon publishing
does not see --lsp-port; no LSP operation was used. Do not trust that published LSP port.
No shared editor, connector configuration or unrelated project was mutated.

The provided connector could not reach6550. Private toolkit transport is
`tools/asset_production/integration/editor_client.mjs`, with process/project guards
and token-path readback; tokens are never retained in Git. Toolkit scene.instantiate
rejects .glb paths. An editor-only inspector bridge was therefore authored through
script.write/edit and called through node.call_method to create the linked model and
collider children. Temporary author script is detached before prefab save. Authored
hierarchies live in saved scenes; the bridge is not production runtime composition.

Context/bridge preparation requests and results, including two corrected parameter
mistakes and the inaccessible-singleton expression failure, are retained. Bootstrap
malformed JSON and manifest list/dict parsing failures made no asset mutation. The
corrected commands then succeeded; no failed check is reclassified as passed.

## Actual camera observation and diagnostics

Saved tests/fixtures/asset_production/lights_camera.tscn inherits the existing
player-character preview, reuses its Blender-sourced ground/Coral Courier and lights,
selects its existing vertical47 m/42deg north-up perspective GameCamera, and adds four
saved light instances at X=-2,-5,+2,+5 m. Actual Forward+ NVIDIA GTX1070 Vulkan capture
is integration-evidence/lights_gameplay.png, viewport1280x800; initial capture retained.
The central actor remains visible between poles. Pole heads cast long shadows and
warm/cool appearance is subtle in the overhead view. This small inspection fixture
is not full district readability/aim/occlusion or repeated-population cost acceptance.

Runtime started via the private editor; toolkit bridge reported runtime_ready:false,
then private22651 authenticated and viewport capture returnedOK. The game was stopped.
Final context reports no unsaved scenes. Full editor log and final runtime diagnostics
are retained without filtering. New saved-prefab UID references still warn "invalid
UID ... using text path instead" at runtime, including after targeted refresh. Text
paths resolve and draw, but UID/cache registration is **an unresolved integration
gate**. Next concrete integration step: diagnose/cache-register the four saved
prefab UIDs through pinned editor/import, reopen/resave affected inherited fixture,
and rerun capture/log check; do not regenerate identities to hide the warning.

Addon authentication emits Invalid call. Nonexistent 'int' constructor at
addons/godot_mcp_toolkit/core/unfocused_sleep_controller.gd:111. This vendor diagnostic
is retained and not modified/suppressed. Engine/plugin version warning (4.8 versus
latest tested4.7) and ordinary auto-created-directory warnings remain classified.

Remaining: UID warning resolution; .02 second-save byte/identity roundtrip and
inherited-variant checks as applicable; actual collision/query/movement checks;
review imported normals/materials and readable fixed-camera comparison; repeat-cost
observation; clean-context independent art-review of frozen exact candidate; concrete
fix/recheck. Hardware/whole-city gates stay open. No TODO was closed.

## Safe resume

Editor is left running with inspector.tscn active and saved, runtime stopped, no
integration writers active. Verify live launch.json PID/cwd/cmdline before reuse:
`node tools/asset_production/integration/editor_client.mjs /tmp/asset-register-production-editor/context-requests.json`.
Requests/results are retained under integration-evidence; fresh writes use the private
endpoint, no global connector reconfiguration. Source workers remain independent.
ROOT now owns queue/dispatch; integrator idles until a concrete batch assignment.
