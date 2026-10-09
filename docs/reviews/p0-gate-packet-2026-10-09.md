# P0-GATE owner review packet — 9 October 2026

**Status: PASSED on 9 October 2026 under owner decision 27.**

This packet reconciles the integrated foundation work through local `main` revision `7351f3b`.
The [8 October owner decisions](owner-decisions-2026-10-08.md) remain authoritative; the
[P0 readiness audit](p0-readiness-audit-2026-10-08.md) explains why the additional
foundation tasks were commissioned.

## Disposition

The owner accepted the packet and S17 quiet result, passed P0-GATE and started M1 production.
S03-R, S05, S06 and S08 are done as foundation tasks; their remaining work is assigned to their
M1 consumers. P0-PROFILES remains non-blocking, and the S04 handling fix and owner re-test must
finish before M1-B1 freezes handling. This disposition records owner decision 27 without changing
the reviewed foundation evidence below.

## Executive summary

**Recommendation: the concept-foundation phase is ready for P0-GATE review.** Owner decision 14
sets the remaining gate inputs to this packet and the S17 quiet measurement; both are now
integrated. The packet does not itself pass the gate, but no extra S10 foundation spike or quiet
rerun of the other contended spikes is required before the owner records the gate disposition.
The planned work is sufficient to make the production architecture concrete: linked source assets,
world-relative foot control, ENet session boundaries, local foot/car prediction, foot-to-car
transfer, bounded chains, shared topology, desktop export configuration, traffic and pedestrian
prototypes, packed population replication, authoritative combat, character/audio/VFX carriers,
and an integrated host-tick composition all exist as executable evidence.

The owner's governing principle is **make it work, then make it pretty, then make it fast**.
Foundation results establish concepts and high-level limits; reasonable numeric targets remain
adjustable during M1. Accordingly:

- S17 is the only quiet rerun. Its production-schedule substituted total is
  **2.069/3.989/5.849 ms median/p95/p99**. Decision 22 treats approximately 4 ms p95 for the
  full M1 host as a soft tracked target, not a per-feature acceptance gate; the 0.011 ms fixture
  margin provides no headroom for omitted real physics, prediction or sockets.
- S10's 64-pedestrian prototype has unacceptable overlap/stuck counts and pedestrians are the
  largest timing contributor. Decision 22 makes old subsystem shares reporting only; behavior and
  total-host risk still make S10/S17 the first production work under decision 14.
- All other spike timings remain explicitly **contended**; owner decision 13 defers their quiet
  optimization to implementation rather than treating those upper bounds as gate failures.
- S11 fits the bandwidth budgets with large margin; decision 20 sets the initial remote-motion
  policy, while drawable smoothness acceptance remains production work.
- S03-L retains a provisional 350 ms p95 contended Windows authoritative-loop allowance.
- Linux graphical/runtime confirmation remains unperformed; Steam Deck remains later.
- Decision 25 closes the bounded S02 physical controls/readability and Alt-Tab native-focus owner
  checklist. S03-R drawable remote continuity plus later production playtests, vehicle handling,
  audio listening and other visual reviews remain M1 work, not P0-GATE prerequisites.

## Quiet re-measurement — completed S17-only scope

The [quiet record](../spikes/quiet-remeasure-2026-10-09.md) reran only S17, per owner
decision 13. CPU-load snapshots are instantaneous and do not prove exclusive CPU use; the
orchestrator guaranteed the quiet window, zero unrelated `godot.exe` engines were present, and
idle `godot-ai.exe` bridges explain the runner's retained mechanical contended labels.

| Workload | Existing result | Quiet-pass disposition | Gate/production use |
| --- | --- | --- | --- |
| S17 pedestrians | contended p95 2.960 ms | quiet p95 **2.559 ms**; former 1.0 ms share exceeded | Reporting only; optimize pedestrians first when the total is threatened. |
| S17 traffic | contended p95 1.423 ms | quiet p95 **1.264 ms** | Former 1.5/2.0 ms shares are reporting only; remeasure real bodies. |
| S17 combat/history | contended p95 0.141 ms | quiet p95 **0.119 ms** | Reporting only; fixture result. |
| S17 explosions/chains | contended p95 0.018 ms | quiet p95 **0.015 ms** | Reporting only; fixture result. |
| S17 subset encode every four ticks | contended p95 0.664 ms | quiet p95 **0.499 ms** | Reporting only; use shared/rate-bucket encoding as the production starting point. |
| S17 conservative total | contended 3.527/6.519/8.643 ms | quiet **3.027/5.658/8.321 ms** median/p95/p99 | Comparison only; three full encodes/tick is not the intended schedule. |
| S17 production-schedule total | contended 2.394/4.582/6.286 ms | quiet **2.069/3.989/5.849 ms** median/p95/p99 | Meets the soft ~4 ms p95 target by 0.011 ms in the fixture; no production headroom claim. |
| S03-L, S03-P, S04-P/T, S07, S09–S15 | contended values retained | **Not rerun by owner decision 13** | Make systems work, then improve presentation and optimize during M1. |

