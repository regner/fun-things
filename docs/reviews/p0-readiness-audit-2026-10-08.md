# P0 readiness audit — 8–9 October 2026

Independent read-only audit of the foundation work, the plan to P0-GATE, and confidence in
every system the M1 brief requires. The auditor changed no code or planning file. This
report is the only file written by the audit lane.

## Snapshot audited

| Item | State |
| --- | --- |
| Audit lane base | `4fa669a` (lane `lane/p0-audit`) |
| Main / `s08-enet-bandwidth` during audit | `4fa669a` → `9d1ee3f` (S07-ENV integrated) → `ffb7ede` (S05-NOCAP integrated). Findings cite `ffb7ede` unless stated |
| Handover base | `fb1a372`; 34 commits to `ffb7ede` |
| Committed, unintegrated lanes | `decisions-docs` (`c282a62`, `2e2d3bf`), `s03s-abstraction` (`15ec6e6`, review BLOCK), `ui-mockups` (`5852d0c`) |
| Uncommitted work in progress | `s02-controls` (26 files), `s04-drive` (5), `s09`, `s10`, `s11`, `s12`, `s13`, `s14`, `s15`, `ui-mockups` (fix round). `s16-production-plan` has no files yet |
| Not launched | Foot prediction and car prediction lanes, queued after S02 controls in `docs/workflows/root-handover.md` |

Wave 3 (S09–S16) has no committed output. Its contribution to confidence below is therefore
**planned, not evidenced**. The laptop slept from 23:06 to 07:24, so wave-3 lanes lost most
of a night.

## 1. Commit and record review

### Main since `fb1a372`

| Commits | Claim | Assessment |
| --- | --- | --- |
| `828df12`, `f77bb86`, `26c6a41`, `59eb955` | An upstream ENet `create_server` argument-order defect explains the S08 20 ms stall. The `bandwidth_limit(0, 0)` workaround fixes it. | **Supported.** The fix is one line plus a comment in `tests/fixtures/s03/transport.gd:46-48` (call at line 48). `proof.gd:169-173` asserts `PEER_PACKET_THROTTLE_LIMIT == PACKET_THROTTLE_SCALE`, independently of the formula. Telemetry, the MRP and logs are retained. The upstream write-up correctly states "NOT POSTED" and links the existing #123963, matching owner decision 2. Residual: the check runs only at the end of the subset case. |
| `f529bb4`, `dd65b40` (S03-R/S04 Windows) | Post-fix drawn response is 123/273/379 ms for S03-R and 90/277/386 ms for S04. | **Numbers supported, but the framing is incomplete.** S03-R adverse **failed** its expiry criterion (`docs/spikes/s03-r.md:297`). The task-requirements S03-R bullet on main lists the p95s but omits the failure. The proposed analyzer fix is still unapplied. Post-fix *baseline* (zero injected RTT) authority response is 109–123 ms drawn and **255 ms headless** (`s03-r.md:283`), against 69 ms historically on Linux. The record says Windows' higher latency is "uninvestigated". That is an open anomaly, not a platform constant (see gap G1). |
| `33465c6`, `92134ba` | Test discovery and gate independence; S08 export gated on diagnostics. | Acceptable. However, `tools/s08/windows_observation.py:155` strips `[autoload]` and `[editor_plugins]` before exporting. The real project's export with the MCP autoload and the loaded GodotSteam GDExtension was therefore never exercised (gap G6). |
| `48e2380`, `1f39df0`, `ad09e4f` (S05 Windows draw) | Eight drawn and four dropped, with settled hydration. | Supported. These results were superseded by S05-NOCAP. |
| `6efa3c9`, `19fbd4d`, `29ee423` (S07 graphical T) | 60-capped T passed 3/3. Both uncapped attempts ended in GPU device removal. | Supported after the T-FIX retention rework (`analyze_hitches.py` + raw `.gz` files). Note: **uncapped rendering crashed the GPU driver twice on this laptop.** The design still asks for "CPU/GPU times uncapped for headroom" (`docs/design.md` frame-time row). That method cannot be run safely here. |
| `84e793c`…`242b644` (C0 comparator) | 20 headless and 3 windowed fresh-session trials passed. Expectations derive from capacity. | Supported. The three windowed PNGs are byte-identical (same SHA in the S05-NOCAP record). That is expected for a deterministic camera, but they prove nothing per trial beyond the receipt. |
| `e0b152f`, `e174c4d` (S06 Windows) | Proof plus 42°/50° route/minimap captures. | Supported. Camera, layout and minimap position were later ratified by the owner. |
| `fda435f`…`4fa669a` (S02 Windows) | Exact 1280×800 automatic draws. Native focus is inconclusive. | Supported and honestly labelled. Physical Alt-Tab is still open. |
| `6c1f601`…`9d1ee3f` (S07-ENV) | The 6/24/96-block envelope passes. 384 blocks crashed with `0xC0000005`. | **Supported, with caveats.** (a) The machine is an RTX 4070 **Laptop** GPU, while the record says "desktop CPU" (orchestrator P3 note). (b) Every building instance overrides its script with the S02 cutaway `building_view.gd` (`tests/fixtures/s07_env/city_6.tscn:7,90…`), and the VRAM fit includes per-instance cutaway materials. The measured envelope therefore includes a presentation path the owner just removed. (c) **Integration hazard (P1):** `s02-controls` deletes `building_view.gd` and `actor_cutaway.gdshader`. Its base predates S07-ENV, so after rebase all four `city_*.tscn` files and `tools/s07_env/run.py:41-43` will reference deleted files. The orchestrator note covers only the `run.py` staging list, not the saved scene references. |
| `23335c2`…`ffb7ede` (S05-NOCAP) | Every explosion in the 12-car fixture gets a saved effect (12 drawn, 0 dropped). | Supported, and honestly bounded. It is a fixed 12-slot authoring, not a production pool, as the record says. Cost is unmeasured and delegated to S15. |

