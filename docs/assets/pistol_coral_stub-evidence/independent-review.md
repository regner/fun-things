# Independent Coral Stub static asset review

9 October 2026. Reviewer: clean-context independent Codex, Sol 6.1 medium;
read-only technical/art inspection and nonspatial verification. Producer: pistol
workstream identified in the handoff. No implementation changes or commits.

**Disposition: accepted for the scoped reusable static visual asset handoff.**
No actionable P0–P3 findings were observed within the coverage below. This accepts
the delivered source/export, materials, sockets, saved wrapper and local previews.
It does not accept production-player hand fit or combined game integration.

## Revision and scope

- Candidate/verified HEAD: `b8363f55a6cfe8ab6cf02b1458a3d193629de59b`.
- Base/verified merge base: `c030d66d7d0a9db19c0c2aebf1aa2b83eded6275`.
- Candidate parent: `117316a1ab182bcc13f59dfaa3f24c2fd72271ec`; the nominated
  base is an ancestor, not the immediate parent. Four commits comprise the scoped
  concept/contract/asset/routing change. Initial working tree was clean.
- Authoritative selection: Regner explicitly chose A, “Lets go with concept A.”
  Inspected the raw `docs/concepts/assets-v1/pistol/01_coral_stub.png`, original
  prompt/provenance and the selected asset handoff rather than accepting its verdict.
- Read AGENTS, parallel-art-production workflow, art-review skill, applicable asset
  and scene contracts, art direction/world layout, S01 import/inheritance limits,
  catalogue, current TODO and validation envelope/development instructions.
- Reviewed new pistol source/export/import, wrapper/environment/two previews,
  fixture, editor bridge/reexport/manifest and provenance/evidence. Shared planning,
  gameplay, existing S02 assets and main launch configuration are unchanged.
  Reverse consumers of the pistol wrapper are the two local previews; its linked
  model has only the reusable wrapper as a saved scene consumer.

## Independently verified evidence

| Check | Result and evidence |
| --- | --- |
| Actual source and exact exporter | Fresh read-only Blender process loaded the committed `.blend`: 5.2.2 LTS, build `d13f752e3b9c`, installed glTF exporter 5.2.40. Metric scale 1; 12 meshes and 2 empties in `export_pistol_coral_stub`; positive unit scales, applied rotations, no remaining modifiers/object animation, libraries or images. `independent-source.log`. |
| Source/export freshness | Ran committed `reexport.py`, after reading it, against the original source; exported only to scratch. Delivered GLB and scratch export are byte-identical. All seven handoff fingerprints match actual files. `independent-blender-freshness.log`, `independent-glb.json`. Bootstrap `author.py` was not run; source was not saved. |
| Geometry, materials and axes | Independent GLB accessor inspection: 2,424 triangles, 1,384 finite unit normals, valid indices, no external buffer URI. Six named opaque PBR materials match source slots and documented roughness/metallic/base colors; no texture, skin, animation, camera or extension payload. Collection/GLB names match manifest. Source muzzle `(0,0.421,0.122)` converts once to Godot `(0,0.122,-0.421)`; origin grip and identity orientation agree. Aperture source bounds show 0.048 m diameter on the declared front plane. `independent-source.log`, `independent-integrity.log`, `independent-glb.json`. |
| Fresh isolated Godot profile | Godot `4.8.dev7.official.c971f93e7`, new scratch project/cache/private XDG state, only pistol and unchanged S02 actor/ground dependencies. Development/Steam plugins and autoloads excluded. Unused 16780–16784 range checked; no toolkit listener enabled. Import metadata, saved scene/resource bytes and `.uid` sidecars preserved. `independent-import.log`, `independent-import-final.log`, `independent-persisted.log`. |
| Delivered focused fixture | Ran `tests/fixtures/pistol_coral_stub/check_asset.gd`, exit 0, failures 0. Loaded production-facing wrapper; linked import, unit transforms, sockets and camera checks pass. Bounds min `(-0.075,-0.205,-0.421)`, max `(0.075,0.204,0.143)` m; size `(0.150,0.409,0.564)` m. `independent-fixture.log`. |
| Independent saved-resource inspection | Wrapper `Visuals/Model` remains noneditable linked GLB, import UID `uid://b76txaphm8oqg`, wrapper UID `uid://d074bk5ladf6v`. `Sockets/Grip`/`Sockets/Muzzle` are saved markers; no corrective root/model transforms. No generated/copied render meshes, detached geometry, collision, gameplay scripts, animation or particles in owned scenes. No UID collision among repository-owned nonignored resources (220 identities inspected). `independent-integrity.log`. |
| Owned GDScript checks | Explicit `--check-only` compilation of fixture and editor-only bridge both exit 0. Pinned gdstyle 0.3.0 format/check and lint both pass on those two scripts. Manual purpose comments/type hints/function spacing inspected. `independent-compile-*.log`, `independent-format.log`, `independent-lint.log`. |
| Existing editor roundtrip receipts | Read actual `editor-prefab.jsonl`, `editor-previews.jsonl`, `editor-refresh-final.jsonl`: linked instantiation/socket relay, bridge detachment, saved wrapper, close/reopen and post-export refresh/reopen/save of all three scenes. Receipt tree agrees with saved hierarchy and fresh instantiated fixture. These are producer receipts, not a reviewer-controlled GUI roundtrip; no live editor was touched. |

