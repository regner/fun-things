# P0-GATE owner review packet — 9 October 2026

This packet reconciles the integrated foundation work through local `main` revision `406b9b6`.
It is a decision aid, not an assertion that P0-GATE has passed. The
[8 October owner decisions](owner-decisions-2026-10-08.md) remain authoritative; the
[P0 readiness audit](p0-readiness-audit-2026-10-08.md) explains why the additional
foundation tasks were commissioned.

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
  **2.069/3.989/5.849 ms median/p95/p99**, passing the provisional 4/8 ms host fixture targets,
  but its 0.011 ms p95 margin provides no headroom for omitted real physics, prediction or sockets.
- S10's 64-pedestrian prototype still misses its proposed share and has unacceptable overlap/stuck
  counts. Owner decision 14 makes S10 quality/budget and S17 host-budget work the first production
  tasks with acceptance checks, not additional foundation gates.
- All other spike timings remain explicitly **contended**; owner decision 13 defers their quiet
  optimization to implementation rather than treating those upper bounds as gate failures.
- S11 fits the bandwidth budgets with large margin, but remote smoothness remains production work.
- S03-L retains a provisional 350 ms p95 contended Windows authoritative-loop allowance.
- Linux graphical/runtime confirmation remains unperformed; Steam Deck remains later.
- Physical Alt-Tab, walking/aim feel, vehicle handling, audio listening and visual reviews remain
  valuable production acceptance/tuning work, but are not P0-GATE prerequisites under decision 14.

## Quiet re-measurement — completed S17-only scope

The [quiet record](../spikes/quiet-remeasure-2026-10-09.md) reran only S17, per owner
decision 13. CPU-load snapshots are instantaneous and do not prove exclusive CPU use; the
orchestrator guaranteed the quiet window, zero unrelated `godot.exe` engines were present, and
idle `godot-ai.exe` bridges explain the runner's retained mechanical contended labels.

| Workload | Existing result | Quiet-pass disposition | Gate/production use |
| --- | --- | --- | --- |
| S17 pedestrians | contended p95 2.960 ms | quiet p95 **2.559 ms**; proposed 1.0 ms share fails | Optimize and accept in the first production work. |
| S17 traffic | contended p95 1.423 ms | quiet p95 **1.264 ms**; 1.5 ms share passes | Preserve as a planning ceiling; remeasure real bodies. |
| S17 combat/history | contended p95 0.141 ms | quiet p95 **0.119 ms**; 0.25 ms share passes | Fixture result only. |
| S17 explosions/chains | contended p95 0.018 ms | quiet p95 **0.015 ms**; 0.10 ms share passes | Fixture result only. |
| S17 subset encode every four ticks | contended p95 0.664 ms | quiet p95 **0.499 ms**; 0.75 ms share passes | Use shared/rate-bucket encoding as the production starting point. |
| S17 conservative total | contended 3.527/6.519/8.643 ms | quiet **3.027/5.658/8.321 ms** median/p95/p99; fails 4/8 ms | Comparison only; three full encodes/tick is not the intended schedule. |
| S17 production-schedule total | contended 2.394/4.582/6.286 ms | quiet **2.069/3.989/5.849 ms** median/p95/p99; passes 4/8 ms | No claimed headroom: p95 passes by only 0.011 ms and important work is omitted. |
| S03-L, S03-P, S04-P/T, S07, S09–S15 | contended values retained | **Not rerun by owner decision 13** | Make systems work, then improve presentation and optimize during M1. |

## Foundation status matrix

“Complete” means the commissioned bounded foundation question has an integrated record. It does
not mean that the corresponding production system, human review or M1 acceptance is complete.
All timing values explicitly marked **contended** are upper bounds from a shared workstation.