### Committed lanes not yet integrated

- **decisions-docs.** The first commit generalized "S07 D4 budgets are guidance only" to
  *all* M1 budgets. It also extended disconnect coasting to driver death. The reviewer
  blocked both, and `2e2d3bf` fixes them correctly. Remaining issues:
  - **P0-GATE dependency narrowing (P1, owner question).** The `TODO.md` P0-GATE line
    previously read "After: S02, S03-S, S03-R, S04, S05, S06, S07, S08". It now reads
    "After: S09…S16" only (`TODO.md:33-34` on the lane). S02 (controls change), S03-R
    (required foot prediction) and S04 (drive scene and required car prediction) remain
    open TODO items, but they **no longer gate P0**. Production could therefore start with
    the highest-risk netcode, prediction, wholly unproven. No owner decision removed these
    dependencies.
  - **No M1 frame target.** The only frame-time row is Deck-specific
    (`design.md:181`), and Deck targets are now owner-deferred. M1 therefore has no
    desktop frame-pacing target at all. Needs an explicit owner decision, for example
    60 FPS p99 ≤ 20 ms on named Windows/Linux hardware.
  - **Stale handover.** `docs/workflows/root-handover.md`'s active-lane list predates
    wave 3. It omits S09–S16 and this audit.
  - **Dropped follow-up.** The S08 bullet dropped "export delivery/target compatibility"
    and "ENet with Steam uninstalled". M1-A-GATE keeps "Steam absent", but nobody owns an
    early export check (G6).
- **s03s-abstraction (`15ec6e6`).** This is a good, comprehensive concept map. It is blocked
  on cross-document consistency and an incomplete `SessionDirectory.join` sequence. That is
  documentation only and does not block production start if M1-A1 implements ENet only.
- **ui-mockups (`5852d0c`).** 17 SVG/PNG screens. They include a "join-steam" screen even
  though Steam is deferred (`11-join-steam.svg`), so the owner should not read it as M1
  scope. `04-foot-art-context.png` is 1.1 MB and `09-main-menu.png` is 0.7 MB, which is
  acceptable.

### Style, contract and validation issues found

1. **The mandated check is red on main.** `python tools/script_checks.py --style-only` on
   `4fa669a` exits 1: `76 files checked, 3 warnings found … exceeding --max-warnings 0`
   (`tests/fixtures/s07_driver/{fixture,guards,run}.gd`). Lanes are told these are "accepted",
   but the tool reports failure. That makes CI impossible and forces every lane to say
   "exited 1 only because…". Fix the warnings or add a reviewed baseline.
