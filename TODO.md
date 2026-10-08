# Fun Things — foundations through the first playable milestone

Planning baseline: 7 October 2026. The project has engine/style configuration,
the Godot MCP Toolkit, isolated [S01 asset fixtures](docs/spikes/s01.md), a bounded
[S02 desktop fixture](docs/spikes/s02.md), an [S03 session proof](docs/spikes/s03.md),
a [bounded headless S03-R ENet result](docs/spikes/s03-r.md),
a [reviewed S04 car/body/ENet technical result](docs/spikes/s04.md),
an [accepted partial S05 authoritative chain result](docs/spikes/s05.md),
and an [accepted partial S06 saved topology/body-route result](docs/spikes/s06.md),
but no production gameplay or main scene.
This active work list retains remaining tasks and links completed work to evidence.
Periodic whole-plan/documentation checks are indexed in
[the checkpoint record index](docs/reviews/plan-checkpoints.md).

Phase zero establishes decisions, documentation, review skills, reproducible checks,
and small technical proofs. M1 builds the playable game using those results. A spike
closes with evidence and changes to documentation **and this plan**, not just code.

Use [repository guidance](AGENTS.md), [development](docs/development.md),
[assets](docs/assets.md), and [multiplayer](docs/multiplayer.md) as working contracts.
Assign an owner and experiment budget when taking a task. Remove completed tasks
and commit their removal together with the resolving changes; retain evidence in
decision/spike records and replace downstream prerequisite references with those records. Keep unresolved
findings as specific tasks. Do not silently turn prototypes into production systems.

## Product requirements and scope to settle

The required experience is a playful, irreverent city sandbox: top-down 3D with
GTA2-style camera and controls, quick readable action, forgiving arcade cars,
weapons, pedestrians, traffic, player vehicle entry/driving/exit, and car explosions
that can trigger nearby cars. Traffic does not need modeled people inside cars.
M1 includes custom art, a road minimap, shooting/explosion effects, host/join menus,
and audio settings. Multiplayer/store/platform dependencies need focused APIs.
**Confirmed:** M1 supports ENet for local/loopback/LAN testing and Steam for friends
playtesting over the internet, using the existing Steam app. Both use the same
session/gameplay contracts. Steam is required for that path; ENet works without it.
**Confirmed in P0-01 review:** Steam Deck LCD at native 1280×800 is the performance
baseline, with 60 FPS on LCD and OLED; graphics should be stylized, not realistic.
Deck controls and Gaming Mode validation are required. The user designated VCS's
existing AppID 5294580 and Windows/Linux depots 5294581/5294582 for this project.
The intended private Steam beta branch is `fun-things`. Live setup/access is
deferred to S03-S/S08; the current engine pin awaits the early Deck input proof.

Every visible 3D model comes from Blender, including blockouts, spike fixtures,
and mesh-based VFX. Commit sources and explicit GLB exports; scenes instance the
imports. No primitive/CSG draw meshes, copied embedded model data, generated render
meshes, or runtime rebuilding of the authored city. Collision shapes, navigation
and occluder data, shaders/particle behavior, debug overlays, and 2D UI/minimap
drawing are separate concerns. Import processing retains the Blender source link.

The [ratified P0-01 brief](docs/design.md) owns product scope, gameplay policies
and the provisional validation envelope. The table below summarizes scope;
the accepted [art direction](docs/art-direction.md) and [city brief](docs/world-layout.md)
own the starting style/layout; spikes still settle dimensions, tuning, toolchain and measured budgets.

| Area | Ratified first-milestone scope / remaining proof |
| --- | --- |
| Session | 1–4 players; authoritative listen server; host loss ends the match cleanly |
| Targets | Steam Deck LCD/OLED and Windows/Linux desktop; choose renderer and verify exact-engine exports/Gaming Mode |
| Connection | Required ENet local host/join and Steam friend lobby/invite joining; integration choice is a spike decision |
| Offline | Standalone sandbox using the same authoritative gameplay rules |
| City | One exterior district, roughly six connected blocks; loops, alleys, plaza, stunt/chain-reaction space |
| Weapons | Pistol, SMG, rocket launcher: distinct fire rates/range and hitscan/projectile behavior |
| Population | Simple wandering/fleeing pedestrians; lane-following cars; bounded replenishment |
| Art | Two car silhouettes; shared pedestrian rig/variants; reusable building, road, sidewalk and prop kit |
| Presentation | Readable stylized forms, restrained detail, playful signage, fixed daytime lighting |
| Menus/audio | Host, Join, Settings, Quit; Master/Music/SFX levels and mute, saved locally |
| Performance | Confirmed 60 FPS on Steam Deck LCD/OLED at native 1280×800; ratify frame pacing, simulation/memory/network and load budgets |

The Steam integration package/version remains to be selected. Prove actual Steam
gameplay transport and relay behavior; lobby success alone cannot satisfy friend
playtesting. Record the existing AppID and tester access/build route during phase
zero; no new Steam app is needed. Additional stores/platforms get capabilities and
adapter contracts now, and real integrations when selected. Record unsupported
targets honestly. A session selects ENet or Steam before host/join and keeps that
transport until teardown.

Defer missions, police/wanted systems, interiors, passengers, detailed civilian
simulation, building destruction, procedural cities, persistent worlds, host
migration, and production matchmaking unless a scope decision explicitly adds them.

## Phase zero — foundations

P0-01 was ratified on 7 October 2026; evidence and review decisions live in
[the product brief](docs/design.md). The user approved scope with budgets provisional,
explicitly deferred unknown live Steamworks setup to its proofs, and left the engine
choice open for early S08 Deck evidence. These deferrals are owned below; completed
scope work is removed from this active list.

P0-02 draft output is recorded in [architecture](docs/architecture.md),
[scene structure](docs/scene-structure.md), and [API contracts](docs/api-contracts.md).
These define owners, concrete proposed paths, typed boundaries, identities,
admission/cancellation/lifecycle, provisional limits and future contract tests.
No gameplay is implemented or proof claimed. Spikes refine the drafts and P0-GATE
settles them; remaining proof/tuning choices stay with the tasks below.

P0-04 was accepted for continued work on 7 October 2026. The [art direction](docs/art-direction.md),
[city brief](docs/world-layout.md) and [complete concept review](docs/concepts/p0-04/review.html)
retain the selection evidence. Regner considered the concepts sufficient to continue;
actual fixture captures/paintovers and overhead weapon readability move to S02/S04,
with production design refinement in M1-C1. Dimensions remain provisional for
S02/S04/S06 and measured cost remains S07/P0-GATE work.

P0-06's project GDScript review skill and independent dry-run evidence are recorded
in [the review-skill completion record](docs/reviews/p0-06.md). The skill reads the
P0-02 contract drafts when reviewing affected systems; remaining gameplay proofs
are tracked below.

P0-07's project art review skill and independent isolated-prefab exercise are recorded
in [the art-review evidence](docs/reviews/p0-07.md). It covers source/scene/style and
measured acceptance while keeping unfinished camera, movement, load and Deck gates
explicit. The dry run is a technical review proof, not production asset acceptance.

S01's bounded Blender/GLB/linked-prefab workflow is complete in
[the evidence record](docs/spikes/s01.md), with two committed source/export fixtures,
repeated instances, wrapper-level inherited material tuning, source reexport,
asset-profile clean import and editor close/reopen. Direct imported-child identity
churn is a rejected alternative on the unchanged engine pin; full-project plugin
and editor diagnostics, Deck compatibility and production art/gameplay acceptance
remain outside that result. S01 is removed from the active task list with its
resolving change.

