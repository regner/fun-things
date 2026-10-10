# M1-A-GATE — exported multiplayer shell

10 October 2026. Windows functional acceptance is **PASS**. Linux export/package
inspection is **PASS**, but Linux launch acceptance is **OPEN** because no Linux
machine was available. This record does not claim performance, physical input feel,
or Linux execution.

## Implementation

[`tools/export_builds.py`](../../tools/export_builds.py) is the repeatable export
entrypoint. It requires a fresh external output directory, verifies the pinned engine
and exact official template members, wraps every Godot invocation in GNU `timeout`
(600 seconds per export), builds all four committed presets, scans export logs for
missing dependencies, and runs the existing PCK/native inspector. Binaries remain
under `C:/tmp/ft/exports/` and are never committed.

The production Boot recognizes explicit `--m1-a-gate-*` arguments and delegates to
[`ExportedMultiplayerAcceptance`](../../scripts/boot/exported_multiplayer_acceptance.gd).
The coordinator calls the existing SessionService, ENetTransport, MatchReplication,
ActorMotion and lifecycle/reset APIs; it does not implement a second gameplay rule.
Ordinary launches do not enter this path. The debug export is used because the existing
lethal integration hook is deliberately disabled in release builds. Release still
receives the standalone S08-X smoke.

[`run_exported_acceptance.py`](../../tools/m1_a_gate/run_exported_acceptance.py)
launches real Windows exported processes side by side, at 60 FPS, with private user
roots and a 180-second hard timeout. It waits for structured `host_ready` and Match
receipts rather than sleeping. It rejects nonzero exits and runtime warnings/errors.
The silent-auth timeout case uses a real ENet peer but deliberately withholds the
SceneMultiplayer auth response; the host still uses production admission.

## Template and package identity

Engine: `4.8.dev7.official.c971f93e7`. Template directory version: `4.8.dev7`.
The exact official template member SHA-256 values are:

| Member | SHA-256 |
| --- | --- |
| `linux_debug.x86_64` | `8b2871a1e2f8baf482282422f7e64cd7cfcc713eb53d8db671025b041bb23eb9` |
| `linux_release.x86_64` | `c436b976ff5ac2e5f3197732ba7d9462267573e5a108782f84928d0606885695` |
| `windows_debug_x86_64.exe` | `c3287ae1c7fad6f6f2e0e09b0ebbb1321b49ec2423b74d513f12649e4c03bff6` |
| `windows_release_x86_64.exe` | `b538554df997ea699122d5b31f2ea8929301bcf3017e12dba664d85d351f60cd` |

The final package inspection found 1,206 members in each PCK after excluding repository tools. Every recursively
source-addressable Boot/Match/Brackett dependency was present. No package had a missing
required path, forbidden PCK entry, forbidden sidecar file, or missing-dependency log
diagnostic. The guard rejects GUT, tests, prototypes, repository tools, development
scenes, MCP, GodotSteam and Steamworks native libraries. The terminal runtime receipts also reported
both Steam class and singleton absent.

## Windows acceptance receipts

Command (from the repository root):

```sh
python tools/export_builds.py --output C:/tmp/ft/exports/m1-agate-final
python tools/m1_a_gate/run_exported_acceptance.py \
  --executable C:/tmp/ft/exports/m1-agate-final/windows-debug/FunThingsDebug.exe \
  --output C:/tmp/ft/lanes/m1-agate/exported-acceptance-final
```

All eight exported child processes exited zero with no `SCRIPT ERROR:`, `ERROR:`, or
`WARNING:` in stdout/engine logs. Structured outcomes:

- gameplay host/client loaded the whole Brackett saved world; both authority-owned
  actors moved by at least 0.5 m; the client reported bounded local prediction and
  continuous remote presentation; both observed death, three-second respawn and reset
  to MatchRevision 2, while the client independently proved reopened post-reset input/motion;
- protocol mismatch returned `INCOMPATIBLE` and both peers cleaned up;
- a silent authenticated peer reached the bounded deadline and returned
  `HANDSHAKE_TIMEOUT`, with clean host cleanup;
- an admitted host exited and the client returned `HOST_LOST` through SessionService;
- every process was externally hard-bounded and all accepted terminal paths exited 0.

Concise retained receipts are under
[`m1-a-gate-evidence/`](m1-a-gate-evidence/). Full logs and binaries stay outside the
checkout under `C:/tmp/ft/`.

## Owner playtest kit

After exporting, launch a bounded side-by-side pair:

```sh
python tools/m1_a_gate/launch_exported_pair.py \
  --executable C:/tmp/ft/exports/m1-agate-final/windows-debug/FunThingsDebug.exe \
  --output C:/tmp/ft/lanes/m1-agate/owner-pair
```

The script waits for both real Match receipts, places host/client windows side by side,
caps each at 60 FPS and hard-bounds each to 180 seconds. Focus either window; WASD
walks and the mouse aims. Close both windows when finished. This is a manual owner kit,
not automated feel acceptance.

## Open Linux gate

The Linux debug/release binaries and PCKs were produced on Windows and passed package
inspection. They were not launched. Follow
[`m1-a-gate-linux-checklist.md`](m1-a-gate-linux-checklist.md) on a Linux Vulkan
desktop. Until its two-process matrix and release smoke pass, M1-A-GATE remains open
for Linux and the production-plan row is not advanced here.

The editor/MCP scene tools were unavailable for this worktree. No saved scene hierarchy
changed; production scripts, repository tools and docs were edited directly, and the
new GDScript UID was generated by the pinned headless editor import.
