# Independent Dock Thumper technical and asset audit

9 October 2026. Read-only candidate audit by independent Codex reviewer, authorized Sol 6.1 high technical-review scope. No modeling, animation, geometry, pose, gameplay or worktree implementation was performed. All inspector scripts, exports, editor saves and captures were confined to this unique /tmp directory. No subagents were launched or polled.

## Findings

No P0, P1 or P2 findings. Two P3 findings remain. These are minor corrections, not evidence of broken rendering, gameplay authority, imported ancestry or attachment frames.

### F1 — P3: collapsed faces survive source, GLB export and Godot import

**Path/objects:** `art/source/models/rocket_launcher/dock_thumper_a.blend`: launcher collection `RearRecess`; rocket collection `ExhaustRecess` and `RocketIvoryBand`. Affected outputs: `art/models/rocket_launcher/dock_thumper_launcher_a.glb` and `dock_thumper_rocket_a.glb`. Historical bootstrap locations are `author_dock_thumper.py:142`, `:178`, `:191`; the saved blend, rather than that bootstrap, is authoritative.

**Observed evidence:** read-only Blender bmesh face-area inspection finds 64 zero-area faces in each of these three objects. Independent raw GLB POSITION/index decoding confirms exactly 64 zero-area triangles per object: 192 exported triangles contribute no surface. Imported Godot surface-array inspection still finds 64 on RearRecess, 64 on ExhaustRecess and 128 on RocketIvoryBand (256 total; import compression also collapses additional band triangles). Retained evidence: `source-inspection.json`, `gltf-inspection.json`, `project/independent_mesh_checks.json`, `source-inspection-final.log`, `mesh-check-final.log`; reproducible inspectors are `inspect_blender.py`, `inspect_glb.py` and `project/tools/independent_mesh_checks.gd`.

**Impact/contract:** minor source geometry/triangulation quality issue under the asset workflow's source/export/normals inspection. These triangles have no valid geometric face normal and add avoidable indexed geometry. Stored/imported vertex normals remain finite and unit length, and no visible artifact was observed in the reviewed captures. This does not establish a measurable performance regression or justify a new triangle budget.

**Fix owner/minimal correction:** producer's Astra modeling owner should remove the collapsed faces or adjust the affected thin bevel geometry in the authoritative blend, preserving silhouettes, bounds, pivots, materials and sockets, and reexport the affected outputs together. Do not repair imported cache meshes or regenerate the asset from its historical recipe. Preserve import/resource UIDs.

**Retest:** fresh source-to-export comparison; raw/exported and imported triangle-area check; existing source/socket/AABB tests and native detail/game-camera views. The source zero-area check is **rejected** for these objects; all other independently measured source contracts passed.

### F2 — P3: stage serialization does not reproduce the claimed final byte-identical roundtrip

**Path/line:** `tests/fixtures/rocket_launcher/stage.tscn:9`; evidence claim `docs/assets/rocket_launcher_dock_thumper.md:147`, `:152`, and `docs/assets/rocket_launcher_evidence/editor_roundtrip.json`.

**Observed evidence:** starting from candidate bytes, pinned Godot editor save/reload/save removes the redundant `type="Node3D"` from imported `Visuals/Model`. Candidate SHA256 is `d90858f921f84609ef0449435f0718b1c7ea4ca29722c30f5b0c0b47e147c21f`; saved SHA256 is `71fb7038906c5709d65c81ccf5e0830254ef24bed81c69615ced3167d0999219`. The result repeats in a rendered editor, so it is not caused by headless thumbnail errors. `stage.tscn.diff` contains the sole change. Root/resource UID, dependency UID, node IDs, transforms and imported ancestry are preserved. Launcher and rocket wrappers and preview are byte-identical through this same check. A subsequent stage roundtrip is stable.

**Impact/contract:** evidence overstates candidate roundtrip stability and leaves routine first-save normalization for the next editor user. This is bookkeeping/serialization noise, not an identity or visual failure. The committed fingerprint itself matches the file; the claim about saving it is what fails reproduction.

