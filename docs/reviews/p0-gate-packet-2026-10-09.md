# P0-GATE owner review packet — 9 October 2026

This packet reconciles the integrated foundation work at local `main` revision `13722e0`.
It is a decision aid, not an assertion that P0-GATE has passed. The
[8 October owner decisions](owner-decisions-2026-10-08.md) remain authoritative; the
[P0 readiness audit](p0-readiness-audit-2026-10-08.md) explains why the additional
foundation tasks were commissioned.

## Executive summary

**Recommendation: do not record P0-GATE as passed yet.** The planned foundation work is now
integrated and is sufficient to make the main production architecture concrete: linked source
assets, world-relative foot control, ENet session boundaries, local foot/car prediction,
foot-to-car transfer, bounded chains, shared topology, desktop export configuration, traffic and
pedestrian prototypes, packed population replication, authoritative combat, character/audio/VFX
carriers, and an integrated host-tick composition all exist as executable evidence.

The evidence does **not** show that the current foundation meets every proposed production budget
or subjective requirement:

- S10's 64-pedestrian prototype misses its proposed 1 ms p95 share and produces unacceptable
  overlap/stuck counts.
- S17's contended production-schedule composition is 2.394/4.582/6.286 ms
  median/p95/p99, so it misses the proposed 4 ms p95 whole-host target before real body physics,
  sockets and prediction are added.
- S11 fits the bandwidth budgets with large margin, but remote smoothness is not accepted.
- S03-L leaves a provisional 350 ms p95 Windows authoritative-loop allowance.
- Linux graphical/runtime confirmation remains unperformed; Steam Deck is explicitly later.
- Physical Alt-Tab, walking/aim feel, vehicle handling, audio listening and several visual
  reviews still need a human.
- Combat defaults, lag compensation, traffic/crossing policy, visual degradation and internal
  budget allocations are proposals awaiting owner review.

The quiet timing pass that should separate contention from subsystem cost is running while this
packet is drafted. Its results are deliberately not anticipated here. The owner can review the
architecture and product questions now, but should defer the final performance disposition until
the marked quiet fields are filled.

## Quiet re-measurement — follow-up must fill this section

> **TODO(QUIET):** `docs/spikes/quiet-remeasure-2026-10-09.md` does not exist at packet
> preparation time. Replace every TODO below from that committed record; do not copy the
> contended values into this column or infer a pass from lower process counts.

