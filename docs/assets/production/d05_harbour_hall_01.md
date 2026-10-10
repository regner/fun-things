# d05_harbour_hall.01 — Harbour hall exterior

10 October 2026. **Source/export and linked prefab delivered; bounded checks pass.
Independent review and world-placement acceptance pending.** Produced by the isolated
asset-production worker on `lane/a-hhall`, commissioned under the current asset-common
brief and [production commission](commission.md). Parent/reviewer owns acceptance.
Family: [Harbour hall](../d05_harbour_hall.md). No shared tracker or sibling files changed.

## Design and dimensions

Original Blender construction: broad hipped slate roof, short restrained teal ridge/eave,
warm rendered civic walls, limestone cornices, broad opaque window bays, and a closed
four-panel entrance above three shallow steps. Smooth bevels and weighted normals;
no fine tile grid, clutter, interior, rooftop gameplay, door animation or destruction.
No downloads, real brands, external artwork/fonts or third-party mesh construction.

References inspected: accepted Petrol & Coral direction; Stage 3 Old Quay identity;
Stage 4 streets; selected district 05 map context; Old Quay v03 and its asset breakdown.
The 26 × 18 m neutral hall footprint is a sizing reference, not a measurement from the
concept image or an approved replacement placement. The broad roof remains subordinate
to the basin and harbour bridge. The civic square is separate open space, not included
as geometry or a placement in this asset.

**All authored dimensions below are provisional production choices**, permitted by the
standing dimension rule. Envelope tolerance is ±0.001 m; units are metres.

| Element | Authored dimensions / Godot coordinates |
| --- | --- |
| Wall mass | 26.0 X × 18.0 Z m; ground to 6.0 Y m including overlap with eave |
| Plinth | 26.4 X × 18.4 Z × 0.35 Y m, bottom Y=0 |
| Roof eave | 27.6 X × 19.6 Z m; fascia bottom Y=5.76, roof edge Y≈6.05 |
| Ridge | 8.36 m cap length; highest point Y=9.20 |
| Whole visual AABB | min (-13.8, 0, -10.8), max (13.8, 9.2, 9.8) |
| Whole visual size | **27.6 X × 9.2 Y × 20.6 Z m** |
| Entrance landing | X ±4.2; Z -9.6 to -9.2; top Y=0.30 |
| Shallow visible stairs | X ±4.2; Z -10.8 to -9.6; three 0.10 m risers, 0.40 m treads |
| Main entry surround | 6.25 m wide; frontmost pull Z=-9.2825; closed, no usable interior |

Root and mesh origin are (0,0,0), the ground-centred **main body footprint**, not the
asymmetric step/roof AABB centre. Blender +Y is front and maps to Godot -Z; Blender +Z
maps to Godot +Y. All static transforms are applied: translation zero, unit scale,
zero rotation at export root and mesh. Terrain stays flat; only the shallow entry
assembly rises 0.30 m. No ramps, curbs, roads or square paving are authored here.
The collision-only smooth slope beneath the visible stairs is described below.

### Sequential family handoff: d05_harbour_hall.02

The entry canopy is a separate asset and is deliberately absent. Use the hall at
identity. Provisional wall mounting centre is **(0, 3.85, -9.0)**, facing Godot -Z.
The source root records this datum; no exported socket was requested or added.
The central lintel is X ±3.3, top Y=3.74, projecting to Z=-9.215. Attach above it,
with mounting contact against the blank wall; do not bury the canopy slab in the lintel.
An approximately 8 m wide canopy with up to 2.4 m forward projection is a sensible
provisional fit inside the broad central bay; its own author owns final dimensions.
Keep the underside at least Y=3.3 for 3.0 m clearance above the landing, and preferably
above Y=3.74 at the wall to clear the lintel. No posts, rails or additional square
obstacles are part of this handoff. Civic identity hardware/artwork remains the
separate graphics/support records; this hall includes no duplicate sign carrier.

## Source, export and materials

- Source: `art/source/models/environment/d05_harbour_hall_01/d05_harbour_hall_01.blend`.
- Named export collection: `export_d05_harbour_hall_01`.
- Export root: `D05HarbourHall01`; child: `D05HarbourHall01_Mesh`.
- Linked export: `art/models/environment/d05_harbour_hall_01/d05_harbour_hall_01.glb`.
- Wrapper: `scenes/prefabs/environment/d05_harbour_hall_01.tscn`.
- Reproducible tools: `tools/asset_production/d05_harbour_hall_01/`.