## Foundation status matrix

“Complete” means the commissioned bounded foundation question has an integrated record. It does
not mean that the corresponding production system, human review or M1 acceptance is complete.
All timing values explicitly marked **contended** are upper bounds from a shared workstation.

| Task | Foundation status | Key evidence and headline result | Residual risk / open follow-up | Quiet value |
| --- | --- | --- | --- | --- |
| S01 | Complete, bounded | [Asset workflow](../spikes/s01.md): explicit Blender→GLB links, wrapper variants and byte-identical re-export | Production art, direct imported-child overrides and throughput remain outside the proof | n/a |
| S01-W | Complete | [Windows supplement](../spikes/s01-w.md): both GLBs byte-identical; Blender 5.2.2 / exporter 5.2.40 | Recheck after tool/source changes | n/a |
| S02 | Complete; bounded owner play test passed | [Controls](../spikes/s02-controls.md): 5 m/s normalized WASD, mouse yaw, left-click fire, 42°/47 m camera, no cutaway; decision 25 passes physical controls/readability and Alt-Tab native focus | Later production playtests remain M1 work | n/a |
| S03 | Complete, bounded | [Session proof](../spikes/s03.md): ENet admission, handoff, freshness and cleanup; ENet bandwidth workaround retained | Production Session/Replication and full baseline still M1 work | n/a |
| S03-R | Technical response/expiry complete; remote review open | [Response record](../spikes/s03-r.md) plus [S03-L](../spikes/s03-l.md): exact decision-age expiry fix passes | Drawable remote continuity and later production playtests; old pre-fix response values are historical | see S03-L |
| S03-L | Diagnostic complete | Corrected passing direct loopback 317 ms p95; provisional **350 ms p95 allowance**, all contended | Linux comparison and production tuning | Not rerun; contended retained by decision 13 |
| S03-P | Complete, bounded; M1 queue contract accepted | [Foot prediction](../spikes/s03-prediction.md): predicted p95 19–29 ms physics, 39 ms drawn; correction p95 ≤0.25 m in selected runs, contended | Production moving-body contacts, lifecycle and queue acceptance tests | Not rerun; contended retained by decision 13 |
| S03-S | Documentation review complete | [Abstraction review](../spikes/s03-s-abstraction-review.md): ENet-first provider/stream/lifecycle seam | Future Steam adapter has no runtime evidence by design | n/a |
| S04 | Technical body complete; handling fix/re-test open | [Car spike](../spikes/s04.md), [drive scene](../spikes/s04-drive-scene.md): decision 26 saved coast 10.0 / grip 9.0 and found no handbrake braking | Finish the handbrake fix and owner re-test before B1; final dimensions remain open | n/a |
| S04-P | Complete, bounded with mixed adverse results | [Car prediction](../spikes/s04-prediction.md): normal passes; post-rebase adverse correction p95 0.576 m fails 0.5 m target; drawn p95 85 ms; **contended** | Clean adverse production proof, moving-car contacts, subjective feel | Not rerun; contended retained by decision 13 |
| S04-T | Complete, bounded; M1 entry policy decided | [Transition fixture](../spikes/s04-t.md): seat race, moving/blocked exit, AI release and disconnect coast pass; predicted-entry machinery remains a later option; timings **contended** | Implement ~0.3 s confirmed-entry presentation, acceptance-only control/camera/HUD transfer, rejection without snap, real exit clearance and lifecycle races | Not rerun; contended retained by decision 13 |
| S05 | Foundation logic/presentation complete | [Chain](../spikes/s05.md), [uncapped presentation](../spikes/s05-uncapped-effects.md): 12 explosions, 144 visits, 12 drawn/0 dropped | Production pool, in-flight join/reset, wreck art/contact and final dimensions | S15 owns cost |
| S06 | Topology complete; visual/UI review open | [Topology](../spikes/s06.md): foot route, two car turns, stale-bake and shared minimap checks pass; scale/top-right accepted | Minimap size/look, whole UI, contested recovery and final-body reruns | n/a |
| S07 | Complete planning guidance | [Environment envelope](../spikes/s07-environment-scale.md): 6/24/96 pass; historical 384 crash; 96 frame p99 18.405 ms, **contended** | Shared grey-block art is not production; no Deck result; 96 is not a product ceiling | Not rerun; contended retained by decision 13 |
| S08 | Windows diagnosis complete; Linux follow-up open | [Windows result](../spikes/s08-windows-observation.md): original-main DEBUG/RELEASE matrix passes with workaround | Linux original-main and Linux-only diagnostics remain non-blocking follow-up | n/a |
| S08-X | Windows/configuration complete; Linux runtime open | [Export smoke](../spikes/s08-x.md): four desktop exports inspect cleanly; Windows release launches quiet; Linux checklist recorded | GodotSteam removal completed in `660b4fd`/`7351f3b`; Linux launch not claimed | n/a |
| S08-C | Complete, bounded | [Stability](../spikes/s08-c-stability.md): current no-cutaway 192/288/384 instantiate; 384 crash not reproduced; safe capped GPU method | Historical cause unknown; owner approval to replace unsafe design wording | short diagnostic only |
| S09 | Foundation prototype complete | [Traffic](../spikes/s09.md): 24-car p95/p99 1.165/1.690 ms, 18/18 recoveries per aggregate row, zero sampled overlaps/gridlocks; **contended** | Actual bodies, production graph/replenishment and owner intersection policy | Not rerun; contended retained by decision 13 |
| S10 | Foundation concept complete; first production task | [Pedestrians](../spikes/s10.md): normal graph p95 2.654 ms median, flee 3.658 ms; **contended**; large overlap/stuck counts | Production must improve behavior/budget with acceptance checks; no extra foundation spike | Not rerun; contended retained by decision 13 |
| S11 | Codec/bandwidth direction and initial remote policy complete; smoothness acceptance open | [Population replication](../spikes/s11.md): worst host out 55.16 KiB/s vs 256 budget; 3.2 KiB join vs 1 MiB; adverse extrapolation median 15.30% | Implement 100–150 ms tunable extrapolation→hold→smooth correction; drawable playtest and full production baseline/input | Not rerun; contended CPU retained by decision 13 |
| S12 | Foundation comparison complete; hit policy and M1 starting values decided | [Combat](../spikes/s12.md) retains bounded ≤250 ms rewind evidence for later; decisions 18/21 set host-current-time verdicts, forgiving hit shapes and starting combat values | Tune values in playtests; production fire-intent, confirmation, damage/respawn, impact and rocket integration | Not rerun; contended retained by decision 13 |
| S13 | Technical rig path complete | [Characters](../spikes/s13.md): 68 live + 16 dead; throttling 68→30 mixers; contended headless median proxy 35.9% lower | Production art/readability, blending and target-platform evidence | Not rerun; contended retained by decision 13 |
| S14 | Automated audio/settings foundation complete; listening open | [Audio](../spikes/s14.md): exact 8 engine / 8 explosion / 6 weapon voice caps and settings roundtrip | Human mix/listening, production assets/licenses, attributable CPU profiling | Not rerun; contended context retained by decision 13 |
| S15 | Technical VFX comparison complete | [VFX](../spikes/s15.md): all 12/24 roots retained; 24-full frame p95 18.445 ms median, **contended** | Owner approval for tiers; adaptive `amount_ratio` did not prove lower cost; readability | Not rerun; contended retained by decision 13 |
| S16 | Complete proposal | [M1 production plan](../plans/m1-production-plan.md): owner map, promotion plan, testing layers and ordered backlog | Owner ratification of quantitative/product choices in this packet | n/a |
| S17 | Quiet foundation measurement complete; first production task | [Quiet host tick](../spikes/quiet-remeasure-2026-10-09.md): production schedule 2.069/3.989/5.849 ms median/p95/p99 | Fixture meets decision 22's soft ~4 ms total p95 by 0.011 ms; omitted work means no production headroom claim | Quiet S17 complete |
| P0-TOOLING | Complete | [Baseline repair](../spikes/p0-tooling.md): canonical script checks green; complete Python discovery | Linux tooling execution remains unverified | n/a |
| P0-TOOLING-2 | Complete | [Runner hardening](../spikes/p0-tooling-2.md): 60 FPS guards, post-case sampling, identity receipts and incremental log reads | Long measurements were not rerun merely for this repair | n/a |
| P0-PROFILES | Intentionally deferred | [Owner decision 11](owner-decisions-2026-10-08.md): non-blocking Paseo profile review later | Keep outside P0-GATE | n/a |

