"""SQLite single-host report ledger. No external actions or distributed lock claims."""
import json
import hashlib
import sqlite3
from contextlib import contextmanager


class Ledger:
    def __init__(self, path):
        self.db = sqlite3.connect(path, isolation_level=None, timeout=10)
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS leases(repository TEXT PRIMARY KEY, owner TEXT, expires REAL);
        CREATE TABLE IF NOT EXISTS snapshots(repository TEXT PRIMARY KEY, observed REAL, digest TEXT);
        CREATE TABLE IF NOT EXISTS observations(repository TEXT, number INTEGER, observed REAL,
          proposal TEXT, PRIMARY KEY(repository, number));
        CREATE TABLE IF NOT EXISTS reports(id TEXT PRIMARY KEY, payload TEXT, state TEXT);
        ''')

    @contextmanager
    def transaction(self):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            yield
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def acquire(self, repository, owner, now, ttl=60):
        if not owner or ttl <= 0:
            raise ValueError('owner and positive ttl required')
        with self.transaction():
            row = self.db.execute('SELECT owner, expires FROM leases WHERE repository=?', (repository,)).fetchone()
            if row and row[1] > now:
                return False
            self.db.execute('INSERT OR REPLACE INTO leases VALUES(?,?,?)', (repository, owner, now + ttl))
            return True

    def record(self, repository, owner, rows, now, observed_at=None):
        with self.transaction():
            lease = self.db.execute('SELECT owner, expires FROM leases WHERE repository=?', (repository,)).fetchone()
            if not lease or lease[0] != owner or lease[1] <= now:
                raise ValueError('lost or expired lease')
            observed_at = (rows[0]['observed_at'] if rows else now) if observed_at is None else observed_at
            if any(row['observed_at'] != observed_at for row in rows):
                raise ValueError('mixed snapshot observation times')
            digest = hashlib.sha256(json.dumps(sorted(row['proposal_id'] for row in rows)).encode()).hexdigest()
            previous_snapshot = self.db.execute('SELECT observed,digest FROM snapshots WHERE repository=?', (repository,)).fetchone()
            if previous_snapshot and observed_at < previous_snapshot[0]:
                self.db.execute('DELETE FROM leases WHERE repository=? AND owner=?', (repository, owner))
                return
            if previous_snapshot and observed_at == previous_snapshot[0] and digest != previous_snapshot[1]:
                raise ValueError('contradictory equal-time snapshot')
            self.db.execute('INSERT OR REPLACE INTO snapshots VALUES(?,?,?)', (repository, observed_at, digest))
            previous_rows = {n: (proposal, json.loads(payload)) for n, proposal, payload in self.db.execute(
                'SELECT o.number,o.proposal,r.payload FROM observations o JOIN reports r ON o.proposal=r.id WHERE o.repository=?', (repository,))}
            # Input is a complete repository discovery; omissions retire old pending observations.
            self.db.execute('DELETE FROM observations WHERE repository=?', (repository,))
            for source_row in rows:
                row = dict(source_row)
                evidence_id = row['proposal_id']
                row['evidence_id'] = evidence_id
                prior = previous_rows.get(row['number'])
                if prior and prior[1].get('evidence_id', prior[0]) == evidence_id:
                    row['proposal_id'] = prior[0]
                elif self.db.execute('SELECT 1 FROM reports WHERE id=?', (evidence_id,)).fetchone():
                    row['proposal_id'] = hashlib.sha256((evidence_id + ':' + str(observed_at)).encode()).hexdigest()
                self.db.execute('INSERT OR REPLACE INTO observations VALUES(?,?,?,?)', (repository, row['number'], row['observed_at'], row['proposal_id']))
                self.db.execute('INSERT INTO reports VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload', (row['proposal_id'], json.dumps(row, sort_keys=True), 'pending'))
            self.db.execute('DELETE FROM leases WHERE repository=? AND owner=?', (repository, owner))

    def pending(self, repository=None):
        # Old pending proposals become obsolete when newer evidence arrives.
        return [json.loads(row[0]) for row in self.db.execute('''SELECT r.payload FROM reports r
          JOIN observations o ON o.proposal=r.id WHERE r.state='pending' AND (? IS NULL OR o.repository=?) ORDER BY o.repository,o.number''', (repository, repository))]

    def acknowledge(self, proposal_id, repository=None):
        self.db.execute("UPDATE reports SET state='reported' WHERE id=? AND id IN (SELECT proposal FROM observations WHERE ? IS NULL OR repository=?)", (proposal_id, repository, repository))

    def close(self):
        self.db.close()
