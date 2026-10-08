# S05 — bounded authoritative damage and chain experiment

Predeclared 8 October 2026 before S05 implementation or measurements. Direct lead
`50c01e86-3164-4592-a48b-8181b3275d63`, GPT-6.1-Sol HIGH (effective HIGH verified),
workspace `wks_42b1f3912dacdb26`, branch `s05-authoritative-chain-fixture`, base LOCAL
main `c0eda26f7f010af75bbf10c272ec5cb001442331`. Root alone coordinates integration
and editor relocation/archive. ONE experiment, normally 1–2 focused days, ONE fresh
Sol HIGH independent review and justified correction cycle. No production combat,
vehicle/population/reset architecture, general replay or transport framework.

## Question, prerequisites and fixture

Can host-owned damage and finite chain jobs finish once with bounded work, even
when cosmetic presentation is saturated? Read raw S05 in TODO, the accepted
[fifth checkpoint](../reviews/plan-check-2026-10-08-05.md), [S03](s03.md),
[S04](s04.md), [body/seat contract](s04-contracts.md), [API](../api-contracts.md),
and repository development/assets/multiplayer guidance and review/toolkit skills.
S03 owns session/admission, primitive validation and current baseline/handoff.
S04 supplies reusable linked car/track and public configure/neutralize/body APIs;
it supplies NO damage/destruction owner. Original fixtures, sources, exports,
UID/import metadata, project, pins and vendor files remain immutable.

Use saved new S05 scenes with unchanged S04 CharacterBody3D instances and track.
The provisional car collider is 1.8×1.5×3.4 m, visual 1.88×1.54×3.4 m; S02 actor
radius0.38/height1.8 m remains provisional. Three-car centres at X0/4/12 m give
near/far independent expected outcomes. Extend the same fixture with twelve cars
at saved four-metre grid spacing, hiding all car visuals for the off-camera burst.
No new Blender assets are essential. Technical neutral cars are neither wreck art
nor ratified body, dimensions, turning, blast spacing, controls, feedback or fun.

## Falsifiable criteria declared before measurement

1. Public host APIs: root shot wrecks car A, its blast wrecks near B, far C retains
   health100. Each wreck gets exactly one explosion and one occupant sentinel death
   (A occupied only), seat clears once. Duplicate ShotId during active work AND
   after all active damage caches retire produce zero extra damage/events/jobs.
   Wrong session/revision/shooter generation, invalid sequence and passive calls
   reject without mutation. Per-shooter monotonic acceptance watermark survives
   retirement/disconnect until session teardown; no ID reuse in this fixture.
2. Physics: unchanged live collider remains queryable through wreck retention;
   the body is neutralized and simulation disabled before terminal observers run.
   After retention and completed blast work the host collision clears. A passive
   replica has zero simulation collision before tree entry. Hydration restores
   current life/health/seat/collision revision before admission; motion cannot undo it.
3. Twelve-car burst: accept at most four root shots per tick over three ticks,
   reserve one chain job per car independently of eight cosmetic slots. All twelve
   terminal cars complete all 144 bounded target visits within 60 host ticks of
   first shot. Queue peak <=12, target visits <=4/tick, root requests <=4/tick,
   active damage target cache <=12, no duplicate source-target outcomes. Complete
   jobs sort by (due tick, EventId sequence); retire caches only on job completion.
   Exactly eight cosmetic reservations and four saturation drops with 120-tick
   presentation lifetime; hidden visuals must not change twelve final outcomes.
4. Real separate ENet processes: initial admitted client sends duplicate fire intent;
   server derives participant from RPC sender and validates admitted exact context,
   primitive shape, size/rate/window before resolve_shot. Only host chooses target/
   amount. Duplicate request after cache retirement remains rejected. Forged owner,
   stale context, malformed and oversized intents change no outcome. Live client
   applies current reliable rows once and each live event once. A third process
   joins after chains finish and before wreck expiry: current wreck/health/occupant
   state at baseline install with disabled input, then normal S03 admission; zero
   historical explosion reservations. Wrong-session/revision/generation cuts and
   stale/duplicate current rows rejected atomically. No full during-chain joining
   races, sustained load, Steam or platform acceptance claimed.
5. Validate pinned lint, explicit compilation of every owned affected script,
   dependency UID/path agreement, editor save/reopen including inherited resources,
   saved node identities/bytes and all original tracked-file fingerprints. Inspect
   every runtime log beyond exit status. Retain raw failures separately. One
   meaningful negative mutation may check ShotId retirement if needed; no copied
   formula expectations or broad error suppression.

## Provisional policies and hard bounds

Health100, root damage100 and blast damage100. Radius4.1 m, flat centre-distance
query, no falloff, **obstruction ignored**, self/friendly damage enabled. No wall
protection or host historical hit queries established. Six 60 Hz host ticks delay
(100 ms nominal), ordering by due tick then monotonically allocated EventId.
Single owner marks terminal and closes motion before scheduling exactly one blast.
An occupant is a fixed nonrendering fixture sentinel, killed/released atomically;
no production player death, respawn, seat transition or equipment rule implemented.

At most12 saved cars, one reserved pending/active job per car, four target visits
and four root resolution calls/tick; bounded work estimate 12×12=144 target visits
plus12 root resolutions, at most36 target-work ticks plus initial delay/spacing.
Reject unreserved external work before shot acceptance; accepted jobs never depend
on cosmetic capacity. Four registered shooter refs maximum per session, immutable
IDs/generation, sequence-ahead window16, retained monotonic watermark even after
shooter removal. No completed per-event/per-target history; active job target cache
retired only after all its targets. Reject new shooter when lifetime slots exhausted.

Wreck retains the original stationary box for300 host ticks (5 s nominal), then
retires only after its own blast completes. Twelve retained wrecks maximum, no
replenishment or eviction. Replicas remain passive per S04; current collision
revision is applied with lifecycle before admission, not a second physics owner.
Live effects use EventId/dependency fences and eight120-tick slot reservations;
hydration suppresses historical events. Current wreck presentation retains the
unchanged technical car mesh. No explosion geometry/audio/drawn VFX is claimed.

Wire: reuse four-channel S03 session/baseline/handoff/movement contract. New fire
intent <=512 Variant bytes, exact three fields (context, sequence, boolean fire), 4/s burst4,
sequence window16, no request queue. New current car cut <=8192 UTF-8 bytes,
<=12 fixed rows and <=12 live events; no future event buffer. Request and event
bounds are application evidence, not proof of predecoder transport allocation or
production capacity. Sequence/EventId integer bound2,147,483,647; fail closed before
exhaustion. Session teardown clears jobs/caches/watermarks/rate/effect slots/bindings.

## Stop boundary and open gates

Do not repair renderer/display, repeat the known can_draw=false/zero drawn diagnosis,
or change services/configuration/pins/vendor. If safe local installed-handler recovery
fails, report the concrete operational blocker. Technical public API/physics/ENet
outcomes do not prove drawn feedback, physical input, feel, device or Steam behavior.
Full S02/S03-R/S04, P0-GATE, S07 and production gates stay OPEN. Rerun affected
spacing/contact rows after final S04/S02 dimensions are ratified. Full joining
races/reset/sustained capacity and production cleanup remain M1-B3/M1-D.
S05 TODO is removed only if every explicit bounded acceptance has independent
coverage; otherwise retain exact actionable remaining gates with the resolving change.

## Results and evidence

Pending. The declaration above is saved before S05 measurement.
