#!/usr/bin/env python3
"""Record an OpenCode session in the `activity-log` Basic Memory project.

Creates (or, with --update, rewrites) both nodes of a session record, the
`type: activity` parent and its `type: continuity` child, following the
activity-log README: each node lands at exactly `.../index.md` through
`bm tool write-note --title index` plus the `edit-note find_replace` title fix.
Every Basic Memory call selects `--project activity-log`, and nothing under
~/basic-memories/ is touched directly.

Inputs are validated before anything is written, and both nodes are read back
through `bm` afterwards and checked, so the caller never has to read them.
Prints one line with both permalinks on success; on any failure prints what is
wrong and exits non-zero.

Usage:
    record-activity.py --session-id ID --author A --directory D \\
        --started-at ISO --status STATUS --title TITLE --summary SENTENCE \\
        [--update] [--dry-run] <<'EOF'
    Continuity body (Markdown).
    EOF

`--session-id`, `--author`, `--directory` and `--started-at` all come
straight from memory_session_context's fields; the script never invents or
looks any of them up itself. `--update` still keeps the originally recorded
`started_at`: if the given value disagrees with the record's, that is
memory_session_context returning a different session's identity, and the
script fails rather than silently rewriting history.
"""

import argparse
import json
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone

PROJECT = "activity-log"
SESSION_ID = re.compile(r"^ses_[A-Za-z0-9]{26}$")
STATUSES = ("complete", "blocked", "active")
# Plain YAML scalars must not start with an indicator character or contain
# `: ` / ` #`; the title is written unquoted by the find_replace title fix.
YAML_UNSAFE_START = tuple("-?:,[]{}#&*!|>'\"%@`")
MAX_TITLE = 120
MAX_SUMMARY = 300  # Same limits as check-layout.py.


class Failure(Exception):
    """A problem to report to the caller before exiting non-zero."""


def utc_iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(value: str) -> datetime:
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise Failure(f"--started-at `{value}` is not ISO 8601: {exc}") from exc
    if moment.tzinfo is None:
        raise Failure(f"--started-at `{value}` has no timezone; use UTC (`...Z`)")
    return moment


def validate(args: argparse.Namespace, body: str) -> list[str]:
    problems = []
    if not SESSION_ID.fullmatch(args.session_id):
        problems.append(
            f"--session-id `{args.session_id}` is not an OpenCode session ID "
            "(ses_ plus 26 letters or digits)"
        )
    for name in ("author", "directory"):
        value = getattr(args, name)
        if not value.strip() or "\n" in value:
            problems.append(f"--{name} must be a non-empty single line")
    if not args.directory.startswith("/"):
        problems.append(f"--directory `{args.directory}` must be an absolute path")

    title = args.title
    if not title or title != title.strip() or "\n" in title:
        problems.append("--title must be one line without leading/trailing spaces")
    elif title.lower() == "index" or title.lower().startswith("continuity for "):
        problems.append(f"--title `{title}` is reserved")
    elif (
        title.startswith(YAML_UNSAFE_START)
        or ": " in title
        or " #" in title
        or title.endswith(":")
    ):
        problems.append(
            f"--title `{title}` needs YAML quoting; avoid `: `, ` #`, a trailing "
            "`:` and a leading punctuation character"
        )
    if len(title) > MAX_TITLE:
        problems.append(f"--title is {len(title)} characters, at most {MAX_TITLE}")

    summary = " ".join(args.summary.split())
    if not summary:
        problems.append("--summary is empty")
    else:
        if len(summary) > MAX_SUMMARY:
            problems.append(
                f"--summary is {len(summary)} characters, at most {MAX_SUMMARY}"
            )
        if summary.startswith(("- ", "* ", "#")):
            problems.append("--summary must be prose, not a list item or heading")
        if len(re.findall(r"[.!?](?:\s|$)", summary)) != 1 or summary[-1] not in ".!?":
            problems.append(
                "--summary must be exactly one sentence ending in `.`, `!` or `?` "
                "(no other `. `, `! ` or `? ` inside it)"
            )

    if not body.strip():
        problems.append("the continuity body (stdin) is empty")
    elif body.lstrip().startswith("---"):
        problems.append("the continuity body must not carry frontmatter; the script adds it")
    return problems


def bm(argv: list[str], stdin: str | None = None) -> str:
    cmd = ["bm", "tool", *argv]
    try:
        result = subprocess.run(
            cmd, input=stdin, capture_output=True, text=True, check=False
        )
    except FileNotFoundError as exc:
        raise Failure("`bm` is not on PATH; defer the record") from exc
    if result.returncode != 0:
        raise Failure(
            f"`{shlex.join(cmd)}` exited {result.returncode}:\n"
            f"{(result.stderr or result.stdout).strip()}"
        )
    return result.stdout


def read_note(permalink: str) -> dict:
    out = bm(["read-note", "--project", PROJECT, permalink, "--json", "--frontmatter"])
    try:
        return json.loads(out)
    except json.JSONDecodeError as exc:
        raise Failure(f"unexpected read-note output for {permalink}: {out[:200]}") from exc


