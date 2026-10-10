# M1-B1.2 validation evidence

All commands used the Mise-pinned Godot `4.8.dev7.official.c971f93e7`. Generated logs remain outside
the checkout. [`validation.json`](validation.json) records the concise machine-readable outcomes.

- `mise exec -- python tools/production_checks.py --output
  C:/tmp/ft/lanes/m1-b12/production-checks-r3-final4`: every canonical layer passed. Saved-identity,
  owned-script format, zero-warning style and explicit compilation passed; Python passed **62/62**;
  GUT passed **250/250 tests** with **9,280 assertions**; the isolated diagnostic failure was observed
  as required.
- `mise exec -- python tools/vehicles/run_vehicle_replication.py --output
  C:/tmp/ft/lanes/m1-b12/enet-r3-final2`: every separately bounded host/client ENet process exited
  zero. Each profile first resolved a same-tick claim to the lower participant, rejected the remote
  ENTER without changing its binding, released the winning seat on driver death, then entered, drove
  all five command phases, rejected a reservation-blocked EXIT atomically, and committed the clear
  retry. Direct, normal and adverse converged at acknowledgement 460 with empty prediction history.
  Host evidence also covered authored-wall and moving-car contact.
- Every profile additionally ran two fresh-process lifecycle races. Reset committed while remote ENTER
  was pending and left match revision 2 with zero pending actions, no old binding and no applied old
  action. A seated client then accelerated above 23 m/s and terminated; the host cleared its driver and
  observed the surviving car slow from about 24.0 m/s to about 10.3 m/s under neutral coast.
- Direct: **504** client movement receipts, **155** reconciliations, raw correction p95
  **0.018688 m**.
- Normal (75 ms one-way, ±30 ms jitter, 2% loss): **507** receipts, **152** reconciliations, raw
  correction p95 **0.407036 m**.
- Adverse (125 ms one-way, ±50 ms jitter, 5% loss): **456** receipts, **142** reconciliations, raw
  correction p95 **0.791865 m**.
- `python tools/m1_a_gate/run_exported_acceptance.py --executable
  C:/tmp/ft/exports/b12-r3/ft-lanes.exe --output
  C:/tmp/ft/exports/b12-r3-acceptance-final`: the complete exported Windows matrix passed, including
  gameplay death/respawn/reset, direct and delayed sustained input, incompatible protocol, admission
  timeout, host loss, and the vehicle scenario. Both host and client walked into range through saved
  foot input, used physical E viewport presses for entry and exit, produced **600** saved-collector
  drive samples over **10.0 s**, exceeded **128 m** authoritative displacement, exited below 0.5 m/s,
  had zero stale-foot drift, and resumed walking more than **12.7 m**. Host entry confirmation was
  **284 ms**; client confirmation was **302 ms**.
- The exported E-seam mutation disabled LocalRig interaction collection. It failed with
  `VEHICLE_INTERACTION_SEAM_NOT_OBSERVED`, exactly one attempted E press and a nonzero client exit,
  which the runner accepted only as the required expected failure.
- The exported drive mutation disabled the client `DriveInput` collector. It failed with
  `VEHICLE_DRIVE_SEAM_NOT_OBSERVED`, zero displacement and a nonzero client exit, which the runner
  accepted only as the required expected failure.

The unchanged raw-correction target is 0.5 m. Direct and normal meet it in this final run; adverse does
not. Every profile still confirms both transaction outcomes, completes all movement and lifecycle
outcomes, and converges with last correction zero. No threshold or measurement was weakened. No
windowed visual or vehicle-feel review is claimed.
