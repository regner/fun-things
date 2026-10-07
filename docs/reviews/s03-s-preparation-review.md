# S03-S preparation independent review

7 October 2026. Reviewer: independent clean-context transport reviewer
(`/root/transport_review`), GPT-6.1-Sol, high reasoning.

**Verdict: approved for the bounded preparation scope; no actionable findings.**
This approval does not complete S03-S, S08, P0-GATE or dependent production
acceptance. Real Steam testing and LCD/OLED Deck testing remain explicitly deferred.

Exact reviewed candidate: `473567fa3de1114106f15c336dd98224b4632bb9`, branch
`s03-steam-preflight`, against local main
`81efb403fedb1e02eba8d4a0ddc37d73a5f64b17`. Candidate HEAD and clean status were
confirmed before writing this report. This report is the reviewer's sole repository
write and is uncommitted for the author to retain with the resolving change.
Any subsequent substantive revision needs an explicit follow-up disposition.

## Scope and contracts examined

Read AGENTS.md; raw current and base S03-S/S08 TODO text; design's existing-app,
toolchain, targets and historical decisions; S03 boundary/fixture/evidence;
relevant session/admission/transport/channel/lifecycle contracts; multiplayer,
architecture and development guidance; the orchestrator review/model policy and
Godot MCP Toolkit guidance. The review did not use the shared Godot/Blender session
owned by S02. Isolated CLI checks used a fresh `/tmp/s03-s-review` project.

The ten-file candidate diff contains only TODO/design supplements, the preparation
record and evidence. No vendor addon, pin, API contract, fixture, source asset or
live configuration changed. Original S03-S/S08 cases remain present. No duplicate
gate or silent requirement reduction was introduced. The dated supplement retains
the provisional Deck engine decision and existing VCS delivery obligations.

## Independent evidence checks

- Fresh read-only Codeberg downloads independently verified both release tags via
  `api/v1/repos/godotsteam/godotsteam/git/refs/tags/<tag>`: `v4.23-gde` resolves to
  `532740f3f9c6a826c68914db81af9de1e32d5dc3`; `v4.23.1` resolves to
  `37cc25db782a58a60a4f7b0971782f08769a8f5d`. Release API metadata identifies
  Godot 4.4+, SDK 1.65, versions 4.23 and 4.23.1. The release pages were unavailable
  through the browser fetch tool; direct public API/raw downloads succeeded.
- Independently downloaded the archive at the manifest's exact release URL:
  27,592,373 bytes, SHA-256
  `c1728b4bf330da851a00eaf64dab2e99c506018b1d9f529511b25d7fe7649e97`.
  Python `zipfile`/`hashlib` comparison verified all 22 installed native/configuration
  files byte-for-byte against the archive and the committed manifest. Fresh raw
  immutable-source downloads matched all eight recorded source hashes, including
  the identical patch peer/packet files. This establishes published-byte provenance,
  not a reproducible native build or runtime correctness.
- `readelf -d`, `readelf --version-info` and `objdump -p` independently confirmed
  the documented Linux x86_64 debug dependencies, `$ORIGIN` RPATH and maximum
  GLIBC 2.25 requirement, and the three Windows debug DLL imports. These observations
  do not establish Windows or SteamOS execution or release-export dependency delivery.
- Re-read immutable peer/packet/settings sources: P2P uses Networking Sockets;
  ordered-unreliable maps to reliable and receive mode reports only reliable/plain
  unreliable; `p_channel >= configured_lanes - 1` falls back to zero; default lanes
  are four. Thus channel 3 falls back at the default setting, and five lanes alone
  cannot fix ordered-unreliable. Lane configuration and send-message results are
  unchecked at the inspected call sites. The record correctly refuses conformance.
- Re-read initialization/lobby/diagnostic sources: `steamInitEx` exposes status/verbal
  diagnostics; create-lobby retains one call result without exposing its handle;
  join-lobby discards the native request handle and its callback includes the lobby
  ID. The record preserves serialized/drained operation requirements instead of
  treating a local counter or ENet's close delay as safe Steam correlation.
  Native account/peer mapping and host ID 1 are inventory, not admission proof.
- Current primary sources confirm [lanes and P2P sockets](https://partner.steamgames.com/doc/api/ISteamNetworkingSockets),
  [message size and fragmentation flags](https://partner.steamgames.com/doc/api/steamnetworkingtypes),
  [relay availability](https://partner.steamgames.com/doc/api/ISteamNetworkingUtils),
  [initialization requirements](https://partner.steamgames.com/doc/sdk/api), and
  [package/depot testing access](https://partner.steamgames.com/doc/store/testing).
  The record distinguishes a 512 KiB native send ceiling from tested RPC budgets,
  and relay readiness from an observed connection route. Expresso's current
  [maintainer README](https://github.com/expressobits/steam-multiplayer-peer) confirms
  paused development/no channel support; its historical GodotSteam comparison is
  correctly treated as stale rather than applied to the exact bundled source.
- Read-only VCS VDF/runtime/guide inspection confirmed AppID 5294580, Windows/Linux
  depots 5294581/5294582, executable recipes and absence of `SetLive`. These repository
  facts cannot verify live app type/release/packages/testers/launch/branch settings.

## Fresh isolated CLI check and log review

Copied the installed addon and committed probe/project text into
`/tmp/s03-s-review/probe`, with separate XDG data/config/cache directories.
Used `/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot`
through Python `subprocess.run`, with a 30-second bound for each invocation:

| Invocation | Independent result |
| --- | --- |
| `--version` | Exit 0; `4.8.dev7.official.c971f93e7` |
| `--headless --editor --path <scratch> --import` | Exit -6; socket creation/listen errors in restricted environment; failed, not counted as import acceptance |
| `--headless --path <scratch> --script res://probe.gd` | Exit 0; completion marker; no engine/script diagnostics; singleton/classes present, version 4.23, auto-init false, max_channels 4 |

Reviewer logs are `/tmp/s03-s-review/probe/{version,import,registration}.log`; full
fresh API data is `registration.json` there. Selected retained registration methods,
signals and getters matched the fresh result exactly. The committed JSON explicitly
labels its projection. Original restricted-import log retains secondary rich-text
diagnostics too; neither it nor the reproduced socket failure establishes a vendor
crash cause. All reviewer subprocesses finished.

`git diff --check <base> <candidate>` passed. Both evidence JSON files parsed;
local file links and Markdown anchors in changed Markdown passed. No sensitive
credentials, keys, passwords or account identifiers were found in the new evidence.
No blanket gameplay tests were run for this documentation preparation.

## Constraints and next work

Local registration exercised only version/settings getters. Native Steam
initialization, authenticated connection identity, cancellation/drain, actual
gameplay modes/channels, route diagnostics, exports and target execution remain
unproved. The next compatibility experiment is bounded and explicitly conditional;
it must establish four streams and ordered-unreliable semantics without a hidden
reliable fallback or production framework expansion.

S03-S retains the actual-app, distinct-account/separate-machine/network tiny
admitted baseline/intent, lobby/invite, route and canceled-attempt cases, with live
partner prerequisites. S08 retains exact engine/templates, LCD/OLED Gaming Mode,
controller/native-init, native 1280×800/60 FPS, offline, suspend and private install/
update/launch acceptance. Availability answers are deferral, not pass or waiver.
No renewed access question, substitute account/device, service mutation, upload,
publishing, merge, archive or push was performed.
