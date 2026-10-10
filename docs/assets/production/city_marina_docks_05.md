# city_marina_docks.05 — Small dock mooring cleat

10 October 2026. **Source, export and linked mounted component delivered; independent
review and full world/gameplay acceptance pending.** Original Blender construction by
the commissioned implementation specialist, following the [commission](commission.md),
[marina brief](../city_marina_docks.md), [Old Quay concept](../../concepts/districts-v1/old-quay.md)
and Petrol & Coral direction. No downloads, external artwork, real brands or generated
runtime meshes. This is small pontoon hardware, not the separate quay-bollard family.

## Design and provisional dimensions

A gently lifted continuous twin-horn crossbar on two tapered cast legs, above a rounded
dark mounting plate with four restrained hex fasteners. The throat is a real open gap,
not a black face. Broad satin highlights and the clear horn silhouette carry the close
view; no ropes, fine wear, timber texture or mooring simulation is introduced.

The dark plate reuses the exact `dock_frame_metal` palette of [main .01](city_marina_docks_01.md),
[finger .02](city_marina_docks_02.md), [gangway .03](city_marina_docks_03.md) and
[connector .04](city_marina_docks_04.md). New satin metal stays neutral and subordinate
to the pale pontoon perimeter. No existing sibling files or materials were modified.

Dimensions are **provisional authored values**, allowed by the current production
brief's standing dimension rule; they are not inferred raster measurements or basin-fit
approval. The earlier .01 family handoff explicitly permits visual-only .05 hardware.
This low deck-mounted fitting follows that exception, not the freestanding-prop rule.

| Interface | Godot local metres |
| --- | --- |
| Root/pivot | (0,0,0), centred on deck-contact mounting plane |
| Whole visual AABB | min (-.240,0,-.080), max (.240,.150,.080) |
| Whole size X/Y/Z | (.480,.150,.160) |
| Base plate | .320 X × .028 Y × .160 Z |
| Horn axis | Local X; either end is equivalent |
| Family mounting height | Root Y=.500, top Y=.650 relative to pontoon water datum |
| Fastener centres | X=±.115, Z=±.050; decorative heads only |
| Numeric envelope/datum tolerance | ±.001 m |

Root and mesh have identity local transforms, metre units and applied modifiers.
Blender +Z maps to Godot +Y; Blender +Y maps to Godot -Z. Unlike the water-centred
pontoon roots, the cleat's zero is its actual deck-contact plane: placing it at water
level would submerge it. No sockets, rig, clips, moving parts or runtime attachment API.

### Mounting examples, not world placement

Mount only on flat composite, not the 2 cm higher pale perimeter or the gangway slope.
The horn should run parallel to the exposed dock edge; avoid walking joins and gangway
landings. Never enlarge this asset into a quay bollard or scale it to force a fit.

- Identity .01 main: cleat at **(±1.28,.50,0)** with **+90° Y** rotation.
- Identity .02 finger: cleat at **(±.53,.50,0)** with **+90° Y** rotation.
- These bases stop **.02 m inside the composite inset** and **.14 m inside the outer
  pontoon boundary**. Opposed finger bases leave **.90 m clear visual space** between
  them; the existing production capsule is .70 m wide.
- On a flat .04 connector the same 1.28 m lateral inset applies along an exposed side;
  do not put fittings across its open joining faces. That optional mounting is not
  included in the measured fixture.

## Source, export and materials

- Source: `art/source/models/environment/city_marina_docks_05/city_marina_docks_05.blend`.
- Collection: `export_city_marina_docks_05`; root `CityMarinaDocks05`, mesh child
  `CityMarinaDocks05_Mesh`. Eight closed manufactured islands joined into one mesh.
- Explicit GLB: `art/models/environment/city_marina_docks_05/city_marina_docks_05.glb`
  with committed `.glb.import` identity.
- Linked wrapper: `scenes/prefabs/environment/city_marina_docks_05.tscn`.
- Reproducible author/export/validate/render/manifest scripts and mounting fixture:
  `tools/asset_production/city_marina_docks_05/`.

Two opaque Principled material surfaces; no textures, embedded images or Godot remaps:

| Material | Linear RGB | Metallic | Roughness |
| --- | --- | --- | --- |
| `dock_frame_metal` | .055, .075, .079 | .55 | .44 |
| `dock_cleat_satin_metal` | .32, .37, .36 | .65 | .36 |

Blender **5.2.2 LTS**, build `d13f752e3b9c`; glTF exporter **5.2.40**. The export
loads shared `tools/assets/blender/export_settings.json`, filters only the named
collection, disables skins/animations and converts Y-up once. Lane construction and
validation patterns are reused; there is no shared marina geometry-authoring library.
Studio objects live only in the unsaved evidence scene. Godot's default generated LODs
remain enabled; transitions and repeated-placement cost are not yet accepted.

## Prefab and bounded checks

`Visuals/Model` is an identity-transform imported scene instance, not copied geometry.
The cleat is **visual-only mounted decoration** under the earlier family approval.
The pontoon slab remains the sole collision owner; no small snagging collider, invisible
obstacle or independently walkable cleat top is added. This is not a freestanding prop,
barrier, boat-attachment mechanic or a general exemption for other fixtures.

Pinned Godot **4.8.dev7.official.c971f93e7** imported the export. The wrapper and owned
`mount_check.tscn` were loaded, packed, saved and reloaded twice with byte-stable scene
UIDs/node identities and linked ancestry. Checks resolve every saved dependency UID,
verify actual imported bounds, two opaque/back-culled surfaces and identity transforms.
The wrapper has no gameplay script or collision object.