## Top production risks and options

1. **Pedestrian behavior and budget (S10).** The prototype visibly fails crowd separation/flow
   quality and pedestrians are the largest timing contributor. Per decisions 14 and 22, make compact
   state, spatial indexing, crossing reservations and selective queries the first production work,
   with behavior acceptance and total-host timing checks. The old 1.0 ms share is reporting only.
2. **Whole-host tick budget (S17).** The quiet production schedule meets the soft ~4 ms total p95
   target by only 0.011 ms and omits real physics, sockets and prediction. Implement shared packet
   reuse and indexing, check the total regularly, and optimize the largest contributor first when
   threatened. Do not turn subsystem shares into acceptance gates.
3. **Windows authoritative latency floor (S03-L).** A provisional contended 350 ms p95 allowance
   is much larger than desirable. Keep local prediction mandatory and size history for the tail.
   Replace this allowance with production Windows and later Linux evidence; do not compensate by
   weakening host authority or enabling S12 rewind without the playtest need and bounded host-only
   change required by decision 18.
4. **Remote smoothness (S11).** Bandwidth passes, but adverse delivery extrapolated/froze 15.30%
   of sampled entity frames. Decision 20 starts with one tunable short bound around 100–150 ms:
   extrapolate along last velocity, hold until data returns, then blend smoothly to authority.
   Validate it in a drawable production-like route and revisit per-entity hybrids after playtests.