| Task | Foundation status | Key evidence and headline result | Residual risk / open follow-up | Quiet value |
| --- | --- | --- | --- | --- |
| S01 | Complete, bounded | [Asset workflow](../spikes/s01.md): explicit Blender→GLB links, wrapper variants and byte-identical re-export | Production art, direct imported-child overrides and throughput remain outside the proof | n/a |
| S01-W | Complete | [Windows supplement](../spikes/s01-w.md): both GLBs byte-identical; Blender 5.2.2 / exporter 5.2.40 | Recheck after tool/source changes | n/a |
| S02 | Automated implementation complete; human check open | [Controls](../spikes/s02-controls.md): 5 m/s normalized WASD, mouse yaw, left-click fire, 42°/47 m camera, no cutaway | Physical Alt-Tab, aim/control feel, roof and weapon readability | n/a |
| S03 | Complete, bounded | [Session proof](../spikes/s03.md): ENet admission, handoff, freshness and cleanup; ENet bandwidth workaround retained | Production Session/Replication and full baseline still M1 work | n/a |
| S03-R | Technical response/expiry complete; feel open | [Response record](../spikes/s03-r.md) plus [S03-L](../spikes/s03-l.md): exact decision-age expiry fix passes | Physical feel and remote continuity; old pre-fix response values are historical | see S03-L |
| S03-L | Diagnostic complete | Corrected passing direct loopback 317 ms p95; provisional **350 ms p95 allowance**, all contended | Linux comparison and production tuning | Not rerun; contended retained by decision 13 |
| S03-P | Complete, bounded | [Foot prediction](../spikes/s03-prediction.md): predicted p95 19–29 ms physics, 39 ms drawn; correction p95 ≤0.25 m in selected runs, contended | Owner approval of three-frame pending-lag revision; production moving-body contacts and lifecycle | Not rerun; contended retained by decision 13 |
| S03-S | Documentation review complete | [Abstraction review](../spikes/s03-s-abstraction-review.md): ENet-first provider/stream/lifecycle seam | Future Steam adapter has no runtime evidence by design | n/a |
| S04 | Technical body complete; handling review open | [Car spike](../spikes/s04.md), [drive scene](../spikes/s04-drive-scene.md): CharacterBody candidate and live tuning harness | Owner tuning and final dimensions; death now coasts then becomes abandoned/parked | n/a |
| S04-P | Complete, bounded with mixed adverse results | [Car prediction](../spikes/s04-prediction.md): normal passes; post-rebase adverse correction p95 0.576 m fails 0.5 m target; drawn p95 85 ms; **contended** | Clean adverse production proof, moving-car contacts, subjective feel | Not rerun; contended retained by decision 13 |
| S04-T | Complete, bounded | [Transition fixture](../spikes/s04-t.md): seat race, moving/blocked exit, AI release and disconnect coast pass; timings **contended** | Adverse moving-traffic transfer correction 6.999 m; camera smoothing, real clearance and lifecycle races remain | Not rerun; contended retained by decision 13 |
| S05 | Foundation logic/presentation complete | [Chain](../spikes/s05.md), [uncapped presentation](../spikes/s05-uncapped-effects.md): 12 explosions, 144 visits, 12 drawn/0 dropped | Production pool, in-flight join/reset, wreck art/contact and final dimensions | S15 owns cost |
| S06 | Topology complete; visual/UI review open | [Topology](../spikes/s06.md): foot route, two car turns, stale-bake and shared minimap checks pass; scale/top-right accepted | Minimap size/look, whole UI, contested recovery and final-body reruns | n/a |
| S07 | Complete planning guidance | [Environment envelope](../spikes/s07-environment-scale.md): 6/24/96 pass; historical 384 crash; 96 frame p99 18.405 ms, **contended** | Shared grey-block art is not production; no Deck result; 96 is not a product ceiling | Not rerun; contended retained by decision 13 |
| S08 | Windows diagnosis complete; Linux follow-up open | [Windows result](../spikes/s08-windows-observation.md): original-main DEBUG/RELEASE matrix passes with workaround | Linux original-main and Linux-only diagnostics remain non-blocking follow-up | n/a |
| S08-X | Windows/configuration complete; Linux runtime open | [Export smoke](../spikes/s08-x.md): four desktop exports inspect cleanly; Windows release launches quiet; Linux checklist recorded | GodotSteam removal is decided and underway separately; Linux launch not claimed | n/a |
| S08-C | Complete, bounded | [Stability](../spikes/s08-c-stability.md): current no-cutaway 192/288/384 instantiate; 384 crash not reproduced; safe capped GPU method | Historical cause unknown; owner approval to replace unsafe design wording | short diagnostic only |
| S09 | Foundation prototype complete | [Traffic](../spikes/s09.md): 24-car p95/p99 1.165/1.690 ms, 18/18 recoveries per aggregate row, zero sampled overlaps/gridlocks; **contended** | Actual bodies, production graph/replenishment and owner intersection policy | Not rerun; contended retained by decision 13 |
| S10 | Foundation concept complete; first production task | [Pedestrians](../spikes/s10.md): normal graph p95 2.654 ms median, flee 3.658 ms; **contended**; large overlap/stuck counts | Production must improve behavior/budget with acceptance checks; no extra foundation spike | Not rerun; contended retained by decision 13 |
| S11 | Codec/bandwidth direction complete; smoothness open | [Population replication](../spikes/s11.md): worst host out 55.16 KiB/s vs 256 budget; 3.2 KiB join vs 1 MiB; adverse extrapolation median 15.30% | Drawable interpolation/extrapolation policy, full production baseline/input | Not rerun; contended CPU retained by decision 13 |
| S12 | Foundation comparison complete; first hit policy decided | [Combat](../spikes/s12.md) retains bounded ≤250 ms rewind evidence for later; decision 18 starts with host-current-time verdicts and forgiving hit shapes | Review damage/rate starting values; production fire-intent, confirmation, damage/respawn and rocket integration | Not rerun; contended retained by decision 13 |
| S13 | Technical rig path complete | [Characters](../spikes/s13.md): 68 live + 16 dead; throttling 68→30 mixers; contended headless median proxy 35.9% lower | Production art/readability, blending and target-platform evidence | Not rerun; contended retained by decision 13 |
| S14 | Automated audio/settings foundation complete; listening open | [Audio](../spikes/s14.md): exact 8 engine / 8 explosion / 6 weapon voice caps and settings roundtrip | Human mix/listening, production assets/licenses, attributable CPU profiling | Not rerun; contended context retained by decision 13 |
| S15 | Technical VFX comparison complete | [VFX](../spikes/s15.md): all 12/24 roots retained; 24-full frame p95 18.445 ms median, **contended** | Owner approval for tiers; adaptive `amount_ratio` did not prove lower cost; readability | Not rerun; contended retained by decision 13 |
| S16 | Complete proposal | [M1 production plan](../plans/m1-production-plan.md): owner map, promotion plan, testing layers and ordered backlog | Owner ratification of quantitative/product choices in this packet | n/a |
| S17 | Quiet foundation measurement complete; first production task | [Quiet host tick](../spikes/quiet-remeasure-2026-10-09.md): production schedule 2.069/3.989/5.849 ms median/p95/p99 | Fixture passes 4/8 ms by 0.011 ms p95; omitted work means no production headroom claim | Quiet S17 complete |
| P0-TOOLING | Complete | [Baseline repair](../spikes/p0-tooling.md): canonical script checks green; complete Python discovery | Linux tooling execution remains unverified | n/a |
| P0-TOOLING-2 | Complete | [Runner hardening](../spikes/p0-tooling-2.md): 60 FPS guards, post-case sampling, identity receipts and incremental log reads | Long measurements were not rerun merely for this repair | n/a |
| P0-PROFILES | Intentionally deferred | [Owner decision 11](owner-decisions-2026-10-08.md): non-blocking Paseo profile review later | Keep outside P0-GATE | n/a |

