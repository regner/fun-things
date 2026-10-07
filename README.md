# Fun Things

A Godot project with multiplayer planned. The checkout has engine/style
configuration, the Godot MCP Toolkit, [S01 asset fixtures](docs/spikes/s01.md) and an isolated
[S03 ENet session-contract proof](docs/spikes/s03.md). There is no production
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
engine/input decisions, P0-GATE and profile work remain deferred. Add executable
tasks alongside their implementations and document only commands that work in this
checkout.
