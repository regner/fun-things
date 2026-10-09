# city_shop_fittings.06 — static glazed shop door leaves

9 October 2026. Original editable source and explicit GLB candidate for ROOT
`fbd92534-e159-432f-aae7-28072c2bf3b2`, requested Astra MEDIUM commission.
Commission reference: `commission.md` at `2a0fe4f588f86ca1d9b1226f8fb5ede065e6c661`;
the supplied production authorization supersedes the historical concept-only brief.
Source/export and actual .03 mating checks are candidate evidence, **not READY**.
Independent acceptance and engine integration remain with ROOT/integrator.

## F2 correction submitted for same-reviewer disposition

This is the existing-ID correction to Batch03 initial F2 (P3), against immutable
candidate `028775618c4493ca672646e6e37fdc3c83e0e313`, parent
`10ddb64d16e6cb2f137923a31d3ca14991468f7d`, original base
`66400c26a01bf917dfe631af4762c2b444d9c48f`. The frozen independent report, callbacks,
images and rejected source/export bytes remain authoritative historical evidence;
the reviewer pack was not modified. No new ID or delegation was performed.

The three leaf rings now use the bevel modifier's `MITER_ARC` inner join with
spread equal to the existing 4 mm bevel radius, replacing sharp inner miter
patches. Broad-face weighted normals remain. This changes inner-corner surface
tessellation, without adding decorative detail or changing outer/body/handle
bounds, slots, datum, materials, glazing, pulls or .03 inputs. Each ring now has
1,088 triangles (+480); the extra triangles resolve the bounded corner joins.

Both saved-source and raw-GLB tests now assert **every triangle corner normal**
points into its geometric triangle hemisphere, rather than checking only their
mean. All opposing corners are eliminated. The worst ring source dot is
+0.612006; the full outputs' minimum is approximately +0.54917 on unchanged pulls.
The reviewer front/rear 35 mm close-camera views were repeated at the same lights,
800×800 resolution, 32 samples and AgX. The sharp inverted-normal streak is softened
into a continuous miter highlight; a soft joining highlight remains in this highly
magnified crop. This is producer evidence, not independent visual acceptance.

**Current authoritative checks/renders:**
[`city_shop_fittings_06-evidence/fix_f2/`](city_shop_fittings_06-evidence/fix_f2/).
The previous root-level checks, renders and `initial/` / preview-fix history are
retained unchanged as historical payloads. The top-level `fitted_comparison.blend`
is refreshed from current sources; its prior bytes are retained in
`fix_f2/before/fitted_comparison.blend`. All 17 current .03/.06 scratch mesh signatures
(vertices, polygons, normals, smooth flags, slots and material values) match actual
saved sources in `scratch_correspondence.json`.

`preservation_before.json` verifies all 80 previous expected files before mutation,
records immutable .03 and importer-sidecar hashes and the frozen Git identities.
`before/manifest.json` and `before/author.py` preserve exact previous bytes.
`preservation_after.json` verifies that no previous payload path was removed, only
the permitted correction paths changed, all .03 inputs/sidecars remain unchanged,
and actual GLB materials, glazing and pull payloads equal the frozen reviewer
exports. No Git/index or sidecar mutation was performed. Root `manifest.json` is
the complete current expected-set/byte/SHA inventory, retaining all previous history
and additive correction evidence; integrator-owned `.import` files are excluded.

Both actual .03 source/GLB mating assemblies pass again: 8 mm side/head/meeting,
10 mm sill, 6 mm stop clearance; no leaf/surround surface intersections. Fresh
saved-source reexports are byte-identical. Final source SHA256 is
`40122b4ab26a6a348fc914e936421e75453a33f77cee88c16bd86df2a87e4fe7`;
single GLB (38,928 bytes)
`37e9ce1667105cc66120edf4d114b3a4228972000ac89c14ed1a2608e9b309c6`;
double GLB (64,608 bytes)
`b4138a6a2b7ebd96f934448d4617bc6b0d127d48bf814eab8016695e50153cbf`.

