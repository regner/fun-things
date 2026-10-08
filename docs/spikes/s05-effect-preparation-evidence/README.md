# S05 source-only preparation evidence

This directory retains original authoring, exact command arrays, complete stdout/
stderr, exit/reaping records, source/export hashes and static inspections. The
[handoff](../s05-effect-preparation.md) declares criteria, observations and limits;
[pending Godot card](godot-request.md) grants nothing. No screenshot/runtime/import
or fabricated UID is included. Read reports and raw streams, not just exit codes.

- `author.py` is the one-time original Blender bootstrap, refuses overwrite.
  The committed `.blend` is the editable source, not a runtime generator.
- `export.py` exports the declared saved collection without rebuilding geometry.
  It consumes accepted `tools/s01/export_settings.json`, disabling UV/skins/animations.
- `run_blender.py` and `commands.json` retain initial creation, probes/reopen/exports.
  Initial author stdout contains a blocked shared extension-cache attempt;
  author stderr contains Blender's use_nodes deprecation. Do not delete/relabel it.
- `private_check.py` / `private-commands.json` retain corrected private user-path
  environment, installed `--help`, saved-source probe and identical scratch export.
  All9 Blender children were reaped normally; no termination fallback was used.
- Three export stdouts retain the optional missing MeshOptimizer diagnostic.
  Exported bytes contain no compression extension; no vendor/library repair occurred.
- `source-probe.json`, `reopen-probe.json`, `private-probe.json` are byte-identical
  source/material/dependency checks. `fingerprints.json` and `private-check.json`
  retain installed binary/source/export identities and reexport results.
- `check_glb.py` / `glb-check.json` / `glb-structure.json` independently decode all
  exported accessors/triangles, check finite normalized normals, closed welded edges,
  Y-up bounds and literal occupied/open XZ probes. Static gaps are not drawn evidence.
- `inspect_isolation.py` / `isolation-source-receipt.json` inspect accepted toolkit
  source and installed server/binary metadata. They launch no editor/bridge, inspect
  no registry/token credentials and query no shared process/service/app. Git blob
  references keep accepted sources immutable without recursively copying histories.
- `record_checks.py` / `check-commands.json` retain full non-editor check raw streams.
  `model-receipt.json` is the actual own-agent configured/effective HIGH snapshot.
- `godot_help.py` / `godot-help-command.json` and complete raw help stdout/empty
  stderr retain root's separately authorized five-second metadata-only invocation.
  No editor/project/runtime was loaded; DAP/debug-server/LSP semantics are documented
  by the exact pinned binary. Actual isolated editor operation remains ungranted.
- The original `manifest.json` / `preservation.json` are immutable initial-base
  receipts. `final-manifest.json` / `final-preservation.json` bind the accepted-main
  rebase and the complete current expected set; old receipt scopes remain historical.

Reexport the existing source with a PRIVATE environment matching private-commands:
`/usr/bin/blender --background --factory-startup --python-exit-code 1 <source>
--python <this-directory>/export.py -- <new-private-output.glb>`; compare bytes
before replacing any output. Never rerun the bootstrap on an existing source.
The nine subprocess arrays and logs are historical observations with their actual
temporary paths. Scratch directories stay under /tmp, not normal art paths.

Full S05 remains open: actual Godot import/link/identity roundtrip, eight drawn
effects/drop behavior/live versus settled-hydrated, cosmetic lifetime cleanup,
Regner policies/final dimensions/contact and other documented downstream gates.
There is no whole-repo compilation, ENet rerun, graphical/device/performance claim
for a new unimported source model. Independent review and exact-final readback are
retained with the reviewed revision; prior review histories remain Git-blob references.
