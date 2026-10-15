"""Offline proposals only. Output is durable until explicitly acknowledged."""
import argparse
import json
import time
import uuid
from .core import reconcile
from .ledger import Ledger


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('--snapshot', required=True)
    parser.add_argument('--state', required=True)
    parser.add_argument('--now', type=float, default=None, help='Epoch seconds; deterministic replay only')
    parser.add_argument('--ack', action='append', default=[], help='Previously delivered proposal ID to acknowledge')
    args = parser.parse_args()
    try:
        with open(args.config, encoding='utf-8') as f:
            config = json.load(f)
        with open(args.snapshot, encoding='utf-8') as f:
            snapshot = json.load(f)
        now = time.time() if args.now is None else args.now
        rows = reconcile(snapshot, config, now)
        ledger = Ledger(args.state)
        try:
            owner = str(uuid.uuid4())
            if not ledger.acquire(config['repository'], owner, now):
                raise ValueError('another reconciliation holds the lease')
            ledger.record(config['repository'], owner, rows, time.time() if args.now is None else now, snapshot['observed_at'])
            for proposal in args.ack:
                ledger.acknowledge(proposal, config['repository'])
            print(json.dumps({'mode': 'report-only', 'proposals': ledger.pending(config['repository'])}, indent=2))
        finally:
            ledger.close()
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, 'unknown: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
