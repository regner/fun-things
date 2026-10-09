# Dock Thumper — launcher and rocket asset handoff

9 October 2026. Regner approved **A — Dock Thumper** for its top-down silhouette.
This handoff covers the static launcher, visible rocket and asset-local preview.
Independent technical review of `0be3af33d6c9cab30cffca1aed748875b9a36373`
returned no P1/P2 findings and two P3 corrections. F1 is corrected in this candidate;
F2 is normalized and awaits same-reviewer roundtrip disposition. Equipped poses remain pending
on the player-owned production rig; gameplay, networking and effect integration
belong to the external integrator. No shared planning files were changed.

## Ownership and provenance

Producer: Codex, Paseo `29438b4a-4815-4a68-8614-5d0a704809f2`, branch
`art/brackett-rocket-launcher`, worktree
`/home/regner/.paseo/worktrees/0u71f39f/brackett-rocket-launcher`.
Shared baseline: `c030d66d7d0a9db19c0c2aebf1aa2b83eded6275`;
concept commit: `504486494f5ce21e9ffa5e58eed4373f8ba7d286`.
[Approved concept and exact imagegen prompts](../concepts/assets-v1/rocket-launcher/README.md).
Names are fictional working labels. No real brands or downloaded models/textures
were incorporated. Original Blender geometry/materials were authored in this
worktree using bpy; no third-party asset attribution or separate asset license is asserted.

Modeling instruction: realize A's chunky shoulder tube, coral muzzle ring, broad
ivory crown and restrained cyan accents; simplify concept microdetail for the
47 m overhead camera; provide a matching coral-nosed, ivory-finned rocket, measured
contact markers and a Blender-authored neutral stage. The original executable
recipe is `art/source/models/rocket_launcher/author_dock_thumper.py`. Subsequent
saved-source refinements widened the crown to ±30° and corrected face winding.
The saved `.blend` is authoritative; reexport does not regenerate geometry.

Owner's prospective routing instruction supersedes the old cohort skill policy:
all modeling, deformation, spatial rig/rest design and animation use Astra;
nonspatial Godot configuration/import/bookkeeping may use Sol 6.1. Effective active
runtime was verified as `gpt-6-astra` / high before resumed spatial work. Source,
editor state and processes were preserved. [Runtime receipt](rocket_launcher_evidence/model_routing.json).

## Source → export → reusable scene

All paths below are repository-relative. Source:
`art/source/models/rocket_launcher/dock_thumper_a.blend`, Blender **5.2.2 LTS**
`d13f752e3b9c`, bundled glTF exporter **5.2.40**. `art/source/.gdignore` excludes
sources from Godot. Exact export settings, membership, materials, source AABBs
and triangle counts: `art/source/models/rocket_launcher/source_manifest.json`.

| Export collection | Explicit GLB in `art/models/rocket_launcher/` | Saved wrapper | Base triangles |
| --- | --- | --- | ---: |
| `export_dock_thumper_launcher_a` | `dock_thumper_launcher_a.glb` | `scenes/prefabs/rocket_launcher/dock_thumper_launcher_a.tscn` | 8,204 |
| `export_dock_thumper_rocket_a` | `dock_thumper_rocket_a.glb` | `scenes/prefabs/rocket_launcher/dock_thumper_rocket_a.tscn` | 3,650 |
| `export_dock_thumper_preview_stage` | `dock_thumper_preview_stage.glb` | `tests/fixtures/rocket_launcher/stage.tscn` | 752 |

Wrappers retain linked `Visuals/Model` imports, unit roots and positive scales.
All visible stage geometry also comes from Blender. No embedded/generated visible
Godot meshes, collision, simulation, damage, effects or gameplay scripts are added.
S02 launcher and S15 rocket technical fixtures remain untouched.

Flat PBR materials are embedded in GLBs with one named material per mesh:
`dock_thumper_petrol`, `dock_thumper_coral`, `dock_thumper_ivory`,
`dock_thumper_graphite`, `dock_thumper_cyan` (subtle emission), and stage-only
`dock_thumper_asphalt`. No texture maps are required for these broad colors;
UV texture painting, normal maps and external material remaps are not applicable.
Imported `.glb.import` metadata is committed, including default generated LODs and
shadow meshes. No source LOD variants or ratified triangle/performance budget.
Triangle counts above describe the source, not measured frame cost.

Static, fixed geometry needs no skin, bones or weapon-local animation clips.
No reload clip is implied: the agreed design uses cooldown presentation.
Player owns hold/aim/fire recovery and future equipped acceptance.

## Measured contacts and frames