def title_owners(title: str) -> set[str]:
    """Permalinks of notes whose title is exactly `title`."""
    out = bm([
        "search-notes", "--project", PROJECT, "--title", title,
        "--page-size", "50", "--json",
    ])
    try:
        results = json.loads(out).get("results", [])
    except json.JSONDecodeError as exc:
        raise Failure(f"unexpected search-notes output: {out[:200]}") from exc
    return {r.get("permalink", "") for r in results if r.get("title") == title}


def node(meta: dict[str, str], heading: str, body: str) -> str:
    lines = ["---", *(f"{key}: {value}" for key, value in meta.items()), "---", ""]
    return "\n".join(lines) + f"\n# {heading}\n\n{body.strip()}\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Record a session in activity-log in one command; the "
        "continuity body is read from stdin."
    )
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--author", required=True)
    parser.add_argument("--directory", required=True)
    parser.add_argument("--status", required=True, choices=STATUSES)
    parser.add_argument("--title", required=True, help="activity title")
    parser.add_argument("--summary", required=True, help="exactly one sentence")
    parser.add_argument("--started-at", required=True, help="ISO 8601 UTC, from memory_session_context")
    parser.add_argument(
        "--update", action="store_true",
        help="rewrite an existing record (resumed or manager sessions)",
    )
    parser.add_argument("--dry-run", action="store_true", help="print, write nothing")
    args = parser.parse_args()

    if sys.stdin.isatty():
        print("error: pipe the continuity body on stdin (heredoc)", file=sys.stderr)
        return 2
    body = sys.stdin.read()

    try:
        problems = validate(args, body)
        if problems:
            raise Failure("invalid input:\n" + "\n".join(f"- {p}" for p in problems))

        started = parse_iso(args.started_at)
        sid = args.session_id
        folder = f"sessions/{started:%Y}/{started:%m}/{sid}"
        continuity = f"{folder}/continuity"

        existing = read_note(folder)
        if existing.get("permalink") is None and folder.lower() != folder:
            lowered = read_note(folder.lower())
            if lowered.get("permalink") is not None:
                raise Failure(
                    f"a lowercased record already exists at {lowered['permalink']}; "
                    "update it with edit-note instead"
                )
        if existing.get("permalink") is not None:
            if not args.update:
                raise Failure(
                    f"{folder} already exists; pass --update to rewrite it"
                )
            old_start = (existing.get("frontmatter") or {}).get("started_at")
            if old_start and parse_iso(str(old_start)) != started:
                raise Failure(
                    f"--started-at `{args.started_at}` does not match the "
                    f"record's `{old_start}`; pass memory_session_context's "
                    "current started_at, which never changes for this session"
                )
        elif args.update:
            raise Failure(f"--update given but {folder} does not exist")

        others = title_owners(args.title) - {folder}
        cont_title = f"Continuity for {args.title}"
        others |= title_owners(cont_title) - {continuity}
        if others:
            raise Failure(
                f"title already used by {', '.join(sorted(others))}; titles must "
                "be unique"
            )

        identity = {
            "session_id": sid,
            "session_author": args.author,
            "started_at": f'"{utc_iso(started)}"',
            "last_active_at": f'"{utc_iso(datetime.now(timezone.utc))}"',
            "status": args.status,
            "directory": args.directory,
        }
        summary = " ".join(args.summary.split())
        nodes = [
            (folder, "activity", args.title,
             node({"permalink": folder, **identity, "continuity": continuity},
                  args.title, summary)),
            (continuity, "continuity", cont_title,
             node({"permalink": continuity, **identity}, cont_title, body)),
        ]

        for permalink, kind, title, content in nodes:
            write = ["write-note", "--project", PROJECT, "--title", "index",
                     "--type", kind, "--folder", permalink]
            if args.update:
                write.append("--overwrite")
            fix = ["edit-note", "--project", PROJECT, permalink,
                   "--operation", "find_replace", "--find-text", "title: index",
                   "--content", f"title: {title}"]
            if args.dry_run:
                print(f"$ bm tool {shlex.join(write)} <<'EOF'\n{content}EOF")
                print(f"$ bm tool {shlex.join(fix)}\n")
                continue
            bm(write, content)
            bm(fix)

        if args.dry_run:
            print(f"dry run, nothing written: {folder} {continuity}")
            return 0

        wrong = []
        for permalink, kind, title, _ in nodes:
            got = read_note(permalink)
            meta = got.get("frontmatter") or {}
            checks = {
                "title": (got.get("title"), title),
                "permalink": (got.get("permalink"), permalink),
                "file_path": (got.get("file_path"), f"{permalink}/index.md"),
                "type": (meta.get("type"), kind),
                "session_id": (meta.get("session_id"), sid),
                "status": (meta.get("status"), args.status),
            }
            if kind == "activity":
                checks["continuity"] = (meta.get("continuity"), continuity)
            wrong += [
                f"- {permalink}: {key} is `{actual}`, expected `{expected}`"
                for key, (actual, expected) in checks.items()
                if actual != expected
            ]
        if wrong:
            raise Failure(
                "written, but the result is wrong; fix it with edit-note "
                "or rerun with --update:\n" + "\n".join(wrong)
            )
    except Failure as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"recorded {folder} {continuity}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
