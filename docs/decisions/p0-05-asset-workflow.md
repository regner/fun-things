# P0-05 — concept-to-asset-to-world specification

Completed specification: 7 October 2026. Owner: Codex. Effort cap: one focused
documentation/verification session. This record closes the workflow documentation
task; it does not certify assets, final art choices or an export/import proof.

## Inputs and scope

Reviewed the [ratified product brief](../design.md), original asset guide,
[development](../development.md), [multiplayer](../multiplayer.md),
[repository guidance](../../AGENTS.md) and the scene/handoff plan in
[TODO.md](../../TODO.md). The working tree was clean at task start. No owned
gameplay scripts, scenes, models or asset tests exist for this task to exercise.

At initial authoring, P0-02/P0-04 drafts were not present on this branch, so the
specification used the ratified scope and scene starting points. During rebase onto
main at `b644931`, reviewed the completed P0-02 drafts and accepted P0-04
[art direction](../art-direction.md)/[city layout](../world-layout.md). Reconciled
this workflow with their reserved `art/source/` authoring subtree,
`scenes/world/sectors/` placement, entity/effect paths, prefab socket interfaces,
physics/presentation transforms and first-use derived-data fingerprints. The
Petrol & Coral direction and vertical perspective camera are accepted inputs;
asset-specific briefs and measured envelopes/settings remain future work.

## Result and acceptance map

The [expanded asset guide](../assets.md) is canonical. The
[handoff template](../templates/asset-handoff.md) supplies a per-asset brief/spec,
dependency mapping, acceptance and rejection log. The
[catalogue](../asset-catalogue.md) indexes those records and honestly has no assets.

| P0-05 requirement | Specification/evidence location |
| --- | --- |
| All seven handoffs name owner, evidence and rejection path | Guide: Owners and handoffs; template: Handoff acceptance and Change and rejection log |
| Sources outside runtime exports in a `.gdignore` subtree | Guide: Files, catalogue and provenance; required `art/source/.gdignore` created when sources arrive |
| Metres, axes, origins, collections and export membership | Guide: Units, axes, origins and export scope; S01 must prove orientation on a static and rigged fixture |
| Sockets, rigs, animation names and consumers | Guide: Sockets, rigs and animations; template tables preserve source-to-prefab mapping |
| Material/texture conventions, collision, bounds and LOD | Guide: respective sections; measured limits remain spike inputs; P0-04 supplies accepted provisional dimensions/camera |
| Catalogue and shared-source output consistency | Guide: Files, catalogue and provenance; record lists all outputs/consumers, index links records |
| Changed source updates outputs and affected prefabs/placements together | Guide: Reexport and change acceptance; preserve identity/ancestry/transforms, review unchanged consumers, commit complete changed set |

Preserved the existing project rule of Godot local -Z forward and documented its
deliberate difference from the usual +Z model-front convention. Blender +Y front
with glTF Y-up conversion is the proposed matching authoring orientation; S01
must independently verify front/right/up, sockets and rig behavior. No corrective
prefab transform or existing identity migration is introduced.

## Remaining decisions and proofs

| Follow-up | Owner | Closure evidence/task |
| --- | --- | --- |
| Scene/component/socket API paths and gameplay ID/envelope consumers | Codex | P0-02 draft paths are reconciled here; S01/S02/S04/S06 validate and P0-GATE settles remaining body/envelope choices |
| Asset-specific briefs and production refinement | Codex; Regner reviews direction changes | P0-04 direction/layout is accepted; S02/S04 actual-camera evidence and M1-C1 briefs refine the selected kit |
| Blender version/build/exporter, exact collection/skin/action/sampling/material/import settings | Codex | S01 pins settings and records static + rigged, repeated + inherited prefab roundtrips, reexport, clean import, open-editor refresh and saved identities/overrides |
| Actual camera, foot/car envelopes and route/connector dimensions | Codex; Regner reviews feel | S02/S04/S06 measurements update affected briefs before production acceptance |
| Renderer, LOD/texture/effect budgets and Deck performance | Codex; Regner owns device access/scope changes | S07/S08 and P0-GATE; 60 FPS at native 1280×800 remains required |
| Executable resource/source-link checks | Codex | P0-03 grows checks with owned fixtures; manual records are not an implemented validator |

Unproven items remain in their existing spike/production tasks. P0-GATE reconciles
the final contracts and measured evidence; P0-07 uses this workflow and S01/S02 evidence for art review.

## Verification and limitations

Reviewed requirement coverage against the P0-05 acceptance condition and all seven
planned handoffs, and checked Markdown links, template/index consistency, downstream
prerequisite references and whitespace. Rebase review also checked the P0-02 path,
socket, physics/presentation and bake-fingerprint contracts and P0-04 camera/layout
inputs; completed P0-02/P0-04 tasks remain removed from the active list. Consulted
official Godot model conventions,
import configuration/process and LOD guidance and Blender glTF action/export guidance;
links sit beside the relevant guidance. Stable/latest documentation is a reference,
not exact-engine/exporter evidence.

No engine/editor mutation, import, Blender export, gameplay/network run or Deck
performance check ran. Such checks need the owned S01/S02 fixtures and later proofs.
Only documentation changed; no scripts, engine scenes/resources, art outputs,
tool pins or vendor addons changed. P0-05 removal and downstream record references
are committed with this specification.
