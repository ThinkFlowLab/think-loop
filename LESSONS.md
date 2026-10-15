# Lessons

This is a small index of actionable, test-backed lessons, not a transcript archive. The initial cases below are synthetic design fixtures, not claims of observed production incidents.

| Case | Failure mode | Prevention / regression |
| --- | --- | --- |
| stale-head | Prior checks/analysis accidentally clear a new commit | Match each evidence head; `test_stale_check_unknown`, `test_stale_head_invalidates_analysis` |
| unknown-page | Partial discovery interpreted as no backlog | Reject incomplete pages/API errors; `test_partial_pagination_rejected`, `test_api_error_not_empty` |
| duplicate-delivery | Repeated event publishes duplicate report | Stable proposal ID and explicit acknowledgement; `test_duplicate_replay_and_explicit_ack` |
| out-of-order | Late old snapshot overwrites newer evidence | Monotonic observed time; conflicting equal-time snapshots fail; ordering fixtures |
| crash-window | Printed report incorrectly counted as delivered | Pending reports survive restart; `test_crash_recovery_replays_unacknowledged` |

Add adjudicated project cases using [the lesson record](templates/LESSON.md). Each record needs source revision, scenario, expected/actual behavior, prevention test, scope and an owner to re-evaluate obsolete advice. Production sample size: **0**. Synthetic replay coverage is not an accuracy estimate.
