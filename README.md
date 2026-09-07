# opencode-basic-memory-curation

Curation policy and provenance helper for using
[Basic Memory](https://github.com/basicmachines-co/basic-memory) as durable
knowledge in [opencode](https://opencode.ai). Three independent pieces, each
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
  naming and frontmatter across every project under `~/basic-memories/`, and
  exits non-zero on a structural error. The skill tells the agent to run it
  before calling any memory change finished.
- `src/session-context.ts`: an opencode plugin registering one tool,
  `memory_session_context`, which returns the current session ID, the
  configured author, the session's directory and worktree, and cheap git
  position (root, branch, commit, origin) when the directory is a repository.
- `snippets/AGENTS.md`: a short always-on section to paste into your own
  `AGENTS.md`, telling the agent when to recall memory at all.

The plugin has no event hooks, injects nothing into prompts or context, makes
no memory calls of its own, and never touches your `AGENTS.md`. It answers one
question, only when an agent asks it, right before recording session-derived
evidence.

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

## Replacing memory-notes

This skill carries the note syntax itself and is meant to be the only memory
skill loaded. If Basic Memory's upstream `memory-notes` skill is installed,
unload it, by renaming its `SKILL.md` so opencode's loader stops seeing it:

```sh
mv ~/.config/opencode/skills/memory-notes/SKILL.md \
   ~/.config/opencode/skills/memory-notes/REFERENCE.md
```

Keeping both loaded is worse than picking one. They disagree about how long a
note should be, upstream arguing that longer notes are more discoverable, and
an agent reading both tends to follow the more emphatic advice. The measured
behaviour is the opposite: Basic Memory indexes a note as one row holding the
entire body, so every search hit pays for the whole note, while observations
are indexed as separate rows regardless of body length. The reasoning and the
measurements are in the skill under "Size" and "Retrieval".

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