The saved fixture instances unchanged .01 and .02 prefabs, with one main-deck cleat and
two opposed finger cleats at the documented offsets. Mounting checks verify deck contact,
height, orientation and inset containment. **Four down-rays** through hardware/centre
hit the existing deck at Y=.50, never the decorative hardware top. A production
`ActorMotion` body with capsule radius .35 m / height 1.8 m walks the central finger
route from (0,.501,-2) for **48 ticks in each of AUTHORITY and REPLAY**. Both reach
**(0,.500999987,2.000000715)** with native downward support confirmed each tick.
Two separate standalone process runs reproduce those outcomes with clean runtime logs.
This is component mounting and movement/replay API evidence, **not network transport,
admission/prediction or whole-marina gameplay acceptance**.

Direct scene text authoring plus isolated headless normalization was the mandated
fallback because the windowed editor is unavailable. No live Blender/Godot MCP session
was used. Headless checks do not synchronize or prove a roundtrip in another open editor.

## Evidence and validation

[Hero](city_marina_docks_05-evidence/hero.png) ·
[Side](city_marina_docks_05-evidence/side.png) ·
[Mounting/throat detail](city_marina_docks_05-evidence/detail.png) ·
[47 m / 42° overhead](city_marina_docks_05-evidence/overhead_47m_42deg.png).
All four final compressed images were visually inspected alongside the earlier family
hero. Rounded horn ends, two supports, open throat and restrained fasteners read cleanly
up close. The side camera was raised after self-review to remove an underside-of-studio
floor strip; no geometry correction was needed.

These are isolated Blender Cycles/AgX renders, **not engine or world screenshots**.
All are **1280×720**, following the current brief rather than the older 1280×800 figure.
Overhead is vertical-down at 47 m, 42° vertical perspective FOV, Blender +Y at image top.
At this honest scale the cleat is only a tiny metal dash, roughly ten pixels long;
individual legs/fasteners are not gameplay-readable. It intentionally remains quiet
mounted decoration, not an interaction marker. Actual mounted engine readability and
shimmer remain pending; the asset was not inflated to fake overhead recognition.
PNG compression 95 at render, then level 9 with seven significant RGB bits/channel.
Final images are **362–399 KiB**. No paintover, labels or geometry edits in images.

[validation.json](city_marina_docks_05-evidence/validation.json) records:

- **2,144 triangles; 1,088 source vertices; 1,388 exported split vertices**.
- **One mesh, two surfaces**, zero degenerate source faces/export triangles,
  zero non-manifold source edges, consistent winding and unit-length normals.
- Actual binary GLB positions, normals and triangle indices checked independently
  of accessor bounds; no images, skins, animations or extra scene nodes.
- Provisional .48 × .15 × .16 m envelope and identity deck-contact pivot pass.
- Fresh separate-process export **byte-identical** to the **59,552-byte GLB**.
- Full `production_checks.py` passes: pinned engine/GUT, owned-script formatting,
  lint and explicit compilation, **14 Python tests**, **75/75 GUT tests / 2,041 asserts**,
  and the intentional failing-GUT negative control. No known failures were ignored.
- Owned `check.gd` passes pinned gdstyle 0.3.0 with zero warnings.

[manifest.json](city_marina_docks_05-evidence/manifest.json) hashes every produced
payload with SHA-256/byte counts, excluding itself to avoid recursive hashing.
[final.log](city_marina_docks_05-evidence/final.log) retains one concise command/result
receipt. Raw logs and scratch exports remain outside the repository under
`C:/tmp/ft/assets/city_marina_docks_05/`.

Diagnostics: Blender emits a `use_nodes` deprecation warning but exits normally.
Headless editor normalization emits the addon's engine-version warning and shutdown
RID/ObjectDB leak diagnostics, as with earlier lane assets. Normalization completion
and stable saved bytes were independently checked. Standalone checks and the isolated
full production-check compiler/test mirror are clean; no diagnostics were suppressed.

## Reproduction

Run from repository root in Bash. Every Blender call uses factory startup, four threads,
disabled audio and a 900-second cap. Use only the mise-pinned Godot, never live sessions.
Image compaction and manifest generation require Pillow.

```sh
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy
B='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
G="$(mise which godot)"
T=tools/asset_production/city_marina_docks_05
S=C:/tmp/ft/assets/city_marina_docks_05
mkdir -p "$S"
for step in author export render; do
  timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
    --python-exit-code 1 --python "$T/$step.py" || exit $?
done
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/export.py" -- "$S/reexport.glb"
timeout 900 "$B" -noaudio --background --factory-startup --threads 4 \
  --python-exit-code 1 --python "$T/validate.py" -- "$S/reexport.glb"
timeout 300 "$G" --headless --editor --path . --import
timeout 180 "$G" --headless --editor --path . --script "$T/check.gd" -- --normalize
timeout 180 "$G" --headless --path . --script "$T/check.gd"
"$(mise which gdstyle)" --max-warnings 0 "$T/check.gd"
# Use a fresh output directory on subsequent production-check runs.
timeout 1800 mise exec -- python tools/production_checks.py --output "$S/checks-reproduction"
python "$T/manifest.py" "$S/checks-reproduction"
```

## Remaining acceptance

Independent reviewer disposition is required. The world owner must place sparse fittings
on compatible deck surfaces, preserve walking joins and basin/bridge clearance, coordinate
yacht envelopes, and resolve shore access/water/fall-off before gameplay placement.
Actual engine-camera contrast/shimmer, blue-hour lighting, generated LOD transitions,
repeated GPU/Deck costs, packaged builds and real-process multiplayer remain pending.
No world, shared brief/queue/progress, gameplay rule or earlier family asset changed.
This delivery is for review, not blanket whole-city production acceptance.
