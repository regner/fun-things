# Initial Edge attempt — retained failure

8 October 2026. Scratch output: `C:/tmp/ft/lanes/ui-mockups/render-01`.

The first authoring version rendered 01 and 02, then Python's `subprocess.run` raised
`TimeoutExpired` waiting **40 seconds** for the third Edge command. A complete
[03-foot-wide.png](03-foot-wide.png) existed despite the process-wait failure. It is an
**initial version**, not the final screenshot; the bottom control caption was subsequently
moved above the interaction panel after visual review.

The command that timed out, copied from the observed Python exception:

```text
C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe
  --headless --disable-gpu --no-first-run --disable-extensions
  --disable-background-networking --hide-scrollbars --force-device-scale-factor=1
  --user-data-dir=C:\tmp\ft\lanes\ui-mockups\render-01\edge-user
  --screenshot=C:\tmp\ft\lanes\ui-mockups\render-01\03-foot-wide.png
  --window-size=1280,800
  file:///C:/GameDev/git/ft-lanes/ui-mockups/docs/concepts/ui-v1/03-foot-wide.svg
```

This attempt used one scratch profile for sequential screenshots. The helper wrote logs
only after `subprocess.run` returned, so **no third log or completed result manifest was
written**. Do not infer a clean third browser log from that absence. The first two raw
logs are retained as [01-foot-compact.log](01-foot-compact.log) and
[02-foot-balanced.log](02-foot-balanced.log). The second includes a Chromium background
sync `ERR_ABORTED` diagnostic.

Python's timeout handler killed/waited its own direct child. A read-only process query
for the unique scratch-profile path afterwards found no surviving matching Edge process;
no unrelated process was killed. The query's own shell/PowerShell commands matched their
search string and were left alone.

The next attempt isolated each screen's profile and disabled browser sync, retained logs
as the child ran, recorded each PID/exit, and used a bounded 45-second wait. Render-02
completed all 18. After a car-marker-orientation correction, final render-03 completed all
18 again. Profile reuse/sync is a **possible explanation**, not an established root cause.
The change preserves the required headless Edge renderer and native resolution; it does
not weaken an SVG or output criterion. See the final render manifest separately.
