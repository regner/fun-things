# Independent S02 code review

Reviewed candidate: **8d5c8d7caf62ef54cc1e90ce7c050e0780eb8d32**, branch
`s02-desktop-camera-controls`. Base: **eb8e9d5c9f92ea95f582603aada6f05ff6b2415e**
(`refs/heads/main`). Review date: 7 October 2026.

**Recommendation: request changes for the advertised keyboard aliases.** The candidate
provides useful bounded desktop preparation, with passing compilation, resource and
core physics/query checks. It does not establish whole-S02, subjective feel, handheld,
early-S08, P0-GATE or production acceptance. Preserve the existing preparation and
hardware/account deferral records.

## Findings

### 1. P2 — Releasing one keyboard alias cancels another alias that remains held

**Location:** `tests/fixtures/s02/desktop_input.gd:34–38`; bindings in
`project.godot:37–169`. Missing regression coverage:
`tests/fixtures/s02/check_s02.gd:101–120`.

**Trigger and evidence:** Press physical W, press Up, release W while Up remains held.
The collector returns `move = 0` instead of `move = 1`. The independent viewport-routing
probe reproduced the same failure for S+Down, A+Left and D+Right. A repeat echo from the
remaining key leaves the action neutral. Results are retained in
`/tmp/s02-review-independent.log`, with source `/tmp/s02-review-independent.gd`.

**Cause and impact:** `_held` stores one value per action. A release from any bound key
unconditionally erases that action, losing the other key's contribution. Because echoes
are deliberately rejected, holding the second key cannot recover movement/turning;
the user must release and press it again. This breaks the declared supported keyboard
bindings and can confound a control-feel experiment. Opposite actions correctly cancel
and resume the remaining direction; the defect specifically concerns aliases of one
action. The supplied check tests W alone and cannot detect it.

**Minimal fix:** Keep held contributions by individual physical binding in the input
owner and aggregate them into action strength. A release removes only its own binding.
Retain GUI/unhandled routing, clearing on suspension, and rejection of stale echoes;
using global polling without those safeguards would change the focus contract.

**Retest:** Through normal viewport routing, exercise all four alias pairs in both
press/release orders. Releasing one must retain the other's move/turn until its own
release. Also verify opposite-direction cancellation and focus/menu clearing with
both aliases held; echoes on regain must remain neutral until a fresh press.

### 2. P3 — Suspension resets the diagnostic ray's advertised minimum interval

**Location:** `tests/fixtures/s02/aim_probe.gd:48–50`, called by
`tests/fixtures/s02/fixture.gd:58–61`. Advertised contract:
`docs/spikes/s02.md:37` (minimum 0.25 s interval).

**Trigger and evidence:** Fire, release Space, suspend/resume with Escape, then press
Space freshly. An independent probe using the ordinary input collector and automatic
fixture physics callback recorded shots on physics frames **3 and 5**, at 60 Hz:
about **0.033 s apart**, with `interval_seconds = 0.25`. See
`/tmp/s02-review-cooldown.log` and `/tmp/s02-review-cooldown.gd`.

**Cause and impact:** Every input suspension invokes `aim.clear()`, which zeros the
cooldown. Repeated suspension can bypass the documented ray cadence. Severity is low:
this fixture applies no damage/ammo/production weapon outcomes and still performs at
most one probe per physics callback. It does, however, make the stated minimum and
held-fire-only bounded-rate evidence incomplete. This is a fresh-input rate issue,
not stale firing after focus regain.

**Minimal fix:** Preserve the remaining cooldown when canceling local input/feedback.
Keep a deliberate test/reset operation separate if the query harness needs an immediate
fresh shot between cases. The query owner should continue advancing the cooldown while
input is suspended.

**Retest:** Fire once, suspend/resume before 0.25 s expires, and request a fresh shot
through routed keys. No second shot may occur before the interval. Repeat with the
focus API; movement/fire intent must still clear immediately. Rerun existing blocked,
close-muzzle and held-fire checks after adapting explicit fixture resets if necessary.

