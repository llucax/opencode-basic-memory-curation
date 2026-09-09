---
title: Local OpenCode activity
type: note
permalink: activity-local/readme
---

# Local OpenCode activity

This local-only Basic Memory project is a compact index of recent top-level
OpenCode sessions and their continuity. It is operational state, not durable
knowledge, and must never be synchronized or published.

## Record shape

Each recorded session has two nodes:

```text
sessions/YYYY/MM/<session-id>/index.md
sessions/YYYY/MM/<session-id>/continuity/index.md
```

The parent has `type: activity` and exactly one short summary sentence. Its
title and sentence answer only what the session is about. Detailed state,
decisions, blockers, workers, and next steps belong in the `type: continuity`
child.

Record user-owned and manager sessions. Do not create one record per worker;
the parent manager's continuity can reference workers when needed.

## Recall

For recent context, search `activity-local` first with `note_types=["activity"]`,
`after_date="7d"`, and `page_size=20`. Reading all returned activity bodies is
safe because each is one sentence. Do not read continuity children by default.

Read one exact continuity child only when resuming that effort or when its
details are needed. Use OpenCode history only when the selected activity and
continuity notes do not contain enough information, or when exact session
evidence is required.

Activity and continuity are routing hints. Verify repository, branch, worker,
PR, issue, and deployment state live before acting.

## Recording

Call `memory_session_context` once after a top-level session's purpose is clear.
Create the two `index.md` files directly because `write_note` derives filenames
from titles. Let Basic Memory index the filesystem changes, then wait for sync
before testing recall.

The activity parent carries `session_id`, `session_author`, `started_at`,
`last_active_at`, `status`, `directory`, and `continuity`. Update its single
sentence only when the session's overall purpose or result changes.

The continuity child carries the same identity and status fields. Keep enough
detail to resume without replaying history, but never copy a transcript,
command log, or hidden reasoning.

Use UTC ISO 8601 timestamps and one of these statuses: `active`, `blocked`,
`complete`, or `superseded`. An imported historical record may use `YYYY-MM-DD`
when no exact time survives; never manufacture precision. The parent
`continuity` value is the exact permalink of its child. Titles must remain
unique across the project.

Durable decisions, recurring failure modes, and reusable lessons belong in a
canonical note in `personal` or the relevant shared knowledge project. Link to
them from continuity instead of duplicating them here.

## Age

`last_active_at` records when the work changed; it is not an accuracy review.
Default recall covers seven days. Explicit recent-work searches may cover 30
days. Completed or superseded records may be deleted after 30 days. Active or
blocked records may remain for 90 days, but must not appear in default recall
after seven days without a more specific query.

OpenCode history remains the forensic record after an activity record expires.
