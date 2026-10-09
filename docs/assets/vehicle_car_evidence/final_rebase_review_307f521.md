# Final vehicle rebase disposition

9 October 2026. Same independent Codex/Sol reviewer; review only.
Candidate/observed HEAD: `307f5216d6b01b3fe5ae808d21651475392d29d5`.
New base: `9182f64c01631f405fa68d311076d50e4ac0043c`.
Pre-rebase complete delivery: `921af54` (door correction `c494a89`).
Prior audit: `69219f0655f0233a2a8de6d738029a3b7fcdef2a` against
`9ff045f9c9ed14075a855bc9e0dc0266fc6936a8`; that audit is retained, not rerun in full.

**Verdict: accepted for the owner-authorized local main fast-forward.** No
source/GLB/scene-linkage or rebase-payload blocker found. One nonblocking evidence
defect below limits the claimed editor-refresh proof. This review neither performs
the fast-forward nor authorizes a remote push.

## Finding

**P2 — stale post-refresh inspection evidence; editor synchronization remains
unproven for the revised mesh.**
`latch-door-refresh.jsonl:14`, final `inspect_asset` result, reports both
`DoorPanelFront*` longitudinal spans as **1.932 m** and includes **no QuarterPanel
or QuarterGlass nodes**. Those are the old whole-side doors. Current source and GLB
have 1.245 m moving panels and four fixed quarter nodes. Thus the successful
close/refresh/open/save calls in lines 1–13 record operations, but the final mesh
inspection cannot validate the revised import. The stronger synchronization claim
in `latch_door_revision.md` must not be inferred from this receipt.

Minimal correction, vehicle evidence owner: label that inspection as stale and
replace/supplement it in a later authorized private editor session with an
inspection that lists all four fixed quarter nodes and the 1.245 m front panels
after reload/reopen. Preserve scene IDs and confirm saved hashes again. No editor
operation or evidence fix was performed by this reviewer. This does not block the
Git fast-forward: independently read source/export and committed fresh-looking
drawn captures establish the corrected deliverable; live-editor synchronization
acceptance is separately **pending**.

## Checks actually performed

- Clean entry status and exact HEAD verified; read the revision, source/hash,
  refresh/parent receipts, correction recipe, owner-approval handoff and prior
  review. Ran candidate/base `git diff --check`: exit 0. New base is an ancestor;
  `git rev-list --merges BASE..CANDIDATE` is empty.
- Inline read-only Python compared recursive `git ls-tree` entries: **all 111
  changed vehicle-owned paths have identical blobs and modes to `921af54`**.
  Paths are confined to car sources/exports/scenes/tools and vehicle documentation/
  concepts. All other new-base entries are preserved. No rebase payload drift.
- Independently SHA-256 checked all four source/export pairs against current
  `reexport.json` and six scenes against `roundtrip.json`: pass. Revised Latch
  source hash `15f1acc54486c57e71de40899adc0d25efb1d4c60029d3f922f49479ee931502`;
  GLB hash `264cd46c027cce85738f3818ee426aa75346c1024d958351ee67b4c90e7c71f7`.
  Byte-identical re-export remains a producer assertion, not a reviewer re-export.
- Inline Python/NumPy parsed revised Latch GLB headers, hierarchy, position/index
  buffers and transformed vertices; exit 0. **10,480 triangles**, closed bounds
  approximately X±0.9465, Y0–1.5400, Z-1.7200–1.7120 m. Both moving panels span
  Z-0.6310–0.6140; fixed panels span Z0.6260–1.3010. Fixed panel/glass nodes parent
  directly to `car_latch_a`; panel/window/handle/mirror descendants remain beneath
  their front hinges. Pivot/socket node local transforms match prior `69219f0`.
- Latch wrapper, preview and GLB import sidecar are byte-identical to the earlier
  audited revision, retaining socket mapping, resource/node IDs and scene paths.
  Every saved RESET/demo target resolves against the revised GLB. Quarter nodes
  are outside the animated hinge branches; animation still changes only visuals.
- Private read-only source probe: `ALSOFT_DRIVERS=null /usr/bin/blender --background
  -noaudio --factory-startup --python-expr ...`; exit 0, Blender5.2.2 LTS
  `d13f752e3b9c`. Read only the saved Latch `.blend`, without save/export/authoring.
  Verified revision1, exact 62-member export collection, 10,480 triangles and
  source split parents/bounds matching the GLB's axis conversion.
- Viewed approved `01_latch_compact.png` and all three current Latch PNG captures
  via `view_image`. Closed image places door seam/handle forward of the rear wheel;
  open image leaves rear-quarter body/glazing in place while the front door swings.
  This addresses the owner's specific comparison request. Read capture JSON/logs:
  1280×800 Compatibility, pinned Godot4.8-dev7/GTX1070, successful save/root checks,
  open left/right hinges -50°/+50°, narrowed reported open width3.625518 m.
  No new runtime/script error appeared in the inspected open-capture stdout.
  These are inspected committed captures, not independently rerendered results.

## Approval and remaining boundaries

Owner requested: “The orange car needs more work. The door shouldn't go all the way
to the back of the car. Compare to the concept image.” After the correction:
“Approved. We should be done with you now. Merge this into local main, rebase
fastforward.” **Current vehicle delivery is owner-approved.** The earlier audit's
pending owner approval is historical and does not override that instruction.

Further rounded-form/concept fidelity and upper door-edge shading observations
remain recorded follow-up work, not a new approval prerequisite. Full-loop and
intermediate-clearance playback, per-door production APIs, driver fit, collision/
handling/routes/exits, integration/network/lifecycle/wreck states, Forward+ parity,
LOD appearance and performance/device acceptance remain unperformed/pending.
Owner delivery approval does not manufacture those results. Bus/truck remain
concept-only and outside production review. No full earlier audit, lint rerun,
live editor/MCP access, captures, services, fixes, commits or merge were performed.
Only this disposition file was written.
