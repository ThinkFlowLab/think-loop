# Architecture

## Implemented v0.1

A trusted local project config and normalized snapshot enter the pure policy evaluator. The evaluator validates discovery coverage and freshness, then emits a deterministic status/TODO and evidence identity per PR. A SQLite ledger commits the observations and pending reports under a short single-host lease. The CLI outputs pending reports. An explicit acknowledgement marks delivered reports, allowing recovery after interrupted delivery.

| Subsystem | Responsibility | Boundary |
| --- | --- | --- |
| [Policy evaluator](docs/subsystems/policy.md) | Classification and evidence identity | No transport or writes |
| [Ledger](docs/subsystems/ledger.md) | Deduplication, ordering, leases, recovery | Local SQLite only |
| [Adapter contract](docs/adapter-contract.md) | Normalize complete authoritative evidence | Specification only |

`ready_handoff` is a suggested maintainer handoff, not permission to approve or merge. The engine cannot independently verify that an adapter is honest; trusted adapter implementation and credentials are a production prerequisite.

## Proposed production extension

Event → authenticated intake → current source refresh → normalized snapshot → reconcile → bounded plan → authorized isolated worker → tests → independent review → CI → human acceptance → lesson.

An event is a hint to fetch current state, never an authoritative snapshot. Planning and writing must be separate capabilities. A write adapter must re-fetch state/head/discussion/checks immediately before action, enforce authorization and exact-head binding, and read back uncertain outcomes before retry. Durable action identity and provider-side idempotency/readback are needed; the local report ledger does not provide exactly-once external writes.

Issue implementation workers, transport adapters, prioritization quotas, approval workflows, deployment and distributed leases are future work. Their interfaces must receive separate tests and owner authorization. See [the staged plan](docs/development-loop.md).