| Workload | Contended evidence currently available | Quiet re-measurement | Gate use after fill |
| --- | --- | --- | --- |
| S03-L Windows authority loop | passing direct loopback p95 317 ms; contended | **TODO(QUIET-S03-L or NOT-RERUN)** | Replace the provisional allowance only if the quiet record measured this path. |
| S09, 24 moving cars | p95 1.165 ms, p99 1.690 ms; contended | **TODO(QUIET-S09)** | Compare with proposed traffic share and preserve behavior outcomes. |
| S10, 64 pedestrians, normal graph | p95 median/worst 2.654/3.146 ms; contended | **TODO(QUIET-S10-NORMAL)** | Does not erase overlap/stuck quality failures even if timing improves. |
| S10, flee graph | p95 median/worst 3.658/3.916 ms; contended | **TODO(QUIET-S10-FLEE)** | Compare with the proposed 1 ms share; retain all-agent reaction checks. |
| S11 encode/decode | encode p95 median 492–625 us; decode 604–756 us; contended | **TODO(QUIET-S11)** | CPU budgeting only; bandwidth evidence is already measured separately. |
| S13 character presentation | graphical frame tails and headless process proxy were contended | **TODO(QUIET-S13)** | Use for presentation planning, not host simulation. |
| S14 audio | no attributable audio CPU monitor; contended process context only | **TODO(QUIET-S14)** | Record limitation if the quiet pass still cannot isolate audio cost. |
| S15 VFX | 24 full frame p95 18.445 ms median; contended | **TODO(QUIET-S15)** | Require safe capped method and retained effect roots. |
| S17 production schedule | 2.394/4.582/6.286 ms median/p95/p99; contended | **TODO(QUIET-S17)** | Principal evidence for the proposed 4/8 ms host target. |

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
| S03-L | Diagnostic complete | Corrected passing direct loopback 317 ms p95; provisional **350 ms p95 allowance**, all contended | Quiet Windows replacement and Linux comparison | **TODO(QUIET-S03-L)** |
| S03-P | Complete, bounded | [Foot prediction](../spikes/s03-prediction.md): predicted p95 19–29 ms physics, 39 ms drawn; correction p95 ≤0.25 m in selected runs, contended | Owner approval of three-frame pending-lag revision; production moving-body contacts and lifecycle | not scheduled here |
| S03-S | Documentation review complete | [Abstraction review](../spikes/s03-s-abstraction-review.md): ENet-first provider/stream/lifecycle seam | Future Steam adapter has no runtime evidence by design | n/a |
| S04 | Technical body complete; handling review open | [Car spike](../spikes/s04.md), [drive scene](../spikes/s04-drive-scene.md): CharacterBody candidate and live tuning harness | Owner tuning, final dimensions, death behavior | n/a |
| S04-P | Complete, bounded with mixed adverse results | [Car prediction](../spikes/s04-prediction.md): normal passes; post-rebase adverse correction p95 0.576 m fails 0.5 m target; drawn p95 85 ms | Clean adverse production proof, moving-car contacts, subjective feel | not scheduled here |
| S04-T | Complete, bounded | [Transition fixture](../spikes/s04-t.md): seat race, moving/blocked exit, AI release and disconnect coast pass | Adverse moving-traffic transfer correction 6.999 m; camera smoothing, real clearance and lifecycle races remain | not scheduled here |
| S05 | Foundation logic/presentation complete | [Chain](../spikes/s05.md), [uncapped presentation](../spikes/s05-uncapped-effects.md): 12 explosions, 144 visits, 12 drawn/0 dropped | Production pool, in-flight join/reset, wreck art/contact and final dimensions | S15 owns cost |
| S06 | Topology complete; visual/UI review open | [Topology](../spikes/s06.md): foot route, two car turns, stale-bake and shared minimap checks pass; scale/top-right accepted | Minimap size/look, whole UI, contested recovery and final-body reruns | n/a |
| S07 | Complete planning guidance | [Environment envelope](../spikes/s07-environment-scale.md): 6/24/96 pass; historical 384 crash; 96 frame p99 18.405 ms | Shared grey-block art is not production; no Deck result; 96 is not a product ceiling | historical values; no replacement required for gate |
| S08 | Windows diagnosis complete; Linux follow-up open | [Windows result](../spikes/s08-windows-observation.md): original-main DEBUG/RELEASE matrix passes with workaround | Linux original-main and Linux-only diagnostics remain non-blocking follow-up | n/a |
| S08-X | Windows/configuration complete; Linux runtime open | [Export smoke](../spikes/s08-x.md): four desktop exports inspect cleanly; Windows release launches quiet; Linux checklist recorded | Owner GodotSteam keep/remove decision; Linux launch not claimed | n/a |
| S08-C | Complete, bounded | [Stability](../spikes/s08-c-stability.md): current no-cutaway 192/288/384 instantiate; 384 crash not reproduced; safe capped GPU method | Historical cause unknown; owner approval to replace unsafe design wording | short diagnostic only |
| S09 | Foundation prototype complete | [Traffic](../spikes/s09.md): 24-car p95/p99 1.165/1.690 ms, 18/18 recoveries per aggregate row, zero sampled overlaps/gridlocks; **contended** | Actual bodies, production graph/replenishment and owner intersection policy | **TODO(QUIET-S09)** |
| S10 | Foundation spike complete; proposal not production-ready | [Pedestrians](../spikes/s10.md): normal graph p95 2.654 ms median, flee 3.658 ms; **contended**; large overlap/stuck counts | Decide follow-up spike vs M1 optimization; crossing/crowd-look policy | **TODO(QUIET-S10)** |
| S11 | Codec/bandwidth direction complete; smoothness open | [Population replication](../spikes/s11.md): worst host out 55.16 KiB/s vs 256 budget; 3.2 KiB join vs 1 MiB; adverse extrapolation median 15.30% | Drawable interpolation/extrapolation policy, full production baseline/input | **TODO(QUIET-S11)** |
| S12 | Foundation comparison complete; owner selection open | [Combat](../spikes/s12.md): 250 ms target rewind improves normal agreement to 89.3% pedestrian / 62.5% car medians; adverse fast car 44.8% | Ratify rewind and combat defaults; production damage/respawn/rocket integration | query timings contended; quiet composition in S17 |
| S13 | Technical rig path complete | [Characters](../spikes/s13.md): 68 live + 16 dead; throttling 68→30 mixers; contended headless median proxy 35.9% lower | Production art/readability, blending and target-platform evidence | **TODO(QUIET-S13)** |
| S14 | Automated audio/settings foundation complete; listening open | [Audio](../spikes/s14.md): exact 8 engine / 8 explosion / 6 weapon voice caps and settings roundtrip | Human mix/listening, production assets/licenses, attributable CPU profiling | **TODO(QUIET-S14)** |
| S15 | Technical VFX comparison complete | [VFX](../spikes/s15.md): all 12/24 roots retained; 24-full frame p95 18.445 ms median, **contended** | Owner approval for tiers; adaptive `amount_ratio` did not prove lower cost; readability | **TODO(QUIET-S15)** |
| S16 | Complete proposal | [M1 production plan](../plans/m1-production-plan.md): owner map, promotion plan, testing layers and ordered backlog | Owner ratification of quantitative/product choices in this packet | n/a |
| S17 | Integrated measurement complete; proposed budget misses | [Host tick](../spikes/s17.md): production schedule 2.394/4.582/6.286 ms median/p95/p99, **contended** | p95 miss before omitted real physics/network work; optimize and rerun | **TODO(QUIET-S17)** |
| P0-TOOLING | Complete | [Baseline repair](../spikes/p0-tooling.md): canonical script checks green; complete Python discovery | Linux tooling execution remains unverified | n/a |
| P0-TOOLING-2 | Complete | [Runner hardening](../spikes/p0-tooling-2.md): 60 FPS guards, post-case sampling, identity receipts and incremental log reads | Long measurements were not rerun merely for this repair | n/a |
| P0-PROFILES | Intentionally deferred | [Owner decision 11](owner-decisions-2026-10-08.md): non-blocking Paseo profile review later | Keep outside P0-GATE | n/a |

