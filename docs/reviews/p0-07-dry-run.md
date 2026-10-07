**Verdict: rejected for the candidate’s technical S01 prefab/placement handoff.** Two observed contract violations block that scope. The isolated asset import succeeds, but resource acceptance fails. This is not a production-art, S02 gameplay, or P0-07 implementation review.

**P1 — Restore the static collider’s specified envelope and ground datum.**

- **Location:** candidate `tests/fixtures/s01/static_prefab.tscn:7` (`BoxShape3D_fv7hq.size`) and `:21` (`StaticPrefab/Collision/Body/Shape.transform`). Inherited consumers: `static_variant.tscn:6`; `roundtrip.tscn:16`, `:20`, `:24` (StaticA, StaticB, Variant).
- **Observation:** serialized size is `(4,1,1)` and shape translation is `(0,1.5,0)`. The fresh-process query resolves that same enabled shape, directly parented to StaticBody3D, in both standalone wrappers and all three placed static consumers. In prefab coordinates its bounds are min `(-2,1,-0.5)`, max `(2,2,0.5)`. The imported Body remains min `(-1,0,-0.5)`, max `(1,1,0.5)`. The GLB and Blender source are byte-identical to the base. This is a wrapper collision change, not an exported geometry change.
- **Violated contract:** `docs/assets/s01_static.md:51–54` specifies a 2×1×1 m box at `(0,0.5,0)`; `docs/assets.md`, “Collision envelopes, bounds and LOD,” requires deliberate solid regions and ground contact. The permitted decorative front/ruler overhang is not a reason to enlarge or lift this collider.
- **Impact/inference:** the saved collision occupies the wrong volume: doubled width and a lower face 1 m above ground, with no positive-volume overlap with the body’s vertical interior. It invalidates the fixture’s solid-envelope proof and propagates through inheritance. Bounds establish the discrepancy; no actor pass-through, vehicle snag, clearance, or multiplayer outcome was exercised or claimed.
- **Fix owner/minimal correction:** Codex in the prefab-integrator role should restore size `(2,1,1)` and translation `(0,0.5,0)` through the pinned editor, preserving shape/node/resource identities. No source re-export or material change is warranted by this defect.
- **Retest:** fresh load must give collider bounds `(-1,0,-0.5)` to `(1,1,0.5)` in the base and variant; inspect all three placed static consumers. Rerun the resource check, then perform the authorized editor save/close/reopen roundtrip for affected wrappers and placement, comparing IDs and transforms. Actual movement/query/network acceptance belongs to downstream gameplay integration.
- **Evidence/reproduction:** `base-candidate.diff`, `independent_query.log` from `query.gd`, and `resource_check.log`. The unchanged checker reports `deliberate static collision envelope` and `collision ground datum` failures.

**P1 — Preserve StaticB’s distinct authored world ID.**

- **Location:** candidate `tests/fixtures/s01/roundtrip.tscn:22`, node `Roundtrip/StaticB`, property `world_id`; duplicates StaticA’s value at `:18`.
- **Observation:** both instances serialize and load `s01/roundtrip/statica`. The base gives StaticB `s01/roundtrip/staticb`. The five placed fixtures therefore have only four distinct world IDs. Their instance transforms and editor node IDs are unchanged; distinct node IDs do not repair a duplicate authored world ID.
- **Violated contract:** `docs/scene-structure.md:111–122`, “Authored identity and topology,” requires distinct placed identities and preservation through asset changes. S01’s fixture contract specifies five distinct StringName IDs (`docs/spikes/s01.md:115`); the unchanged checker independently asserts StaticB’s expected value and uniqueness at `check_s01.gd:55–58`.
- **Impact/inference:** the fixture no longer proves stable unique placement identity. A future consumer indexing these records by world ID could alias the two instances, but no such gameplay consumer or network failure was demonstrated here.
- **Fix owner/minimal correction:** Codex in the fixture/world-integrator role should restore StaticB’s existing `s01/roundtrip/staticb` value, preserving its transform, node identity and scene UID. Do not mint a new identity or change StaticA.
- **Retest:** load all five fixtures and assert their exact saved IDs plus uniqueness; rerun the resource checker and editor save/close/reopen identity comparison. No topology/navigation bake exists in this fixture to refresh.
- **Evidence/reproduction:** `base-candidate.diff`, `independent_query.log`, and `resource_check.log`, which reports both `StaticB authored world_id` and `StaticB distinct world_id` failures. These are two assertions of one identity defect, not two separate findings.