**Fix owner/minimal correction:** producer's nonspatial Godot owner should save the stage through the private editor and commit its normalized serialization with refreshed roundtrip hashes/evidence; alternatively narrow the claim explicitly to the two launcher/rocket wrappers and record stage normalization as outstanding. Verify the actual candidate presented for handoff.

**Retest:** start from final committed stage bytes, save/reload/save and compare bytes and IDs. Evidence: `editor-roundtrip-final.log`, `editor-roundtrip-graphical.log`, `stage.tscn.diff`. The byte-identical-stage claim is **rejected**; its linkage and identity preservation are **accepted**.

## Immutable scope and identity

- Base: `504486494f5ce21e9ffa5e58eed4373f8ba7d286`.
- Candidate: `0be3af33d6c9cab30cffca1aed748875b9a36373`.
- Requested branch/worktree: `art/brackett-rocket-launcher`, `/home/regner/.paseo/worktrees/0u71f39f/brackett-rocket-launcher`.
- Producer: Codex rocket-launcher lead, Paseo `29438b4a-4815-4a68-8614-5d0a704809f2`.
- Review stage: committed static launcher/rocket production-asset technical handoff and saved asset-local preview; no integrated or equipped acceptance.

The candidate was archived by exact Git revision to `snapshot/`; the final audit fingerprints all 46 changed paths against that snapshot. All 46 candidate files remained unchanged, HEAD stayed pinned, and Git status remained empty. `diff.log` enumerates every changed path; `final-identity.json` supplies per-path SHA256s. No worktree creation, candidate edits, shared planning edits, main-scene changes, commits, pushes or remote operations occurred.

Read AGENTS.md, the art-review skill, parallel-art-production workflow, asset and scene contracts, accepted art direction/world layout, catalogue, S01 workflow, relevant development/Mise validation guidance, TODO/design camera envelope, concept README/gallery/prompt record, source recipe/manifest/export tools, all new wrappers/preview/scripts/import metadata, all producer evidence logs/JSONs and native captures. Reverse consumer search found only the asset-local preview and focused tooling. Existing S02 held-launcher and S15 rocket/trail remain separate technical fixtures; neither was changed. No production humanoid rig contract is present in the candidate.

## Independently supported observations

**Provenance/freshness:** original geometry is committed in `dock_thumper_a.blend`, under existing `art/source/.gdignore`. Blender reads Metric/unit scale 1; no linked libraries, external images, armatures or actions. Declared collections and source manifest membership, materials, measured bounds and triangle counts match the actual source. All static rotations are applied and scales positive unit. Fresh host reexport completes normally and all three GLBs compare byte-for-byte to candidate outputs. Blender 5.2.2 LTS build `d13f752e3b9c`, exporter generator 5.2.40; pinned Godot `4.8.dev7.official.c971f93e7`. Producer's authorship/model-routing receipts are documentary claims, not an independently witnessed modeling session. No external incorporated asset/dependency was found.

**Ancestry/metadata:** launcher/rocket wrappers link `Visuals/Model` to their explicit GLBs; stage similarly links its Blender export. Saved preview instantiates the wrappers four times at authored headings plus the rocket and stage. No embedded/generated authored visible Godot mesh or gameplay collision is introduced. Nine saved external UID dependencies resolve to their committed definitions without duplicate definitions; new script UID sidecars and GLB import sidecars agree. Unit imported roots and source-derived socket parity pass. No inherited variant is added, so inherited-variant migration testing is not applicable; repeated-instance ancestry and save/reload were checked. First clean import preserves all 15 candidate runtime files; later review-only stage normalization is accounted for separately.

**Frames/contacts:** Blender +Y/+Z maps to Godot -Z/+Y once. Grip pivot is origin. Wrapper/source socket positions match the documented WeaponMount (0,0,0), Muzzle (0,.3,-.905), SupportHand (0,-.0825,-.43), Shoulder (0,.085,.28), Trail (0,0,.23), with identity weapon-frame bases. BVH nearest-surface checks independently locate SupportHand at SupportIvoryBase's bottom centre (error 7.45e-9 m), Shoulder at ShoulderPad's bottom centre (zero error); both stored normals are Blender (0,0,-1), hence Godot (0,-1,0), separate from marker frames. Rocket exhaust is behind along local +Z; trail is 5 mm beyond the .225 m rear rim. These are surface/pivot contracts, not hand-bone poses or proof of fit.

