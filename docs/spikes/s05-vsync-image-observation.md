# S05 conditional disabled-VSync image observation — 8 October 2026

Workspace `wks_d1e27dac99ebaab3`, branch `s05-vsync-image-observation`, original
commissioned base `3f5fb4067c5ce5fca721f54d42165a833e4c884c`. Lead pi session
`01a11bc0-4150-732b-9910-86aadb16c700` verified effective OpenAI/GPT-6.1-Sol HIGH
once through PI environment; no mode/features. ROOT parent
`56025a67-0fb8-4968-8d02-1fbec744bb12` owns integration/archive; no worker push.
Complete [raw commission](s05-vsync-image-observation-evidence/raw-commission.txt)
and [Card I](p0-drawable-route.md#proposed-card-i--conditional-automatic-s05-workload-images)
are the authority and exact acceptance, not the historical consumed grants.

## Question and immutable prerequisites

Can **one** run of the real saved S05 burst produce automatic workload PNGs with
process-local `--disable-vsync`? This is an optional **low-confidence changed
presentation mode**, not a demonstrated timeout/suspension fix or bypass. Discovery
advertised `wp_fifo_manager_v1`: manual VSync emulation may already be inactive.
The original group02 argv did not disable VSync. Effective disabled VSync alone
cannot establish drawability or close any native criterion.

Original [saved presentation](s05-saved-presentation.md),
[render observation](s05-render-observation.md) and [contract](s05-contracts.md)
remain immutable at the original base, including both failed graphical groups,
empty PNG sets, original executed camera-path defect, final source-only corrections
and independent reviews. Their in-place evidence indexes identify complete original
streams; no vanished `/tmp` path is recreated as historical evidence.

Reuse `tests/fixtures/s05_draw/burst.tscn`, saved camera at `(6,47,4)`, vertical -Y,
yaw0, perspective42°, near0.1/far160, the Blender-linked eight saved slots and
unchanged twelve-car burst. All scenes, node IDs/placement, UID sidecars, Blender/
GLB/import source bytes, gameplay/replication/ENet rules and event schedule remain
unchanged. The accepted natural expiry wait is not altered. The proof's original
pre-network API/negative fixtures are not workload images/events.

## Script-only preparation and private protection

Accessible tool-name discovery returned no Godot/editor authoring tool. ROOT
expressly permits the limited direct-file **observation script only** fallback.
No scene/node mutation, editor session, save/reload roundtrip or editor playtest is
claimed. Initial checkout was clean at exact commissioned base; no unsaved work is
discarded. The modified observer is refreshed by copying its exact frozen bytes
into a **new private runtime project**; no separate open editor is involved.

`tests/fixtures/s05_draw/observer.gd` retains its UID/public APIs/resource path.
Its existing `uid://dljjuwyn8s77o` sidecar is byte-preserved and copied at the same path.
Instrumentation reads supported `window_get_vsync_mode`/`window_can_draw`, requested
project size, actual native window/root viewport and callback-bound image size
separately. Internal `can_any_window_draw` is null with an unavailable reason;
there is no native bridge, call or inference. Cap65536 is an observation failure
if exhausted. Sparse rows retain first three callbacks, meaningful state/dimension/
mode changes and each capture; ticks alone no longer produce rows. Captures add
current cut/session/match/tick/revision and actual PNG SHA256, without advancing an
owner, injecting effects/expiry/churn, forcing draws or emitting frame signals.

New `tools/s05_vsync_image/run.py` owns one fresh
`/tmp/p0-image-01a11bc0-attempt01/` project, four private mode0700 XDG roots per
import/host/client/late role and exact Popen handles. HOME is unchanged. The
existing `/run/user/1000/wayland-0` socket is shared **read-only**; type/UID/canonical
path/inode/device are checked at attempt entry and before each graphical spawn.
No exclusive output ownership is inferred. ROOT permits these fresh owned windows;
other workers are headless/private. No shared editor/UI/window/config/service is
queried, changed, focused, activated, resized or supplied input. Any discovered
identity/conflict/unsaved-work risk stops before further launch.

Stage only transitive saved paths and fixture class dependencies, preserving UID
and source import sidecars, with8MiB cap including private project settings. Only
private autoload/editor_plugins declarations are removed; display/input/physics/
rendering/quality settings are unchanged. No toolkit/native Steam addon is copied.
One minimal headless closure import may generate only this private project's caches;
generated outputs/bytes are ledgered separately. This is not a whole-project import
or all-script validation. No engine call is permitted outside the attempt.

An OS-selected loopback UDP port is released before the existing ENet owner binds
it. Before live launch, `/proc/<owned-host>/fd` socket inode and `/proc/.../net/udp`
prove the owned listener is bound to127.0.0.1 at that exact port. Actual role
PID/start/argv/executable/project/env/handles and socket identity are retained.
There is no historical fixed port, private MCP endpoint or global editor lock.

## Committed single-attempt protocol

Total lead preparation/collection/retention/review-fix cap60min begins at the lead
session's13:42:26Z start, ending14:42:26Z. One120s monotonic absolute deadline begins
**before runtime closure staging/hashing**. First90s: stage/hash/one minimal import;
next at most20s: real-time collection (also bounded by actual collection start+20s
and absolute start+110s); shared cleanup6s; readback4s. Early launch never extends
the absolute cutoff. Preparation failure consumes the attempt. Stop before any
spawn at cutoff. No second graphical group, runtime replay or fallback follows.

Exact graphical argv (private `<P>`, `<R>`, OS-selected `<port>` resolved and written
in lifecycle receipts before each spawn):

```text
/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot
  --audio-driver Dummy --disable-vsync --path <P> --display-driver wayland
  --log-file <R>/engine.log res://tests/fixtures/s05_draw/burst.tscn
  -- --role=<host|client|late> --port=<owned-loopback-port>
```

Minimal prerequisite argv, at most once inside the same clock:
`godot --headless --path <P> --import --log-file <import-role>/engine.log`.
Binary SHA256 must remain
`6aea356032435e7af19dbfbf48dd20c5012a7dc1267eb8e92406f44e3584b5fd`, exact engine
revision `c971f93e7e76b0ef919bf6009e7b868bea04db7f`. Forward+/Wayland/Dummy unchanged.
Host actual ready precedes live; actual host settled precedes late.

Normal existing Session.leave/result/SceneTree.quit comes first. Failed handles
alone receive shared2s SIGINT, shared2s terminate, shared2s kill/reap intervals;
never per-child grace or process-name kills. Nonzero/interruption/fallback/diagnostic/
overrun/unreaped handle stays failed. All separate streams including empties close.

Offline pre-engine checks: Python AST/source preservation/saved-camera UID/resource/
API checks, pinned gdstyle0.3.0 zero-warning lint, and actual-runner fake-clock
normal completion/preparation cutoff/import timeout/three stubborn children/live
spawn at cutoff. No engine or real socket executes in these checks. Full check
sources/argv/exits/failures/diagnostics are retained, not just successful summaries.

## Exact acceptance and remaining gates

Card I requires actual effective VSYNC_DISABLED per role, genuine increasing
post-draw callbacks through real workload and at least3 callbacks before capture;
host+live baseline/eight **distinct** linked slots/four-drop burst/naturally expired
PNGs, and settled-late twelve-wreck/zero-historical-effect PNG. Each direct viewport
readback is bound to actual saved camera, role/session/cut/tick/revision, physics/
render indices, events/watermark/counters and source links. No crop or resize.
Independent image inspection of **actual collected PNGs** must assess car/effect
relationships and live-versus-hydrated distinction. Nonblank/counts alone do not pass.

Original twelve real EventIds, health0/explosion1,144visits, live12/duplicates12,
8accepted/4dropped, fence/negative/admission checks, natural expiry and hydration
before input must survive. All roles exit0 normally without new diagnostics, within
phase/aggregate deadlines, with complete bounded teardown/source preservation.
Missing stage/callback, cap exhaustion or unavailable observation remains failure.

Even an IMAGE partial pass leaves native resolution/viewport/output matching,
can_draw/input/focus/scanout/feel, final dimensions/spacing/contact/blast/wreck policy,
readability/user ratification/hardware cost, admitted-player transactions/during-chain
join/reset/races/sustained capacity, Deck/Steam/full S05/S07/S08/P0/M1 OPEN. This
card cannot close full S05. Steam remains Valve API/interface research only; live
testing is deferred. No new workstream is launched by this worker.

## Evidence and independent review

The evidence package will retain complete separate import/role/supervisor streams,
executed sources/settings/UID/imports/argv/env/identities/endpoint/observer JSONL,
actual PNGs (or exact absence lists), evaluator outcomes and all failures. One
declared expected-set/stored+decoded hash/readback covers the package; original
historical groups are referenced at the base, never recursively recreated.

Freeze a committed saved/clean/quiescent candidate for one fresh clean-context
pi/OpenAI GPT-6.1-Sol HIGH reviewer. ROOT's13:39–41Z receipt reports zero fitting
profiles, pi available/no modes/features and verified model/high IDs; launch with
no modes/features and verify effective once. Raw commission/card/base/exact HEAD
are supplied without an implementer verdict. Same reviewer disposes material fixes
or docs-only rebase; all review fixes/checks are offline, with **no runtime replay**.
Metadata-only unchanged-candidate review retention needs no extra acknowledgement
or report-only tree commit. ROOT integrates/archives; the worker never pushes.

## Actual single-attempt result: IMAGE FAIL, consumed

Executed source candidate `4a50808ba0441a7c116d14d78a4286a6f89f7691` at exact original
base above. Supervisor PID721366; wrapper PID721365. Start13:56:07.545Z through
readback13:56:12.642Z, **5.096420s** total inside120s. Runtime closure61files,
**236947source bytes** including copied project settings, versus8MiB cap. Generated
private import outputs16files/**124103bytes**, separately ledgered. The socket's
fresh canonical path/type/owner1000/inode90/device72 checks matched before host use.
No endpoint was contacted by an editor tool; no existing UI was controlled.

- One minimal private import PID721438 exited0 normally, no engine/script warning/
  error and empty stderr. It imported three linked GLBs and the original icon,
  registered the closure's20classes, and made the new private cache. This is not
  whole-project compilation, authored scene saving or interactive acceptance.
- One graphical host PID721561 used the exact card argv, requested disabled VSync,
  Wayland/Dummy, and reported Forward+/GTX1070. Its original pre-network cosmetic
  API/fence/negative checks returned ok, then fixture ready. Observer ready names
  the saved camera source and exact engine/project/PID. These narrow positives
  are not network completion, presented effects or effective disabled-VSync proof.
- The executed `bound_endpoint` checked owned host fd links against only
  `/proc/<owned-host>/net/udp` and raised **runner-owned endpoint-binding PROOF
  failure**. Live and settled-late were never spawned. This does **not** prove
  absent binding or a native/network fault. The requested OS-selected endpoint was
  127.0.0.1:45971; actual binding was not proven by the retained evidence.
- **Evidence limitation:** the executed probe did not retain its raw failed fd/table
  lookup inputs. Full actual probe source/argv/supervisor exit1 and exception are
  retained, but the missing historical `/proc` snapshot cannot be reconstructed.
  No post-exit lookup is substituted. No dual-stack/race/native causal diagnosis
  follows from source or the failed match alone.
- Collection stopped and sent only the owned host SIGINT. Host exited**-2**, reaped;
  shared grace start99675.542199/cutoff99677.542199/end99675.605734, no terminate/kill
  needed. Normal leave/result/quit did not complete; interruption remains FAIL.
  Both engine handles and wrapper command were reaped; all streams closed.
  Complete host/import stdout, stderr and engine logs are retained; both stderr
  streams are actual zero-byte files. No new runtime warning/error was logged.
- Host observer JSONL contains **only one ready row**, no post-draw callback row or
  final observer row. All seven required PNGs are absent; client/late/draw streams
  were never produced. Effective VSync, callback count, actual camera-current/window/
  viewport/image dimensions and real twelve-event workload outcomes are unproved.
  No actual PNG exists to inspect; **no image-inspection credit** is claimed.
- Bounded readback took0.001733s; every copied input and matching checkout input
  remained byte-preserved, including scenes/UIDs/GLBs/source import sidecars.
  Source preservation/import0/ready/empty stderr/short bounded cleanup are narrow
  positives only; the evaluator correctly exits1. IMAGE and all full gates FAIL/OPEN.

### Offline-only probe correction, no retrospective credit

After consumption, only the owned runner probe/checks are corrected offline: inspect
both IPv4 UDP and IPv4-mapped loopback UDP6 representations, associate exact socket
inode with the owned fd, reject external/all-interface/foreign/ambiguous rows, and
save complete actual lookup inputs/failures **before** raising. This addresses
observable probe coverage/retention limitations; it does not identify the historical
cause. Five literal **synthetic** proc cases test IPv4, mapped IPv4, wrong bind,
wrong inode and ambiguity. These are offline test inputs, not historical snapshots.
The full fake-clock suite and old-stream evaluator negatives also pass offline.
Executed original runner remains reachable at4a50808 and is retained separately
from the corrected source. The observer has no post-attempt runtime change.
There is **no** second import, runtime, graphical fallback, new condition or past-credit.

ROOT's subsequent raw stop confirmation preserves these limits. The notified main
advance30471e6 changes Steam docs/evidence and only unrelated S03-S TODO/readiness
prose. Initial review stays on the commissioned base; inspect actual delta and
rebase once at a saved boundary before same-reviewer exact-final disposition.
No code/pin/settings/scene/gameplay change or runtime replay follows that rebase.
