# S07 environment authoring and measurement

`author_city.gd` is an intentional procedural **authoring** tool. It runs only from the
command line and saves fixed scene composition; no runtime game system invokes it. Each
block instances the existing S06 west/east sector scenes and four existing S02 building
prefabs. The tool creates no mesh, collision shape, material, or gameplay topology.
Placed instance names and transforms are saved in `tests/fixtures/s07_env/city_<N>.tscn`.

The fixed parameters are: 48 m block pitch (the S06 sector's 48 m road span), existing
9 m roads and 4 m sidewalks, buildings at the four existing 16.25 m island centres,
3x2/6x4/12x8/24x16 grids for the original 6/24/96/384-block envelope, and the S02
camera at 47 m with 42 degree FOV. The bounded stability triage also supports 16x12 and
18x16 grids for 192 and 288 blocks. Building selection rotates through low/near/tall/low
to avoid an all-identical height field while preserving the same four-building density
per block.

Run one growth step only after the prior measured step is comfortably within its stop
limits:

```sh
godot --headless --path . --script tools/s07_env/author_city.gd -- --blocks 6
python tools/s07_env/run.py --output C:/tmp/ft/lanes/s07-env/city-6 --variants 6
```

Repeat with 24, 96, then 384. For the bounded stability triage, author and run 192 and
288 individually between the last passing and first failing original rows. The measurement
runner uses fresh external output and a fresh process per repeat, but one warm import cache.
It rejects dirty copied inputs,
including `project.godot` and this tool directory. Defaults are the commissioned two
repeats, 10 s warmup, 30 s measured, 1280x800, VSync disabled, and 60 FPS cap. It stops
growth after load exceeds 30 s, working set exceeds 2 GiB, measured frame p99 exceeds
20 ms, or a process/diagnostic failure. Do not run this fixture uncapped.
