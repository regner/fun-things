# S02 controls — world-relative movement and mouse aim

8 October 2026. This lane applies the owner's ratified desktop-control decision to the
saved S02 technical corner and its accepted downstream fixtures. It is not a human feel,
native-focus, Deck, prediction or production acceptance result.

## Implemented contract

- W/S (or Up/Down) move along world -Z/+Z; A/D (or Left/Right) move along world
  -X/+X. The fixed north-up camera therefore matches screen directions.
- Cardinal and normalized diagonal movement use one immediate 5 m/s speed. Releasing
  movement stops velocity immediately.
- The desktop collector projects the viewport mouse ray onto the actor's horizontal
  ground plane. The resulting yaw snaps facing once per physics command. Device reads
  remain outside `S02ActorMotion`.
- Left mouse fires. Space remains an alternate fire binding and remains the S04 car
  handbrake rather than making mouse fire a car control.
- `S02MotionRules.advance` is the pure state/command rule for velocity and yaw. The
  existing `CharacterBody3D` owner applies that result and owns collision. A later
  prediction lane can replay the rule without replaying query/fire side effects.
- The building cutaway shader and owner script were removed. Building scene roots,
  linked models, collisions, world IDs and remaining saved node identities are retained.
- S03-R held intent now carries normalized `move: Vector2` plus canonical `aim_yaw`.
  S06/S07 foot routes issue world movement toward the lookahead point and face travel.

The 42 degree, 47 m, fixed north-up camera is unchanged. Held weapon silhouettes are
unchanged. Gamepad input remains deferred.

## Owner play instruction

Use the pinned engine from the repository root:

```sh
mise exec -- godot --path . res://prototypes/s02/tests/fixtures/s02/corner.tscn
```

At 1280x800, perform this route with physical controls:

1. Put the pointer above the actor and hold W through the four-metre passage. Verify the
   actor moves toward the top of the screen and faces the pointer, not the travel direction.
2. Hold W+D and verify a diagonal does not move faster than a cardinal direction. Move the
   pointer around the actor while moving, then stop moving and confirm facing still follows.
3. Move around the north-east corner, aim at the previously hidden target and left-click.
   Confirm solid building collision still blocks shots before the corner and the target can
   be hit after rounding it.
4. Back away from a wall with S while aiming elsewhere. Confirm movement remains
   screen/world-relative rather than facing-relative.
5. Compare roof/actor/target readability without any circular building cutaway. Also inspect
   the retained pistol, SMG and launcher silhouettes at normal play scale.
6. Hold a movement key and left mouse, physically Alt-Tab to a normal non-Godot window,
   release both while away, then return. Neither movement nor fire should resume until a
   fresh press.

Record movement/aim confusion, missed targets, camera-follow comfort, roof obstruction and
weapon readability. Automated outcomes do not ratify those subjective points or physical
native-focus behavior.

## Validation and evidence boundary

The lane uses direct text-file edits because the Godot editor was not running and editor
MCP tools were unavailable. A pinned headless editor import generated the new script UID;
its full-checkout plugin diagnostics are the known development-addon diagnostics, not a
clean script-validation result. Isolated runners remove those development plugins. Retained
receipts are under [`s02-controls-evidence/`](s02-controls-evidence/).

The S02 outcome now independently checks equal-speed cardinal movement, normalized
movement, facing-independent translation, snap aim, instant stop, collision, mouse ray
projection, left-click/Space fire, lifecycle cancellation, cadence and unchanged source
links. The old tank-model turn-without-strafe and turn-rate samples were replaced only by
the corresponding independent strafe, stationary snap-aim and network aim-yaw checks.
S03-R, S04, S06 and S07 receipts remain separate so a downstream regression cannot be
hidden by the standalone result.

| Check | Result |
| --- | --- |
| S02 isolated movement/input/query/resources | Pass; no failures and staged files unchanged |
| Windows automatic draw | Pass; 30 callbacks and three 1280x800 captures without cutaway |
| Native focus automation | Inconclusive because initial foreground focus was unavailable |
| S03-R baseline/normal/adverse headless | Pass; 20/20 applied physics responses in each profile |
| S03-R windowed baseline | Pass on the bounded final run, including 20/20 drawn responses |
| S04 saved body/baseline/fence/producer checks | Pass |
| S06 content and all three body routes | Pass |
| S07 driver offline checks and capped 30 s graphical smoke | Pass |
| Rebasing compatibility with S07 environment variants | Pass; 6-block two-repeat smoke |
| All-owned compilation | Pass, 78/78 scripts |
| Formatting/lint wrapper | Expected nonzero: two newly integrated S07 environment scripts are pre-existing unformatted inputs, plus the three accepted S07-driver lint warnings; changed S02/control scripts add no finding |
| Tool unit tests | Pass, 17 tests |

The first S03-R headless/windowed attempts around the workstation standby/warm-up boundary
missed bounded response samples; their exact failed receipts are retained separately from
the clean final runs rather than being relabelled as passes. No accepted criterion was
weakened to obtain the final results.
