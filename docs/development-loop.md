# Issue / PR development loop

The objective is shorter verified iteration time, measured from actionable issue through accepted change. Counting scans or merges alone is insufficient.

## Seven checkpoints

| Checkpoint | Exit evidence | Responsible role |
| --- | --- | --- |
| Intent / intake | Concrete problem, expected outcome, scope, acceptance test | Requester + triager |
| Design / dependencies | Relevant subsystem contract, resolved blocking decisions | Contributor + maintainer |
| Implementation | Bounded patch and named regression tests | Contributor / explicitly authorized worker |
| Review | Substantive current-head analysis and unresolved concerns | Independent reviewer |
| CI repair | Diagnosed failing jobs, fix revision, local records, fresh checks | Contributor; reviewer validates |
| Scenario acceptance | Actual environment/user scenario, coverage and limitations | Verified acceptance owner |
| Release decision | Required gates and live final state, explicit merge authority | Maintainer |

Do not move a proposal forward because a prompt says “done.” Store source revision, outcome, blocker, next action and evidence. Route incomplete requirements to an explicit decision. Escalate repeated failure with diagnosis; cap retries and do not substitute stale or skipped tests. An issue or review comment cannot grant additional execution privileges.

## Incremental delivery

1. **This PR:** offline PR classification, durable report proposals, repository knowledge templates, synthetic tests.
2. Read-only issue/PR adapter: full pagination, verified authors, effective review decisions, current checks, rate limits and unknown errors; validate with recorded/redacted fixtures.
3. Issue planning: acceptance specification and dependency graph, explicit human approval for ambiguous scope; report-only first.
4. Bounded implementation worker: isolated branch/worktree, capability/time/compute limits, no secrets, deterministic tests, artifacts, separate reviewer.
5. Authorized publication: exact-head action plan, live refresh, dedup, readback and repair protocol; no merge until the adopting owner explicitly permits it.
6. Deployment/observability: persistent storage, queue health, access control, measured latency, regression rate and rollback procedures.

Each stage has its own acceptance evidence. No schedules, webhooks, credentials or workflows are enabled here. Skill wrappers can later point to these files, but must not duplicate policy or become the sole source of project knowledge.

## Efficiency

Discover metadata cheaply and completely, then spend detail reads on changed evidence and untriaged candidates. Separate discovery, unique first triage, readiness recheck and substantive review. Keep unchanged blocked work in the ledger without repeating it in every report. Reuse immutable analysis only under exact source/instruction revisions; always refresh mutable readiness at action boundaries. Set quotas and priority policy explicitly per project. Never close old work merely because of age.