5. **Linux and Deck.** Windows is the only passing graphical/runtime platform in the recent
   foundation work. Run S08-X's Linux Vulkan checklist before M1-A-GATE. Deck remains later and
   must stay labelled unverified; desktop evidence cannot become a Deck claim.
6. **Foot/car transfer presentation.** S04-T proves ownership safety but its predicted-entry
   path reports a 6.999 m adverse moving-traffic correction. Decision 23 avoids speculative M1
   ownership: play a short ~0.3 s get-in presentation, transfer control and camera/HUD ownership
   only on host acceptance, and leave rejection without an ownership change or snap.
7. **Production content cost.** S07 reuses tiny grey-block assets; S13/S15 are technical carriers.
   Measure representative production art as C1 families land rather than treating 96 blocks or
   current draw calls as a production budget.

## Owner decisions recorded

The owner recorded decisions 13–25 on 9 October 2026:

- **Decision 13 — measurement scope and principle:** S17 is the only quiet rerun. Other spike
  timings remain labelled contended. Foundation establishes concepts and high-level limits; M1
  follows “make it work, then make it pretty, then make it fast,” with reasonable numeric targets
  tuned during implementation.
- **Decision 14 — P0-GATE scope (audit Q1 = a):** P0 waits only for the integrated S17 quiet
  record and this gate packet. Both are now present. S10 behavior/budget and S17 host-budget
  improvement become the first production tasks with acceptance checks, not more foundation spikes.
- **Decision 15 — desktop frame target (audit Q2):** M1 targets capped 60 FPS with p95 ≤16.7 ms
  and p99 ≤20 ms on named hardware: the RTX 4070 Laptop Windows reference and a Linux machine
  when available. This remains a reasonable, tunable M1 target.
- **Decision 16 — driver death (audit Q3):** if the car survives, release the seat, neutralize
  controls and coast to a stop like disconnect; it then becomes an ordinary abandoned parked car
  under the existing cleanup/replenishment policy. Death remains an explicit lifecycle event.
- **Decision 17 — GodotSteam (audit Q4):** remove the addon/GDExtension, keep the S03-S
  provider abstraction, re-add a pinned release only when Steam adapter work is commissioned,
  and retain S08-X's Steam-library export rejection. The removal is complete in
  `660b4fd`/`7351f3b`.
