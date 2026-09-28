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
`memory_session_context`, then run `scripts/record-activity.py` ONCE. Do not
read the activity-log README first and do not read the notes back: the script
validates the input, writes both nodes, checks them through `bm`, and prints
either one line with both permalinks or exactly what is wrong. Trivial
sessions (smoke tests, one-off questions, read-only lookups with nothing to
resume) record nothing.

## Recording

```sh
python3 ~/.config/opencode/skills/memory-curation/scripts/record-activity.py \
  --session-id <session_id> --author <author> --directory <directory> \
  --status complete --title "<title>" \
  --summary "<exactly one sentence.>" <<'EOF'
Mission, decisions, blockers, next steps. Never a transcript or command log.
EOF
```

The three identity options are `memory_session_context`'s fields. `--status`
is the state the session leaves its work in: `complete`, `blocked`, or
`active` when more work is planned. The heredoc is the continuity body,
without frontmatter or title heading. `started_at` comes from OpenCode's
database; pass `--started-at` only if the script says it cannot find it.
`--dry-run` prints the `bm` commands without writing.

On an error, fix the input and rerun the same command; nothing is written
until validation passes. If the error says the record was written but is
wrong, rerun with `--update`.

## Later updates

Ordinary sessions do not update their records while they run. Two cases do,
and both rerun the script with `--update`, which rewrites both nodes and keeps
the recorded `started_at`:

- Manager sessions record once their purpose is clear and rerun on each
  material change, because the continuity is their compaction recovery point
  and holds running state such as the notifications-sweep tally.
- A finished session that resumes and does more work reruns once more, when
  that work is done.

The script is the only way to create or rewrite a record. For a one-field fix
on an old record, use `bm tool edit-note --project activity-log "<permalink>"
--operation find_replace ...`; `find_replace` reaches into frontmatter too.
The layout check is periodic, run by whoever commits the `activity-log` Git
repository (see its README); do not use `bm doctor --local` for it, since it
only round-trips a file through its own throwaway project.

Keep the activity parent's summary to one sentence; put everything else in
the continuity child. Reindex is not required after `edit-note`, since it
already updates the search index; it matters only after a Git operation or
bulk migration touches the Markdown directly, per `references/maintenance.md`.
