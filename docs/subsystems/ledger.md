# Local ledger

Implementation: `think_loop/ledger.py`. SQLite `BEGIN IMMEDIATE` serializes local mutation. A repository lease includes a per-attempt random owner and expiry; expired owners cannot record. Snapshot observations reject backward time and contradictory equal-time evidence. A new proposal supersedes old pending evidence; acknowledged unchanged proposals do not reappear.

Reports are pending until explicit acknowledgement. A crash before acknowledgement may repeat delivery: the consuming reporter must deduplicate by proposal_id and read back uncertain sends. This MVP guarantees local proposal deduplication, not exactly-once external delivery. Retrying an event should fetch a current snapshot, not trust its event timestamp.

The database contains project evidence and should remain in private runtime storage; never commit it. Backups, retention, distributed coordination, network filesystem safety and migrations are not implemented. Run one local host with an access-controlled SQLite file. Test entry: `python -m unittest discover -s tests -v`.

Delivery identity is transition-aware: unchanged evidence keeps its proposal ID; a material return to a previously reported state receives a new delivery ID. The evidence_id remains stable for comparison. Complete empty snapshots retire absent observations; older whole-repository snapshots cannot resurrect them.
