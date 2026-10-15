# Reference decisions and provenance

Primary reference inspected on 2026-10-16 (Asia/Shanghai): **yetone/magpie**, pinned at `9dd72f5bce3ae4fd43ff482e4f72fd711d3911b6`. These are source-grounded design inspirations; this template is original implementation and paraphrased guidance, not a copy of Magpie's product code.

| Verified reference | Adopted mechanism | Adaptation / limit |
| --- | --- | --- |
| [AGENTS.md](https://github.com/yetone/magpie/blob/9dd72f5bce3ae4fd43ff482e4f72fd711d3911b6/AGENTS.md) | Short routing entry to standards, subsystem design and lessons | No provider-specific migration behavior imported |
| [Code standards](https://github.com/yetone/magpie/blob/9dd72f5bce3ae4fd43ff482e4f72fd711d3911b6/docs/code-standards.md) | Whole-path review, negative controls, unknown on failed reads, isolated network-free tests, exact reviewed revision | Python checks fit this project; no Go/platform commands copied blindly |
| [Subsystem references](https://github.com/yetone/magpie/blob/9dd72f5bce3ae4fd43ff482e4f72fd711d3911b6/docs/subsystems/README.md) | Responsibilities, runtime state and contracts beside code; update docs with semantic changes | Our policy/ledger maps describe actual MVP files |
| [LESSONS.md](https://github.com/yetone/magpie/blob/9dd72f5bce3ae4fd43ff482e4f72fd711d3911b6/LESSONS.md) | Turn repeated adjudicated defects into actionable rules and regression tests | Initial cases here are synthetic; no invented production history or measured benefit |

Magpie's contributor exclusions, automatic closure decisions, product-specific policies and merge authority are not imported. These documents do not establish that Magpie supplies a reusable issue/PR scheduler or that copying them increases throughput. A runnable queue, trusted adapters, workers and measured deployment are separate engineering work.

The vLLM-Omni coordination experience informs the separation of unique first triage, readiness recheck and substantive review; evidence-bound decisions and contributor/reviewer/maintainer responsibilities. Hardware gates, quotas and particular maintainers are deliberately project configuration, not universal template policy.

## Acceptance and scope

Run the network-free unit suite, CLI replay and negative-control tests. They exercise synthetic failure and clean cases, not model review accuracy. No upstream implementation, live GitHub adapter, cloud deployment or end-to-end issue resolution was tested. A future production trial should record sample sizes, first feedback time, ready-queue waiting, rework and escaped regressions with comparable baseline cohorts.
