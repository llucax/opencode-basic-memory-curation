# Recording activity and continuity records

Policy for what belongs in these records, their required frontmatter fields,
and retention lives in `~/basic-memories/activity-log/README.md`; that file
is the authority for content. This page is the CLI mechanics for creating and
updating the two nodes it describes:

```text
sessions/YYYY/MM/<session-id>/index.md
sessions/YYYY/MM/<session-id>/continuity/index.md
```

Call `memory_session_context` once, after the session's purpose is clear, to
get the real session ID, author, and directory rather than guessing.

## Creating both nodes

Both nodes need the exact `index.md` layout, so both use the two-command
recipe from `references/editing.md`. First the activity parent:

```sh
bm tool write-note --project activity-log --title index --type activity \
  --folder "sessions/YYYY/MM/<session-id>" <<'EOF'
---
permalink: sessions/YYYY/MM/<session-id>
session_id: <session-id>
session_author: <author>
started_at: "<ISO 8601 UTC>"
last_active_at: "<ISO 8601 UTC>"
status: active
directory: <working directory>
continuity: sessions/YYYY/MM/<session-id>/continuity
---

# <real title>

One sentence.
EOF

bm tool edit-note --project activity-log "sessions/YYYY/MM/<session-id>" \
  --operation find_replace --find-text "title: index" \
  --content "title: <real title>"
```

Then the continuity child, same recipe, one folder level deeper:

```sh
bm tool write-note --project activity-log --title index --type continuity \
  --folder "sessions/YYYY/MM/<session-id>/continuity" <<'EOF'
---
permalink: sessions/YYYY/MM/<session-id>/continuity
session_id: <session-id>
session_author: <author>
started_at: "<ISO 8601 UTC>"
last_active_at: "<ISO 8601 UTC>"
status: active
directory: <working directory>
---

# Continuity for <real title>

Mission, decisions, blockers, next steps. Never a transcript or command log.
EOF

bm tool edit-note --project activity-log "sessions/YYYY/MM/<session-id>/continuity" \
  --operation find_replace --find-text "title: index" \
  --content "title: Continuity for <real title>"
```

Verify each with `bm tool read-note --project activity-log "<permalink>"
--json --frontmatter` and confirm `file_path` ends in `index.md`. Do not use
`bm doctor --local` as that verification: it creates its own throwaway
project (`doctor-<random>`), round-trips a file through only that project,
and deletes it again, so it never looks at `activity-log` or the record you
just wrote.

## Later updates

Use `bm tool edit-note --project activity-log "<permalink>" --operation
find_replace ...` for any later field or content change, on either node.
Because `find_replace` reaches into frontmatter, the same operation updates
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
