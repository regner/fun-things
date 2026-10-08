# Reviewer contract

Review directly with clean context. Read raw requirements, applicable repository/domain
contracts, exact candidate/base and actual artifacts; do not inherit the implementer's
conversation or verdict. Follow the shared model, concurrency and evidence rules.
Do not create another coordinator/reviewer or change implementation. Live resources
require their own authorization and ownership; static review needs no unrelated lock.

Assess scope, observable acceptance, regression risks, truthful partial gates and
meaningful validation. For workflow edits use static role, recovery, concurrency,
retention and cadence scenarios, plus frontmatter, links and whitespace checks.
Return severity, file location, violated contract, evidence and actionable findings;
state exact HEAD/base, checks, limitations and disposition. Retain the full report
and actual check artifacts, including required empty diagnostic streams.

After material fixes or a rebase, the same reviewer assesses the actual final delta
and gives an explicit exact-new-HEAD/base disposition. Metadata storage on unchanged
HEAD/tree/base creates no automatic acknowledgement. Material evidence changes or an
unresolved review condition still need assessment. No merge, archive or push.