## Top production risks and options

1. **Pedestrian behavior and budget (S10).** The prototype misses the proposed p95 share and
   visibly fails crowd separation/flow quality. Option A (recommended) is a bounded pre-production
   optimization spike using compact state, spatial indexing, crossing reservations and selective
   capsule queries, then quiet/integrated measurement. Option B carries it into M1-C3 behind an
   explicit acceptance risk; it avoids more fixture work but makes production architecture absorb
   an unresolved behavior and budget problem.
2. **Whole-host tick budget (S17).** The best measured schedule still misses p95 under contention
   and omits several real costs. Option A (recommended) keeps 4/8 ms unchanged, implements shared
   packet reuse plus pedestrian/traffic indexing, and repeats on quiet Windows before codec/C3
   freeze. Option B accepts the risk into M1-D3, but must not reinterpret the current result as a
   pass or silently lower caps/tick rate.
3. **Windows authoritative latency floor (S03-L).** A provisional 350 ms p95 allowance is much
   larger than desirable. Keep local prediction mandatory and size history for the tail. Replace
   this allowance with quiet Windows and later Linux evidence; do not compensate by weakening host
   authority or increasing S12 rewind without owner review.
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

## Owner decisions needed

Record one answer per line in the gate decision; an explicit deferral must name the consumer it
holds or the risk it accepts.

1. **P0-GATE scope (audit Q1):** confirm that all commissioned foundation evidence in the matrix
   is reviewed, with unresolved human/performance rows either completed or explicitly waived.
   **Recommendation:** keep the gate open until quiet values and the named human checks are recorded;
   do not reopen completed tasks merely because production work remains.
2. **M1 desktop frame target (audit Q2):** ratify or replace capped 60 FPS with frame p99 ≤20 ms
   on named Windows and Linux hardware. **Recommendation:** ratify it, using S08-C's safe capped
   renderer timings rather than uncapped throughput.
3. **Driver death (audit Q3):** choose coast, brake or another rule when the driver dies.
   **Recommendation:** coast under neutral control, matching disconnect, unless playtesting shows a
   clear lifecycle/gameplay problem; record death separately rather than inferring it from disconnect.
