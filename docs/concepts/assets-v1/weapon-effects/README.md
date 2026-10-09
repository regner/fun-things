# Weapon effects — concept selection

Concept images for completed production assets were removed during production cleanup; retrieve them from commit `80d0f24`.

9 October 2026. Owned by the weapon effects lead; art selection belongs to Regner.
Base: `c030d66d7d0a9db19c0c2aebf1aa2b83eded6275`. Concept status:
**A selected by Regner, 9 October 2026; production in progress**.

Owner selection: “I really like both A and B. Lets start with A and we can review again later.”
Keep B as an alternate for later review; this selection authorizes A source/scene production.

Original generated visual references for muzzle flash, surface hit, rocket trail and
explosion. This checkpoint contains no production model, texture atlas, shader,
particle scene, collision, gameplay, networking or performance acceptance.
The removed full-resolution gallery remains available at commit `80d0f24`.

| Option | Visual language | Self-review / recommendation |
| --- | --- | --- |
| A — Compact combustion | Ivory/amber directional flash, small spark impact, short porous warm trail, coral/orange separated fire lobes and broken slate smoke | Recommended. Closest to the accepted fire language; warm action separates from cyan/magenta street lighting. Keep impact distinctly smaller than explosion. |
| B — Neon ion | Cyan-white forks and cores, coral/violet petals, broken arc impacts, discrete luminous trail knots | Strong sci-fi alternative; cyan/magenta effects compete with signs and imply energized weapons. This is a proposed style change requiring Regner's selection. |
| C — Arcade pop | Rounded butter-yellow pops, orange droplets, scalloped fire petals, tiny pink accents | Strongest irreverent arcade tone; oversized petals could read as flowers. Tighten the centre and shorten the trail if chosen. |

## Brief and camera

Follow [parallel commissioning](../../../workflows/parallel-art-production.md),
[asset rules](../../../assets.md), [scene contract](../../../scene-structure.md)
and the viewed [city reference](../../world-v1/stage-01-setting/15-long-island-cyberpunk.png).
Use smooth stylized 3D, ordinary city architecture under darker vibrant cyberpunk
lighting, chunky silhouettes, warm/cool separation and restrained bloom.

Target camera: vertical downward perspective, north-up, height 47 m, vertical FOV
42 degrees, viewport 1280×800. Nominal ground span is approximately 58×36 m at
ground level. All sheets contain overhead sequences and context studies; the
supplementary comparison keeps approximately matching
street placement across the directions. **These are imagegen illustrations, not
actual camera renders or measured scale evidence.** The generated insets and
supplementary panel aspect ratios differ from 16:10, and some visible facades
exaggerate perspective. Printed camera/scale claims in the pictures are prompt
intent, not verification. Actual saved-camera checks await selected source-backed
art and the private Godot preview. No crop/resize is presented as camera validation.

Self-review: all four families are present and sequences communicate ignition,
peak and breakup. Warm cores remain distinct on navy asphalt. A has the clearest
fit with existing ivory/amber → coral/orange → slate language. Some `CLEAR`
frames still contain too much smoke/chips; final authoring must actually clear,
keep smoke porous and prevent hit impacts from resembling small explosions.
The comparison trail is longer than desired: shorten it during the selected
blockout. No numerical timing, brightness, dimensions or emitter budget is
accepted by this concept checkpoint. Generated neutral guns, rockets, people,
cars and buildings are context only; their designs belong to the other leads.

## Ownership and provisional attachment agreement

- Pistol/SMG supply Blender `socket_muzzle` and wrapper `Sockets/Muzzle`, local
  -Z forward/+Y up; weapon pivot at grip, metres/unit roots. Effects attach at
  the presentation muzzle origin, extending forward along -Z. No extra anchor
  requested. Measured aperture/offset and local envelope await their selections.
- Rocket lead owns the visible rocket and launcher. Requested source
  `socket_trail` at exhaust centre, same -Z/+Y orientation, optionally relayed to
  wrapper `Sockets/Trail`. Exhaust extends behind along +Z. This name/path remains
  a proposal until the rocket lead confirms; exact transform follows approval.