One proportionate correction cycle retained distinct diagnostic probes: clearing
custom normals and changing eight corner diagonals did not solve the opposing
normals; hardening alone also failed. An arc probe used an invalid enum `ARC`
(exit 1); the diagnostic identified `MITER_ARC`, and the corrected probe used it.
Default arc spread was too large and generated opposing normals; explicitly
bounding spread to 4 mm solved them. Arc-plus-harden was also inspected, but gave
no useful visual advantage, so production retains its existing weighted normals.
Probe exit 0 means the diagnostic completed, **not** that its measured geometry
passed; their JSON records retain negative dots. The failed enum script, literal
commands, exits, stdout and stderr are retained. No failed probe was retried unchanged.

Current `f2_run.py` jobs (pin, author, export, raw GLB, fresh reexport, actual assembly,
scratch correspondence, retained close cameras and refreshed previews) exit 0.
`*.command.json` records exact argv/cwd/process-local environment and each separate
raw `.stdout` / `.stderr`, including empty streams. Existing thumbnail-cache denial,
optional MeshOptimizer absence and use_nodes deprecations remain unsuppressed.
Reproduction: `python tools/asset_production/city_shop_fittings_06/f2_run.py`, then
`python tools/asset_production/city_shop_fittings_06/f2_capture.py final_audit python tools/asset_production/city_shop_fittings_06/f2_finalize.py`,
then `python tools/asset_production/city_shop_fittings_06/manifest.py`.

Same independent reviewer owns final F2 disposition. Engine/prefab/runtime/collision/
network/device gates remain pending; no READY claim. All owned writers are quiescent
at callback, and the worker remains available for concrete corrections.

## Source, outputs and original provenance

- Editable source: `art/source/models/environment/city_shop_fittings_06/city_shop_fittings_06.blend`.
- Named collection: `export_city_shop_fittings_06`, with `variant_single` and
  `variant_double`; identity roots `city_shop_fittings_06_single` and `_double`.
- Game outputs: `art/models/environment/city_shop_fittings_06/city_shop_fittings_06_single.glb`
  and `city_shop_fittings_06_double.glb`. Double contains the complete closed pair.
- Each leaf has independently editable `stiles_rails`, `glazing`, and `static_pull`
  mesh objects, named `{variant}_leaf_{1|2}_{component}`. Bevels and weighted normals
  are applied. Both variant collections intentionally overlap at the same datum;
  isolate one for editing/export. No live editor session was used.
- `authoring_excluded/authoring_1m_reference` is a saved, measured 1 m cube,
  excluded from both GLBs and shown in `measured_1m_comparison.png`.

Original geometry was authored inside pinned private Blender by owned `author.py`:
a continuous broad leaf ring, opaque tinted glazing slab and rounded U-profile pull.
No external mesh, texture, font, paid generation or image-generated model input.
Read-only .03 exporter/check patterns informed the owned tools. No external
attribution obligation is introduced. Palette and smooth broad highlights follow
`docs/art-direction.md`; shared practical frontage scope follows `city_shop_fittings.md`.
The .03 source and two exports are reference inputs only; their unchanged SHA256
values are recorded before/after inspection in `assembly_checks.json` and match
the delivered .03 exact manifest.

The leaf supplies no fixed entrance frame, shell wall, tenant graphics, interior,
working hinge, lock, animation, collision or gameplay logic. Glazing is deliberately
opaque and single-sided; no see-through interior, refraction or alpha sorting is assumed.

## Interface v1 and measured assembly

Metres, identity wall-plane/floor origin `(0,0,0)`, Blender +Y street and +Z up.
One glTF conversion gives Godot `(X,Z,-Y)`: -Z street, +Y up. All production mesh
and root transforms are identity; geometry carries the asymmetric depth offset.