4. **GodotSteam in ENet-only M1 (audit Q4):** remove it or keep it disabled and excluded.
   **Recommendation:** keep vendor source in the repository for now, disabled at runtime and excluded
   by the proven S08-X export filters; reconsider removal before release hardening.
5. **Quiet-pass ownership/checkpoint (audit Q5):** name who accepts and integrates the current quiet
   pass and when the packet is refreshed. **Recommendation:** one owner fills this packet and the
   quiet record before the final P0-GATE disposition; do not split acceptance across subsystem lanes.
6. **S03-P command contract:** accept oldest-valid consumption with a three-frame pending-lag bound,
   replacing the earlier newest-valid wording. **Recommendation:** accept; it bounds queue work while
   preserving one host step per tick and measured prediction behavior.
7. **S11 extrapolation:** choose how remote actors behave after the interpolation buffer is exhausted.
   **Recommendation:** retain 200 ms extrapolation then freeze as the safe default, subject to a
   drawable comparison; never extend through the one-second adverse blackout by default.
8. **S12 hit registration and combat defaults:** accept/revise 250 ms target-only rewind and the
   pistol/SMG/rocket/car-impact starting values. **Recommendation:** accept target-only rewind and
   client-intent-only authority; review balance values separately before M1-B2.
9. **S04 handling:** provide drive-scene feedback and an F12 value set. **Recommendation:** run the
   saved harness before freezing B1.1 body/tuning; do not promote defaults solely from automated
   route success.
10. **S10 disposition:** require another optimization/behavior spike or carry it into M1-C3.
    **Recommendation:** require a small follow-up before production population architecture freezes.
11. **S17 budget allocation:** ratify or revise traffic 1.5, pedestrians 1.0, replication 0.75,
    combat 0.25, chains 0.10 and remaining work 0.40 ms p95, all inside 4 ms.
    **Recommendation:** use them as profiling ceilings, not independent entitlements, pending quiet data.
12. **Traffic/crossing policy:** choose reservation priority/lights and whether cars yield at marked
    crossings. **Recommendation:** deterministic authored reservations; cars yield at selected marked
    crossings, while uncontrolled player cars remain collision-authoritative.
13. **VFX degradation:** confirm full→reduced→minimum tiers when many explosions overlap, with one
    visible root and all feedback families retained per event. **Recommendation:** approve; dropping
    an event remains forbidden.
14. **Audio starting policy:** accept/revise nearest-eight engines, eight blast voices, six weapon
    voices and ambience under Music. **Recommendation:** treat these as first-pass caps and decide only
    after the listening checklist.
15. **Safe GPU wording:** replace the design's uncapped-headroom instruction with S08-C's capped
    frame/RenderingServer method. **Recommendation:** approve; uncapped runs caused two device removals.
16. **Production testing:** approve adding pinned test-only GUT under M1-D1.1.
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

Do not start these as a claim that P0-GATE passed. After the owner records the decisions above,
quiet results are reconciled, and any required S10/S17 follow-up is complete or explicitly waived:

1. **M1-D1.1 — production checks:** pin test-only GUT, add CI/check entrypoints and prove export
   exclusion, consuming P0-TOOLING and P0-TOOLING-2.
2. **M1-A1.1 — Boot/session composition:** saved Boot/menu/status scenes and typed ENet-first
   operation lifecycle, consuming S08-X and S03-S.
3. **M1-A3.1 — LocalSettings/settings UI:** start after D1.1's test seam, based on S14's schema
   boundary but not its placeholder sounds.
4. **M1-C1.1 — starter road/building/prop subset:** start after owner art quality selection,
   using the byte-identical S01/S01-W pipeline.
5. **M1-C2.1 — CityData and first production sector:** begin when the approved starter subset
   exists; preserve one topology/minimap representation from S06.
6. Continue **M1-A1.2** after the provider seam stabilizes. Do not freeze M1-A2.2's production
   codec until the S11/S17 budget disposition is recorded, and do not start production population
   by copying S09/S10 fixture internals.

The detailed ordering and hard consumers remain in the
[M1 production plan](../plans/m1-production-plan.md#5-foundation-entry-criteria-and-ordered-m1-backlog).