No P0/P1 finding was established. No tracked changes or fixes were made during review.

## Scope and contract assessment

Read `AGENTS.md`, `.agents/skills/gdscript-review/SKILL.md`, TODO S02/S08 and gate/access
records, ratified design, accepted art direction/world layout, development/assets,
architecture, scene/API and multiplayer contracts, S01's evidence and existing fixtures.
Reviewed the complete base-to-candidate change: 149 paths, including saved scenes,
all eleven new owned scripts/helpers, the shader, tools, nine GLBs/imports, source
mapping, documentation and retained evidence. Binary GLB structures and source/export
fingerprints were inspected; the Blender source was not opened or reexported by this
code review. The full diff is retained at `/tmp/s02-review-8d5c8d7-full.diff`.

| Technical scope | Review disposition |
| --- | --- |
| Facing-relative turn/forward/back, no strafe or independent mouse aim | Supported by code and independent normal-callback checks; alias handling requires the P2 fix |
| Input/simulation/query/presentation separation | Supported: collector owns held intent, ActorMotion owns pose/velocity, AimProbe owns ray/cadence, coordinator orders motion then query, presentation consumes results |
| Fixed-yaw vertical perspective camera | Saved composition and runtime axes agree; 47 m/42° and inherited 50° are exploratory values, not ratified choices |
| Flat actor collision, passage/corner movement, blocked/clear/muzzle queries | Supported within the tested fixture; additional target collision, diagonal sliding and tower-ray probes passed |
| Local focus/menu cancellation | API behavior independently passes; committed native-window log supports one bounded automated minimize/restore case, not every OS input path |
| Saved scene/source/import boundary | Supported by static inspection and clean import/resource checks; no runtime authored node hierarchy or owned render primitive/copied mesh was found |
| 0.25 s ray minimum across suspension | Not supported as implemented; P3 discrepancy above |
| Full S02, production motion/combat/network/prediction, early-S08 engine/input decision | Not accepted by this review; required evidence remains pending |

The single coordinator explicitly samples input before motion and performs queries
after motion. Camera process priority -10 precedes the coordinator's cutaway update.
The actor does not access Input devices; the ray probe emits results and does not
apply damage. There are no new RPC/replication/prediction paths. This is appropriate
for the authorized standalone spike; eventual authoritative/replay equivalence remains
S03-R/M1 work, not a networking requirement imposed on this change.

All authored nodes, colliders, UI and placements are in saved scenes. Runtime-created
objects are input events, ray-query parameters and per-instance shader materials,
not authored node assemblies. Building presentation changes material overrides without
changing mesh vertices, solid collision or saved placement. Each inspected imported
mesh has one material surface, compatible with `building_view.gd`'s current palette
conversion. This assumption is bounded to this kit, not a general multi-material API.

The actor has a direct capsule collision child; static shapes are direct children of
their StaticBody3D nodes. Imported GLB ancestry is retained. `corner_wide.tscn` changes
only the owned Camera3D FOV and stores the inherited node identity/path. New script and
shader UID sidecars are present. Clean resource checks found unique owned resource
UIDs; S02 dependency checks found UID/path agreement. Metadata world IDs and distinct
saved building placements are present. No existing serialized public API was migrated.
Purpose comments, type hints, tabs/LF, two-empty-line function separation and new
export spacing were inspected in addition to pinned format/lint.

## Independent executable checks and retained logs

Exact binaries used:

- `/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot`
  — reported `4.8.dev7.official.c971f93e7`.
- `/home/regner/.local/share/mise/installs/github-atelico-gdstyle/0.3.0/gdstyle`.

All runs used isolated project/user/cache directories and headless Godot. No shared
editor/MCP mutation, Blender session, display window, vendor, pin or checkout
configuration was changed. No subdelegation was used.