**Geometry/materials:** source counts are launcher 8,268, rocket 3,842, stage 752 triangles, including F1's degenerates. Imported AABBs reproduce launcher min (-.203,-.0825,-.900), size (.406,.585,1.430), rocket min (-.064095,-.105819,-.225), size (.184095,.211638,.450). Three-fin asymmetry is documented and present. Imported source material names/slots match six flat PBR definitions; opaque materials, finite unit normals, no material overrides/external textures, skins or clips. Blender and GLB PBR factors are consistent. Materials import double-sided; no culling or performance acceptance is inferred. Open crown surface and nose rear boundary are not treated as watertight-collision requirements. Default generated LODs/shadow meshes are recorded; no new source LOD or triangle budget is required.

**Visual judgment:** approved A reference, committed native PNGs and freshly rendered native PNGs were inspected. The production realization retains the long petrol tube, broad pale crown, coral muzzle collar, restrained cyan accent and matching coral-nosed ivory-finned rocket. Simplified concept microdetail is permitted by the handoff. At vertically downward north-up 47 m/42 degrees, near .1/far160, native1280x800, the isolated four launcher headings preserve distinct muzzle/crown contrast. Projected AABB reproduces launcher10.63947x33.00540 px and rocket4.709656x10.76892 px; those are projected bounds, not an assertion that every pixel is filled. Rocket remains tiny; trail readability and equipped silhouette remain pending. Renderer/API/device: Forward+/Vulkan1.4.312/GTX1070/X11. Screenshot output was direct from the viewport without image edits. Detail captures have minor pixel differences from committed images; camera, geometry and broad appearance reproduce. No city-lighting, motion, head/hand occlusion, device, load or feel pass is claimed.

## Checks, exits and diagnostics

Exact commands, start times, process IDs, durations and exits are in `commands.jsonl`; a readable command table is in `commands.md`. Logs are retained beside this report.

| Actual check | Exit/result | Evidence/diagnostics |
| --- | --- | --- |
| Exact revision archive/initial/final identity | 0; candidate unchanged | `identity.json`, `final-identity.json`, `diff.log` |
| Host Blender fresh reexport and comparison | 0 / 0; three outputs identical | `reexport-host.log`, `freshness-host.log`, `fresh-host/`; optional MeshOptimizer library absence is an existing exporter diagnostic, not required by these uncompressed exports |
| Independent source measurements | 2; discovers F1, remaining tests pass | `source-inspection-final.log`, `source-inspection.json`; deliberate final zero-area assertion fails |
| Independent raw GLB inspection | 0; reproduces F1 | `glb-inspection.log`, `gltf-inspection.json`, `inspect_glb.py` |
| Truly fresh plugin-free isolated import | 0; no warnings/errors | `clean-import-final.log`, `clean-final/`; all 15 runtime files remain identical |
| Candidate focused headless assertions | 0; PASS | `clean-check-final.log`, `clean-final/docs/assets/rocket_launcher_evidence/imported_checks.json` |
| Explicit compile of both candidate scripts | 0 / 0; no diagnostics | `compile-preview.log`, `compile-capture.log` |
| Pinned gdstyle0.3.0 | 0; two files, no issues | `style.log`; manual purpose/spacing/scope inspection also performed |
| Native graphical assertions/three captures | 0; PASS | `capture.log`, `project/docs/assets/rocket_launcher_evidence/*.png` and `imported_checks.json` |
| Independent imported surface normals/materials/triangles | 0; finite unit normals and opaque materials; F1 reproduced | `mesh-check-final.log`, `project/independent_mesh_checks.json` |
| Rendered private editor save/reload/save | 0; completed, stage bytes differ | `editor-roundtrip-final.log`, `stage.tscn.diff`; PASS means probe completed, not that every before/after hash matched |
| Git diff whitespace check | 2; extra EOF blank line in retained producer log | `diff-check.log`; `clean-import-verified.log:65`, cosmetic diagnostic only |

