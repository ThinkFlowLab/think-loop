# Policy evaluator

Implementation: `think_loop/core.py`. Input: contract v0.1 config + complete fresh snapshot. Output: ordered per-PR proposals.

Invariants: closed/draft/ineligible items cannot become ready; missing evidence is unknown; unresolved human concerns remain blocking; configured checks require exact-head executed success; substantive analysis and a trusted non-author approval must bind the same head. All normalized evidence and policy content are part of the proposal digest, because discussion/checks can change without commits.

Check providers and review aggregation are adapter responsibilities. Historical approvals must not be passed as effective approvals. See [contract](../adapter-contract.md).

Test entry: `python -m unittest discover -s tests -v`. No model, GPU, transport or production accuracy is tested. Diagnostic CI classification intentionally remains code/infra unknown until logs establish causality.