| Check actually run | Result / evidence |
| --- | --- |
| `tools/script_checks.py`, pinned binaries, initial sandbox run | Format/lint pass; all **21/21 individual scripts compile**. Aggregate command exits 1 because editor import setup reports socket creation/image errors. `/tmp/s02-review-8d5c8d7-checks/` |
| Same all-owned-script check, fresh copy with approved local-socket access | **Pass**, exit 0, setup and **21/21 explicit per-script compilations** clean. Includes unused/editor helpers and all existing S01/S03 scripts. `/tmp/s02-review-8d5c8d7-checks-host/` |
| `tools/s02/run.py`, initial sandbox run | Runtime outcomes pass and persisted hashes unchanged; aggregate exit 1 due import socket errors. `/tmp/s02-review-8d5c8d7-outcomes/` |
| Same S02 runner, fresh copy with approved local-socket access | **Pass**, exit 0, import/outcomes clean, saved files unchanged. `/tmp/s02-review-8d5c8d7-outcomes-host/summary.json`, `import.log`, `outcomes.log`, `identities.json` |
| Independent alias/focus/menu and physics-rate probes | Clean exit 0, no runtime diagnostics; observations demonstrate P2, cancellation/fresh-press behavior and rate limits described below. `/tmp/s02-review-independent.gd`, `/tmp/s02-review-independent.log` |
| Independent ordinary-callback and extra collision/query probes | **Pass**, no failures/diagnostics in final run. `/tmp/s02-review-runtime.gd`, `/tmp/s02-review-runtime.log` |
| Independent ordinary-input cooldown probe | Clean exit 0; demonstrates P3 at frames 3/5. `/tmp/s02-review-cooldown.gd`, `/tmp/s02-review-cooldown.log` |
| `tools/s01/clean_import.py`, pinned engine/local-socket access | **Pass**, clean import/resources, identity preservation and seven expected negative cases. `/tmp/s02-review-8d5c8d7-s01-host/` |
| Static evidence/source/GLB audit | All **60** validated-file hashes and **10** source/export hashes match. Both **11-scene** roundtrip manifests match current files and each other. Nine GLBs have valid containers, no external buffers/images/compression extensions, linked source sockets. `/tmp/s02-review-static-audit.json` |
| `git diff --check` | Exit 2: raw captured compiler logs contain blank EOF lines/progress trailing spaces. No source-code whitespace finding; raw logs were preserved. `/tmp/s02-review-diff-check.log` |

The supplied S02 outcome check independently specifies 5 m forward, 3 m reverse,
90° turn without displacement, facing-relative movement, solid wall stopping and a
traversable 4 m corridor/corner. It expects specific collider identities for clear,
blocked and muzzle-obstructed rays; it does not merely compare implementation formulas.
The rerun reproduced wall stop `(6, 0.001, 0.38021)` and corner end approximately
`(3, 0.001, -9)`. However, its input check covers W/Space/Escape, not overlapping
aliases, and its firing-rate check covers continuous hold, not lifecycle transitions.

The independent normal-callback run measured 5.000002 m forward and -89.999968°
right turn, fixed vertical/world-yaw camera axes, and a TargetClear hit. Target collision
stopped the actor at `(0.43, 0.001, -9.238928)`. Diagonal sliding ended at
`(1.619122, 0.001, -7.932874)` without entering EastCorner. Queries from clear positions
beside the near/tall towers hit their solid faces at Z=-8.

An initial reviewer tower probe started the near-tower actor on the WestCorner wall
boundary, so its muzzle correctly intersected WestCorner instead. That was a reviewer
placement error, not a candidate defect; the corrected probe starts outside the corner
footprint. The original failure log is retained at `/tmp/s02-review-runtime-initial.log`.

The 60/120 Hz exploratory probes both travel approximately 5 m and turn 180° in one
second. At 10 Hz, travel remains 5 m but turning is only 90°: ActorMotion clamps the
supplied turn delta to 0.05 s while `move_and_slide()` integrates the engine delta.
**This is a reuse limitation, not a failure of the required fixed-60-Hz fixture.** Do not
accept the current method as an arbitrary-delta/replay integrator. Before reuse, define
one fixed engine-step contract or resolve the inconsistent cap, and validate through
the actual authoritative/replay caller. No tick-rate/pin/config change is recommended
for this spike on the basis of the 10 Hz probe.