Historical attempts are retained, not called passes: sandbox Blender export wrote identical outputs then stalled during restricted audio teardown and timed out124; sandbox Godot import returned0 but logged socket creation errors. A permitted owned host reexport and a fresh plugin-free host import replaced those acceptance attempts. Initial reviewer source helper returned0 despite an Euler AttributeError; it was corrected, rerun with `--python-exit-code2`, and produced the complete measured report/F1. Initial reviewer mesh helper timed out124 after assuming backface culling was required; that assumption was removed because double-sided opaque materials are permitted, and the final helper passes. Headless editor save emitted dummy-renderer thumbnail null-texture errors and the initial strict byte-equality assertion stopped at F2, leading to its45-second timeout; rendered editor repeats F2 with no thumbnail diagnostics. These are explicitly distinguished from candidate script or asset failures.

## Ownership/isolation

CLI processes were created by reviewer Popen, with bounded timeout parents, private XDG data/config/cache under this review directory and only temporary project paths. `commands.jsonl` records owned process trees/executable/argv for later checks, including the private editor and fresh import. Reviewer editor used23650/23651, no toolkit/vendor addons. The isolated preview used no MCP runtime server. Author PID62466/19650–19654, greybox16650–16654 and all other workspace processes were neither contacted nor switched/stopped. Timeout cleanup targets only processes launched by that command. The temporary review plugin saves/reloads copied scenes without changing node placement or geometry. It is not a proposed repository implementation.

## Disposition and remaining owners

| Scope | Status | Meaning/next owner |
| --- | --- | --- |
| Owner's concept A selection | accepted | User's supplied approval; no new direction requested |
| Original source/dependencies, source/export freshness, units/axes/pivot/material mappings | accepted | Bounded static technical proof, subject to F1's narrow rejected mesh-quality check |
| Imported linkage, wrapper sockets, positive roots, stable resource/node identities | accepted | F2 changes serialization only; no identity loss |
| Isolated native camera/static silhouette | accepted | Scoped visual review of this saved preview; no equipped/in-city acceptance |
| Zero-area face quality check | rejected | F1, P3; Astra source owner correction/reexport |
| Claimed byte-identical stage roundtrip | rejected | F2, P3; Godot/evidence owner normalize or narrow claim |
| Final production handoff reconciliation | pending | Producer records this audit and resolves or explicitly tracks both minor corrections; this review does not claim full production/game acceptance |
| Equipped fit/reach/head clearance/right dominant-left support-right shoulder/hold-aim-fire recovery | pending | Player owns versioned production rig and actual equipped checks; none exists here |
| Effects trail/explosion and camera-edge/city/motion readability | pending | Effects owner/external integrator; rocket trail anchor is only linkage |
| Projectile simulation/damage/spawn/lifecycle/networking/game-launch integration | pending, outside this asset delivery | External integrator; no gameplay implementation or network claim made |
| Sustained CPU/GPU/load/overdraw/Deck LCD-OLED/packaged Windows-Linux compatibility | pending | S07/S08/integrated owners; no performance/device measurements performed |
| Weapon-local rig/clips/reload, skinning, retargeting | not applicable | Fixed static visual; cooldown design requires no launcher reload; player owns pose/recovery |
| Texture painting/normal maps/external remaps | not applicable | Embedded named flat PBR colors suffice for approved scoped design |
| World placement/collision/routes/navigation/minimap/damage authority | not applicable to this diff | Cosmetic wrappers and isolated stage have no collision or world/gameplay placement changes |
| Source LOD variants/inherited variants | not applicable | Neither is introduced; default import LOD settings are documented, performance remains pending |

Producer notification: this report and its logs are ready for selective committed evidence under `docs/assets/rocket_launcher_evidence/` in a producer-owned follow-up. Do not commit the complete /tmp snapshot, caches, temporary plugin or copies. Recommended durable evidence is this report, relevant final logs/JSONs and the stage diff, with candidate/base identities preserved. The candidate itself was not changed by review. Final branch/HEAD/status recheck confirms the requested branch and revision with an empty working-tree status. `owned-processes-final.json` verifies all 13 recorded reviewer-owned host PIDs have exited; no cleanup of another workspace process was performed.