| Measurement | Single | Closed double pair |
| --- | --- | --- |
| Leaf X interval(s) | [-.512,.512] | [-.912,-.004], [.004,.912] |
| Individual leaf width | 1.024 | .908 each |
| Body Blender Y / Z | [-.475,-.430] / [.030,2.232] | same |
| Body Godot Y / Z | [.030,2.232] / [.430,.475] | same |
| Body height / thickness | 2.202 / .045 | same |
| Whole GLB Blender AABB | (-.512,-.475,.030) → (.512,-.352,2.232) | (-.912,-.475,.030) → (.912,-.352,2.232) |
| Whole GLB Godot AABB | (-.512,.030,.352) → (.512,2.232,.475) | (-.912,.030,.352) → (.912,2.232,.475) |
| Whole width × height × depth | 1.024 × 2.202 × .123 | 1.824 × 2.202 × .123 |

Stiles are 85 mm, top rail 125 mm, bottom rail 240 mm. Broad 4 mm leaf bevels;
3 mm glazing bevel and 6 mm pull bevel use four segments. Glazing tucks 6 mm under
the ring; these internal assembly overlaps are intentional. Hardware stays inside
each leaf X/Z envelope, Z=[.920,1.320], front Y=-.352, projecting 78 mm from the
leaf front (22 mm within the permitted 100 mm maximum).

`assembly.py` appends actual .03 source geometry into private scratch with both
.06 variants at the shared identity datum. It independently imports the actual
.03/.06 GLBs and repeats measurements. Saved-mesh ray hits into both surfaces
measure 8 mm side and head gaps, 10 mm threshold clearance, 6 mm rear-stop clearance,
and 8 mm double meeting gap. Nine lateral probes per leaf and nine double-meeting
probes span three depths/heights. Body bounds and hardware bounds are measured;
BVH triangle-pair tests find zero intersections between every .06 mesh and all four
.03 surround meshes. Numerical assertions use 0.01 mm tolerance, within the supplied
±1 mm interface bound tolerance. These are actual source/export assembly checks,
not clearance arithmetic alone or Godot physics certification. Hardware mounts
also pass actual opposing surface probes after the owned fix described below.

The retained `fitted_comparison.blend` contains the real appended .03/.06 source
meshes, translated together by -1.55 m (single) / +1.05 m (double) along X for views.
It is scratch evidence only, excluded from game source/export membership. No shell
is fabricated; shell opening, installation and placement remain downstream.

## Materials and geometry

Three embedded opaque, single-sided Principled/glTF PBR materials; each component
has one material slot. Linear base colors are converted from these sRGB references.

| Component | Material / sRGB | Metallic / roughness |
| --- | --- | --- |
| Stiles/rails | `door_slate_petrol` / #405B68 | .25 / .40 |
| Glazing | `door_opaque_tinted_glazing` / #163D48 | .32 / .22 |
| Pull | `door_satin_handle` / #C8C2AD | .65 / .30 |

No emission, images, textures, UVs, tangents or external material dependencies.
Separate materials/textures directories are unnecessary. Per leaf: ring 1,088,
glazing 300, pull 604 triangles; single **1,992**, complete double **3,984**.
Three / six meshes and primitive surfaces, three materials and one identity root
per output. Final GLB sizes: single 38,928 bytes; double 64,608 bytes.
Density supports broad bevel highlights; no accepted device budget is
claimed. Rig, clips, sockets and LODs are not applicable to this static scope.

## Evidence, reproduction and limitations

Current check evidence: [`city_shop_fittings_06-evidence/fix_f2/`](city_shop_fittings_06-evidence/fix_f2/).
The root-level names below describe retained original evidence where not refreshed
in `fix_f2`; use the correction section above for the current reproduction/receipts.
`source_export_checks.json` checks exact collection membership, pin/build/exporter,
identity transforms, finite vertices, nondegenerate polygons, manifold consistent
edge winding, positive signed volume for every connected solid, triangle counts,
measured bounds and excluded metre fixture. `glb_checks.json` independently checks
raw payload triangle area/winding versus finite unit normals, node identity,
converted bounds, material/triangle agreement and studio/animation/skin exclusion.
`assembly_checks.json` contains source and GLB mating probes and unchanged .03 hashes.
`reexport_comparison.json` verifies both GLBs byte-identical in a fresh Blender
process opening the saved source; compared files are retained in `reexports/`.

