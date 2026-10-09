# S09 traffic evidence

Accepted bounded run: `C:\tmp\ft\lanes\s09-traffic-ai\accepted-06`, copied here without
the staged project or private user directory. Every committed file is below 5 MiB.

- `summary.json`: exact commands, engine version, source SHA-256 values, per-case host
  snapshots, aggregate full-sample percentiles and outcome totals.
- `cases/population-*-seed-*.json`: all 36,000 per-tick timings, compact terminal states,
  collision diagnostics, recovery samples, checks and engine identity for one seed.
- Matching `.log` and `.engine.log`: process output and engine log for each case.
- `import.log` and `import.engine.log`: isolated addon-free project import.

The timing samples are contended upper bounds. The case receipts record 4–9 total Godot
processes including the measurement and 1–94% sampled CPU load; consult `summary.json`
rather than inferring workstation load from an instantaneous Windows CPU sample.
The runner counted processes and sampled CPU immediately before each case. It did not kill
or pause concurrent workers.
