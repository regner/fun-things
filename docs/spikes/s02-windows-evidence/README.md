# S02 Windows evidence catalogue

This directory retains the bounded 8 October 2026 Windows observation described in
[`../s02-windows-observation.md`](../s02-windows-observation.md). The graphical run is
bound to revision `1b6b3a3abdfe5fd3839020b20e6da245b98c1ce1`, the pinned engine, and
the copied-input ledger. Scratch projects and private user directories remain outside the
repository under `C:\tmp\ft\lanes\s02\`.

| Path | Contents |
| --- | --- |
| `result.json` | Complete runner result, commands, process IDs/exits, criteria, camera/draw result, focus samples, and foreground-window timeline. |
| `copy-ledger.json` | SHA256 and byte length for every staged runtime input before import. |
| `import.log`, `runner-console.log` | Clean isolated Windows import stream and parent runner result. |
| `draw/stdout.log`, `draw/engine.log`, `draw/stderr.log` | Full automatic-draw process streams; stderr is retained empty. |
| `draw/s02-draw-{03,10,30}.png` | Viewport pixels saved from those exact automatic post-draw callbacks, each 1280×800. |
| `focus/stdout.log`, `focus/engine.log`, `focus/stderr.log` | Full saved-focus-runner streams; stderr is retained empty. |
| `headless/summary.json` | Existing S02 runner result on Windows. |
| `headless/identities.json` | Headless runner's saved-resource fingerprints. |
| `headless/import.log`, `headless/outcomes.log`, `headless/runner-console.log` | Full isolated import, outcome and parent streams for the headless run. |
| `checks/script-checks.log` | All-owned compilation pass and the three accepted pre-existing S07-driver lint warnings. |
| `checks/unit-tests.log` | Complete 12-test Python discovery result. |
| `checks/uid-import.log` | UID-generation import, including the known development-addon diagnostics. |

No file is a physical-display, physical-key, Alt-Tab, subjective-feel, camera-selection,
Steam, Deck, export, or performance receipt.
