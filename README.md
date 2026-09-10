# opencode-basic-memory-curation

Curation policy, compact activity recall, and provenance support for using
[Basic Memory](https://github.com/basicmachines-co/basic-memory) in
[opencode](https://opencode.ai). The integration has independent pieces, each
installed on purpose:

- `skills/memory-curation/SKILL.md`: the policy skill. It says what deserves a
  note and what must never become one, where it belongs in the hierarchy and
  on disk, how big it should be and why, how to search it back cheaply, when
  to point at a live source instead of copying it, how to attach provenance,
  and how to date a note's freshness. It also carries the note syntax, so it
  replaces Basic Memory's upstream `memory-notes` skill rather than layering
  on it; see "Replacing memory-notes" below.
- `skills/memory-curation/scripts/check-layout.py`: a checker for the on-disk
  conventions. It validates filenames, permalinks, unique titles, source-note
  naming and frontmatter across every project under `~/basic-memories/`. For
  `activity-log`, it also validates the two-node session shape and the compact
  parent boundary. It exits non-zero on a structural error.
- `src/session-context.ts`: an opencode plugin registering one tool,
  `memory_session_context`, which returns the current session ID, the
  configured author, the session's directory and worktree, and cheap git
  position (root, branch, commit, origin) when the directory is a repository.
- `snippets/AGENTS.md`: a short always-on section to paste into your own
  `AGENTS.md`, telling the agent when to recall and record activity.
- `templates/activity-log/README.md`: the policy file for a separate private
  Basic Memory project containing one-sentence activity parents and opt-in
  continuity children.

The plugin has no event hooks, injects nothing into prompts or context, makes
no memory calls of its own, and never touches your `AGENTS.md`. It answers one
question, only when an agent asks it, before creating an activity record or
recording durable session-derived evidence.

## Installing

Everything is explicit. Nothing here installs itself.

```sh
git clone https://github.com/llucax/opencode-basic-memory-curation
cd opencode-basic-memory-curation
npm install
ln -sfn "$PWD/src/session-context.ts" ~/.config/opencode/plugins/opencode-basic-memory-curation.ts
ln -sfn "$PWD/skills/memory-curation" ~/.config/opencode/skills/memory-curation
```

Then paste `snippets/AGENTS.md` into your own `AGENTS.md` by hand, and restart
opencode. The skill can be copied instead of symlinked if you prefer to edit
your own copy.

`npm install` is required, not optional: module resolution follows the
symlink's real path, so `@opencode-ai/plugin` is resolved from this repo's own
`node_modules`.

Create and register the private activity project separately:

```sh
mkdir -p ~/basic-memories/activity-log
cp templates/activity-log/README.md ~/basic-memories/activity-log/README.md
bm project add activity-log ~/basic-memories/activity-log
```

Keep the default project pointed at durable personal knowledge; every activity
operation selects `activity-log` explicitly. A private Git remote may back up
the project, but it must never be public, team-shared, or synchronized through
Basic Memory cloud.

## Why this exists

Basic Memory is a good tool aimed at a different job than this one. Its design
centre is a knowledge journal, where notes are the artifact, capture is
generous, and there is no competing source of truth. This skill treats memory
as a thin, curated pointer layer over sources that are already authoritative:
repositories, documentation, other skills, and `AGENTS.md` files. Same tool,
different job, so several of upstream's recommendations are inverted here.
Each inversion below is a problem that showed up in real use, not a
preference.

**Notes duplicating what the agent already has.** The most common failure is
not a wrong note, it is a redundant one. `AGENTS.md` files are auto-loaded, so
anything written in one is in the agent's context exactly when it applies;
copying it into memory produces a second version that can only drift from the
one actually being read. The skill turns this into a test rather than a
judgement call: name the reader and the moment, and if the fact will already
be in context then, write nothing. The same applies to something the agent
just wrote into a repository during the session.

**Length.** Upstream advises writing generously, favouring completeness, and
argues that longer notes are more discoverable. Measurement says otherwise for
this use case. `bm inspect chunks` shows a note is indexed as one `entity` row
holding the entire body plus one row per observation and relation; for a large
note that whole-body row was 79% of its indexed bytes. Every search hit
returns the body in full, and `page_size` caps how many results come back, not
how big they are. On a nine-note base a default search returned 31,706
characters. Length is therefore a cost paid on every match, and it buys almost
no discoverability, because observations are indexed as their own rows
whatever the body does.

**Retrieval.** The documented workflow searches and reads through the MCP
tools, which return note bodies in both steps. The skill splits discovery from
reading and takes each off that path. Discovery goes through the CLI, where
`bm tool search-notes --plain` keeps the titles, permalinks, scores and
capped snippets while dropping the bodies: 2,817 to 3,185 characters across
four queries on a 41-note base, against 28,678 to 39,702 for the equivalent
JSON. Reading goes to the Markdown on disk, which is the canonical copy
anyway, and unlike the tools supports ranged reads and `rg`. Clients without
shell access fall back to the MCP tool restricted to observations, worth 63%
there because it is the only way to drop the bodies.

**Conventions that only exist as prose.** The tree layout, one `index.md` per
node with a permalink matching its path, was documented in three places and
still got broken repeatedly, partly because `write_note` derives the filename
from the title and cannot produce an `index.md` at all. Prose alone did not
hold, so the layout rules moved into this skill, the `write_note` limitation
is stated outright, and `scripts/check-layout.py` makes the conventions
falsifiable.

**Recall on every turn.** The MCP server instructs connected agents to call
`recent_activity` when a session starts, but that tool reports note changes,
not work. `snippets/AGENTS.md` instead searches only one-sentence parents in
`activity-log` when recent context can help. It reads a detailed continuity
child only for a selected effort, then falls back to session history for exact
evidence. Durable memory remains query-driven, and a session that produces no
durable knowledge is a normal outcome rather than a missed one.

**Continuity mixed with knowledge.** Resumable state is useful but mutable and
too verbose for default recall. Keeping it in a separate private project lets a
short parent answer what each session is about while an exact child holds
blockers, workers, decisions, and next steps. Both are retained as permanent
history, but only recent parents enter default recall. Worker sessions are
aggregated under their parent manager, preventing parallel work from flooding
the activity list.

## Replacing memory-notes

This skill carries the note syntax itself and is meant to be the only memory
skill loaded. If Basic Memory's upstream `memory-notes` skill is installed,
unload it, by renaming its `SKILL.md` so opencode's loader stops seeing it:

```sh
mv ~/.config/opencode/skills/memory-notes/SKILL.md \
   ~/.config/opencode/skills/memory-notes/REFERENCE.md
```

Keeping both loaded is worse than picking one. They disagree about note length
as described above, and an agent reading both tends to follow the more
emphatic advice, which is upstream's. Upstream also presents itself as covering
syntax while giving policy, so the boundary an overlay would need does not
exist.

Upgrading Basic Memory does not restore the skill: the package ships no skills,
and any copy on disk was fetched by hand. The risk is a future upgrade
re-fetching it as `SKILL.md` on purpose, so leave a note next to it saying it
is unloaded deliberately.

## Configuring the author

The tool refuses to guess who you are. Set either the
`OPENCODE_MEMORY_AUTHOR` environment variable, or `username` in opencode's
config, to a stable identity such as a GitHub handle or a work email. With
neither set, the tool returns an error naming both instead of falling back to
`$USER` or git's `user.name`, since a wrong author on a shared note is worse
than no note.

## Development

```sh
npm install
npm run check   # typecheck + unit tests
```

The logic lives in `src/author.ts`, `src/git-info.ts` and `src/context.ts`,
which are testable without loading anything into opencode. `src/session-context.ts`,
the file actually symlinked into opencode, only wires them together and must
keep a single default export: opencode's plugin loader iterates every export in
a loaded file and throws on the first one that is not a plugin factory, which
would silently take the tool down with it.
