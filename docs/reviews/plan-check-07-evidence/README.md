# Seventh checkpoint static evidence

[Requirements](requirements.txt) and [root facts](root-facts.txt) are the review inputs.
[Accepted audit](accepted-audit.json) binds every ten-commit parent/path/mode/blob,
consulted immutable source and note/report payload SHA, exact expected review/archive
sets and supplied150-entry relocation ledger verification. Old large note snapshots
and unchanged source trees are not copied; exact reachable Git blob/revision/SHA
references preserve those inputs. Read accepted runtime reports as history only.

[Checker](check.py) executes new read-only static checks; it never imports historical
checkers or executes engine/probe/archive code. [Worker retention](worker-retention.json)
indexes every newly captured source/output/failure through deterministic gzip bytes
and original raw SHA. Initial historical/current-ledger key collision, absent guessed
source filename, wrong manifest schema and historical-patch whitespace classification
remain separate original or explicitly labeled replay receipts. No payload is edited
or broadly excluded. Final actual checker/rebase/clean outputs and one fresh reviewer's
COMPLETE new reports/all meaningful raw artifacts are retained losslessly in valid JSON
`refs/notes/paseo-orchestration` on the same final HEAD after actual byte/hash readback.
Future storage is a delivery obligation until verified, not inferred from this text.
