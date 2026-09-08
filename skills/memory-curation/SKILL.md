---
name: memory-curation
description: How to write, structure, size and retrieve durable Basic Memory knowledge: note syntax, the index.md file layout, observation-first search, live-source provenance, session evidence, and deciding whether a note should exist at all. Use before writing, editing, reorganising or searching persistent memory, and when calling write_note, edit_note or search_notes.
---

# Persistent memory

Policy for the Basic Memory knowledge bases under `~/basic-memories/`.

Replaces the upstream `memory-notes` skill, kept for syntax questions at
`~/.config/opencode/skills/memory-notes/REFERENCE.md`. Where they disagree,
THIS ONE WINS.

## Before writing

1. Search for an existing canonical note.
2. UPDATE IT rather than creating a near-duplicate.
3. Place it at the narrowest appropriate node.
4. Split independently useful subtopics into children.
5. WRITE NOTHING when the session produced no durable knowledge. That is a
   normal outcome, not a missed one.

## What must never become a note

Name the reader and the moment. If the fact will ALREADY BE IN THAT AGENT'S
CONTEXT then, DO NOT WRITE IT.

NEVER memorise:

- anything in a global or repository `AGENTS.md`; those are auto-loaded;
- anything in a skill that will load for the task;
- anything you wrote into a repository this session; THE REPO IS AUTHORITATIVE;
- anything visible in the current README or source;
- session narrative, command history, or mutable status.

DO persist: durable decisions and their rationale, recurring non-obvious
failure modes, expensive-to-rediscover facts, stable preferences, durable
pointers to live sources.

DO NOT invent conventions. No frontmatter keys, banners or headings the project
does not already use; ASK instead. NEVER add an "AI-generated" banner.

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

`title` MUST be unique within the project. It is what `[[wiki links]]` resolve
on and what search results show, so it MUST also stand alone: carry enough
scope to be unambiguous without its path (`Frequenz dispatch flow`, not
`Dispatch`).

DO NOT restate the permalink in the title. The path is already in the
permalink, and a title tied to the path has to change whenever the note moves,
BREAKING EVERY WIKI LINK to it.

CHECK THE CANDIDATE BEFORE WRITING, since a collision found later may already
have links pointing at it:

```sh
bm tool search-notes "<candidate title>" --title --plain --project <project>
```

`0 result(s)` means free. Any hit is a collision or a near-duplicate; pick a
different title, or reconsider whether you should be updating that note.

Observations are `- [category] fact #tag`. ONE FACT PER LINE, specific enough
to stand alone: that line is what search returns. Categories are free-form, but
be consistent within a project.

Relations are `- relation_type [[Target Title]]`. A `[[wiki link]]` in prose
also creates an edge. Common types: `part_of`, `relates_to`, `source`,
`evidence_for`, `depends_on`, `contrasts_with`, `replaces`.

`classification` and `public_candidate` are for SHARED projects only. Follow
what the project already does.

## Size

KEEP THE BODY SHORT: a couple of sentences of orientation, 200 words MAX.
Durable facts go in observations, the full explanation goes in the source. A
longer body means the content belongs somewhere else.

## Retrieval

DISCOVER FIRST, THEN READ.

Discover with the CLI:

```sh
bm tool search-notes "..." --project <project> --plain
```

DO NOT add `--entity-type observation` to save output; IT DOES NOT. Use it only
when you want the decisions themselves rather than the notes holding them.
Without shell access, use `search_notes(query="...",
entity_types=["observation"])`.

Read the chosen note FROM DISK, not through a tool. Permalink `a/b/c` in
project `p` is `~/basic-memories/p/a/b/c/index.md`; the only exception is a
project's root `README.md`. Use offset and limit on long notes, and `rg` over
`~/basic-memories/` for literal search.

DO NOT load a subtree merely because one node matched.

## Layout

EVERY node is a directory holding an `index.md`, and its `permalink` EQUALS its
conceptual path, with NO project-name prefix.

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

Exactly two exemptions: a project's root `README.md`, and session evidence
under `sources/`.

Index notes hold orientation, the high-level distinctions, and links to
children. Details go in children; depth is unlimited. Cross-cutting concepts
use relations, NEVER duplicated prose.

NEVER create a node with `write_note`. It derives the filename from the title
and has no filename parameter, so it always writes `<Title>.md`, never
`index.md`. WRITE `<path>/index.md` DIRECTLY with the `write` tool, frontmatter
included. `edit_note` is fine afterwards.

BEFORE saying you are done:

```sh
python3 ~/.config/opencode/skills/memory-curation/scripts/check-layout.py
```

NON-ZERO EXIT MEANS NOT FINISHED.

## Live information

DO NOT copy what is cheap and safer to read live: repository inventories and
counts, current versions, current API documentation, issue and PR status,
mutable deployment state. Keep only a durable concept saying what the source
holds, why it matters, when to consult it, and how to query it.

## Freshness

- `reviewed_at` (`YYYY-MM-DD`): when the whole note was last read and judged
  accurate.
- `(<source>, checked YYYY-MM-DD)` on an observation: when that claim was last
  verified. ONLY for claims restating mutable state.
- `updated_at` is file mtime, NOT a freshness signal.

Past its horizon, roughly three months for volatile things, means RE-CHECK, not
wrong. With no live source to check against, SAY SO OR ASK. Update the date
ONLY once confirmed.

## Sources

Attach provenance at the LOWEST node whose claims it supports. NEVER propagate
descendant sources up into parent or index notes.

Preference order: current source code, repository, commit, specification or
authoritative docs; then other authoritative external sources; then opencode
session evidence, ONLY when the session holds reasoning, experiment results,
logs or decisions preserved nowhere else. If a session merely discovered an
external source, CITE THAT SOURCE, not the session.

Pin a commit SHA when a decision depends on a specific historical state.

Session evidence is a file of its own under the node it supports, NEVER an
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

Call `memory_session_context` AT THAT POINT AND ONLY THEN, to get the session
ID, author and checkout rather than guessing. It is a provenance lookup, NOT a
routine step.

## Shared knowledge

Assume other developers and agents will read shared projects, and that a
private local session is UNAVAILABLE to them. Session source notes MUST carry
enough selected evidence to stand alone. The session ID is a forensic pointer,
not the only copy.

## Security

NEVER infer that content is safe to publish because a note says
`public_candidate: true`. Security boundaries are repositories and projects
plus human review.
