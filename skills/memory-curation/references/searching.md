# Searching and filtering

`bm tool search-notes` takes an optional positional query plus filter flags,
and only needs a project when you are not using the CLI's own default:

```sh
bm tool search-notes "candidate title" --title --plain --project personal
```

`--title` and `--permalink` restrict the query to those fields instead of
full text; `--vector` and `--hybrid` switch retrieval mode.

## Filters

- `--type <name>` (repeatable): frontmatter `type`, the MCP `note_types`
  parameter. `bm tool search-notes --project personal --type note --type
  person ...` matches either.
- `--entity-type <kind>` (repeatable): search item kind, one of `entity`,
  `observation`, `relation`. This is the MCP `entity_types` parameter, and it
  is unrelated to `--type`: `--entity-type observation` does NOT shrink
  output by itself, it changes what kind of row comes back (an observation
  fact instead of the note that holds it).
- `--category <name>` (repeatable): restricts observation results to exact
  categories, only meaningful paired with `--entity-type observation`:

  ```sh
  bm tool search-notes --project personal --entity-type observation \
    --category decision --page-size 3 --json
  ```

- `--tag <name>` (repeatable, singular flag): frontmatter `tags` filter for
  search. `--tags` (plural) is a completely different flag that only exists
  on `write-note`, to set tags on a note.
- `--status <value>`: exact frontmatter `status` match.
- `--meta key=value` (repeatable): exact frontmatter key/value match, for
  fields with no dedicated flag:

  ```sh
  bm tool search-notes --project activity-log --type activity \
    --meta status=active --page-size 3 --json
  ```

- `--after_date <value>` (underscore, unlike the other flags): passed
  straight to `dateparser.parse` with no calendar-boundary handling and no
  minimum lookback. `"yesterday"` means a rolling 24 hours ago, not "since
  the start of yesterday". `"2 days"` or `"7d"` are safer defaults than a
  bare weekday name; when calendar days matter, compare the returned
  timestamps against a boundary computed client-side instead of trusting the
  parser's wording.
- `--page` / `--page-size`: pagination, defaults `1` / `10`.

## Output mode

`--json` (automatic when piped) gives the full structured payload, including
fields most recall tasks do not need (`external_id`, `entity_id`, `score`,
`updated_at`, `file_path`, `metadata`, and a duplicate of the title inside
`content`). Trim it with `jq` when only the permalink and title matter:

```sh
bm tool search-notes --project activity-log --type activity \
  --after_date 7d --page-size 20 --json \
  | jq -r '.results[] | "\(.permalink)  \(.title)"'
```

`--plain` gives undecorated numbered text instead, useful for a quick
existence check:

```sh
bm tool search-notes "candidate title" --title --plain --project personal
```

## `recent-activity` is not what its name suggests

`bm tool recent-activity` reports raw Basic Memory changes (entities,
observations, relations touched), not session work, and it rejects
`--type activity` outright:

```
$ bm tool recent-activity --project activity-log --type activity
Error: Invalid type: activity. Valid types are: ['entity', 'observation', 'relation']
```

For "what did I do recently", use `search-notes --type activity` as above,
never `recent-activity`.

## `build-context` for relation traversal

`bm tool build-context <permalink>` returns the primary note plus related
entities and observations across `[[wiki link]]` edges, which `search-notes`
does not do.

Pass a PLAIN permalink, never a `memory://` URI. The two take different
lookup paths: a plain identifier is looked up literally, while the
`memory://` form is first pushed through Basic Memory's permalink generator,
which lowercases, turns underscores into hyphens and splits camelCase. A
permalink that is not already in that generated shape gets normalized into
something that no longer matches what is stored, and the call returns zero
results with no error.

The same stored permalink, queried both ways:

```
$ bm tool build-context --project activity-log \
    "sessions/2026/09/ses_f70d4bd30ffeovrrdrjhukf61c"
-> primary_count 1, uri unchanged, relations traversed

$ bm tool build-context --project activity-log \
    "memory://sessions/2026/09/ses_f70d4bd30ffeovrrdrjhukf61c"
-> primary_count 0, uri mangled to ses-f70d4bd30ffeovrrdrjhukf61c
```

This bites exactly where a note's `permalink` was set explicitly in
frontmatter rather than derived from its filename, which is every node in
this layout. `memory://` happens to work on permalinks that are already
generator-shaped, such as `memory://ai-tooling/basic-memory` in `personal`,
which is what makes the failure look project-specific when it is not. Use
plain permalinks everywhere and the question does not arise.
