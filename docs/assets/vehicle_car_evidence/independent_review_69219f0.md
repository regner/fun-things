# Independent three-car checkpoint review

9 October 2026. Reviewer: clean-context Codex/Sol, review only.
Candidate and observed HEAD: `69219f0655f0233a2a8de6d738029a3b7fcdef2a`.
Base: `9ff045f9c9ed14075a855bc9e0dc0266fc6936a8`.
Working tree was clean at entry. Producer: vehicle lead; concept approval owner: Regner.

## Findings and verdict

**No P0/P1/P2/P3 defect found that requires correction for the scoped first
source/import/preview checkpoint. Checkpoint: accepted, bounded to the evidence
below. Final production art and gameplay acceptance: pending.** This accepts a
reviewable checkpoint, not finished production vehicles or a production body choice.
No asset fixes were made.

The following are actionable continuation observations, not newly discovered
checkpoint defects or waived acceptance requirements:

| Status / owner | File or node and evidence | Next bounded action |
| --- | --- | --- |
| Final art pending / Astra art author, then Regner | All three `art/source/models/city_cars/car_*_a.blend`: `Body`, `Roof`, glazing and lamps. Compare each `*_inspection.png` and `*_game.png` with approved `01_latch_compact.png`, `02_crate_hatch.png`, `03_sable_sedan.png`. Colour families and the longer Sable bonnet/trunk survive; models retain a common angular cabin/front treatment. Latch lacks the concept's rounded compact envelope, Crate lacks its distinct round-lamp/front treatment, and Sable lacks its broad swept sedan surfaces/slim lamps. Native game views distinguish paint and length more strongly than the two short-car shapes. | Refine those family-defining broad forms in source and re-export together, retaining pivots/socket identities; repeat matched inspection/game views and seek owner model approval. This is the already declared unfinished silhouette/surface work, not rejection for missing final polish. |
| Surface polish pending / Astra art author | All three `Doors/Hinge*/DoorPanel*`; `*_doors.png` shows repeated tooth-like highlights along upper panel edges, strongest on Latch/Crate, also visible along closed Latch side. This is an observed shading issue; the captures do not isolate topology, normals or shadow contribution. | Inspect the source panel edge/normal treatment and compare under matched lighting before choosing a correction. Re-export affected sources and repeat open/closed captures. Do not assume a renderer-independent cause from these PNGs. |
| Playback acceptance pending / asset author and integrator | `scenes/previews/city_cars/*_preview.tscn/AnimationPlayer`: saved six-second looping `mechanical_demo` plus `RESET`. Captures sample rest and 2.5-second open poses; they do not show a complete moving cycle. No production per-door clip/controller is delivered or claimed. | In a later authorized private session, observe a full loop including wheel/steering motion and closure; check intermediate clearances and reset. Establish the per-door API only with the integrator's requirements. |

## Independent checks actually performed

No live Godot/Blender editor, shared MCP or workspace service was accessed. No new
worktree, capture run, import, re-export, engine save/reopen, gameplay test, commit,
merge or push was performed. Only this report was authored.

- Read `AGENTS.md`, `docs/workflows/parallel-art-production.md`,
  `.agents/skills/art-review/SKILL.md`, all three scoped car handoffs, evidence
  README, concept handoff/routing receipt and supporting art/assets/scene,
  S01, layout/catalogue, validation and TODO guidance. The owner-approved three-car
  scope and later Astra/high spatial authoring receipt are consistent. Initial
  geometry preceding that routing update is preserved history, not a new violation.
- Ran `git rev-parse HEAD`, `git status --short`, candidate/base name/stat diff,
  consumer searches and `git diff --check BASE CANDIDATE`; exit 0, no whitespace
  errors. Inspected saved wrappers/previews and editor/capture/export helpers.
  Runtime previews consume saved composition; authoring helpers are editor-only.
- Ran installed pinned `gdstyle 0.3.0 --version`, `gdstyle fmt --check
  tools/vehicle_assets/editor_author.gd tools/vehicle_assets/preview_capture.gd`,
  and `gdstyle --max-line-length 100 --max-warnings 0` on those same files.
  Exit 0: two files already formatted; no lint issues. Also inspected purpose
  comments and function spacing. This is scoped lint, not all-project compilation.
  `mise which gdstyle` returned the pin with a read-only tracked-config warning;
  direct binary invocation avoided requiring that state update.
- Ran an inline independent Python/NumPy GLB/resource audit, exit 0. Parsed all
  four GLB headers/chunks, buffer accessors, mesh indices, material references,
  node hierarchy/transforms and actual transformed vertices. All index ranges and
  attribute values checked were valid/finite. No skins, GLB animations, textures
  or images. Car roots are identity, ground bottom Y=0, front hinges/axles are
  at negative Godot Z. Source +Y forward/+Z up maps to Godot -Z forward/+Y up.
  Eight opaque source material names remain present; glass is intentional opaque,
  double-sided material with roughness approximately 0.42, not transparent glazing.
