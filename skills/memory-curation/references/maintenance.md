# Project and index maintenance

## Projects

```sh
bm project list                          # table of local (and cloud) projects
bm tool list-projects                    # same data as JSON
bm project add <name> <path> --local     # register a local project directory
bm project remove <name>                 # stop tracking, keep files on disk
bm project remove <name> --delete-notes  # stop tracking AND delete the files
bm project info <name>                   # entity/observation/relation counts, embedding status
bm project ls --name <name> [subpath]    # list files inside a project
bm project move <name> <new-path>        # update a local project's configured path
bm project default <name>                # set the CLI's fallback project
```

`bm project set-cloud` / `set-local` switch a project between local and cloud
routing; neither is relevant to a local-only setup and both need cloud
credentials the container may not have, so treat them as read-the-help-first
territory rather than routine commands. `bm tool list-workspaces` needs cloud
credentials too; without them it fails with "Cloud routing requested but no
credentials found."

For a throwaway project used to test a writing command, always clean up with
`bm project remove <name> --delete-notes` afterward.

## Reindexing

```sh
bm reindex                        # every project: project-index + embeddings
bm reindex --project <name>       # just one project (or -p <name>)
bm reindex --search               # only the full-text index
bm reindex --embeddings           # only vector embeddings
bm reindex --full                 # full project-index run plus full re-embed
```

`write-note` and `edit-note` already update the search index as part of the
call; a query immediately after either one sees the change with no reindex
in between. Reindex matters only when Markdown changed outside the API, for
example a Git operation that touched the worktree directly, or an explicitly
approved bulk migration. `bm reindex --project <name> --search` after such a
change took about 3 seconds on a two-file project; scale that for larger
ones.

## `bm doctor --local`

```sh
bm doctor --local
```

This is a self-test of the write/index/search pipeline, not a check of any
existing project. Running it creates its own throwaway project (named
`doctor-<random>`), writes and reads one file through only that project, and
deletes it again. It never looks at `activity-log`, `personal`, or any other
real project, so it cannot verify that a specific record you just wrote is
correctly indexed; use `bm tool read-note --json --frontmatter` on that
record's permalink for that instead. Where it is useful is as a general
"is the pipeline itself broken" check after something unusual, such as a
version upgrade.

## Schema commands

Picoschema definitions are optional per note `type`; a type with none simply
reports "no schema found" rather than failing.

```sh
bm tool schema-infer <type> --project <project>   # suggest a schema from existing notes
bm tool schema-infer <type> --threshold 0.5 ...   # raise the frequency bar for optional fields
bm tool schema-diff <type> --project <project>    # drift between the schema and actual usage
bm tool schema-validate <type> --project <project>       # validate every note of a type
bm tool schema-validate <note-path> --project <project>  # validate one note
```

`schema-infer` looks at real notes and both `-diff`/`-validate` report `{"error":
"No schema found for type '<type>'"}` cleanly when the type has no schema
defined yet, rather than raising.
