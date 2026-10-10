# M1-A-GATE Linux launch checklist

Linux packaging and PCK inspection passed on Windows with the official Godot
4.8-dev7 templates. No Linux machine was available, so every launch item below is
**OPEN**. Passing this checklist is required before Linux launch acceptance can be
claimed.

## Prerequisites

1. Use a Linux x86-64 desktop with Vulkan and Python 3.14 available.
2. Check out the reviewed revision and install the exact Mise pins. Require
   `godot --version` to print `4.8.dev7.official.c971f93e7`.
3. Install the official `4.8.dev7` export templates. Require these SHA-256 values:

   - `linux_debug.x86_64`:
     `8b2871a1e2f8baf482282422f7e64cd7cfcc713eb53d8db671025b041bb23eb9`
   - `linux_release.x86_64`:
     `c436b976ff5ac2e5f3197732ba7d9462267573e5a108782f84928d0606885695`
   - `windows_debug_x86_64.exe`:
     `c3287ae1c7fad6f6f2e0e09b0ebbb1321b49ec2423b74d513f12649e4c03bff6`
   - `windows_release_x86_64.exe`:
     `b538554df997ea699122d5b31f2ea8929301bcf3017e12dba664d85d351f60cd`

4. Confirm Steam is absent with the desktop's read-only process viewer. Do not stop
   another user's process. Record other Godot/game processes and label contention.

## Build and package inspection

From the repository root, with the pinned tools on `PATH`:

```sh
rm -rf /tmp/ft/m1-a-gate-export
python tools/export_builds.py --output /tmp/ft/m1-a-gate-export
```

Require `summary.json` to report `ok: true`, all four export commands to exit zero,
all four PCKs to have no missing production dependency, and no `addons/gut/`,
`tests/`, `tools/`, `prototypes/`, MCP, GodotSteam, or Steamworks member/library. Do not commit
the exported binaries.

## Two-process Linux acceptance

```sh
chmod +x /tmp/ft/m1-a-gate-export/linux-debug/FunThingsDebug.x86_64
rm -rf /tmp/ft/m1-a-gate-linux-acceptance
python tools/m1_a_gate/run_exported_acceptance.py \
  --executable /tmp/ft/m1-a-gate-export/linux-debug/FunThingsDebug.x86_64 \
  --output /tmp/ft/m1-a-gate-linux-acceptance \
  --rendering-driver vulkan
```

The runner starts every process with `--max-fps 60`, a private writable user root,
and GNU `timeout 180s`. It starts each client only after the host emits a structured
`host_ready` receipt; no startup sleep is permitted. Require:

- `gameplay`: host and client exit zero; both load Brackett and move; client reports
  bounded prediction and remote smoothing; both observe death, respawn, revision-2
  reset, and post-reset input/motion.
- `incompatible`: client reports `INCOMPATIBLE`; both processes exit zero.
- `admission_timeout`: silent-auth client reports `HANDSHAKE_TIMEOUT`; both exit zero.
- `host_loss`: admitted host exits zero and client reports `HOST_LOST`, returns to
  idle, and exits zero.
- Every terminal receipt reports both Steam class and singleton absent.
- Every retained stdout and engine log contains no `SCRIPT ERROR:`, `ERROR:`, or
  `WARNING:` diagnostic.

Observe both 1280×800-capable windows during the gameplay case. Record Vulkan device,
driver, compositor/session type, display scale and contention. This is functional
acceptance, not a frame-time or broad hardware claim.

## Release smoke and owner pair

Run the release shell smoke separately:

```sh
LOG=/tmp/ft/m1-a-gate-linux-release.engine.log
timeout 60s /tmp/ft/m1-a-gate-export/linux-release/FunThings.x86_64 \
  --resolution 1280x800 --max-fps 60 --rendering-driver vulkan \
  --log-file "$LOG" -- --s08-x-export-smoke
```

Require the `S08-X` `boot` and `smoke_complete` receipts, exit zero, Steam absent,
and no runtime diagnostic. Then optionally launch the owner pair:

```sh
rm -rf /tmp/ft/m1-a-gate-owner-pair
python tools/m1_a_gate/launch_exported_pair.py \
  --executable /tmp/ft/m1-a-gate-export/linux-debug/FunThingsDebug.x86_64 \
  --output /tmp/ft/m1-a-gate-owner-pair
```

Focus one window at a time; WASD walks and the mouse aims. Both processes are capped
at 60 FPS and hard-bounded to 180 seconds.
