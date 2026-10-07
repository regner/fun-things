# S04 receipts

This directory retains complete bounded technical receipts, not full S04 acceptance.
`raw-manifest.json` names each stored raw receipt, uncompressed byte count and SHA256.
Logs/JSONL are losslessly gzip-compressed (`gzip -dc path.log.gz`); JSON is plain.
Exact measured fixture sources are retained in `canonical/tested-fixtures.tar.gz`
and `api/tested-fixtures.tar.gz`; result manifests bind all saved dependency hashes.
No caches/user data/tokens are evidence. See [protocol/results](../s04.md),
[source handoff](../../assets/s04_kit.md), [contracts](../s04-contracts.md).

- `protocol-before-measurement.md`: original predeclaration, unchanged; later car
  measurement/scenario amendments are explicit in the spike before canonical runs.
- `canonical`: baseline/normal/adverse separate-process raw host/client engine/stdout,
  seeded actual UDP packet logs, commands/PIDs/exits/source hashes and full outcomes.
- `api`: normally paced body comparison (480 rigid solver samples), untouched passive
  engine body, JSON seated baseline roundtrip plus atomic malformed-cut rejections,
  stale/equal/fresh baseline admission and replacement/rollback/clear checks.
- `checks`: pinned formatting/lint plus explicit all38-owned-script compilation,
  including unused scripts in a fresh full dependency mirror. Import alone is not
  all-script validation. New authoring probe later has an affected follow-up check.
- `reexport`: byte-identical bothGLBs from committed .blend, exporter log/fingerprints.
  Optional absent MeshOptimizer diagnostic is retained, not broadly suppressed.
- `editor`: fresh HOST inventory, preserved saved-main relocation, pinned S04 launch,
  toolkit scene composition/socket operations, actual imported bounds, save/reopen
  and saved/quiescent state. Editor warnings include toolkit's pin compatibility
  warning, automatic new-directory creation and Steam version inventory; these are
  not suppressed or claimed absent. Main originals were not modified.
- `window-diagnosis`: single bounded native1280×800 window attempt, intentional12 s
  diagnostic deadline rather than full22 s gameplay run. Both windows visible with
  `can_draw=false`, no frame_post_draw telemetry. No visible/feel evidence available.
- `failed-attempts`: initial contact reverse failure, JSON baseline handoff deadline,
  old analyzer mismatch (foot-shaped expiry and moving convergence reference), and
  sandbox import socket errors. Failed exploratory receipts are retained but do not
  certify current outcomes; canonical hashes are the authoritative measured version.

Reproduce with the repository's exact pinned binaries (output directories fresh,
outside checkout; native sockets require host access in a restricted sandbox):

```sh
python3 tools/s04/reexport.py --output /tmp/s04-reexport-new
python3 tools/s04/run_checks.py --godot "$GODOT_BIN" --output /tmp/s04-api-new
python3 tools/run_s04.py --godot "$GODOT_BIN" --port 25130 --proxy-port 25131 --output /tmp/s04-enet-new
python3 tools/script_checks.py --godot "$GODOT_BIN" --gdstyle "$GDSTYLE_BIN" --output /tmp/s04-scripts-new
python3 -m unittest discover -s tools/s04 -p 'test_*.py'
```

Do not repeat graphical launch/repair to infer a drawn result. No force-render timing,
renderer/pin changes, production lifecycle framework or replay is part of this spike.

`roundtrip-checks` passes all three public API/body cases after saved inherited boot
normalization; `final-checks` passes pinned format/style and all38 explicit script
compilations including the expanded editor-only probe. `analysis-followup` reruns the
current analyzer on unchanged canonical raw logs, adds explicit physics missing-counts
(zero each), and binds the analyzer source hash. The runner now requires every one of
20 physics samples; it does not accept a p95 over silently omitted responses.
`tools/s04/test_runner.py` independent counterexamples reject coasting-only motion,
foreign/unacknowledged poses and stale active throttle, while allowing coast after
intent expiry. No handling or physics/network measured source changed in that analyzer
follow-up. Save/reopen preserved authored identities and placement; only redundant
inherited instance serialization was removed by Godot.

Blender MCP was unavailable. Fresh HOST inspection found no Blender writer, so the
new source was authored/exported by the exact pinned local CLI. Initial bootstrap
saved the new source but audio teardown stalled; only the two exact owned CLI process
identities were gracefully terminated, with receipts retained. Private null-audio
export/reexport then exited0 with identical GLBs. No unknown process was killed and
no original source was overwritten. Suitable Godot toolkit script/scene/resource
operations authored and saved all owned resources; the temporary authenticated
client used the existing toolkit endpoint when worktree connection discovery failed.
No token/config/vendor mutation was made. A read-only inherited editor probe method
was unavailable; the saved new S04 inspection harness supplies its own bounded probe.
