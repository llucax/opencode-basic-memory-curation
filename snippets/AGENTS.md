<!-- Paste this section into your own AGENTS.md by hand; nothing installs it for you. -->

## Persistent knowledge

Basic Memory holds durable curated knowledge and a separate local activity
index.

- For recent or ongoing work, search project `activity-local` FIRST with
  `note_types=["activity"]`, `after_date="7d"`, and `page_size=20`.
- Activity bodies are one short summary sentence. Read several, but DO NOT read
  continuity children unless one relevant effort needs details.
- `activity-local` is an operational exception to durable-memory policy. Follow
  its README and do not load `memory-curation` merely to list or update it.
- For a user-owned top-level session, call `memory_session_context` once after
  its purpose is clear and maintain its activity plus continuity nodes using
  `~/basic-memories/activity-local/README.md`. A `W:` worker does not record
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
