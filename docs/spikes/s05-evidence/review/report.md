# Independent S05 review — exact f7883c3

8 October 2026. Sole independent reviewer: Paseo agent
`770f9536-788e-4348-b335-86224c24e5fa`, GPT-6.1-Sol HIGH. Clean initial context
contained the raw assignment and named artifacts, without the implementer's
conversation. No coordinator, specialist or other subagent was created.

**Verdict: ACCEPT the partial bounded technical experiment at exact
`f7883c332a3728267afc86343d6e0f8dc696ede6`, with one nonblocking P3 documentation
whitespace finding. Full S05 remains OPEN.** No P0, P1 or P2 defect was found in
the inspected minimum owner, saved fixture, API outcomes or separate-process
ENet rows. This verdict does not accept actual explosion effects, product policies,
production combat/lifecycle/joining, capacity, device or transport targets.

Reviewed branch: `s05-authoritative-chain-fixture`. Accepted base:
`refs/heads/main` at `c8096b55ef97412552366fdaa74c220b976ed82e`. Original experiment
base: `c0eda26f7f010af75bbf10c272ec5cb001442331`. The accepted base is an ancestor;
the two candidate commits form a linear chain, without a merge commit. All
substantive reads and the independently executed fixture used an archive of the
immutable candidate, not pending working-tree evidence additions. The shared
worktree acquired implementer-owned retention additions during review; they are
explicitly excluded from this disposition. No approval transfers to their future
commit. The same reviewer must inspect and explicitly dispose of the exact final
retention/correction HEAD.

## Findings

### P3, nonblocking — extra blank line at the end of the authored spike record

Location: `docs/spikes/s05.md:207`. `git diff --check c8096b5 f7883c3` exits 2 and
reports a new blank line at EOF. This is a low-impact authored-document hygiene
failure under the requested whitespace checks, without gameplay impact. Remove
only the surplus terminal blank line from the current authored record and verify
the scoped diff. Do not normalize retained raw evidence to make the check green.
The other two reported EOF blanks are in
`docs/spikes/s05-evidence/raw-s05-todo.md:21` and
`editor/protocol-queue-before-measurement.md:189`; their exact raw bytes are
intentional historical retention and should remain unchanged. Evidence:
`diff-check.log`. No technical rerun is needed for this correction.

No other actionable finding is asserted. The limitations below are required open
acceptance gates, not hidden production approval or requests to expand this
experiment.

## Contracts and scope actually examined

Read the complete original S05 TODO receipt, the fifth accepted checkpoint,
current S05 block, AGENTS, development/assets/multiplayer/API guidance, S03 and
S04 evidence, S04 body/seat contracts and source handoff. Applied project
GDScript Review, Art Review, Godot MCP Toolkit, and the Paseo reviewer template
and model policy. Consulted the applicable design, architecture, saved-scene,
art-direction, world-layout and catalogue contracts. Inspected all seven new
GDScripts, all three new saved scenes and UID sidecars, both new Python tools,
their staging/check/cleanup dependencies, actual inherited S03 Match/Session/
Replication routes and S04 body/rule APIs, and the evidence catalogue/protocols/
compiler/network/editor/negative/queue receipts. Vendor interfaces were preserved.

The entire accepted `c0eda26..c8096b5` changed-path delta was examined: README,
TODO, architecture, development, multiplayer, saved-scene/world guides, S04 source
handoff and record, stopped compatibility record, and DOC6/DOC7 completion records.
It consists of accepted guide discovery/contract reconciliation plus the separately
authorized S05 assignment paragraph/readiness row. It changes no technical
dependencies. Candidate scope preserves those guides, completions and current
operational ownership prose/table. The only changed pre-existing file is the
owned S05 TODO block; it does not remove S05 or another task. Technical reruns
were justified by reviewing the executable final fixture and proof amendment,
not by this documentation rebase.

The immutable archive comparison independently confirms **1,519 accepted-base
files other than TODO are byte-identical**. Every changed path is within new
`tests/fixtures/s05`, `tools/run_s05.py`, `tools/s05`, `docs/spikes/s05*`/evidence,
or the S05 TODO block. The scoped resource check separately confirms **501
original technical files** unchanged, three scene UID/path/node-identity sets,
and seven unique script UID sidecars. This includes original sources/imports,
project settings, pins and vendor/tool contracts. No S01/S02/S03/S03-R/S04 code,
scene, asset or identity migration was introduced.

