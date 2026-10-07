---
name: art-review
description: Review Fun Things art assets, linked Godot prefabs and world placement against accepted concepts, Blender provenance and scene contracts. Use for requested art reviews or asset handoff audits; distinguish technical fixtures from production art and measured gameplay acceptance.
---

# Project art review

Review the requested asset, diff or handoff. Produce independently evidenced findings;
review alone does not authorize fixes, new art direction or production acceptance.
Resolve links relative to this skill directory.

## Establish scope and source of truth

Read [repository guidance](../../../AGENTS.md), the accepted
[art direction](../../../docs/art-direction.md) and
[world layout](../../../docs/world-layout.md), then the affected
[asset workflow](../../../docs/assets.md) and
[scene contracts](../../../docs/scene-structure.md). Find the asset's brief/handoffs
through the [catalogue](../../../docs/asset-catalogue.md); follow its source, export,
material, prefab, inherited-variant and placed-instance mappings in both directions.
Search actual consumers; a catalogue entry alone does not prove ancestry.

Record base/candidate revision, changed paths, intended use, producer/reviewer and
handoff stage. Separate accepted direction from proposed dimensions and unfinished
proofs. Read [S01](../../../docs/spikes/s01.md) for the bounded import/inheritance
route and its known failures, not as production art approval. Consult the
[product validation envelope](../../../docs/design.md#provisional-validation-envelope)
and [active tasks](../../../TODO.md) for outstanding owners/gates. Neutral technical
fixtures may use their own brief; do not reject them for lacking production detail.
Missing briefs or conflicting constraints are evidence gaps to resolve with the
owning handoff, not permission to invent an art or gameplay requirement.

## Inspect applicable review lenses

Mark unused systems not applicable with a reason. Missing evidence for an applicable
requirement stays pending; do not turn every planned feature into a defect.

- **Concept and style:** compare actual assets and views with the selected concept,
  silhouette families, smooth broad forms, restrained detail and Petrol & Coral
  hierarchy. Inspect geometry-based car/weapon recognition, actor/background contrast,
  roofs, conventional high-rises, signage and shadows. Name the reference and visible
  discrepancy; distinguish personal preference from a contract failure. Concept PNGs
  and their illustrative dimensions are not calibrated engine/material evidence.
- **Provenance and ancestry:** trace placed instance → prefab/inherited wrapper →
  imported GLB → handoff → committed Blender source, export collection and dependencies.
  Check authorship/license, source `.gdignore`, explicit outputs, sidecars, tools/settings,
  reverse consumers and source/export freshness. File existence alone proves neither
  a fresh export nor rights. Inspect unexpected embedded meshes, generated draw meshes,
  import suffix collision, detached models and copied vertex data. Visible 3D fixtures
  and mesh VFX also need Blender sources. Source edits require affected exports together.
  Preserve UIDs, node/inheritance identities and placed IDs. On the S01 pin use its
  supported wrapper-level appearance route; direct imported-child overrides have an
  observed identity failure. Test changed base/inherited scenes through save/reopen.
- **Gameplay camera and readability:** inspect actual vertically downward perspective,
  fixed-yaw captures at recorded height/FOV/near/far planes and native 1280×800, plus
  a useful overview. Compare matched lighting, renderer and states. Check foot/car
  motion, aim/held weapons, local player/target separation, HUD/minimap and camera-edge
  silhouettes. Test towers below, near and above camera height, follow transitions,
  clipping and visual occlusion without changing authoritative collision. S02/S04
  own final camera/envelopes. Provisional captures, concept art and S01's overview
  cannot close those gates; absence of actual camera evidence is not a visual pass.
- **Scale, pivots, sockets and rigs:** measure imported AABBs, datum and axes against
  the asset brief/tolerance in metres, +Y up and project -Z forward. Check unit roots,
  applied static transforms, winding/normals and documented asymmetry; avoid corrective
  prefab scaling/rotation that hides export faults. Inspect source markers → stable
  prefab-facing socket mappings and physics versus smoothed presentation consumers.
  For rigs check bind/rest alignment, shared bones/skins/weights, attachments, intended
  clips/durations/loop seams and animated/death bounds. Animation must not move the
  simulation root or decide gameplay. A rest-pose screenshot cannot prove attachments
  or clip behavior. Do not impose production socket paths on a documented neutral test.
- **Materials:** inspect stable slots, external remaps and intentional inherited
  overrides, shared-resource mutation, UVs/seams, channel/color-space conventions,
  normal orientation, mip/filter/compression and alpha/emission. Follow editable
  texture provenance and runtime outputs. Check contrast, shimmer, highlights and
  silhouette preservation under target lighting; uncalibrated palette swatches do
  not prove rendered color. No arbitrary texture/triangle budget is ratified.
- **Collision and routes:** compare intentional solid envelope with visual footprint,
  decorative overhang, ground contact, masks and required shape parentage. Inspect
  corners, seams, sidewalks/crossings, two-way turns, alternate routes, spawn/exit
  candidates and boundaries. Check saved placement, stable IDs and affected derived
  navigation/minimap/occluder revisions; do not introduce a second placement writer.
  Confirm behavior through actual movement/query APIs and affected separate-process
  multiplayer checks, including blocked exits and lifecycle changes. Static bounds
  expose mismatches, but neither bounds nor screenshots certify traversability.
- **VFX bounds and overdraw:** inspect lifetime, spawn/concurrency/debris caps, particle
  travel/animated bounds, camera-edge culling, transparent layering and target/road
  visibility during worst bursts. Require Blender provenance for mesh carriers,
  collision-free cosmetics and no presentation authority over damage/chains. Measure
  overdraw/cost under relevant bursts; a pretty keyframe is not load evidence.
- **LOD and culling:** inspect per-asset import settings or explicit source/output
  LODs, rationale and transitions at actual camera distances. Check silhouettes,
  normals/shadows, roof/road seams and maximum animation/effect extents. Visual
  culling must not stop simulation, chain propagation or routes. LOD is optional
  until measurement justifies it; do not prescribe streaming or global compression
  changes to solve an isolated defect.
- **Measured performance:** require build/source identity, engine, hardware/OS,
  renderer/API, quality/resolution, scenario, population/effect counts, role,
  duration/warmup and retained profiler/log evidence. Compare normal/burst/load
  cases with CPU/GPU frame and physics time, pacing, draw calls/primitives, memory
  and relevant overdraw. Use the current validation envelope and label provisional
  budgets. Desktop, headless or capped-FPS results do not certify sustained 60 FPS
  on Deck LCD/OLED, Gaming Mode, controls or packaged builds. Report unmeasured cost
  as pending, not an invented performance defect or a pass.

## Obtain evidence without disrupting authoring

Discover actual checks in [Mise](../../../mise.toml), repository tools and
[validation instructions](../../../docs/development.md#foundation-validation-tasks).
Use relevant checks, inspect their coverage and logs, and retain command, version,
exit status and diagnostics. Import is not all-script compilation; S01's resource
checker is specific to its fixtures. Do not extrapolate a clean asset-profile copy
to full-project plugin, gameplay, export or device compatibility.

Prefer suitable Godot MCP tools; inspect current editor state before mutations,
coordinate exclusive shared-editor/source access and preserve unsaved work. Save
mutation batches and compare saved diffs. If tools are unavailable/insufficient,
explain the fallback before using it. An authorized isolated copy with fresh CLI
processes can inspect resources without touching a shared editor; identify precisely
what that evidence establishes. Before later saves/playtests in an existing editor,
refresh external changes and close/reopen affected scenes. Headless import never
proves that another editor's open scenes are synchronized. Do not manufacture
screenshots, device access, measurements, successful checks or acceptance.

## Report a bounded verdict

Lead with actionable findings ordered by severity (P1 blocking the scoped handoff,
P2 substantive defect, P3 minor issue); reserve P0 for immediate critical impact.
For each give file and line/node/resource or source object, violated contract,
observed evidence and reproduction, impact, minimal correction/fix owner and retest.
Separate observed behavior, static inference, visual judgment and missing evidence.
Avoid repeating one cause as multiple findings; do not report speculative defects.

Then state reviewed scope/revision, checks actually run and evidence paths, applicable
coverage and limits, and each handoff status (`accepted`, `rejected`, `pending`, or
reasoned `not applicable`). Acceptance is explicitly technical/spike-only or
production. Reject observed failures; missing required evidence remains pending,
with the next bounded check and owning task. No findings means only that none were
found with the stated coverage. Review does not replace movement/load/device proof.
