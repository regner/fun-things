# UI v1 — review R1: ENet-only current presentation

Review finding: **P1 / REQUEST_CHANGES**. The original UI pack presented Steam as a
current/default selectable transport. Owner decision 9 (8 October) instead says the
initial game is **ENet ONLY**, with no Steam-specific features or testing now. Steam
only informs abstractions/APIs for a possible later adapter.

This revision implements that instruction. It does not change the product decision or
implement any networking/UI behaviour.

## Screen disposition

| Current/default M1 | What changed |
| --- | --- |
| 10 · Host | Explicit ENet port and Create ENet lobby. No Steam tab. States ENet-only current scope. |
| 12 · Join direct | Removed Steam selector; ENet-only address/port entry is the current presentation. |
| 13 · Lobby | ENet heading and address/port sharing; no Steam invite action. |
| 18 · Admission | ENet address/connection context, not Steam friend joining. |

| FUTURE ADAPTER EXPLORATION only | Preservation |
| --- | --- |
| 11 · Friends join | Retained original list/controls; added visible future title and explicit ENet-only-current-M1 footer. |
| 19 · Steam host | Preserves the previous 10 host concept with the same explicit future-only labels. |
| 20 · Steam lobby | Preserves the previous 13 invite/lobby concept with the same labels. |
| 21 · Steam admission | Preserves the previous 18 Steam admission concept with the same labels. |

Every Steam sheet has **FUTURE ADAPTER EXPLORATION** in both its SVG `<title>` and its
visible top title tag, plus **CURRENT M1: ENET ONLY · NO STEAM FEATURES OR TESTING NOW**
in the footer. Those labels apply to all controls shown within that sheet. README and
HTML gallery separate these four future references from the current ENet-only flow.
No future sheet is offered as a current transport choice.

Three explicit future copies keep the requested Steam mockups rather than discarding
or obscuring them. The pack now has **21** self-contained SVG/PNG pairs. No scenes,
themes, gameplay, runtime UI, other task records or original source images changed.
Text-file authoring remains appropriate; no editor/MCP tools were available or used.

## Validation

- [Render results](render-results.json): **8/8 revised/new screens exited 0**, all PNGs
  **1280 × 800**. Exact Edge commands, source/output hashes and child PIDs are retained.
  Per-screen `.log` files in this directory contain screenshot-write receipts and no
  ERROR/WARNING diagnostics. No unowned process was stopped.
- All eight PNGs were opened at native size: the current ENet-only headings/actions and
  four future title/footer labels are visible, without cropped text or overlapping controls.
- [Text bounds](text-bounds.json): **21 screens, 504 text elements, zero outside frame**.
  No intersections in the eight revised/new sheets. Four unchanged font-metric
  intersections remain in 06/07/09, already visually reviewed in the initial record.
  [Browser log](text-bounds.log) is retained; bounds are not a runtime layout proof.
- [Static asset/scope audit](static-validation.json): checks all 21 SVG/PNG pairs,
  current hashes, source PNG embedding, local links, file size and the P1 regression:
  no Steam action/tab labels in 10/12/13/18; explicit future title and footer in all four
  Steam sheets; those sheets occur only in the gallery's future section.
- The initial [render manifest](../renders/render-results.json) is historical and unchanged.
  The updated [validator](../validate.py.txt) overlays this revision's eight rows onto the
  original manifest, verifying all 21 current outputs without claiming the old hashes bind
  revised files. Initial static/browser/compiler receipts likewise remain historical.
- Pre-rebase Python tool tests: 10 passed. The post-rebase receipt below supersedes that
  quick check for the rebased tree. No Godot, Blender or Steam test ran in this revision;
  there is no runtime code change. Initial engine/style results are historical, not rerun.

### Commands and retained outputs

The eight-screen renderer ran successfully before the resumed session's new shell-timeout
rule. Its bounded child wait was 45 seconds. The exact invocation was:

```sh
python .pi/ui-v1-render.py C:/tmp/ft/lanes/ui-mockups/revision-01-render \
  10-host 11-join-steam 12-join-direct 13-lobby 18-join-loading \
  19-host-steam-future 20-lobby-steam-future 21-loading-steam-future
```

Each expanded headless Edge command is in `render-results.json`, including 1280×800
window size, scale factor 1 and a private per-screen profile. No renderer substitution.
After resume, Python commands are wrapped in shell `timeout`; browser children also
have bounded waits. Static audit recipe:

```sh
timeout 60 python docs/spikes/ui-v1-evidence/validate.py.txt \
  --output C:/tmp/ft/lanes/ui-mockups/revision-01-audit/static-validation.json
timeout 60 python -m unittest discover -s tools -p 'test_*.py'
git diff --check
```

Scratch evidence is outside the checkout in `C:/tmp/ft/lanes/ui-mockups/revision-01-render`
and `revision-01-audit`. No browser profiles or scratch project are committed.
The checked-in SVGs remain the editable source; scratch author/render helpers are not
runtime tools. See the main concept README for a standalone render recipe.

## Integration and remaining limits

The follow-up requests `git rebase s08-enet-bandwidth`, quick checks on the rebased tree,
and `.pi/review/lane.patch` from `git diff s08-enet-bandwidth...HEAD`. The post-rebase
receipt records the resulting base and checks. Rebase replaces the earlier patch bases;
no merge or push is requested.

This addresses review P1 in the artifacts; independent re-review remains required.
Owner visual selection, optional marker scope, real input/navigation, runtime UI and
later physical handheld readability are not established by the drawings. No Steam
feature or test has been newly commissioned.
