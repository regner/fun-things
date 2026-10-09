# S08 — Windows observation and held-input stall root cause

8 October 2026. Work branch `s08-enet-bandwidth`. The observation ran on revision
`828df1214cb3306ee05f7792bf10d4237ae3c530`, which this record's commit follows. Platform: Windows 11
(10.0.26200), with the pinned engine from Mise
(`4.8.dev7.official.c971f93e7`, 194052248 bytes, SHA256 `7129acb9…`). The user
authorized testing on this machine and asked that Linux-only concerns be recorded
for implementation-time review rather than block progress. [Evidence](s08-windows-evidence/)
keeps results and full role streams; binaries, scratch projects and private user
directories were not committed.

## Outcome

**The original-main held/resync stall is explained and fixed.** It is caused by an
upstream Godot argument-order defect in `ENetMultiplayerPeer::create_server`, not by
release templates, native signal caches, S08 assets or the 20 ms proxy itself.
With the fix, the **exported saved S08 main passes the full S03 matrix in both
Windows RELEASE and DEBUG** at the original 20 ms servicing. Both sets have zero
engine/script diagnostics and empty stderr.

| Set | Before fix (`fb1a372`) | After fix (`828df12`) |
| --- | --- | --- |
| Exported S08 main, Windows RELEASE, 20 ms | Host `case deadline in ACTIVE`; client stalls at first post-admission held send (seq 1, expected OK) | PASS: 2 host / 4 client cases, exits 0, five proxy datagrams, 173 S08 checks per role, handoff 1.245 s |
| Exported S08 main, Windows DEBUG, 20 ms | Same stall | PASS, handoff 1.166 s |
| Editor-run minimal S03 (`prototypes/s03/tools/run_s03.py`), 20 ms | Stalls at the STALE_SEQUENCE held send | PASS 5/5 runs |

The two pre-fix stalls hit different held sends. That pointed to sender-side loss of
the unreliable `_held` RPC rather than a deterministic gameplay edge.

## Root cause

The separate [upstream defect write-up](../upstream/godot-enet-create-server-bandwidth.md)
provides exact pin/`master` source links, a runnable MRP, measured before/after logs,
and the report/fix draft.

1. Scratch-only telemetry ([diff](s08-windows-evidence/throttle-telemetry/proof-scratch-telemetry.diff))
   logged ENet peer statistics at each proof event. Just before the lost send,
   the client's peer for the host fell from `PEER_PACKET_THROTTLE_LIMIT` 32
   (`PACKET_THROTTLE_SCALE`, send everything) to **1**. ENet then drops roughly 30
   of every 32 unreliable packets at the sender: counter positions 0 and 1 pass. The `_held` RPC is
   `unreliable_ordered` channel 2; its reliable `_result` therefore never comes,
   and `_send_expect` waits until the host's 8 s case deadline. Setting throttle
   deceleration to 0 did not help, which ruled out RTT-jitter throttling.
2. The limit comes from ENet's bandwidth throttle (`enet_host_bandwidth_throttle`),
   which only applies when the remote peer advertises a non-zero incoming bandwidth.
   Pinned `modules/enet/enet_multiplayer_peer.cpp` (c971 and current `master`)
   calls `host->create_host_bound(bind_ip, p_port, p_max_clients, 0,
   p_max_channels > 0 ? p_max_channels + SYSCH_MAX : 0, p_out_bandwidth)`, while
   `ENetConnection::create_host_bound` takes `(…, max_peers, max_channels,
   in_bandwidth, out_bandwidth)`. The channel count lands in **in_bandwidth** and
   `p_in_bandwidth` is ignored. S03Transport calls `create_server(port, 3, 4)`, so
   the server advertises 6 bytes/s. Each client's throttle limit collapses at its
   next one-second bandwidth epoch.
3. This also explains the history without any release/native cause. The collapse
   happens at the next ENet one-second bandwidth-throttle epoch, which can fall
   less than a second after the client host is created (366 ms in the retained
   telemetry). Fast sequences
   (minimal S03 under unplanned 10 ms servicing) can finish before it. Slower
   ones (original S08 main under 20 ms servicing) cross it. It is
   platform-independent ENet behaviour; the Linux re-run is listed under concerns.

