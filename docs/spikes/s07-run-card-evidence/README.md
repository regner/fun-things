# S07 static run-card evidence

This small package contains new static evidence only. The original accepted inputs
remain reachable at `52941da4b4c92a547a8066b5c13f733043ecbe48`; the later accepted
TODO-only base is `48aef3dbd133876743f504f94a1b788a26d5638f`. No old evidence pack
is recopied. All source/resource/vendor/pin/contract bytes stay unchanged.

- [Inventory](inventory.json): deterministic schema1,186 input fingerprints,14 GLBs,
  33 saved scenes/resources,11 composed placement summaries. Original source/export
  relationships use accepted saved handoff records; no Blender roundtrip is claimed.
- [Raw commission/steering](raw-commission.md), [launch receipt](launch.json) and
  [independent review brief](review-brief.md): This workspace owns the fresh Sol6.1 HIGH
  review, respecting actual concurrency capacity and notifying ROOT without acknowledgement. No review verdict is claimed by this package.
- [Check source](validate.py): independent literal placement sets, expected root/model
  set, scoped fixture-file completeness, all input hash/base readback, camera override,
  finite historical S05 receipt decode, local links/anchors, Python syntax and scoped
  TODO/diff checks. It launches no engine or service and modifies no input file.
- `commands.json`, `pre-rebase.stdout/stderr` and `final.stdout/stderr` retain actual
  static command argv/exits and complete diagnostics, including empty stderr streams.
- `expected-set.json` declares the full payload paths before packaging; `manifest.json`
  binds byte counts/SHA256 read back from that set. The manifest itself is metadata
  excluded from self-hashing; directory equality includes it. No encoded payloads.

Reproduce from repository root with Python3 and Git only:

```sh
python tools/s07/inventory.py --output /tmp/s07-reproduced.json
cmp docs/spikes/s07-run-card-evidence/inventory.json /tmp/s07-reproduced.json
python docs/spikes/s07-run-card-evidence/validate.py --base 48aef3dbd133876743f504f94a1b788a26d5638f
```

The helper deliberately retains original input base52941da; all186 input bytes also
match48aef3d. It resolves this saved fixture subset, not arbitrary Godot import or
runtime semantics. GLB accessor bounds remain mesh-local; saved counts include hidden
placements and omit runtime material creation/spawns/caches. Imported generated LODs,
actual drawable frames, four graphical views, RAM/GPU allocations and capacity remain
unmeasured. T/R/G entry gates in the [prepared cards](../s07-run-cards.md) stay BLOCKED.

Initial implementation diagnostics: the first static helper invocation exited1 on
`AssertionError: ('tests/fixtures/s06/proof.gd', 's06-result.json')`. The actual script
literal names an output rather than an input; the helper now lists absent literal
strings separately and validates saved external dependencies strictly. That tool
response was not captured as a file stream; no invented stdout/stderr payload exists.
Initial unprivileged rebase failed because linked Git metadata is outside the writable
workspace; the authorized escalated rebase succeeded. No engine/check retry occurred.
Final reproduction and validation streams below are separately captured actual runs.

## Independent review and necessary fix

Reviewer `cdc5d0fa-3765-402d-bf3d-7e9f2ab3d4a4`, verified Sol6.1 HIGH/auto-review/
Plan false, requested one P2 change on exact `1ba0f189`/base48aef3d: T lacked an
accepted repeated-route/reset driver. The complete original report, actual sources,
argv/exits/full streams (including failures/empty streams), reproduced inventory and
all80 payloads plus original manifest are retained byte-for-byte in
[the initial review archive](review-initial.tar.gz).
[Its receipt](review-initial-package.json) binds the complete explicit source set,
source hashes, archive and decoded readback. Earlier reviewer retention failures/
source versions are preserved in that package; provisional payload counts are history.
The [retention source](retain_review.py) archives an explicit set without pruning.

The narrow T fix names the missing driver, later S07 worker/S06 acceptance ownership,
restoration/reload constraints and actual repeated-traversal acceptance, and blocks
primary launch until those receipts exist. No driver, source inventory, fixture or
TODO change is part of the fix. `post-fix.stdout/stderr` retain the affected static
check. The SAME reviewer supplies compact exact-final delta disposition before handoff.
After this necessary fix/review/retention, the workspace remains idle under deferred
pause steering; no new workstream or broader audit is assigned.
