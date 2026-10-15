# Adapter contract v0.1

Normative for the offline MVP. JSON Schema for project config: [schema](../loop.project.schema.json). Runtime validation is `validate_config`; unknown config keys are rejected. A project config changes the proposal identity; it does not authorize external actions.

## Config

- `contract_version`: literal `0.1`.
- `repository`: exact `owner/repo`, isolated per authenticated account by the deployment. This local MVP has no credentials or transport.
- `policy_version`: nonempty project-owned policy revision.
- `required_labels`: all labels required for selection, or empty for all non-drafts. Discover labels before configuring; do not infer passing evidence from labels.
- `required_checks`: nonempty names needed for a ready handoff. Empty is allowed for onboarding but evaluates unknown. No implicit docs-only skips in v0.1.
- `trusted_reviewers`: verified actor logins; empty list prevents a ready handoff. The author cannot approve their own change.
- `evidence_max_age_seconds`: positive integer freshness bound.

## Normalized snapshot

See [complete synthetic example](../examples/snapshot.json).

Top level: `repository`, `observed_at` (epoch seconds), `complete` (literal true), `pages` (`expected`/`received` positive equal integers), `errors` (empty list), `pull_requests` (unique positive numbers). Any incomplete collection, error, future or stale fetch is unknown: CLI exits 2 and leaves prior backlog unchanged. The adapter must fully paginate each discovery query, record its scope, reconcile duplicate/missing pages, and refresh selected mutable evidence. Do not fabricate expected page counts. This engine checks the normalized coverage assertion but cannot independently prove transport completeness.

Each PR: `number`, `state`, `draft`, exact lowercase 40-character `head`, `author`, `labels`, `mergeable`, `discussion_complete`, `human_blockers`, `checks_complete`, `checks`, `reviews_complete`, `reviews`, `analysis`, `evidence_revision`.

Checks have `{name, head, status}`. The adapter supplies exactly one effective latest attempt per required check and tested head. Historical reruns and multiple applications with the same name must be resolved under explicit trusted provider policy, never arbitrarily discarded. Status is `success`, `pending`, `failure` or `unknown`; skipped/cancelled/neutral are unknown here. Do not treat a merge-queue tested revision as the PR head unless a separately verified policy establishes the relationship; v0.1 provides no such mapping.

Reviews have `{actor, head, state}`. Supply only each actor's **effective latest non-dismissed decision**, with dismissed/revoked approvals removed. An old approval followed by changes requested is not an approval. Normalize unresolved threads and any effective changes-requested decision into `human_blockers`; `discussion_complete` and `reviews_complete` require full pagination. Preserve unresolved concerns across head changes until explicitly resolved by evidence/human decision.

`analysis` is `{head, complete}` and is an assertion by the trusted substantive-review producer, not a source-analysis engine in this MVP. A label, title, agent self-report, or another review alone cannot set it true. Keep audit links, actual coverage, actor and findings in the private evidence store; bind the digest through `evidence_revision`. No private source content belongs in the public template.

`evidence_revision` identifies the normalized evidence bundle, including edited comments, effective review decisions, test logs and relevant instruction revision. It must change when those change. Do not set it to the head alone or use unstable fetch IDs/timestamps that make unchanged observations appear new. Snapshot fetch time is excluded from proposal identity; the PR evidence content and full config are included.

## Events, retries and publication

Webhook/event payloads only schedule a new current fetch. Out-of-order events cannot supply older state as current. `observed_at` is the source-read observation time, not the event receive time. Single-repository observations are serialized by a lease; conflicting equal-time observations fail closed. All workers use the same private local state database. Multi-host coordination is out of scope.

The output is a proposal, not an approval, GitHub comment or published message. The reporter reads pending proposals, sends only permitted content, confirms provider readback, then passes `--ack ID`. An uncertain send must be read back before retry. Future write adapters must independently check authority, live open/non-draft state, head, current checks and latest human decisions immediately before mutation. Proposal identity alone never authorizes execution. External write actions and adapters are not implemented in this version.