- **Decision 18 — first hit-registration policy:** clients send fire intent only; the host chooses
  the target and damage at host current time using forgiving enlarged hit shapes sized for typical
  network/interpolation delay at target speed. The shooter gets immediate cosmetic muzzle/tracer
  feedback, while impacts and damage wait for host confirmation. Every intent carries the shooter's
  view tick from day one so S12's bounded ≤250 ms rewind can be added later as a host-only change if
  playtests require it. This non-competitive game favors the simple policy that works and looks fair.
- **Decision 19 — S03-P input-queue contract:** accept ordered one-frame-per-tick held-input
  consumption for M1. Pending lag is bounded to three ticks (50 ms) by tick/sequence distance from
  the newest accepted frame; the hard eight-frame participant queue remains separate from the
  120-sequence freshness window. Older frames are superseded without extra simulation, held intent
  neutralizes after 250 ms, and the acknowledgement watermark is the last consumed or superseded
  frame. This supersedes the earlier newest-valid-frame wording and is marked owner-accepted in
  [`api-contracts.md`](../api-contracts.md).
- **Decision 20 — S11 remote extrapolation:** use one tunable short bound around 100–150 ms.
  Remote entities extrapolate along their last velocity, then hold position until data arrives,
  then blend smoothly to authority. Revisit alternatives such as per-entity-type hybrids after
  drawable playtests.
- **Decision 21 — S12 combat starting values:** accept health 100 for players, pedestrians and
  cars. Pistol starts at 34 damage / 0.25 s / 12 rounds / 1.4 s reload / 45 m; SMG at
  12 damage / 0.10 s / 30 rounds / 1.8 s reload / 35 m; rocket at 100 damage via S05 /
  1.0 s cooldown / 18 m/s / 2.5 s lifetime / 4.1 m radius. Car-pedestrian impact uses host
  contact/velocity only: none below 6 m/s, 25 at 6 m/s linearly to 100 at 14 m/s, with a
  0.5 s per-car/target cooldown. These are M1 starting values, tuned in playtests.
- **Decision 22 — S17 host budget:** track a soft **~4 ms p95 total host simulation target** at
  full M1 population in regular performance checks; it is not a per-feature acceptance gate.
  Pedestrian 1.0 ms and traffic 1.5/2.0 ms shares are reporting only. When the total is
  threatened, optimize the largest contributor—pedestrians first. Population counts remain
  tunable settings, starting from 64 pedestrians and 32 cars.
- **Decision 23 — M1 car entry:** entry is host-confirmed, not predicted. The client sends intent
  and plays a short ~0.3 s get-in presentation; control and camera/HUD ownership transfer only
  with the host's accepted transition. Rejection causes no ownership change or snap. Preserve
  S04-T's predicted-entry machinery as a documented later upgrade. Exit remains below 0.5 m/s
  with the authored 1.5 m offset and still requires production clearance queries.
- **Decision 24 — world concepts:** M1-C0 is in progress under a separate owner-run agent using the
  [world concept handover](../workflows/world-concept-handover.md). It is outside this orchestration;
  the owner will report when its work is integrated. Its image-provider/concept-method question
  belongs to that owner-run work, not to this orchestration.
- **Decision 25 — S02 owner play test:** the Windows laptop physical mouse/keyboard test passed
  screen-relative WASD and equal-speed diagonals, moving/stationary mouse facing, wall-blocked and
  post-corner shots, no-cutaway readability, and Alt-Tab native-focus neutralization until a fresh
  press. This closes only the bounded S02 human controls/readability/native-focus checklist;
  drawable S03-R remote continuity and later production playtests remain open.

## Owner decisions still open

These six choices are presented when their consuming M1 task is reached under decision 27; they are
not extra foundation prerequisites. An explicit deferral should still name its consumer or accepted
risk. M1-C0 is not an open decision: it is in progress outside this orchestration. Its
image-provider/concept-method question belongs to the owner-run work under decision 24 and is not an
orchestrator decision.

1. **S04 handling (entry policy settled):** decision 26 records the owner's drive-scene session and
   F12 values (`coast_mps2` 10.0, `grip_per_second` 9.0). The handbrake had no longitudinal braking;
   its fix lane is in progress, followed by an owner re-test before B1.1 freezes handling.
2. **Traffic/crossing policy:** choose reservation priority/lights and whether cars yield at marked
   crossings. **Recommendation:** deterministic authored reservations; cars yield at selected marked
   crossings, while uncontrolled player cars remain collision-authoritative.
3. **VFX degradation:** confirm full→reduced→minimum tiers when many explosions overlap, with one
   visible root and all feedback families retained per event. **Recommendation:** approve; dropping
   an event remains forbidden.
