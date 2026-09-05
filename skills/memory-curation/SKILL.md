---
name: memory-curation
description: Policy for curating durable Basic Memory knowledge: hierarchical progressive disclosure, canonical notes, live-source provenance, session evidence, and avoiding duplicate or noisy memory. Use before writing or reorganizing persistent memory, when calling write_note or edit_note, and when deciding whether notes should be created at all.
---

# Persistent memory curation

Use the upstream `memory-notes` skill for Basic Memory note syntax: frontmatter,
observations, relations, wiki links and granular edits. This skill is an overlay
on it and defines policy, not syntax.

## Purpose

Maintain a compact, durable, navigable knowledge graph with a clear tree spine.
Memory is not a transcript archive.

## Before writing

1. Search for an existing canonical note.
2. Prefer updating it over creating a near-duplicate.
3. Find the narrowest appropriate place in the hierarchy.
4. Split independently useful subtopics into child nodes.
5. Write nothing when the session produced no durable knowledge.

## Hierarchy

The filesystem/tree is the primary navigation spine.

- Every knowledge node has one canonical conceptual parent, except roots.
- A branch/index note contains:
  - a short orientation paragraph;
  - only durable high-level distinctions;
  - links/relations to child nodes.
- Details belong in children.
- There is no fixed number of levels.
- A node may be arbitrarily deep.
- Cross-cutting concepts use relations instead of duplicated prose.

Do not recursively load a subtree merely because one node matched.
Search directly when the question is specific; use the hierarchy when
orientation or progressive zoom is useful.

## Live information

Do not copy information that is cheap and safer to obtain from a live
authoritative source.

A memory may retain a small durable concept that teaches the agent:

- what the source contains;
- why it matters;
- when to consult it;
- how to find/query it.

Examples of information that should usually stay live:

- repository inventories and counts;
- current versions/releases;
- current API/reference documentation;
- issue/PR status;
- mutable deployment state.

## Sources

Attach provenance at the lowest knowledge node whose claims it supports.
Do not propagate descendant sources into parent/index notes.

Source preference:

1. current source code, repository, commit, specification or authoritative docs;
2. other authoritative external sources;
3. OpenCode session evidence only when the session contains unique reasoning,
   experiment results, logs, or decisions not preserved elsewhere.

If a session merely discovered an external source, cite the external source,
not the session.

For session-derived evidence:

- create a source/evidence child note only when useful;
- retain selected relevant excerpts, not the whole session;
- record session ID and the developer identity;
- treat the session as secondary provenance because it may later be deleted.

Call the `memory_session_context` tool at that point, and only at that point, to
get the session ID, the configured author and the current checkout instead of
guessing them. It is a provenance lookup, not a routine step: skip it when
nothing session-derived is being recorded.

## Shared knowledge

Assume shared/company knowledge may be read by other developers and agents.
Do not rely on a private local OpenCode session being available to them.

Session source notes therefore need enough selected evidence to stand alone.
The session ID is a forensic pointer, not the only copy of the evidence.

## Security

Never infer that content is safe to publish because its note says
`public_candidate: true`.

Security boundaries are repositories/projects plus human review.
