#!/usr/bin/env python3
"""Check that Basic Memory notes follow the knowledge base layout conventions.

Conventions enforced here come from the memory-curation skill, the
activity-local README, and the structure the durable projects actually use.

Errors are structural and always wrong. Warnings are policy metadata that some
projects do not use yet; fix them at least in notes you touch.

Usage:
    check-layout.py [PROJECT_DIR ...]

With no arguments, checks every project directory under ~/basic-memories/.
Exits non-zero if any error was found.
"""

import re
import sys
from pathlib import Path

# Scalar frontmatter keys every knowledge node must carry.
REQUIRED = ("title", "type", "permalink")
# Policy metadata that only some projects use. `classification` and
# `public_candidate` are for SHARED projects, where they queue notes for the
# eventual public split (02-frequenz-migration.md section 2,
# 03-team-sharing-and-public-split.md). They mean nothing in a project that is
# never shared, so they are not required globally: a project is expected to
# carry a key only if it already uses it somewhere. That keeps frequenz-internal
# at full coverage without pushing dead metadata into personal.
ADVISED = ("classification", "public_candidate", "reviewed_at")

SOURCE_NAME = re.compile(r"^opencode-[A-Za-z0-9._-]+-ses_[A-Za-z0-9]+$")
ACTIVITY_PARENT = re.compile(
    r"^sessions/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/"
    r"(?P<session>ses_[A-Za-z0-9]+)/index\.md$"
)
ACTIVITY_CONTINUITY = re.compile(
    r"^sessions/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/"
    r"(?P<session>ses_[A-Za-z0-9]+)/continuity/index\.md$"
)
ACTIVITY_REQUIRED = (
    "session_id",
    "session_author",
    "started_at",
    "last_active_at",
    "status",
    "directory",
)
ACTIVITY_STATUSES = {"active", "blocked", "complete", "superseded"}

errors: list[str] = []
warnings: list[str] = []


def error(path: Path, msg: str) -> None:
    errors.append(f"ERROR {path}: {msg}")


def warn(path: Path, msg: str) -> None:
    warnings.append(f"WARN  {path}: {msg}")