## Top production risks and options

1. **Pedestrian behavior and budget (S10).** The prototype misses its planning share and visibly
   fails crowd separation/flow quality. Per owner decision 14, make compact state, spatial indexing,
   crossing reservations and selective queries the first production work, with explicit behavior
   and timing acceptance checks. Do not add another foundation spike or copy fixture internals into
   production.
2. **Whole-host tick budget (S17).** The quiet production schedule passes 4/8 ms, but only by
   0.011 ms at p95 and with real physics, sockets and prediction omitted. Per owner decisions 13–14,
   retain the target as a tunable planning limit, implement shared packet reuse and indexing in the
   first production work, and measure the production path before codec/C3 architecture freezes.
3. **Windows authoritative latency floor (S03-L).** A provisional contended 350 ms p95 allowance
   is much larger than desirable. Keep local prediction mandatory and size history for the tail.
   Replace this allowance with production Windows and later Linux evidence; do not compensate by
   weakening host authority or enabling S12 rewind without the playtest need and bounded host-only
   change required by decision 18.
4. **Remote smoothness (S11).** Bandwidth passes, but adverse delivery extrapolated/froze 15.30%
   of sampled entity frames. Compare the current 200 ms-then-freeze policy with a modestly longer
   bound in a drawable production-like route. Recommend bounded freeze rather than long invented
   travel unless the visual comparison clearly favors the latter.