- Trail puffs should remain in world space and fade after emission stops. Actual
  rocket speed/maximum residual travel must be supplied by the integrator before
  trail bounds/culling can be accepted. Effects never choose trajectory or damage.
- Player owns the shared rig and holding clips. This track needs no additional
  hand/shoulder anchor, does not copy S13's technical rest rig and does not author
  shared rig files. Physics muzzle queries stay with the integrator.

Inspected consumers: S05 saved source-linked explosion carrier and current
S05 presentation contract; S15 imported mesh particle scenes and technical
source/output handoff. Existing `prototypes/s15/art/models/effects/s15_*` and
`prototypes/s15/tests/fixtures/s15/` remain untouched. S15 trail direction is a fixture convention,
not a production projectile axis to copy. Follow its source linkage pattern,
not its unaccepted count/tier proposal or runtime mesh-binding workaround by default.
Every accepted explosion must receive a visible effect. Do not add pool exhaustion
drops, an on-screen cap or an automatic quality policy through this art track.
Any future tier choice remains owner/integrator policy and separate acceptance.

## Provenance and next handoff

Concept direction/prompt authorship: weapon effects lead (Codex), commissioned
by Regner. Tool: built-in `image_gen.imagegen`; original generated concepts,
no external asset library, brand, font or stock texture used. The local city
reference was viewed and described in text, not passed as a tool image input.
[prompts.json](prompts.json) preserves every successful prompt and provenance;
[files.json](files.json) records outputs, dimensions and SHA256. Outputs were
copied into this worktree, retaining the generated originals. These references
may be iterated for project concept work; they do not establish Blender provenance
or constitute a third-party license. No generated raster is installed as runtime art.

After Regner selects/iterates: author distinct `weapon_effects_*` family sources
under `art/source/models/effects/weapon_effects/` (committed Blender collections and
explicit GLBs under `art/models/effects/weapon_effects/`), source textures where needed,
local runtime textures/materials, and saved reusable `scenes/effects/weapon_effects_*`
scenes. Non-mesh flash/smoke may use documented source textures/shaders; all visible
mesh lobes/sparks/debris need Blender provenance. Decoration has no collision.
An asset-local saved preview will exercise play/stop/restart/clear and measured
camera/bounds, with capped bounded playback, import/UID checks and editor save/reopen.
No rig clips are needed for particles unless the chosen effect calls for an
authored mesh animation. Require one clean-context independent production review
before declaring finished assets. Initial concepts need self-review only.

Tools discovered: `/usr/bin/blender` reports 5.2.2 LTS;
`/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot`
reports `4.8.dev7.official.c971f93e7`. Blender MCP reports connection unavailable;
no Blender session was mutated. No private editor/process has been started during
concept work. Recheck bound project/PID/endpoint before editor writes; avoid
greybox PID49308, ports16650–16654 and `/tmp/brackett-greybox` XDG state.
Godot MCP read-only scene-tree probe returned `CONNECT_FAILED`,
`ECONNREFUSED 127.0.0.1:6550`; no bound project identity could be obtained and
no editor was switched or written. This is not a blocker for concept selection.

Scoped reconciliation delta for integrator (shared files deliberately untouched):
add pending catalogue family `weapon_effects` linking this record; keep production
effects/S15 readability, overdraw, device/performance and every-explosion acceptance
open. No shared TODO completion/removal is claimed by concept delivery. Gameplay
event plumbing, duplicate suppression, collision, damage/chains, network acceptance,
overflow policy and main-scene/world integration belong to the external integrator.

## Approved A implementation

Regner selected A on 9 October 2026; B stays available. The first saved Godot
revision now has an [actual-camera sequence](production-a/index.html) and
[scoped asset handoff](../../../assets/weapon_effects_a.md). Concept-only caveats
above describe the generated sheets; production checks/limits are in that handoff.
