# S07 driver predeclaration — 8 October 2026

Base `233493abc7d2e3c106fb620105cfb766f542813b`; branch
`s07-sustained-route-reset-driver`; workspace `wks_08760af59ce23966`.
Direct Sol6.1 HIGH implementer (PI_PROVIDER=openai, PI_MODEL=gpt-6.1-sol,
PI_REASONING_LEVEL=high verified once). ROOT coordinates, does not implement.

Only new `tools/s07_driver`, `tests/fixtures/s07_driver`, this record/evidence,
exact primary T driver-prerequisite cells in `docs/spikes/s07-run-cards.md` and
S07 TODO/table cells are owned. Original S02/S04/S06 and all assets/UIDs/bakes stay
unchanged. No S05 comparator/effect reset. No graphical/display/native addon,
Steam/accounts/devices, pin/renderer changes or shared editor/config/service access.

## Exact scenario and before-engine limits

One new saved scene inherits `tests/fixtures/s06/intersection.tscn` unchanged,
overriding only its root script with a subclass exposing one-shot admission and
owned cancellation. No new runtime-authored nodes/placement. The executable
SceneTree driver instantiates that saved scene, assigns standalone authority before
tree entry, validates all three saved starts/passive roles and S06 content, and
calls existing `start_route`. The inherited owner alone steps actual S02/S04 bodies.
Route order: foot, east_to_north, west_to_south, repeat. Each repetition neutralizes
and clears commands, queues free, observes actual retirement, then instantiates the
saved fixture afresh. No direct pose installation, teleport or runtime rebake.

Starts/yaws: foot(-20,0.001,6.5)/-pi/2; CarWest(-20,0,2.25)/-pi/2;
CarEast(20,0,-2.25)/pi/2; velocity zero. Destinations:
foot(20,0.001,6.5)/-pi/2, north(2.25,0,-20)/0, south(-2.25,0,20)/pi.
Use unchanged S06 1200/1800-tick deadlines and speeds. Require nonempty per-tick
samples, actual displacement, literal destination <=0.5m and heading <=10 degrees,
zero contacts, one continuous seam passage and legal source-derived footprints.
Timeout is failure. Passive collision/cleared producer/stopped velocity must precede
completion notification. Restore/revalidate ALL starts before every new binding.

At least two actual consecutive traversals of each route in the short group.
Sustained group runs paced headless physics over >=600 actual monotonic seconds,
finishing the final admitted route (no incomplete traversal counted as success).
Record simulation delta separately, and separate monotonic load/admission,
traversal, cancellation/retirement phases. Reload is NOT normal traversal/performance.
No FPS/GPU/drawn/capacity/readability claim. Independent analysis checks literal
starts/destinations, source road/crossing envelopes, footprints, seams and contacts.

Total lead effort <=3h, starting with this task session. All attempts count:
- <=1 private headless editor, <=1500s including owned cleanup. Standard installed
  auto-allocated discovery, token and canonical project/PID binding, no pinned
  Toolkit endpoint. Ancillary engine listener ports privately allocated.
- <=1 addon-free minimal closure import, <=90s INCLUDING owned cleanup.
- <=2 short simulation groups, <=120s EACH including compiles/guards/cleanup.
  Group1: compile all three new scripts, guards and two full cycles. Group2 reserved
  for material fixes or independent reviewer runtime; no unchanged lead retry.
- <=1 sustained simulation group, <=660s INCLUDING owned cleanup. Actual requested
  interval600s, complete last route, fail on correctness/admission/error or deadline.

HOME unchanged. All engine children use fresh private XDG scopes and recorded
Popen handles, reaped with bounded cleanup; no process-name scan. Editor mirror has
only unchanged Toolkit addon, no Steam/native addon/autoload. Runtime mirror has
no addons/autoloads. No shared editor query. Ordinary owned request/supervisor
mistakes recover only within these counts; uncertain identity/unsaved risk/new
shared resource/access/scope or exhausted total budgets escalate to ROOT.

ROOT explicitly authorizes byte-for-byte reading/copying the successful private
EditorSettings seed named by committed `tools/s05_draw/private_author.py`:
`/tmp/s05-author-56eb6b28-run01/config/godot/editor_settings-4.8.tres`. Bind source
and copied bytes/SHA; actual seed and authenticated context must show boost=false.
Never synthesize/edit the seed or mutate shared settings. Missing/incompatible seed
means no editor launch. Bounded no-editor fallback is authorized only for scripts/
tools reusing existing saved fixtures without new hierarchy/placement; no claimed
roundtrip. New saved scene composition requires suitable editor authoring.

## Review and retention

Freeze/commit; commission one fresh clean-context Sol6.1 HIGH reviewer on exact
HEAD/base, complete raw requirements/contracts/check sources/receipts, without
implementer verdict. Same reviewer disposes material fixes/rebases. Reviewer runtime
must use the unspent second development group, not a second sustained/import/editor
attempt. Static independent review needs no editor lock. Retain full reports,
actual check sources/argv/exits/full diagnostics/failures/required empty streams;
one expected-set/SHA/readback on the proportionate evidence set. Immutable base
references bind old S06/S02/S04 data; do not recursively copy their evidence packs.
No merge/archive/push. Full S07/P0/product/platform gates remain open.
