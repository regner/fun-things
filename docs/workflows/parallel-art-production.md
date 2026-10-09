# Parallel art and whole-city greybox commissioning

9 October 2026. Active owner-directed workflow; replaces the six-block-first and
sequential concept-stage prerequisites for the content tracks commissioned here.
This is a coordination record, not a declaration that foundation tests passed.

## Owner instructions

> I want to revise how we are approaching this. I don't want to do "the m1 six block" area. I want to get us to playable game as fast as possible, which means we need to work more in parallel.
>
> As I see it we have the following things that we need to get accomplished:
> - The player character
> - A pedestrian
> - A vehicle
> - Weapons
> - Weapon effects
> - The overall map needs to be constructed
> - The map needs to be filled with grey block buildings
> - Each district needs concept art individually for overall looks and fell
> - Each district needs its concept broken down into concrete list of assets that need to be produced
> - The assets need to be produced
> - The world needs the grey blocking updated to be replaced with the new visuals
>
> I think our workflow should be as follows:
> - Spawn an astra agent to being creating the grey block map
> - For each item in this list we spawn a sub agent that I can interact with:
>   - Player character
>   - Pedestrian
>   - Vehicle
>   - Pistol
>   - SMG
>   - Rocket launcher
> - For each item in that list we create some concept art for it and work through that until we are happy with it
> - For each item, once we have approved the concept for it, the agent then proceeds to create  the item in blender, this includes animations where needed such as player character and pedestrians, these items are done when they are in the Godot editor with their model, texture, rig, and animation as required
>
> After all of that we will return to flushing out each district.
>
> Does that sound like a good plan? Since each agent would be working on something entirely isolated each should get a dedicated workspace with worktree so they don't stomp on eachother.

The agreed response added an effects track and explicit compatibility ownership.
The owner then clarified:

> integration work will likely be done by another person. Lets keep it in mind, but not plan on doing it ourselves just yet.

Launch authorization:

> Lets get started.

## Active assignments and boundaries

Eight persistent, separately addressable Paseo workspaces, each with a dedicated
branch/worktree: whole-city greybox; player; pedestrian; vehicle; pistol; SMG;
rocket launcher; weapon effects. The owner explicitly requests Astra for the
whole-city greybox, overriding the skill's usual Sol workspace-lead policy for
that assignment. Other leads use Sol 6.1 high. No gameplay integration worker.

The greybox author starts from the current full-island road plan and exact exported
district polygons. The yellow M1 envelope is historical, not a construction limit.
Build source-linked Blender massing, roads/coast/bridge and saved Godot placement,
with appropriate provisional collision. Preserve flat terrain, larger gridded
high-rise centre, unequal districts/blocks, road hierarchy, open harbour entrance
and one bridge. No district polish, new mechanics or runtime city generation.

Each asset lead starts with a concise brief and three meaningfully different visual
concept directions, grounded in the accepted cyberpunk city and top-down camera.
The owner selects/iterates directly in that workspace. Do not start detailed
modelling before that asset's explicit concept approval. Approval of one asset
unblocks that asset, independently of every other asset.

Player owns the shared humanoid rig contract. Pedestrian reuses that contract;
concept work proceeds independently, while final rigging waits for compatibility.
Weapon leads agree grip/muzzle/holding conventions with player. Each lead owns
asset-local materials and scenes; no competing shared rig/material writers.
Effects owns visual feedback, not weapon rules or damage simulation.

Deliver committed Blender sources, explicit exports, textures/materials as required,
import/UID metadata, reusable Godot scenes, applicable rigs/clips and an asset-local
review scene. Verify appearances/animations/sockets from the actual gameplay camera,
plus source/export linkage and save/reopen. Keep missing checks explicit. Provide
handoff paths, dependencies and remaining gameplay integration for the other person.
Do not implement combined gameplay, replace the main launch scene, merge to main,
push, archive or close unrelated foundation tasks.

## Resource ownership and review

Own files only in the assigned worktree. Worktrees do not isolate a shared Godot or
Blender MCP session. Discover process/project/endpoint identity before writes; use
private worktree-bound sessions where available. Never switch another workspace's
editor. Author source-first work while an actual conflicting editor is occupied.
Follow repository source/export, authored-scene and validation requirements.

Use one proportionate clean-context independent review before a production handoff;
retain meaningful evidence and report remaining acceptance rather than inventing it.
Initial concept presentation needs visual self-review, not a completed asset audit.
Initial launch should reach a useful concept presentation (assets) or first reviewable
whole-city blockout (world); report actual blockers instead of repeating failed tool
setup. No unbounded infrastructure repair or automatic model/profile changes.

## Subsequent work and plan status

After these tracks, return to each district: approved concept, concrete asset list,
production, then incremental replacement of grey buildings. That later work has not
been launched. Overall playable-game integration belongs to another person.

The existing foundation results remain partial where documented. Content authoring
is now explicitly authorized in parallel; no six-block concept gate or old P0 ordering
should stop these assignments. Gameplay, networking, performance and full-game
acceptance are not claimed or waived. Scale/collision/animation assumptions may
need adjustment when the external integrator exercises them in the game.

Current map reference is docs/concepts/world-v1/stage-04-streets/; exact polygons are
in its district-editor/brackett-districts.json. Selected visual reference is
../concepts/world-v1/stage-01-setting/15-long-island-cyberpunk.png. Names are placeholders.
A frozen concept snapshot is distributed to each workspace before its agent starts.
Launch receipts and live ownership are recorded in parallel-art-workspaces.json.

The previous whole-plan checkpoint watermark remains 2d5457250701ebf93ef6e90f0e82ec9f384fd530.
This scoped commissioning changes content ordering; it does not advance that audit
watermark or certify the intervening foundation work. Broader gameplay backlog
reconciliation remains for the integration/production planning owner.
