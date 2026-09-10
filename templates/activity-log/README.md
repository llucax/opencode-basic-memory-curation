---
title: OpenCode activity log
type: note
permalink: activity-log/readme
---

# OpenCode activity log

This private Basic Memory project is a permanent compact log of top-level
OpenCode sessions and their continuity. It is operational history, not
canonical durable knowledge. A private Git remote may back it up, but it must
never be public, team-shared, or synchronized through Basic Memory cloud.

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

For recent context, search `activity-log` first with `note_types=["activity"]`,
`after_date="7d"`, and `page_size=20`. Reading all returned activity bodies is
safe because each is one sentence. Do not read continuity children by default.

Read one exact continuity child only when resuming that effort or when its
details are needed. Use OpenCode history only when the selected activity and
continuity notes do not contain enough information, or when exact session
evidence is required.

For historical questions, select `type: activity` records from the requested
year or month and read their one-sentence summaries first. Read only the
continuity children needed to add detail.

Activity and continuity are routing hints. Verify repository, branch, worker,
PR, issue, and deployment state live before acting.

## Recording

Call `memory_session_context` once after a top-level session's purpose is clear.
Select `activity-log` explicitly on every Basic Memory call. Create each node
through `write_note` in its intended directory, with the exact stable permalink
in the content's opening frontmatter. Do not pass it through the `metadata`
argument, which ignores `permalink`. Then use MCP `move_note` to place the
indexed note at its final `index.md` destination and use `read_note` to confirm
the returned `file_path`. Repeat for the parent and continuity child.

Use `edit_note` for every later content or metadata update and `delete_note` for
deletion. The CLI does not currently expose `move_note`, so creation in this
layout requires MCP. If the required tool is unavailable, defer the record;
never create, edit, move, or delete a file in this project through raw
filesystem tools.

A Git operation that changes Markdown, or an explicitly approved bulk
migration, is the only direct-mutation exception. Immediately run
`bm reindex --project activity-log --full` and `bm doctor --local` afterward.

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

When a finished session resumes, set its status back to `active`. Once it is
finished again, keep the completed record unchanged except to correct a factual
error; do not rewrite historical state to match the present.

Durable decisions, recurring failure modes, and reusable lessons belong in a
canonical note in `personal` or the relevant shared knowledge project. Link to
them from continuity instead of duplicating them here.

## Retention

`last_active_at` records when the work changed; it is not an accuracy review.
Retain activity and continuity records permanently. Default recall still covers
only seven days, and older records must not appear without a more specific
historical query. Git commits and pushes are backup checkpoints, not part of
per-session recording. Before considering a record complete, run the installed
layout checker and `bm doctor --local`; both must pass.
