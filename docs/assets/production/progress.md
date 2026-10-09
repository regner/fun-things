# Production progress

Dispatch is **paused at the user's request**, after the 19 already-started assets
completed independent source/export and linked-prefab review with bounded engine
fixtures. All 19 source specialists, the integrator and three reviewers are idle.
The remaining **204 of 223 register IDs are queued and unstarted**. All 12 trailing
readiness tracks are preserved. Resume requires an explicit user instruction.

**9 October 2026 — cleaned-project reconciliation.** Runnable review fixtures moved from
`tests/fixtures/asset_production/` to `tests/assets/asset_production/`, preserving their
saved scene and script UIDs. Their archived S02 dependencies were replaced by test-only
accepted-envelope clearance and line-of-sight probes under `tests/assets/support/`; the
Coral Courier is the probe's visible scale reference, and the Batch 01 mounting facade now
uses the delivered Brackett greybox shop prefab. Current headless observations preserve the
retained movement, clearance and aim outcomes. These stand-ins must switch to the production
player/`ActorMotion` API when M1-A2.1 lands. The editor was unavailable, so this reconciliation
used direct text edits followed by pinned headless import and fixture loading. The paused
asset-production workspace must rebase onto this reconciliation commit before dispatch resumes.

| Batch | Assets | Reviewed candidate | Final disposition |
| --- | --- | --- | --- |
| 01 | Three lights, wall sign panel, two planters | `c4067ff3abe1384301471d9a64e94e84201235e2` | [Source/prefab review accepted; G1 closed](../../reviews/asset-production/batch_01/final/report.md) |
| 02 | Shrub, tree crowns, grass/weed variants, roof vent/enclosure, canopy | `10ddb64d16e6cb2f137923a31d3ca14991468f7d` | [Bounded source/prefab review accepted; C1 closed](../../reviews/asset-production/batch_02/final/report.md) |
| 03 | Fascia, surround, window bay, door leaves, upper windows, blade sign, inline shell | `dbcbd8e60dfe7da1bd15a77d87cb908d446b11c3` | [Source/engine review](../../reviews/asset-production/batch_03/final/report.md), [F3 retention closed](../../reviews/asset-production/batch_03/retention-final/report.md); F1/F2 closed |

These are 19 asset records with **26 linked variant prefabs**. Full game-ready
acceptance remains pending: world integration owns routes/placements and compatible
upper-window openings; S02/S04 own final camera/readability; multiplayer owners own
actual transport/admission/prediction; device/build owners own packaged and Deck
behavior; performance owners own sustained GPU/frame-pacing/load measurements.
Signage artwork remains its separate owner's handoff. The upper-window group was
checked against a source-linked technical wall; this one-storey shell has no upper
opening. Recorded fixture checks do not establish a completed world attachment.

All source specialists used verified Astra medium. Integration used Sol medium,
independent review Sol high. Sources, explicit exports, raw diagnostics, fixes and
complete review packs are retained. The rectangular planter's missing producer
manifest is documented as an integrator retention manifest, preserving provenance.

Private editor PID277464 is saved in Inspector with no unsaved scenes and runtime
stopped; its lease is released. Runtime port22651 is closed. Live editor stdout and
stderr remain outside immutable packs under `/tmp/asset-register-production-editor/f3/`.
On resume verify PID/project/pin/ports/context through the guarded private client
and current launch state before acquiring the lease. Preserve the 46 untracked
review-only importer sidecars; they are outside the immutable producer/review packs.

The production handoff `f891bf9a9b8286f09a94ff62b4b09204a8933c6c` was fast-forwarded
into local main at the user's request, preserving the exact original input files.
[Local integration receipt](local-integration.json) records old main, adopted input
snapshot and delivered revision. No push, archival or TODO closure; production
dispatch remains paused. The production worktree is preserved for safe resume.
The queue records exact IDs, specialists, source/engine/review revisions and remaining
gates. [Pause retention receipt](pause-readback.json) records complete final-review
expected-set/hash readback and the idle-agent inventory.

The latest whole-plan watermark remains `2d5457250701ebf93ef6e90f0e82ec9f384fd530`.
This pause reconciles the affected tracker only: three bounded asset batches are
now integrated into local main, with no new product/gate decision.
Retention repairs and metadata do not count as additional substantive workstreams;
no new whole-plan audit is dispatched while paused. Reassess the existing 6–8
workstream cadence and unchanged profile followups on an authorized resume.
