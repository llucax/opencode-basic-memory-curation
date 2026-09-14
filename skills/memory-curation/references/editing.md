# Writing, editing, and deleting notes

## Plain writes

```sh
bm tool write-note --project <project> --title "My Note" --folder "topics/x" \
  --type note --content "Orientation sentence.

## Observations
- [fact] first observation #demo"
```

`--content` may be omitted to read from stdin (a heredoc, for content with its
own frontmatter). `--folder` is the MCP `directory` parameter; `--tags` sets
tags at write time and is a different flag from search's singular `--tag`.
`--type` here is the note's frontmatter `type`, but a `type:` present in the
content's own frontmatter wins over the flag. `--overwrite` replaces an
existing note instead of erroring on conflict.

The filename comes from `--title`, not from the folder or the frontmatter
`permalink`: `--folder "topics/x" --title "My Note"` writes
`topics/x/My Note.md`. A `permalink` in the content's opening frontmatter is
honored exactly as given, independent of that filename.

## Landing a file at an exact `index.md`

Basic Memory's node layout requires `<path>/index.md`, and the CLI has no
`move-note` to relocate a title-derived file there. Use `--title index`
directly instead, verified end to end:

```sh
bm tool write-note --project <project> --title index --type <type> \
  --folder "<path>" <<'EOF'
---
permalink: <path>
... remaining frontmatter ...
---

# <real title>

Body content.
EOF
```

`--folder "<path>" --title index` writes exactly `<path>/index.md`, because
the filename derives from `--title`. The DB title is now the string `index`,
so a second command fixes it:

```sh
bm tool edit-note --project <project> "<path>" \
  --operation find_replace --find-text "title: index" \
  --content "title: <real title>"
```

`find_replace` operates on the whole file including YAML frontmatter; this is
undocumented and is exactly what makes this recipe work. It is also a
foot-gun if `title: index` appears more than once in the file, which is why
`--expected-replacements` defaults to `1` and fails loudly on an ambiguous
match. The permalink from the content's frontmatter, including any uppercase
in it, and any custom frontmatter fields, survive both steps unchanged.

Verify with:

```sh
bm tool read-note --project <project> "<path>" --json --frontmatter
```

and confirm `file_path` ends in `index.md`. A note whose title is still the
literal string `index` after this is the residue of this recipe left
half-finished; `scripts/check-layout.py` flags it as a structural error.

## Editing an existing note

`bm tool edit-note <identifier> --operation <op> --content "..."` supports:

- `append` / `prepend`: add content at either end; creates the note if it
  does not exist yet.
- `find_replace`: needs `--find-text`; reaches into frontmatter as well as
  the body (see above); `--expected-replacements` defaults to `1`.
- `replace_section` / `insert_before_section` / `insert_after_section`: need
  `--section "## Heading"`. `replace_section` replaces through the next
  heading of the same or higher level by default, so it also replaces
  subsections; pass `--no-replace-subsections` to stop at the next heading of
  any level instead.

All three were run against a throwaway note and each updated only the
targeted part, leaving the rest of the file intact.

### `replace_section` and a repeated header

`replace_section` keeps the matched header line and replaces only what comes
after it. If `--content`'s very first non-blank line is that exact header
text, `bm` strips it for you, so re-including the header as the first line of
the replacement is safe and a no-op. The real trap is a repeated header
ANYWHERE ELSE in `--content`, most often because the replacement text has a
preamble line before it: that occurrence is NOT stripped, and you end up with
the header twice in the file. Verified against a throwaway note by putting
one line of preamble before the repeated header:

```sh
bm tool edit-note --project P "<permalink>" --operation replace_section \
  --section "## Next steps" \
  --content $'Some preamble text.\n\n## Next steps\n\n1. New item'
```

This is a compounding trap, not a cosmetic slip: once a header is duplicated,
every later `replace_section` or `insert_before_section`/`insert_after_section`
call on it fails outright, because both require a unique match:

```
Error: Multiple sections found with header '## Next steps'. Section
replacement requires unique headers.
```

Recover with `find_replace`, giving enough surrounding context in
`--find-text` to disambiguate the two occurrences (a bare newline needs a
`$'...'` string, not a plain quoted one):

```sh
bm tool edit-note --project P "<permalink>" --operation find_replace \
  --find-text $'## Next steps\nSome preamble text.' \
  --content $'### Old preamble section\n\nSome preamble text.'
```

Verify the header count is back to one with
`bm tool read-note --project P "<permalink>" --plain | grep -n '^## '`.

## Deleting

```sh
bm tool delete-note --project <project> "<permalink>"
bm tool delete-note --project <project> "<dir-path>" --is-directory
```

Returns `{"deleted": true, ...}` with the removed title, permalink, and
`file_path`. There is no undo; check the identifier with `read-note` first if
unsure.
