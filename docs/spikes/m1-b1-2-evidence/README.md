# M1-B1.2 validation evidence

All commands used the Mise-pinned Godot `4.8.dev7.official.c971f93e7`. Generated logs remain outside
the checkout. [`validation.json`](validation.json) records the concise machine-readable outcomes.

- `python tools/production_checks.py --output
  C:/tmp/ft/lanes/m1-b12/production-checks-r2-final`: every canonical layer passed. Saved-identity,
  owned-script format, zero-warning style and explicit compilation passed; Python passed **34/34**;
  GUT passed **247/247 tests** with **9,261 assertions**; the isolated diagnostic failure was observed
  as required.
- `python tools/vehicles/run_vehicle_replication.py --output
  C:/tmp/ft/lanes/m1-b12/enet-r2-final5`: every separately bounded host/client ENet process exited
  zero. Each profile first resolved a same-tick claim to the lower participant, rejected the remote
  ENTER without changing its binding, released the winning seat on driver death, then entered, drove
  all five command phases, rejected a reservation-blocked EXIT atomically, and committed the clear
  retry. Direct, normal and adverse converged at acknowledgement 460 with empty prediction history.
  Host evidence also covered authored-wall and moving-car contact.
- Direct: **505** client movement receipts, **155** reconciliations, raw correction p95
  **0.017604 m**.
- Normal (75 ms one-way, ±30 ms jitter, 2% loss): **507** receipts, **153** reconciliations, raw
  correction p95 **0.729657 m**.
- Adverse (125 ms one-way, ±50 ms jitter, 5% loss): **443** receipts, **134** reconciliations, raw
  correction p95 **0.806491 m**.
- `python tools/m1_a_gate/run_exported_acceptance.py --executable
  C:/tmp/ft/exports/b12-r2/ft-lanes.exe --output
  C:/tmp/ft/exports/b12-r2-acceptance-final`: the complete exported Windows matrix passed, including
  gameplay death/respawn/reset, direct and delayed sustained input, incompatible protocol, admission
  timeout, host loss, and the new vehicle scenario. Both host and client produced one physical key
  press, **600** saved-collector drive samples over **10.0 s**, more than **128 m** authoritative
  displacement, sub-0.5 m/s clear exits, zero stale-foot drift, and more than **12.6 m** resumed walk.
  Host entry confirmation was **284 ms**; client confirmation was **318 ms**.
- The exported mutation case disabled the client `DriveInput` collector. It failed with
  `VEHICLE_DRIVE_SEAM_NOT_OBSERVED`, zero displacement and a nonzero client exit, which the runner
  accepted only as the required expected failure.

The unchanged raw-correction target is 0.5 m. Direct meets it; normal and adverse do not in this fresh
production-action transaction run. Every profile still confirms both transaction outcomes, completes
all movement outcomes and converges with last correction zero. No threshold or measurement was
weakened. No windowed visual or vehicle-feel review is claimed.
