# Independent S07 preparation review

Date: 7 October 2026. Reviewer agent: `/root`; model/profile: Sol 6.1
(`gpt-6.1-sol`), high effort. One bounded, clean-context technical review pass.

**Verdict: ACCEPT the documentation-only preparation candidate; no actionable
findings.** This does not accept capacity, a renderer/budget decision, or any
unexecuted gameplay/target gate.

Exact reviewed candidate: `f8b83d8738fe5a0a59a5f1820aec2072a77e8476`.
Explicit review base: `62e080000077f5d5b5551883b940aad0f4e2fde0`.
HEAD/base and clean status were confirmed before review. The diff contains only
`TODO.md`, `docs/spikes/s07.md`, `docs/spikes/s07-evidence/research.json` and
`docs/spikes/s07-evidence/document-checks.txt`. These substantive files remained
unchanged throughout this pass. This report is the sole repository write and is
left uncommitted for author retention.

## Contract and criteria assessment

Read the raw request and review constraints, AGENTS.md, relevant development/review
guidance, base TODO and the candidate diff, design scope/pins/budgets, world layout,
art direction, asset/source rules, scene composition/IDs, architecture ownership,
API admission/limits/lifecycle, multiplayer, accepted S01/S03 records and the latest
checkpoint. Conclusions below come from those contracts and fresh source inspection,
not adoption of the author's research conclusions.

1. **Capabilities — pass.** The archive/release records corroborate 4.7.2 stable
   and 4.8-dev7 as the current published development snapshot on the research date.
   G7 implements experimental dynamic mip residency, distinct from ordinary mipmaps
   and compression. Enablement/import/restart, disabled streaming/budget defaults,
   Compatibility exclusion and qualified Forward+/Mobile feedback support are
   correctly described. Newer changes do not update the installed pin. Loading,
   instantiation/tree entry, node deletion and referenced resource lifetime remain
   distinct; application-controlled object streaming is qualified rather than
   universally denied. Culling/LOD/instancing do not certify unloading or authority.
2. **Measurement method — pass.** Extent, density/object work, unique variety,
   resident bytes, active simulation and camera/player distribution are independently
   accounted for, including coupled extent/count growth. Saved two-sector calibration,
   six-block reference and one bounded growth axis provide a credible controlled
   sequence. Graphical host/client/standalone, four separate process views, fast
   driving/seams, bursts and off-camera outcomes are included. Build/content/tool
   identities, cold/warm runs, repeat variance, owner thresholds and stop rules are
   explicit. Proxy/missing subsystem and GPU-telemetry limits are honest; Deck memory
   domains are not added blindly. No measured Deck result or maximum is invented.
3. **Investigation and contracts — pass.** Attribution precedes one cheap intervention;
   streaming, pooling, batching and scheduling changes need demonstrated pressure
   and lifecycle proof. No manager/cache/procedural architecture is selected.
   Blender/GLB linkage, saved placement, inherited/import metadata and stable IDs
   survive the recommendations. Authority, collision/AI, global caps, current-state
   hydration, prediction and stale identity/revision fences remain requirements
   for future unloading/relevance decisions.
4. **Coordinates — pass.** Distance from origin/precision is a symptom- or
   extent-driven investigation axis. Documentation ranges are not measured project
   limits; no speculative origin shift or precision-build change follows.
5. **Ownership/completion — pass.** S07 sharpens the existing capacity/culling task;
   S06 retains topology, S08 exact exports/input and M1-D3 integrated acceptance.
   Later experiment ownership, effort/stops, durable results, conservative envelope,
   diagnostic recipe, canonical reconciliation and bounded follow-ups are specified.
   Growth does not enlarge six-block M1. Preparation leaves S07/P0-GATE open.
6. **Document integrity — pass.** Independently checked 85 local Markdown paths/
   anchors across both changed Markdown files at the exact candidate: zero errors.
   JSON parsed with duplicate-key rejection; refs/hash shapes were checked.
   Candidate/base `git diff --check` and substantive-file preservation checks passed.

## Independently sourced checks

Fresh official downloads were inspected in temporary storage. All **15/15 G7
source-file SHA-256s** match the candidate receipt. G7 is exactly
`c971f93e7e76b0ef919bf6009e7b868bea04db7f`. The installed executable's version-only
invocation independently returned `4.8.dev7.official.c971f93e7`; no project launched.