## Owner and execution-path assessment

`S05Damage` is the single minimum owner of health, terminal phases, occupant
sentinel, EventId allocation, shot floor, active jobs and wreck retention. It
combines the necessary damage/life/explosion responsibilities locally rather
than creating a production framework. S03 still owns participant/session and
marker admission; S05 subclasses adapt only baseline/fire/cleanup and lifetime
slot admission. Replication publishes owner cuts and events rather than applying
an alternate damage formula. There is no competing Synchronizer/Spawner writer.

`resolve_shot` (`damage.gd:83–109`) checks authority, exact five-field committed
identity, session/match, registered active generation, retained sequence floor,
window and root/EventId capacity before mutation. The shooter sequence floor is
independent of active damage caches and survives shooter retirement. A repeated
old shot cannot allocate a new EventId after jobs disappear. Terminal targets
return without applying another damage outcome or scheduling a second blast.
The public API is a host-only committed-shot resolver, not a weapon/ammo/muzzle
implementation. Its target is supplied by trusted fixture code; the wire endpoint
does not accept client amounts or targets.

`_damage` neutralizes the body and commits health, life/collision revisions,
occupant death/release and deadline before `changed` publication. `S05Car` uses
the unchanged S04 `configure`/`retire` API: LIVE host bodies own collision,
WRECK bodies stop simulation/velocity but keep the stationary original box,
and RETIRED bodies lose collision/visibility. Saved cars start passive; the
Match's tree-entry configuration also establishes passive roles before ready
callbacks. There is no pose writer, playable seat/controller or runtime-authored
render hierarchy added to these fixed cars.

`advance` processes at most four target visits per host tick, sorting jobs by
due tick and EventId, and advances each finite target cursor once. A cache retires
only with its completed job. Every saved car can become terminal once, so its
single job reservation bounds pending/active jobs at twelve. Work does not depend
on visibility or presentation slots. The bounded scan/sort/retirement operations
also remain finite at twelve, though the four-visit metric is not a measurement
of all CPU instructions or host time. Completed telemetry is capped at twelve;
no unbounded completed damage history is used for acceptance.

The RPC boundary derives participant identity from the real sender before allocating
a rate bucket. It validates admitted ownership/context and exact intent shape,
then invokes the same resolver. The new receipt uses a 512-Variant-byte cap,
four-per-second burst-four bucket, window sixteen, and no action queue; current
cuts are capped at 8,192 JSON UTF-8 bytes. Authority annotations protect replica
state/event direction. The 632-byte observed receipt is the deliberately rejected
oversize input, not an accepted-message budget. Serialization/predecoder engine
allocation and production flood work are not proved by these application caps.

Full fixed-row preflight precedes car mutation. Session/match/generation and current
revision fences reject old/malformed cuts; integral JSON fields are normalized only
after validation. The inherited baseline decoder handles transfer/baseline identity.
Marker movement never writes car life/health/seat/collision. Hydration installs
current wreck rows while local input is closed and emits no historical live events.
There is deliberately no journal of arbitrary car changes during an in-flight
baseline: only settled post-chain joining is accepted here. S05 documents that
limitation; the canonical M1 journal is still required for during-chain races.

Presentation consumes ordered live EventIds after their current-state dependency;
duplicates and future-dependent events cannot advance accepted history improperly.
Saturation advances the watermark and drops only tokens. Host advancement retires
token deadlines, and later consumption checks deadlines; this is a reservation
stub. It cannot prove real client effect expiration, draw visibility, sound,
overdraw or presentation cost. Teardown clears owner jobs/floors/rows, rate buckets,
effect history/slots, bindings and inherited transfer work. General reset/retry/
sustained churn is outside the single finite session experiment.

## Predeclaration, amendments and evidence integrity

The original and amended protocols retain falsifiable API, physics, ENet, source
and work expectations and explicitly provisional choices before their respective
measurements. The first twelve-root version was amended to a one-root propagating
grid, with completion bound changed from sixty to ninety ticks and a conservative
finite work estimate. Both are retained rather than rewriting historical criteria.
The one-root row is important evidence of propagation; twelve independent roots
alone would not prove that behavior.

