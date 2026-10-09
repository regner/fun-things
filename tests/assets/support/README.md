# Asset-check support

These saved helpers are test-only stand-ins for delivered-asset scale, clearance and
line-of-sight checks. `asset_scale_clearance_probe.tscn` keeps the accepted S02 foot
capsule (0.38 m radius, 1.8 m height), moves at the accepted 5 m/s, and uses the delivered
Coral Courier prefab as its visible scale reference. `asset_line_of_sight_probe.gd`
provides only the bounded forward query consumed by the asset fixtures.

They do not own production movement, input, combat or networking. Switch these fixtures
to the production player and `ActorMotion` public API when M1-A2.1 lands; retain the
independent scale and clearance expectations during that migration.