One joined static mesh retains closed disconnected construction pieces; no destructive
boolean union is required. Source topology is manifold per piece. Studio floor, cameras
and lights are outside the named export collection and never enter the GLB.
Blender **5.2.2 LTS**, build `d13f752e3b9c`, glTF exporter **5.2.40**; export.py loads
`tools/assets/blender/export_settings.json`, selects the named collection and disables
skins/animations. Fresh saved-source export is byte-identical to the committed GLB.

Seven opaque, back-culled Principled materials, in exported surface order:

1. `harbour_hall_base_stone` — quiet grey-beige plinth and steps.
2. `harbour_hall_warm_render` — warm ochre civic walls.
3. `harbour_hall_limestone_trim` — pale surrounds, cornice, sills and pulls.
4. `harbour_hall_teal_metal` — restrained waterside frames, fascia and ridge cap.
5. `harbour_hall_slate_roof` — broad quiet blue-slate hip planes.
6. `harbour_hall_opaque_glazing` — dark closed glazing, no transparency/interior.
7. `harbour_hall_entry_amber` — small warm entrance kick panels.

Exact linear PBR values are in validation.json and author.py. No textures, embedded
images, material overrides, emission or runtime light nodes. No rig, clips or authored
LOD variants. Standard Godot automatic LOD/shadow mesh/compression settings are retained;
actual device/LOD silhouette review is pending, not a ratified budget.

## Prefab and collision

Saved `Visuals/Model` is an identity-transform linked GLB instance, not embedded mesh data.
Prefab UID `uid://mwj75ktxjny1`; model UID `uid://crp443cckseei`. Godot-generated node
identities and import/script sidecars are retained. There is no TSCN `.uid` sidecar:
the engine stores its UID in the scene header. A two-save load/pack/reload roundtrip
preserves bytes; a subsequent fresh-process load resolves dependencies and UIDs.

`Collision/Body` is one static-world body (layer 1, mask 0) with three simple shapes:

- `HallSolid`: 26.4 × 5.85 × 18.4 m box, centre (0,2.925,0). It follows the plinth,
  conservatively extending 0.2 m beyond the plain wall faces. It blocks the entire
  closed hall; window sills are cosmetic, not individual snag colliders.
- `EntryLanding`: 8.4 × 0.3 × 0.4 m box, centre (0,0.15,-9.4).
- `SmoothEntrySteps`: closed convex wedge, X ±4.2, Z -10.8 to -9.6, rising from
  Y=0 to Y=0.3. Slope **14.036°**, below ActorMotion's 45° floor limit. It meets
  landing and ground continuously. Visual treads differ from the slope by at most
  0.10 m; no individual riser can snag the actor capsule.

Roof, eave, frames and lintel are cosmetic; they do not enlarge solid collision.
No ground plane or square collider ships with the prefab. Test-only ground/capsule
shapes are created by the checker with no render geometry. World integration must
keep pedestrian/car routes outside this envelope and preserve the open square.

## Evidence and validation

[Hero](d05_harbour_hall_01-evidence/hero.png) ·
[Side](d05_harbour_hall_01-evidence/side.png) ·
[Entry detail](d05_harbour_hall_01-evidence/entry_detail.png) ·
[Gameplay overhead](d05_harbour_hall_01-evidence/overhead_47m_42deg.png).

All four are isolated Blender Cycles CPU renders, 32 samples, AgX, 1280×720,
RGB8 PNG compression 95, no dithering; each is below 400 KiB. All were visually inspected.
The side view was reframed to include the plinth; the hero/detail retain broad smooth
facade rhythms and steps. The vertical-down **47 m / 42° vertical-FOV** perspective
view shows a quiet, readable hip-and-ridge silhouette. It does not expose the entrance
or establish hall-plus-square orientation on its own; placement and canopy review
must preserve that cue. These are not Godot screenshots or gameplay visual acceptance.

[validation.json](d05_harbour_hall_01-evidence/validation.json),
[manifest.json](d05_harbour_hall_01-evidence/manifest.json) and
[final.log](d05_harbour_hall_01-evidence/final.log) retain lean measurements, checks,
SHA-256 payload hashes and final diagnostics. Scratch logs stay outside the repository.

