# S03-S Valve API/interface evidence index

Research dated **2026-10-08**, base/contract `233493abc7d2e3c106fb620105cfb766f542813b`.
Candidate document: [Valve APIs and proposed interface](../s03-s-valve-api-interface.md).
Full original task and later authority are in [requirements.txt](requirements.txt).
This is static/public evidence only, not native SDK/runtime conformance or a peer.

## Declared package

- `retrieve.py`, `retrieval.json`, `retrieval/`: exact public curl URLs/argv/UTC/exits
  and complete stdout/stderr (including empty streams). Each URL was fetched once;
  adding public `steam_api_common.h` followed inspection of callback documentation.
  It is Valve's explicit open-source callback stub, not the restricted SDK header.
  All 14 declared public retrievals succeeded. No restricted-source bypass occurred.
- `extract.py`: reproducible Valve `documentation_bbcode` HTML-to-text extraction.
  Text excerpts preserve numbered extracted lines; they are **not raw HTML**.
- `snapshot.py`, `sources.json`, `sources/`: complete small immutable public headers/
  README/license plus numbered Sockets/types and selected documentation excerpts.
  Source ledger distinguishes full original bytes/SHA from extracted and stored bytes/
  SHA and records every range. URLs with revision d534c19… are immutable; public
  Steamworks web pages are mutable and are not an SDK-1.65 signature/version pin.
- Sockets/types original scratch bytes were read back against the accepted full
  hashes at upstream evidence **57d337312bb6f98a22e8d94a41eace3b9e7cc50b**;
  neither was refetched. Prior excerpts remain at that revision's
  `docs/spikes/s03-s-upstream-peer-evidence/sources/valve/include/steam/`.
  Prior review/complete diagnostics live in `refs/notes/paseo-orchestration` on
  57d3373. This package neither copies nor relabels prior probes/acceptance.
- `check.py`, `run_checks.py`, `expected-set.json`, `checks/`: actual owned static
  check sources, declared complete expected set, argv/exits and full diagnostic
  streams. A static failure remains saved alongside its corrected run.
- Sole independent reviewer operates in clean context against a **committed exact
  HEAD/base**, with static/read-only public checks only. Complete substantive/final
  reports, actual check sources/argv/exits/stdout/stderr/failures and launch receipt
  are retained losslessly on that reviewed HEAD in local
  `refs/notes/paseo-orchestration`. The note's declared expected set, byte hashes and
  one readback receipt cover the full package. ROOT receives the reviewer ID/verdict
  and exact SHA in handoff. Metadata-only note storage changes no candidate tree.

No reviewer verdict is implied by this pre-review index. The exact final disposition
is the report in the note, not this mutable wording or another candidate's approval.

## Offline checks

From repository root (Python 3; Git only, no engine/native/Steam execution):

```sh
python3 docs/spikes/s03-s-valve-api-evidence/check.py
# Optional original/extracted scratch and numbered excerpt verification, no retrieval:
python3 docs/spikes/s03-s-valve-api-evidence/check.py --source-readback
```

`check.py` verifies independently declared expected paths, source/stored hashes,
Python/JSON parseability, local Markdown paths, exact owned diff and byte-identical
TODO outside the S03-S task and its readiness phrase. With `--source-readback`, it
checks original fetched HTML/header hashes and regenerates every stored excerpt
from the downloaded source or reproducible parsed text. Raw original HTML and
already accepted full Sockets/types headers are scratch inputs, **not retained whole
in this package**; the ledger's raw hashes are not hashes of their smaller excerpts.
Public-doc refetch may differ; that does not change these dated snapshot identities.

Run records are immutable evidence of their own invocation. Re-running checks is
allowed offline; do not overwrite original streams or infer dynamic acceptance.
Only doc/static tooling changed. No native build, SDK acquisition, Godot/Blender/
editor/service/process/config mutation, Steam initialization/lobby/traffic, account/
private branch/depot/device testing, vendor/pin/gameplay/scene/asset edits occurred.
Actual Steam validation is **DEFERRED / UNEXECUTED** under the latest requirement.
S03-S/Steam/Deck/P0/M1 gates stay OPEN; ENet/Standalone remain Steam-independent.