The later queue-pressure declaration adds a finite capacity row in the same saved
twelve-car fixture because the one-root chain reaches only five queued jobs.
It reserves four roots per batch over three completed host ticks before the first
six-tick due deadline. Its timestamp/criterion receipt and original failed row
are retained separately. The corrected proof waits for the owner tick to advance
instead of assuming `physics_frame` resumes after the owner's budget reset. Static
comparison with the original canonical proof shows the new queue role/helper only;
the previously exercised API and ENet helper bodies remain unchanged. Gameplay
owner/replication source hashes agree with final HEAD. This is one bounded experiment
with a justified test-timing correction, not a sustained-load or population trial.

Independently verified all **237** candidate retention rows against both stored
bytes/SHA256 and decompressed raw bytes/SHA256. All pass. All 237 original `/tmp`
sources were still readable: 236 exactly match their raw hash; the live editor
log has appended since capture, and its retained 39,466 bytes are an exact prefix
of the now-longer source. This is a valid snapshot, not lost/corrupted retention.
`raw-s05-todo.md` exactly equals the original TODO block, including its terminal
blank line. Roundtrip summary hashes agree with all three immutable final scenes.

The canonical result's expected source differences are its deliberately staged
`project.godot` and historical `proof.gd`. The corrected queue result agrees with
final new source files, with only the documented staged project-settings difference.
Initial-host evidence differs in historical proof/boot before the admission guard
and is not used as final guard proof. Failed queue results lack a completed final
source manifest; they remain failure evidence rather than a pass. Independent
execution below closes final executable binding rather than inheriting an old pass.

The negative-retirement mutation changes only the retained floor condition to
apply while jobs remain. Its actual API run fails specifically `retired ShotId
rejected`; active duplicate rejection remains. That test detects reacceptance/
identity allocation even though terminal-car immunity would prevent a second
health decrement in this static fixture. It is a meaningful contract negative.
It was inspected, not rerun unnecessarily or applied to the candidate.

## Independent checks actually executed

An immutable `git archive` of the candidate was extracted under
`/tmp/s05-independent-review`. The full provided runner was executed from that
archive, with pinned Godot
`/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot`
and gdstyle
`/home/regner/.local/share/mise/installs/github-atelico-gdstyle/0.3.0/gdstyle`.
It created a separate fresh output/project outside that archive:

```sh
python tools/run_s05.py --godot /home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot --gdstyle /home/regner/.local/share/mise/installs/github-atelico-gdstyle/0.3.0/gdstyle --output /tmp/s05-review-execution-host-f7883c3 --port 29374
```

Exit 0, engine `4.8.dev7.official.c971f93e7`; seven explicit new-script compiles,
pinned format/lint, both API rows, both actual three-process ENet rows, corrected
queue pressure and unchanged staged-source fingerprints pass. Ports 29374/29375
were used by the two sequential ENet cases. Each process had private XDG user/log
directories; no addon, Steam or authoring source was loaded by the gameplay mirror.

| Independent outcome | Three-car row | Twelve-car single-root row |
| --- | --- | --- |
| Literal host/live/late health | 0, 0, 100 | Twelve zeros |
| Damage / completed blasts | 2 / 2 | 12 / 12 |
| Occupant sentinel deaths | 1 | 1 |
| Total target visits / peak per tick | 6 / 3 | 144 / 4 |
| Queue / active cache peak | 2 / 3 | 5 / 12 |
| API completion tick from root at tick0 | 12 | 46 |
| Cosmetic accepted / dropped / peak | 2 / 0 / 2 | 8 / 4 / 8 |
| Current car cut / baseline max JSON bytes | 558 / 906 | 1964 / 2312 |
| Live event unique / duplicate rejection | 2 / 2 | 12 / 12 |
| Post-chain baseline historical tokens | 0 | 0 |
| Saved car visuals hidden during burst | Not required | Yes |

Actual independent ENet PIDs were boot host315839/client315861/late315883 and
burst host315930/client315952/late316009. All six exit0. Both remote clients
observe, through actual RPCs, NOT_ADMITTED, OK, active DUPLICATE, forged-owner
STALE_CONTEXT, RATE_LIMIT, malformed INVALID, oversize INVALID, WINDOW, then
retired DUPLICATE. Settled health rows agree in host/live/late processes. The late
processes report wreck hydration with input disabled and zero event tokens before
normal inherited admission; teardown checks pass. The network completion ticks
are33/67 because fire starts at tick21; chain work still takes12/46 ticks.

