# S02 Windows evidence catalogue

This directory retains the bounded 8 October 2026 Windows observation described in
[`../s02-windows-observation.md`](../s02-windows-observation.md). The graphical run is
bound to revision `1b6b3a3abdfe5fd3839020b20e6da245b98c1ce1`, the pinned engine, and
the copied-input ledger. Its raw focus result is retained unchanged but is **inconclusive
because initial native foreground was not established**. The corrected gated focus-only
follow-up is bound to `826bc029ebd4626d426a5ccc596aee3ef120fb78`; it is also
inconclusive because the child never acquired sustained native foreground. Scratch projects
and private user directories remain outside the repository under `C:\tmp\ft\lanes\s02\`.

| Path | Contents |
| --- | --- |
| `result.json` | Complete runner result, commands, process IDs/exits, criteria, camera/draw result, focus samples, and foreground-window timeline. |
| `copy-ledger.json` | SHA256 and byte length for every staged runtime input before import. |
| `import.log`, `runner-console.log` | Clean isolated Windows import stream and parent runner result. |
| `draw/stdout.log`, `draw/engine.log`, `draw/stderr.log` | Full automatic-draw process streams; stderr is retained empty. |
| `draw/s02-draw-{03,10,30}.png` | Viewport pixels saved from those exact automatic post-draw callbacks, each 1280×800. |
| `focus/stdout.log`, `focus/engine.log`, `focus/stderr.log` | Original raw saved-focus-runner streams; invalid initial-foreground precondition, not a native-focus failure. |
| `focus-fixed/result.json` | Corrected runner result and stage-aware foreground timeline; classification is `inconclusive: initial native focus not established`. |
| `focus-fixed/stdout.log`, `focus-fixed/engine.log`, `focus-fixed/stderr.log` | Corrected bounded fixture streams; no key injection or minimize occurred. |
| `focus-fixed/copy-ledger.json`, `focus-fixed/import.log`, `focus-fixed/runner-console.log` | Corrected input binding, clean import and parent result. |
| `headless/summary.json` | Existing S02 runner result on Windows. |
| `headless/identities.json` | Headless runner's saved-resource fingerprints. |
| `headless/import.log`, `headless/outcomes.log`, `headless/runner-console.log` | Full isolated import, outcome and parent streams for the headless run. |
| `checks/script-checks.log` | All-owned compilation pass and the three accepted pre-existing S07-driver lint warnings. |
| `checks/unit-tests.log` | Original complete 12-test Python discovery result. |
| `checks/review-fix-unit-tests.log` | Corrected complete 13-test discovery, including nonzero-startup stage mapping. |
| `checks/review-fix-script-checks.log` | Corrected all-owned compilation pass and the same three accepted S07-driver lint warnings. |
| `checks/uid-import.log` | UID-generation import, including the known development-addon diagnostics. |

No file is a physical-display, physical-key, Alt-Tab, subjective-feel, camera-selection,
Steam, Deck, export, or performance receipt.