5. **Linux and Deck.** Windows is the only passing graphical/runtime platform in the recent
   foundation work. Run S08-X's Linux Vulkan checklist before M1-A-GATE. Deck remains later and
   must stay labelled unverified; desktop evidence cannot become a Deck claim.
6. **Foot/car transfer presentation.** S04-T proves ownership safety but reports a 6.999 m adverse
   moving-traffic correction. Preserve camera world framing, define snap/smooth thresholds and
   reject speculative control cleanly before production B1.2.
7. **Production content cost.** S07 reuses tiny grey-block assets; S13/S15 are technical carriers.
   Measure representative production art as C1 families land rather than treating 96 blocks or
   current draw calls as a production budget.

## Owner decisions recorded

The owner recorded decisions 13–18 on 9 October 2026:

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
- **Decision 17 — GodotSteam (audit Q4):** remove the addon/GDExtension in a separate lane, keep
  the S03-S provider abstraction, re-add a pinned release only when Steam adapter work is
  commissioned, and retain S08-X's Steam-library export rejection. This packet does not fold that
  repository change into its docs-only scope.
- **Decision 18 — first hit-registration policy:** clients send fire intent only; the host chooses
  the target and damage at host current time using forgiving enlarged hit shapes sized for typical
  network/interpolation delay at target speed. The shooter gets immediate cosmetic muzzle/tracer
  feedback, while impacts and damage wait for host confirmation. Every intent carries the shooter's
  view tick from day one so S12's bounded ≤250 ms rewind can be added later as a host-only change if
  playtests require it. This non-competitive game favors the simple policy that works and looks fair.

## Owner decisions still open

These remaining choices belong to their named production consumer; they are not extra foundation
or quiet-pass prerequisites under decision 14. An explicit deferral should still name its consumer
or accepted risk.

1. **S03-P command contract:** accept oldest-valid consumption with a three-frame pending-lag bound,
   replacing the earlier newest-valid wording. **Recommendation:** accept; it bounds queue work while
   preserving one host step per tick and measured prediction behavior.
2. **S11 extrapolation:** choose how remote actors behave after the interpolation buffer is exhausted.
   **Recommendation:** retain 200 ms extrapolation then freeze as the safe default, subject to a
   drawable comparison; never extend through the one-second adverse blackout by default.
3. **S12 damage/rate defaults:** review the pistol/SMG/rocket/car-impact starting values as
   balance choices before M1-B2.
4. **S04 handling:** provide drive-scene feedback and an F12 value set. **Recommendation:** run the
   saved harness before freezing B1.1 body/tuning; do not promote defaults solely from automated
   route success.
5. **S17 budget allocation:** ratify or revise traffic 1.5, pedestrians 1.0, replication 0.75,
   combat 0.25, chains 0.10 and remaining work 0.40 ms p95, all inside 4 ms.
   **Recommendation:** use them as adjustable profiling ceilings, not independent entitlements.
6. **Traffic/crossing policy:** choose reservation priority/lights and whether cars yield at marked
   crossings. **Recommendation:** deterministic authored reservations; cars yield at selected marked
   crossings, while uncontrolled player cars remain collision-authoritative.
7. **VFX degradation:** confirm full→reduced→minimum tiers when many explosions overlap, with one
   visible root and all feedback families retained per event. **Recommendation:** approve; dropping
   an event remains forbidden.
8. **Audio starting policy:** accept/revise nearest-eight engines, eight blast voices, six weapon
   voices and ambience under Music. **Recommendation:** treat these as first-pass caps and decide only
   after the listening checklist.
9. **Safe GPU wording:** replace the design's uncapped-headroom instruction with S08-C's capped
   frame/RenderingServer method. **Recommendation:** approve; uncapped runs caused two device removals.
10. **Production testing:** approve adding pinned test-only GUT under M1-D1.1.
    **Recommendation:** approve, excluded from release exports and runtime autoloads.

