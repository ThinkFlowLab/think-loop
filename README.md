# think-loop

the repo template to help loop developments faster than ever

A repository-first template for an evidence-driven issue → implementation → review → CI → acceptance loop. Inspired by Magpie's compact agent entry point, subsystem documentation and reusable lessons. Keep durable project knowledge in the repository; an optional skill is only a small entry point.

## What works today

Version **0.1.0** is a Python 3.11+ standard-library, **offline report-only MVP**. It classifies normalized PR snapshots, requires exact-head checks and analysis, preserves human blockers, and stores idempotent proposed TODOs in SQLite with single-host leases and crash recovery. It never calls GitHub, runs a model, edits a project, sends a comment, approves, triggers CI or merges.

```sh
python -m unittest discover -s tests -v
python -m think_loop --config examples/loop.project.json \
  --snapshot examples/snapshot.json --state /tmp/think-loop-demo.sqlite --now 1000
```

The example is synthetic replay data, not a real passing PR. Repeated runs retain one pending proposal until the recipient confirms delivery with `--ack PROPOSAL_ID`. Printing a report does not establish successful delivery. Real snapshots must use current time; `--now` is for controlled replay only.

## Start a new project

1. Read [AGENTS.md](AGENTS.md), [CONTRIBUTING.md](CONTRIBUTING.md), [architecture](ARCHITECTURE.md) and [lessons](LESSONS.md).
2. Copy [the project onboarding worksheet](templates/PROJECT.md) and fill it from actual code, maintainers and executable tests. Link each subsystem to its owner, invariants and test commands.
3. Adapt [loop.project.json](examples/loop.project.json) using [contract v0.1](docs/adapter-contract.md). Obtain the project owner's policy choices. Missing required checks never means green.
4. Replay snapshots offline. Measure unique first triage, changed-state rechecks, deep reviews, time blocked and escaped regressions separately.
5. Before production, implement and independently test a read-only adapter, authentication isolation, complete pagination and freshness. Only then consider explicitly authorized actions with a separate write adapter and live final checks.

## Implementation status

| Component | Status |
| --- | --- |
| Repository guidance, subsystem and lesson templates | Implemented |
| Offline PR classification / local report ledger / replay tests | Implemented |
| Normalized GitHub adapter contract | Documented; transport not implemented |
| Issue intake and implementation-worker protocol | Documented; worker not implemented |
| Live GitHub ingestion, webhooks and schedules | Not implemented or enabled |
| Model-based review, automatic fixes, approvals, merge | Not implemented or authorized by this template |
| Multi-host coordination, distributed transactions | Not implemented |

There is no deployment, daemon or service to run yet. This small executable core is the first verifiable step, not a claim that a Markdown template alone automates development. See [delivery stages](docs/development-loop.md) and [reference decisions](docs/references.md).
