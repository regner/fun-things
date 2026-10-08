# Checkpoint09 static evidence

[Record](../plan-check-2026-10-08-09.md), [complete raw requirements](raw-requirements.md),
[launch receipt](launch-receipt.json), [selected immutable sources](references.json).
No old runtime archive is recursively copied and no engine/toolchain experiment ran.

`accepted-ledger.json.gz` is deterministic gzip of strict UTF-8 JSON. It records all
69 commits, exact sole parents/name-status changed paths, examined exclusive/inclusive
bounds, and immutable consulted note blobs with bytes/SHA256 and complete report
selectors. Older reports remain in those Git objects; transient decoded paths are not
required. Report selectors include initial findings and exact-final qualifications,
not just verdicts. Original checkpoint08 note report selectors are available references,
not a repeated review of its old runtime package. Historical reports are unchanged.

Read an exact old note without trusting a subsequently appended mutable note:

```sh
git cat-file blob <blob-from-ledger>
```

Selectors identify plain UTF-8 text or lossless base64/gzip/zlib fields according to
that note's own encoding metadata. The S08 handoff note has a gzip+base64 JSON payload
dictionary; standard-editor reports are UTF-8 `reviewer_payloads`; S07 cards store
`complete_reports_verbatim`. Current research/driver/image/lifecycle notes retain
separate initial/final report fields. No missing historical stream, lookup, exit or
reap is reconstructed. `references.json` also binds the independent Luna final-package
note and separate original report-only carrier; that carrier was not integrated.

Run only the new offline checkpoint checker, from repository root:

```sh
python3 -B docs/reviews/plan-check-09-evidence/check.py
```

It checks exact range/parents/path identities, immutable note/source identities,
27→28 task coverage, exact single-task TODO addition, conditional dependencies,
JSON/Python syntax, links/anchors, LF/authored whitespace and permitted scope. It
neither imports project/runtime tools nor rebuilds old archives. Historical runtime
results are accepted inputs, not re-executed checks. The TODO has 64 lines solely
because one genuine task was added to the accepted 63-line list.

Actual worker/reviewer check sources, argv/cwd/exits, complete stdout/stderr,
failures and required empty streams plus complete independent initial/final reports
are retained in ONE ordinary exact-candidate `refs/notes/paseo-orchestration` package.
Its independent expected set and stored/decoded/source hashes/readback are verified
before handoff. This is metadata-only storage after frozen-candidate review, not an
extra report-only candidate commit or acknowledgement cycle. Final SHA/base/verdict,
reviewer identity and actual readback locator are supplied in the delivery note.