P0-03's minimum foundation tooling is complete with the combined
[S01 asset evidence](docs/spikes/s01.md) and [S03 runner/script evidence](docs/spikes/s03.md#integration-validation).
Pinned formatting/lint, explicit compilation of every owned script, focused
resource/source-link checks and a bounded two-process runner can rerun the fixtures
and retain useful failure evidence. Manual purpose-comment/spacing review remains
required; preserving formatter tooling, CI and broader coverage belong to M1-D1.

S03's minimum ENet session proof is complete on 7 October 2026; its
[evidence and limitations](docs/spikes/s03.md) retain the code, real-process results,
held-window recovery and split-subset reordering/loss decision. The fixture remains
isolated. Full admission errors, reset/seat/collision lifecycle, floods, capacity,
production codecs and gameplay belong to M1-A/D and the remaining spikes. This does
not close any Steam/Deck proof. Combined P0-03 tooling acceptance is recorded above.

### Contracts to validate with spikes

Use the [canonical scene draft](docs/scene-structure.md) for saved paths, prefab
interfaces, sockets, placement, IDs and pre-tree simulation setup; S01/S06 validate
its resource/topology assumptions. Use the [API draft](docs/api-contracts.md) for
session/provider/platform boundaries, commands, lifecycle, replication, presentation,
settings and their acceptance matrix. [S03 evidence](docs/spikes/s03.md) covers ENet;
S03-S must prove Steam independently.
Keep revised contracts in those documents rather than duplicating them in this plan.

### Asset handoffs and workflow evidence

The [asset workflow](docs/assets.md) now owns the seven handoffs, named owner roles,
acceptance/rejection paths and source/export/prefab/placement conventions. Use its
[handoff template](docs/templates/asset-handoff.md) and
[catalogue](docs/asset-catalogue.md) as assets arrive. The
[P0-05 record](docs/decisions/p0-05-asset-workflow.md) records specification completion
and alignment with the P0-02 contracts and accepted P0-04 direction.
[S01 evidence](docs/spikes/s01.md)
pins and proves the bounded tool/settings workflow; a specification is not production
asset acceptance.

### Deferred orchestration configuration

- [ ] **P0-PROFILES — Create Paseo profiles from observed session requirements (configuration DEFERRED).**
  Owner: delegated workflow worker; orchestrator coordinates readiness and review.
  **Requirements/proposal independently reviewed; live configuration/launch stage DEFERRED.**
  See [proposed bundles and deferred install/launch plan](docs/workflows/p0-profiles-proposal.md)
  and [session evidence/coverage](docs/workflows/p0-profiles-evidence.md), with the
  [independent review](docs/workflows/p0-profiles-review.md). This resolving
  proposal stage leaves the task open for later authorized configuration, safe launches,
  final inventory and next periodic revisit. No live profile/configuration change or
  representative launch has run. Readiness was established at the third checkpoint: accepted
  S02 implementation and completed independent code/visual reviews now supplement
  the earlier documentation/network-preparation sessions. Inventory remains empty;
  readiness comes from those outcomes, not the inventory or elapsed time. Propose
  Sol lead/review and bounded Astra specialist routing separately. This does not
  authorize installation or claim that post-policy launches/capabilities are validated.
  [Eighth read-only assessment](docs/reviews/plan-check-2026-10-08-08.md#profile-assessment)
  retains zero installed profiles and four reviewed INERT proposals. Accepted DOC10/11
  Sol MEDIUM/HIGH, stopped S02 Sol HIGH/HIGH and S08 preparation plus accepted stopped Linux observation HIGH/HIGH
  add evidence for direct ownership, finite stops, exact-candidate review, proportionate
  lossless retention, staged-input/runtime-manifest distinctions and release entrypoint/assertion limits. No installed-bundle
  launch/effective permission proof or necessary new specialist follows. Configuration
  and representative launches remain deferred; no extra coordinator/Astra is needed.
  Do not manufacture a specialist session to unlock configuration. Revisit with full
  checkpoints (normally6–8 substantive integrated workstreams or milestone transition),
  or earlier meaningful
  supported routing/capability/permission drift, and before any later authorized
  configuration. Docs/retention/reviewfix/lifecycle work alone does not advance cadence;
  no per-workstream model inventory. At that revisit reconcile historical pending S03-R/lease prose in
  `docs/workflows/p0-profiles-proposal.md`, `docs/workflows/p0-profiles-evidence.md`
  and the exact notes in `docs/workflows/p0-profiles-evidence/proposed.patch.json`
  with accepted scope and current routing/lease/retention requirements. Preserve original
  dated samples; remove the current next-revisit dependency on a manufactured specialist.
  The same workflow owner supplies a dated supplement and independently checked notes
  before authorized configuration; this is no new parallel profile task.
  Needs: [checkpoint/profile baseline](docs/reviews/plan-check-2026-10-07.md#profile-baseline)
  and [second assessment](docs/reviews/plan-check-2026-10-07-02.md#profile-assessment)
  and [third assessment](docs/reviews/plan-check-2026-10-07-03.md#profile-assessment)
  plus those later sessions' prompts, settings, outcomes, permission/tool limitations
  and repeated operational friction, reconciled with supported provider capabilities.
  Review evidence by actual task category, model/effort, tools/capabilities, permission
  needs and recurring launch/routing problems. Propose a small useful set with notes
  explaining intended use, exclusions and tradeoffs; avoid bundles without demonstrated need.
  Apply the [orchestrator model policy](.agents/skills/paseo-orchestrator/SKILL.md#model-policy-workers-subagents-and-reviewers):
  Sol 6.1 medium/high leads workspaces, effort chosen for task; Luna 6 high remains an
  option for very simple delegated subtasks/reviews. Astra is limited to necessary
  bounded visual/spatial/modeling specialist subagents with explicit question,
  output, validation boundary and proportionate effort/budget, returning results to
  the Sol lead. A 3D/art/map mention alone cannot route whole research/planning,
  implementation, broad review or orchestration to Astra. Assess and validate lead
  versus specialist routing separately; no automatic ultra or broad-access default.
  Cost-aware routing preserves independent review and required validation.
  Done when: a later checkpoint records readiness evidence; proposed notes and exact
  provider/model/effort/mode/features bundles are independently reviewed; configuration
  follows then-authorized workflow; safe representative launches materialize each
  bundle and demonstrate intended routing/capabilities, retained approval boundaries
  and no silent model fallback. Record tests, limits, final inventory and next profile
  revisit. Do not create/configure profiles, schedules or services in this checkpoint.

### Documentation checkpoint follow-ups

These are documentation work, owned by a delegated documentation worker with
independent review; they do not reopen completed proofs or require hardware access.
Assign a named worker before starting. Finish before P0-GATE uses the reconciled guides.
P0-DOC1 and P0-DOC2 are complete. The [tooling reconciliation](docs/reviews/p0-doc1.md)
and [proof-ownership reconciliation](docs/reviews/p0-doc2.md) retain accepted evidence,
current fixture scope, historical observations and active owners for unproved cases.
P0-DOC3's README networking disclaimer is resolved in `62e0800`.
P0-DOC4's six-guide S02/S07 and profile-stage reconciliation is complete in
[the completion/review record](docs/reviews/p0-doc4.md); full S02, measured S07,
profile configuration and all target/production gates remain open.

P0-DOC5's accepted S03-R tooling/consumer and delivered-profile discovery is
complete in [the completion/review record](docs/reviews/p0-doc5.md). Only the
three guides and resolving references changed; full S02/S03-R, profile
configuration/launch, Steam/Deck/P0/production gates remain open.

P0-DOC6/7 and P0-DOC8/9 remain complete in their linked resolving records;
[DOC8](docs/reviews/p0-doc8.md) and [DOC9](docs/reviews/p0-doc9.md) were accepted at
exact6c36c12 with separate resolving1691424/dbce2f9. DOC10 and DOC11 are complete in
[their](docs/reviews/p0-doc10.md) [separate records](docs/reviews/p0-doc11.md), resolving
02aa254/4169a44 on accepted64bd46b. The new stopped S02 acceptance discovery below
is a subsequent bounded supplement; completed DOC1–11 are not reopened.

- [ ] **P0-DOC12 — Discover exact accepted stopped S02 operational disposition.**
  Owner: one root-assigned direct Sol MEDIUM/HIGH documentation worker; sole independent
  Sol HIGH reviewer, serialized with conflicting documentation reviews/writes.
  Files: exactly `docs/spikes/s02-drawability.md` and
  `docs/spikes/s02-drawability-evidence/README.md`. Their terminal review/retention
  paragraphs still require future exact-final review without discovering its now
  accepted completion. Add a dated exact-final supplement; preserve those paragraphs
  as historical and all original protocol/criteria/observations/negative evidence.
  Needs: accepted exact `a311c576d25a1554471c8381e1620136b76d9b23` and its reachable
  strict JSON note/report in `refs/notes/paseo-orchestration`; see
  [eighth identity ledger](docs/reviews/plan-check-08-evidence/accepted-audit.json).
  Sole reviewer81d6afb9 accepted the stopped record, not full positive criteria:
  three automatic callbacks/frames0/1/2/nonblank2112×1320 PNG, can_drawfalse, actual
  viewport differs from declared1280×800, focusfalse/input suspended. Keep auxiliary
  source-index/client-snapshot/CUA receipt limitations, original failures and full gates OPEN.
  No engine/surface/query/technical rerun, evidence rewrite or canonical guide sweep.
  Done when: both files discover exact stopped-record ACCEPT and full-criteria FAIL,
  original complete report/notes/retention and next changed-condition STOP boundary;
  static links/identity/history/LF/whitespace checks and exact independent review pass.
  Remove this item with its resolving supplement commit, link completion from P0-GATE,
  and finish before that gate uses the reconciled records. No new experiment is assigned.

- [ ] **P0-DOC13 — Reconcile stopped S08 acceptance and failed release entrypoint discovery.**
  Owner: one ROOT-assigned direct Sol MEDIUM/HIGH documentation worker and sole
  independent Sol HIGH reviewer; serialize conflicting doc writes/reviews.
  Files: exactly `docs/spikes/s08.md`, `docs/spikes/s08-linux-observation.md` and
  `docs/spikes/s08-linux-evidence/README.md`. Add a dated supplement discovering
  accepted exact1229782/base93da622 and completed full review/retention; label the
  original future `--script` asset card as the attempted failed/unproved route,
  preserving predeclarations, preparation/R1, original terminal requests and raw failures.
  Needs: exact accepted Git revisions and full report/JSON note identities in
  [delta ledger](docs/reviews/plan-check-08-evidence/accepted-delta-122.json);
  report31950 bytes/SHA4d0e1a4b863411b80ceb7fa071332a96362ba395974ee72b25ac38baff5602b2.
  Distinguish exact TPZ/import/export0/static46-member/22-map positives from ignored observer/
  missing-role exit1/no receipt/never-started ENet and STOP. Discover existing S08
  ownership of supported entrypoint and RELEASE assert-side-effect prerequisites;
  do not invent a working recipe or authorize fixture changes/retry/production work.
  Done when: all three files identify stopped-record ACCEPT/retention MET and full
  asset/ENet/Steam/both-OS/device gates OPEN; accepted notes/report remain reachable,
  history/identity/link/LF/whitespace checks and exact independent review pass.
  Remove this task together with the resolving dated supplements; link completion
  from P0-GATE before reconciled-record use. No new technical owner or experiment.

## Phase-zero technical spikes

Each spike gets a short `docs/spikes/<id>.md`: question/hypothesis, alternatives,
minimum fixture, tool versions, proposed effort cap, experiment, measurements/logs/
captures, decision, limitations, production acceptance cases and resulting doc/TODO
changes. Start with a proposed **1–2 focused days per experiment**, adjusted before
work; this is an effort cap, not a delivery promise. If inconclusive, record the
next bounded question and whether it blocks M1. Do not expand into full feature
implementation. Save editor mutations before playtests; preserve unsaved work.

- [ ] **S02 — GTA2-style foot controls, camera and aiming.**
  **Desktop technical fixture reviewed; full S02 acceptance remains OPEN.**
  [Bounded operational drawability record](docs/spikes/s02-drawability.md): one native
  Wayland observation produced automatic callbacks/pixels, but drawable-status and
  exact viewport criteria failed; stopped, saved main restored, full acceptance open.
  Exact stopped record `a311c576` is independently ACCEPTED; full positive criteria FAIL:
  automatic frames0/1/2/nonblank2112×1320 PNG, can_drawfalse, focusfalse/input suspended.
  Next operational card requires a genuinely changed authorized surface/output condition
  and named root grant; otherwise retain STOP. Native focus/physical-key/user-feel
  validation follows usable interactive access, not an identical Wayland retry.
  Coordinate through the orchestrator and reuse the retained fixture.
  Deck cases are deferred for unavailable hardware; desktop 1280×800 views do not
  prove Deck input/performance or ratify subjective feel. Keep full S02 open.
  Needs: [ratified brief](docs/design.md), [accepted art/city brief](docs/art-direction.md)
  and tiny Blender fixture; S01 settings can refine it.
  Question: which height/FOV/framing and control/aim choices deliver the desired feel
  with the confirmed vertically downward perspective camera, including buildings
  below, near and above camera height?
  Minimum: walk/turn/aim/shoot in one corner/alley fixture; evaluate fixed camera yaw,
  rooftops/obstruction, target readability, input focus loss and selected device support.
  Retain actual-camera captures for paintovers; refine held-weapon silhouettes/aim
  readability against the accepted concepts. S04 repeats the camera evidence while driving.
  Include Deck controls and 1280×800 readability; early S08 resolves the engine input
  blocker before handheld evidence can be accepted.
  Start with GTA2 turn/forward/back controls; an alternative needs a deliberate
  product decision. Decision: camera/control contract, actor/collision/aim envelope,
  playtest evidence and feel targets. No finished animation or weapon system required.
  Desktop exploration: [S02 fixture and evidence](docs/spikes/s02.md) supplies a
  provisional 47 m/42° keyboard corner harness. Native focus revalidation, physical-key
  playtesting and user feel remain pending; handheld/early S08 and dependent gates stay open.

- [ ] **S03-S — Steam integration, friend connection and transport proof.**
  Needs: [S03 boundary/fixture evidence](docs/spikes/s03.md) and
  [existing-app record](docs/design.md).
  Owner: Codex (proof/setup record), Regner (Steamworks access).
  **Preparation recorded, final Steam proof DEFERRED (7 October 2026):** Regner
  reports no multiple Steam accounts/testing access. Resume the two-account,
  separate-machine/network cases only when those facilities become available.
  [Preparation evidence](docs/spikes/s03-s.md) identifies bundled 4.23/SDK 1.65,
  isolated Linux class registration and source mode/default-channel mismatches;
  integration selection, native cancel/drain and live app/access remain unproved.
  Next bounded compatibility experiment is specified there; no vendor/engine pin
  or four-channel/ordered-unreliable contract change is implied. Deferral does not
  satisfy P0-GATE or dependent Steam acceptance; keep this task open.
  One bounded [compatibility design/probe](docs/spikes/s03-s-compatibility.md)
  records exact singleton Sockets API lane/metadata/ownership limitations,
  finite synthetic counterexamples and copied registration; native delivery and
  lifecycle remain unobserved. It stopped before peer/native machinery; no adapter,
  five-lane setting, integration or contract change is selected. Same compatibility
  owner: Codex; root chooses whether to commission exact upstream peer-revision
  evidence or a separately bounded native-boundary design using the saved criteria.
  No implementation expansion is implied. Network proof still needs external access;
  full S03-S remains OPEN.
  Before the network proof, verify app type/release state, distinct authorized
  testers/package entitlement, depot OS/package inclusion and launch settings;
  confirm/create the intended `fun-things` private branch and record its access route.
  Live setup is unknown and was explicitly deferred from P0-01 by the user.
  Compatibility/access research can proceed using the completed S03 boundary;
  no new app is required.
  Question: which pinned integration works with our exact Godot engine and supports
  Steam lobbies/invites plus actual gameplay traffic across friends' networks?
  Minimum: initialize the existing app, create/join one friend lobby and exchange
  the same tiny admitted baseline/intent via a real Steam multiplayer peer, using
  distinct authorized accounts on separate machines/networks without port forwarding.
  Inspect connection/relay diagnostics, native API/export compatibility, transfer
  modes/channels/limits and cleanup after one canceled attempt. Keep the fixture small.
  Decision: integration/SDK/native-library pins, account/peer mapping, lifecycle and
  proven networking route, plus private install/access recipe. Record failures as
  blockers; ENet exchanged through a lobby is not the required Steam transport.
  Full invitation races and gameplay acceptance belong in M1-A/D.

- [ ] **S03-R — Networked on-foot responsiveness.**
  Needs for desktop/ENet: [reviewed S02 controller/envelope](docs/spikes/s02.md#reviewed-desktop-handoff)
  within its provisional assumptions and [S03 evidence](docs/spikes/s03.md).
  Bounded technical result accepted at `ae48eb3`; prior implementation workspace
  archived after integration and saved editor relocation. No active S03-R writer or
  lease is assigned. Root assigns a Sol lead and serialized fixture lease for remaining
  work; original S02/S03 resources stay immutable. No duplicate responsiveness task.
  Final responsiveness decisions need S02 human feel/target evidence and S03-S's
  real Steam route. Desktop/ENet can proceed with explicit target assumptions and
  rerun affected cases after S02 choices; fixed-step S02 does not prove prediction replay.
  Question: does the actual foot controller meet the feel target over the selected network envelope?
  Minimum: two processes walking/turning/aiming under representative latency/loss,
  repeated through ENet and Steam;
  measure local response and correction behavior. Try minimal shared-rule prediction
  only if needed. Decision: foot interpolation/prediction/reconciliation requirements,
  limits and evidence; independent of the vehicle prediction choice. Required for M1-A2.
  [Accepted bounded ENet technical result](docs/spikes/s03-r.md) retains headless two-process
  controller response, convergence, collision, expiry/resync and teardown evidence;
  [Independent technical review](docs/reviews/s03-r-b87f889.md) closed its scoped
  P2; **full S03-R remains OPEN.**
  Next: measure predeclared owned visible response/camera/aim and remote presentation
  continuity with a drawable fixture and human feel review. Keep synthetic physics
  latency, drawn response, stationary convergence and prediction correction distinct.
  If that evidence warrants prediction,
  commission a separately bounded trial: predeclare how newest held intent per
  host tick maps to numbered client steps/acknowledgements, including repeated held
  values, supersession, contact restoration, bounded history/overflow/resync and
  replay side-effect exclusion. Keep the actual S02 movement rule as sole owner;
  do not assume one acknowledged sequence equals one simulation step. Require
  matching-tick correction and adverse convergence evidence, then real Steam and
  target/user acceptance under existing gates. Headless timing cannot close these.

- [ ] **S04 — Arcade car physics and network response.**
  Needs for desktop/ENet: [S02 desktop actor/camera envelope](docs/spikes/s02.md)
  within its scoped assumptions and [S03 evidence](docs/spikes/s03.md).
  Bounded desktop body/ENet implementation and evidence: [S04 record](docs/spikes/s04.md),
  [source handoff](docs/assets/s04_kit.md) and [body/seat contract](docs/spikes/s04-contracts.md).
  Bounded technical handoff ACCEPTED and integrated at
  `2370ad1c182b46e51f5dc4c6b6ab6157819e84b0`; full S04 remains OPEN. Both body
  candidates passed the flat-track comparison. CharacterBody3D is the recommended
  next technical candidate, not ratified product body/handling/dimensions/prediction.
  The sole independent Sol HIGH reviewer closed P2 producer fresh-motion admission
  and P3 mask naming; complete exact-final review/handoff is in the Git note on
  that revision under `refs/notes/paseo-orchestration`. Original physics p95
  97/269/401 ms and corrected normal/adverse 248/380 ms are separate observations,
  not drawn latency, physical input, human feel or prediction corrections.
  Prior direct lead `4b965847-a374-47da-aa0e-2800adaebc4f` and S04 workspace
  `wks_f739d0d8cb771a1d` are archived after integration and saved editor relocation.
  Current lease UNASSIGNED; no active S04 implementation candidate or next authoring
  allocation. Root assigns the next direct Sol lead, serialized lease and bounded budget.
  Next: drawable owned car response/camera/target/roof evidence and Regner physical
  input/focus/handling/controls review, final dimensions/turning and independent
  car prediction decision. If evidence warrants a permitted local-step trial,
  predeclare host-tick/held-intent/contact/history/correction expectations and
  side-effect exclusions before replay machinery; stop/report substantial scope.
  The prior bounded window attempt had can_draw=false and zero actual drawn
  receipts; do not repeat renderer repair or infer visible response from physics.
  Finish with S02 feel/target and S03-S Steam evidence; rerun affected rows if
  provisional actor/camera choices change. Full S02/S03-R closure is not required
  for separately bounded desktop preparation. Use [S03-R's metric/held-intent
  lessons](docs/spikes/s03-r.md#unavailable-graphical-evidence-and-stop-boundary)
  without importing a foot-prediction choice. Steam/device gates remain deferred.
  Use a Blender car fixture.
  Question: which simple body/control approach gives fun handling and tractable replication?
  Minimum: compare a small kinematic/custom dynamic candidate on one track, fast
  steering/sliding/braking and a wall contact; repeat host/client under latency/loss
  through ENet and Steam before settling the responsiveness decision.
  Compare VehicleBody3D only if useful. Do not assume cross-peer physics determinism.
  Decision: body/handling/recovery approach, car prediction needs, dimensions/turning
  envelope and seat/control contract. Specify the full seat race/disconnect/exit
  matrix for M1-B1 rather than building it here. Confirm the draft's no seated
  firing/reloading policy in the feel review before P0-GATE.
  Specify passive replica-body configuration and physics-phase pose capture for the
  selected body; disabling gameplay scripts alone must not leave engine physics active.
  Verify seated resync preserves the player/seat/equipment while reauthorizing input.

- [ ] **S05 — Authoritative explosion-chain feasibility.**
  Needs: [S03 evidence](docs/spikes/s03.md) and a minimal vehicle/damage fixture
  using the [reviewed S04 technical body/source](docs/spikes/s04.md#bounded-recommendation-and-next-question).
  Accepted partial bounded experiment at exact
  `754a0b501fe705c93675ff09b43d5bfca201cd94` on base `c8096b5`, explicitly renewed by
  sole Sol HIGH reviewer `770f9536-788e-4348-b335-86224c24e5fa`; P3 resolved/no new
  findings. Full S05 remains OPEN under provisional collider/visual/handling policies.
  Independently reviewed partial technical result: [bounded S05 record](docs/spikes/s05.md),
  [new fixture contract](docs/spikes/s05-contracts.md) and
  [full review](docs/spikes/s05-evidence/review/report.md) and
  [raw evidence](docs/spikes/s05-evidence/README.md). Full S05 remains open.
  The accepted direct Sol lead added only the minimum authoritative damage/life
  owner in new saved scenes; original S02/S03/S04 sources/resources are unchanged.
  Remaining bounded acceptance: authored explosion presentation exercising eight
  cosmetic slots with drawn receipts under a separately named drawable lease;
  current evidence proves eight token reservations/four drops, not visible effects.
  [Provisional source preparation](docs/spikes/s05-effect-preparation.md) adds one
  provisional new Blender carrier/explicit GLB only; Godot import, saved presentation
  and actual eight-effect drawable/saturation/live-versus-hydrated gates remain pending.
  Actual public API/ENet host/live/settled-late health0/0/100, retired-ShotId negative,
  twelve-car144visits/4 per tick, normal queue5/46ticks and pressure queue12/tick41
  are accepted finite outcomes. Occupant sentinel is not an admitted player; only
  settled wreck hydration before input/no history is proved, not during-chain journal.
  Regner ratifies provisional range/obstruction/delay/occupant/wreck policies;
  rerun affected spacing/contact rows after final S04/S02 dimensions. Use only the
  reviewed bounded contracts; full joining/reset/sustained load remains
  M1-B3/M1-D. S05 stays open; no P0/S07/production/Steam/device closure.
  Full S04 feel/dimensions are not prerequisites for this scoped preparation,
  but do not ratify blast spacing or production clearance from the technical kit.
  Rerun affected spacing/contact cases after final S04/S02 decisions.
  Question: how do we order and bound damage/chain events without duplicate outcomes?
  Minimum: three cars, near/far spacing, one duplicate event and wreck-state hydration.
  Estimate peak work and choose blast range/obstruction, chain delay/order, occupant
  outcome, wreck/collision lifetime and live-versus-historical presentation behavior.
  Decision: host-owned damage/explosion contract, event IDs and per-tick/queue/effect
  bounds, including duplicate ShotId rejection after damage-cache retirement.
  Extend the small fixture with a bounded 12-car burst to prove reserved chain work
  completes despite only eight cosmetic explosion slots; retain queue/work peaks and
  off-camera outcomes. Full joining races and sustained capacity loads belong in
  M1-B3/M1-D.

- [ ] **S06 — Shared city topology, navigation and minimap.**
  Needs: [S01 pipeline evidence](docs/spikes/s01.md), [S02 actor/camera envelope](docs/spikes/s02.md),
  [reviewed S04 technical dimensions](docs/assets/s04_kit.md#measured-technical-geometry)
  and [accepted district brief](docs/world-layout.md).
  Accepted PARTIAL bounded saved two-sector experiment at exact
  `7fb302ba2829966c9a687a12a7f00d09ce6a7824`, base `6c36c12`, in [S06](docs/spikes/s06.md),
  [contract](docs/spikes/s06-contracts.md), [source handoff](docs/spikes/s06-source-handoff.md)
  and [raw evidence](docs/spikes/s06-evidence/README.md). Sole fresh Sol HIGH reviewer
  `0f8ba889-b2e4-47be-bcbb-6c8ccf23cf76` explicitly ACCEPTS exact FINAL partial,
  R1 finite ROAD width P2/R2 evidence index P3 CLOSED; same-note condition MET.
  Actual S02 crossing477 ticks/7.95 s and two actual S04 opposing legal LEFT turns
  721 ticks/12.0167 s each cross X=0 once, without contacts/outside dense sampled
  source footprints. All four map arms/seam agree; actual saved stale+1 m/explicit
  rebake, missing/duplicate/revision/corrupt-map and INF/NAN/zero/negative ROAD-width
  API negatives are retained. This satisfies S07's technical saved-topology dependency
  within the provisional planar envelope, not full S06 or representative capacity.
  Full S06 remains OPEN. Final S04 dimensions/turning/exit and S02 feel/camera
  ratification remain open; larger-footprint/FOV geometric sensitivity is not actual
  changed-body physics/drawn/user approval. Rerun affected actual clearances afterward.
  Question: which authored representation supports lanes, sidewalks, seams and road-map drawing?
  Minimum: one intersection split across two saved sectors; one person takes a
  sidewalk/crossing route, one car makes a legal turn, and minimap roads align at
  the seam. Compare sidewalk graph/navmesh choices and lane graph/curves for cars.
  Validate stale derived data. Scene placement owns geometry/transforms; topology
  references it and owns connectivity, avoiding an independent layout writer.
  Decision: representation, stable IDs/layers, host AI/controller APIs and bake/update
  workflow. Specify bounded blockage/junction/stuck/wreck recovery for M1-C3.

  Remaining: actual drawn camera/layout/crossing/minimap readability and Regner feel
  decisions, affected actual body/contact/legal-turn/seam checks after final S02/S04
  choices, and M1-C3 integration/checks of specified bounded blockage/contested
  junction/stuck/wreck recovery. Full S06 remains OPEN; no production traffic or
  renderer/streaming/map-maximum decision.

- [ ] **S07 — Map capacity, top-down culling and growth headroom.**
  Owner: Sol-led capacity-spike worker; Regner ratifies scope/budgets. Assign a named
  experiment owner and normally 1–2 focused days per experiment at launch.
  [Researched preparation and method](docs/spikes/s07.md) is documentation-only;
  representative capacity measurements remain unexecuted. S07 is the single owner
  of the map/content envelope and diagnostic/organization recommendations.
  Needs for representative experiments: [S01 pipeline evidence](docs/spikes/s01.md),
  reviewed S02 desktop camera/controller within its scoped assumptions (final feel/
  handheld gates remain open), real S02 actor/S04 car envelope, S06 saved seam/topology
  and relevant S05 chain/effect load. Exact7fb302b partial S06 now supplies saved
  source-linked technical topology/seam/actual-body routes within its provisional
  planar envelope; drawn readability/final dimensions/recovery remain S06/M1-C3 gates.
  Accepted754a0b5 proves finite chain work and
  token reservations only; actual source-linked drawable effects/saturation and
  live-versus-hydrated receipts remain S05 work, not a representative presentation
  cost substitute. Capability research/run-sheet preparation can
  proceed earlier; stand-ins cannot certify missing gameplay or residency costs.
  [Eighth checkpoint readiness/options](docs/reviews/plan-check-2026-10-08-08.md#readiness-and-next-trigger)
  distinguishes stopped drawability from accepted S08 preparation and exact1229782
  stopped observation/full asset-ENet gates OPEN, alongside limited S07 static preparation. No experiment
  is allocated by this plan; diagnose limits before simple interventions, and select scene/asset structure only from evidence.
  Physical LCD/OLED and real Steam cases remain DEFERRED with S08/S03-S availability;
  desktop results name their hardware and cannot select Deck budgets/renderer or
  certify native 1280×800/60 FPS. P0-GATE/engine-input/feel/production gates stay open.
  Question: what practical envelope supports the current district and progressively
  larger authored layouts at named extent/density/variety/population/camera/views?
  Minimum: controlled saved imported two-sector baseline, six-block reference load,
  then one bounded growth axis; graphical host/client, four separated views, rapid
  driving/seams, bursts and off-camera outcomes. Retain CPU/GPU/physics percentiles,
  pacing, render/content/resident costs, loading/traversal and lifecycle stability,
  relevant AI/query/navigation/network costs and last passing/first failing axis.
  All visible 3D stays source-linked Blender/GLB in saved authored composition.
  Decision: tested envelope/headroom and limiting axis; simplest supported culling/
  LOD/texture/sector configuration or no change. Diagnose before optimizing; actual
  unloading/streaming/pooling/batching require measured need and lifecycle proof.
  Growth experiments do not expand the ratified six-block M1 city.
  Done when: accepted experiment record contains identities/capacity table, named
  target gaps, scene/asset recommendations, reproducible profiling/escalation guide,
  selected decision and bounded owned follow-ups; update canonical guides and TODO
  together. S06 owns topology, S08 exact exports, M1-D3 integrated target acceptance.

- [ ] **S08 — First-target export and service compatibility.**
  One separately commissioned [isolated Linux release observation](docs/spikes/s08-linux-observation.md#actual-stopped-observation)
  acquired/verified exact templates and exported the unchanged S01/S03 closure.
  The first asset invocation returned S03 `missing role`/exit1, so it STOPPED;
  asset runtime and exported ENet are NOT passed. Static package membership is
  distinct from runtime resolution. Full S08 and all existing gates remain OPEN.
  Bounded [desktop static preparation and next Linux observation card](docs/spikes/s08.md)
  records exact installed engine/native bytes, published matching templates and the
  missing installed-template/preset/access gaps. Preparation stops before exports;
  Accepted exact `93da622` remains PREPARATION after R1 staged-input/runtime-manifest
  correction. Exact `122978243dba25b3fb5d8d90fc50ffb1a468ecf5`/base93da622 is
  ACCEPT_STOPPED_EVIDENCE, sole Sol HIGH reviewer40c83e6a, full report/retention MET:
  temporary exact TPZ acquisition/member hashes, scratch import/release export exit0
  and static46 PCK members/22 logical resource mappings pass. The exact first exported `--script`
  invocation ignored the observer and ran unchanged S03 boot without role: exit1,
  no S08 receipt. ENet/proxy/host/client never created; STOP/no fix/re-export/retry grant.
  Static membership does not prove asset runtime semantics. Prior lead076a388a,
  reviewer40c83e6a and workspacewks_aa2a7ef710b90059 are archived/directory removed;
  S08 follow-up UNASSIGNED/no active S08 implementation. No shared lease used or relocation.
  Next bounded static preparation under this SAME S08 owner must identify a supported
  exported observer entrypoint and resolve the independently reported RELEASE proof
  limitation in `tests/fixtures/s03/replication.gd:40`: state-changing `apply_journal`
  is inside debug `assert`. Future release ENet baseline/journal/resync health70
  expectations require explicit mutation execution plus independent assertions;
  an assert-elided pass cannot prove them. This is not the missing-role failure's cause.
  Any S03 immutable-fixture change needs a distinct scoped ROOT grant and exact review;
  no source fix or runtime retry is allocated here. Preserve original S03 proofs/failures.
  A distinct [saved-entrypoint follow-up](docs/spikes/s08-release-entrypoint.md#actual-private-authoring-stop)
  is ACTIVE UNACCEPTED under lead488b6000/workspacewks_e2ba2fe7704a8fa6, base0c84f01.
  Its granted single private editor authenticated but STOPPED at an invalid readiness
  probe; unchanged toolkit authentication diagnostics are also retained. No source
  mutation/new S08 resource/S03 fix or release phase occurred. Required entrypoint,
  fixture fix and asset/exported ENet outcomes remain OPEN; no editor retry inferred.
  Full asset loading/exported ENet and stronger Steam-uninstalled/stopped evidence,
  both selected OS and device/account gates stay OPEN; stronger environment unavailable/
  uncommissioned. No global install/shared editor/Blender/display/Steam/PID/service query.
  Needs: [ratified target/pin record](docs/design.md) for early input/template checks;
  [S01 pipeline evidence](docs/spikes/s01.md), [S03 evidence](docs/spikes/s03.md)
  and S03-S for the complete proof. Owner: Codex (proof), Regner (device access).
  **Device cases DEFERRED (7 October 2026):** Regner reports no Steam Deck access.
  Resume Gaming Mode/input/native-init, performance and suspend proofs when the
  required LCD/OLED devices become available. Keep native 1280×800, both models,
  60 FPS/controller/Gaming Mode constraints and the provisional engine decision;
  specs/public docs/desktop checks cannot pass these cases. S03-S's two-account
  Steam cases are also deferred, with [preparation/access limits](docs/spikes/s03-s.md).
  Ungated desktop preparation may continue; S08 and dependent acceptance stay open.
  Early input evidence settles the engine decision deliberately left open in P0-01.
  First: minimal exported Deck Gaming Mode input/native-extension initialization
  test, exact templates and candidate engine choice for the dev7 controller regression.
  When LCD/OLED devices become available, record OS/client/driver/power versions;
  choose the exact engine/template pair from the proof and update the pins/docs together.
  Do this before S02 handheld validation; Desktop Mode alone cannot close it.
  Question: can the exact toolchain package the selected model/renderer/service path?
  Minimum: one imported fixture exported on each selected OS, an ENet connection
  without Steam installed/running, and a Steam connection between authorized accounts.
  Check templates/native dependencies, intended export exclusions and Steam app/
  depot/launch settings. Reuse S03-S network evidence where applicable; prove the
  private test package can be installed/launched through Steam by a test account.
  Verify the selected `fun-things` branch/build and preserve existing VCS delivery;
  repo IDs/recipes do not prove live setup or account access.
  Include Deck LCD/OLED built-in controls, native 1280×800 readability, offline and
  suspend/resume outcomes. Prefer native Linux; document/prove any Proton fallback.
  Decision: supported-target matrix, export recipe and capability/failure behavior.
  Record missing hardware/access as unresolved evidence; full gameplay acceptance is M1-D4.

- [ ] **P0-GATE — Review the foundation evidence and revise the milestone plan.**
  Needs: [ratified brief](docs/design.md), [ownership](docs/architecture.md),
  [scene](docs/scene-structure.md) and [API](docs/api-contracts.md) drafts,
  [accepted art/city brief](docs/art-direction.md),
  [foundation tooling evidence](docs/spikes/s03.md#integration-validation),
  [art-review evidence](docs/reviews/p0-07.md),
  [GDScript review evidence](docs/reviews/p0-06.md),
  [P0-05 workflow record](docs/decisions/p0-05-asset-workflow.md),
  [S01 pipeline evidence](docs/spikes/s01.md), S02,
  [P0-DOC1 reconciliation](docs/reviews/p0-doc1.md),
  [P0-DOC2 reconciliation](docs/reviews/p0-doc2.md),
  [P0-DOC4 guide reconciliation](docs/reviews/p0-doc4.md),
  [P0-DOC5 discovery/consumer reconciliation](docs/reviews/p0-doc5.md),
  [DOC6 accepted S04 guide reconciliation](docs/reviews/p0-doc6.md),
  [DOC7 stopped compatibility discovery](docs/reviews/p0-doc7.md),
  [DOC8 partial S05 tooling/review discovery](docs/reviews/p0-doc8.md),
  [DOC9 partial S05 contract/consumer reconciliation](docs/reviews/p0-doc9.md),
  [S03 fixture boundary](docs/spikes/s03.md#fixture-and-boundary),
  [completed S03 proof](docs/spikes/s03.md), S03-R/S03-S and S04 through S08,
  [DOC10 partial S06 tooling/review discovery](docs/reviews/p0-doc10.md) and
  [DOC11 partial S06 topology/source reconciliation](docs/reviews/p0-doc11.md),
  and P0-DOC12/13 exact stopped S02/S08 acceptance discovery before reconciled-record use.
  S07 supplies the documented capacity envelope, limiting axes, organization and
  diagnostic decisions; research alone leaves representative/target gaps open.
  Done when: critical design/feasibility assumptions required to begin M1 are resolved;
  the user ratifies scope, chosen art/layout and camera/control choices against
  concepts/spike evidence; implementers settle API/scene/source contracts and budgets.
  Record decisions in `docs/decisions/`, update canonical guides and this TODO, and
  identify prototype code to discard or deliberately productionize. Review skills
  and minimum checks work. A failed proof means a specific follow-up or deliberate
  scope revision; production acceptance is not a phase-zero requirement.
  Steam transport/integration feasibility and tester access are required evidence;
  successful ENet tests cannot close an unresolved Steam proof.

## First milestone — implementation

All M1 tasks follow P0-GATE. Gameplay can initially use accepted Blender fixture
imports while final assets are produced; final acceptance requires the ratified
custom art/content. Add production tests with each rule/lifecycle change. Art
families proceed from their relevant approved contracts alongside M1-A/B, without
waiting for unrelated gameplay systems.

### M1-A — Playable session and player foundation

- [ ] **M1-A1 — Production session service and main-menu flow.**
  Needs: [S03 evidence](docs/spikes/s03.md), S03-S/S08 decisions.
  Build both providers, Steam lobby/invite adapter and Host/Join/Settings/Quit
  scenes with loading/readiness/roster, actionable errors, cancel, leave and retry.
  Include Standalone entry and in-match leave/settings/host-reset requests, following
  the ratified brief; only host/standalone may reset, including when dead.
  Offer local-network and Steam friend sessions; route manual endpoints, friend/
  overlay invites and launch requests through the same join/cancel lifecycle.
  Done when: baseline/admission/compatibility and bounded teardown are correct;
  unreachable/full/incompatible games, unavailable Steam and host loss return to a
  usable menu. ENet remains available without Steam; close stale peers/lobbies from
  canceled callbacks, including invites received while loading or in a match.

- [ ] **M1-A2 — Player simulation, input, camera and replication.**
  Needs: M1-A1 and S02/S03-R decisions.
  Implement the chosen foot controls/aim, collision, one local rig, remote
  interpolation and foot prediction if required. Keep rules shared across offline,
  authoritative simulation and permitted replay. Add safe spawn/death/respawn lifecycle.
  Done when: distinct players move/aim independently; input expiry/focus loss work;
  convergence meets the selected envelope. Standalone play uses the same rules.
  Match owns a reset coordinator: preserve admitted peers, restore initial player
  state and rehydrate before input; reject old-match commands and preserve saved
  placement. Extend this same transition with each later dynamic gameplay owner.

- [ ] **M1-A3 — Settings, audio buses and persistence.**
  Needs: P0 API decisions; can run alongside M1-A1/A2.
  Implement Master/Music/SFX levels and mute, defaults, validated local load/save,
  live preview and settings access from menu/in-game UI. Apply settings at startup.
  Done when: values survive restart, invalid/missing data recovers, controls work on
  selected input devices and changing audio does not pause or mutate shared gameplay.

- [ ] **M1-A-GATE — Verify the multiplayer shell in real builds.**
  Needs: M1-A1 through M1-A3.
  Two exported processes independently walk/collide, late-join and leave/rejoin with
  one rig each; cancel/retry and host-loss/error flows clean up. Validate selected
  offline mode, host/standalone reset with admitted peers retained, audio persistence
  and latency response. Review logs and owned-script
  checks; retain evidence before extending the shell.
  Run the shared lifecycle through both providers: ENet with Steam unavailable and
  Steam with distinct accounts/networks, using friend joining/invites. Inspect the
  real Steam traffic route; lobby success alone is insufficient.

### M1-B — Arcade vehicles, weapons and destruction

- [ ] **M1-B1 — Vehicle gameplay and authoritative driver transitions.**
  Needs: M1-A-GATE and S04 decision.
  Implement chosen handling, throttle/reverse/brake/steering/handbrake, contacts,
  stuck/rollover recovery and selected car replication/prediction.
  Done when: players enter/drive/exit; simultaneous claims, blocked exits, death,
  disconnect and car destruction follow the seat contract. NPC-to-player control
  transfer has one authoritative simulation owner; player input ownership never
  grants client physics authority. Preserve the ratified parked-car policy after
  abandonment; resuming traffic AI requires a recorded product change.

- [ ] **M1-B2 — Weapons, health, damage and respawn.**
  Needs: M1-A-GATE and combat/API decisions; can run alongside M1-B1.
  Build the ratified weapon list with stable definitions, equip/fire/reload/ammo
  rules, authoritative hitscan/projectile outcomes, pedestrian/player/car damage,
  and coherent death/respawn state. HUD consumes owned state.
  Done when: weapon behavior is distinct and readable; rates/ownership are validated,
  stale commands cannot fire after transitions and late joins hydrate current state.

- [ ] **M1-B3 — Car explosions, wrecks and chain reactions.**
  Needs: M1-B1, M1-B2 and S05 decision.
  Implement threshold damage, bounded exactly-once blast propagation, chosen
  obstruction/falloff/delay, occupant outcomes, wreck collision and cleanup.
  Done when: clustered cars chain and distant/protected cars follow the blast policy;
  no cycles/duplicate damage; collision/lifecycle completes before dependent state
  is published. Offscreen chains work; joining during/after one receives correct
  wreck/health state without replaying historical explosions. Register combat,
  seats, rockets, chains and wreck cleanup with the existing Match reset transition;
  reset while driving/firing restores initial dynamic state and clears old work.

- [ ] **M1-B4 — Shooting/explosion feedback and vertical-slice review.**
  Needs: M1-B2/B3 event contracts; effects/audio can develop alongside those tasks.
  Add muzzle flash, impact/tracer/projectile feedback, explosions/smoke/sparks and
  bounded cosmetic debris using Blender mesh carriers where meshes are needed.
  Source/license sound for weapons, hits, explosions, engine/tires, footsteps, UI
  and music/ambience; retain originals, edits and notices. Mix buses and bound voices.
  Done when: both players can walk, shoot, enter/drive/exit and cause visible chains;
  replay/duplicate packets do not repeat effects or sounds. Effects preserve aim,
  road/minimap readability and chosen performance limits.

### M1-C — Custom city, population and minimap

- [ ] **M1-C1 — Produce the ratified custom art families.**
  Needs: P0-GATE; pipeline/style/camera/dimensions for each family.
  Produce reusable building types/landmark, roads/junctions/sidewalks, props,
  player/pedestrian rig and animations, car variants/wrecks, weapons and VFX carriers.
  Refine the accepted concept shapes and overhead weapon presentation with S02/S04
  camera evidence; source handoffs include final gameplay-camera views/paintovers.
  Use the documented handoffs and art review for each accepted prefab.
  Done when: the content catalogue links concepts, `.blend`, exports, import settings,
  reusable scenes and previews; reexport/save/reload preserves ancestry/placement.
  Families can run in parallel with distinct source/prefab ownership and M1-A/B.

- [ ] **M1-C2 — Assemble the authored district in saved sectors.**
  Needs: accepted M1-C1 road/building/prop subsets, S06 topology and
  S07 documented capacity/organization decisions (see [brief](docs/spikes/s07.md)).
  Instance individual building scenes repeatedly; compose the ratified district,
  loops/sidewalks/intersections/alleys/landmark, stunt/chain space, safe spawns and
  boundaries. Implement selected culling configuration and rebuild derived data.
  Done when: placement survives reexport/reopen, actor/vehicle/camera clearance is
  proven, sector seams connect and actual gameplay-camera views remain readable.
  Record actual density/asset variety/residency against S07 assumptions; expanded
  experimental layouts are not production scope.

- [ ] **M1-C3 — Host-owned pedestrians and traffic.**
  Needs: M1-A2, M1-B1/B2, S06 decision and an accepted M1-C2 route fixture.
  Use actor/vehicle command APIs for wandering/fleeing pedestrians and lane-following
  cars; add bounded spawn/replenishment, crossing/junction/blocked-route/stuck policies,
  damage/death and wreck avoidance. Cars need no visible occupants.
  Done when: pedestrians stay on sidewalks except sanctioned crossings; cars make
  legal road turns and recover from obstruction; NPC-to-player vehicle transfer,
  sector routes, distant players, late joins and offscreen gameplay remain coherent.
  Population reset restores initial descriptors under Match, clears old AI/replenishment
  work and stays within caps without rewriting city placement.

- [ ] **M1-C4 — Road minimap and local HUD integration.**
  Needs: S06 topology contract and M1-A2; final alignment uses M1-C2.
  Draw roads from the selected city data with the local controlled-entity
  position/orientation marker; additional markers require a product decision.
  Define map scale, rotation, bounds and sector data lifetime.
  Done when: intersections/seams match world roads at both walking/driving speeds,
  late-join/map load works, markers track the local controlled entity and HUD state
  comes from gameplay owners. No separately maintained minimap street layout.

### M1-D — Integration, fun tuning and private review builds

- [ ] **M1-D1 — Complete production validation tooling and CI.**
  Needs: [foundation tooling evidence](docs/spikes/s03.md#integration-validation); grows alongside production implementations.
  Extend style/compiler/resource/source checks to all owned code/assets; add the
  preserving formatter wrapper if needed, meaningful gameplay tests, production
  network scenarios and local/CI parity. Exclude vendor addon rules and retain logs.
  Done when: checks fail on actual contract violations, including unused scripts,
  and run reproducibly without broad diagnostic suppression or implementation-copy tests.

- [ ] **M1-D2 — Integrated playtests, reviews and feel tuning.**
  Needs: M1-B4 and M1-C1 through M1-C4 accepted content/behavior.
  Use both review skills; test several players, camera transitions, aim, collisions,
  rapid driving/slides, readable spectacle, exploration routes, menu/focus/controller
  flows and audio mix. Record player feedback and specific changes.
  Done when: the agreed arcade feel criteria are met in windowed play; the district
  supports varied traversal and playful chain/stunt situations; review findings and
  gameplay defects are fixed or explicitly scoped out by the user.

- [ ] **M1-D3 — Capacity, adverse-network and performance acceptance.**
  Use [S07 methodology/results](docs/spikes/s07.md) for content identities, distinct
  capacity axes and diagnostic baselines; repeat with actual production content.
  Needs: integrated M1-A/B/C behavior and M1-D1 runner.
  Test selected player/population capacity, far-apart views, sustained traffic and
  effect/chain bursts on named hardware. Measure frame/physics times, draw calls,
  memory, bandwidth, queue/replay work and response/correction behavior.
  Exercise delay/jitter/loss/duplicates/stale identities, slow admission, host stalls,
  invalid intent, seat/lifecycle races, reset while driving/firing or joining, and
  changing collision through production APIs. Verify retained peers, new revision
  hydration, cleared history/effects/queues and unchanged authored placement.
  Run shared gameplay scenarios through both ENet and Steam; verify each provider's
  transfer modes/channels, payload limits and observed behavior independently.
  Done when: ratified budgets/convergence hold, limits stay bounded, authoritative
  state survives adverse delivery and real-process logs contain no new errors.
  Culling never disables required simulation; additional optimization needs evidence.

- [ ] **M1-D4 — Export and deliver private milestone review builds.**
  Needs: M1-D1 through M1-D3 and S08 target recipe.
  Clean-import/save/reload representative inherited assets; export with exact
  templates, packaged build/protocol/content identity and intended exclusions.
  Exclude authoring sources, tests, captures and development MCP tooling.
  Done when: each selected target/transport passes packaged launch/render/input/audio/
  settings/network checks and the promised external-network route. Record versions,
  hardware, results and unavailable evidence; retain builds, logs and known limits.
  Deliver the Steam build on the existing app's `fun-things` private beta branch
  and verified access route;
  verify friends can install/update, launch, invite/join and play across networks.
  Record build/depot/branch IDs and retain a rollback build. ENet remains usable for
  local testing. Public store launch/certification remains a separate later task.

- [ ] **M1-GATE — User review of the first playable milestone.**
  Needs: M1-D4.
  Done when: the ratified capacity can host/join a custom Blender-authored district,
  explore on foot/in cars, use the agreed weapons, encounter sidewalk pedestrians
  and road traffic, and cause car explosion chains; roads appear on the minimap;
  shooting/explosion feedback is readable; audio settings persist; menus/failures/
  leave/retry and host/standalone reset work. Require the agreed feel, performance
  and multiplayer evidence,
  ENet local testing and Steam friend playtesting on the existing app, plus the
  selected offline/target promises. Current docs describe shipped behavior.

## Parallel work and dependency checkpoints

Current ROOT-supplied coordination at held accepted LOCAL main1229782: all prior
workspaces/leads/reviewers, including S08 lead076a388a/reviewer40c83e6a/workspace
wks_aa2a7ef710b90059, are archived and removed. S02 exacta311c576 stopped record
is ACCEPTED/full positive criteria FAIL; S08 exact93da622 preparation and exact1229782
stopped evidence are accepted, full asset/ENet/target criteria OPEN. Shared Godot
authoring lease UNASSIGNED/no shared writer. S08 used no shared lease; none returned
and no operational relocation required. The stopped S02 restored main483496/16 saved
no-unsaved receipt remains time-specific ROOT-accepted evidence, not a fresh query.
ROOT releases this checkpoint's sole fresh HIGH review and holds main1229782 through
handoff; ROOT alone integrates/archives. No surface/PID/service query or allocation
by this checkpoint.

ROOT now assigns ONE ACTIVE UNACCEPTED isolated S05 source-asset preparation: Sol6.1
HIGH auto-review worker92400a44-fc12-400a-a0d0-126e7f8f984e, workspace
wks_437a9484cd5db686 / `s05-source-linked-effect-preparation`, accepted base1229782.
It owns only NEW Blender source/explicit GLB files and its own isolated Blender CLI
processes for one stylized technical explosion carrier. No outputs or technical
acceptance adopted; no shared Godot/Blender GUI/display/editor/PID/service/Steam
lease/query or actual-effect runtime/drawability test. Concrete future Godot operations
must be reported before ROOT grants a writer lease. ROOT additionally commissions
read-only private editor/port/auth/registry/log-cache/connector-route capability
inspection only; no isolation support proof or editor/process/config/vendor/global
service launch grant. One-writer is per shared instance/MCP/source, not global Godot
serialization; verified isolated workspace editors may operate in parallel under
confirmed ports/routes/process/resource isolation. Existing S05 stays sole task owner/
full OPEN; its provisional private ports remain editor16650/runtime16670/LSP16015/
DAP16016/debug16017, with read-only capability planning and no private editor launch grant.

Alongside S05, ROOT assigns ACTIVE UNACCEPTED S08 release follow-up to sole Sol6.1
HIGH lead488b6000-b152-4bee-8a52-28febe9c1fe2, workspace
wks_e2ba2fe7704a8fa6 / branch `s08-release-entrypoint-enet`, accepted base/held LOCAL
main0c84f01f2a0c817a5c6851a3a360e193a5f846d8. It owns the release-compatible saved
asset receipt entrypoint, narrowly authorized existing S03 assertion-side-effect fix,
and one bounded isolated addon-free Linux release asset/ENet follow-up after separately
granted private authoring and committed protocol. Provisional private ports are
editor17650/runtime17670/LSP17015/DAP17016/debug17017. No shared editor lease or private
editor launch grant yet; concrete source-supported isolation/connector request precedes
launch. No outcome or technical acceptance adopted; full S08 remains OPEN.

Current readiness: bounded S04 source/body/admission/ENet handoff is independently
ACCEPTED and integrated at `2370ad1`; P2/P3 are closed and full S04 stays open.
Prior direct Sol HIGH lead `4b965847-a374-47da-aa0e-2800adaebc4f`, workspace
`wks_f739d0d8cb771a1d`, branch `s04-desktop-enet-cars`, are archived by Paseo after
saved/quiescent editor relocation to main. Root's complete `2370ad1` note retains
historical assignment, review/integration and relocation receipts. No active S04
candidate or new S04 authoring allocation. S05 exact754a0b5 is accepted and
integrated as a PARTIAL technical result; full S05 remains OPEN. Lead
`50c01e86-3164-4592-a48b-8181b3275d63`, Sol6.1 HIGH auto-review, workspace
`wks_42b1f3912dacdb26` / `s05-authoritative-chain-fixture` and sole reviewer
`770f9536-788e-4348-b335-86224c24e5fa` are archived via normal Paseo lifecycle,
directory removed after saved main-editor relocation. Operational lease RETURNED;
historical S05 authoring lease UNASSIGNED after return. S06 exact7fb302b/base6c36c12
is now independently ACCEPTED PARTIAL, sole Sol HIGH lead7bad34e7 and reviewer0f8ba889;
full S06/drawn/final dimensions/feel/actual recovery remain open. No active S06
candidate or new authoring allocation. S06 workspace `wks_7908651972db6fe3`,
lead7bad34e7 and reviewer0f8ba889 are archived
via normal Paseo lifecycle, directory removed after saved main-editor relocation.
Historical S06 operational lease RETURNED; authoring UNASSIGNED, no active S06 candidate
or new allocation. Root's time-specific external `/tmp/s06-editor-relocation/receipt.json`
and readback are retained in exact7fb302b `root_receipts`: old386156 saved/graceful
quit, separate HOST absence before sole pinned main426974,16 saved tabs/no unsaved,
bytes of all2,390 tracked FILES per checkout stable/10 preexisting vendor CRLF-LF
differences preserved,61 resources/64 UID edges stable, refresh/reopen only/no
authored save/measurement. Owned operational clients stopped;14 managed cwd refs
handled by archive/no unknown kills. This worker only read supplied durable receipts;
no editor/service/PID/worktree query or operation. Root assigns subsequent named leases.
Root's complete754a0b5 JSON note retains original20 review/handoff entries and
added receipt/31-entry ledger/reference facts. At its time-specific supplied HOST
boundary, old286171 gracefully quit, sole pinned main325756 saved/unsavedempty,
ten tabs/six reopens and bytes of all 1,794 tracked files per checkout preserved,
no authored save or CRLF/LF normalization. This worker made no shared surface/PID query;
no new runtime/device proof. Root grants subsequent named leases separately. Original
S02/S03 fixtures remain immutable. Separate drawable S02/S03-R/S04 physical input,
native focus, camera/readability/feel and conditional prediction decisions remain
open. DOC1–11 are complete; [DOC6](docs/reviews/p0-doc6.md) reconciles accepted S04
discovery without reopening DOC1–5 or closing technical/product gates. Four profile proposals remain reviewed
and inert, zero installed, configuration and representative launches deferred.

S03-S compatibility `ca38e4fc55b32a379ef7e3bf947e27d4ca8edc4c` is independently
ACCEPTED and integrated on local main; workspace `wks_18746ba26c666eb7` and direct
Sol HIGH lead `6a768b9c-b35d-4008-b94f-e713554dd1a5`/same independent Sol HIGH
reviewer `ed0c2c1d-f028-497d-822c-c3be476c314e` archived by Paseo. Its
[stopped compatibility record](docs/spikes/s03-s-compatibility.md) is accepted
static/model/reflection/copied-registration evidence, not a native peer, selected
adapter/integration or live delivery/lifecycle proof. Root's next commission
chooses exact immutable upstream-revision evidence or separately bounded native
API/peer design; no repeat model expecting network proof or contract weakening.
Same S03-S task owns remaining compatibility/Steam acceptance; root assigns the
next worker/budget. [DOC7](docs/reviews/p0-doc7.md) discovers this partial result;
no duplicate technical task or native acceptance follows.

DOC1–11 guide reconciliation is complete. Ready scoped DOC12/13 acceptance discovery
and existing P0-PROFILES dated-notes reconciliation do not require a visual lease.
Stopped S02 visual access does not hold up independent ready work. S08's bounded
isolated observation is accepted STOPPED, archived, with full proof gates OPEN.
Existing S08 owns the active UNACCEPTED lead488b6000/workspacewks_e2ba2fe7704a8fa6
isolated release follow-up above; private editor authoring/launch awaits ROOT grant.
Active S05 source
preparation proceeds independently within its NEW-file/Blender CLI boundary. Limited S07 static run-card/content-gap preparation can be separately
assigned; representative measurements await actual content/effects/drawability/hardware.
The [eighth checkpoint](docs/reviews/plan-check-2026-10-08-08.md#readiness-and-next-trigger)
records decision/output/caps/stop boundaries. Root names writers and serializes
conflicting reviews; no identical window rerun, broad display/
renderer/driver/service repair, pin/contract choice or duplicate technical owner.
S07's research/method remains accepted; partial S06 now supplies saved technical
seam/topology within provisional planar assumptions. Actual source-linked S05 effects/
drawability/saturation/live-versus-hydrated, named hardware/four separated views,
representative content/residency/sustained measurements remain missing. No maximum,
renderer or streaming choice. Final Steam/feel/target and early S08 Deck input/engine
choices remain open; no device/account request repeated. All production M1 stays
behind P0-GATE; P0-PROFILES remains outside it.
The [S03 fixture boundary](docs/spikes/s03.md#fixture-and-boundary) remains isolated.
The table describes dependency stages, not a claim that deferred proofs are runnable.

| When | Work that can run together | Must wait |
| --- | --- | --- |
| Initial foundation | Ratified brief, contract drafts, concept exploration, tool inventory | Chosen style/layout and measured scope revisions need user ratification and evidence |
| Tiny fixtures available | S02 camera using [S01 pipeline evidence](docs/spikes/s01.md); use [completed S03 session evidence](docs/spikes/s03.md); review skill dry runs | All visible fixtures must have Blender sources; only minimum harness required |
| ENet boundary available | Stopped S03-S compatibility accepted; root commissions exact-revision evidence or bounded native-boundary design; S08 desktop preparation | No adapter selection/native delivery/access proof inferred; existing-app/tester/native compatibility still required |
| Reviewed desktop and partial S05/S06 technical results available | Exact754a0b5 and7fb302b PARTIAL accepted; provisional S07 seam dependency satisfied; S02 exacta311c576 stopped record ACCEPT/full-positive FAIL; DOC1–11 complete; scoped DOC12/13 ready; S08 exact1229782 stopped evidence ACCEPTED/full asset-ENet OPEN; ACTIVE UNACCEPTED S08 lead488b6000/workspacewks_e2ba2fe7704a8fa6 owns isolated release follow-up, no accepted outcome | Time-specific S02 operational/display lease RETURNED; authoring UNASSIGNED/no shared writer; archived S08 used no shared lease; ACTIVE UNACCEPTED S05 source prep owns only NEW asset files/isolated Blender CLI with read-only private capability plan, Godot operations await ROOT grant; active S08 has no shared/private editor launch grant yet and reserves distinct17650/17670/17015/17016/17017 versus S05's16650/16670/16015/16016/16017; full S02/S07 and actual effects/drawn/physical keys/feel/final dimensions/Steam/targets remain open |
| Both providers available | Finish S03-R foot response and S04 network response; S08 exports | Both transports need evidence; foot/vehicle prediction are separate decisions |
| Provisional technical topology available | Accepted S06 crossing/opposing legal LEFT turns/four-arm minimap/stale-data and finite guard; S07 static preparation | Actual drawn/readability/final bodies/contact/exit reruns and real M1-C3 contested recovery remain open; geometric sensitivity is not changed-body proof |
| City/effect fixtures available | S07 capacity/culling experiments, finish S08, skill dry runs and doc reconciliation | P0-GATE resolves critical assumptions before production |
| M1 begins | M1-A shell/settings, M1-C1 art families | Each art class uses its approved style/pipeline/envelope |
| Shell accepted | M1-B1 vehicles and M1-B2 weapons; static sector assembly | M1-B3 needs both vehicle and damage ownership |
| Routes/actors accepted | NPCs, minimap, final asset integration and growing CI | Population needs actual movement, roads and control transfer |
| Integrated district accepted | Feel/reviews and network/performance work | Final builds/user acceptance require all selected evidence |

Do not let multiple agents edit one shared scene/source at once. Give independent
workstreams separate fixture/prefab/sector files and explicit handoffs. Parallelism
does not bypass editor save/reload, source review or gameplay ownership contracts.

## Primary references for spike questions

Stable docs guide research; verify APIs and behavior against the exact pinned engine.

- [Godot 3D import formats](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html): GLB/import workflow for S01.
- [Godot high-level multiplayer](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html): transport/RPC constraints for S03/S08.
- [Steam networking/relay](https://partner.steamgames.com/doc/features/multiplayer/steamdatagramrelay): actual Steam gameplay route for S03-S.
- [Steam lobbies](https://partner.steamgames.com/doc/features/multiplayer/matchmaking): friend discovery/join lifecycle, separate from gameplay transport.
- [Testing on Steam](https://partner.steamgames.com/doc/store/testing): existing-app tester access, private branches and installation checks for S03-S/S08/M1-D4.
- [VehicleBody3D](https://docs.godotengine.org/en/stable/classes/class_vehiclebody3d.html): known limitations to consider when choosing S04 candidates.
- [NavigationAgents](https://docs.godotengine.org/en/stable/tutorials/navigation/navigation_using_navigationagents.html): path following and avoidance questions for S06.
- [S07 researched capability/method brief](docs/spikes/s07.md): exact dev7 streaming scope, capacity axes, measurements and investigation path.
- [Occlusion culling](https://docs.godotengine.org/en/stable/tutorials/3d/occlusion_culling.html): camera-dependent opportunities and CPU cost to measure in S07.
