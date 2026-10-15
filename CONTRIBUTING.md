# Contributing

## Before implementation

Open or identify an issue describing the user problem, reproduction, expected outcome, scope, risks, dependencies and named acceptance tests. Confirm the request is actionable and authorized; an unassigned issue is not proof nobody is working on it. Check overlapping PRs and ask for a design decision when requirements conflict.

For a new subsystem, fill [the subsystem template](templates/SUBSYSTEM.md) before substantial implementation. The design must identify data ownership, API contracts, failure/recovery behavior, security boundaries and test entry points. Use an ADR for a consequential choice; [architecture](ARCHITECTURE.md) distinguishes implemented behavior from planned extensions.

## Change and review

- Keep one bounded change per branch/PR. Link the issue and acceptance criteria.
- Contributor: diagnose failures, fix code, provide fix revision, commands, environment, results and redacted logs. Disclose unavailable hardware or unexecuted tests.
- Reviewer: inspect implementation and relevant callers, validate evidence, current-head checks and unresolved human concerns. State review coverage and limitations.
- Maintainer: decide policy exceptions, ownership and release acceptance; perform the final merge under the adopting project's rules.
- A review request must say what changed, why, what was tested and what remains unknown. Performance claims need matched model/hardware/workload/baseline and repeatable measurements.

Run the commands in [AGENTS.md](AGENTS.md), check whitespace with `git diff --check`, and add negative tests before changing readiness rules. No routine workflow or paid resource is activated by this template. No network is needed for this repository's tests.

## Evidence and learning

Use [the lesson template](templates/LESSON.md) for an adjudicated defect or clean case. Cite the public issue/PR and exact revision, distinguish local replay from production, and record the regression that enforces the lesson. Do not assert review accuracy without labeled sample sizes and a documented evaluation.

For copied templates, preserve applicable license notices, record the source revision, and review updates as normal diffs. Do not silently overwrite a project's existing AGENTS.md, contributing guide or subsystem docs. `CONTRIBUTING.md` and `LESSONS.md` are the canonical names; avoid separate conflicting contribution.md/lesson.md copies.
