# Fun Things

A Godot project with multiplayer planned. The checkout has engine/style
configuration, the Godot MCP Toolkit, [S01 asset fixtures](docs/spikes/s01.md), a reviewed
[S02 desktop camera/control fixture](docs/spikes/s02.md#reviewed-desktop-handoff) and an isolated
[S03 ENet session-contract proof](docs/spikes/s03.md), plus the accepted
[bounded headless S03-R foot-response experiment](docs/spikes/s03-r.md) and accepted
[S04 car/body/ENet technical fixture](docs/spikes/s04.md#accepted-exact-final-disposition).
The accepted [stopped S03-S compatibility probe](docs/spikes/s03-s-compatibility.md#accepted-exact-final-compatibility-disposition)
adds source/model/reflection evidence, with no selected Steam adapter.
The accepted [partial S05 damage/chain fixture](docs/spikes/s05.md#accepted-exact-final-disposition)
adds finite authoritative outcomes and settled wreck hydration. Later accepted
[source carrier](docs/spikes/s05-effect-preparation.md) and
[saved eight-slot presentation](docs/spikes/s05-saved-presentation.md) add linked geometry,
not proven drawn explosion effects.
The accepted [partial S06 two-sector topology/body proof](docs/spikes/s06.md#accepted-exact-final-disposition)
adds saved source-linked seams, routes, shared map data and fail-closed bake validation.
There is no production gameplay yet; the real project now has an S08-X boot scene that
loads the saved S06 intersection for desktop export smoke checks. The first milestone
uses ENet only; the session/transport APIs preserve room for a later Steam adapter.
Steam Deck LCD/OLED is the confirmed primary target: 60 FPS at native 1280×800
with stylized graphics. Product scope is ratified; budgets and proof-dependent
toolchain choices remain provisional.

## Setup

Run from the repository root:

```sh
mise trust
mise install
mise exec -- godot --version
mise run editor
```

`mise.toml` currently pins Godot **4.8-dev7**, gdstyle **0.3.0**, and Python
**3.14.2**. Keep the gdstyle pin aligned with `.gdstyle-version`. Use the pinned
engine for editor, imports, checks, and exports; install export templates matching
that exact release.
`mise run play` opens the saved S06-intersection boot scene. Matching desktop export
template hashes and install/export recipes are recorded in
[S08-X](docs/spikes/s08-x.md).

The foundation checks use the Mise-pinned Python and tools on Windows and Linux:

```sh
mise run gdstyle:check
mise run gdscript:check
mise run tools:check
mise run spike:s03
# Direct validation baseline and an alternate runner invocation:
python tools/script_checks.py
python -m unittest discover -s tools -p "*test*.py"
mise exec -- python tools/run_s03.py --port 24700 --proxy-port 24701 \
  --output /tmp/s03-my-run
```

Each command prints its evidence directory. The runner imports the saved fixture
into an addon-free project, explicitly compiles every owned script in a separate
dependency mirror, then launches two real ENet processes through the session APIs.
Host/client user and log directories are separate. It rejects engine/script
diagnostics even with a zero exit status, retains logs on failure and stops only
its own children. This proves the small Linux loopback contract; S01 owns asset
checks and later tasks own gameplay, Steam, exports and target compatibility.

The S02 corner/alley fixture has a separate supplementary runner (no Mise task):

```sh
mise exec -- godot --path . res://tests/fixtures/s02/corner.tscn
python3 tools/s02/run.py --godot /path/to/pinned/godot --output /tmp/s02-my-run
```

Supply the exact pinned Godot binary and a fresh evidence directory outside the checkout. The runner checks isolated
movement/input/query outcomes and saved resource/source links; it does not replace
all-script compilation, Blender reexport or native OS focus/physical-key playtests.
The [source handoff](docs/assets/s02_kit.md) and
[development recipe](docs/development.md#s02-desktop-fixture-tooling) describe its scope.
The 47 m/42° camera is a provisional desktop candidate; 50° remains an inherited
comparison. Current native focus revalidation is incomplete, historical focus
passes remain historical, and human feel/readability, physical-key Alt-Tab and
Deck input/performance acceptance remain open. Desktop 1280×800 captures do not
certify Deck targets or production gameplay.

The supplementary S03-R runner reuses the saved S02 controller/source kit and S03
session fixture (no Mise task):

```sh
python3 tools/run_s03_r.py --godot /path/to/pinned/godot --output /tmp/s03-r-my-run
```

Defaults are headless, `--profiles baseline normal adverse`, `--port 24900`,
`--proxy-port 24901` and `--deadline 45` seconds per two-process case after import.
Ports must be distinct in 1–65535; the deadline must be 1–90 seconds. `--godot`
defaults to Godot on PATH and verifies the exact pin. `--output` must be a fresh
empty directory outside the checkout; omitted output uses a printed temporary
directory. Each profile imports an addon-free copy of S02/S03/S03-R and S02 models,
with private user/cache/log directories and a bounded seeded loopback UDP proxy.
It retains results, commands, fingerprints, import/proxy/host/client logs and
stops only its own children. Nonzero exits and engine/script errors or warnings
fail the run. It does not compile every owned script; use the separate foundation
checks. `--windowed` attempts real drawn-frame receipts; missing frames remain
unavailable and do not fail the technical criteria by themselves.
See the [full recipe and log scope](docs/development.md#s03-r-foot-response-tooling).

Accepted synthetic input-to-applied-client-physics p95 is 69/235/365 ms for
baseline/normal/adverse. Stationary convergence and the separate fix follow-up
are recorded in [S03-R](docs/spikes/s03-r.md); these are not drawn response,
human feel or predicted correction measurements. The [resync baseline-floor P2
is closed](docs/reviews/s03-r-b87f889.md), but full S03-R, native focus/physical
input, visible owned/remote response, camera/aim continuity, replay if warranted,
Steam/Deck/Windows/export and P0-GATE/production acceptance remain open.

The supplementary S04 car runner and four API/body checks have no Mise task:

```sh
python3 tools/run_s04.py --godot /path/to/pinned/godot --output /tmp/s04-my-run
python3 tools/s04/run_checks.py --godot /path/to/pinned/godot --output /tmp/s04-my-checks
```

The runner defaults to headless baseline/normal/adverse, distinct UDP ports
24900/24901 and a 45 s case deadline after isolated import. It retains copied
S02/S03/S04 dependencies, private user directories, results/fingerprints and
import/proxy/host/client logs; cleanup stops owned children. Neither command
compiles every owned script or reexports Blender sources. The
[development recipe](docs/development.md#s04-car-fixture-tooling) maps exact flags,
check scopes and the separate scratch reexport tool. Assign process/source access
before running these recipes; no new execution is part of this guide reconciliation.

Exact `2370ad1` is accepted for bounded technical use, with original review P2/P3
closed. Original applied-client-physics p95 **97/269/401 ms** and corrected
normal/adverse **248/380 ms** are distinct historical receipts; zero drawn-frame
receipts were obtained. Shared handling, passive bodies and injured seated resync
are fixture evidence, not production vehicle identity or a full seat system.
CharacterBody is a next technical recommendation; body/controls/dimensions/turning,
physical keys/focus, camera/readability, human feel and prediction remain unratified.
Full S02/S03-R/S04, Steam/Deck/input, capacity, P0-GATE/M1/production gates stay open.

S03-S compatibility is accepted at exact `ca38e4fc55b32a379ef7e3bf947e27d4ca8edc4c`
for the stopped source/model/copied-registration result. The inspected singleton
Sockets API lacks lane-addressed send and receive lane identity; source ownership/
mode/result limitations and finite counterexamples do not prove native behavior.
API registration/getters establish presence only. See the
[bounded reproduction/evidence recipes](docs/development.md#s03-s-stopped-compatibility-tooling)
for the source probe, copied registration and read-only exact-final note retrieval.
No fetch/model/registration or native experiment ran for this documentation task.
Later accepted [upstream assessment](docs/spikes/s03-s-upstream-peer-evidence.md)
and [Valve public API/interface proposal](docs/spikes/s03-s-valve-api-interface.md)
complete those source-research steps; adoption and native validation remain open.
No adapter, five-lane fix, reliable fallback, SDK/vendor/pin/package or integration
choice is selected. Full S03-S,
native delivery/lifecycle/queue/allocation, external route/relay/package/device,
Steam/Deck/S04 and P0/M1/production gates remain open.

The supplementary S05 runner and read-only resource checker have no Mise task:

```sh
python3 tools/run_s05.py --godot /path/to/4.8-dev7/godot --gdstyle /path/to/0.3.0/gdstyle --output /tmp/s05-my-run
python3 tools/s05/check_resources.py --base c8096b55ef97412552366fdaa74c220b976ed82e --output /tmp/s05-resources-my-run.json
```

Both executable flags are required by the runner. Its optional output must be fresh,
empty and outside the checkout; omitted output prints a temporary directory.
Default headless mode runs both API scenes, separate host/live/settled-late ENet
processes on ports25040/25041, then finite queue pressure. `--api-only` omits ENet;
`--queue-only` runs just pressure after import/seven-script compile/style checks.
Private user/log scopes and owner-only child cleanup are described with every
flag/default and the resource checker's different output rules in the
[development recipe](docs/development.md#s05-partial-damagechain-tooling).
Seven S05 compiles do not replace all-owned compilation; neither import nor tokens
prove drawn effects. Sentinel death is not admitted-player death/respawn, and settled
hydration is not a during-chain journal/reset proof. Exact754a0b5 partial acceptance
keeps full S05, policy/dimension reruns, Steam/Deck/input/feel/capacity and P0/M1/
production gates open.

The supplementary S06 runner and static resource checker have no Mise task:

```sh
python3 tools/s06/run.py --godot /path/to/4.8-dev7/godot --output /tmp/s06-my-run
python3 tools/s06/run.py --godot /path/to/4.8-dev7/godot --content-only --output /tmp/s06-content-my-run
# Clean committed current checkout; existing parent directory, new JSON filename:
python3 tools/s06/check_resources.py --base "$(git rev-parse HEAD)" --output /tmp/s06-resources-my-run.json
```

`--godot` is required; runner output must be fresh, empty and external. The checker
requires a JSON filename with an existing parent and overwrites an existing file;
it has no runner-style output guard. Its default original base `096469f` and historical
accepted base `6c36c12` guard every base file except TODO, so later guide changes fail
those comparisons by construction. The current-HEAD recipe checks clean current
bytes; it does not independently prove preservation against the immutable accepted
base. The [source-derived development recipe](docs/development.md#s06-partial-topology-tooling)
explains that separate docs-delta audit, staging, private users/logs, deadlines,
cleanup, editor-only bake and import versus explicit all-owned compilation.
These recipes are for separately assigned checks; none ran for this documentation task.

Exact `7fb302b` is independently ACCEPTED PARTIAL, R1 P2/R2 P3 closed and same-HEAD
note condition MET. Unchanged S02 crossing **477 ticks/7.95 s** and S04 opposing legal
LEFT turns **721 ticks/12.0167 s each** are discrete planar body/seam evidence.
Content-only checks include finite ROAD width; shared four-arm map values and saved
stale/rebake negatives are technical evidence. They do not prove drawn minimap/
camera/readability, final dimensions/feel or contested blockage/stuck/wreck recovery.
Full S06, S02/S03-R/S04/S05/S07/S08, Steam/Deck/input and P0/M1/production gates stay open.

## Current foundation discovery — 8 October 2026

Accepted research and partial prerequisites, not full foundation acceptance:

- **S05:** source `2294a111` and saved presentation `a15a7fbe` provide an original
  Blender → GLB → eight saved-slot chain. [Render observation](docs/spikes/s05-render-observation.md)
  `233493ab` proves node/ENet/natural-expiry behavior, but `can_draw=false` and no
  workload PNG. [Consumed Card I](docs/spikes/s05-vsync-image-observation.md)
  `af65276d` failed endpoint-binding **proof** before live/late launch, not a proven
  native bind fault; no PNG, effective-VSync or image-review credit, no retry.
- **S07:** [static cards](docs/spikes/s07-run-cards.md) `30a97532` and the accepted
  [sustained primary-T driver](docs/spikes/s07-sustained-driver.md) `8689168d`
  provide 57 traversals over 600 declared seconds, not graphical calibration,
  representative capacity or a load choice. Historical runtime attempts are exhausted.
- **S08:** [standard-editor/release preparation](docs/spikes/s08-standard-editor-release.md)
  `52941da4` resolves saved entrypoint and assert-side-effect prerequisites with
  API106/asset172 positives, while retaining shutdown/exported-host failures.
  [Handoff](docs/spikes/s08-exported-enet-handoff.md) `0add6257` observes live readiness/
  admission but fails deadlines. [Lifecycle](docs/spikes/s08-release-lifecycle.md)
  `fd375c03` passes matrices only under unplanned 10 ms servicing: scheduling/grant
  compliance FAIL, strict RELEASE diagnostics FAIL (2 host/6 client errors).
  Restored 20 ms helper source is unexecuted; original saved S08-main stall is unfixed.

[Current helper discovery](docs/development.md#current-foundation-helper-discovery--8-october-2026)
separates usable offline checks from exhausted runtime protocols and historical paths.
[Checkpoint09](docs/reviews/plan-check-2026-10-08-09.md) and the
[reconciliation record](docs/reviews/p0-doc14.md) bind acceptance and immutable evidence.
Full drawn S05, graphical/capacity S07, clean release, Windows/Linux target proof,
actual Steam gameplay/testing, LCD/OLED Gaming Mode/native1280×800/60FPS/input/offline/
suspend, human feel, P0-GATE and M1 remain OPEN. No integration, load, pin or budget
is selected; Steam testing is deferred, not waived. No runtime ran for this supplement.

## Project guidance

- [Plan through the first milestone](TODO.md): phase-zero foundations, technical
  spikes, dependencies, and playable-milestone acceptance.
- [Product brief and validation envelope](docs/design.md): ratified P0-01 scope,
  gameplay policies, provisional budgets and owned proof/setup decisions.
- [Ownership architecture](docs/architecture.md), [scene structure](docs/scene-structure.md)
  and [API contracts](docs/api-contracts.md): P0-02 drafts for state owners, authored
  paths, session/gameplay lifecycle, data shapes, limits and future acceptance tests.
- [Repository guidance](AGENTS.md): everyday working rules for contributors and agents.
- [Development workflow](docs/development.md): architecture, validation, resource
  identities, version control, and release checks.
- [Asset workflow](docs/assets.md): source ownership, model integration, collision,
  art review, and audio provenance.
- [Complete concept review](docs/concepts/p0-04/review.html), [art direction](docs/art-direction.md)
  and [city layout](docs/world-layout.md): P0-04 uses Petrol & Coral, smooth 3D and
  mixed-height buildings with a downward perspective camera. The starting art/city brief
  is accepted; dimensions and camera/asset behavior remain provisional for the proofs.
- [Multiplayer guidance](docs/multiplayer.md): authority, admission, lifecycle,
  replication, prediction, transports, and staged acceptance tests.
- [Guidance provenance](docs/guidance-sources.md): what was extracted from VCS,
  what was generalized, and what was intentionally left there.

The guides set working conventions and describe future implementation choices.
This checkout has executable foundation checks and an isolated ENet session-contract
fixture/runner, but no production gameplay networking or Steam integration. The
fixture's Linux loopback evidence does not establish Steam or Deck compatibility;
engine/input decisions and P0-GATE remain open. [S07 preparation](docs/spikes/s07.md)
assigns one map/content-capacity and diagnostic owner; graphical/capacity measurements
remain unexecuted.
It selects no maximum map size, streaming implementation, renderer or engine.

P0-PROFILES' requirements/proposal stage is delivered and independently reviewed:
the [four proposed bundles](docs/workflows/p0-profiles-proposal.md#four-proposed-bundles)
cover Sol 6.1 medium/high leads and non-specialist review, Luna high very simple
delegation, and Astra high necessary bounded spatial specialists. The
[review](docs/workflows/p0-profiles-review.md) and
[fourth assessment](docs/reviews/plan-check-2026-10-07-04.md#profile-assessment)
retain evidence and limits. All four bundles remain PROPOSED/inert, zero profiles
are installed, and no representative launches have run. Installation, effective
settings/permission checks and launch validation require the later explicitly
authorized workflow; P0-PROFILES remains open in [the plan](TODO.md).

Add executable tasks alongside their implementations and document only commands that work in this
checkout.