**Scope and evidence identity.** Reviewed 7 October 2026 by this Codex reviewer, independently of candidate production. Candidate producer identity was not independently supplied; the S01 contracts name Codex as the source/integration owner, which is the role assignment used above. Historical acceptance statements in the required S01 documents were treated as context, not carried forward as candidate acceptance.

Base: `7626f66f34d54f07446a1c8afd8fc6005e69c22d`. Candidate: `/tmp/p0-07-review-irdbxx5x/project`, an uncommitted asset-profile copy, identified by all 33 supplied-file hashes in `candidate-before.json`. Primary SHA-256 values:

| Candidate file | SHA-256 |
| --- | --- |
| `tests/fixtures/s01/static_prefab.tscn` | `c9a60ae924c6c38faf3e5c7e43abb8c04c115d7e6f1d59aa2cd718d2e0c600fa` |
| `tests/fixtures/s01/static_variant.tscn` | See complete inventory; byte-identical to base |
| `tests/fixtures/s01/roundtrip.tscn` | `93985059e52bd710c0387bdd1b14a8da27b01a529d81dd84ace730e8efe78995` |

Comparing each supplied file directly with its Git blob found only the two scene changes above and the expected removal of autoload/editor-plugin sections from `project.godot`. Both sources, GLBs, import sidecars, materials, textures, scripts and variant are unchanged from base. The user restored the omitted root icon and import sidecar before import; both match base. `raw_inventory.log` retains the initial 31-file inventory; `raw_inventory_corrected.log` and `candidate-before.json` identify the corrected 33-file input. Missing full-project content is an explicit profile boundary, not a handoff defect.

Guidance read: repository AGENTS.md; the requested art-review skill; assets, scene structure, static/rig handoffs, art direction, world layout, catalogue, S01 and development documents; the design validation envelope and relevant TODO gates; Mise and relevant check/export/import tooling. Contract readbacks are retained in `contracts_*.log`. No prohibited fixture generator, manifest, supplied patch, P0-07 review/evidence records, or separate producer conclusions were opened. No shared Godot/Blender tools, orange-baboon resources, Blender operations, scene saves, or subagents were used.

**Dependency and technical coverage.** Raw files and engine-resolved dependencies agree on these chains:

- StaticA/StaticB → static prefab; Variant → inherited static variant → static prefab → `Visuals/Model` → `s01_static.glb` and sidecar → mapped `s01_static.blend` / `export_s01_static`.
- RigA/RigB → rig prefab → `Visuals/Model` → `s01_rig.glb` and sidecar → mapped `s01_rig.blend` / `export_s01_rig`.
- Both imports’ `body_paint` → external petrol material → runtime palette, with byte-identical editable palette source. The variant stores coral material on the wrapper root; presentation applies it to that instance’s Body without changing the shared imported mesh material.

Reverse consumers were searched in the candidate’s art/tests/tools (`consumers.log`). Source files have supported compressed Blender headers and an empty source `.gdignore`; source/output/tool bytes match base. GLB JSON was decoded independently and retained as `s01_static.glb.json` and `s01_rig.glb.json`: generator declares Blender glTF I/O 5.2.40, internal buffers, no images/textures/compression extensions, expected static members and four rig clips. These facts corroborate mapping, not current Blender collection contents, library completeness, authorship, or reproducible export freshness. The briefs declare original project-owned authorship; no external asset dependency was found in the inspected runtime graph. Blender-side validation remains unperformed.

The completed resource check has exactly the four assertions listed above as failures; its other assertions reported none. Coverage includes static bounds, normalized normals, axes/socket basis, 8×8 texture and material settings, linked/shared meshes, wrapper material isolation, two-bone skin/attachment, clip names/durations/loop seams, sampled socket movement and death-pose retention. The independent query additionally prints actual collider bounds, parentage, default fixture layer/mask `1/1`, resolved material paths, and all 12 dependency edges with registered UIDs matching fallback paths. No detached/copied owned render meshes or direct editable imported-child override was found. These are headless resource/presentation observations, not graphical or gameplay acceptance.

**Checks actually run.** All evidence paths below are relative to `/tmp/p0-07-review-irdbxx5x/reviewer`. Each execution has a matching `*.command.json` recording exact argv, cwd, private XDG paths, deadline, elapsed time, exit code and timeout state; `run.py` retains stdout/stderr and bounds the child process group.