`hero.png` shows leaves only; `fitted_hero.png`, `fitted_front.png`, `fitted_rear.png`
show actual .03/.06 assembly. `measured_1m_comparison.png` retains the excluded metre
reference. `project_camera.png` uses straight-down perspective, 47 m height,
42° vertical FOV and 1280×800; isolated fittings are tiny at that scale. It does
not establish door readability in a mounted shell, roof occlusion, engine lighting,
collision or gameplay. `preview_checks.json` records camera/render parameters. Visual self-review of the
final fitted hero finds broad smooth stiles/rails, quiet tinted panels and readable
paired pulls; the single pull is partly occluded by its recess at oblique angles.
The actual project-camera view cannot resolve these small hardware details.

Reproduce from repository root:

```sh
python tools/asset_production/city_shop_fittings_06/run.py --preview
python tools/asset_production/city_shop_fittings_06/manifest.py
```

Private Blender uses process-local `ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy`,
`-b -noaudio -t 4 --python-exit-code 1`; Cycles CPU, 32 samples, AgX. Version is
5.2.2 LTS / build `d13f752e3b9c`, glTF exporter 5.2.40. The runner regenerates
source and exports; no byte-identical `.blend` regeneration is claimed. Saved-source
verification can run `export.py` with that `.blend` loaded and `-- <scratch-dir>`.
`commands.json` and corresponding full raw logs retain actual argv, cwd, process-local
environment overrides and exits; initial receipts and outputs remain under `initial/`.

One meaningful owned fix cycle moved the pull centres from 122 mm to 43 mm from
closing leaf edges, onto the broad stiles. Initial geometry left the mounting feet
4 mm clear of the glazing. Final two-point mount ray probes per handle measure
4 mm engagement into the stile in both saved source and imported GLBs. All affected
exports, geometry/assembly checks, exact reexports and renders were repeated.
Initial source, exports, scripts, checks and previews are retained under `initial/`.
Visual QA also found that collection visibility iteration left the double surround
visible in the intended leaf-only hero/metre views. Preview visibility now targets
the eight named surround meshes explicitly and asserts all are hidden; renders
were repeated without changing production geometry. Earlier captures/log/script
remain under `preview_before_visibility_fix/`; `preview_fix_command.json` retains
the exact corrective render argv and exit.

Actual diagnostics/failures, with complete raw logs and argv/exits retained:

- Requested `/usr/bin/blender5.2.2LTS` is absent (exit 127). Fallback `/usr/bin/blender`
  verifies the exact authorized 5.2.2 LTS build/exporter before authoring/export.
- Version command exits 0 but reports one unfreed memory block (0.000023 MB).
- `Material.use_nodes` / `World.use_nodes` deprecation warnings appear in author/preview.
- OpenImageIO cannot write sandbox-excluded desktop thumbnail cache files during
  source and scratch saves; saves, independent reopen and validation succeed.
- Export/reexport report missing optional MeshOptimizer library. No compression is
  requested; uncompressed geometry and byte-identical saved-source reexports pass.
- BlenderMCP addon registration messages are private CLI startup output; no live
  endpoint was accessed. No global addon/configuration change was made.
- Initial documentation lookup included nonexistent root `art-direction.md` and
  returned exit 1; corrected read used the actual `docs/art-direction.md`.

All final author/export/raw-GLB/reexport/assembly/preview jobs exit 0. Logs retain
these diagnostics without filtering or suppression; thumbnail and optional-library
messages do not constitute engine or device certification.

Engine import/sidecars, prefab, inherited save/reload, mounted shell/world placement,
runtime/collision/query/network/device tests and independent art/technical acceptance
are pending. Frozen six-asset engine candidate `c4067ff3abe1384301471d9a64e94e84201235e2`,
Git/index, shared docs/project/prefab/world files, services/configuration and other
assets were not mutated. No source-only readiness or self-acceptance is asserted.

`manifest.json` is the exact expected path/byte-size/SHA256 inventory of all owned
source, outputs, scripts, report and retained evidence, excluding itself to avoid
recursion. Check that inventory before integration. All owned writers are quiescent
at handoff; this worker remains available for concrete fixes.