Metres; Blender +Y forward/+Z up/+X right converts once to Godot -Z/+Y/+X.
Launcher origin is the dominant grip attachment pivot, not a hand bone or wrist.
Every imported socket has identity basis: X=(1,0,0), Y=(0,1,0), Z=(0,0,1).
No root compensation or S13 fixture binding is used.

| Source marker | Stable wrapper path | Imported position (X,Y,Z), m | Contact normal |
| --- | --- | --- | --- |
| `socket_grip` | `Sockets/WeaponMount` | (0, 0, 0) | Pivot inside grip; no single surface normal |
| `socket_muzzle` | `Sockets/Muzzle` | (0, .300, -.905) | Opening faces (0,0,-1) |
| `socket_support_hand` | `Sockets/SupportHand` | (0, -.0825, -.430) | Actual underside surface (0,-1,0) |
| `socket_shoulder` | `Sockets/Shoulder` | (0, .085, .280) | Actual pad underside (0,-1,0) |
| `socket_trail` (rocket) | `Sockets/Trail` | (0, 0, .230) | Exhaust points (0,0,+1) |

Grip cross-section: .090 m X × .100 m Z; vertical extent Y=[-.075,.175].
Support contact footprint: .090 m X × .105 m Z. Shoulder underside footprint:
.235 m X × .220 m Z. Contact markers describe the surfaces, not bone transforms.
Right dominant hand, left support hand and right shoulder are provisional player
posing conventions. Exact bone twist/offset, reach and head clearance require the
future `docs/assets/shared_humanoid_rig.md` contract from player owner
`7016b739-5eea-480c-afa3-2c0cbad484a2`. No versioned production rest rig exists yet.

Launcher imported AABB: min (-.203,-.0825,-.900), size (.406,.585,1.430).
Rocket imported AABB: min (-.064095,-.105819,-.225), size (.184095,.211638,.450).
Rocket three-fin asymmetry accounts for its asymmetric X bounds.
Rocket trail marker is 5 mm behind the rim at Z=.225; opening radius .033 m
(diameter .066 m), outer rim radius .060 m. Effects owner
`c9207bb9-925b-46e4-bd68-e37aaa66a617` owns emission/trail/explosion presentation.
Selected-effects candidate `d015ae6cc5ad070a86c5025383f39f0f8cc79d08` attaches
`scenes/effects/weapon_effects/weapon_effects_a_trail.tscn` at `Sockets/Trail`
identity. It emits along +Z; puffs fade at .25/.50 s. Integrator retains/detaches
the trail when removing the rocket, calls `stop_emission()`, then waits for `finished`
after .58 s so residual puffs survive. Its ±12 m XZ / ±3 m Y visibility box is
provisional until speed and turn displacement are known. Preview uses the marker only;
it contains no duplicate rocket. Effects review is underway. The source marker is visual
linkage only; it defines no projectile speed or lifetime.

## Saved preview and actual camera evidence

Open `tests/fixtures/rocket_launcher/preview.tscn` with pinned Godot
**4.8.dev7.official.c971f93e7**. Keys: 1 game camera, 2 launcher detail, 3 rocket
detail, Escape close. Preview caps 60 FPS and enables VSync. For bounded playback:

```sh
godot --path . --max-fps 60 --resolution 1280x800 --quit-after 600 tests/fixtures/rocket_launcher/preview.tscn
```

The saved stage contains four launcher headings at grip height 1.35 m and a rocket
at 1.65 m; these are isolated visual samples, not an equipped character test.
Game camera is vertically down, north-up, perspective 47 m / 42°, near .1 m,
far 160 m, 1280×800. Measured projected AABB: launcher **10.64×33.01 px**, rocket
**4.71×10.77 px**. Coral muzzle and broad pale crown preserve front/back contrast
in the four orientations. The rocket remains small; trail readability belongs to
the effects preview. Fine grooves are detail-view decoration.

[Actual game-camera capture](rocket_launcher_evidence/game_camera.png) ·
[Launcher detail](rocket_launcher_evidence/detail_camera.png) ·
[Rocket detail](rocket_launcher_evidence/rocket_camera.png).
Captured with Forward+ / Vulkan / GTX 1070 / X11 at native resolution; no image edits.
The detail rocket camera uses a short far plane to isolate it. Preview colors and
silhouette are inspected; the full city's lighting, hand occlusion, controls and
motion acceptance remain pending. Screenshots are not performance measurements.

## Validation and reproducibility

`tools/rocket_launcher/capture_check.gd` loads the saved preview and asserts source
instance ancestry, unit roots, no physics collision, marker/wrapper transforms,
independent numeric expectations, imported AABBs and camera settings. It instantiates
saved content only. `-- --capture` additionally writes the three native PNGs.

