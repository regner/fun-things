# SMG concept selection

9 October 2026. **Regner selected C — Wedgewire.**
The [production asset handoff](../../../assets/smg_wedgewire_a.md) records the
Blender source, imported wrapper and actual Godot camera evidence.
Open [the review gallery](index.html) or each full sheet:

| Option | Sheet | Main overhead cue | Tradeoff |
| --- | --- | --- | --- |
| A — Switchback | [01_switchback.png](01_switchback.png) | Open forked stock and broad coral receiver | Stock gap may close at game scale or disappear over the player |
| B — Roundabout | [02_roundabout.png](02_roundabout.png) | Broad rounded drum lobes around a narrow roof | Strong comic identity; broad belly may crowd support hand and torso |
| C — Wedgewire | [03_wedgewire.png](03_wedgewire.png) | Tapered shell with large coral/cyan planes | Strong forward direction; requires held-view check to avoid rifle read |

**Recommendation: C — Wedgewire.** Its short muzzle, broad tapered body and large
roof color regions offer a compact two-hand silhouette without the long cylindrical
shape of a launcher. Selection can combine a preferred shape with a revised palette.
These names are working labels, not fictional brands or final product names.

## Visual self-review

All three sheets were inspected. They offer side/three-quarter and overhead shape
studies. C also shows a plausible two-hand shoulder aim pose. B's tiny figure is
schematic; A has no holding pose. All require player-led pose checking after selection.
Small details and magazine shape are secondary: they are mostly hidden from above.

A's overhead muzzle includes a front-facing circular opening, which is inconsistent
with a horizontal -Z muzzle viewed vertically. Its stock also differs between the
side and overhead interpretations. Read the open fork as a direction to resolve in
Blender, not a dimensional drawing. B's large drum sides need careful support-hand
clearance. C's top taper and broad color regions are the most coherent across views.
The images contain unrequested slogans, tiny sight blocks and decorative backgrounds;
those are unselected generation artifacts, not modelling requirements.

These are attractive concept references, **not actual gameplay-camera captures**.
The small scale examples are generated illustrations and cannot certify dimensions
or recognition. At the centred 47 m / 42 degree vertical perspective camera, a
provisional 0.8 m horizontal length at 1.3 m height projects to approximately 18 px
in an 800 px-high image; 0.28 m width is approximately 6 px. This is an analytical
estimate using vertical FOV, not a rendered test. The actual held asset must be
checked at 1280×800, north-up, against player occlusion and dark city surfaces.

## Compatibility and next decision

- Regner selected C — Wedgewire directly in this workstream on 9 October 2026.
- Provisional length near 0.8 m is a concept target, not an approved envelope.
- Weapon origin is the firing-hand grip; source `socket_grip` and `socket_muzzle`
  remain authored in metres. Blender +Z up/+Y front converts once to Godot +Y up/-Z.
  Roots retain unit scale. Public weapon wrapper `Sockets/Muzzle` relays the source
  marker; the player's `Sockets/WeaponMount` is owned by the player lead.
- All options need firing hand at grip, support hand beneath the forward receiver,
  and shoulder contact with the stock during aim. A's support loop and B's drum
  require extra clearance review. Wedgewire's measured source contact transforms are
  now in the production handoff; fitted bone-to-grip offsets remain player-led.
  Published binding contract: shared_humanoid/1.0.0; S13 is not that rig.
- Effects confirmed this muzzle contract is sufficient; no additional SMG anchor.
  Measured aperture clearance/bounds are in the production handoff. No embedded
  flashes/shells/trails.

Wedgewire now has its own Blender source, explicit GLB, materials, saved imported
wrapper and local preview. It is a rigid visual; player holding clips remain with
the player lead. The shared rig is published; equipped acceptance still awaits
contact fitting and production clips.

Provenance and exact built-in imagegen prompts are in [prompts.json](prompts.json).
Tool availability, scoped catalogue delta and integrator responsibilities are in
[handoff.md](handoff.md). Static import, saved scene roundtrip and independent review
are recorded in the production handoff. Equipped city recognition, gameplay/network
and device acceptance remain pending.