The independent queue-pressure row reaches queue peak exactly12 before due work,
root peak4, target/cache peaks4/12, all144 visits, twelve outcomes/completions,
eight accepted tokens/four drops, no active jobs, and finishes at tick41. Its
due ticks6/9/10 establish root batches at0/3/4. The saved visuals are hidden.

The API rows additionally exercise active and post-retirement ShotId duplicates,
session/match/generation/sequence/passive rejection, coherent terminal observer
state, live/wreck/expired actual physics queries, atomic bad-cut rejection,
current passive hydration, future-dependency event rejection, marker-motion field
separation, fifth root backpressure, departed shooter floor and four lifetime
shooter capacity. These are fixture production APIs, not cloned damage formulas.

Inspected every independent stdout/engine/import/compiler/style log as well as
exit status: no ERROR/WARNING/SCRIPT ERROR, traceback or assertion failure in the
successful run. `independent-log-check.json` binds these logs. A separate resource
checker invocation against accepted base passed, retaining `resources.json` and
`resources-console.log`. `audit_evidence.py` plus JSON/console outputs retain
independent scope, exact source/hash, raw-task, log and roundtrip checks.

The supplied all-owned checker manifest contains48 owned scripts and48 explicit
successful compile receipts, including otherwise unused dependencies and editor
probes; all retained compiler stdout/engine logs and setup/style logs are clean.
Its proof-only later amendment is independently compiled by the final seven-script
run. I did not repeat the unchanged full48 compile or unrelated body/Steam/device
experiments merely for the docs rebase. Import alone was never counted as compilation.

The initial reviewer invocation chose an output below the archive root and was
correctly rejected by the runner's external-output guard before execution. The
corrected sandbox invocation failed during import with `_sock == -1`/
`ERR_CANT_CREATE` plus error-printing diagnostics: no gameplay ran. A narrowly
authorized escalated CLI-only invocation resolved that socket restriction and
ran the successful isolated loopback check. Both substantive run/failure logs are
retained separately. One scratch receipt inspection requested nonexistent
`editor/worktree-state.json` and stopped with FileNotFoundError; the actual
`worktree-state-result.jsonl.gz` was then inspected. This is reviewer scratch
error, not a candidate defect or failed acceptance test.

## Saved/source and operational acceptance

All visible geometry remains linked along
`s05/car.tscn -> s04/kinematic.tscn -> s04_car.glb(.import) -> s04_kit.blend`,
and track follows the corresponding unchanged S04 track chain. Collider envelope
1.8×1.5×3.4 m, visual1.88×1.54×3.4 m and flat grid placement are explicit technical
assumptions. There is no new mesh generation, copied vertex data, imported-child
override, runtime node-layout construction or source/export edit. Rigs, clips,
new materials/LOD and new production concept/source handoffs are not applicable
to this reuse. Actual gameplay camera/readability and explosion/wreck art remain
pending; the unchanged technical car as a wreck is explicitly disclosed.

The supplied actual HOST inventories show the known pinned main editor253677,
then no authoring process after a graceful deferred quit, in host PID namespace
`4026531836`/network namespace`4026531833`. Installed-handler main-state response
identifies the main project, exact engine and empty unsaved scenes before quit.
Launch receipt records a single pinned worktree editor286171 following the empty
HOST inventory; worktree live state likewise reports the correct project/pin and
empty unsaved list. This is actual retained HOST evidence, not sandbox-PID absence.
Credentials were not read or copied by this review. No live editor preflight or
project switch was performed by the reviewer.

Authoring receipts show toolkit script.write/check/indexing, inherited scene
creation, node/script/property composition and explicit scene saves. Early
class-index failures and bare-vector property errors are raw and separated from
corrected tagged-property/refresh receipts. Final car/boot/burst save-close-reopen
operations succeed, report no discarded unsaved changes, retain imported mesh
ancestry and agree byte-for-byte with final scene hashes. This satisfies the new
inherited fixture's supplied editor roundtrip evidence, independently checked
against saved bytes; headless import is not used to prove shared-editor synchronization.

The editor log also contains toolkit newer-engine warnings and progress-dialog
`call_deferred`/task errors during editor operations, in addition to historical
class-index errors. They are retained and do not occur in successful isolated
compiler/API/ENet logs. Successful saved receipts, resource/hash checks and fresh
executable outcomes resolve the scoped evidence without broad suppression or
renderer/service repair. I do not claim the entire editor log is diagnostic-free.