```sh
blender --background --factory-startup -noaudio art/source/models/rocket_launcher/dock_thumper_a.blend --python art/source/models/rocket_launcher/reexport_dock_thumper.py -- /tmp/dock-thumper-fresh
python3 tools/rocket_launcher/check_files.py /tmp/dock-thumper-fresh
gdstyle check tests/fixtures/rocket_launcher/preview.gd tools/rocket_launcher/capture_check.gd --no-color --max-warnings 0
python3 tools/rocket_launcher/prepare_clean.py /tmp/dock-thumper-clean
# Run import/check with private XDG directories and available private editor/debug ports.
godot --headless --path /tmp/dock-thumper-clean --import
godot --headless --path /tmp/dock-thumper-clean --max-fps 60 --quit-after 900 --script res://tools/rocket_launcher/capture_check.gd
```

| Check actually completed | Retained evidence | Result |
| --- | --- | --- |
| Saved `.blend` fresh reexport, all 3 outputs byte-identical | `rocket_launcher_evidence/reexport-final.log`, `source_export_checks.json` | exit 0 / fresh comparison true |
| Godot script compilation, both owned scripts | `clean-script.jsonl` | valid, no diagnostics |
| gdstyle 0.3.0 | `gdstyle.log` | 2 files, no issues |
| Private editor save/close/reopen, stable UIDs/node IDs | `editor_roundtrip.json` | final roundtrip byte-identical |
| Clean project, 15 identical runtime files, fresh import | `clean_file_identity.json`, `clean-import-verified.log` | exit 0, no diagnostics |
| Clean project focused headless assertions | `clean-check-verified.log`, `clean_imported_checks.json` | exit 0, `DOCK_THUMPER_CHECKS_PASS` |
| Bounded graphical assertions and 3 captures | `capture-final.log`, `imported_checks.json`, PNGs | exit 0, checks pass |

Editor roundtrip initially normalized redundant `type="Node3D"` on two imported
instances; preserved UIDs/node IDs, then second pass was byte-identical. The supplied
MCP endpoint at 6550 and Blender MCP were unavailable, explained before fallback.
Authoring used owned Blender CLI and Godot toolkit wire commands on verified private
editor PID62466, exact worktree, ports19650–19654, private XDG under
`/tmp/brackett-rocket-launcher`. No shared editor switch/config changes. Saved scene
composition and resources were authored through this editor, not runtime builders.

Historical sandbox clean-import attempt hit editor socket permission errors
(`clean-import-sandbox.log`); a distinct authorized host run passed with private
ports19662–19664. Blender sandbox teardown stalled after writing and was interrupted;
the final host reexport completed normally. Full-project startup included unrelated
plugin/S02 diagnostics; the clean runtime profile establishes only these assets and
owned scripts. Neither headless import nor this focused check certifies the entire
project, multiplayer, target-device performance or packaged builds.

## Handoff status and reconciliation delta

Owner concept: accepted A. Source/export, imported static geometry, saved wrappers,
marker contracts and isolated visual evidence: produced and locally checked.
Independent review: [complete report](rocket_launcher_evidence/review_0be3af3/REPORT.md),
reviewer `554a3fc2-a56a-43f2-979c-579a28de1978`, Sol 6.1 high, base
`504486494f5ce21e9ffa5e58eed4373f8ba7d286`, candidate `0be3af33d6c9cab30cffca1aed748875b9a36373`.
F1: removed collapsed faces from RearRecess, ExhaustRecess and RocketIvoryBand;
independent Blender and imported Godot mesh checks now report zero-area triangles 0,
and fresh source reexport matches both changed GLBs byte-for-byte. F2: the exact
redundant instance type found in the reviewer’s Godot roundtrip was removed from the
saved stage; resource UID and node identity are preserved. The reviewer must confirm
byte-stable roundtrip at the corrected candidate. Runtime was Astra high before the
geometry correction. Godot toolkit saves later stalled without rewriting the stage,
so this one serialization line used the documented direct-file fallback. The reviewer
repeats save/reopen on the new exact candidate. No other workspace process was used
or stopped. Equipped rig/hold/aim/fire recovery:
pending player contract and actual fit checks. Projectile simulation, damage,
networking, collision, effect integration and game launch: external integrator.

For later catalogue reconciliation, add `dock_thumper_launcher_a` and
`dock_thumper_rocket_a` with this source/export/prefab/preview mapping; stage is a
preview dependency. Proposed TODO delta: mark selected launcher/rocket static asset
production delivered after review, retain player attachment/hold/aim/fire fit and
effects/projectile integration as explicit remaining acceptance. No broad weapon,
foundation, networking or performance task is closed. Shared catalogue/TODO files,
main launch, main branch and remotes remain untouched.
