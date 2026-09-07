---
name: memory-curation
description: How to write, structure, size and retrieve durable Basic Memory knowledge: note syntax, the index.md file layout, observation-first search, live-source provenance, session evidence, and deciding whether a note should exist at all. Use before writing, editing, reorganising or searching persistent memory, and when calling write_note, edit_note or search_notes.
---

# Persistent memory

The whole policy for these Basic Memory knowledge bases: what to write, how to
shape it, and how to get it back.

This replaces the upstream `memory-notes` skill. That skill's text is kept for
rare syntax questions at `~/.config/opencode/skills/memory-notes/REFERENCE.md`,
renamed so the loader ignores it, with its provenance in `UPSTREAM.md` beside
it. Where the two disagree, notably on note length, this one wins. The reason
is measured under "Size".

## Purpose

Maintain a compact, durable, navigable knowledge graph with a clear tree spine.
Memory is not a transcript archive, and it is not a second copy of
documentation.

## Before writing

1. Search for an existing canonical note.
2. Prefer updating it over creating a near-duplicate.
3. Find the narrowest appropriate place in the hierarchy.
4. Split independently useful subtopics into child nodes.
5. Write nothing when the session produced no durable knowledge.

## What must never become a note

Name the reader and the moment before writing. If the fact will already be in
that agent's context at that moment, writing it down is duplication that can
only drift.

Never memorise:

- anything in a global or repository `AGENTS.md`. Those are auto-loaded, so the
  agent already has them exactly when they apply;
- anything in a skill that will be loaded for the task;
- anything you just wrote into a repository file in this same session. Putting
  a rationale in a repo's `AGENTS.md` and also in memory is one fact in two
  places, and the repo is the authoritative one;
- information trivially visible in the current README or source;
- what happened in a session, command history, or mutable status.

Worth persisting: a durable decision and its rationale, a recurring non-obvious
failure mode, an expensive-to-rediscover fact, a stable preference, or a
durable pointer to a live source.

Do not invent conventions. No new frontmatter keys, banners or section headings
the project does not already use; if a note seems to need one, ask. Never stamp
a note with an "AI-generated" banner: no project here does that, `reviewed_at`
and Git authorship already record it, and it is wrong the moment a human reads
the note.

## Note anatomy

```markdown
---
title: Frequenz Python API client wrapping
type: note
permalink: frequenz/arch/api/client/python
reviewed_at: 2026-09-06
tags: [api, python]
---

# Frequenz Python API client wrapping

One or two sentences of orientation. What this is and when it matters.

## Observations
- [decision] Wrap protobuf types at the client boundary #api
- [constraint] Never expose generated stubs to callers

## Sources

- [`frequenz-client-base`](https://github.com/frequenz-floss/frequenz-client-base)
  - authoritative for: the wrapping conventions themselves
  - consult live when: implementing or reviewing a client

## Relations
- part_of [[Frequenz API architecture]]
```

`title` must be unique across the project. `classification` and
`public_candidate` belong to **shared** projects only, where they queue notes
for an eventual public split; they carry no information in a project that is
never shared, and `public_candidate` is explicitly not a security control.
Follow what the project already does.

Observations are `- [category] fact #tag`. Categories are free-form; be
consistent within a project. One fact per line, specific enough to be useful
alone, because that line is what search returns.

Relations are `- relation_type [[Target Title]]`. Common types here: `part_of`,
`relates_to`, `source`, `evidence_for`, `depends_on`, `contrasts_with`,
`replaces`. A `[[wiki link]]` anywhere in the prose also creates an edge.

## Size

Basic Memory indexes a note as one `entity` row holding the **entire body**,
plus one row per observation and relation. A search hit returns that whole body
in its `content` field. Measured on a nine-note base: a default search returned
31,706 characters, roughly 8k tokens, and 79% of a large note's indexed bytes
were the single whole-body row. `page_size` caps how many results come back,
not how big they are.

So the body is a cost paid on every match, and length buys almost no
discoverability, because observations are indexed as their own rows regardless.

Keep the body to a couple of sentences of orientation. Put the durable facts in
observations and the full explanation in the source. A body beyond roughly 200
words means the story belongs somewhere else; a note beyond that is a signal to
move content into a source, not to split hairs about wording.

## Retrieval

Observations are the progressive-disclosure layer; the body is the full story.
Search accordingly.

When you want a rule, decision or conclusion, search observations first:

