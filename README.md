# opencode-basic-memory-curation

Curation policy and provenance helper for using
[Basic Memory](https://github.com/basicmachines-co/basic-memory) as durable
knowledge in [opencode](https://opencode.ai). Three independent pieces, each
installed on purpose:

- `skills/memory-curation/SKILL.md`: the policy skill. It says what deserves a
  note, where it belongs in the hierarchy, when to point at a live source
  instead of copying it, and how to attach provenance. Note syntax stays in
  Basic Memory's own upstream `memory-notes` skill; this one does not repeat it.
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
