# M1-B1.2 validation evidence

All commands used the Mise-pinned Godot `4.8.dev7.official.c971f93e7`. Generated logs remain outside
the checkout. [`validation.json`](validation.json) records the concise machine-readable outcomes.

- `python tools/production_checks.py --output
  C:/tmp/ft/lanes/m1-b12/production-checks-final-rpc`: every canonical layer passed. Owned-script
  format, zero-warning style and explicit compilation passed; Python passed 22/22; GUT passed
  **214/214 tests** with **8,894 assertions**; the isolated diagnostic failure was observed as required.
- Focused vehicle interaction and motion GUT passed **29/29 tests** with **1,416 assertions**. Focused
  replication GUT passed **63/63 tests** with **4,161 assertions**. Focused LocalRig/prediction GUT
  passed **12/12 tests** with **212 assertions**.
- `python tools/vehicles/run_vehicle_replication.py`: separately bounded host/client ENet processes
  entered through `MatchReplication.request_vehicle_entry()` and completed every authoritative and
  predicted straight, turn, brake, reverse and handbrake outcome, plus authoritative wall and moving-
  car contacts, for direct, normal and adverse profiles. All exited zero and converged at command
  acknowledgement 460 with empty prediction history.
- Direct: **368** client movement receipts, **183** reconciliations, raw correction p95
  **0.017155 m**.
- Normal (75 ms one-way, ±30 ms jitter, 2% loss): **350** receipts, **172** reconciliations, raw
  correction p95 **0.685502 m**.
- Adverse (125 ms one-way, ±50 ms jitter, 5% loss): **324** receipts, **159** reconciliations, raw
  correction p95 **0.996232 m**.

The unchanged raw-correction target is 0.5 m. Direct meets it; normal and adverse do not in these fresh
production-action runs. Every profile still confirms entry, completes all transaction/movement outcomes,
and converges with last correction zero. This is the previously documented B1.1 prediction sensitivity
under active delayed/lost phase changes, not a seat-transaction failure; no threshold or measurement
was weakened. No windowed visual or feel review is claimed.
