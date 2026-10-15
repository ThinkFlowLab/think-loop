import copy
import json
from pathlib import Path
import tempfile
import unittest
from think_loop.core import reconcile, validate_config
from think_loop.ledger import Ledger

ROOT = Path(__file__).resolve().parents[1]


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / 'examples/loop.project.json').read_text())
        self.snapshot = json.loads((ROOT / 'examples/snapshot.json').read_text())
        self.pr = self.snapshot['pull_requests'][0]

    def status(self):
        return reconcile(self.snapshot, self.config, 1000)[0]['status']

    def test_ready_is_only_handoff(self):
        self.assertEqual(self.status(), 'ready_handoff')

    def test_stale_head_invalidates_analysis(self):
        self.pr['analysis']['head'] = 'b' * 40
        self.assertEqual(self.status(), 'review_needed')

    def test_stale_check_unknown(self):
        self.pr['checks'][0]['head'] = 'b' * 40
        self.assertEqual(self.status(), 'unknown')

    def test_skipped_not_pass(self):
        self.pr['checks'][0]['status'] = 'skipped'
        self.assertEqual(self.status(), 'unknown')

    def test_missing_check_policy_unknown(self):
        self.config['required_checks'] = []
        self.assertEqual(self.status(), 'unknown')

    def test_partial_pagination_rejected(self):
        self.snapshot['pages']['expected'] = 2
        with self.assertRaises(ValueError):
            self.status()

    def test_api_error_not_empty(self):
        self.snapshot['errors'] = ['rate limited']
        with self.assertRaises(ValueError):
            self.status()

    def test_duplicate_pr_rejected(self):
        self.snapshot['pull_requests'].append(copy.deepcopy(self.pr))
        with self.assertRaises(ValueError):
            self.status()

    def test_stale_or_future_snapshot_rejected(self):
        for timestamp in (0, 1001):
            self.snapshot['observed_at'] = timestamp
            with self.assertRaises(ValueError):
                self.status()

    def test_human_concern_preserved(self):
        self.pr['human_blockers'] = ['unresolved review']
        self.assertEqual(self.status(), 'human_changes')

    def test_own_approval_not_valid(self):
        self.pr['author'] = 'reviewer'
        self.assertEqual(self.status(), 'approval_needed')

    def test_labels_and_drafts(self):
        self.config['required_labels'] = ['high priority', 'ready']
        self.assertEqual(self.status(), 'ineligible')
        self.pr['labels'] = ['high priority', 'ready']
        self.pr['draft'] = True
        self.assertEqual(self.status(), 'draft')

    def test_old_pr_new_head_not_excluded(self):
        self.pr['created_at'] = '2020-01-01'
        self.assertEqual(self.status(), 'ready_handoff')
        first = reconcile(self.snapshot, self.config, 1000)[0]['proposal_id']
        self.pr['head'] = 'c' * 40
        self.assertNotEqual(reconcile(self.snapshot, self.config, 1000)[0]['proposal_id'], first)

    def test_same_head_new_check_changes_identity(self):
        first = reconcile(self.snapshot, self.config, 1000)[0]['proposal_id']
        self.pr['checks'][0]['status'] = 'pending'
        self.assertNotEqual(reconcile(self.snapshot, self.config, 1000)[0]['proposal_id'], first)
        self.assertEqual(self.status(), 'ci_pending')

    def test_missing_author_unknown(self):
        del self.pr['author']
        self.assertEqual(self.status(), 'unknown')

    def test_duplicate_effective_actor_unknown(self):
        self.pr['reviews'].append(dict(self.pr['reviews'][0], state='changes_requested'))
        self.assertEqual(self.status(), 'unknown')

    def test_changes_requested_blocks(self):
        self.pr['reviews'][0]['state'] = 'changes_requested'
        self.assertEqual(self.status(), 'human_changes')

    def test_bad_nested_input_rejected(self):
        self.pr['analysis'] = []
        with self.assertRaises(ValueError):
            self.status()

    def test_invalid_config(self):
        self.config['contract_version'] = 'future'
        with self.assertRaises(ValueError):
            validate_config(self.config)


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / 'examples/loop.project.json').read_text())
        self.snapshot = json.loads((ROOT / 'examples/snapshot.json').read_text())
        self.temp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.temp.name) / 'state.sqlite')
        self.ledger = Ledger(self.path)
        self.rows = reconcile(self.snapshot, self.config, 1000)

    def tearDown(self):
        self.ledger.close()
        self.temp.cleanup()

    def record(self, rows=None, now=1000):
        self.assertTrue(self.ledger.acquire(self.config['repository'], 'a', now))
        self.ledger.record(self.config['repository'], 'a', self.rows if rows is None else rows, now)

    def test_duplicate_replay_and_explicit_ack(self):
        self.record()
        self.record()
        self.assertEqual(len(self.ledger.pending()), 1)
        self.ledger.acknowledge(self.rows[0]['proposal_id'])
        self.record()
        self.assertEqual(self.ledger.pending(), [])

    def test_out_of_order_ignored(self):
        self.record()
        stale = copy.deepcopy(self.rows)
        stale[0].update(observed_at=999, proposal_id='old')
        self.record(stale)
        self.assertEqual(self.ledger.pending()[0]['proposal_id'], self.rows[0]['proposal_id'])

    def test_equal_time_conflict_rolls_back(self):
        self.record()
        altered = copy.deepcopy(self.rows)
        altered[0]['proposal_id'] = 'contradiction'
        with self.assertRaises(ValueError):
            self.record(altered)
        self.assertEqual(self.ledger.pending()[0]['proposal_id'], self.rows[0]['proposal_id'])

    def test_lease_exclusion_and_expiry(self):
        repo = self.config['repository']
        self.assertTrue(self.ledger.acquire(repo, 'a', 1000, 10))
        self.assertFalse(self.ledger.acquire(repo, 'b', 1001))
        self.assertTrue(self.ledger.acquire(repo, 'b', 1011))
        with self.assertRaises(ValueError):
            self.ledger.record(repo, 'a', self.rows, 1011)
        self.ledger.record(repo, 'b', self.rows, 1011)

    def test_crash_recovery_replays_unacknowledged(self):
        self.record()
        self.ledger.close()
        self.ledger = Ledger(self.path)
        self.assertEqual(len(self.ledger.pending()), 1)

    def test_complete_empty_retires_old_proposals(self):
        self.record()
        self.record([], 1001)
        self.assertEqual(self.ledger.pending(), [])
        self.record(self.rows, 1002)
        self.assertEqual(self.ledger.pending(), [])

    def test_refresh_updates_payload_time(self):
        self.record()
        newer = copy.deepcopy(self.rows)
        newer[0]['observed_at'] = 1001
        self.record(newer, 1001)
        self.assertEqual(self.ledger.pending()[0]['observed_at'], 1001)

    def test_pending_scoped_to_repository(self):
        self.record()
        self.assertEqual(self.ledger.pending('other/repo'), [])
        self.ledger.acknowledge(self.rows[0]['proposal_id'], 'other/repo')
        self.assertEqual(len(self.ledger.pending()), 1)

    def test_recurrence_gets_new_delivery_identity(self):
        self.record()
        original = self.ledger.pending()[0]['proposal_id']
        self.ledger.acknowledge(original)
        changed = copy.deepcopy(self.rows)
        changed[0].update(observed_at=1001, proposal_id='different')
        self.record(changed, 1001)
        restored = copy.deepcopy(self.rows)
        restored[0]['observed_at'] = 1002
        self.record(restored, 1002)
        returned = self.ledger.pending()[0]
        self.assertNotEqual(returned['proposal_id'], original)
        self.assertEqual(returned['evidence_id'], original)
        self.record(restored, 1002)
        self.assertEqual(len(self.ledger.pending()), 1)

    def test_newer_evidence_supersedes_pending(self):
        self.record()
        newer = copy.deepcopy(self.rows)
        newer[0].update(observed_at=1001, proposal_id='new')
        self.record(newer, 1001)
        self.assertEqual([p['proposal_id'] for p in self.ledger.pending()], ['new'])


if __name__ == '__main__':
    unittest.main()