- [Official archive](https://godotengine.org/download/archive/),
  [dev5 introduction](https://godotengine.org/article/dev-snapshot-godot-4-8-dev-5/)
  and [dev7 release](https://godotengine.org/article/dev-snapshot-godot-4-8-dev-7/):
  release dates/snapshot identity, introduction and opt-in importer/restart context.
- [G7 streaming implementation](https://github.com/godotengine/godot/blob/c971f93e7e76b0ef919bf6009e7b868bea04db7f/modules/texture_streaming/texture_streaming.cpp),
  [resource](https://github.com/godotengine/godot/blob/c971f93e7e76b0ef919bf6009e7b868bea04db7f/scene/resources/streamed_texture.cpp)
  and [importer](https://github.com/godotengine/godot/blob/c971f93e7e76b0ef919bf6009e7b868bea04db7f/editor/import/resource_importer_streamed_texture.cpp):
  settings/startup, renderer/module gate, fallback and importer identity. Also read
  both streaming class XMLs, module registration, and both renderers' shader compiler/
  GLSL feedback branches. [Latest class documentation](https://docs.godotengine.org/en/latest/classes/class_texturestreaming.html)
  agrees with the capability description; immutable G7 remains the pin evidence.
- [Fresh stable tree](https://api.github.com/repos/godotengine/godot/git/trees/4.7.2-stable?recursive=1):
  complete, 15,212 paths, SHA `ed1daf0bf001b61586d9930840f2f1394092c079`;
  none match the receipt's four new-streaming path terms. This establishes the
  scoped API absence, not absence of all texture/object loading possibilities.
- G7 `Resource`, `ResourceLoader`, `PackedScene`, `Node` and `MultiMesh` XMLs:
  reference/cache lifetime, threaded-get blocking, scene instantiation, removal/free
  semantics and grouped visibility/lighting tradeoffs. The
  [background-loading guide](https://docs.godotengine.org/en/stable/tutorials/io/background_loading.html)
  corroborates the separation of loading and instantiation.
- Fresh [image import](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_images.html),
  [3D performance](https://docs.godotengine.org/en/stable/tutorials/performance/optimizing_3d_performance.html),
  [occlusion](https://docs.godotengine.org/en/stable/tutorials/3d/occlusion_culling.html),
  [mesh LOD](https://docs.godotengine.org/en/stable/tutorials/3d/mesh_lod.html),
  [visibility ranges](https://docs.godotengine.org/en/stable/tutorials/3d/visibility_ranges.html),
  [large coordinates](https://docs.godotengine.org/en/stable/tutorials/physics/large_world_coordinates.html),
  [profiler](https://docs.godotengine.org/en/stable/tutorials/scripting/debug/the_profiler.html)
  and [debugger](https://docs.godotengine.org/en/stable/tutorials/scripting/debug/debugger_panel.html)
  guides support the proposed distinctions and diagnostic candidates. Their moving
  stable/latest URLs do not establish exact-pin runtime benefit.

## Limits and later revision

No representative capacity experiment, streaming enablement/import test, renderer/
driver/export comparison, gameplay/network rerun, scene/asset authoring or shared
editor/Blender/service access occurred. All review subprocesses finished. Restricted
DNS initially failed; scoped read-only network access then succeeded. The stable
tree exceeded the first 3 MB cap and succeeded within an 8 MB retry cap. These are
review-environment events, not candidate defects or unverified source claims.

Physical LCD/OLED and real Steam routes remain explicitly DEFERRED. P0-GATE,
engine-input, user feel/readability, representative measurements and production
acceptance remain open; no access re-request, target waiver or desktop certification.

During this pass the coordinator reported accepted limited S02 desktop integration
at `fc6845fdd945df67d7e66b4dbbca7618eee4bd99`, followed by final integration base
`cc24b5e3b8732aa70c47633ab3f202b951e35bf9` with model-policy/profile wording.
Those later changes were outside this frozen review. The candidate's S02-pending
wording is accurate against its explicit base. The author must reconcile the later
limited desktop evidence and remaining S02 gates when rebasing. This verdict does
not automatically cover retention/rebase or any substantive final revision; an
exact final candidate will receive the requested renewed disposition.