- That audit compared all fifteen wrapper socket positions to transformed GLB
  markers (within 1e-6 m), resolved every RESET/demo target, checked external
  UID/path agreement and unique per-scene node IDs in six deliverable scenes plus
  the authoring harness. No embedded draw meshes or editable imported-child
  overrides. Wrapper → GLB and preview → wrapper/stage links resolve. No inherited
  variants are introduced. Actual Godot imported mesh ancestry/save-reopen remains
  producer receipt evidence, not a rerun by this reviewer.
- Independently SHA-256 checked four source/export pairs against `reexport.json`
  and six saved scenes against `roundtrip.json`: all match the candidate bytes.
  Reviewed `stable-roundtrip.jsonl`, import checks and final capture logs/JSON.
  Matching receipts support freshness; byte-identical re-export and editor
  roundtrip are producer checks, not independent re-executions.
- Read all four saved sources in a private factory-startup background Blender
  process using an inline read-only `--python-expr`; no save/export/authoring calls.
  Successful command used `ALSOFT_DRIVERS=null /usr/bin/blender --background
  -noaudio --factory-startup --python-expr ...`; exit 0. Version 5.2.2 LTS,
  build `d13f752e3b9c`. Export membership matches each source record; unit scale 1,
  no nonunit object scales, nonpositive determinants or remaining modifiers in
  export collections. Inspected source hinge/axle hierarchy and marker poses.
  An earlier reviewer probe failed on a null material slot in the review expression
  and emitted sandbox audio diagnostics; the corrected successful probe filters
  empty slots. Neither event establishes an asset defect.
- Viewed all three accepted concept PNGs and all nine committed Godot PNGs via
  `view_image`. Independently checked PNG IHDR dimensions against capture JSON:
  all 1280×800. Final stdout logs identify pinned Godot
  `4.8.dev7.official.c971f93e7`, GTX1070/OpenGL Compatibility, with no new
  ERROR/WARNING/SCRIPT ERROR lines found. JSON reports rest hinges 0°, open hinges
  left -50°/right +50°, successful saves and fixed wrapper roots. These are
  retained producer capture outcomes, independently inspected rather than recaptured.

| Asset | Source members / triangles | Independent closed vertex size, metres X/Y/Z |
| --- | --- | --- |
| Latch | 58 / 10,104 | 1.8930 / 1.5400 / 3.4320 |
| Crate | 68 / 11,256 | 1.9130 / 1.6500 / 3.6820 |
| Sable | 67 / 11,116 | 1.9330 / 1.4400 / 4.2820 |
| Preview stage | 8 / 1,316 | Source-linked cosmetic floor; no collision |

Car vertex bounds agree with recorded source bounds within 0.002 m. Source read
triangle totals agree with GLB totals. Four axle-centred steer/spin pairs and
2/4/4 front-edge door hinges are preserved; panels/windows/handles and front-door
mirrors follow their hinges. Saved wheel spin targets local X and steering/hinges Y.
Only rigid visual descendants are animated. Door/steering endpoints match at the
loop boundary; wheel spin advances one revolution. Static path/key inspection
does not prove continuous rendered playback or swept collision clearance.

## Acceptance boundaries

Source/export/wrapper linkage and checkpoint inspection: **accepted** with the
coverage above. Accepted concepts remain the art target. Closed native game
captures use the saved vertical-down, north-up perspective camera at (0,47,0),
FOV42°, near/far 0.1/160; separate inspection captures show rest/open states.
Lighting is a shared saved preview setup, not the concept render's lighting or an
integrated city scene. Reported open bounds are transformed mesh AABBs; their
negative lower Y is not independently established ground penetration.

Final owner art approval, driver fit/versioned occupant contract, entry/exit queries,
collision/body/handling reconciliation, routes/contacts/spawning, lifecycle/network,
damage/wreck states and world integration: **pending**, owned by the relevant art
and external integration owners. No such absence is classified as a checkpoint
defect. Forward+ appearance, generated LOD transitions, integrated readability,
desktop load and later target-device performance: **pending/unmeasured**. A capped
Compatibility screenshot is not performance acceptance. Deck is a later delivery
target under the current validation envelope.

Skin/shared humanoid rig, textures/UV baking, VFX, inherited appearance variants
and world placement/collision changes: **not applicable to this rigid visual-only
checkpoint**. Bus/truck modelling and approval are outside review scope; their
concept PNG import sidecars in the diff do not imply production delivery. Existing
S04/gameplay consumers, main, project settings and shared plans are unchanged by
this candidate. No routine implementation-mirroring tests were added or run.