## Human checks still needed

Use the pinned Godot `4.8.dev7.official.c971f93e7`. These are future owner/reviewer runs;
none was performed while drafting this packet.

### Physical controls, focus and camera

```sh
mise exec -- godot --path . res://tests/fixtures/s02/corner.tscn
```

At 1280×800: walk W and W+D through the four-metre passage; move the mouse independently of
travel; fire before/after rounding the corner; back away while aiming elsewhere; compare roof and
weapon readability. Then hold movement and left mouse, physically Alt-Tab, release both outside
Godot and return. Require neutral movement/fire until a fresh press. Record confusion, misses,
follow comfort, roof obstruction and pistol/SMG/launcher readability.

### Vehicle handling

```sh
mise exec -- godot --path . res://tests/fixtures/s04_drive/drive.tscn
```

Test acceleration, broad and tapped steering at low/high speed, coast versus opposite-input brake,
handbrake recovery, wall contact/reverse and reset. Press F12 and retain the complete
`S04_DRIVE_TUNING` JSON plus maneuver-specific notes.

### Audio listening

```sh
mise exec -- godot --path . res://tests/fixtures/s14/audio_test.tscn
```

Start at safe volume. Check blast/SMG distinction, limiter pumping, 280 ms duck/recovery,
north-up panning, near/far engines, dense-action voice caps, music/ambience masking and persistence
of Master/Music/SFX after restart. Record hardware, output mode and volume context. Stop if the
synthetic noise is uncomfortable.

### Visual review

- Open [`docs/concepts/ui-v1/review.html`](../concepts/ui-v1/review.html) and decide the whole-UI
  direction, especially minimap size/look; the Steam join mockup is not M1 scope.
- Review the actual [S13 crowd capture](../spikes/s13-evidence/crowd-throttled.png) for top-down
  silhouette/palette/death readability, while treating it as technical art only.
- Compare [12-full](../spikes/s15-evidence/12-full.png) and
  [24-full](../spikes/s15-evidence/24-full.png) VFX captures for target/road occlusion and approve
  or reject the proposed tiers.
- Review the six-block world direction through the separately staged
  [world concept handover](../workflows/world-concept-handover.md); it begins at Stage 1 and does
  not authorize later-stage assets before each owner approval.
- On Linux, follow the exact five-step checklist in [S08-X](../spikes/s08-x.md#linux-desktop-launch-checklist)
  and retain Vulkan window/focus/log evidence. This is not a Deck substitute.

## Recommended first production work

After the owner records the P0-GATE disposition from this refreshed packet, start with the work
assigned by decision 14. Open production choices above should be resolved by their named consumers;
they do not require more foundation reruns.

1. **S10 production behavior/budget:** establish the production pedestrian owner and compact state,
   add spatial/crossing policy work, and define behavior plus timing acceptance checks before scaling.
2. **S17 production host budget:** add the real simulation/networking costs incrementally, preserve
   the production encode schedule, and measure against tunable 4/8 ms planning limits before the
   population and codec architectures freeze.
3. **M1-D1.1 — production checks:** pin test-only GUT, add CI/check entrypoints and prove export
   exclusion, consuming P0-TOOLING and P0-TOOLING-2.
4. **M1-A1.1 — Boot/session composition:** saved Boot/menu/status scenes and typed ENet-first
   operation lifecycle, consuming S08-X and S03-S.
5. **M1-A3.1 — LocalSettings/settings UI:** start after D1.1's test seam, based on S14's schema
   boundary but not its placeholder sounds.
6. **M1-C1.1 — starter road/building/prop subset:** start after owner art quality selection,
   using the byte-identical S01/S01-W pipeline.
7. **M1-C2.1 — CityData and first production sector:** begin when the approved starter subset
   exists; preserve one topology/minimap representation from S06.
8. Continue **M1-A1.2** after the provider seam stabilizes. Do not freeze M1-A2.2's production
   codec until its S11/S17 acceptance checks are defined, and do not copy S09/S10 fixture internals
   into production.

The detailed ordering and hard consumers remain in the
[M1 production plan](../plans/m1-production-plan.md#5-foundation-entry-criteria-and-ordered-m1-backlog).