def frontmatter(path: Path) -> dict[str, str] | None:
    """Parse the flat scalar keys of a YAML frontmatter block.

    Deliberately not a YAML parser: only top-level `key: value` lines are
    needed, and nested/list values (such as `tags`) are skipped.
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        error(path, f"unreadable: {exc}")
        return None
    if not lines or lines[0].strip() != "---":
        error(path, "missing YAML frontmatter")
        return None
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return data
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):[ \t]*(.*)$", line)
        if match:
            data[match.group(1)] = match.group(2).strip().strip("'\"")
    error(path, "frontmatter block is never closed")
    return None


def markdown_body(path: Path) -> str:
    """Return Markdown after the closing frontmatter delimiter."""
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[index + 1 :]).strip()
    return ""


def check_activity_note(path: Path, rel: Path, meta: dict[str, str]) -> None:
    """Validate the compact activity/continuity record contract."""
    relative = rel.as_posix()
    parent_match = ACTIVITY_PARENT.fullmatch(relative)
    continuity_match = ACTIVITY_CONTINUITY.fullmatch(relative)
    match = parent_match or continuity_match
    if match is None:
        error(rel, "activity-local notes must use the documented session paths")
        return

    expected_type = "activity" if parent_match else "continuity"
    if meta.get("type") != expected_type:
        error(rel, f"session path requires `type: {expected_type}`")

    for key in ACTIVITY_REQUIRED:
        if not meta.get(key):
            error(rel, f"activity frontmatter is missing `{key}`")

    if meta.get("session_id") and meta["session_id"] != match.group("session"):
        error(rel, "`session_id` does not match the session path")
    if meta.get("status") and meta["status"] not in ACTIVITY_STATUSES:
        allowed = ", ".join(sorted(ACTIVITY_STATUSES))
        error(rel, f"`status` must be one of: {allowed}")

    if parent_match is None:
        return

    expected_continuity = f"{rel.parent.as_posix()}/continuity"
    if meta.get("continuity") != expected_continuity:
        error(rel, f"`continuity` must be `{expected_continuity}`")

    body = markdown_body(path)
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", body) if part.strip()]
    if paragraphs and paragraphs[0].startswith("# "):
        paragraphs.pop(0)
    if len(paragraphs) != 1:
        error(rel, "activity body must contain exactly one summary paragraph")
        return

    summary = " ".join(line.strip() for line in paragraphs[0].splitlines())
    if len(summary) > 300:
        error(rel, "activity summary must be at most 300 characters")
    if summary.startswith(("- ", "* ", "#")):
        error(rel, "activity summary must be prose, not a list or heading")
    if len(re.findall(r"[.!?](?:\s|$)", summary)) != 1:
        error(rel, "activity body must contain exactly one sentence")


def check_project(root: Path) -> None:
    if not root.is_dir():
        error(root, "not a directory")
        return

    titles: dict[str, Path] = {}
    notes: list[tuple[Path, dict[str, str], str, bool]] = []

    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(root)

        # The project README is documentation about the project, not a node.
        if rel == Path("README.md"):
            continue

        in_sources = "sources" in rel.parts[:-1]

        if in_sources:
            if not SOURCE_NAME.match(path.stem):
                error(
                    rel,
                    "source notes are named opencode-<author>-<session-id>.md",
                )
            expected_permalink = str(rel.with_suffix(""))
        elif path.name != "index.md":
            error(
                rel,
                "every knowledge node is <concept>/index.md "
                "(only README.md and sources/* are exempt)",
            )
            continue
        else:
            expected_permalink = str(rel.parent)

        meta = frontmatter(path)
        if meta is None:
            continue
        notes.append((rel, meta, expected_permalink, in_sources))

    # A project is held to the advised keys it already uses, and only those.
    # Nothing here pushes a shared project's metadata into a private one.
    advised_here = tuple(
        key for key in ADVISED if any(meta.get(key) for _, meta, _, _ in notes)
    )

    for rel, meta, expected_permalink, in_sources in notes:
        for key in REQUIRED:
            if not meta.get(key):
                error(rel, f"frontmatter is missing `{key}`")
        for key in advised_here:
            if not meta.get(key):
                warn(rel, f"frontmatter is missing `{key}` (used elsewhere in this project)")

        permalink = meta.get("permalink", "")
        if permalink and permalink != expected_permalink:
            error(
                rel,
                f"permalink is `{permalink}`, expected `{expected_permalink}` "
                "(it must match the conceptual path)",
            )

        if in_sources and meta.get("type") != "source":
            error(rel, "notes under sources/ must set `type: source`")

        if root.name == "activity-local":
            check_activity_note(root / rel, rel, meta)

        title = meta.get("title", "")
        if title:
            if title in titles:
                error(rel, f"title `{title}` is already used by {titles[title]}")
            else:
                titles[title] = rel


def main(argv: list[str]) -> int:
    if argv:
        roots = [Path(a).expanduser() for a in argv]
    else:
        base = Path.home() / "basic-memories"
        roots = sorted(
            p
            for p in base.glob("*")
            if p.is_dir() and ((p / ".git").exists() or (p / "README.md").exists())
        )
        if not roots:
            print(f"no Basic Memory projects found under {base}", file=sys.stderr)
            return 2

    for root in roots:
        check_project(root)

    for line in warnings:
        print(line)
    for line in errors:
        print(line, file=sys.stderr)

    checked = ", ".join(r.name for r in roots)
    if errors:
        print(
            f"\n{len(errors)} error(s), {len(warnings)} warning(s) in: {checked}",
            file=sys.stderr,
        )
        return 1
    print(f"\nlayout OK ({len(warnings)} warning(s)) in: {checked}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