| Check / raw log | Deadline | Result |
| --- | --- | --- |
| `godot_version.log` | 10 s | Exit 0; `4.8.dev7.official.c971f93e7` from the user-specified binary |
| `import_sandbox.log` | 60 s | Exit 0 **but environment-failed**: socket/listen errors plus secondary rich-text image diagnostics; not a clean import |
| `import_escalated.log` | 60 s | Approved escalation, fresh cache, exit 0, no warning/error diagnostics; all four assets imported |
| `source_links.log` | 15 s | Exit 0; existing static source/export, external-file, unique resource UID and no copied-mesh checks pass |
| `resource_check.log` | 30 s | Godot exit 1; completed with `failures=4`, mapping to the two findings |
| `independent_query.log` | 30 s | Exit 0, `QUERY_COMPLETE`, no diagnostics; direct base/variant/placement and dependency observations |
| `compile_identity.log`, `compile_check.log`, `compile_editor_probe.log` | 30 s each | Explicit check-only compilation of all three supplied owned scripts; exits 0, no diagnostics |
| `final_audit.log` / `final_audit.json` | 10 s | All 33 supplied files unchanged; no additions outside candidate `.godot` |

The failed sandbox cache was moved to `reviewer/sandbox-import-cache` before the escalated import, so the successful attempt did not reuse it. Both attempts used private `xdg-data`, `xdg-config`, and `xdg-cache` under the reviewer directory. The outer logging wrapper returns normally even for a failed child; the recorded Godot exit 1 is the resource-check result. No timeout occurred. No diagnostic suppression was used.

No formatter/linter was needed for unchanged candidate scripts. The mutation-based `s01:clean` harness and Blender re-export command were inspected but not run: they exceed this review’s no-fixes/no-Blender scope. Equivalent relevant source checks, isolated import, direct resource checks and explicit compilation were run without those mutations.

**Handoff disposition, technical fixture only.**

| Stage | Status | Basis / outstanding owner and next check |
| --- | --- | --- |
| Brief | accepted | Neutral asymmetric metre/socket/material fixture has explicit dimensions, tolerance and bounded purpose. No production building or person requirements imposed. |
| Concept | accepted, neutral specification only | Simple body/front/ruler and rig proof fit the documented technical intent. No rendered style or production palette acceptance. |
| Blender blockout | pending | Imported resource measurements are satisfactory apart from the separately authored collider. Source owner must verify source collections/transforms/dependencies and reproducible export when Blender operations are authorized. |
| Production asset | not applicable | Neither fixture is submitted as finished art or a production humanoid rig. |
| Export/import | pending overall; isolated import accepted | Linked exports, UIDs and clean asset-profile import verified. Source freshness and existing-editor evidence were not independently rerun; source owner/integrator owns those bounded checks. No stale export was observed. |
| Prefab | rejected | Collider violates the explicit fixture envelope. Correct it, rerun resources, and perform the pinned-editor base/inherited save/reopen check. |
| Placement | rejected | Duplicate authored ID is observed; inherited collider is also wrong. Restore identity, correct upstream collider and verify all consumers. Further dependent acceptance remains pending. |

Camera/readability evidence is **pending** for S02/S04: the query records a perspective reference at height 47 m, FOV 50°, near 0.05 m, far 100 m and vertical orientation, but it is not the current camera and no graphical capture was made. The saved overview is current. Neither camera configuration nor concept imagery proves native 1280×800 readability, tower occlusion, aiming, motion or target separation. Production art refinement remains M1-C1 work.

Actual movement, query, vehicle clearance, routes and multiplayer evidence remain **pending** with S02/S04/S06 and the network owners when these assets enter gameplay. No production movement APIs exist in this supplied profile. Rig animation resource checks do not certify a production shared-person rig or animated culling bounds. VFX/overdraw, audio, production sockets, normal/ORM maps, transparent layering, derived navigation/minimap data and LOD transitions are **not applicable** to these neutral assets because those systems are absent; per-asset automatic LOD is disabled as documented, not a performance defect. Rendered material contrast, culling/load cost and sustained Deck LCD/OLED 60 FPS remain **pending** with S02/S07/S08 and production owners. No arbitrary triangle/texture budget, gameplay/device result, or full-project plugin/export compatibility is inferred.

The reviewer changed no supplied candidate files or repository files. Import generated only the authorized candidate cache; queries, commands, results and this report are retained in the reviewer directory. Fixes and subsequent authoring roundtrips remain with the named integration roles.
