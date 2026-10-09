# UI v1 — concept delivery evidence

8 October 2026. Lane `ui-mockups`. [Concept index](../../concepts/ui-v1/README.md) ·
[Visual gallery](../../concepts/ui-v1/review.html).

**Current revision:** [review R1 correction and checks](revision-01/README.md).
Current M1 is **ENet-only**. Sheets 10/12/13/18 are the current ENet flow;
11/19/20/21 are visibly tagged **FUTURE ADAPTER EXPLORATION**, not current Steam features
or testing. The original review's Steam-default presentation was rejected and superseded.

## Scope and provenance

This is **documentation/concept art only**: twenty-one standalone SVGs and twenty-one
headless-Edge PNGs, all 1280 × 800. The initial pass had eighteen; review R1 adds three
labelled future-only copies so the Steam studies remain available without occupying the
current ENet host/lobby/admission paths. No scenes, themes, gameplay, runtime UI code, TODOs,
other task bullets or accepted concept/capture sources changed. SVG and documentation
were authored directly because the editor was not running and MCP tools were unavailable.
The new concept/evidence directories have `.gdignore`; no engine imports or UIDs were
needed for these documentation assets. No project editor was opened or synchronized.

Actual initial checkout: `e174c4d` on `lane/ui-mockups`, clean. The common brief named
`19fbd4d`, but three commits already existed above it: `29ee423`, `e0b152f`, `e174c4d`.
Those are inherited work, not this lane's edits. The original `19fbd4d..HEAD` review
patch included those earlier changes. The review follow-up now requests a rebase onto
`s08-enet-bandwidth` and patch `git diff s08-enet-bandwidth...HEAD`; this supersedes the
old patch recipe. See [changed-files.txt](changed-files.txt) for this delivery's file list.

Only these committed PNG sources were embedded; the [static audit](static-validation.json)
binds their SHA256s and checks every embedded image against those exact bytes:

- `docs/spikes/s06-windows-evidence/captures/camera-42/static.png`
- `docs/spikes/s05-windows-draw-evidence/client/burst.png`
- `docs/concepts/p0-04/i-perspective-high-rise.png`

All new 2D lines, icon shapes and type are authored SVG. The artwork/capture sources are
not modified. No generated 3D assets, external font downloads or third-party icons.

## Initial-pass results (historical)

These receipts bind the original eighteen-screen pass, not all current revised bytes.
Use [R1 results](revision-01/README.md) for the latest scope assertions, eight rerenders,
21-screen asset audit and post-rebase quick checks. Engine checks below are historical;
no engine/Steam test is claimed for a documentation-only revision.

| Check | Outcome and evidence |
| --- | --- |
| Initial final Edge render | **18/18 exit 0**, PNGs exactly **1280 × 800**; [expanded commands and source/output hashes](renders/render-results.json), [per-screen logs](renders/01-foot-compact.log). Other logs use the same SVG basename. |
| XML and asset audit | [static-validation.json](static-validation.json): expected 18 SVG/PNG pairs, root size/viewBox, no script/foreignObject or external references, embedded source equality, SVG/PNG hashes, required state labels, local links and <5 MB per delivered file. |
| Browser text bounds | [text-bounds.json](text-bounds.json): 430 text elements, **zero outside the frame**. Four font-metric box intersections, not four visible clipping defects; see manual review below. [Browser log](text-bounds.log). |
| Visual inspection | Opened all 18 native PNGs, not just thumbnails. Final two car images reopened after rotating the local car map glyph to match the pictured left-facing car. Other 16 PNGs byte-identical to the reviewed render-02 versions. |
| Formatting | Pass: [formatting.log](checks/formatting.log). |
| Lint | Command exits 1 due to **exactly the three pre-existing S07 driver warnings permitted by the lane brief**, not a clean lint pass. [style.log](checks/style.log), [combined console](checks/script-checks.log). No source changed to suppress them. |
| All-owned compilation | **74/74 explicit script compiles pass**: [compilation.json](checks/compilation.json), [manifest](checks/scripts.json). [Import/setup](checks/compiler-setup.json) also passes; [setup log](checks/compiler-import.log). Compilation is separately measured, not inferred from import. |
| Python tools tests | **10 tests pass**: [unittest.log](checks/unittest.log). No new runtime tests added for a concept-only task. |
| Diff/scope checks | `git diff --check` passes. Original sources unchanged versus `e174c4d`. Only the two new documentation directories changed. No staged files remain after the lane commit. |

### Commands and tool versions

Tool setup, exactly as instructed:

```sh
export PATH="$(dirname "$(mise -C C:/GameDev/git/fun-things which godot)"):$(dirname "$(mise -C C:/GameDev/git/fun-things which gdstyle)"):$PATH"
godot --version
gdstyle --version
python --version
```

Observed: Godot `4.8.dev7.official.c971f93e7`, gdstyle `0.3.0`, Python `3.14.2`,
Pillow `12.3.0`. Edge file-version metadata: `154.0.4258.62`, read with:

```powershell
(Get-Item "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe").VersionInfo.FileVersion
```

Repository checks (output paths fresh and outside all worktrees):

```sh
python tools/script_checks.py --output C:/tmp/ft/lanes/ui-mockups/checks-01/scripts
python -m unittest discover -s tools -p 'test_*.py'
git diff --check
git diff --name-only e174c4d -- docs/spikes/s06-windows-evidence docs/spikes/s05-windows-draw-evidence docs/concepts/p0-04
```