- **9,064 source vertices; 17,736 triangles; 10,881 GLB vertices including splits.**
- **1 mesh / 7 surfaces; 0 degenerate source faces or exported triangles;
  0 non-manifold source edges.** Unit-length normals pass (max error <0.000001).
- Source/GLB/engine AABBs match the literal expectation within 0.001 m.
- GLB 461,524 bytes; fresh saved-source re-export byte-identical.
- Nine native physics overlap cases and a front ray pass. Front solid ray Z=-9.2 m.
- Production `ActorMotion.step` with capsule radius 0.35 m / height 1.8 m passes
  ascent and closed-entry stop, clear side bypass, and side-wall blocking in both
  AUTHORITY and REPLAY modes (144 fixed ticks per case).
  Entry end (0,0.300056,-9.550117), bypass end (14,0.000878,-0.000009),
  side-wall end (13.550787,0.000878,0). Both modes and two fresh processes match.
  This is isolated production-API physics equivalence, **not multiplayer transport proof**.
- Canonical production checks **PASS**: all 208 discovered GDScripts compile;
  formatting/lint pass; 17 Python tests; 149 GUT tests / 6,768 assertions;
  intentional negative-control failure detected. No known-failure exemptions used.

Initial editor normalization waited on a timer in an editor custom SceneTree and timed
out (exit 124); the timer/physics wait was replaced with editor process-frame startup,
and physics is now only run in runtime mode. Final normalization exited 0 and saved
stable UIDs, but emitted pinned editor-mode RID/ObjectDB shutdown leak diagnostics.
These remain explicitly recorded, not treated as a clean log. Final import exited 0
with only the existing MCP compatibility warning. Fresh runtime checks exited 0
without ERROR/WARNING diagnostics. No owner live editor/MCP process was used or changed.

## Exact reproduction

Run from the worktree root (Git Bash). Use fresh external check output directories.

```sh
NID=d05_harbour_hall_01
B="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
G="$(mise which godot)"
T="C:/tmp/ft/assets/$NID"
mkdir -p "$T"
timeout 900 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/author.py"
timeout 180 env ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy "$B" \
  -noaudio --background --factory-startup --threads 4 --python-exit-code 1 \
  --python "tools/asset_production/$NID/validate.py"
# validate.py opens the saved source, exports to $T/reexport and compares actual bytes.
timeout 300 "$G" --headless --path . --import > "$T/import-final.log" 2>&1
timeout 180 "$G" --headless --editor --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- --normalize \
  > "$T/prefab-normalize-final.log" 2>&1
timeout 180 "$G" --headless --path . --check-only \
  --script "res://tools/asset_production/$NID/check_prefab.gd"
timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- \
  --output "$T/prefab-fresh-final.json" > "$T/prefab-fresh-final.log" 2>&1
timeout 180 "$G" --headless --path . \
  --script "res://tools/asset_production/$NID/check_prefab.gd" -- \
  --output "$T/prefab-second-process.json" > "$T/prefab-second-process.log" 2>&1
timeout 60 "$(mise which gdstyle)" --max-line-length 100 --max-warnings 0 \
  "tools/asset_production/$NID/check_prefab.gd"
timeout 60 "$(mise which gdstyle)" fmt --check "tools/asset_production/$NID/check_prefab.gd"
timeout 1800 mise exec -- python tools/production_checks.py --output "$T/checks"
python "tools/asset_production/$NID/record.py"
```

`export.py` also runs independently on the saved .blend and accepts an export directory
after `--`. `record.py` combines external final receipts, checks exact second-process
agreement, and hashes every produced deliverable except its self-referential manifest.

## Remaining acceptance

1. Independent art/technical review of this exact candidate.
2. Separate .02 canopy production and combined mounting/visual checks; separate civic artwork.
3. Actual saved district placement, square/route fit, camera occlusion/aim, car movement/turns,
   collision at populated-world seams, multiplayer transport/admission/prediction.
4. Godot visual/lighting/LOD review, packaged build and sustained GPU/Deck performance.
5. Pinned headless editor shutdown diagnostics remain an integration/tooling limitation.

No world placement, route data, gameplay rule, shared brief, queue, progress or TODO
completion was changed. Bounded delivery does not claim full-world or target-device readiness.
