<!-- Paste this section into your own AGENTS.md by hand; nothing installs it for you. -->

## Persistent knowledge

Basic Memory holds durable curated knowledge and a separate private activity
log.

- For recent or ongoing work, search project `activity-log` FIRST with
  `note_types=["activity"]`, `after_date="7d"`, and `page_size=20`.
- Activity bodies are one short summary sentence. Read several, but DO NOT read
  continuity children unless one relevant effort needs details.
- For historical questions, search the requested period in `activity-log`;
  activity and continuity records are retained permanently.
- `activity-log` is an operational exception to durable-memory policy. Follow
  its README and do not load `memory-curation` merely to list or update it.
- Use Basic Memory MCP tools or `bm tool` for normal access and every note
  mutation. Never create, edit, move, or delete files inside a registered
  Basic Memory project through raw filesystem tools.
- To create the required `index.md` layout, call `write_note` with the intended
  permalink in opening frontmatter, then MCP `move_note` to the exact
  destination, and verify it with `read_note`. If MCP is unavailable, defer
  rather than bypassing Basic Memory.
- Direct disk reads are allowed only as a read-only optimization. After a Git
  operation that changes note files or an approved bulk migration, run a full
  project reindex and `bm doctor --local`.
- For a user-owned top-level session, call `memory_session_context` once after
  its purpose is clear and maintain its activity plus continuity nodes using
  `~/basic-memories/activity-log/README.md`. A `W:` worker does not record
  itself; its parent manager aggregates it.
- Prefer activity over broad `history-search`; use history only for missing
  detail or exact session evidence.
- Do not call generic `recent_activity` at startup; it reports memory changes,
  not work.
- Recall durable memory when previous decisions, preferences, known problems,
  or investigations could materially help.
- Search narrowly first. Read the most relevant note and follow children or
  relations only when more detail is needed.
- Prefer current repository/docs state over remembered facts when they
  conflict.
- Do not duplicate live information into memory when a durable pointer to the
  authoritative source is sufficient.
- When durable knowledge is discovered or corrected, update the canonical note
  rather than putting it only in activity or continuity.
- Before creating or substantially restructuring memory, use the
  `memory-curation` skill.