2. **The unit-test command misses tests.** `python -m unittest discover -s tools -p "test_*.py"`
   runs **14** tests and silently skips `tools/s04/test_runner.py` (2 tests),
   `tools/s07_comparator/test_offline.py` (3) and `tools/s07_driver/test_offline.py` (2).
   The subdirectories are not packages. `tools/s05_vsync_image/test_offline.py` and
   `tools/s08/lifecycle_cadence_test.py` report "NO TESTS RAN" when invoked as modules.
   S05-NOCAP changed `test_offline.py` yet claimed validation through the 14-test command.
   The auditor ran the comparator test separately and it passes, so no defect resulted.
   The process gap remains.
3. **`mise` tasks use `python3`** (`mise.toml` `gdstyle:check` and `gdscript:check`). That
   name is not the Windows interpreter the common brief mandates. The comment says
   "used by CI", but there is no CI (`.github/` is absent).
4. **No `run/main_scene` and no `export_presets.cfg`.** `mise run play` cannot run a game.
   Every export so far used scratch presets generated by tools.
5. **GodotSteam remains an enabled editor plugin and GDExtension** in an ENet-only M1.
   Windows imports leave untracked `addons/godotsteam/win32/~libgodotsteam.windows.template_debug.x86_32.dll`
   artifacts. These are already present in the `s09-traffic-ai` and `s14-audio` worktrees
   and are not gitignored, which breaks "leave worktree clean" and clean-input checks.
6. **MCP runtime autoload.** It correctly self-disables in export templates
   (`addons/godot_mcp_toolkit/runtime/mcp_runtime_server.gd:94-108`). However, every
   editor-binary game run starts a WebSocket listener on 6570, and that is how all test
   runners launch. Concurrent lanes can collide unless a runner strips the autoload, as
   S07-ENV and S08 do but `script_checks.py` does not.
7. **Art reexport on Windows is unproven.** The S01 byte-identical reexport was established
   with Linux Blender 5.2.2 (`docs/spikes/s01.md:42`). Blender is not pinned by mise. S13
   will author with the Windows Blender 5.2 install, whose patch level is unrecorded.

## 2. Plan to P0-GATE

The current plan has three layers:

- Remaining wave-2 lanes: S02 controls, S04 drive scene, then foot and car prediction (not
  launched), S03-S fix, and UI mockup iteration.
- Wave 3: S09–S16, launched in parallel.
- Non-blocking follow-ups: S07 guidance, Linux S08, and P0-PROFILES.

Wave-3 briefs are well shaped. Each requires research, options, a prototype, measurement
with contention labelling, and a reproduction command. Weak points:

- **Per-spike budget shares never add up.** S09 proposes ≤1.5 ms and S10 ≤1.0 ms. S11
  (encode), S12 (rewind), S05 (chains), Jolt physics for 32 CharacterBody cars plus 68
  characters, and host-side prediction service will each propose their own. No task
  measures them **together** in one host tick against p95 ≤ 4 ms / p99 ≤ 8 ms. M1-D3 is
  the first place that would catch an over-subscription, which is too late.
- **Timings are contended upper bounds.** Up to about 15 Godot processes ran concurrently
  on one laptop. The briefs correctly require labels, and a "quiet re-measurement pass" is
  promised but has no TODO or owner.
- **Prediction is outside the gate.** See P0-GATE dependency narrowing above.
- **Foot↔car transitions belong to no spike.** S04 explicitly deferred the seat system to
  M1-B1 (`docs/spikes/s04.md:76-78`). S12 covers firing only. With prediction required on
  both bodies, the transition is the riskiest unowned interaction.
- **The Linux M1 target has no passing graphical evidence.** The Linux drawability attempt
  failed: wrong window size (2112×1320) and no native focus (`docs/spikes/s02-drawability.md`).
  So did the Linux VSync image card. Every recent drawn proof is Windows/D3D12. Linux uses
  Vulkan and stays "non-blocking follow-up", yet the design now names Linux an M1 target.

## 3. Systems confidence

Ratings mean the following:

- **High:** the risky part has been demonstrated on the pinned engine with retained evidence.
- **Medium:** partially demonstrated, or a credible plan with a running prototype.
- **Low:** design or contract only, or evidence confounded.
- **None:** nothing yet.