4. **Audio starting policy:** accept/revise nearest-eight engines, eight blast voices, six weapon
   voices and ambience under Music. **Recommendation:** treat these as first-pass caps and decide only
   after the listening checklist.
5. **Safe GPU wording:** replace the design's uncapped-headroom instruction with S08-C's capped
   frame/RenderingServer method. **Recommendation:** approve; uncapped runs caused two device removals.
6. **Production testing:** approve adding pinned test-only GUT under M1-D1.1.
    **Recommendation:** approve, excluded from release exports and runtime autoloads.

## Human checks still needed

Use the pinned Godot `4.8.dev7.official.c971f93e7`. These were future owner/reviewer runs when
this packet was drafted; the vehicle status below now includes owner decision 26.

### Vehicle handling

Decision 26 records the completed owner session and saved F12 values: `coast_mps2` 10.0 and
`grip_per_second` 9.0. The session found that the handbrake only reduced lateral grip and applied no
longitudinal braking. The handbrake fix lane is in progress; after it lands, rerun the saved drive
scene for owner confirmation before M1-B1 freezes handling.

### Audio listening

The old `audio_test.tscn` command is not a listening check. That automated stress fixture requires
`--s14-output=<path>`, emits synthetic placeholder tones for a fraction of a second and quits.
Listening moves to M1-A3 after real audio assets exist, following
[S14 production requirement 10](../spikes/s14.md#m1-production-requirements).

### Visual review

- Open [`docs/concepts/ui-v1/review.html`](../concepts/ui-v1/review.html) and decide the whole-UI
  direction, especially minimap size/look; the Steam join mockup is not M1 scope.
- Review the actual [S13 crowd capture](../spikes/s13-evidence/crowd-throttled.png) for top-down
  silhouette/palette/death readability, while treating it as technical art only.
- Compare [12-full](../spikes/s15-evidence/12-full.png) and
  [24-full](../spikes/s15-evidence/24-full.png) VFX captures for target/road occlusion and approve
  or reject the proposed tiers.
- M1-C0 world concepts are in progress under a separate owner-run agent using the
  [world concept handover](../workflows/world-concept-handover.md). The owner will report when that
  work is integrated; this orchestration must not dispatch it or decide its
  image-provider/concept method.
- On Linux, follow the exact five-step checklist in [S08-X](../spikes/s08-x.md#linux-desktop-launch-checklist)
  and retain Vulkan window/focus/log evidence. This is not a Deck substitute.

## Recommended first production work

P0-GATE passed under decision 27, so start with the work assigned by decision 14. Open production
choices above should be resolved by their named consumers; they do not require more foundation
reruns. Decision 28 moves LocalSettings and the settings UI to M1-D before private review builds;
production audio remains independent and uses default bus levels until settings land.

1. **S10 production behavior/budget:** establish the production pedestrian owner and compact state,
   add spatial/crossing policy work, and define behavior plus timing acceptance checks before scaling.
2. **S17 production host budget:** add real simulation/networking costs incrementally, preserve
   the production encode schedule, and track the soft ~4 ms total p95 target regularly. Keep
   subsystem timings as reports, optimize the largest contributor first when threatened, and tune
   the initial 64-pedestrian/32-car settings as production evidence requires.
3. **M1-D1.1 — production checks:** pin test-only GUT, add CI/check entrypoints and prove export
   exclusion, consuming P0-TOOLING and P0-TOOLING-2.
4. **M1-A1.1 — Boot/session composition:** saved Boot/menu/status scenes and typed ENet-first
   operation lifecycle, consuming S08-X and S03-S.
5. **M1-C1.1 — starter road/building/prop subset:** do not dispatch it yet. Start only after the
   owner reports M1-C0 integrated and its production asset list is approved, using
   the byte-identical S01/S01-W pipeline.
6. **M1-C2.1 — CityData and first production sector:** begin when the approved starter subset
   exists; preserve one topology/minimap representation from S06.
7. Continue **M1-A1.2** after the provider seam stabilizes. Do not freeze M1-A2.2's production
   codec until its S11/S17 acceptance checks are defined, and do not copy S09/S10 fixture internals
   into production.

The detailed ordering and hard consumers remain in the
[M1 production plan](../plans/m1-production-plan.md#5-foundation-entry-criteria-and-ordered-m1-backlog).