## Visual judgment and limits

Inspected retained full-resolution `close.png` and `game_camera.png`, plus capture
receipts/runtime logs and actual saved camera transforms. Close view carries the
selected concept's coral softened rectangular upper, cream rear block, petrol
lower/angled dark grip, open trigger guard and blunt dark muzzle. The simplified
surface detail is consistent with restrained broad forms; no observed discrepancy
requires reopening the selected direction.

The native 1280×800 capture uses vertical-down, fixed-yaw perspective, 47 m/42°,
near/far 0.1/160 m. Three static S02 mannequin poses expose the coral upper in
north/east/south orientations. The weapon occupies approximately a dozen pixels;
cream rear and pale hand are difficult to separate. This supplies limited local
appearance evidence, not recognition/aim-motion or production-player fit acceptance.
The provisional mount is explicitly documented. No geometry/pose adjustment is
recommended from this fixture alone. Captures use neutral lighting and Compatibility
OpenGL on GTX1070, not final city lighting or a production rig. Images were reviewed,
not recaptured; source/export freshness and receipt agreement were checked separately.

The fixture checks the model subtree and selected root/socket conditions; it is
not a comprehensive gameplay or all-script validator. Independent scene/GLB/source
inspection supplies the omitted whole-wrapper/content checks. Finite normals and
positive transforms do not certify every surface winding or future culling/LOD
transition. No inherited pistol variants exist. No fresh GUI save/reopen was performed
by this reviewer, and clean import does not synchronize the producer's live editor.

## Diagnostics and remaining acceptance

All final focused checks exit 0. Blender export prints the known optional unavailable
MeshOptimizer library diagnostic; no compression extension is delivered, and exact
export comparison succeeds. The first scratch import also exited 0 but logged a
missing original main scene omitted from this deliberately small profile. Correcting
only the scratch project's main-scene setting to the owned preview produced an
import with no Godot error/warning diagnostics. Initial log retained; this was an
environment/profile error, not an asset defect. The prelaunch sandbox socket denial,
ignored historical evidence UID probe correction and unavailable optional PIL are
recorded in `independent-check-notes.log`. No diagnostics were broadly suppressed.
Vendor `unfocused_sleep_controller.gd:111` is present in producer receipts; plugins
were excluded here, so this review neither reproduces nor repairs that vendor issue.

| Handoff/system | Status and owner/next bounded check |
| --- | --- |
| Selected concept | Accepted by Regner; independently inspected reference/provenance hashes and PNG dimensions. |
| Static source/export/materials/import/wrapper/local preview | Accepted for this production static visual delivery, with the explicit evidence limits above. No actionable fix requested. |
| Production hand/grip/support-hand and moving aim | Pending player-owned rig/pose integration; fit the actual selected player and inspect held north/east/south views plus moving aim before accepting fit. Spatial changes require Astra. |
| City lighting/readability/occlusion | Pending external integrator; matched production camera/renderer/lighting captures with actual player and backgrounds. |
| Firing/damage/ammo, authoritative queries/network/collision | Not applicable to this static visual assignment; downstream acceptance remains pending with external gameplay integrator. No firing or duplicate VFX implementation was found. |
| Weapon effects integration | Pending effects owner; use supplied muzzle transform/aperture to check flash placement/clearance and visibility. |
| Rigs/clips/textures | Not applicable to the selected static prop/flat-material brief; no competing humanoid rig is authored. |
| LOD/performance/device/full-project compatibility | Pending relevant integration/performance owner; no measured optimization need or sustained performance claim. Asset-profile checks do not certify plugins, packaging, Windows/Deck, networking or the whole project. |
| Catalogue/TODO reconciliation | Deferred to shared-file owner per parallel assignment; handoff includes actionable deltas. No shared planning edits made. |

Reproduction commands and scratch probe source are retained in
`independent-probes.log`; version/command/exit evidence is in the `independent-`
logs above. Only this review and independent evidence were written in the worktree.
Candidate implementation files remain unchanged; no agents/worktrees were created,
no live MCP session/state was touched, and no process was terminated or commit made.