```
search_notes(query="...", entity_types=["observation"])
```

On the same corpus this returned 11,728 characters instead of 31,706, a 63%
saving, and what came back was exactly the decisions rather than the essays
around them. Read the full note only when the fact alone is not enough.

Do not recursively load a subtree merely because one node matched. Search
directly when the question is specific; use the hierarchy when orientation or
progressive zoom is useful.

## Hierarchy

The filesystem tree is the primary navigation spine.

- Every knowledge node has one canonical conceptual parent, except roots.
- A branch/index note holds a short orientation paragraph, the durable
  high-level distinctions, and links to its children.
- Details belong in children. Depth is unlimited.
- Cross-cutting concepts use relations instead of duplicated prose.

## File layout

The tree is literal: every knowledge node is a directory holding an `index.md`.

```text
topic/
├── index.md
├── child-a/
│   ├── index.md
│   └── child-a1/
│       └── index.md
└── child-b/
    ├── index.md
    └── sources/
        └── opencode-<author>-ses_<id>.md
```

Exactly two things are exempt: a project's root `README.md`, and session
evidence under `sources/`. Each node's `permalink` equals its conceptual path,
with no project-name prefix.

### write_note cannot produce this layout

`write_note` derives the filename from the title and has no filename parameter,
so it always writes `<Title>.md` and never `index.md`. Calling it and moving on
is the most common way this layout gets broken, and the mistake is invisible
until someone lists the directory.

Create a node by writing `<path>/index.md` directly with the `write` tool,
frontmatter included. Basic Memory's watcher indexes it within a few seconds;
confirm with `bm status` or a search. `edit_note` works normally afterwards.
`write_note` is only safe if you immediately move the file and fix the
permalink by hand, which `move_note` does not do for you.

### Verify before saying you are done

```sh
python3 ~/.config/opencode/skills/memory-curation/scripts/check-layout.py
```

It validates filenames, permalinks, unique titles, source-note naming and
frontmatter across every project under `~/basic-memories/`, and exits non-zero
on a structural error. Advised keys are enforced per project: a project is held
to a key only if it already uses it somewhere. A non-zero exit means the work
is not finished.

## Live information

Do not copy information that is cheap and safer to obtain from a live
authoritative source. A note may retain a small durable concept teaching what
the source contains, why it matters, when to consult it, and how to query it.

Usually stays live: repository inventories and counts, current versions,
current API documentation, issue and PR status, mutable deployment state.

## Freshness

`reviewed_at` (frontmatter, `YYYY-MM-DD`) marks when a person or agent last
read the whole note and judged it accurate. A trailing
`(<source>, checked YYYY-MM-DD)` on an observation marks when that claim was
last verified. Only claims restating mutable state need a checked date. Basic
Memory's `updated_at` is file mtime, not a freshness signal.

A claim past its horizon, roughly three months for things that change, is a
hint to re-check, not evidence that it is wrong. With no live source to check
against, say so or ask Luca rather than assuming, and update the date only once
confirmed.

## Sources

Attach provenance at the lowest node whose claims it supports. Do not propagate
descendant sources up into parent or index notes.

Preference order: current source code, repository, commit, specification or
authoritative docs; then other authoritative external sources; then OpenCode
session evidence, only when the session holds unique reasoning, experiment
results, logs or decisions preserved nowhere else. If a session merely
discovered an external source, cite that source, not the session.

Record live sources as a `## Sources` section saying what each is authoritative
for and when to read it, as in the anatomy example above. Pin a commit SHA when
a decision depends on a specific historical state.

Session evidence is a file of its own under the node it supports, never an
observation on the parent:

```text
<concept>/sources/opencode-<author>-ses_<session-id>.md
```

```yaml
title: Evidence for <what it establishes>
type: source
permalink: <concept>/sources/opencode-<author>-ses_<session-id>
source_type: opencode-session
session_id: ses_...
session_author: llucax
captured_at: 2026-08-25
availability: local-to-author
```

Call `memory_session_context` at that point, and only then, to get the session
ID, author and checkout rather than guessing. It is a provenance lookup, not a
routine step.

## Shared knowledge

Assume shared knowledge may be read by other developers and agents; do not rely
on a private local session being available to them. Session source notes need
enough selected evidence to stand alone. The session ID is a forensic pointer,
not the only copy.

## Security

Never infer that content is safe to publish because a note says
`public_candidate: true`. Security boundaries are repositories and projects
plus human review.