"Planned" names the lane expected to raise the rating.

| # | System | Confidence | Evidence | Unproven / remaining |
| --- | --- | --- | --- | --- |
| 1 | Foot controls (WASD + mouse facing) | Low → Medium when S02-controls lands | Ratified decision 3. `s02-controls` WIP has a pure `S02MotionRules.advance` (velocity + yaw only) | Not committed. Collision displacement lives in `move_and_slide`, so "pure" covers only the command→velocity step. Mouse ground-plane aim, left-click fire, physical-key feel and Alt-Tab are unproven |
| 2 | Camera (47 m, 42°, north-up) | High | Owner ratified it. S02/S06 Windows drawn captures. Cutaway removal decided | Readability with production art and many actors. Dark right-edge band noted in S03-R captures (`s03-r.md:311`) |
| 3 | Session / transport (ENet) | Medium-High | S03 two-process harness with cases `provisional_rollback`, `authority_validation_and_expiry`, `baseline_cancel_retry`, `subset_reorder_loss_recovery`, `provider_substitution_late_cleanup` and `held_window_resync` (`tests/fixtures/s03/proof.gd`). The ENet workaround is proven. S03-S abstraction draft exists | Production SessionService and menus do not exist yet. Windows latency anomaly (G1). Linux rerun |
| 4 | Admission / late join | Medium | S03 baseline/handoff. S05 settled hydration with no historical effects | In-flight hydration during an active chain ("settled hydration is not in-flight proof"). Late join at full population (S11 planned) |
| 5 | Foot prediction / reconciliation | **None** | Decision 4 requires it. S03-R explicitly ran no prediction (`s03-r.md:150`) | The whole replay/correction loop. Jolt `move_and_slide` replay of N ticks per frame. Correction smoothing. Lane not launched and not gating P0 |
| 6 | Car prediction | **None** | S04 chose a CharacterBody3D custom controller (`s04.md:172`), which is prediction-friendly | Replay against other moving cars. Lane not launched |
| 7 | Vehicles / handling | Medium | S04 body comparison. Post-fix drawn ENet runs. The drive scene for owner tuning is WIP (`s04-drive`) | Owner feel tuning. Car-car and car-world collision response with kinematic bodies (no impulses), rollover/slopes, two car silhouettes. Driver-death stopping behaviour is undecided (`design.md:120`) |
| 8 | Enter/exit seats, control transfer | **Low** | Contract matrix in `s04-contracts.md`. Only bounded seated resync was executed | Claim races, `EXIT_MOVING`, blocked-exit placement, NPC-driver handoff when stealing traffic, camera/HUD transition, and prediction handover between foot and car. No spike (G2) |
| 9 | Combat / weapons / hit registration | Low (planned S12) | Contracts in `api-contracts.md` "Weapons, damage and explosions". ShotId dedupe in S05 | Hitscan versus rewind choice, rocket projectile, reload/cooldown, anti-spam. S12 WIP with no results |
| 10 | Health / death / respawn | Low | Policy ratified (3 s, safe spawn). No fixture contains "respawn" (`git grep` returns empty) | Safe-spawn search, respawn hydration, death while driving. Planned M1-B2; S11 specifies spawn policy only |
| 11 | Explosions / chains / wrecks | Medium-High (logic), Low (presentation cost) | S05 12-car chain: 144 visits, peak 4/tick, 0.1 s delay, every effect presented. C0 comparator 20 trials | Effect cost (S15). Wreck visuals (cars hidden in the burst fixture). Wreck collision lifecycle. Production pool for events beyond 12 |
| 12 | Pedestrian AI | Low (planned S10) | S06 undirected foot graph and clearance queries | Everything behavioural. S10 WIP |
| 13 | Traffic AI | Low (planned S09) | S06 directed lane graph. Shared `S04DriveRules` | Everything behavioural. S09 WIP |
| 14 | Population / spawning / replenishment | Low (planned S11 design) | Caps defined in `design.md` | Out-of-view replenishment across four far-apart views, safe spawn, reset restoration |
| 15 | Replication / bandwidth | Low-Medium | S03 channels and subset refresh. ENet Variant RPCs at fixture scale | Full-cap codec, interpolation, worst-window bytes and join ≤ 1 MiB (S11 WIP). Current fixtures use Variant dictionaries, which will not scale |
| 16 | Match reset / leave / host loss | Low | `host_lost` handling in `tests/fixtures/s03/session.gd`. Reset fragments in S03-R/S04 `match.gd` | Full reset across every owner: players, seats, population, wrecks, shots, effects and prediction history. No integrated fixture |
| 17 | City / collision / navigation | Medium | S06 topology and 47 content checks on Windows. S07-ENV 96-block static envelope. Layout scale accepted | Production sectors (M1-C2). Traffic/foot routing at scale. Static collision only, with no dynamic-obstacle navigation. 384-block crash undiagnosed |
| 18 | Minimap / HUD / menus / settings | Low-Medium | S06 minimap (position accepted). UI mockups v1 | Minimap size/look iteration. No HUD/menu/theme scene exists. Focus/navigation. Settings persistence (S14 planned for audio) |
| 19 | Audio | None (planned S14) | — | Voice caps under uncapped explosions, listener placement, licensing. S14 WIP |
| 20 | VFX | Low (planned S15) | S05 saved explosion carrier (a Blender-linked mesh) | Particle cost and quality fallback. Note that `design.md` requires mesh VFX to be Blender-sourced |
| 21 | Characters / animation | Low (planned S13) | S01 rig prefab and reexport (Linux) | Crowd skinning cost and animation throttling. Windows Blender pipeline |
| 22 | Art pipeline | Medium | S01 source→GLB→linked import, identity checks, `tools/s01/reexport.py` | Windows reexport byte-equality. No art production throughput estimate for M1-C1 (six building families, two cars, rig, weapons, VFX) |
| 23 | Performance (desktop) | Low-Medium | S07 graphical T and S07-ENV capped runs on an RTX 4070 laptop. Draw calls flat at about 60 | No integrated host tick. No desktop frame target (see section 1). Uncapped headroom method crashes the GPU here. Contended timings |
| 24 | Performance on Deck | None (owner-deferred) | — | Everything. Renderer choice (Forward+ vs Mobile) left open |
| 25 | Input / gamepad | Keyboard/mouse Low-Medium; gamepad None (deferred) | InputMap `s02_*` actions in `project.godot` | Production action map, rebinding, Steam Input later |
| 26 | Export / release / CI | Low | S08 Windows release/debug export of a scratch-stripped project passes | Real project config (autoloads, GodotSteam GDExtension, presets). **Linux export and graphics.** Templates not pinned in mise. No CI. Red check command |
| 27 | Testing | Medium (fixtures), Low (production) | Rich per-spike proof runners with clean-input and evidence discipline | No unit-test framework choice (S16 planned). Fragmented discovery. Red style check |
| 28 | Focus / suspend / OS integration | Low | Windows focus observation inconclusive | Physical Alt-Tab. Linux focus |
| 29 | Security / abuse bounds | Medium (contract) | `api-contracts.md` limits, RPC sender identity and size/rate bounds in the S03 fixtures | Fire-rate validation (S12). Codec bounds at full population (S11) |
| 30 | Engine stability (4.8-dev7) | Low-Medium | The pin works for all spikes on Windows | Two GPU device removals uncapped. 384-block `0xC0000005`. Linux-only `tree_exited` diagnostics (upstream PR #123998). Known dev7 Deck-input bug. Staying on dev7 means engine crashes are ours to triage |

## 4. Gaps not covered by the plan plus S09–S16, and risks to starting tomorrow

### Risks to starting production tomorrow

1. **Wave 3 has no results yet** (sleep interruption). P0-GATE would review briefs, not
   evidence, unless it waits for S09–S16.
2. **Prediction is unproven, unlaunched and no longer a P0-GATE dependency.** M1-A2
   ("share rules offline/authority/permitted prediction") would discover the architecture
   while building production code.
3. **The baseline authority latency on Windows is unexplained** (109–255 ms at zero injected
   RTT). It confounds S11 smoothness, S12 hit agreement and later feel work.
4. **Integration breakage:** S02 cutaway deletion versus the S07-ENV saved scenes.
5. **Tooling is not production-ready.** The check command is red, test discovery misses
   tests, there is no main scene, no CI and no committed export presets.
6. **The Linux target has zero passing graphical/export evidence** on the current pin.
7. **No desktop frame target** remains after deferring Deck.

### Proposed additional foundation tasks

**G1 — Windows latency and pacing diagnosis (S03-L).** Explain why post-fix Windows
authority response at zero injected RTT is 109–123 ms drawn and 255 ms headless, versus
69 ms on Linux. Instrument one S03-R baseline run end to end:

- input sample time
- client send
- proxy receive and forward (the Python proxy's sleep/select granularity on Windows; the
  default timer is about 15.6 ms)
- ENet service cadence
- host physics consumption and state send
- client apply and draw

Compare with the proxy bypassed (direct loopback) and with `timeBeginPeriod(1)` or an
equivalent high-resolution timer. Compare `Engine.max_fps` and low-processor-mode settings,
and windowed versus headless. Deliver a per-stage latency budget. Fix the harness or the
fixture if the delay is an artifact. Otherwise record it as a platform constant that the
prediction and S12 designs must absorb. Also apply or reject the pending S03-R
expiry-boundary analyzer fix. This is small (about 1 day) and should finish before the
prediction lanes and S12 conclusions.

**G2 — Foot↔car transition with prediction (S04-T).** Build the smallest two-process
fixture with:

- one player, one parked car and one AI-driven car
- host-granted seat claims with two racing claimants
- `EXIT_MOVING` rejection above 0.5 m/s
- blocked-exit retention
- stealing a traffic car (NPC control released through the host)
- disconnect coasting

The local player must switch between the predicted foot body and the predicted car body
across the seat transaction. That means discarding or rebasing the replay history,
flipping camera/HUD ownership, and handling the correction when the host rejects a
predicted entry. Measure the visual discontinuity and the correction magnitude under
normal/adverse profiles. Depends on the two prediction lanes. Size M.

**G3 — Integrated host-tick composition (S17).** After S09–S12 report, run one headless
host scene at full caps:

- 64 pedestrians on S10's chosen motion
- 24 moving and 8 parked cars on S09's AI
- four scripted players firing through S12's validation
- one 12-car chain
- S11 snapshot encode for three clients

Measure per-subsystem and total physics-tick cost (median/p95/p99, quiet and contended).
Compare against p95 ≤ 4 ms / p99 ≤ 8 ms and reconcile the individual budget shares before
production fixes the architecture. Reuse the spike fixtures read-only. Size M. This is
the earliest point where cross-system over-subscription becomes visible.

**G4 — Real-project export smoke on Windows and Linux (S08-X).** Commit
`export_presets.cfg` for Windows and Linux (debug and release) using the real
`project.godot`. Add a minimal real `run/main_scene` boot scene that loads the saved S06
intersection. Decide and document the GodotSteam GDExtension exclusion for M1, and verify
the MCP autoload stays inert. Export both platforms with pinned templates, recording
template version and hashes, and add templates to mise or a documented fetch step. Launch
the Windows export with Steam not running. Run the Linux export on the Linux desktop when
available, with Vulkan, the 1280×800 window and focus as a short checklist. Size S–M. It
makes the M1-A-GATE "Steam absent, exported" requirement early and cheap.

**G5 — Validation baseline repair (P0-TOOLING).**

- Make `python tools/script_checks.py` exit 0 on main: fix the three S07 driver warnings
  with behaviour-preserving splits, or add an explicit reviewed suppression.
- Make one documented command discover **all** Python tests (add `__init__.py` or
  per-directory discovery) and fix the two zero-test modules.
- Switch mise tasks to an interpreter that works on both OSes.
- Gitignore GodotSteam `~lib*` import artifacts.
- Strip the MCP autoload in the compile mirror.

Size S. It is a prerequisite for M1-D1 CI and for honest "checks pass" reports from every
production lane.

**G6 — Stability triage on the pin (S08-C).** Bounded diagnosis of the 384-block
`0xC0000005`:

- one quiet rerun
- enable crash dumps or the Godot backtrace
- bisect block count between 96 and 384
- try with and without the cutaway script

Record whether this is an engine defect in large saved-scene instantiation. Reproduce
only if cheap. Separately, document the safe GPU measurement method: capped runs with
`RenderingServer` GPU timings in place of uncapped runs. Update the `design.md` frame-time
row's "uncapped for headroom" instruction through the owner if needed. Size S.

**G7 — Windows art reexport check (S01-W).** Run `tools/s01/reexport.py` with the Windows
Blender 5.2 install. Record its exact version and whether the GLBs are byte-identical to
the Linux-authored outputs. If they differ, pin Blender per platform or make the check
semantic. Size S. Do this before S13 and M1-C1 commit Windows-authored assets.

Items that are acceptable as M1 work (no new foundation task), each to be protected by
contract tests in the S16 plan:

- full match reset (M1-A2/B3)
- in-flight chain hydration (M1-B3)
- car-car collision response (fold into S09 if its prototype exposes it, else M1-B1)
- HUD/menu scenes (M1-A1/C4)
- art production throughput estimate (S16 should add one)

## 5. Owner questions

1. Should P0-GATE again depend on S02 controls, foot prediction and car prediction (and G1–G5)?
   The auditor recommends yes.
2. What is the M1 desktop frame target? Proposal: 60 FPS with p99 ≤ 20 ms on named
   Windows/Linux hardware, capped measurement.
3. What should a car do when its driver *dies* (not disconnects)? Coast, brake, or as S04
   proposes?
4. Remove the GodotSteam plugin/GDExtension from the M1 project, or keep it disabled and
   excluded from exports?
5. Should a quiet re-measurement pass for the contended wave-3 timings have an owner and a
   date before M1-D3?

## 6. Prioritized list

1. **P1 — Integration order:** before integrating `s02-controls`, rewrite or regenerate
   `tests/fixtures/s07_env/city_*.tscn` and `tools/s07_env/run.py:41-43` so they do not
   reference the deleted cutaway files. Alternatively, keep the cutaway files until S07-ENV
   is migrated.
2. **P1 — Restore the P0-GATE dependencies** on S02 controls and the foot/car prediction
   lanes (owner question 1). Launch the prediction lanes as soon as S02 controls integrates.
3. **P1 — G1 Windows latency diagnosis** before prediction tuning and S12 conclusions.
4. **P1 — G5 validation baseline repair:** green check command and complete test discovery.
5. **P1 — Wait for S09–S16 results.** Do not hold P0-GATE on briefs alone.
6. **P2 — G4 real-project Windows/Linux export smoke**, with a main scene and committed
   presets.
7. **P2 — G2 foot↔car transition fixture**, after the prediction lanes.
8. **P2 — G3 integrated host-tick composition**, after S09–S12.
9. **P2 — Owner decisions** on the M1 frame target and driver-death behaviour.
10. **P2 — Merge the decisions-docs fix (`2e2d3bf`) and refresh `root-handover.md`** with
    the wave-3 lanes. Add the S03-R adverse expiry failure to its requirement text.
11. **P3 — G6 stability triage and safe GPU method; G7 Windows Blender reexport check.**
12. **P3 — S03-S abstraction fix round.** Treat the `11-join-steam` mockup as post-M1.

## Commands run by the auditor

| Command | Result |
| --- | --- |
| `godot --version` (Mise pin) | `4.8.dev7.official.c971f93e7` |
| `timeout 300 python tools/script_checks.py --style-only --output C:/tmp/ft/lanes/p0-audit/style1` (at `4fa669a`) | **Failed as expected:** formatting true, style false (3 S07 driver warnings over `--max-warnings 0`) |
| `timeout 300 python -m unittest discover -s tools -p "test_*.py"` | 14 tests OK |
| `python -m unittest test_runner` / `test_offline` per subdirectory (s04, s07_comparator, s07_driver, s05_vsync_image, s08) on main `ffb7ede` | 2 / 3 / 2 OK. s05_vsync_image and s08 ran 0 tests |
| Read-only `git log`, `git diff`, `git show` and `git grep` across main and lane branches; `git status` of lane worktrees | Read-only. Running the subdirectory tests in the main checkout created fresh `__pycache__` files (ignored). The auditor deleted those, along with any `__pycache__` directories left empty |

No Godot gameplay or graphical run was made. Every timing figure above is quoted from
committed records, not re-measured.
