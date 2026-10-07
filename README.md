# Fun Things

A Godot project with multiplayer planned. The checkout has engine/style
configuration, the Godot MCP Toolkit, [S01 asset fixtures](docs/spikes/s01.md), a reviewed
[S02 desktop camera/control fixture](docs/spikes/s02.md#reviewed-desktop-handoff) and an isolated
[S03 ENet session-contract proof](docs/spikes/s03.md), plus the accepted
[bounded headless S03-R foot-response experiment](docs/spikes/s03-r.md). There is no production
gameplay or main scene yet.
The first milestone requires ENet for local testing and Steam for friends playtesting,
using the existing Steam app through shared session APIs.
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

`mise.toml` currently pins Godot **4.8-dev7** and gdstyle **0.3.0**. Keep the
gdstyle pin aligned with `.gdstyle-version`. Use the pinned engine for editor,
imports, checks, and exports; install export templates matching that exact release.
`mise run play` is available once a main scene has been configured.

The foundation checks use Python 3.10+ and the pinned tools:

```sh
mise run gdstyle:check
mise run gdscript:check
mise run tools:check
mise run spike:s03
# Alternate ports and a fresh retained evidence directory:
mise exec -- python3 tools/run_s03.py --port 24700 --proxy-port 24701 --output /tmp/s03-my-run
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
assigns one map/content-capacity and diagnostic owner; measurements remain unexecuted.
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
