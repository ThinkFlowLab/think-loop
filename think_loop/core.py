"""Pure policy evaluation. Untrusted snapshot text is data, never instructions."""
import hashlib
import json


def validate_config(config):
    if not isinstance(config, dict):
        raise ValueError('config must be an object')
    required = {'contract_version', 'repository', 'policy_version', 'required_labels',
                'required_checks', 'trusted_reviewers', 'evidence_max_age_seconds'}
    if set(config) != required or config['contract_version'] != '0.1':
        raise ValueError('unsupported or incomplete project contract')
    if not isinstance(config['repository'], str) or (len(config['repository'].split('/')) != 2 or not all(config['repository'].split('/'))):
        raise ValueError('repository must be owner/repo')
    if not isinstance(config['policy_version'], str) or not config['policy_version']:
        raise ValueError('policy_version is required')
    for key in ('required_labels', 'required_checks', 'trusted_reviewers'):
        value = config[key]
        if not isinstance(value, list) or any(not isinstance(x, str) or not x for x in value) or len(set(value)) != len(value):
            raise ValueError('invalid ' + key)
    age = config['evidence_max_age_seconds']
    if type(age) is not int or age <= 0:
        raise ValueError('evidence_max_age_seconds must be positive integer')
    return config


def classify(pr, config):
    """Readiness is a handoff candidate, never permission to approve or merge."""
    if not isinstance(pr.get('author'), str) or not pr['author']:
        return 'unknown', 'Adapter supplies verified author identity'
    if pr.get('state') != 'open':
        return 'closed', 'No action'
    if pr.get('draft') is not False:
        return 'draft', 'Author completes the draft'
    if not set(config['required_labels']).issubset(pr.get('labels', [])):
        return 'ineligible', 'Outside configured selection'
    head = pr.get('head')
    if not isinstance(head, str) or len(head) != 40 or any(c not in '0123456789abcdef' for c in head):
        return 'unknown', 'Adapter supplies an exact current head'
    if pr.get('discussion_complete') is not True or not isinstance(pr.get('human_blockers'), list):
        return 'unknown', 'Reviewer obtains complete discussion and unresolved concerns'
    if pr['human_blockers']:
        return 'human_changes', 'Author addresses unresolved human concerns; reviewer verifies'
    if pr.get('mergeable') is False:
        return 'conflict', 'Author updates against target branch and supplies fresh checks'
    if pr.get('mergeable') is not True:
        return 'unknown', 'Adapter refreshes mergeability'
    if pr.get('checks_complete') is not True or not config['required_checks']:
        return 'unknown', 'Maintainer defines checks; adapter obtains complete current-head results'
    checks = pr.get('checks', [])
    for name in config['required_checks']:
        matches = [c for c in checks if c.get('name') == name and c.get('head') == head]
        if len(matches) != 1:
            return 'unknown', 'Adapter resolves missing, stale or duplicate required check: ' + name
        status = matches[0].get('status')
        if status == 'failure':
            return 'ci_failure_unknown', 'Reviewer diagnoses logs before assigning code or infrastructure cause'
        if status == 'pending':
            return 'ci_pending', 'Monitor current run; do not nudge contributor'
        if status != 'success':
            return 'unknown', 'Required check has no executed pass: ' + name
    if pr.get('reviews_complete') is not True:
        return 'unknown', 'Adapter obtains complete current reviews'
    actors = [r.get('actor') for r in pr.get('reviews', [])]
    if any(not isinstance(a, str) or not a for a in actors) or len(actors) != len(set(actors)):
        return 'unknown', 'Adapter resolves effective review decisions'
    if any(r.get('state') == 'changes_requested' for r in pr.get('reviews', [])):
        return 'human_changes', 'Author addresses effective human changes request'
    analysis = pr.get('analysis', {})
    if analysis.get('head') != head or analysis.get('complete') is not True:
        return 'review_needed', 'Reviewer performs substantive current-head review'
    approved = any(r.get('actor') in config['trusted_reviewers'] and r.get('actor') != pr.get('author')
                   and r.get('head') == head and r.get('state') == 'approved'
                   for r in pr.get('reviews', []))
    if not approved:
        return 'approval_needed', 'Authorized reviewer evaluates approval after a fresh boundary check'
    return 'ready_handoff', 'Maintainer verifies live state and policy before final merge decision'


def reconcile(snapshot, config, now):
    if not isinstance(snapshot, dict):
        raise ValueError('snapshot must be an object')
    validate_config(config)
    if snapshot.get('repository') != config['repository']:
        raise ValueError('snapshot repository mismatch')
    observed = snapshot.get('observed_at')
    if type(observed) not in (int, float) or not 0 <= now - observed <= config['evidence_max_age_seconds']:
        raise ValueError('snapshot stale or future-dated')
    pages = snapshot.get('pages', {})
    if not isinstance(pages, dict):
        raise ValueError('pages must be an object')
    if snapshot.get('complete') is not True or snapshot.get('errors') or pages.get('received') != pages.get('expected') or type(pages.get('expected')) is not int or pages['expected'] < 1:
        raise ValueError('incomplete discovery; preserve prior backlog')
    prs = snapshot.get('pull_requests')
    if not isinstance(prs, list):
        raise ValueError('pull_requests must be a list')
    for pr in prs:
        if not isinstance(pr, dict):
            raise ValueError('PR must be an object')
        if not isinstance(pr.get('evidence_revision'), str) or not pr['evidence_revision']:
            raise ValueError('evidence_revision required')
        for key in ('draft', 'discussion_complete', 'checks_complete', 'reviews_complete'):
            if type(pr.get(key)) is not bool:
                raise ValueError(key + ' must be boolean')
        for key in ('checks', 'reviews'):
            if not isinstance(pr.get(key, []), list) or any(not isinstance(x, dict) for x in pr.get(key, [])):
                raise ValueError(key + ' must be a list of objects')
        if not isinstance(pr.get('analysis', {}), dict) or not isinstance(pr.get('labels', []), list) or any(not isinstance(x, str) for x in pr.get('labels', [])):
            raise ValueError('invalid analysis or labels')
    ids = [p.get('number') for p in prs]
    if any(type(n) is not int or n <= 0 for n in ids) or len(ids) != len(set(ids)):
        raise ValueError('duplicate or invalid PR numbers')
    result = []
    for pr in sorted(prs, key=lambda p: p['number']):
        state, todo = classify(pr, config)
        # Hash all normalized evidence, excluding transport fetch time. Mutable evidence matters.
        identity = {'repository': config['repository'], 'policy': config, 'pr': pr}
        digest = hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        result.append({'repository': config['repository'], 'number': pr['number'], 'head': pr.get('head'), 'status': state,
                       'todo': todo, 'proposal_id': digest, 'observed_at': observed})
    return result