The script-check command returned 1, with JSON
`{"formatting": true, "style": false, "compilation": true}`. The accepted existing lint
warnings are `fixture.gd:6` line length 101, `guards.gd:17` function length 60 and
`run.gd:75` function length 65, all under `tests/fixtures/s07_driver/`.

Scratch-only author/render helpers were invoked as:

```sh
python .pi/ui-v1-author.py
python .pi/ui-v1-render.py C:/tmp/ft/lanes/ui-mockups/render-02
python .pi/ui-v1-render.py C:/tmp/ft/lanes/ui-mockups/render-03
```

These helpers are not runtime or committed repository tools. The final SVGs are the
editable sources. For independent reproduction, each exact browser command is expanded
in [render-results.json](renders/render-results.json), and the concept README gives a
single-screen shell recipe. Each final render used a private per-screen profile,
`--headless --disable-gpu --screenshot=... --window-size=1280,800`, device scale 1,
no first-run UI, no extensions/sync and no background networking. Child deadlines were
45 seconds; all final children exited normally. No unrelated process was stopped.
The static validator invocation and source are retained as documentation evidence in
[validate.py.txt](validate.py.txt); it uses standard-library XML/HTML parsing and Pillow.

Raw scratch output remains under `C:/tmp/ft/lanes/ui-mockups/`: initial `render-01`,
intermediate `render-02`, final `render-03`, `checks-01` and `audit-01`. Retained evidence
contains no browser profiles, compiler mirror, scratch project or file above 5 MB.

### Browser diagnostics and initial failure

- The [initial-attempt record](initial-attempt/README.md) retains the unsuccessful shared
  scratch-profile attempt: third screenshot written, but process wait timed out at 40 s.
  This was not silently called a successful render. First two raw logs and third PNG remain.
- Final logs for screens 01, 04, 08 and 09 contain Chromium's
  `fallback_task_provider.cc:126` task-manager-provider diagnostic. All four exited 0,
  emitted their screenshot, passed dimensions/hash checks and were opened successfully.
  This is a browser-internal diagnostic, **not** a Godot script error or proof that Edge
  logs were clean. No broad error suppression was used. Other final screen logs contain
  screenshot-write receipts. These observations establish image delivery, not browser health.
- The final screenshots do not contain missing-image symbols, blank maps, clipped labels
  or browser chrome in the native frame. Font rendering remains host-system dependent.

## Manual review and limitations

The bounds audit uses SVG `getBBox()`, which includes font ascent/descent whitespace.
It flags four pairs: HATCHBACK with speed in 06 and 07; the main-menu eyebrow with FUN,
and FUN with THINGS in 09. All were reviewed in native PNGs: actual glyphs have visible
separation; no ink collisions. The audit deliberately retains these heuristic findings
rather than silently filtering them out. It is not a general-purpose layout proof.

Other observations:

- Screen 03's larger map covers the top edge of the right-hand car. This is retained as
  the comparison's occlusion cost and documented in the index; it favours testing 200 px
  before 240 px. Moving the screenshot would have hidden that useful limitation.
- Opaque text panels preserve contrast over the pale S06 sidewalk and detailed accepted art.
  Native numeric health/ammo, 22 px interaction copy and 64 px speed are clear in desktop
  images. Numbered 20 px map markers and 16 px tags need a real handheld pass.
- Screen 05 intentionally uses a historical eight-effect burst picture. It does **not**
  preserve or approve an eight-effect cap; the owner removed that cap on 8 October.
- Static captures cannot demonstrate authoritative state, real nearby interaction range,
  stopped-car eligibility, hit/damage confirmation, live Steam connectivity, focus traversal,
  input handling, animation comfort, performance, long names or marker overlap under load.
- No Deck LCD/OLED device, Gaming Mode, Steam account or real-process game test ran for this
  design lane. No runtime changes were needed, and none are claimed.
- Palette, layout and optional extra markers remain **owner-review candidates**. The 200 px
  recommendation is a design preference from these stills, not acceptance or a new product
  rule. Independent reviewer gate and owner selection remain next steps.

## Lane criteria (current delivery)

| Requested deliverable | Status |
| --- | --- |
| Foot HUD on street capture; 2–3 top-right minimap variants, health, weapon/ammo, interaction, hit/damage and peer tags | Delivered: 01–05, with three 160/200/240 px variants |
| In-car speed, condition, stopped-only exit and car minimap marker | Delivered: 06–07; no firing UI |
| Three minimap directions with requested symbol vocabulary and native-size discussion | Delivered: 08 and index; all north-up |
| Current ENet main/host/join/lobby, local menu, audio-only settings and connection states; retained future Steam concepts | Current: 09–10, 12–18. FUTURE ADAPTER EXPLORATION only: 11, 19–21. No current Steam feature/testing promise. |
| Self-contained native SVG plus headless Edge PNG for each | Delivered: 21 pairs; current hashes combine unchanged initial receipts with eight R1 rerenders. |
| README thumbnails, per-screen rationale/readability/questions, coherent token table | Delivered, plus browseable HTML gallery |
| Concept-only scope; no staged files; lane commit and review patch | Committed lane-only documentation; reviewer consumes the required `.pi/review/lane.patch` |

No human product decision was required to deliver the exploration. Owner preference,
optional-marker scope and actual Deck validation are explicitly left open for the next task.
