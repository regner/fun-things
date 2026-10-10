# vehicle_wrecks — Wreck states for the three delivered cars

10 October 2026 · **Commissioned by the owner (decision 64).** Consumer: M1-B3.1
(explosions, wrecks and chains), which swaps a destroyed car's live body for its wreck.

## Members

- `vehicle_wrecks.01` — Sable sedan wreck (from [car_sable_a](car_sable_a.md)).
- `vehicle_wrecks.02` — Crate wreck (from [car_crate_a](car_crate_a.md)).
- `vehicle_wrecks.03` — Latch wreck (from [car_latch_a](car_latch_a.md)).

## Contract

- Derive each wreck from its accepted car source (`art/source/models/vehicles/car_*_a/*.blend`):
  copy the car into the wreck's own source file and author the damage there. The live car's
  source and GLB stay unchanged.
- Keep the live car's origin, ground datum, axes and overall footprint, so B3.1 can swap the
  body in place without a visible jump. A slightly lower stance (deflated tyres, sagging body)
  is fine. Document any envelope change.
- Visual direction (Petrol & Coral, smooth stylised): charred, darkened body with readable
  remnants of the original paint; broad dents and a buckled bonnet and boot; shattered or missing
  glass; one or two missing or hanging panels; scorched wheels. No fire, smoke or embers (VFX own
  those), no noisy grime, no gore or occupants, no interior.
- The wreck must read as that same car model from the 47 m / 42° gameplay camera.
- Static prop: one simple collision envelope (box or ≤2 convex pieces) matching the wreck body,
  derived from dimensions rather than the render mesh. No wheels, physics or doors.
- Prefab: `scenes/prefabs/city_cars/<nid>.tscn` with `Visuals/Model` as an identity-linked GLB
  plus separate collision. Runtime instantiates this saved scene; B3.1 owns lifecycle and
  retention.
- Triangle budget at or below the live car's.

Review criterion: **Instantly recognisable as the destroyed version of its car, without noise.**
