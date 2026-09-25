# Recording activity and continuity records

Policy for what belongs in these records, their required frontmatter fields,
and retention lives in `~/basic-memories/activity-log/README.md`; that file
is the authority for content. This page is the CLI mechanics for creating and
updating the two nodes it describes:

```text
sessions/YYYY/MM/<session-id>/index.md
sessions/YYYY/MM/<session-id>/continuity/index.md
```

Ordinary sessions record once, when their work is done: call
`memory_session_context` to get the real session ID, author, and directory
rather than guessing, then create both nodes in ONE bash call, with no
read-backs and no layout check. Trivial sessions (smoke tests, one-off
questions, read-only lookups with nothing to resume) record nothing. Manager
sessions create both nodes once their purpose is clear and keep the
continuity current; see "Later updates".

## Creating both nodes

Both nodes need the exact `index.md` layout, so both use the two-command
recipe from `references/editing.md`, and all four commands go in the same
bash call, chained with `&&`. Set `status` to the state the session leaves its
work in (`complete`, `blocked`, or `active` when more work is planned) and
both timestamps from `memory_session_context` and the current time. First the
activity parent:

```sh
bm tool write-note --project activity-log --title index --type activity \
  --folder "sessions/YYYY/MM/<session-id>" <<'EOF' &&
---
permalink: sessions/YYYY/MM/<session-id>
session_id: <session-id>
session_author: <author>
started_at: "<ISO 8601 UTC>"
last_active_at: "<ISO 8601 UTC>"
status: <complete|blocked|active>
directory: <working directory>
continuity: sessions/YYYY/MM/<session-id>/continuity
---

# <real title>

One sentence.
EOF

bm tool edit-note --project activity-log "sessions/YYYY/MM/<session-id>" \
  --operation find_replace --find-text "title: index" \
  --content "title: <real title>" &&
```

Then, in the same bash call, the continuity child, same recipe, one folder
level deeper:

```sh
bm tool write-note --project activity-log --title index --type continuity \
  --folder "sessions/YYYY/MM/<session-id>/continuity" <<'EOF' &&
---
permalink: sessions/YYYY/MM/<session-id>/continuity
session_id: <session-id>
session_author: <author>
started_at: "<ISO 8601 UTC>"
last_active_at: "<ISO 8601 UTC>"
status: <complete|blocked|active>
directory: <working directory>
---

# Continuity for <real title>

Mission, decisions, blockers, next steps. Never a transcript or command log.
EOF

bm tool edit-note --project activity-log "sessions/YYYY/MM/<session-id>/continuity" \
  --operation find_replace --find-text "title: index" \
  --content "title: Continuity for <real title>"
```

Do not read the notes back afterwards: `&&` already stops at the first failing
command, and a failure prints its error. The layout check is periodic, run by
whoever commits the `activity-log` Git repository (see its README), with `bm
tool read-note --project activity-log "<permalink>" --json --frontmatter` to
confirm a record it flags. Do not use `bm doctor --local` for either: it
creates its own throwaway project (`doctor-<random>`), round-trips a file
through only that project, and deletes it again, so it never looks at
`activity-log`.

## Later updates

Ordinary sessions do not update their records while they run. Two cases do:

- Manager sessions update their continuity on each material change, because it
  is their compaction recovery point and holds running state such as the
  notifications-sweep tally. Batch the edits for one change into a single bash
  call, with no read-backs.
- A finished session that resumes and does more work updates its records once
  more, when that work is done, in a single bash call.

Use `bm tool edit-note --project activity-log "<permalink>" --operation
find_replace ...` for any field or content change, on either node. Because
`find_replace` reaches into frontmatter, the same operation updates
`last_active_at` and `status`:

```sh
bm tool edit-note --project activity-log "sessions/YYYY/MM/<session-id>" \
  --operation find_replace --find-text "status: active" \
  --content "status: complete"
```

Keep the activity parent's summary to one sentence; put everything else in
the continuity child. Reindex is not required after `edit-note`, since it
already updates the search index; it matters only after a Git operation or
bulk migration touches the Markdown directly, per `references/maintenance.md`.
