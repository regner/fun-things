# Independent production review — Off-Shift Worker

9 October 2026. Reviewer: clean-context `pedestrian_production_review`,
GPT-6.1-Sol/high. Applied project `art-review` skill. Producer: pedestrian lead,
Astra/high. Review base `03b0177`; initial candidate
`d0a03dda62e29a10078c56b682d81d8ae001e06a`; accepted implementation
`723ef39cac4bf193497dd6a4c07f7bc826d8dff5`.

**Verdict: scoped production asset handoff accepted; no unresolved findings.**
This review does not accept gameplay/network/crowd/device performance or replace
Regner's final art judgement. No repository files or other agents' editor/process
state were changed by the reviewer. The lead copied these review receipts afterwards.

## Finding and verified correction

Initial candidate's exported `palette` lacked a setter. In an independent
editor-mode probe (`Engine.is_editor_hint() == true`), Inspector-style assignment
stored magenta but left the jacket shader uniform amber. Calling `apply_palette`
worked. The lead added a validated setter shared with the runtime API; the same
independent probe against `723ef39` then updated the uniform immediately. See
`editor-candidate-probe.log` and `editor-fixed-probe.log`. No geometry, skeleton,
animation or GLB changed in that correction.

## Checks actually performed

- Opened saved source with pinned Blender 5.2.2 LTS. All 28 full rest matrices and
  parents match the canonical contract exactly. Root/object transforms are identity.
  All 7,360 vertices have valid named normalized weights; maximum two influences,
  maximum weight-sum error `2.98e-8`.
- Sampled every source animation frame. All four clips preserve the complete root
  transform; idle/walk/run endpoints match exactly. Animated bounds reproduce the
  retained source measurements. Freshly exporting both declared collections yields
  byte-identical GLBs. See `blender_probe.json` and `reexport.log`.
- Independently parsed GLB: 28 joints/binds, one surface, 9,030 exported vertices,
  four clips, nine palette regions, finite vertices, normalized exported weights
  and normals, no images/extensions. Maximum inverse-bind reconstruction error
  `6.49e-7`. See `glb_probe.json`.
- Private clean import completed without error/warning diagnostics on the pinned
  Godot using isolated ports. Native Forward+/GTX1070 checks passed at 1280×800:
  shared mesh/material, isolated recolouring, invalid-palette rejection, clip policy,
  endpoints and retained death pose. Imported rest-origin error `2.30e-7 m`.
  See `import-final.log` and `native-fixed-check.log`.
- Independent Godot probe sampled 61 positions per clip: root and wrapper remain
  fixed; tracks address presentation bones only. See `independent_probe.log`.
- Checked exact production resources/scenes against the immutable candidate;
  imported-model ancestry, unchanged GLB import UIDs, saved node identities and
  wrapper-level variants are preserved. Inspected save/close/reopen receipts.
  No inherited asset variant was commissioned. See `candidate_identity.json`.
- Inspected concept C, retained and independently rendered game-camera/overview
  images, and motion-recording samples. Cap, amber/cobalt blocks, broad silhouette
  and empty hands fit the accepted simplified worker direction. No substantive
  visual discrepancy found. Pinned gdstyle passes both runtime/preview scripts.

The editor-mode probe has known dummy-editor shutdown RID diagnostics; native checks
are clean. Initial sandbox socket failures and an incorrect debugger connection
argument were probe/environment setup failures followed by the retained clean import.

Collision, stride versus simulation speed, gameplay transitions, network lifecycle,
integrated city/player readability, crowd load, packaged builds and target-device
performance remain for external integration. Weapons/sockets, spawning/AI and world
placement are not applicable to this commissioned asset-only handoff.