The initial search on 8 October 2026 missed existing reports. Follow-up search found
open [godotengine/godot#123963](https://github.com/godotengine/godot/issues/123963)
and archived [#123254](https://github.com/godotengine/godot/issues/123254). Do not
file a duplicate; the owner should review the [pinned-version MRP and comment draft](
../upstream/godot-enet-create-server-bandwidth.md) offline before posting to #123963.

## Fix and checks

- [S03Transport](../../prototypes/s03/tests/fixtures/s03/transport.gd), the native-peer owner, calls
  `candidate.host.bandwidth_limit(0, 0)` after `create_server`. That restores the
  intended unlimited bandwidth and stays harmless if upstream fixes the order.
  Channel behaviour is unchanged, because the defect already passed 0 (maximum)
  as the channel limit. Every fixture using S03Transport inherits the fix
  (S03, S03-R, S04, S05, S08).
- [S03Proof](../../prototypes/s03/tests/fixtures/s03/proof.gd) asserts that the client's host-peer
  throttle limit equals the engine constant `PACKET_THROTTLE_SCALE` at the end of
  the subset case. The expectation is independent of the fix's formula.
- Windows runner corrections:
  - [`environment()`](../../tools/script_checks.py) now also redirects
    `APPDATA`/`LOCALAPPDATA`, because Godot on Windows ignores XDG. Before this,
    host and client shared one user directory (`process user directories overlap`).
  - The S03/S03-R/S04 proxies ignore Windows `ConnectionResetError`. Windows
    reports an earlier ICMP port-unreachable, such as one to a canceled client's
    closed socket, on the next `recvfrom`; Linux does not.
  - [Offline tests](../../tools/test_foundation_tools.py) cover both behaviours.
- [Windows observation tool](../../prototypes/s08/tools/s08/windows_observation.py):
  - Verifies the downloaded TPZ (1436879719 bytes, SHA256 `95c26775…`, the same
    archive as the Linux records) and its Windows members (`windows_release`
    `b538554d…`, `windows_debug` `c3287ae1…`). The Linux release member also
    matches `c436b976…`.
  - Stages the 34-file S01/S03/S08 closure from a Git revision, imports, and
    exports both modes into a fresh external directory without installing
    templates.
  - Runs one host/client set per mode under one absolute 30 s budget: 4 s handoff,
    20 s work, then shared grace/terminate/kill cleanup.
  - [Offline export-gate tests](../../tools/test_windows_observation.py)
    reject zero-exit import/export diagnostics and a missing engine.
  - Fixed release PCK: 182948 bytes, SHA256 `e6bea4d4…`; the debug PCK is
    byte-identical.
- All-owned compilation, pinned formatting and tool tests pass. Lint retains only
  the three pre-existing S07 driver warnings recorded in its evidence.

## Deviations from the unexecuted Linux card

The [source-diagnosis card](s08-source-diagnosis.md) assumed the original Linux
package and `stdbuf -oL`. This observation knowingly differs:

- Windows templates rather than the Linux release template. The original
  `74f2526b…` PCK and Git notes are not present in this clone. The closure is
  restaged from Git; HEAD's S03 Proof/Session include the accepted additive
  lifecycle telemetry.
- The scratch project sets `application/run/flush_stdout_on_print=true` for live
  readiness. This is the same output-delivery role `stdbuf` played, not a gameplay
  change.
- Exploratory sets were not limited to one attempt, at the user's direction. All
  attempts and failures are retained.

## Concerns for implementation-time review

1. **Linux release `tree_exited` diagnostics remain unverified.** The upstream
   strict-aliasing defect in `CallableCustomMethodPointerBase::_setup` hashing
   ([PR #123998](https://github.com/godotengine/godot/pull/123998), open; it
   supersedes the `new` inlining band-aid #120394 that c971 already contains)
   matches the historical Linux-only, release-only missing-disconnect and
   duplicate-connect pattern. The Windows MinGW-built release template showed none in
   either release set (before or after the fix), nor did either debug set. Re-run on Linux with this fix. Choose a pin once upstream merges the
   hashing fix. These diagnostics coexisted with passing gameplay, but they still
   fail strict diagnostics.
2. **Linux re-run of the 20 ms original main** is needed to confirm the fix there.
   The mechanism is ENet code shared by all platforms.
3. **Historical S03-R/S04 response figures are confounded.** Those client inputs
   used the same throttled channel. See the dated notes in [S03-R](s03-r.md) and
   [S04](s04.md). Windows re-measurements are below; they are not Linux-comparable.
4. **Windows latency is higher than historical Linux.** Headless Windows physics
   response p95 is higher even with no impairment. A
   [retained analysis](s08-windows-evidence/s03r-fixed-01/analyze_jitter.py) of
   the post-fix baseline logs shows uplink held input reaching the host in 16–115 ms.
   The client applied 368 host motion rows, against about 440 sent (one per three
   of 1319 ticks), with apply gaps p95 155 ms for a 50 ms interval
   ([output](s08-windows-evidence/s03r-fixed-01/analyze_jitter.json)). A bilateral
   scratch-only run with throttle deceleration 0 on both peers
   ([diff and result](s08-windows-evidence/s03r-scratch-no-deceleration/)) cut
   baseline response p95 from 255 to 110 ms and raised matching-tick samples from
   733 to 865. That is consistent with ENet's RTT-jitter throttle contributing,
   but does not isolate the direction. It is **not adopted**: the throttle is
   congestion control, so throttle/rate policy belongs to the M1-A1 transport owner
   with bandwidth budgets. Windowed runs (below and in the S03-R/S04 records) are
   much faster than headless, so headless Windows pacing is also a factor. The
   scratch run failed only S03-R's expiry criterion, by 1 ms (previous tick age
   251 ms against `≤ 250`), a fixed-boundary check that is fragile to tick jitter.
5. **Production transport:** any future ENet adapter must apply the same bandwidth
   restoration (or a fixed engine) and treat unreliable held/motion traffic as
   lossy. See [multiplayer](../multiplayer.md).
6. Windowed S03-R/S04 runs drew real 1280×800 frames here (see their records).
   Physical input, Steam, Deck, Gaming Mode and export delivery remain untested.

## Windows S03-R/S04 re-measurement (post-fix, headless)

| Runner | Baseline | Normal | Adverse |
| --- | --- | --- | --- |
| S03-R physics response p95 | 255 ms, 20/20 | 268 ms, 20/20 | 400 ms, 20/20; all technical criteria PASS |
| S03-R pre-fix baseline | 252 ms, missing samples → criteria FAILED | — | — |
| S04 physics response p95 | 176 ms, PASS | 430 / 362 ms in two runs; each FAILED with 2/20 samples beyond the 500 ms window | not reached (runner stops at the first failed profile) |

S04 normal's failure is a measurement-window/latency result on this platform, not a
correctness failure: collision, expiry, resync, matching-tick install and recovery
all passed.

## Status

The S08 original-main/20 ms stall question is **answered and fixed on Windows**.
Clean Windows release diagnostics pass for this fixture. Still open: Linux
confirmation, the Linux release signal diagnostics (upstream engine fix/pin), export
delivery/target compatibility, Steam-uninstalled/optional-service behaviour, Deck/
Gaming Mode, and graphical/input checks.