Logs were assessed with exit statuses. Failed sandbox import logs are retained and
were resolved by specific local-socket escalation, without suppressing diagnostics.
The committed final evidence's only additional error line is Blender's declared missing
optional MeshOptimizer library; inspected GLBs use no compression extensions. Historical
editor parse/progress errors and failed focus evidence remain explicitly historical.
Expected S01 negative-probe errors are distinct from clean-run results.

## Evidence limits and pending decisions

- Reviewed all seven current 1280×800 captures, the earlier tower-edge obstruction
  image and accepted weapon concept sheet. Camera state, saved transforms and projection
  measurements are consistent with the captures. I did **not** render new graphical
  captures or independently execute the shader on a GPU in this headless-only review.
  The committed images remain paintover inputs, not traversal, performance or focus proof.
- The 42° starting frame exposes the clear target near the upper edge; the alley frames
  show it much nearer the actor. The tower-edge comparison shows a circular local-actor
  cutaway revealing the held extension. This does not establish moving-camera comfort,
  whole-route roof/target protection or universal near/above-camera clipping. The shader
  protects only the local actor region, not every intended target/turn. Those are explicit
  coverage limits, not an accepted replacement for the ratified readability requirement.
- At native view size the launcher has more length than the pistol/SMG; pistol versus
  SMG distinction remains weak. The current geometry is a blockout study against the
  accepted compact/stocked/tube language. No production asset or subjective silhouette,
  marker, circular cutaway, FOV, speed, instantaneous turn or follow tuning is ratified.
  Art provenance/fresh reexport and shared-editor save/reopen execution were left to the
  art reviewer; code review verified the recorded hashes/links, not that review's verdict.
- Focus API cancellation, neutral echoes on regain, fresh-press resumption and menu
  cancellation passed independently. The committed native-focus log records held motion
  and two shots before real minimize, inactive/native-unfocused state afterward, frozen
  position `(0, 0.001, 3.499997)` and shot count 2, then neutral focused restore. Its failed
  historical run correctly records no OS loss. Neither run was rerun here because display
  windows were prohibited. Human physical-key Alt-Tab/focus behavior remains pending;
  injected key events are not physical-key or suspend/resume evidence.
- Collision/query support is the documented flat fixture. No slope/curb/step, district
  boundary, vehicles, spawn/exit, distant players, combat or replicated collision/lifecycle
  transition acceptance is inferred. No networking is required for this desktop spike.
- No Windows export, packaged-target/native-library compatibility, full-plugin editor
  compatibility, graphical shader/runtime cost, input-to-visible latency or human
  walk/turn/aim/shoot playtest was performed. Isolated imports intentionally differ from
  running the development plugins; the compiler copy retains autoload declarations and
  removes editor-plugin execution for setup, as documented by the existing checker.
- No Steam Deck or multiple-account Steam facilities are available. Required **LCD/OLED,
  native 1280×800, 60 FPS, built-in controls, Gaming Mode, host/client roles and suspend**
  evidence remains **UNPROVEN**. Desktop view size cannot accept these or early S08's
  engine/input decision. No hardware/account acquisition or renewed access request is
  proposed. No whole-S02 removal, P0-GATE waiver, reduced target or production acceptance
  follows from this review.

TODO changed only by the three-line S02 desktop evidence addition. Its S02 task stays
open; S08 and S03-S preparation/deferral records survive. Ratified design/art/world,
source/development/multiplayer contracts, S01 resources/tools/fixtures, vendor addons
and engine/style pins are unchanged from the base. Final checkout status remains clean
at the exact reviewed SHA. A correction requires a new candidate SHA and focused
retesting; this report does not approve an unreviewed follow-up revision.