## Criteria dispositions and remaining owners

| Raw/predeclared acceptance | Disposition and limits |
| --- | --- |
| Three cars, near/far known outcomes | ACCEPT technical fixture; independently observed literal 0/0/100 |
| Host damage/life owner and coherent terminal state | ACCEPT minimum owner; occupant is one nonrendering sentinel, not an admitted player |
| Duplicate request/event and ShotId after cache retirement | ACCEPT scoped API and actual RPC duplicates; retained floor negative is meaningful |
| Event ordering, delay, queue/cache/per-tick bounds and work estimate | ACCEPT finite12-car policy and measured peaks; no CPU/device/sustained budget claim |
| Reserved12-car chain despite8 cosmetic slots, off-camera | ACCEPT gameplay versus eight-token reservation separation, one-root propagation and full-capacity queue row; actual explosion-slot/drawn acceptance PENDING |
| Wreck hydration before input and historical-event suppression | ACCEPT settled post-chain separate-process join; during-chain immutable-cut/journal races remain M1-B3/M1-D |
| Collision/neutralization/retention | ACCEPT stationary host query and passive-replica revision state; no client production collider, moving contact, final clearance or full lifecycle proof |
| Sender/ownership/type/session/generation/revision/rate/size fences | ACCEPT exercised finite boundaries; no predecoder allocation, hostile flood, fifth-peer/reconnect race or full malformed-wire suite closure |
| Saved hierarchy/source ancestry/UID/import/inherited roundtrip | ACCEPT new technical consumer reuse and supplied saved-editor receipts; production art/drawn presentation PENDING |
| Explicit compile/style/log/hash preservation | ACCEPT retained48 compilation and independent final7; P3 authored EOF cleanup remains nonblocking |
| Final range/obstruction/delay/occupant/wreck policy | PROVISIONAL; Regner/P0-GATE ratification remains OPEN |
| Full S05 TODO removal | REJECT removal now; current retained open block is correct |

Exact actionable remaining S05 gates are (1) an explicitly named drawable writer/
budget producing saved/source-linked explosion presentation, saturating eight
actual effects with drawn/live-versus-hydrated receipts while the same gameplay
outcomes complete; (2) Regner ratification of provisional blast/obstruction/falloff,
delay/order, occupant and wreck/collision policies; (3) affected spacing/contact
reruns after final S04/S02 dimensions. The current TODO states these gates and
keeps the original raw acceptance. No further broad authoring is authorized by
this review. Full joining/resync/reset/destruction/seat races, admitted-player
death/respawn/equipment and sustained load retain M1-B1/B2/B3/B4/M1-D/S07 owners.
No full S02/S03-R/S04, P0-GATE, S07, M1, production, Steam, native device or physical
input/feel gate closes.

## Reviewer identity, artifacts and final handoff

Paseo profile discovery returned zero profiles. Provider/model discovery confirms
`gpt-6.1-sol` supports HIGH. This reviewer snapshot reports configured HIGH,
**effective HIGH**, runtime model `gpt-6.1-sol`, mode `auto-review`. Complete
read-only discovery/snapshot receipt is `provider-discovery.json`; no fallback,
profile/runtime mutation or agent spawn occurred.

Report and all new check artifacts reside under `/tmp/s05-independent-review`.
The compact retention bundle includes this full report, the audit source/outputs,
Git/delta/diff/source-binding/resource/provider receipts, and successful independent
raw compiler/API/ENet/queue logs/results plus the sandbox failure.
`checks/original-locations.json` maps copied evidence back to original command paths.
Candidate archives/caches/private XDG directories are not needed in the durable
review pack because exact source identity is bound to Git and manifests. Retain
the report and each check artifact losslessly, with their bytes/hashes; do not
replace this substantive report with a verdict summary.

I made no shared workspace write, editor/native/service/device mutation, source
authoring, merge, push or project/agent archival. Independent subprocesses are complete. The
implementer remains the sole authoring/retention writer and will be notified to
retain this report/artifacts, optionally correct the scoped P3, and provide the
exact resulting committed HEAD for the same reviewer's narrow renewed disposition.
The acceptance above binds only f7883c332a3728267afc86343d6e0f8dc696ede6.
