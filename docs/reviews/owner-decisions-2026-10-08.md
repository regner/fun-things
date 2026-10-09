# Owner decisions — 8 October 2026

Regner made decisions 1–11 in a walkthrough with the orchestrator and gave instruction
12 in chat later that evening. This record transcribes those decisions, the explicitly
labelled orchestrator defaults to which Regner did not object, and the scope authorized
by that later instruction. It does not ratify the orchestrator's proposed measurements.

1. **Integration:** fast-forward main after clean review (done at `29ee423`). Do not
   push. No further task is created by this completed integration decision.
2. **ENet upstream defect (S08):** prepare offline-review markdown with a summary,
   detailed explanation, ELI5 and proposed GitHub issue. Do not file it. Keep the
   workaround. Follow-up: retain the offline review and workaround; file nothing
   without a later decision.
3. **On-foot controls and camera (S02):** the 42° camera is ratified: top-down at
   47 m with fixed north-up orientation. The 50° alternative is rejected. WASD moves
   the character screen/world-relative and the character faces the mouse cursor,
   replacing tank turning. Remove building cutaway for now. Held weapon silhouettes
   are accepted. Orchestrator defaults not objected to: normalize diagonals; use one
   5 m/s speed in all directions; instant start/stop; snap facing to the mouse ground
   point each physics tick; fire with left mouse; defer gamepad left-stick movement
   and right-stick aim. Follow-up: the S02 controls lane implements and validates this.
4. **On-foot response (S03-R):** client-side prediction is required for the local
   character. Shared movement rules must be used, replay has no side effects, and
   authoritative corrections win. Follow-up: implement and validate the prediction lane.
5. **Cars (S04):** no firing from cars for now. Exit only when the car is stopped.
   A disconnected driver's car coasts to a stop without braking. Local-driver car
   prediction is required. Build a single-player drive scene for handling feel review.
   Orchestrator default not objected to: stopped means speed below 0.5 m/s; otherwise
   return `EXIT_MOVING`. Follow-up: the S04 drive-scene lane and later car-prediction lane.
6. **Explosions and chains (S05):** remove the on-screen explosion cap; every explosion
   gets its effect. Other provisional defaults are accepted for later tuning: car
   100 HP, 100 damage so one blast destroys neighbours, 4.1 m radius, no falloff,
   obstruction ignored, 0.1 s chain delay, wreck duration 5 s, and friendly fire plus
   self-damage always on. Follow-up: remove the cap and rerun effect-cost evidence.
7. **Layout and minimap (S06/UI):** accept 9 m roads, 4 m sidewalks and 48 m extent
   for the grey-block prototype; building setback and colours are fine for now.
   Accept the minimap's top-right position. Do not accept its size or look: the current
   version is adequate only for the initial prototype and needs iteration. Commission
   UI mockups from a GPT-6-Astra agent and iterate the whole UI. Follow-up: UI mockups.
8. **Environment scaling (S07):** reframe S07 as a visual/graphical environment-scaling
   investigation that informs how large a city to plan. It is not a requirement or
   capacity gate. Network, AI and population are out of scope because they depend on
   what is near players, not city size. D1 is moot; D2 becomes representative environment
   density and variety per block; D4 budgets are guidance only. Build saved city variants
   from existing grey-block sectors/building prefabs at increasing block counts, for
   example 6, 24, 96 and 384, stopping early at a limit. Measure load time, RAM/VRAM,
   node/static-collider counts and 60-capped frame time along a route with the 42° camera.
   Report a cost-versus-block envelope with caveats for shared grey-block assets versus
   production-art variety and no Deck measurement. Follow-up: the S07 environment lane.
9. **Initial transport (S03-S):** the initial game uses ENet only. Do no Steam-specific
   features or testing now. Ensure session/transport abstractions and APIs can later
   support a Steam adapter, including friend joins, lobby identity mapping, reliable
   and unreliable message lanes, and connection lifecycle. Follow-up: abstraction review.
10. **Engine and delivery targets (S08):** stay on Godot 4.8-dev7 for now. Linux must
    keep working, but Linux confirmation of the ENet fix and Linux-only release
    `tree_exited` diagnostics/upstream PR #123998 do not block proceeding; follow up on
    a Linux machine. Orchestrator defaults not objected to: Windows and Linux desktop
    are M1 targets, with Steam Deck later.
11. **Profiles (P0-PROFILES):** keep this as a Paseo profiles task and review it later;
    it must not block progress. P0-GATE therefore treats it as non-blocking.
12. **Foundation completeness instruction (8 October, evening):** Regner instructed,
    “Review all of the work ... and whats left leading up to P0-Gate. Is there anything
    else ... researched, planned, tested ... before we move onto production? Have we
    researched and tested AI for pedestrians and vehicles? ... If anything is lacking
    create a foundation task for it and get it done. Run as much in parallel as you can.”
    This authorizes orchestrator-created S09–S16 and the audit-derived P0-TOOLING,
    S03-L, S08-X, S08-C, S01-W, S03-P, S04-P, S04-T and S17 tasks listed in
    [section 4 of the P0 readiness audit](p0-readiness-audit-2026-10-08.md).
    Their quantitative criteria are orchestrator proposals derived from the product
    budgets and remain pending owner review at P0-GATE. P0-GATE depends on unfinished
    blocking S02–S08 work, S03-P, S04-P, S09–S17 and the audit-derived gap tasks.

These decisions supersede contradictory earlier planning text. Historical evidence
and stopped experiments remain historical rather than being rewritten as if they used
the newly selected rules.
